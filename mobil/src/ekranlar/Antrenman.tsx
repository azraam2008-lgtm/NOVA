// Antrenman.tsx - "Antrenman" sekmesi: bugünkü hareket ve hareket kütüphanesi
import React, { useEffect, useState } from "react";
import { Pressable, StyleSheet, View } from "react-native";
import { t } from "../dil";
import { type Veri } from "../hesap";
import { EGZERSIZLER, egzersizAdi, kasAdi, tekrarMetni } from "../egzersizler";
import { Cip, Dugme, Girdi, Kart, R, SayfaBasligi, Yazi, temali } from "../bilesenler";
import { adimNotu, hareketKalorisi } from "./Bugun";
import { type AdimDurumu } from "../adim";
import { KocKarti } from "./Koc";

type Suzgec = "hepsi" | "yok" | "dambıl" | "barfiks";

export function AntrenmanSayfasi(p: { veri: Veri; tarih: string; guncelle: (f: (v: Veri) => Veri) => Promise<void>; adimDurumu?: AdimDurumu | null }) {
  const bugun = p.veri.aktivite_loglari?.[p.tarih] ?? {};
  const [adim, setAdim] = useState(String(bugun.adim ?? 0));
  const [ekKalori, setEkKalori] = useState(String(bugun.egzersiz_kalori ?? 0));
  const [kaydedildi, setKaydedildi] = useState(false);
  const [suzgec, setSuzgec] = useState<Suzgec>("hepsi");
  const [acik, setAcik] = useState<string | null>(null);
  // Koç bir antrenman kaydedince kutudaki egzersiz kalorisi de güncellensin
  useEffect(() => { setEkKalori(String(bugun.egzersiz_kalori ?? 0)); }, [bugun.egzersiz_kalori]);
  // Sensör yeni adım yazınca kutu da güncellensin
  useEffect(() => { setAdim(String(bugun.adim ?? 0)); }, [bugun.adim]);

  const kaydet = async () => {
    const a = Math.max(0, Math.min(100000, Math.round(Number(adim) || 0)));
    const e = Math.max(0, Math.min(2000, Math.round(Number(ekKalori) || 0)));
    await p.guncelle((v) => {
      const g = { su: 0, ...(v.aktivite_loglari?.[p.tarih] ?? {}), adim: a, egzersiz_kalori: e };
      return { ...v, aktivite_loglari: { ...v.aktivite_loglari, [p.tarih]: g } };
    });
    setKaydedildi(true);
  };

  const liste = EGZERSIZLER.filter((e) =>
    suzgec === "hepsi" ? true : suzgec === "yok" ? e.ekipman.length === 0 : e.ekipman.includes(suzgec));
  const seviyeRengi = { "başlangıç": R.protein, orta: R.karb, ileri: R.yag } as const;

  return (
    <View testID="sayfa-antrenman">
      <SayfaBasligi baslik={t("Antrenman")} />

      <Kart>
        <Yazi s={{ fontWeight: "700", fontSize: 17, marginBottom: 4 }}>{t("Bugünkü hareketin")}</Yazi>
        <Yazi tur="soluk" s={{ marginBottom: 12 }}>{t("Hareketle kazandıkların")}: + {Math.round(hareketKalorisi(p.veri, p.tarih))} kcal</Yazi>
        <View style={{ flexDirection: "row", gap: 10 }}>
          <View style={{ flex: 1 }}>
            <Girdi testID="adim-girdi" etiket={t("Adım")} value={adim} keyboardType="number-pad" onChangeText={(m) => { setAdim(m); setKaydedildi(false); }} />
          </View>
          <View style={{ flex: 1 }}>
            <Girdi testID="egzersiz-girdi" etiket={t("Egzersiz (kcal)")} value={ekKalori} keyboardType="number-pad" onChangeText={(m) => { setEkKalori(m); setKaydedildi(false); }} />
          </View>
        </View>
        {(p.adimDurumu === "var" || p.adimDurumu === "izin_yok") &&
          <Yazi tur="soluk" s={{ marginTop: -4, marginBottom: 10, fontSize: 13 }}>{adimNotu(p.adimDurumu)}</Yazi>}
        <Dugme testID="hareket-kaydet" yazi={t(kaydedildi ? "Kaydedildi" : "Kaydet")} bas={kaydet} kapali={kaydedildi} />
      </Kart>

      <KocKarti veri={p.veri} tarih={p.tarih} guncelle={p.guncelle} kaydedildi={() => setKaydedildi(true)} />

      {(bugun.antrenmanlar ?? []).length > 0 && (
        <Kart testID="bugunku-antrenman">
          <Yazi s={{ fontWeight: "700", fontSize: 17, marginBottom: 4 }}>{t("Bugünkü antrenmanın")}</Yazi>
          {(bugun.antrenmanlar as any[]).map((a, i) => (
            <View key={i} style={{ marginTop: 6 }}>
              <Yazi s={{ fontWeight: "600" }}>{a.gun} · {a.hareketler.reduce((s: number, h: any) => s + Number(h.sets_done || 0), 0)} {t("set")}</Yazi>
              {a.hareketler.map((h: any, j: number) => {
                const e = EGZERSIZLER.find((z) => z.id === h.id);
                return <Yazi key={j} tur="soluk" s={{ fontSize: 14 }}>{e ? egzersizAdi(e) : h.name} · {h.sets_done} {t("set")}{h.reps ? ` (${h.reps})` : ""}</Yazi>;
              })}
            </View>
          ))}
        </Kart>
      )}

      <Yazi s={{ fontWeight: "700", fontSize: 20, marginVertical: 10 }}>{t("Hareket kütüphanesi")}</Yazi>
      <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 14 }}>
        {([["hepsi", "Hepsi"], ["yok", "Ekipmansız"], ["dambıl", "Dambıl"], ["barfiks", "Barfiks barı"]] as [Suzgec, string][]).map(([k, ad]) =>
          <Cip key={k} testID={`suzgec-${k}`} yazi={t(ad)} secili={suzgec === k} bas={() => setSuzgec(k)} />)}
      </View>

      {liste.map((e) => (
        <Pressable key={e.id} testID={`egzersiz-${e.id}`} onPress={() => setAcik(acik === e.id ? null : e.id)} accessibilityRole="button">
          <Kart s={{ paddingVertical: 16 }}>
            <View style={s.satir}>
              <Yazi s={{ fontWeight: "700", flex: 1 }}>{egzersizAdi(e)}</Yazi>
              <View style={[s.seviye, { borderColor: seviyeRengi[e.seviye] }]}>
                <Yazi s={{ fontSize: 12, color: seviyeRengi[e.seviye], fontWeight: "700" }}>{t(e.seviye === "başlangıç" ? "Başlangıç" : e.seviye === "orta" ? "Orta" : "İleri seviye")}</Yazi>
              </View>
            </View>
            <Yazi tur="soluk" s={{ marginTop: 4 }}>{e.kas.map(kasAdi).join(", ")} · {e.set} {t("set")} × {tekrarMetni(e)}</Yazi>
            {acik === e.id && (
              <View style={s.video}>
                <Yazi tur="soluk" s={{ textAlign: "center" }}>{t("Hareket videosu yakında burada olacak.")}</Yazi>
              </View>
            )}
          </Kart>
        </Pressable>
      ))}
    </View>
  );
}

const s = temali(() => StyleSheet.create({
  satir: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", gap: 10 },
  seviye: { borderWidth: 1, borderRadius: 99, paddingHorizontal: 10, paddingVertical: 3 },
  video: { marginTop: 12, height: 120, borderRadius: 14, borderWidth: 1, borderStyle: "dashed", borderColor: R.cizgi, alignItems: "center", justifyContent: "center", padding: 12 },
}));
