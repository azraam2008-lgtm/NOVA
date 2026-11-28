-- ============================================================================
-- Nova - Supabase kurulum (tek seferde çalıştır)
--
-- Supabase panelinde: SQL Editor -> New query -> bu dosyanın tamamını yapıştır -> Run
-- Hiçbir mevcut veriyi silmez. Tekrar çalıştırmak zararsızdır.
--
-- ÖNEMLİ - ÖNCE ŞUNU OKU:
-- Bu dosya tüm tabloları dışarıya kapatır. Nova sunucuda çalıştığı için (Streamlit),
-- veritabanına "service_role" (secret) anahtarıyla bağlanmalı. O anahtar kullanıcının
-- tarayıcısına hiç gitmez, sadece sunucuda durur.
--
-- 1) Supabase > Project Settings > API > "service_role" anahtarını kopyala
-- 2) Streamlit Cloud > uygulaman > Settings > Secrets:
--        SUPABASE_URL = "https://xxxx.supabase.co"
--        SUPABASE_KEY = "eyJ...service_role anahtarı..."
-- 3) Bu anahtarı ASLA koda yazma, ASLA GitHub'a yükleme.
-- 4) Eski publishable anahtar koda yazılıydı: Supabase panelinden onu yenile (rotate).
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 1) MEVCUT TABLOLARI DIŞARIYA KAPAT  (en kritik adım)
-- ----------------------------------------------------------------------------
alter table public.kullanicilar          enable row level security;
alter table public.kullanici_verileri    enable row level security;

revoke all on table public.kullanicilar       from anon, authenticated;
revoke all on table public.kullanici_verileri from anon, authenticated;


-- ----------------------------------------------------------------------------
-- 2) HESAP: e-posta, şifre sıfırlama, "beni hatırla"
-- ----------------------------------------------------------------------------
alter table public.kullanicilar add column if not exists email text;
alter table public.kullanicilar add column if not exists olusturma timestamptz default now();
create index if not exists kullanicilar_email_idx on public.kullanicilar (email);

-- Tarayıcıda saklanan belirtecin yalnızca özeti tutulur
create table if not exists public.oturumlar (
  belirtec_ozeti text primary key,
  username       text not null,
  son_kullanma   timestamptz not null,
  olusturma      timestamptz not null default now()
);
create index if not exists oturumlar_username_idx on public.oturumlar (username);

create table if not exists public.sifre_sifirlama (
  username      text primary key,
  kod_ozeti     text not null,
  son_kullanma  timestamptz not null,
  deneme        integer not null default 0,
  olusturma     timestamptz not null default now()
);


-- ----------------------------------------------------------------------------
-- 3) YAPAY ZEKA GÜNLÜK HAK SAYACI
--    Sunucu yeniden başlasa da hak sıfırlanmaz (nova_core.py bunu kullanır)
-- ----------------------------------------------------------------------------
create table if not exists public.ai_kullanim (
  gun       date not null,
  kullanici text not null,
  ozellik   text not null,
  adet      integer not null default 0,
  primary key (gun, kullanici, ozellik)
);

-- Hakkı bir artırıp yeni değeri döndürür (aynı anda iki istek gelse bile doğru sayar)
create or replace function public.ai_hak_kullan(p_gun date, p_kullanici text, p_ozellik text)
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  yeni integer;
begin
  insert into public.ai_kullanim (gun, kullanici, ozellik, adet)
  values (p_gun, p_kullanici, p_ozellik, 1)
  on conflict (gun, kullanici, ozellik)
  do update set adet = public.ai_kullanim.adet + 1
  returning adet into yeni;
  return yeni;
end;
$$;

-- 30 günden eski sayaç satırlarını temizlemek için (istersen ara sıra elle çalıştır)
-- delete from public.ai_kullanim where gun < current_date - 30;


-- ----------------------------------------------------------------------------
-- 4) ÜRÜN ÖNBELLEĞİ
--    Open Food Facts'ten bir kez bulunan ürün burada saklanır, ikinci kez sorulmaz
--    (besin_kaynaklari.py bunu kullanır)
-- ----------------------------------------------------------------------------
create table if not exists public.urun_onbellek (
  kod        text primary key,
  ad         text not null,
  marka      text default '',
  veri       jsonb not null,
  guncelleme timestamptz not null default now()
);
create index if not exists urun_onbellek_ad_idx    on public.urun_onbellek using gin (to_tsvector('simple', ad));
create index if not exists urun_onbellek_marka_idx on public.urun_onbellek (marka);


-- ----------------------------------------------------------------------------
-- 5) KULLANICININ KENDİ YEMEKLERİ VE FAVORİLERİ
--    tur = 'favori'  -> yıldızladığı yemek
--    tur = 'kendi'   -> kendi eklediği yemek (veritabanında olmayan)
-- ----------------------------------------------------------------------------
create table if not exists public.kullanici_yemekleri (
  id         bigserial primary key,
  kullanici  text not null,
  tur        text not null check (tur in ('favori', 'kendi')),
  ad         text not null,
  veri       jsonb not null,
  olusturma  timestamptz not null default now(),
  unique (kullanici, tur, ad)
);
create index if not exists kullanici_yemekleri_idx on public.kullanici_yemekleri (kullanici, tur);


-- ----------------------------------------------------------------------------
-- 6) YENİ TABLOLARI DA DIŞARIYA KAPAT
-- ----------------------------------------------------------------------------
alter table public.oturumlar           enable row level security;
alter table public.sifre_sifirlama     enable row level security;
alter table public.ai_kullanim         enable row level security;
alter table public.urun_onbellek       enable row level security;
alter table public.kullanici_yemekleri enable row level security;

revoke all on table public.oturumlar           from anon, authenticated;
revoke all on table public.sifre_sifirlama     from anon, authenticated;
revoke all on table public.ai_kullanim         from anon, authenticated;
revoke all on table public.urun_onbellek       from anon, authenticated;
revoke all on table public.kullanici_yemekleri from anon, authenticated;


-- ----------------------------------------------------------------------------
-- 7) KONTROL: hepsinde rowsecurity = true olmalı
-- ----------------------------------------------------------------------------
select tablename, rowsecurity
from pg_tables
where schemaname = 'public'
  and tablename in ('kullanicilar', 'kullanici_verileri', 'oturumlar',
                    'sifre_sifirlama', 'ai_kullanim', 'urun_onbellek',
                    'kullanici_yemekleri')
order by tablename;

-- ============================================================
-- PAYLASIMLAR  (diyetisyen raporu baglantilari)
-- Baglantinin kendisi degil, yalnizca SHA-256 ozeti saklanir;
-- veritabanini goren biri calisan bir baglanti uretemez.
-- ============================================================
create table if not exists public.paylasimlar (
    belirtec_ozeti text primary key,
    username       text not null,
    veri           jsonb not null,
    son_kullanma   timestamptz not null,
    olusturma      timestamptz not null default now()
);

create index if not exists paylasimlar_username_idx on public.paylasimlar (username);

alter table public.paylasimlar enable row level security;
revoke all on public.paylasimlar from anon, authenticated;
-- Erisim yalnizca sunucu tarafindaki service_role anahtariyla olur.
