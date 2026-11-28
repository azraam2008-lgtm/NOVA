// App.tsx - Nova uygulamasının akışı
// Dil -> Giriş -> Kurulum -> Sekmeli ana ekran. Seçilen temanın fotoğrafı her ekranın arkasında.
import React, { useCallback, useEffect, useState } from "react";
import { ActivityIndicator, View } from "react-native";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { getLocales } from "expo-localization";
import { useFonts } from "expo-font";
import { PlayfairDisplay_700Bold } from "@expo-google-fonts/playfair-display/700Bold";
import { cihazDili, dilAyarla, type Dil } from "./src/dil";
import { BOS_VERI, type Veri } from "./src/hesap";
import { VARSAYILAN_TEMA, temaBul } from "./src/tema";
import { anahtarVarMi, arka } from "./src/veri";
import { Arkaplan, R, Yazi, temaAyarla } from "./src/bilesenler";
import { DilEkrani, GirisEkrani } from "./src/ekranlar/Giris";
import { KurulumEkrani } from "./src/ekranlar/Kurulum";
import { AnaEkran } from "./src/ekranlar/AnaEkran";

type Durum = "yukleniyor" | "dil" | "giris" | "kurulum" | "ana";

export default function App() {
  useFonts({ PlayfairDisplay_700Bold }); // yüklenmezse sistem yazı tipiyle devam eder
  const [durum, setDurum] = useState<Durum>("yukleniyor");
  const [dil, setDil] = useState<Dil>("tr");
  const [tema, setTema] = useState(VARSAYILAN_TEMA);
  const [kullanici, setKullanici] = useState<string | null>(null);
  const [veri, setVeri] = useState<Veri>(BOS_VERI());

  const dilSec = (d: Dil) => {
    dilAyarla(d); setDil(d);
    AsyncStorage.setItem("nova_dil", d).catch(() => {});
  };
  const temaSec = (ad: string) => {
    const x = temaBul(ad).ad;
    temaAyarla(x); setTema(x);
    AsyncStorage.setItem("nova_tema", x).catch(() => {}); // giriş ekranı da bu temayla açılsın
  };

  const iceriAl = useCallback(async (k: string) => {
    setKullanici(k);
    const v = await arka.oku(k);
    if (v.profil?.dil) dilSec(v.profil.dil as Dil); // hesabın dili ve teması cihazdakini geçer
    if (v.profil?.tema) temaSec(String(v.profil.tema));
    setVeri(v);
    setDurum(v.profil?.setup_tamamlandi ? "ana" : "kurulum");
  }, []);

  useEffect(() => {
    (async () => {
      let kayitliDil: string | null = null, kayitliTema: string | null = null;
      try {
        kayitliDil = await AsyncStorage.getItem("nova_dil");
        kayitliTema = await AsyncStorage.getItem("nova_tema");
      } catch { /* boş */ }
      dilSec((kayitliDil as Dil) || cihazDili(getLocales()[0]?.languageCode));
      temaSec(kayitliTema || VARSAYILAN_TEMA);
      try {
        const k = await arka.oturumKullanici();
        if (k) return iceriAl(k);
      } catch { /* oturum yoksa girişe */ }
      setDurum(kayitliDil ? "giris" : "dil");
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
  if (durum === "yukleniyor") ekran = <View style={{ flex: 1, justifyContent: "center" }}><ActivityIndicator color={R.murekkep} /></View>;
  else if (durum === "dil") ekran = <DilEkrani secili={dil} sec={dilSec} devam={() => setDurum("giris")} />;
  else if (durum === "giris") ekran = <GirisEkrani girildi={iceriAl} />;
  else if (durum === "kurulum") ekran = (
    <KurulumEkrani profil={veri.profil} temaSec={temaSec}
      bitti={async (p) => { await guncelle((v) => ({ ...v, profil: { ...v.profil, ...p } })); setDurum("ana"); }} />
  );
  else ekran = (
    <AnaEkran kullanici={kullanici!} veri={veri} guncelle={guncelle} cikis={cikis}
      dilDegistir={(d) => { dilSec(d); guncelle((v) => ({ ...v, profil: { ...v.profil, dil: d } })); }}
      temaDegistir={(ad) => { temaSec(ad); guncelle((v) => ({ ...v, profil: { ...v.profil, tema: ad } })); }} />
  );

  return (
    <SafeAreaProvider>
      {/* Tema ve dil değişince ekran yeniden çizilir ama yarım kalan kurulum adımı kaybolmaz */}
      <Arkaplan>
        {!anahtarVarMi && <Yazi tur="soluk" s={{ backgroundColor: "#FFF4E5", color: "#7A4B00", padding: 8, textAlign: "center" }}>EXPO_PUBLIC_SUPABASE_KEY eksik</Yazi>}
        {ekran}
      </Arkaplan>
      <StatusBar style={temaBul(tema).acik ? "dark" : "light"} />
    </SafeAreaProvider>
  );
}
