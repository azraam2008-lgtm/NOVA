// AnaEkran.tsx - Sekmeli çerçeve
// Altta adı yazan dört sekme ve ortada tek "Ekle" düğmesi. Sağ altta Nova balonu.
import React, { useMemo, useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { aktifDil, t, type Dil } from "../dil";
import { bugunMetni, gunToplami, hedefHesapla, yas, type Kayit, type Veri } from "../hesap";
import { R, temali } from "../bilesenler";
import { EklePaneli } from "./EklePaneli";
import { AsistanBalonu } from "./Asistan";
import { BugunSayfasi } from "./Bugun";
import { GelisimSayfasi } from "./Gelisim";
import { AntrenmanSayfasi } from "./Antrenman";
import { ProfilSayfasi } from "./Profil";
import { gunHedefi } from "../denge";
import { useAdimSayar } from "../adim";

type Sekme = "bugun" | "gelisim" | "antrenman" | "profil";
const SEKMELER: { k: Sekme; ad: string; ikon: keyof typeof Ionicons.glyphMap; ikonDolu: keyof typeof Ionicons.glyphMap }[] = [
  { k: "bugun", ad: "Bugün", ikon: "sunny-outline", ikonDolu: "sunny" },
  { k: "gelisim", ad: "Gelişim", ikon: "stats-chart-outline", ikonDolu: "stats-chart" },
  { k: "antrenman", ad: "Antrenman", ikon: "barbell-outline", ikonDolu: "barbell" },
  { k: "profil", ad: "Profil", ikon: "person-circle-outline", ikonDolu: "person-circle" },
];
const CUBUK = 64;

export function AnaEkran(p: {
  kullanici: string; veri: Veri; guncelle: (f: (v: Veri) => Veri) => Promise<void>; cikis: () => void;
  dilDegistir: (d: Dil) => void; temaDegistir: (ad: string) => void;
}) {
  const ic = useSafeAreaInsets();
  const [sekme, setSekme] = useState<Sekme>("bugun");
  const [ekleAcik, setEkleAcik] = useState(false);
  const tarih = bugunMetni();
  const pr = p.veri.profil;
  const hedef = Math.round(gunHedefi(pr, tarih).hedef);
  const [dengeTetik, setDengeTetik] = useState(0);
  const gun = gunToplami(p.veri.gunluk_kayitlar, tarih);
  const adimDurumu = useAdimSayar(p.veri, p.guncelle);

  // Nova'nın her yerde aynı kişiyi tanıması için tek bağlam
  const baglam = useMemo(() => [
    `Kullanıcı: ${pr.ad ?? ""}, ${yas(pr)} yaş, ${pr.cinsiyet ?? ""}, ${pr.boy ?? ""} cm, ${pr.mevcut_kilo ?? ""} kg, hedef ${pr.hedef_kilo ?? ""} kg.`,
    `Amaçları: ${(pr.amaclar ?? []).join(", ") || "-"}.`,
    `Bugün: ${Math.round(gun.kalori)} / ${hedef} kcal, protein ${Math.round(gun.protein)} g.`,
    `Yanıt dili: ${({ tr: "Türkçe", en: "English", de: "Deutsch", es: "Español", fr: "Français", ar: "العربية" } as any)[aktifDil()]}`,
  ].join("\n"), [pr, gun.kalori, gun.protein, hedef]);

  const ekle = (kayitlar: Kayit[]) => p.guncelle((v) => ({ ...v, gunluk_kayitlar: [...v.gunluk_kayitlar, ...kayitlar] }));
  const altBosluk = CUBUK + ic.bottom;

  const sekmeDugmesi = (x: (typeof SEKMELER)[0]) => {
    const secili = sekme === x.k;
    return (
      <Pressable key={x.k} testID={`sekme-${x.k}`} onPress={() => setSekme(x.k)} accessibilityRole="tab"
        accessibilityState={{ selected: secili }} accessibilityLabel={t(x.ad)} style={s.sekme}>
        <Ionicons name={secili ? x.ikonDolu : x.ikon} size={23} color={secili ? R.murekkep : R.soluk} />
        <Text style={[s.sekmeYazi, { color: secili ? R.murekkep : R.soluk, fontWeight: secili ? "700" : "500" }]} numberOfLines={1}>{t(x.ad)}</Text>
      </Pressable>
    );
  };

  return (
    <View style={{ flex: 1 }} testID="ana-ekran">
      <ScrollView key={sekme} contentContainerStyle={{ padding: 20, paddingTop: ic.top + 14, paddingBottom: altBosluk + 90 }} keyboardShouldPersistTaps="handled">
        {sekme === "bugun" && <BugunSayfasi veri={p.veri} tarih={tarih} hedef={hedef} guncelle={p.guncelle} dengeTetik={dengeTetik} adimDurumu={adimDurumu} />}
        {sekme === "gelisim" && <GelisimSayfasi veri={p.veri} hedef={hedef} guncelle={p.guncelle} />}
        {sekme === "antrenman" && <AntrenmanSayfasi veri={p.veri} tarih={tarih} guncelle={p.guncelle} adimDurumu={adimDurumu} />}
        {sekme === "profil" && <ProfilSayfasi veri={p.veri} kullanici={p.kullanici} temaSec={p.temaDegistir}
          dilSec={p.dilDegistir} cikis={p.cikis} guncelle={p.guncelle} />}
      </ScrollView>

      <View style={[s.cubuk, { paddingBottom: ic.bottom, height: altBosluk }]}>
        {SEKMELER.slice(0, 2).map(sekmeDugmesi)}
        <View style={s.sekme}>
          <Pressable testID="ekle-dugmesi" onPress={() => setEkleAcik(true)} accessibilityRole="button" accessibilityLabel={t("Ekle")}
            style={({ pressed }) => [s.ekle, pressed && { transform: [{ scale: 0.95 }] }]}>
            <Ionicons name="add" size={32} color="#fff" />
          </Pressable>
        </View>
        {SEKMELER.slice(2).map(sekmeDugmesi)}
      </View>

      <AsistanBalonu baglam={baglam} altBosluk={CUBUK + 14} dengeAc={() => { setSekme("bugun"); setDengeTetik((x) => x + 1); }} />
      <EklePaneli acik={ekleAcik} kapat={() => setEkleAcik(false)} profil={pr} tarih={tarih} baglam={baglam} kullanici={p.kullanici}
        ekle={async (k) => { await ekle(k); setSekme("bugun"); }} />
    </View>
  );
}

const s = temali(() => StyleSheet.create({
  cubuk: {
    position: "absolute", left: 0, right: 0, bottom: 0, flexDirection: "row", alignItems: "flex-start", paddingTop: 6,
    backgroundColor: R.panel, borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: R.cizgi,
  },
  sekme: { flex: 1, alignItems: "center", justifyContent: "center", gap: 2, minHeight: 52 },
  sekmeYazi: { fontSize: 11 },
  ekle: {
    width: 58, height: 58, borderRadius: 29, backgroundColor: R.vurgu, alignItems: "center", justifyContent: "center", marginTop: -22,
    borderWidth: 3, borderColor: R.panel, shadowColor: "#000", shadowOpacity: 0.3, shadowRadius: 10, shadowOffset: { width: 0, height: 4 }, elevation: 6,
  },
}));
