// Asistan.tsx - Sağ alttaki yuvarlak Nova balonu ve sohbet
// Her ekranda aynı yerde durur. Ayrı bir "Asistan" sekmesi yok.
import React, { useRef, useState } from "react";
import { KeyboardAvoidingView, Modal, Platform, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { t } from "../dil";
import { arka } from "../veri";
import { kacamakMi } from "../denge";
import { Dugme, Girdi, R, Yazi, hataMetni, temali } from "../bilesenler";

type Mesaj = { kim: "ben" | "nova"; metin: string; denge?: boolean };

export function AsistanBalonu(p: { baglam: string; altBosluk: number; dengeAc?: () => void }) {
  const ic = useSafeAreaInsets();
  const [acik, setAcik] = useState(false);
  const [mesajlar, setMesajlar] = useState<Mesaj[]>([]);
  const [soru, setSoru] = useState("");
  const [bekle, setBekle] = useState(false);
  const kaydir = useRef<any>(null); // RN 0.88: ScrollView tipi işlev oldu

  const gonder = async () => {
    const s = soru.trim();
    if (!s || bekle) return;
    setSoru("");
    const gecmis = [...mesajlar, { kim: "ben" as const, metin: s }];
    setMesajlar(gecmis);
    setBekle(true);
    // Sitedeki gibi son üç soru-cevap bağlam olarak gider
    const onceki = mesajlar.slice(-6).map((m) => `${m.kim === "ben" ? "Kullanıcı" : "Nova"}: ${m.metin}`).join("\n");
    const metin = (onceki ? `Önceki konuşma:\n${onceki}\n\n` : "") + `Yeni soru: ${s}`;
    const r = await arka.yapayZeka("ask", metin, p.baglam);
    setBekle(false);
    // "Dün kaçamak yaptım" gibi bir cümleye cevabın altına dengeleme planı düğmesi eklenir
    setMesajlar([...gecmis, { kim: "nova", metin: r.tamam ? String(r.deger?.text ?? "") : hataMetni(r.hata), denge: r.tamam && kacamakMi(s) }]);
    setTimeout(() => kaydir.current?.scrollToEnd({ animated: true }), 50);
  };

  return (
    <>
      <Pressable testID="asistan-balonu" accessibilityRole="button" accessibilityLabel={t("Asistanı aç")}
        onPress={() => setAcik(true)}
        style={({ pressed }) => [s.balon, { bottom: p.altBosluk + ic.bottom }, pressed && { transform: [{ scale: 0.95 }] }]}>
        <Text style={s.balonYazi}>N</Text>
      </Pressable>

      <Modal visible={acik} animationType="slide" transparent onRequestClose={() => setAcik(false)}>
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined} style={{ flex: 1 }}>
          <Pressable style={{ flex: 0.12 }} onPress={() => setAcik(false)} />
          <View style={[s.panel, { paddingBottom: ic.bottom + 12 }]} testID="asistan-paneli">
            <View style={s.ust}>
              <View style={s.mini}><Text style={[s.balonYazi, { fontSize: 16 }]}>N</Text></View>
              <Yazi tur="baslik" s={{ fontSize: 20, flex: 1 }}>{t("Nova'ya sor")}</Yazi>
              <Dugme tur="yalin" yazi={t("Kapat")} bas={() => setAcik(false)} s={{ minHeight: 36 }} />
            </View>
            <ScrollView ref={kaydir} style={{ flex: 1 }} contentContainerStyle={{ paddingVertical: 8 }}>
              {mesajlar.length === 0 && <Yazi tur="soluk">{t("Beslenme ve antrenman soruların için. Genel bilgi verir, tıbbi tavsiye değildir.")}</Yazi>}
              {mesajlar.map((m, i) => (
                <View key={i} style={[s.mesaj, m.kim === "ben" ? s.benim : s.onun]} testID={`mesaj-${m.kim}`}>
                  <Yazi s={m.kim === "ben" ? { color: "#fff" } : undefined}>{m.metin}</Yazi>
                  {m.denge && p.dengeAc && <Dugme testID="asistan-denge" tur="ikincil" yazi={t("Dengeleme planını aç")}
                    bas={() => { setAcik(false); p.dengeAc!(); }} s={{ marginTop: 10, minHeight: 40 }} />}
                </View>
              ))}
              {bekle && <Yazi tur="soluk">{t("Nova yazıyor...")}</Yazi>}
            </ScrollView>
            <View style={{ flexDirection: "row", gap: 8, alignItems: "flex-start" }}>
              <View style={{ flex: 1 }}>
                <Girdi testID="asistan-girdi" value={soru} onChangeText={setSoru} placeholder={t("Bir şey sor...")} maxLength={1000} onSubmitEditing={gonder} />
              </View>
              <Dugme testID="asistan-gonder" yazi={t("Gönder")} bas={gonder} kapali={!soru.trim()} yukleniyor={bekle} />
            </View>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </>
  );
}

const s = temali(() => StyleSheet.create({
  balon: {
    position: "absolute", right: 18, width: 58, height: 58, borderRadius: 29, backgroundColor: R.murekkep,
    alignItems: "center", justifyContent: "center",
    shadowColor: "#000", shadowOpacity: 0.22, shadowRadius: 12, shadowOffset: { width: 0, height: 6 }, elevation: 8,
  },
  balonYazi: { color: R.zemin, fontSize: 24, fontWeight: "300", letterSpacing: 1 },
  mini: { width: 34, height: 34, borderRadius: 17, backgroundColor: R.murekkep, alignItems: "center", justifyContent: "center", marginRight: 10 },
  panel: { flex: 1, backgroundColor: R.panel, borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 20, paddingTop: 16 },
  ust: { flexDirection: "row", alignItems: "center", marginBottom: 8 },
  mesaj: { borderRadius: 16, paddingVertical: 10, paddingHorizontal: 14, marginBottom: 8, maxWidth: "88%" },
  benim: { backgroundColor: R.vurgu, alignSelf: "flex-end" },
  onun: { backgroundColor: R.girdi, alignSelf: "flex-start", borderWidth: StyleSheet.hairlineWidth, borderColor: R.cizgi },
}));
