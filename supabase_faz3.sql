-- Nova 3. aşama: e-posta, şifre sıfırlama ve "beni hatırla"
--
-- Supabase panelinde: SQL Editor -> New query -> bu dosyanın tamamını yapıştır -> Run
-- Bu dosya hiçbir mevcut veriyi silmez; kullanıcılar tablosuna yalnızca boş bir e-posta sütunu ekler.

-- 1) Kullanıcılara e-posta sütunu (isteğe bağlı, şifre sıfırlama için)
alter table public.kullanicilar add column if not exists email text;
create index if not exists kullanicilar_email_idx on public.kullanicilar (email);

-- 2) "Beni hatırla" oturumları (tarayıcıdaki belirtecin yalnızca özeti saklanır)
create table if not exists public.oturumlar (
  belirtec_ozeti text primary key,
  username text not null,
  son_kullanma timestamptz not null,
  olusturma timestamptz not null default now()
);
create index if not exists oturumlar_username_idx on public.oturumlar (username);

-- 3) Şifre sıfırlama kodları (kodun yalnızca özeti saklanır, 15 dakika geçerli)
create table if not exists public.sifre_sifirlama (
  username text primary key,
  kod_ozeti text not null,
  son_kullanma timestamptz not null,
  deneme integer not null default 0,
  olusturma timestamptz not null default now()
);

-- 4) Diğer tablolar gibi dışarıya kapalı (uygulama secret anahtarla erişir)
alter table public.oturumlar enable row level security;
alter table public.sifre_sifirlama enable row level security;
revoke all on table public.oturumlar from anon, authenticated;
revoke all on table public.sifre_sifirlama from anon, authenticated;

-- 5) Kontrol: iki satır, ikisinde de rowsecurity = true olmalı
select tablename, rowsecurity from pg_tables
where schemaname = 'public' and tablename in ('oturumlar', 'sifre_sifirlama');
