// TemaSecici.tsx - Altı arka planı küçük resimleriyle gösterir
import React, { useState } from "react";
import { Image, Pressable, StyleSheet, Text, View } from "react-native";
import { t } from "../dil";
import { TEMALAR } from "../tema";
import { R, temali } from "../bilesenler";

const ARA = 10;

export function TemaSecici(p: { secili: string; sec: (ad: string) => void }) {
  // Kutu boyu pikselle verilir: iPhone'da yüzde genişlik + en-boy oranı kutuyu sıfır yüksekliğe indirip
  // yalnızca kenar çizgisini bırakabiliyordu. Önce ızgaranın genişliği ölçülür.
  const [genislik, setGenislik] = useState(0);
  const en = genislik > 0 ? Math.floor((genislik - ARA * 2) / 3) : 0;
  const boy = Math.round(en / 0.62);
  return (
    <View style={s.izgara} onLayout={(e) => setGenislik(e.nativeEvent.layout.width)}>
      {en > 0 && TEMALAR.map((x) => {
        const secili = p.secili === x.ad;
        return (
          <Pressable key={x.ad} testID={`tema-${x.ad}`} onPress={() => p.sec(x.ad)} accessibilityRole="button"
            accessibilityLabel={t(x.ad)} accessibilityState={{ selected: secili }} style={[s.kutu, { width: en, height: boy }, secili && s.secili]}>
            <Image source={x.resim} style={{ position: "absolute", width: en, height: boy }} resizeMode="cover" />
            <View style={[s.etiket, { backgroundColor: x.kart }]}>
              <Text numberOfLines={1} style={[s.etiketYazi, { color: x.yazi }]}>{t(x.ad)}</Text>
            </View>
          </Pressable>
        );
      })}
    </View>
  );
}

const s = temali(() => StyleSheet.create({
  izgara: { flexDirection: "row", flexWrap: "wrap", gap: ARA, width: "100%", minHeight: 40 },
  kutu: { borderRadius: 16, overflow: "hidden", borderWidth: 2, borderColor: "transparent" },
  secili: { borderColor: R.murekkep },
  etiket: { position: "absolute", left: 0, right: 0, bottom: 0, paddingVertical: 6, paddingHorizontal: 6 },
  etiketYazi: { fontSize: 11, fontWeight: "700", textAlign: "center" },
}));
