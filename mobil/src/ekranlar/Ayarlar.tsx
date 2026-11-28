// Ayarlar.tsx - Profil sayfasındaki ayar bölümleri (sitedeki ayarlar.py ile aynı alanlar)
// Bilgiler tek sayfada düzenlenir; kurulum soruları baştan sorulmaz.
import React, { useEffect, useState } from "react";
import { Platform, Share, View } from "react-native";
import * as Print from "expo-print";
import * as Sharing from "expo-sharing";
import { aktifDil, t } from "../dil";
import { AKTIVITE, AMACLAR, bugunMetni, haftalikHiz, hedefHesapla, yas, type Profil, type Veri } from "../hesap";
import { METOTLAR, VARSAYILAN_METOT, saatleriAl, type Saatler } from "../oruc";
import { raporHtml, raporVerisi } from "../rapor";
import { arka } from "../veri";
import { Cip, Dugme, Girdi, Hata, Kart, R, Secenek, Yazi, hataMetni } from "../bilesenler";

type Guncelle = (f: (v: Veri) => Veri) => Promise<void>;
const SITE = "https://azzzrss.streamlit.app";
const sayi = (m: string) => Number(String(m).replace(",", "."));
const Baslik = (p: { children: string; alt?: string }) => (
  <View style={{ marginBottom: 10 }}>
    <Yazi s={{ fontWeight: "700", fontSize: 17 }}>{p.children}</Yazi>
    {p.alt ? <Yazi tur="soluk" s={{ marginTop: 4 }}>{p.alt}</Yazi> : null}
  </View>
);

// ------------------------------------------------------------------ bilgiler
const ALANLAR: [keyof Profil, string, boolean][] = [
  ["dogum_yili", "Doğum yılı", false], ["boy", "Boy (cm)", false], ["mevcut_kilo", "Kilo (kg)", true],
  ["hedef_kilo", "Hedef kilo (kg)", true], ["hedef_sure_ay", "Kaç ayda?", false],
];

export function BilgilerKarti(p: { profil: Profil; guncelle: Guncelle }) {
  const ilk = () => Object.fromEntries(ALANLAR.map(([k]) => [k, String(p.profil[k] ?? "")]));
  const [metin, setMetin] = useState<Record<string, string>>(ilk);
  const [ad, setAd] = useState(String(p.profil.ad ?? ""));
  const [cinsiyet, setCinsiyet] = useState(p.profil.cinsiyet ?? "Kadın");
  const [aktivite, setAktivite] = useState(p.profil.aktivite ?? AKTIVITE[1][0]);
  const [amaclar, setAmaclar] = useState<string[]>(p.profil.amaclar ?? []);
  const [hata, setHata] = useState<string | null>(null);
  const [durum, setDurum] = useState<"" | "bekle" | "tamam">("");

  const yeni: Profil = { ...p.profil, ad: ad.trim(), cinsiyet, aktivite, amaclar, ...Object.fromEntries(ALANLAR.map(([k]) => [k, sayi(metin[k as string])])) };
  const yil = new Date().getFullYear();
  const gecerli = (): string | null => {
    if (!yeni.ad) return t("Lütfen adını gir.");
    if (!(Number(yeni.dogum_yili) >= 1920 && Number(yeni.dogum_yili) <= yil - 13)) return `${t("Doğum yılı")}: 1920 - ${yil - 13}`;
    if (!(Number(yeni.boy) >= 130 && Number(yeni.boy) <= 220)) return `${t("Boy (cm)")}: 130 - 220`;
    if (!(Number(yeni.mevcut_kilo) >= 35 && Number(yeni.mevcut_kilo) <= 250)) return `${t("Kilo (kg)")}: 35 - 250`;
    if (!(Number(yeni.hedef_kilo) >= 35 && Number(yeni.hedef_kilo) <= 250)) return `${t("Hedef kilo (kg)")}: 35 - 250`;
    if (!(Number(yeni.hedef_sure_ay) >= 1 && Number(yeni.hedef_sure_ay) <= 36)) return `${t("Kaç ayda?")}: 1 - 36`;
    return null;
  };
  const h = gecerli() ? null : hedefHesapla(yeni);
  const degisti = (["ad", "cinsiyet", "aktivite", ...ALANLAR.map((a) => a[0])] as (keyof Profil)[]).some((k) => String(yeni[k] ?? "") !== String(p.profil[k] ?? ""))
    || [...amaclar].sort().join("|") !== [...(p.profil.amaclar ?? [])].sort().join("|");

  const kaydet = async () => {
    const e = gecerli(); setHata(e);
    if (e) return;
    setDurum("bekle");
    const bugun = bugunMetni();
    const kiloDegisti = Number(yeni.mevcut_kilo) !== Number(p.profil.mevcut_kilo);
    try {
      await p.guncelle((v) => {
        const pr: Profil = { ...v.profil, ...yeni };
        if (kiloDegisti) {
          const gecmis = ((v.profil.kilo_gecmisi as any[]) ?? []).filter((x) => x.tarih !== bugun);
          pr.kilo_gecmisi = [...gecmis, { tarih: bugun, kilo: Number(yeni.mevcut_kilo) }];
          pr.son_tarti_tarihi = bugun;
        }
        return { ...v, profil: pr };
      });
      setDurum("tamam");
    } catch { setHata(t("Bir sorun çıktı. Biraz sonra tekrar dene.")); setDurum(""); }
  };

  return (
    <Kart testID="bilgiler-kart">
      <Baslik>{t("Bilgilerin")}</Baslik>
      <Girdi testID="ayar-ad" etiket={t("Adın")} value={ad} onChangeText={(m) => { setAd(m); setDurum(""); }} maxLength={40} />
      <Yazi tur="alt" s={{ marginBottom: 6 }}>{t("Cinsiyet")}</Yazi>
      <View style={{ flexDirection: "row", gap: 8, marginBottom: 12 }}>
        {(["Kadın", "Erkek"] as const).map((c) => <Cip key={c} testID={`ayar-cins-${c}`} yazi={t(c)} secili={cinsiyet === c} bas={() => { setCinsiyet(c); setDurum(""); }} />)}
      </View>
      <View style={{ flexDirection: "row", flexWrap: "wrap", columnGap: 10 }}>
        {ALANLAR.map(([k, etiket, ondalik]) => (
          <View key={String(k)} style={{ width: "48%", flexGrow: 1 }}>
            <Girdi testID={`ayar-${String(k)}`} etiket={t(etiket)} keyboardType={ondalik ? "decimal-pad" : "number-pad"}
              value={metin[k as string]} onChangeText={(m) => { setMetin((x) => ({ ...x, [k]: m })); setDurum(""); }} />
          </View>
        ))}
      </View>
      {!gecerli() && <Yazi tur="soluk" s={{ marginBottom: 8 }}>{yas(yeni)} {t("yaşındasın")}</Yazi>}
      {!gecerli() && haftalikHiz(yeni) > 1 && <Yazi tur="soluk" s={{ color: R.hata, marginBottom: 8 }}>{t("Bu tempo hızlı. Güvenli aralık genelde haftada 0,5-1 kilodur; süreyi uzatmanı öneririm.")}</Yazi>}
      <Yazi tur="alt" s={{ marginBottom: 8 }}>{t("Günlük hareket düzeyin")}</Yazi>
      {AKTIVITE.map(([a]) => <Secenek key={a} yazi={t(a)} secili={aktivite === a} bas={() => { setAktivite(a); setDurum(""); }} />)}
      <Yazi tur="alt" s={{ marginBottom: 8, marginTop: 4 }}>{t("Amaçların")}</Yazi>
      <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 12 }}>
        {AMACLAR.map((a) => {
          const secili = amaclar.includes(a);
          return <Cip key={a} yazi={t(a)} secili={secili} bas={() => { setAmaclar(secili ? amaclar.filter((x) => x !== a) : [...amaclar, a]); setDurum(""); }} />;
        })}
      </View>
      {h && (
        <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 6 }}>
          <Yazi tur="soluk">{t("Günlük hedefin")}</Yazi>
          <Yazi s={{ fontWeight: "700" }} testID="ayar-hedef">{Math.round(h.hedef)} kcal</Yazi>
        </View>
      )}
      <Hata metin={hata} />
      <Dugme testID="bilgi-kaydet" yazi={t(durum === "tamam" ? "Kaydedildi" : "Kaydet")} bas={kaydet}
        yukleniyor={durum === "bekle"} kapali={durum === "tamam" || !degisti} />
    </Kart>
  );
}

// ------------------------------------------------------------------ oruç
export function OrucAyarlari(p: { profil: Profil; guncelle: Guncelle }) {
  const acik = !!p.profil.oruc_modu;
  const [sehir, setSehir] = useState(String(p.profil.sehir ?? ""));
  const [ulke, setUlke] = useState(String(p.profil.ulke ?? ""));
  const [metot, setMetot] = useState(Number(p.profil.namaz_metodu ?? VARSAYILAN_METOT));
  const [imsak, setImsak] = useState(String(p.profil.elle_imsak ?? ""));
  const [iftar, setIftar] = useState(String(p.profil.elle_iftar ?? ""));
  const [elleAcik, setElleAcik] = useState(!!(p.profil.elle_imsak || p.profil.elle_iftar));
  const [saatler, setSaatler] = useState<Saatler | null | undefined>(undefined);
  const [bekle, setBekle] = useState(false);
  const [hata, setHata] = useState<string | null>(null);

  const yukle = async (pr: Profil) => { setSaatler(undefined); setSaatler(await saatleriAl(pr)); };
  useEffect(() => { if (acik) yukle(p.profil); }, [acik]);

  const kaydet = async () => {
    const saat = /^([01]?\d|2[0-3]):[0-5]\d$/;
    if ((imsak && !saat.test(imsak)) || (iftar && !saat.test(iftar))) return setHata(t("Saati 05:12 biçiminde yaz."));
    setHata(null); setBekle(true);
    const ek = { sehir: sehir.trim(), ulke: ulke.trim(), namaz_metodu: metot, elle_imsak: imsak.trim(), elle_iftar: iftar.trim() };
    await p.guncelle((v) => ({ ...v, profil: { ...v.profil, ...ek } }));
    await yukle({ ...p.profil, ...ek });
    setBekle(false);
  };

  return (
    <Kart testID="oruc-ayar">
      <Baslik alt={t("Öğünler sahur ve iftar olarak değişir, iftara kalan süre ana ekranda görünür, su hedefi oruç saatlerine göre ayarlanır.")}>{t("Oruç modu")}</Baslik>
      <View style={{ flexDirection: "row", gap: 8, marginBottom: acik ? 14 : 0 }}>
        <Cip testID="oruc-ac" yazi={t("Açık")} secili={acik} bas={() => p.guncelle((v) => ({ ...v, profil: { ...v.profil, oruc_modu: true } }))} />
        <Cip testID="oruc-kapat" yazi={t("Kapalı")} secili={!acik} bas={() => p.guncelle((v) => ({ ...v, profil: { ...v.profil, oruc_modu: false } }))} />
      </View>
      {acik && <>
        <View style={{ flexDirection: "row", gap: 10 }}>
          <View style={{ flex: 1 }}><Girdi testID="oruc-sehir" etiket={t("Şehir")} value={sehir} onChangeText={setSehir} placeholder="Istanbul" autoCapitalize="words" /></View>
          <View style={{ flex: 1 }}><Girdi testID="oruc-ulke" etiket={t("Ülke")} value={ulke} onChangeText={setUlke} placeholder="Turkey" autoCapitalize="words" /></View>
        </View>
        <Yazi tur="alt" s={{ marginBottom: 4 }}>{t("Hesaplama yöntemi")}</Yazi>
        <Yazi tur="soluk" s={{ marginBottom: 8, fontSize: 13 }}>{t("Ülkenin resmi kurumunu seç. Emin değilsen Muslim World League genel bir seçimdir.")}</Yazi>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 12 }}>
          {METOTLAR.map(([k, ad]) => <Cip key={k} testID={`metot-${k}`} yazi={ad} secili={metot === k} bas={() => setMetot(k)} />)}
        </View>
        <Dugme tur="yalin" yazi={t("Saatleri elle gir")} bas={() => setElleAcik(!elleAcik)} s={{ minHeight: 36, marginBottom: 6 }} />
        {elleAcik && <>
          <Yazi tur="soluk" s={{ marginBottom: 8, fontSize: 13 }}>{t("Servise ulaşılamazsa ya da kendi takvimini kullanmak istersen.")}</Yazi>
          <View style={{ flexDirection: "row", gap: 10 }}>
            <View style={{ flex: 1 }}><Girdi testID="oruc-imsak" etiket={t("İmsak")} value={imsak} onChangeText={setImsak} placeholder="05:12" keyboardType="numbers-and-punctuation" /></View>
            <View style={{ flex: 1 }}><Girdi testID="oruc-iftar" etiket={t("İftar")} value={iftar} onChangeText={setIftar} placeholder="17:30" keyboardType="numbers-and-punctuation" /></View>
          </View>
        </>}
        <Hata metin={hata} />
        <Dugme testID="oruc-kaydet" yazi={t("Kaydet ve saatleri getir")} bas={kaydet} yukleniyor={bekle} />
        {saatler && <Yazi s={{ color: R.iyi, marginTop: 10 }} testID="oruc-saatler">
          {t("İmsak")} {saatler.imsak} · {t("İftar")} {saatler.iftar}{saatler.hicriAyAdi ? `  ·  ${t("Hicri ay")}: ${saatler.hicriAyAdi} ${saatler.hicriGun || ""}` : ""}
        </Yazi>}
        {saatler === null && !!p.profil.sehir && <Yazi s={{ color: R.hata, marginTop: 10 }}>{t("Saatler alınamadı. Şehir ve ülke adını İngilizce yazmayı dene (örnek: Istanbul / Turkey) ya da aşağıdan elle gir.")}</Yazi>}
      </>}
    </Kart>
  );
}

// ------------------------------------------------------------------ diyetisyen
const DONEMLER = [7, 30, 90];
const SURELER = [1, 7, 30, 90];

export function PaylasimKarti(p: { veri: Veri; kullanici: string; hedef: number }) {
  const [donem, setDonem] = useState(30);
  const [sure, setSure] = useState(30);
  const [bekle, setBekle] = useState<"" | "pdf" | "bag" | "iptal">("");
  const [baglanti, setBaglanti] = useState<string | null>(null);
  const [acikSayi, setAcikSayi] = useState(0);
  const [onay, setOnay] = useState(false);
  const [hata, setHata] = useState<string | null>(null);
  const [mesaj, setMesaj] = useState<string | null>(null);
  const rapor = raporVerisi(p.veri, donem, p.hedef);

  const say = () => arka.paylasimSayisi(p.kullanici).then(setAcikSayi).catch(() => {});
  useEffect(() => { say(); }, []);

  const pdf = async () => {
    setHata(null); setBekle("pdf");
    try {
      const html = raporHtml(rapor, t, aktifDil());
      if (Platform.OS === "web") { await Print.printAsync({ html }); }
      else {
        const { uri } = await Print.printToFileAsync({ html });
        if (await Sharing.isAvailableAsync()) await Sharing.shareAsync(uri, { mimeType: "application/pdf", UTI: "com.adobe.pdf", dialogTitle: "Nova" });
      }
    } catch { setHata(t("PDF hazırlanamadı. Biraz sonra tekrar dene.")); }
    setBekle("");
  };
  const olustur = async () => {
    setHata(null); setMesaj(null); setBekle("bag");
    const r = await arka.paylasimOlustur(rapor, sure);
    setBekle("");
    if (!r.tamam) return setHata(r.hata === "limit" ? t("Bugün çok fazla bağlantı oluşturdun. Yarın tekrar dene.") : hataMetni(r.hata));
    setBaglanti(`${SITE}/?rapor=${r.deger}`); say();
  };
  const iptal = async () => {
    setBekle("iptal");
    const ok = await arka.paylasimlariIptal(p.kullanici);
    setBekle(""); setOnay(false);
    if (ok) { setBaglanti(null); setAcikSayi(0); setMesaj(t("Bütün paylaşım bağlantıları iptal edildi.")); }
    else setHata(t("Bir sorun çıktı. Biraz sonra tekrar dene."));
  };

  return (
    <Kart testID="paylasim-kart">
      <Baslik alt={t("Seçtiğin dönemin özetini PDF olarak indirebilir ya da bağlantı olarak paylaşabilirsin. Bağlantıyı açan kişi hesabına giremez, sadece bu raporu görür.")}>{t("Diyetisyenine gönder")}</Baslik>
      <Yazi tur="alt" s={{ marginBottom: 8 }}>{t("Hangi dönem")}</Yazi>
      <View style={{ flexDirection: "row", gap: 8, marginBottom: 8 }}>
        {DONEMLER.map((g) => <Cip key={g} testID={`donem-${g}`} yazi={`${g} ${t("gün")}`} secili={donem === g} bas={() => { setDonem(g); setBaglanti(null); }} />)}
      </View>
      <Yazi tur="soluk" s={{ marginBottom: 10 }} testID="rapor-ozet">
        {rapor.kayitli_gun === 0 ? t("Bu dönemde kayıt yok. Rapor boş çıkar.") : `${t("Kayıt girilen gün")}: ${rapor.kayitli_gun}/${donem} · ${t("Ortalama")} ${Math.round(rapor.ortalama.kalori)} kcal`}
      </Yazi>
      <Dugme testID="pdf-paylas" yazi={t("PDF olarak paylaş")} bas={pdf} yukleniyor={bekle === "pdf"} />

      <Yazi tur="alt" s={{ marginTop: 16, marginBottom: 8 }}>{t("Bağlantı kaç gün geçerli olsun?")}</Yazi>
      <View style={{ flexDirection: "row", gap: 8, marginBottom: 10 }}>
        {SURELER.map((g) => <Cip key={g} testID={`sure-${g}`} yazi={`${g} ${t("gün")}`} secili={sure === g} bas={() => setSure(g)} />)}
      </View>
      <Dugme testID="baglanti-olustur" tur="ikincil" yazi={t("Bağlantı oluştur")} bas={olustur} yukleniyor={bekle === "bag"} />
      {baglanti && (
        <View style={{ marginTop: 10 }}>
          <Yazi s={{ color: R.iyi, marginBottom: 6 }}>{t("Bağlantı hazır. Kopyalayıp diyetisyenine gönderebilirsin.")}</Yazi>
          <Yazi selectable testID="baglanti" s={{ fontSize: 13, backgroundColor: R.girdi, padding: 10, borderRadius: 10 }}>{baglanti}</Yazi>
          <Dugme tur="ikincil" yazi={t("Paylaş")} bas={() => Share.share({ message: baglanti, url: baglanti }).catch(() => {})} s={{ marginTop: 8 }} />
        </View>
      )}
      <Hata metin={hata} />
      {mesaj && <Yazi s={{ color: R.iyi, marginTop: 8 }}>{mesaj}</Yazi>}
      {acikSayi > 0 && (
        <View style={{ marginTop: 12 }}>
          <Yazi tur="soluk" testID="acik-baglanti">{t("Açık paylaşım bağlantısı")}: {acikSayi}</Yazi>
          {!onay
            ? <Dugme testID="iptal-sor" tur="yalin" yazi={t("Bütün bağlantıları iptal et")} bas={() => setOnay(true)} />
            : <View style={{ flexDirection: "row", gap: 8, marginTop: 6 }}>
                <Dugme tur="ikincil" yazi={t("Vazgeç")} bas={() => setOnay(false)} s={{ flex: 1 }} />
                <Dugme testID="iptal-onay" yazi={t("Evet, iptal et")} bas={iptal} yukleniyor={bekle === "iptal"} s={{ flex: 1, backgroundColor: R.hata }} />
              </View>}
        </View>
      )}
    </Kart>
  );
}
