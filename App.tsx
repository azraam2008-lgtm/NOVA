// App.tsx - Nova uygulamasının akışı
// Dil -> Giriş -> Kurulum -> Ana ekran. Hepsi tek yerde, sırası değişmez.
import React, { useCallback, useEffect, useState } from "react";
import { ActivityIndicator, View } from "react-native";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { getLocales } from "expo-localization";
import { cihazDili, dilAyarla, type Dil } from "./src/dil";
import { BOS_VERI, type Veri } from "./src/hesap";
import { anahtarVarMi, arka } from "./src/veri";
import { R, Yazi } from "./src/bilesenler";
import { DilEkrani, GirisEkrani } from "./src/ekranlar/Giris";
import { KurulumEkrani } from "./src/ekranlar/Kurulum";
import { AnaEkran } from "./src/ekranlar/AnaEkran";

type Durum = "yukleniyor" | "dil" | "giris" | "kurulum" | "ana";

export default function App() {
  const [durum, setDurum] = useState<Durum>("yukleniyor");
  const [dil, setDil] = useState<Dil>("tr");
  const [kullanici, setKullanici] = useState<string | null>(null);
  const [veri, setVeri] = useState<Veri>(BOS_VERI());
  const [, yeniden] = useState(0);

  const dilSec = (d: Dil) => {
    dilAyarla(d); setDil(d); yeniden((x) => x + 1);
    AsyncStorage.setItem("nova_dil", d).catch(() => {});
  };

  const iceriAl = useCallback(async (k: string) => {
    setKullanici(k);
    const v = await arka.oku(k);
    if (v.profil?.dil) dilSec(v.profil.dil as Dil); // hesabın dili cihazdakini geçer
    setVeri(v);
    setDurum(v.profil?.setup_tamamlandi ? "ana" : "kurulum");
  }, []);

  useEffect(() => {
    (async () => {
      let kayitli: string | null = null;
      try { kayitli = await AsyncStorage.getItem("nova_dil"); } catch { /* boş */ }
      dilSec((kayitli as Dil) || cihazDili(getLocales()[0]?.languageCode));
      try {
        const k = await arka.oturumKullanici();
        if (k) return iceriAl(k);
      } catch { /* oturum yoksa girişe */ }
      setDurum(kayitli ? "giris" : "dil");
    })();
  }, [iceriAl]);

  const guncelle = async (f: (v: Veri) => Veri) => {
    if (!kullanici) return;
    setVeri((v) => f(v)); // ekranda hemen görünsün
    const son = await arka.guncelle(kullanici, f);
    setVeri(son);
  };

  const cikis = async () => {
    await arka.cikis();
    setKullanici(null); setVeri(BOS_VERI()); setDurum("giris");
  };

  let ekran: React.ReactNode;
  if (durum === "yukleniyor") ekran = <View style={{ flex: 1, justifyContent: "center" }}><ActivityIndicator /></View>;
  else if (durum === "dil") ekran = <DilEkrani secili={dil} sec={dilSec} devam={() => setDurum("giris")} />;
  else if (durum === "giris") ekran = <GirisEkrani girildi={iceriAl} />;
  else if (durum === "kurulum") ekran = (
    <KurulumEkrani profil={veri.profil} bitti={async (p) => { await guncelle((v) => ({ ...v, profil: { ...v.profil, ...p } })); setDurum("ana"); }} />
  );
  else ekran = <AnaEkran kullanici={kullanici!} veri={veri} guncelle={guncelle} cikis={cikis}
    dilDegistir={(d) => { dilSec(d); guncelle((v) => ({ ...v, profil: { ...v.profil, dil: d } })); }} />;

  return (
    <SafeAreaProvider>
      <View style={{ flex: 1, backgroundColor: R.zemin }} key={dil}>
        {!anahtarVarMi && <Yazi tur="soluk" s={{ backgroundColor: "#FFF4E5", padding: 8, textAlign: "center" }}>EXPO_PUBLIC_SUPABASE_KEY eksik</Yazi>}
        {ekran}
      </View>
      <StatusBar style="dark" />
    </SafeAreaProvider>
  );
}
