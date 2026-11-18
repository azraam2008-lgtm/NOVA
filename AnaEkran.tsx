// AnaEkran.tsx - Sade ana ekran
// Üstte günün özeti, altında öğünler, en altta tek "Ekle" düğmesi.
// Sağ altta Nova balonu. Başka hiçbir giriş noktası yok.
import React, { useMemo, useState } from "react";
import { Pressable, ScrollView, StyleSheet, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { DILLER, aktifDil, t, type Dil } from "../dil";
import { Modal } from "react-native";
import { bugunMetni, gunToplami, hedefHesapla, ogunler, yas, type Kayit, type Veri } from "../hesap";
import { Cubuk, Dugme, Kart, R, Secenek, Yazi } from "../bilesenler";
import { EklePaneli } from "./EklePaneli";
import { AsistanBalonu } from "./Asistan";

const ALT_CUBUK = 84;

export function AnaEkran(p: {
  kullanici: string; veri: Veri; guncelle: (f: (v: Veri) => Veri) => Promise<void>; cikis: () => void;
  dilDegistir: (d: Dil) => void;
}) {
  const ic = useSafeAreaInsets();
  const [ekleAcik, setEkleAcik] = useState(false);
  const [dilAcik, setDilAcik] = useState(false);
  const tarih = bugunMetni();
  const pr = p.veri.profil;
  const hedef = Math.round(hedefHesapla(pr).hedef);
  const gun = gunToplami(p.veri.gunluk_kayitlar, tarih);
  const kalan = Math.round(hedef - gun.kalori);
  const su = Number(p.veri.aktivite_loglari?.[tarih]?.su ?? 0);

  // Nova'nın her yerde aynı kişiyi tanıması için tek bağlam
  const baglam = useMemo(() => [
    `Kullanıcı: ${pr.ad ?? ""}, ${yas(pr)} yaş, ${pr.cinsiyet ?? ""}, ${pr.boy ?? ""} cm, ${pr.mevcut_kilo ?? ""} kg, hedef ${pr.hedef_kilo ?? ""} kg.`,
    `Amaçları: ${(pr.amaclar ?? []).join(", ") || "-"}.`,
    `Bugün: ${Math.round(gun.kalori)} / ${hedef} kcal, protein ${Math.round(gun.protein)} g.`,
    `Yanıt dili: ${({ tr: "Türkçe", en: "English", de: "Deutsch", es: "Español", fr: "Français", ar: "العربية" } as any)[aktifDil()]}`,
  ].join("\n"), [pr, gun.kalori, gun.protein, hedef]);

  const tarihYazisi = new Intl.DateTimeFormat(aktifDil(), { weekday: "long", day: "numeric", month: "long" }).format(new Date());

  const ekle = (kayitlar: Kayit[]) => p.guncelle((v) => ({ ...v, gunluk_kayitlar: [...v.gunluk_kayitlar, ...kayitlar] }));
  const sil = (k: Kayit) => p.guncelle((v) => {
    const i = v.gunluk_kayitlar.findIndex((x) => x.Tarih === k.Tarih && x.Öğün === k.Öğün && x.Tarif === k.Tarif && x.Kalori === k.Kalori);
    return i < 0 ? v : { ...v, gunluk_kayitlar: v.gunluk_kayitlar.filter((_, j) => j !== i) };
  });
  const suDegistir = (fark: number) => p.guncelle((v) => {
    const gunluk = { adim: 0, su: 0, egzersiz_kalori: 0, ...(v.aktivite_loglari?.[tarih] ?? {}) };
    gunluk.su = Math.max(0, Math.round((Number(gunluk.su) + fark) * 100) / 100);
    return { ...v, aktivite_loglari: { ...v.aktivite_loglari, [tarih]: gunluk } };
  });

  const makro = (ad: string, g: number, renk: string, tavan: number) => (
    <View style={{ flex: 1 }}>
      <Yazi tur="alt">{t(ad)}</Yazi>
      <Yazi s={{ fontWeight: "700", marginVertical: 4 }}>{Math.round(g)} g</Yazi>
      <Cubuk oran={g / tavan} renk={renk} yukseklik={6} />
    </View>
  );

  return (
    <View style={{ flex: 1, backgroundColor: R.zemin }} testID="ana-ekran">
      <ScrollView contentContainerStyle={{ padding: 20, paddingTop: ic.top + 12, paddingBottom: ALT_CUBUK + ic.bottom + 40 }}>
        <View style={st.ust}>
          <View style={{ flex: 1 }}>
            <Yazi tur="baslik" testID="selam">{t("Merhaba")}, {pr.ad}</Yazi>
            <Yazi tur="soluk">{tarihYazisi}</Yazi>
          </View>
          <Dugme tur="yalin" yazi={aktifDil().toUpperCase()} bas={() => setDilAcik(true)} s={{ minHeight: 36, paddingHorizontal: 8 }} testID="dil-dugmesi" />
          <Dugme tur="yalin" yazi={t("Çıkış yap")} bas={p.cikis} s={{ minHeight: 36, paddingHorizontal: 6 }} testID="cikis" />
        </View>

        <Kart testID="ozet">
          <Yazi tur="alt">{t(kalan >= 0 ? "kcal kaldı" : "kcal fazla")}</Yazi>
          <Yazi tur="buyuk" testID="kalan" s={kalan < 0 ? { color: R.hata } : undefined}>{Math.abs(kalan)}</Yazi>
          <View style={{ marginVertical: 10 }}><Cubuk oran={gun.kalori / hedef} renk={kalan < 0 ? R.hata : R.vurgu} yukseklik={10} /></View>
          <View style={st.satir}>
            <Yazi tur="soluk">{t("Alınan")}: {Math.round(gun.kalori)} kcal</Yazi>
            <Yazi tur="soluk">{t("Hedef")}: {hedef} kcal</Yazi>
          </View>
          <View style={[st.satir, { marginTop: 16, gap: 14 }]}>
            {makro("Protein", gun.protein, R.protein, Math.max(60, Number(pr.mevcut_kilo ?? 60) * 1.2))}
            {makro("Karbonhidrat", gun.karb, R.karb, (hedef * 0.5) / 4)}
            {makro("Yağ", gun.yag, R.yag, (hedef * 0.3) / 9)}
          </View>
        </Kart>

        <Kart>
          <View style={st.satir}>
            <View>
              <Yazi tur="alt">{t("Su")}</Yazi>
              <Yazi s={{ fontWeight: "700", fontSize: 20 }} testID="su">{su.toFixed(2)} L</Yazi>
              <Yazi tur="soluk">{Math.round(su / 0.25)} {t("bardak")}</Yazi>
            </View>
            <View style={{ flexDirection: "row", gap: 8 }}>
              <Dugme tur="ikincil" yazi="−" bas={() => suDegistir(-0.25)} kapali={su <= 0} s={st.kare} testID="su-eksi" />
              <Dugme tur="ikincil" yazi="+" bas={() => suDegistir(0.25)} s={st.kare} testID="su-arti" />
            </View>
          </View>
        </Kart>

        {ogunler(pr).map((o) => {
          const liste = gun.kayitlar.filter((k) => k.Öğün === o);
          const top = liste.reduce((a, k) => a + Number(k.Kalori || 0), 0);
          return (
            <Kart key={o} testID={`ogun-${o}`}>
              <View style={st.satir}>
                <Yazi s={{ fontWeight: "700" }}>{t(o)}</Yazi>
                <Yazi tur="soluk">{Math.round(top)} kcal</Yazi>
              </View>
              {liste.length === 0
                ? <Yazi tur="soluk" s={{ marginTop: 6 }}>{t("Henüz bir şey eklemedin.")}</Yazi>
                : liste.map((k, i) => (
                  <View key={i} style={[st.satir, st.kalem]}>
                    <Yazi s={{ flex: 1, fontSize: 15 }}>{k.Tarif}</Yazi>
                    <Yazi tur="soluk" s={{ marginHorizontal: 8 }}>{Math.round(k.Kalori)} kcal</Yazi>
                    <Pressable onPress={() => sil(k)} accessibilityRole="button" accessibilityLabel={`${t("Sil")}: ${k.Tarif}`} hitSlop={10}>
                      <Yazi s={{ color: R.soluk, fontSize: 18 }}>×</Yazi>
                    </Pressable>
                  </View>
                ))}
            </Kart>
          );
        })}
      </ScrollView>

      <View style={[st.altCubuk, { paddingBottom: ic.bottom + 12 }]}>
        <Dugme testID="ekle-dugmesi" yazi={`+  ${t("Ekle")}`} bas={() => setEkleAcik(true)} s={{ width: "62%", borderRadius: 99, minHeight: 56 }} />
      </View>
      <AsistanBalonu baglam={baglam} altBosluk={ALT_CUBUK + 6} />
      <Modal visible={dilAcik} transparent animationType="fade" onRequestClose={() => setDilAcik(false)}>
        <Pressable style={st.perde} onPress={() => setDilAcik(false)}>
          <Pressable style={st.dilKutu} testID="dil-paneli">
            <Yazi tur="baslik" s={{ fontSize: 20, marginBottom: 14 }}>{t("Hangi dili kullanmak istersin?")}</Yazi>
            {DILLER.map((d) => <Secenek key={d.kod} testID={`dil-sec-${d.kod}`} yazi={d.ad} secili={aktifDil() === d.kod}
              bas={() => { setDilAcik(false); p.dilDegistir(d.kod); }} />)}
          </Pressable>
        </Pressable>
      </Modal>
      <EklePaneli acik={ekleAcik} kapat={() => setEkleAcik(false)} profil={pr} tarih={tarih} baglam={baglam} ekle={ekle} />
    </View>
  );
}

const st = StyleSheet.create({
  ust: { flexDirection: "row", alignItems: "center", marginBottom: 16 },
  satir: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  kalem: { marginTop: 10, paddingTop: 10, borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: R.cizgi },
  kare: { width: 48, minHeight: 44, paddingHorizontal: 0 },
  perde: { flex: 1, backgroundColor: "rgba(10,12,16,0.35)", justifyContent: "center", padding: 24 },
  dilKutu: { backgroundColor: R.zemin, borderRadius: 20, padding: 20 },
  altCubuk: { position: "absolute", left: 0, right: 0, bottom: 0, alignItems: "center", paddingTop: 12, backgroundColor: "rgba(244,245,247,0.94)" },
});
