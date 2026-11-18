// bilesenler.tsx - Ortak görsel parçalar ve renkler
import React from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View, type TextInputProps, type ViewStyle } from "react-native";
import { sagdanSola, t } from "./dil";

export const R = {
  zemin: "#F4F5F7",
  kart: "#FFFFFF",
  murekkep: "#14161A",
  ikincil: "#5F6670",
  soluk: "#9AA1AB",
  cizgi: "#E4E7EB",
  vurgu: "#1F6FEB",
  vurguAcik: "#E8F0FE",
  protein: "#2F9E6E",
  karb: "#E0A21B",
  yag: "#D9534F",
  su: "#2C8BD8",
  hata: "#C0392B",
};

export const yaziYonu = () => (sagdanSola() ? ({ writingDirection: "rtl", textAlign: "right" } as const) : {});

export function Yazi(p: { children: React.ReactNode; s?: any; tur?: "baslik" | "buyuk" | "alt" | "soluk" | "normal"; testID?: string }) {
  const tur = p.tur ?? "normal";
  return <Text testID={p.testID} style={[st[tur], yaziYonu(), p.s]}>{p.children}</Text>;
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
      style={({ pressed }) => [st.dugme, st[`d_${tur}`], (p.kapali) && { opacity: 0.45 }, pressed && { opacity: 0.8 }, p.s]}
    >
      {p.yukleniyor
        ? <ActivityIndicator color={tur === "ana" ? "#fff" : R.vurgu} />
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
      <Text style={[st.secenekYazi, p.secili && { color: R.vurgu, fontWeight: "700" }, yaziYonu()]}>{p.yazi}</Text>
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
  return t(m[kod] ?? "Bir sorun çıktı. Biraz sonra tekrar dene.");
}

const st = StyleSheet.create({
  baslik: { fontSize: 26, fontWeight: "700", color: R.murekkep, letterSpacing: -0.3 },
  buyuk: { fontSize: 40, fontWeight: "800", color: R.murekkep, letterSpacing: -1 },
  alt: { fontSize: 13, fontWeight: "600", color: R.ikincil },
  soluk: { fontSize: 13, color: R.soluk, lineHeight: 18 },
  normal: { fontSize: 16, color: R.murekkep, lineHeight: 22 },
  kart: { backgroundColor: R.kart, borderRadius: 20, padding: 18, marginBottom: 14, borderWidth: StyleSheet.hairlineWidth, borderColor: R.cizgi },
  dugme: { minHeight: 52, borderRadius: 14, alignItems: "center", justifyContent: "center", paddingHorizontal: 18 },
  d_ana: { backgroundColor: R.vurgu },
  d_ikincil: { backgroundColor: R.vurguAcik },
  d_yalin: { backgroundColor: "transparent" },
  dugmeYazi: { fontSize: 16, fontWeight: "700" },
  dy_ana: { color: "#fff" },
  dy_ikincil: { color: R.vurgu },
  dy_yalin: { color: R.ikincil, fontWeight: "600" },
  girdi: { minHeight: 50, borderRadius: 12, borderWidth: 1, borderColor: R.cizgi, backgroundColor: "#fff", paddingHorizontal: 14, fontSize: 16, color: R.murekkep },
  secenek: { borderWidth: 1, borderColor: R.cizgi, backgroundColor: "#fff", borderRadius: 12, paddingVertical: 14, paddingHorizontal: 16, marginBottom: 10 },
  seceneSecili: { borderColor: R.vurgu, backgroundColor: R.vurguAcik },
  secenekYazi: { fontSize: 16, color: R.murekkep },
});
