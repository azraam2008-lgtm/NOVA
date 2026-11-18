// EklePaneli.tsx - Tek "Ekle" düğmesinin açtığı panel
// Bütün ekleme yolları burada toplanır; ana ekranda ayrı ayrı durmazlar.
// Bu aşamada: Ara (internetsiz) ve Yazarak anlat (Nova hesaplar).
// Barkod, Fotoğraf ve Tarif Aşama C'de aynı panele eklenecek.
import React, { useMemo, useState } from "react";
import { ActivityIndicator, Modal, Pressable, ScrollView, StyleSheet, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { t } from "../dil";
import { kayitYap, kcal, ogunler, type Kayit, type Profil } from "../hesap";
import { yemekAra, type Yemek } from "../yemekler";
import { arka } from "../veri";
import { Dugme, Girdi, Hata, R, Secenek, Yazi, hataMetni } from "../bilesenler";

type Kip = "menu" | "ara" | "anlat";

export function varsayilanOgun(p: Profil, saat = new Date().getHours()): string {
  const l = ogunler(p);
  if (p.oruc_modu) return saat < 12 ? l[0] : saat < 22 ? l[1] : l[2];
  return saat < 11 ? l[0] : saat < 16 ? l[1] : saat < 21 ? l[2] : l[3];
}

function OgunSecici(p: { profil: Profil; ogun: string; sec: (o: string) => void }) {
  return (
    <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 6 }}>
      {ogunler(p.profil).map((o) => (
        <Pressable key={o} onPress={() => p.sec(o)} accessibilityRole="button" accessibilityState={{ selected: p.ogun === o }}
          style={[s.cip, p.ogun === o && s.cipSecili]}>
          <Yazi s={[s.cipYazi, p.ogun === o && { color: R.vurgu, fontWeight: "700" }]}>{t(o)}</Yazi>
        </Pressable>
      ))}
    </View>
  );
}

export function EklePaneli(p: {
  acik: boolean; kapat: () => void; profil: Profil; tarih: string; baglam: string;
  ekle: (kayitlar: Kayit[]) => Promise<void>;
}) {
  const ic = useSafeAreaInsets();
  const [kip, setKip] = useState<Kip>("menu");
  const [ogun, setOgun] = useState(varsayilanOgun(p.profil));
  const [sorgu, setSorgu] = useState("");
  const [secilen, setSecilen] = useState<Yemek | null>(null);
  const [gram, setGram] = useState("100");
  const [anlatim, setAnlatim] = useState("");
  const [tahmin, setTahmin] = useState<any[] | null>(null);
  const [bekle, setBekle] = useState(false);
  const [hata, setHata] = useState<string | null>(null);
  const [bilgi, setBilgi] = useState<string | null>(null);

  const sonuclar = useMemo(() => (kip === "ara" ? yemekAra(sorgu) : []), [kip, sorgu]);

  const sifirla = () => {
    setKip("menu"); setSorgu(""); setSecilen(null); setAnlatim(""); setTahmin(null); setHata(null); setBilgi(null);
  };
  const kapat = () => { sifirla(); p.kapat(); };

  const ekleVeKapat = async (k: Kayit[]) => {
    setBekle(true); setHata(null);
    try { await p.ekle(k); kapat(); }
    catch { setHata(t("Bir sorun çıktı. Biraz sonra tekrar dene.")); }
    setBekle(false);
  };

  const hesapla = async () => {
    setBekle(true); setHata(null); setTahmin(null);
    const r = await arka.yapayZeka("voice", anlatim, p.baglam);
    setBekle(false);
    if (!r.tamam) return setHata(hataMetni(r.hata));
    if (!r.deger?.is_food || !(r.deger.items ?? []).length) return setHata(t("Bu bir yiyecek gibi görünmüyor."));
    setTahmin(r.deger.items);
  };

  const MENU: { kip: Kip | null; yazi: string; id: string }[] = [
    { kip: "ara", yazi: "Ara", id: "ara" },
    { kip: "anlat", yazi: "Yazarak anlat", id: "anlat" },
    { kip: null, yazi: "Barkod", id: "barkod" },
    { kip: null, yazi: "Fotoğraf", id: "fotograf" },
    { kip: null, yazi: "Tarif", id: "tarif" },
  ];

  return (
    <Modal visible={p.acik} transparent animationType="slide" onRequestClose={kapat}>
      <Pressable style={s.perde} onPress={kapat} accessibilityLabel={t("Kapat")} />
      <View style={[s.panel, { paddingBottom: ic.bottom + 16 }]} testID="ekle-paneli">
        <View style={s.tutamac} />
        <View style={s.ust}>
          <Yazi tur="baslik" s={{ fontSize: 20, flex: 1 }}>{t(kip === "menu" ? "Ne eklemek istersin?" : kip === "ara" ? "Yemek ara" : "Ne yediğini anlat")}</Yazi>
          <Dugme tur="yalin" yazi={kip === "menu" ? t("Kapat") : t("Geri")} bas={() => (kip === "menu" ? kapat() : (secilen ? setSecilen(null) : sifirla()))} s={{ minHeight: 36 }} />
        </View>

        <ScrollView keyboardShouldPersistTaps="handled" style={{ maxHeight: 520 }}>
          {kip === "menu" && (
            <View style={s.izgara}>
              {MENU.map((m) => (
                <Pressable key={m.id} testID={`ekle-${m.id}`} disabled={!m.kip} onPress={() => m.kip && setKip(m.kip)}
                  accessibilityRole="button" accessibilityState={{ disabled: !m.kip }}
                  style={({ pressed }) => [s.kutu, !m.kip && { opacity: 0.45 }, pressed && { opacity: 0.8 }]}>
                  <Yazi s={{ fontSize: 16, fontWeight: "700" }}>{t(m.yazi)}</Yazi>
                  {!m.kip && <Yazi tur="soluk">{t("Yakında")}</Yazi>}
                </Pressable>
              ))}
            </View>
          )}

          {kip === "ara" && !secilen && (
            <>
              <Girdi testID="arama-girdi" value={sorgu} onChangeText={setSorgu} placeholder={t("Yemek ara")} autoFocus autoCorrect={false} />
              {sorgu.trim().length >= 2 && sonuclar.length === 0 && <Yazi tur="soluk">{t("Bulamadım. \"Yazarak anlat\" seçeneğini dene.")}</Yazi>}
              {sonuclar.map((y, i) => (
                <Pressable key={`${y.ad}-${i}`} testID={`sonuc-${i}`} style={s.sonuc} accessibilityRole="button"
                  onPress={() => { setSecilen(y); setGram(String(y.g || 100)); }}>
                  <Yazi s={{ fontWeight: "600" }}>{y.ad}</Yazi>
                  <Yazi tur="soluk">{y.por ? `${y.por} · ` : ""}{y.g} g · {Math.round(kcal(y.p, y.k, y.y) * y.g / 100)} kcal</Yazi>
                </Pressable>
              ))}
            </>
          )}

          {kip === "ara" && secilen && (() => {
            const g = Number(gram.replace(",", ".")) || 0;
            const k = kayitYap(secilen.ad, g, p.tarih, ogun, secilen.p, secilen.k, secilen.y, secilen.ek);
            return (
              <View testID="secilen-yemek">
                <Yazi tur="baslik" s={{ fontSize: 20 }}>{secilen.ad}</Yazi>
                <Yazi tur="soluk" s={{ marginBottom: 12 }}>{secilen.kaynak}</Yazi>
                <Girdi testID="gram-girdi" etiket={t("gram")} value={gram} onChangeText={setGram} keyboardType="decimal-pad" />
                <Yazi s={{ marginBottom: 12 }}>{k.Kalori} kcal · {t("Protein")} {k.Protein} g · {t("Karbonhidrat")} {k.Karbonhidrat} g · {t("Yağ")} {k.Yağ} g</Yazi>
                <Yazi tur="alt" s={{ marginBottom: 8 }}>{t("Hangi öğün?")}</Yazi>
                <OgunSecici profil={p.profil} ogun={ogun} sec={setOgun} />
                <Hata metin={hata} />
                <Dugme testID="yemek-ekle" yazi={t("Ekle")} bas={() => ekleVeKapat([k])} kapali={g <= 0} yukleniyor={bekle} s={{ marginTop: 8 }} />
              </View>
            );
          })()}

          {kip === "anlat" && (
            <>
              <Girdi testID="anlat-girdi" value={anlatim} onChangeText={setAnlatim} multiline maxLength={600}
                placeholder={t("Örnek: 2 yumurta, 1 dilim peynir ve bir bardak çay")} style={{ minHeight: 90, paddingTop: 12, textAlignVertical: "top" }} />
              {!tahmin && <Dugme testID="anlat-hesapla" yazi={t("Hesapla")} bas={hesapla} yukleniyor={bekle} kapali={anlatim.trim().length < 3} />}
              {bekle && <View style={{ flexDirection: "row", gap: 8, marginTop: 10 }}><ActivityIndicator /><Yazi tur="soluk">{t("Nova hesaplıyor...")}</Yazi></View>}
              <Hata metin={hata} />
              {tahmin && (() => {
                const kayitlar = tahmin.map((it) => kayitYap(it.name, Number(it.grams) || 0, p.tarih, ogun,
                  Number(it.protein_per_100g) || 0, Number(it.carbs_per_100g) || 0, Number(it.fat_per_100g) || 0));
                const top = kayitlar.reduce((a, k) => a + k.Kalori, 0);
                return (
                  <View testID="tahmin">
                    <Yazi tur="alt" s={{ marginVertical: 8 }}>{t("Tahmin")}: {top} kcal</Yazi>
                    {kayitlar.map((k, i) => <Yazi key={i} s={{ marginBottom: 4 }}>{k.Tarif} · {k.Kalori} kcal</Yazi>)}
                    <Yazi tur="alt" s={{ marginVertical: 8 }}>{t("Hangi öğün?")}</Yazi>
                    <OgunSecici profil={p.profil} ogun={ogun} sec={setOgun} />
                    <Dugme testID="tahmin-ekle" yazi={t("Bunları ekle")} bas={() => ekleVeKapat(kayitlar)} yukleniyor={bekle} s={{ marginTop: 8 }} />
                  </View>
                );
              })()}
            </>
          )}
          {bilgi && <Yazi>{bilgi}</Yazi>}
        </ScrollView>
      </View>
    </Modal>
  );
}

const s = StyleSheet.create({
  perde: { flex: 1, backgroundColor: "rgba(10,12,16,0.35)" },
  panel: { backgroundColor: R.zemin, borderTopLeftRadius: 24, borderTopRightRadius: 24, paddingHorizontal: 20, paddingTop: 10 },
  tutamac: { alignSelf: "center", width: 40, height: 5, borderRadius: 3, backgroundColor: R.cizgi, marginBottom: 10 },
  ust: { flexDirection: "row", alignItems: "center", marginBottom: 12 },
  izgara: { flexDirection: "row", flexWrap: "wrap", gap: 10 },
  kutu: { width: "48%", minHeight: 76, backgroundColor: R.kart, borderRadius: 16, padding: 14, justifyContent: "center", borderWidth: StyleSheet.hairlineWidth, borderColor: R.cizgi },
  sonuc: { backgroundColor: R.kart, borderRadius: 12, padding: 14, marginBottom: 8, borderWidth: StyleSheet.hairlineWidth, borderColor: R.cizgi },
  cip: { borderWidth: 1, borderColor: R.cizgi, backgroundColor: "#fff", borderRadius: 99, paddingVertical: 8, paddingHorizontal: 14 },
  cipSecili: { borderColor: R.vurgu, backgroundColor: R.vurguAcik },
  cipYazi: { fontSize: 14 },
});
