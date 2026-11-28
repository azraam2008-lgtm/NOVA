// TemaSecici.tsx - Altı arka planı küçük resimleriyle gösterir
import React from "react";
import { Image, Pressable, StyleSheet, Text, View } from "react-native";
import { t } from "../dil";
import { TEMALAR } from "../tema";
import { R, temali } from "../bilesenler";

export function TemaSecici(p: { secili: string; sec: (ad: string) => void }) {
  return (
    <View style={s.izgara}>
      {TEMALAR.map((x) => {
        const secili = p.secili === x.ad;
        return (
          <Pressable key={x.ad} testID={`tema-${x.ad}`} onPress={() => p.sec(x.ad)} accessibilityRole="button"
            accessibilityLabel={t(x.ad)} accessibilityState={{ selected: secili }} style={[s.kutu, secili && s.secili]}>
            <Image source={x.resim} style={s.resim} resizeMode="cover" />
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
  izgara: { flexDirection: "row", flexWrap: "wrap", gap: 10 },
  kutu: { width: "31%", aspectRatio: 0.62, borderRadius: 16, overflow: "hidden", borderWidth: 2, borderColor: "transparent" },
  secili: { borderColor: R.murekkep },
  resim: { width: "100%", height: "100%", position: "absolute" },
  etiket: { position: "absolute", left: 0, right: 0, bottom: 0, paddingVertical: 6, paddingHorizontal: 6 },
  etiketYazi: { fontSize: 11, fontWeight: "700", textAlign: "center" },
}));
