// Giris.tsx - Dil seçimi, giriş ve kayıt
import React, { useState } from "react";
import { KeyboardAvoidingView, Platform, ScrollView, StyleSheet, View } from "react-native";
import { DILLER, t, type Dil } from "../dil";
import { arka } from "../veri";
import { Dugme, Girdi, Hata, Kart, R, Secenek, Yazi, hataMetni } from "../bilesenler";

export function Logo() {
  return (
    <View style={{ alignItems: "center", marginTop: 24, marginBottom: 28 }}>
      <Yazi s={s.logo}>N O V A</Yazi>
      <Yazi tur="soluk" s={{ letterSpacing: 4, textAlign: "center" }}>{t("ZARAFET VE DENGE")}</Yazi>
    </View>
  );
}

export function DilEkrani(p: { secili: Dil; sec: (d: Dil) => void; devam: () => void }) {
  return (
    <ScrollView contentContainerStyle={s.sayfa} testID="dil-ekrani">
      <Logo />
      <Yazi tur="baslik" s={{ marginBottom: 6 }}>{t("Hangi dili kullanmak istersin?")}</Yazi>
      <Yazi tur="soluk" s={{ marginBottom: 18 }}>{t("Nova'yı bu dilde kullanacaksın. Daha sonra ayarlardan değiştirebilirsin.")}</Yazi>
      {DILLER.map((d) => (
        <Secenek key={d.kod} testID={`dil-${d.kod}`} yazi={d.ad} secili={p.secili === d.kod} bas={() => p.sec(d.kod)} />
      ))}
      <Dugme testID="dil-devam" yazi={t("Devam")} bas={p.devam} s={{ marginTop: 12 }} />
    </ScrollView>
  );
}

export function GirisEkrani(p: { girildi: (kullanici: string) => void }) {
  const [sekme, setSekme] = useState<"giris" | "kayit">("giris");
  const [ad, setAd] = useState("");
  const [eposta, setEposta] = useState("");
  const [sifre, setSifre] = useState("");
  const [hata, setHata] = useState<string | null>(null);
  const [bekle, setBekle] = useState(false);

  const gonder = async () => {
    setHata(null);
    if (!ad.trim() || !sifre) return;
    setBekle(true);
    const r = sekme === "giris" ? await arka.girisYap(ad, sifre) : await arka.kayitOl(ad, eposta, sifre);
    setBekle(false);
    if (r.tamam) p.girildi(r.deger);
    else setHata(hataMetni(r.hata));
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined} style={{ flex: 1 }}>
      <ScrollView contentContainerStyle={s.sayfa} keyboardShouldPersistTaps="handled" testID="giris-ekrani">
        <Logo />
        <Kart>
          <View style={s.sekmeler}>
            {(["giris", "kayit"] as const).map((k) => (
              <Dugme key={k} testID={`sekme-${k}`} tur={sekme === k ? "ikincil" : "yalin"}
                yazi={t(k === "giris" ? "Giriş Yap" : "Kayıt Ol")} bas={() => { setSekme(k); setHata(null); }} s={{ flex: 1 }} />
            ))}
          </View>
          <Girdi testID="girdi-ad" etiket={t(sekme === "giris" ? "Kullanıcı adı veya e-posta" : "Kullanıcı adı")}
            value={ad} onChangeText={setAd} autoCapitalize="none" autoCorrect={false} />
          {sekme === "kayit" && (
            <Girdi testID="girdi-eposta" etiket={t("E-posta (isteğe bağlı, şifreni unutursan gerekli)")}
              value={eposta} onChangeText={setEposta} autoCapitalize="none" keyboardType="email-address" />
          )}
          <Girdi testID="girdi-sifre" etiket={t(sekme === "giris" ? "Şifre" : "Şifre (en az 8 karakter, bir büyük harf ve bir rakam)")}
            value={sifre} onChangeText={setSifre} secureTextEntry onSubmitEditing={gonder} />
          <Hata metin={hata} />
          <Dugme testID="giris-gonder" yazi={t(sekme === "giris" ? "Giriş Yap" : "Kayıt Ol")} bas={gonder} yukleniyor={bekle}
            kapali={!ad.trim() || !sifre} />
        </Kart>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const s = StyleSheet.create({
  sayfa: { padding: 20, paddingBottom: 60, flexGrow: 1, backgroundColor: R.zemin },
  logo: { fontSize: 38, fontWeight: "300", letterSpacing: 12, color: R.murekkep, textAlign: "center", marginBottom: 6 },
  sekmeler: { flexDirection: "row", gap: 8, marginBottom: 16 },
});
