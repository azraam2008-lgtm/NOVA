-- ============================================================================
-- Nova - Aşama A: Telefon uygulaması için veritabanı kuralları
--
-- Supabase panelinde: SQL Editor -> New query -> bu dosyanın tamamını yapıştır -> Run
-- Önce supabase_kurulum.sql çalışmış olmalı (zaten çalıştırdın).
-- Hiçbir veriyi silmez. Tekrar çalıştırmak zararsızdır.
--
-- Ne değişir:
--   Site (Streamlit) eskisi gibi gizli anahtarla çalışır, hiçbir şeyi etkilenmez.
--   Telefon uygulaması gizli anahtar taşımaz; kullanıcı giriş yapınca veritabanı
--   ona YALNIZCA kendi satırlarını gösterir. Başkasının günlüğünü, şifre özetini,
--   oturumlarını göremez, değiştiremez.
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 1) Her Nova hesabını Supabase giriş sistemindeki karşılığına bağla
-- ----------------------------------------------------------------------------
alter table public.kullanicilar
  add column if not exists auth_id uuid unique references auth.users(id) on delete set null;

-- Kullanıcı adı tekil olmalı. Eskiden aynı adla iki kayıt oluştuysa dosya burada
-- durmasın diye önce kontrol edilir; varsa yalnızca uyarı verir.
do $$
begin
  if exists (select username from public.kullanicilar group by username having count(*) > 1) then
    raise notice 'UYARI: ayni kullanici adiyla birden cok kayit var, tekil indeks atlandi';
  else
    create unique index if not exists kullanicilar_username_uq on public.kullanicilar (username);
  end if;
end $$;


-- ----------------------------------------------------------------------------
-- 2) Giriş yapmış kişinin Nova kullanıcı adı
--    security definer: kullanicilar tablosunu kendisi okur, çağırana açmaz.
-- ----------------------------------------------------------------------------
create or replace function public.benim_adim()
returns text
language sql
stable
security definer
set search_path = public
as $$
  select username from public.kullanicilar where auth_id = auth.uid() limit 1;
$$;

revoke all on function public.benim_adim() from public, anon;
grant execute on function public.benim_adim() to authenticated;


-- ----------------------------------------------------------------------------
-- 3) kullanicilar: kendi satırını görür, şifre özetini ASLA görmez
--    Yetki sütun bazında verilir; password_hash ve auth_id listede yok.
-- ----------------------------------------------------------------------------
grant select (username, email, olusturma) on public.kullanicilar to authenticated;

drop policy if exists kendi_hesabim on public.kullanicilar;
create policy kendi_hesabim on public.kullanicilar
  for select to authenticated
  using (auth_id = auth.uid());


-- ----------------------------------------------------------------------------
-- 4) kullanici_verileri: profil, günlük, kilo kayıtları - yalnız kendisininki
-- ----------------------------------------------------------------------------
grant select, insert, update on public.kullanici_verileri to authenticated;

drop policy if exists kendi_verim on public.kullanici_verileri;
create policy kendi_verim on public.kullanici_verileri
  for all to authenticated
  using (username = public.benim_adim())
  with check (username = public.benim_adim());


-- ----------------------------------------------------------------------------
-- 5) kullanici_yemekleri: favoriler ve kendi yemekleri - yalnız kendisininki
-- ----------------------------------------------------------------------------
grant select, insert, update, delete on public.kullanici_yemekleri to authenticated;
grant usage on sequence public.kullanici_yemekleri_id_seq to authenticated;

drop policy if exists kendi_yemeklerim on public.kullanici_yemekleri;
create policy kendi_yemeklerim on public.kullanici_yemekleri
  for all to authenticated
  using (kullanici = public.benim_adim())
  with check (kullanici = public.benim_adim());


-- ----------------------------------------------------------------------------
-- 6) paylasimlar: kendi diyetisyen bağlantılarını görür ve iptal eder
--    (Bağlantı oluşturma sunucuda kalır: rapor verisi orada hazırlanıyor.)
-- ----------------------------------------------------------------------------
grant select, delete on public.paylasimlar to authenticated;

drop policy if exists kendi_paylasimlarim on public.paylasimlar;
create policy kendi_paylasimlarim on public.paylasimlar
  for all to authenticated
  using (username = public.benim_adim());


-- ----------------------------------------------------------------------------
-- 7) urun_onbellek: herkese açık besin bilgisi - giriş yapan okur, kimse yazamaz
-- ----------------------------------------------------------------------------
grant select on public.urun_onbellek to authenticated;

drop policy if exists onbellek_oku on public.urun_onbellek;
create policy onbellek_oku on public.urun_onbellek
  for select to authenticated
  using (true);


-- ----------------------------------------------------------------------------
-- 8) Sunucuya özel kalanlar (bilerek hiçbir yetki verilmez)
--    oturumlar        : sitenin "beni hatırla" belirteçleri
--    sifre_sifirlama  : sıfırlama kodları
--    ai_kullanim      : yapay zeka hak sayacı (hile yapılmasın)
--    ai_hak_kullan()  : yalnız sunucu fonksiyonu çağırır
-- ----------------------------------------------------------------------------
revoke all on table public.oturumlar       from anon, authenticated;
revoke all on table public.sifre_sifirlama from anon, authenticated;
revoke all on table public.ai_kullanim     from anon, authenticated;
revoke all on function public.ai_hak_kullan(date, text, text) from public, anon, authenticated;


-- ----------------------------------------------------------------------------
-- 9) Yapay zeka hakkı iadesi
--    Sunucu fonksiyonu hakkı çağrıdan ÖNCE düşer (aynı anda gelen istekler
--    sınırı aşamasın diye). Gemini hata verirse kullanıcının hakkı geri verilir.
-- ----------------------------------------------------------------------------
create or replace function public.ai_hak_iade(p_gun date, p_kullanici text, p_ozellik text)
returns integer
language sql
security definer
set search_path = public
as $$
  update public.ai_kullanim set adet = greatest(adet - 1, 0)
  where gun = p_gun and kullanici = p_kullanici and ozellik = p_ozellik
  returning adet;
$$;
revoke all on function public.ai_hak_iade(date, text, text) from public, anon, authenticated;


-- ----------------------------------------------------------------------------
-- 10) Kontrol: auth_id sütunu ve kurallar
-- ----------------------------------------------------------------------------
select tablename, policyname, cmd
from pg_policies
where schemaname = 'public'
order by tablename, policyname;
