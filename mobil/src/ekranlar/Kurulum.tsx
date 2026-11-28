// Kurulum.tsx - İlk açılış soruları (sitedeki kurulumla aynı sorular, aynı veriler)
// Her ekranda tek soru. Dil, girişten önce seçildiği için burada yok.
import React, { useState } from "react";
import { ScrollView, StyleSheet, View } from "react-native";
import { aktifDil, t } from "../dil";
import { AKTIVITE, AMACLAR, haftalikHiz, hedefHesapla, yas, type Profil } from "../hesap";
import { TemaSecici } from "./TemaSecici";
import { VARSAYILAN_TEMA } from "../tema";
import { Dugme, Girdi, Hata, Kart, R, Secenek, Yazi, temali } from "../bilesenler";

const sayi = (m: string) => Number(String(m).replace(",", "."));

export function KurulumEkrani(p: { profil: Profil; bitti: (p: Profil) => Promise<void>; temaSec: (ad: string) => void; vazgec?: () => void }) {
  const [adim, setAdim] = useState(1);
  const [pr, setPr] = useState<Profil>({
    ad: "", amaclar: [], cinsiyet: "Kadın", dogum_yili: 2000, boy: 165, mevcut_kilo: 60, hedef_kilo: 55,
    hedef_sure_ay: 3, aktivite: AKTIVITE[1][0], tema: VARSAYILAN_TEMA, ...p.profil,
  });
  const [metin, setMetin] = useState<Record<string, string>>({});
  const [hata, setHata] = useState<string | null>(null);
  const [bekle, setBekle] = useState(false);
  const guncel = (a: Partial<Profil>) => setPr((x) => ({ ...x, ...a }));
  const alan = (k: keyof Profil, etiket: string, ondalik = false) => (
    <Girdi testID={`girdi-${String(k)}`} etiket={etiket} keyboardType={ondalik ? "decimal-pad" : "number-pad"}
      value={metin[k as string] ?? String(pr[k] ?? "")}
      onChangeText={(m) => { setMetin((x) => ({ ...x, [k]: m })); const n = sayi(m); if (!Number.isNaN(n)) guncel({ [k]: n } as Profil); }} />
  );

  const yil = new Date().getFullYear();
  const gecerli = (): string | null => {
    if (adim === 1 && !String(pr.ad ?? "").trim()) return t("Lütfen adını gir.");
    if (adim === 4 && !(Number(pr.dogum_yili) >= 1920 && Number(pr.dogum_yili) <= yil - 13)) return `1920 - ${yil - 13}`;
    if (adim === 5 && !(Number(pr.boy) >= 130 && Number(pr.boy) <= 220)) return "130 - 220 cm";
    if (adim === 6 && !(Number(pr.mevcut_kilo) >= 35 && Number(pr.mevcut_kilo) <= 250)) return "35 - 250 kg";
    if (adim === 7 && !(Number(pr.hedef_kilo) >= 35 && Number(pr.hedef_kilo) <= 250 && Number(pr.hedef_sure_ay) >= 1)) return "35 - 250 kg";
    return null;
  };
  const ileri = () => {
    const h = gecerli();
    setHata(h);
    if (!h) setAdim((a) => a + 1);
  };
  const bitir = async () => {
    setBekle(true);
    try { await p.bitti({ ...pr, ad: String(pr.ad).trim(), dil: aktifDil(), setup_tamamlandi: true }); }
    catch { setHata(t("Bir sorun çıktı. Biraz sonra tekrar dene.")); }
    setBekle(false);
  };

  let govde: React.ReactNode = null;
  if (adim === 1) govde = <>
    <Yazi tur="baslik">{t("Merhaba! Adın nedir?")}</Yazi>
    <View style={{ height: 16 }} />
    <Girdi testID="girdi-isim" etiket={t("Adın")} value={String(pr.ad ?? "")} onChangeText={(m) => guncel({ ad: m })} />
  </>;
  if (adim === 2) govde = <>
    <Yazi tur="baslik">{t("Nova'yı hangi amaçla kullanmak istiyorsun?")}</Yazi>
    <Yazi tur="soluk" s={{ marginVertical: 10 }}>{t("Birden fazla seçebilirsin.")}</Yazi>
    {AMACLAR.map((a) => {
      const secili = (pr.amaclar ?? []).includes(a);
      return <Secenek key={a} yazi={t(a)} secili={secili}
        bas={() => guncel({ amaclar: secili ? pr.amaclar!.filter((x) => x !== a) : [...(pr.amaclar ?? []), a] })} />;
    })}
  </>;
  if (adim === 3) govde = <>
    <Yazi tur="baslik">{t("Cinsiyetin nedir?")}</Yazi>
    <View style={{ height: 14 }} />
    {(["Kadın", "Erkek"] as const).map((c) => <Secenek key={c} testID={`cins-${c}`} yazi={t(c)} secili={pr.cinsiyet === c} bas={() => guncel({ cinsiyet: c })} />)}
    <Yazi tur="soluk">{t("Cinsiyetin, günlük enerji ihtiyacını hesaplamamızı doğrudan etkiler.")}</Yazi>
  </>;
  if (adim === 4) govde = <>
    <Yazi tur="baslik">{t("Doğum yılın ne?")}</Yazi>
    <View style={{ height: 14 }} />
    {alan("dogum_yili", "")}
    <Yazi>{yas(pr)} {t("yaşındasın")}</Yazi>
    {yas(pr) < 18 && <Yazi tur="soluk" s={{ marginTop: 10, color: R.hata }}>{t("18 yaşından küçüksün. Büyüme çağında kalori kısıtlamak gelişimi etkileyebilir; kilo hedefi koymadan önce bir doktora ya da diyetisyene danışmanı öneririm.")}</Yazi>}
  </>;
  if (adim === 5) govde = <><Yazi tur="baslik">{t("Boyun kaç?")}</Yazi><View style={{ height: 14 }} />{alan("boy", t("Boy (cm)"))}</>;
  if (adim === 6) govde = <><Yazi tur="baslik">{t("Şu andaki kilon ne?")}</Yazi><View style={{ height: 14 }} />{alan("mevcut_kilo", t("Kilo (kg)"), true)}</>;
  if (adim === 7) govde = <>
    <Yazi tur="baslik">{t("Hedef kilon nedir?")}</Yazi>
    <View style={{ height: 14 }} />
    {alan("hedef_kilo", t("Hedef kilo (kg)"), true)}
    {alan("hedef_sure_ay", t("Kaç ayda?"))}
    {haftalikHiz(pr) > 1 && <Yazi tur="soluk" s={{ color: R.hata, marginBottom: 10 }}>{t("Bu tempo hızlı. Güvenli aralık genelde haftada 0,5-1 kilodur; süreyi uzatmanı öneririm.")}</Yazi>}
    <Yazi tur="alt" s={{ marginBottom: 8 }}>{t("Günlük hareket düzeyin")}</Yazi>
    {AKTIVITE.map(([a]) => <Secenek key={a} yazi={t(a)} secili={pr.aktivite === a} bas={() => guncel({ aktivite: a })} />)}
  </>;
  if (adim === 8) govde = <>
    <Yazi tur="baslik">{t("Nova deneyimin için bir tema seç")}</Yazi>
    <View style={{ height: 14 }} />
    <TemaSecici secili={String(pr.tema)} sec={(ad) => { guncel({ tema: ad }); p.temaSec(ad); }} />
  </>;
  if (adim === 9) {
    const h = hedefHesapla(pr);
    govde = <View testID="kurulum-sonuc">
      <Yazi tur="alt">{t("Günlük hedefin")}</Yazi>
      <Yazi tur="buyuk" testID="hedef-kalori">{Math.round(h.hedef)} kcal</Yazi>
      <View style={s.satir}><Yazi tur="soluk">{t("Dinlenik metabolizman")}</Yazi><Yazi>{Math.round(h.bmr)} kcal</Yazi></View>
      <View style={s.satir}><Yazi tur="soluk">{t("Tahmini günlük harcaman")}</Yazi><Yazi>{Math.round(h.tdee)} kcal</Yazi></View>
      <Yazi tur="soluk" s={{ marginTop: 14 }}>{t("Nova bir sağlık uygulaması değildir ve tıbbi tavsiye vermez. Hesaplamalar genel formüllere dayanan tahminlerdir.")}</Yazi>
    </View>;
  }

  return (
    <ScrollView contentContainerStyle={s.sayfa} keyboardShouldPersistTaps="handled" testID={`kurulum-${adim}`}>
      <View style={s.ilerleme}>{Array.from({ length: 9 }, (_, i) => <View key={i} style={[s.nokta, i < adim && { backgroundColor: R.vurgu }]} />)}</View>
      <Kart>{govde}<Hata metin={hata} /></Kart>
      <View style={{ flexDirection: "row", gap: 10 }}>
        {adim === 1 && p.vazgec && <Dugme tur="ikincil" yazi={t("Vazgeç")} bas={p.vazgec} s={{ flex: 1 }} />}
        {adim > 1 && <Dugme tur="ikincil" yazi={t("Geri")} bas={() => { setHata(null); setAdim(adim - 1); }} s={{ flex: 1 }} />}
        {adim < 9
          ? <Dugme testID="kurulum-ileri" yazi={t("İleri")} bas={ileri} s={{ flex: 2 }} />
          : <Dugme testID="kurulum-bitir" yazi={t("Uygulamaya başla")} bas={bitir} yukleniyor={bekle} s={{ flex: 2 }} />}
      </View>
    </ScrollView>
  );
}

const s = temali(() => StyleSheet.create({
  sayfa: { padding: 20, paddingTop: 40, paddingBottom: 60, flexGrow: 1 },
  ilerleme: { flexDirection: "row", gap: 6, marginBottom: 18 },
  nokta: { flex: 1, height: 4, borderRadius: 2, backgroundColor: R.cizgi },
  satir: { flexDirection: "row", justifyContent: "space-between", marginTop: 10 },
}));
