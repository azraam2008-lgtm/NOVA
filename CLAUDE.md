# Nova

Nova bir beslenme ve hareket takip uygulaması: kalori ve makro takibi, su, adım, egzersiz, kilo gelişimi, yapay zeka asistanı.
İki yüzü var ve ikisi aynı Supabase veritabanını paylaşıyor:

- **Site:** Streamlit (Python), https://azzzrss.streamlit.app. Depo kökündeki `.py` dosyaları.
- **Telefon uygulaması:** Expo (React Native, TypeScript), `mobil/` klasörü. iPhone'da Expo Go ile açılıyor.

Proje sahibi Azra. Türkçe konuş, sade ve teknik olmayan bir dille anlat.

## Değişmez kurallar

- **Değer uydurma.** Kalori, makro, vitamin, mineral, restoran menüsü: yalnızca kaynağı belli değerler (USDA, Open Food Facts, etiket fotoğrafı, AB referans değerleri). Veri yoksa "veri yok" yaz, sıfır yazma.
- **Emoji yok.** Arayüzde, metinlerde, commit mesajlarında hiçbir yerde.
- **Dünya geneli, Türkiye'ye yerel değil.** Arama, oruç saatleri, birimler, örnekler her ülkeye uymalı. Altı dil var: Türkçe, İngilizce, Almanca, İspanyolca, Fransızca, Arapça (sağdan sola). Yeni her metin altı dile birden eklenir.
- **Ücretsiz.** Premium kararı Aşama F'ye ertelendi; şimdilik her özellik ücretsiz.
- **Sağlık dili nazik.** Suçlayıcı, ceza gibi açlık öneren ya da yeme bozukluğunu besleyen hiçbir şey yok. 18 yaş altında ve oruç modunda kalori düşürülmez. Hedef hiçbir gün dinlenik metabolizmanın (BMR) altına inmez. "Tıbbi tavsiye değildir" notu korunur.
- **Ayarlar soruları tekrar sormaz.** Kurulum bir kez yapılır; sonra bilgiler Profil'de tek sayfada düzenlenir. Azra kurulum sorularının baştan sorulmasını istemiyor.
- **Arka plan temaları önemli.** Altı tema var (Koyu Cam, Yakut Kızılı, Turkuaz Ferahlığı, Altın Zarafet, Bordo Kadife, Derin Mavi); görsel düzenlemelerde arka planlar kaybolmamalı.

## Güvenlik

- **Gizli anahtarlar asla koda, depoya ya da telefona girmez.** Gemini anahtarı, Supabase `service_role` / `sb_secret_` anahtarı yalnızca Supabase sunucu fonksiyonlarının ortam değişkenlerinde ve Streamlit Secrets'ta durur.
- Telefona yalnızca herkese açık `sb_publishable_` anahtarı gider; o da GitHub secret `EXPO_PUBLIC_SUPABASE_KEY` üzerinden, koda yazılmadan.
- Azra'dan anahtar ya da şifre istemeyi, ekran görüntüsünde anahtar göstermesini gerektiren adımlar önerme. Anahtarı bir panele yapıştırmak gerekirse adımı o yapar.
- Kullanıcı e-postası ve kişisel veri, onay alınmadan dış servislere gönderilmez.
- Veritabanında RLS açık: herkes yalnızca kendi satırlarını görür (`benim_adim()` fonksiyonu). Yeni tablo eklenirse RLS politikasıyla birlikte eklenir.

## Depo yapısı

```
app.py                Streamlit ana uygulama (giriş, sekmeler, kayıt)
nova_core.py          Yapay zeka çekirdeği: modlar (meal, coach, ask, label, voice), Gemini çağrısı, günlük haklar
nova_pages.py         Antrenman koçu ve sayfalar
hesap.py, hesap_koprusu.py, oturum.py, sifre_sifirlama.py   Hesap ve Supabase Auth köprüsü
yemek_arama.py, besin_kaynaklari.py, meal_scan.py, nutrition_check.py, tarif.py   Yemek arama, barkod, tarama, tarif
mikro.py              Vitamin ve mineraller (AB 1169/2011 NRV)
ramazan.py            Oruç modu (Aladhan API)
paylasim.py           Diyetisyen raporu: PDF ve süreli bağlantı (?rapor=<belirteç>)
gelisim.py, tarti.py  Gelişim grafikleri, tartı günleri (Pazartesi, Cuma, Pazar)
ayarlar.py            Tek sayfalık ayarlar
diller.py, ceviriler_ek.py   Site çevirileri
bildirim.py, hatirlatma.py, hatirlatma.yml   E-posta ve Telegram hatırlatmaları (GitHub Actions)
exercises.json        35 hareketlik egzersiz kütüphanesi (id'ler telefondakiyle aynı)
cok_daha_kapsamli_yemek_veritabani.csv   Yerel yemek veritabanı
mobil/                Telefon uygulaması (aşağıda)
supabase/             Sunucu fonksiyonları ve SQL (aşağıda)
.github/workflows/nova-mobil.yml   Telefon uygulamasını Expo'ya yayınlar
```

## Telefon uygulaması (`mobil/`)

Expo SDK 58, React Native 0.88, React 19, TypeScript. Paket adı `app.nova.tracker`.

```
App.tsx                      Akış: yukleniyor -> dil -> giris -> kurulum -> ana
src/bilesenler.tsx           Ortak bileşenler (Yazi, Kart, Dugme, Girdi, Cip, Secenek, Cubuk...) ve tema paleti R
src/tema.ts                  Altı tema, arka plan görselleri assets/arkaplan/*.jpg
src/dil.ts                   Çeviriler: anahtar Türkçe metin, değer [en, de, es, fr, ar]. t() ve yer tutuculu tf()
src/hesap.ts                 Profil/Kayıt tipleri, hedef kalori formülü (siteyle aynı), öğünler
src/veri.ts                  Arka uç: SupabaseArka (gerçek) ve SahteArka (deneme, AsyncStorage)
src/disari.ts                Open Food Facts barkod, fotoğraf çekme ve küçültme
src/adim.ts                  iPhone hareket sensöründen adım (useAdimSayar)
src/mikro.ts, oruc.ts, rapor.ts, denge.ts, egzersizler.ts   Sitedeki modüllerin karşılıkları
src/ekranlar/                Giris, Kurulum, AnaEkran (sekmeler), Bugun, Gelisim, Antrenman, Koc, Profil, Ayarlar,
                             EklePaneli, Asistan (Nova balonu), GunKartlari, Denge, TemaSecici
scripts/expo_hazirla.js      Yayın öncesi runtimeVersion ve updates.url ayarı
```

Kurallar:
- Tanımlayıcılar Türkçe (`kaydet`, `guncelle`, `hedefHesapla`). Bu düzeni koru.
- Tema değişince StyleSheet'ler `temali()` ile yeniden kurulur; renkleri doğrudan yazma, `R.*` kullan.
- `Arkaplan` bileşenine `key` verme: tema değişince ağaç baştan kurulur ve kurulum adımı başa döner.
- Veri biçimi siteyle ortak (`kullanici_verileri` tablosunda `gunluk_kayitlar`, `aktivite_loglari`, `profil`). Alan adlarını değiştirme; site aynı satırı okuyor. Kayıt alanları: `Tarih, Öğün, Tarif, Kalori, Protein, Karbonhidrat, Yağ` ve mikro besinler (`"Kalsiyum (mg)"` gibi).
- Kaçamak dengeleme (`profil.dengeleme`) şimdilik yalnızca telefonda; site o günlerde normal hedefi gösteriyor.

Komutlar (`mobil/` içinde):
```
npm install
npx tsc --noEmit -p .                    # tip denetimi
npx expo start                           # Expo Go ile telefonda aç (Mac ile aynı Wi-Fi)
EXPO_PUBLIC_SAHTE=1 npx expo start --web # deneme kipi, tarayıcıda, Supabase'e bağlanmaz
npx expo export --platform ios           # iOS paketinin derlendiğini doğrula
```
`EXPO_PUBLIC_SAHTE=1` ile uygulama sahte arka uçla açılır; deneme hesabı oluşturup her akışı veritabanına dokunmadan sınayabilirsin. Yeni özelliği önce böyle dene.

Çevirileri denetlerken: `src/` içinde `t("...")` ve `tf("...", {...})` ile geçen her metnin `dil.ts`'de beş çevirisi olmalı. Yer tutucular `{k}` biçiminde.

## Supabase

Proje: `klncgexnykfwzpcrijrt` (https://klncgexnykfwzpcrijrt.supabase.co).

Tablolar: `kullanicilar` (kullanıcı adı ve `auth_id`), `kullanici_verileri` (tüm uygulama verisi, JSON), `kullanici_yemekleri` (favoriler ve kendi tarifleri, `kullanici,tur,ad` benzersiz), `paylasimlar` (diyetisyen bağlantıları: yalnızca belirtecin SHA-256 özeti saklanır). RPC: `ai_hak_kullan`, `ai_hak_iade` (günlük yapay zeka hakkı).

Sunucu fonksiyonları (`supabase/functions/`, Deno). Üçünde de panelde "Verify JWT" KAPALI; kimliği kendileri doğruluyor:
- `giris`: kullanıcı adıyla giriş ve kayıt, günde en fazla 10 hatalı deneme.
- `yapay-zeka`: Gemini kapısı. Modlar `modlar.json`'da; bu dosya `supabase/modlari_aktar.py` ile `nova_core.py`'den üretilir. Mod metnini değiştirirsen önce `nova_core.py`'yi değiştir, sonra betiği çalıştır.
- `paylasim`: giriş yapmış kullanıcının raporunu kaydeder, belirteç döndürür. Bağlantı: `https://azzzrss.streamlit.app/?rapor=<belirteç>`.

Anahtarları `SUPABASE_SECRET_KEYS` / `SUPABASE_PUBLISHABLE_KEYS` (JSON, `.default`) ile okur, yoksa eski `SUPABASE_SERVICE_ROLE_KEY`'e düşer. Eski (legacy) anahtarlar 2027 başında kalkıyor; sitenin hâlâ eski anahtarı kullanıp kullanmadığını kontrol et.

`supabase/panele_yapistir/` içinde her fonksiyonun panele tek dosya olarak yapıştırılabilen hali var. Supabase CLI kuruluysa `supabase functions deploy <ad> --no-verify-jwt` de olur.

SQL kurulumu: `supabase_kurulum.sql`, `supabase_asama_a.sql` (RLS, Auth köprüsü). Veritabanı değişikliğini önce Azra'ya anlat, onayla çalıştır.

## Yayın

`main`'e gelen her değişiklikte `.github/workflows/nova-mobil.yml` uygulamayı EAS Update ile `nova` kanalına yayınlar; Azra Expo Go'da yeniden açınca yeni sürümü görür. GitHub secret'ları: `EXPO_TOKEN` (zorunlu), `EXPO_PUBLIC_SUPABASE_KEY` (yoksa uygulama deneme kipinde açılır).

**Önemli:** Telefon uygulaması artık doğrudan `mobil/` klasöründe duruyor; `mobil.zip` silindi. Eskiden Safari klasör yüklemeyi bozduğu için zip kullanılıyordu. Workflow depoda yeniden bir `mobil.zip` görürse `mobil/` klasörünü siler ve zip'i açar; bu yüzden depoya bir daha zip yüklenmemeli, yoksa zip'teki eski sürüm klasörün üzerine yazılır.

Site Streamlit Cloud'da `main` dalından kendiliğinden yayınlanır.

## Durum ve sıradaki işler

Ayrıntılı plan ve puan tablosu: "Nova Yol Haritası" belgesi (claude.ai). Puan 73/100.

- Aşama A (güvenlik, Supabase Auth, sunucu fonksiyonları): bitti.
- Aşama B (uygulama iskeleti, sade ana ekran, Nova balonu): bitti.
- Aşama C (sitedeki her özelliğin telefona taşınması, kaçamak dengeleme): bitti.
- **Aşama D:** Apple geliştirici hesabı (yılda 99 dolar) şimdilik alınmıyor. Bu yüzden önce ücretsiz parçalar:
  1. Adım sayar: bitti. `src/adim.ts` (`expo-sensors` Pedometer). Açılışta, öne gelince ve açıkken 3 dakikada bir son 7 günün sensör adımını `aktivite_loglari[tarih].adim`'a yazar; kayıtlı sayı daha yüksekse (elle girilmişse) dokunmaz. Yalnızca iOS; Android ve web'de elle giriş. Apple Health bağlantısı tam sürüme kalıyor.
  2. Yerel hatırlatmalar (`expo-notifications`): akşam kaydı, sahur ve iftar, su.
  Widget ve TestFlight Apple hesabı açılınca.
- Aşama E: 35 hareket x kadın ve erkek egzersiz videoları. Videoları Azra başka bir araçla üretiyor; senden istem (prompt) isteyebilir. Biçim dikey 9:16, sessiz döngü, çalışan kaslar kırmızı. Dosya adları `squat_kadin.mp4`, `squat_erkek.mp4` gibi, id'ler `exercises.json` ile aynı.
- Aşama F: mağaza yayını ve premium. Aşama G: restoran menüleri ve arkadaşla takip. Aşama H: Apple Watch.

## Çalışma biçimi

- İşe başlamadan ne yapacağını bir cümleyle söyle; bitince ne değiştiğini ve Azra'nın neyi denemesi gerektiğini sade bir dille yaz.
- Telefon tarafında değişiklik yaptıktan sonra: tip denetimi, deneme kipinde akışı tarayıcıda dene, iOS paketi derleniyor mu bak.
- Sitedeki bir modülün telefon karşılığını yazarken önce sitedeki Python dosyasını oku; formüller, eşikler ve metinler aynı kalsın.
- Sunucu fonksiyonunu ya da veritabanını değiştirmeden önce Azra'ya sor.
