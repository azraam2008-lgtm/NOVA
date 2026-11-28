// bilesenler.tsx - Ortak görsel parçalar
// Renkler sabit değil: seçilen temadan gelir (tema.ts). Tema değişince
// uygulama baştan çizilir, stiller de yeni renklerle yeniden kurulur.
import React from "react";
import { ActivityIndicator, ImageBackground, Pressable, StyleSheet, Text, TextInput, View, type TextInputProps, type ViewStyle } from "react-native";
import { sagdanSola, t } from "./dil";
import { VARSAYILAN_TEMA, opak, saydam, temaBul } from "./tema";

function paletKur(ad: string) {
  const x = temaBul(ad);
  return {
    ad: x.ad,
    acik: x.acik,
    resim: x.resim,
    perde: x.perde,
    zemin: x.zemin,
    kart: x.kart,
    panel: opak(x.kart, 1), // alt çubuk ve açılır paneller: arkadaki yazı görünmesin
    murekkep: x.yazi,
    ikincil: saydam(x.yazi, 0.78),
    soluk: saydam(x.yazi, 0.58),
    cizgi: x.cizgi,
    vurgu: x.vurgu,
    vurguAcik: saydam(x.vurgu, x.acik ? 0.16 : 0.32),
    girdi: x.acik ? "#ffffff" : "rgba(255,255,255,0.08)",
    protein: "#34C77B",
    karb: "#F2B233",
    yag: "#FF6B5E",
    su: "#4AA8F0",
    hata: x.acik ? "#B3261E" : "#FF8A80",
    iyi: x.acik ? "#1E7D4F" : "#7BE0A8",
  };
}

/** Etkin temanın renkleri. Tema değişince içeriği yerinde güncellenir. */
export const R = paletKur(VARSAYILAN_TEMA);
export function temaAyarla(ad: string) {
  Object.assign(R, paletKur(ad));
}

/** Temaya bağlı stil: tema değişince bir kez yeniden kurulur. */
export function temali<T extends Record<string, any>>(kur: () => T): T {
  let onbellek: { ad: string; s: T } | null = null;
  return new Proxy({} as T, {
    get(_h, anahtar: string) {
      if (!onbellek || onbellek.ad !== R.ad) onbellek = { ad: R.ad, s: kur() };
      return onbellek.s[anahtar];
    },
  });
}

/** Seçilen temanın fotoğrafı ve okunurluk perdesi */
export function Arkaplan(p: { children: React.ReactNode }) {
  return (
    <ImageBackground source={R.resim} resizeMode="cover"
      style={{ flex: 1, width: "100%", overflow: "hidden", backgroundColor: R.zemin }}
      imageStyle={{ width: "100%", height: "100%" }}>
      <View style={{ flex: 1, backgroundColor: R.perde }}>{p.children}</View>
    </ImageBackground>
  );
}

export const yaziYonu = () => (sagdanSola() ? ({ writingDirection: "rtl", textAlign: "right" } as const) : {});

export function Yazi(p: { children: React.ReactNode; s?: any; tur?: "baslik" | "buyuk" | "alt" | "soluk" | "normal"; testID?: string; selectable?: boolean }) {
  const tur = p.tur ?? "normal";
  return <Text testID={p.testID} selectable={p.selectable} style={[st[tur], yaziYonu(), p.s]}>{p.children}</Text>;
}

export function SayfaBasligi(p: { baslik: string; alt?: string; sag?: React.ReactNode }) {
  return (
    <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 16 }}>
      <View style={{ flex: 1 }}>
        <Yazi tur="baslik" s={{ fontSize: 30 }}>{p.baslik}</Yazi>
        {p.alt ? <Yazi tur="soluk">{p.alt}</Yazi> : null}
      </View>
      {p.sag}
    </View>
  );
}

export function Kart(p: { children: React.ReactNode; s?: ViewStyle; testID?: string }) {
  return <View testID={p.testID} style={[st.kart, p.s]}>{p.children}</View>;
}

export function Dugme(p: {
  yazi: string; bas: () => void; tur?: "ana" | "ikincil" | "yalin"; yukleniyor?: boolean; kapali?: boolean; s?: ViewStyle; testID?: string;
}) {
  const tur = p.tur ?? "ana";
  return (
    <Pressable
      testID={p.testID}
      accessibilityRole="button"
      accessibilityLabel={p.yazi}
      disabled={p.kapali || p.yukleniyor}
      onPress={p.bas}
      style={({ pressed }) => [st.dugme, st[`d_${tur}`], p.kapali && { opacity: 0.45 }, pressed && { opacity: 0.8 }, p.s]}
    >
      {p.yukleniyor
        ? <ActivityIndicator color={tur === "ana" ? "#fff" : R.murekkep} />
        : <Text style={[st.dugmeYazi, st[`dy_${tur}`]]}>{p.yazi}</Text>}
    </Pressable>
  );
}

export function Girdi(p: TextInputProps & { etiket?: string }) {
  const { etiket, style, ...geri } = p;
  return (
    <View style={{ marginBottom: 12 }}>
      {etiket ? <Yazi tur="alt" s={{ marginBottom: 6 }}>{etiket}</Yazi> : null}
      <TextInput placeholderTextColor={R.soluk} accessibilityLabel={etiket} style={[st.girdi, yaziYonu(), style]} {...geri} />
    </View>
  );
}

export function Secenek(p: { yazi: string; secili: boolean; bas: () => void; testID?: string }) {
  return (
    <Pressable testID={p.testID} accessibilityRole="button" accessibilityState={{ selected: p.secili }} onPress={p.bas}
      style={[st.secenek, p.secili && st.seceneSecili]}>
      <Text style={[st.secenekYazi, p.secili && { fontWeight: "700" }, yaziYonu()]}>{p.yazi}</Text>
    </Pressable>
  );
}

export function Cip(p: { yazi: string; secili: boolean; bas: () => void; testID?: string }) {
  return (
    <Pressable testID={p.testID} onPress={p.bas} accessibilityRole="button" accessibilityState={{ selected: p.secili }}
      style={[st.cip, p.secili && st.seceneSecili]}>
      <Text style={[st.cipYazi, p.secili && { fontWeight: "700" }]}>{p.yazi}</Text>
    </Pressable>
  );
}

export function Hata(p: { metin?: string | null }) {
  if (!p.metin) return null;
  return <Yazi s={{ color: R.hata, marginVertical: 8 }}>{p.metin}</Yazi>;
}

export function Cubuk(p: { oran: number; renk: string; yukseklik?: number }) {
  const o = Math.max(0, Math.min(1, p.oran || 0));
  return (
    <View style={{ height: p.yukseklik ?? 8, backgroundColor: R.cizgi, borderRadius: 99, overflow: "hidden" }}>
      <View style={{ width: `${o * 100}%`, height: "100%", backgroundColor: p.renk, borderRadius: 99 }} />
    </View>
  );
}

/** Sunucunun hata kodunu kullanıcının dilinde cümleye çevirir */
export function hataMetni(kod: string): string {
  const m: Record<string, string> = {
    hatali_giris: "Hatalı kullanıcı adı veya şifre.",
    kilitli: "Çok fazla yanlış deneme. Yarın tekrar dene ya da şifreni sıfırla.",
    kullanici_alinmis: "Bu kullanıcı adı zaten alınmış.",
    eposta_kayitli: "Bu e-posta ile kayıtlı bir hesap var.",
    kullanici_gecersiz: "Kullanıcı adı 3-30 karakter olmalı; harf, rakam, nokta ve tire kullanabilirsin.",
    eposta_gecersiz: "E-posta adresi geçerli görünmüyor.",
    sifre_kisa: "Şifre en az 8 karakter olmalıdır.",
    sifre_buyuk_harf: "Şifre en az bir büyük harf içermelidir.",
    sifre_rakam: "Şifre en az bir rakam içermelidir.",
    tasinamadi: "Hesabın hazırlanamadı. Bir kez siteden giriş yapıp tekrar dene.",
    baglanti: "Giriş servisine şu an ulaşılamadı. Biraz sonra tekrar dene.",
    hak_doldu: "Bugünkü hakkın doldu. Yarın tekrar dene.",
    kapasite_doldu: "Bugünkü hakkın doldu. Yarın tekrar dene.",
  };
  // Bilinmeyen kodda genel mesajın yanına kısa kodu ekle: sorunun yerini bulmayı sağlar
  return m[kod] ? t(m[kod]) : `${t("Bir sorun çıktı. Biraz sonra tekrar dene.")} (${String(kod).slice(0, 80)})`;
}

const st = temali(() => StyleSheet.create({
  baslik: { fontSize: 26, fontWeight: "700", color: R.murekkep, letterSpacing: -0.3 },
  buyuk: { fontSize: 44, fontWeight: "800", color: R.murekkep, letterSpacing: -1 },
  alt: { fontSize: 13, fontWeight: "600", color: R.ikincil },
  soluk: { fontSize: 13, color: R.soluk, lineHeight: 18 },
  normal: { fontSize: 16, color: R.murekkep, lineHeight: 22 },
  kart: { backgroundColor: R.kart, borderRadius: 24, padding: 20, marginBottom: 14, borderWidth: 1, borderColor: R.acik ? "rgba(0,0,0,0.06)" : "rgba(255,255,255,0.14)" },
  dugme: { minHeight: 52, borderRadius: 14, alignItems: "center", justifyContent: "center", paddingHorizontal: 18 },
  d_ana: { backgroundColor: R.vurgu },
  d_ikincil: { backgroundColor: R.vurguAcik },
  d_yalin: { backgroundColor: "transparent" },
  dugmeYazi: { fontSize: 16, fontWeight: "700" },
  dy_ana: { color: "#fff" },
  dy_ikincil: { color: R.murekkep },
  dy_yalin: { color: R.ikincil, fontWeight: "600" },
  girdi: { minHeight: 50, borderRadius: 12, borderWidth: 1, borderColor: R.cizgi, backgroundColor: R.girdi, paddingHorizontal: 14, fontSize: 16, color: R.murekkep },
  secenek: { borderWidth: 1, borderColor: R.cizgi, backgroundColor: R.girdi, borderRadius: 12, paddingVertical: 14, paddingHorizontal: 16, marginBottom: 10 },
  seceneSecili: { borderColor: R.vurgu, backgroundColor: R.vurguAcik },
  secenekYazi: { fontSize: 16, color: R.murekkep },
  cip: { borderWidth: 1, borderColor: R.cizgi, backgroundColor: R.girdi, borderRadius: 99, paddingVertical: 8, paddingHorizontal: 14 },
  cipYazi: { fontSize: 14, color: R.murekkep },
}));
