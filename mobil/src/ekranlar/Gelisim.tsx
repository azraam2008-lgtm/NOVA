// Gelisim.tsx - "Gelişim" sekmesi: kalori grafiği, kilo takibi, makro ortalamaları
import React, { useState } from "react";
import { StyleSheet, View } from "react-native";
import { aktifDil, t } from "../dil";
import { bugunMetni, gunToplami, type Veri } from "../hesap";
import { Cip, Cubuk, Dugme, Girdi, Kart, R, SayfaBasligi, Yazi, temali } from "../bilesenler";

function gunler(sayi: number): string[] {
  const l: string[] = [];
  for (let i = sayi - 1; i >= 0; i--) {
    const d = new Date(); d.setDate(d.getDate() - i); l.push(bugunMetni(d));
  }
  return l;
}

export function GelisimSayfasi(p: { veri: Veri; hedef: number; guncelle: (f: (v: Veri) => Veri) => Promise<void> }) {
  const [donem, setDonem] = useState(7);
  const [kiloMetni, setKiloMetni] = useState(String(p.veri.profil.mevcut_kilo ?? ""));
  const [kaydedildi, setKaydedildi] = useState(false);
  const pr = p.veri.profil;

  const liste = gunler(donem).map((g) => ({ g, ...gunToplami(p.veri.gunluk_kayitlar, g) }));
  const dolu = liste.filter((x) => x.kalori > 0);
  const ort = (f: (x: (typeof liste)[0]) => number) => (dolu.length ? dolu.reduce((a, x) => a + f(x), 0) / dolu.length : 0);
  const enYuksek = Math.max(p.hedef * 1.25, ...liste.map((x) => x.kalori));
  const hedefAlti = dolu.filter((x) => x.kalori <= p.hedef).length;

  const kiloGecmisi = [...((pr.kilo_gecmisi as { tarih: string; kilo: number }[]) ?? [])].sort((a, b) => a.tarih.localeCompare(b.tarih));
  const kaydet = async () => {
    const k = Number(kiloMetni.replace(",", "."));
    if (!(k >= 30 && k <= 250)) return;
    const bugun = bugunMetni();
    await p.guncelle((v) => {
      const gecmis = ((v.profil.kilo_gecmisi as any[]) ?? []).filter((x) => x.tarih !== bugun);
      return { ...v, profil: { ...v.profil, mevcut_kilo: k, son_tarti_tarihi: bugun, kilo_gecmisi: [...gecmis, { tarih: bugun, kilo: k }] } };
    });
    setKaydedildi(true);
  };
  const ilkKilo = kiloGecmisi[0]?.kilo ?? Number(pr.mevcut_kilo);
  const fark = Number(pr.mevcut_kilo) - ilkKilo;
  const hedefeKalan = Number(pr.mevcut_kilo) - Number(pr.hedef_kilo);
  const gunAdi = (g: string) => new Intl.DateTimeFormat(aktifDil(), donem === 7 ? { weekday: "narrow" } : { day: "numeric" }).format(new Date(g + "T12:00:00"));

  return (
    <View testID="sayfa-gelisim">
      <SayfaBasligi baslik={t("Gelişim")} />
      <View style={{ flexDirection: "row", gap: 8, marginBottom: 14 }}>
        {[7, 30].map((d) => <Cip key={d} testID={`donem-${d}`} yazi={t(d === 7 ? "Son 7 gün" : "Son 30 gün")} secili={donem === d} bas={() => setDonem(d)} />)}
      </View>

      <Kart testID="kalori-grafigi">
        <Yazi s={{ fontWeight: "700", fontSize: 17, marginBottom: 4 }}>{t("Günlük kalori")}</Yazi>
        <Yazi tur="soluk" s={{ marginBottom: 14 }}>{t("Ortalama")}: {Math.round(ort((x) => x.kalori))} kcal · {t("Hedef")}: {Math.round(p.hedef)} kcal</Yazi>
        <View style={s.grafik}>
          <View style={[s.hedefCizgisi, { bottom: `${(p.hedef / enYuksek) * 100}%` }]} />
          {liste.map((x) => (
            <View key={x.g} style={s.sutunKutu}>
              <View style={s.sutunAlan}>
                <View style={[s.sutun, { height: `${(x.kalori / enYuksek) * 100}%`, backgroundColor: x.kalori > p.hedef ? R.yag : R.murekkep }]} />
              </View>
              {(donem === 7 || Number(x.g.slice(8)) % 5 === 1) && <Yazi tur="soluk" s={s.gunYazi}>{gunAdi(x.g)}</Yazi>}
            </View>
          ))}
        </View>
        <View style={[s.satir, { marginTop: 12 }]}>
          <Yazi tur="soluk">{t("Kayıt girilen gün")}: {dolu.length}/{donem}</Yazi>
          <Yazi tur="soluk">{t("Hedefin altında")}: {hedefAlti}</Yazi>
        </View>
      </Kart>

      <Kart testID="kilo-karti">
        <Yazi s={{ fontWeight: "700", fontSize: 17, marginBottom: 10 }}>{t("Kilo")}</Yazi>
        <View style={s.satir}>
          <View><Yazi tur="soluk">{t("Şimdi")}</Yazi><Yazi s={s.sayi}>{Number(pr.mevcut_kilo).toFixed(1)} kg</Yazi></View>
          <View><Yazi tur="soluk">{t("Hedef")}</Yazi><Yazi s={s.sayi}>{Number(pr.hedef_kilo).toFixed(1)} kg</Yazi></View>
          <View><Yazi tur="soluk">{t("Hedefe kalan")}</Yazi><Yazi s={s.sayi}>{Math.abs(hedefeKalan).toFixed(1)} kg</Yazi></View>
        </View>
        {kiloGecmisi.length > 1 && (
          <Yazi tur="soluk" s={{ marginTop: 10 }}>
            {t("İlk kayıttan bu yana")}: {fark > 0 ? "+" : ""}{fark.toFixed(1)} kg
          </Yazi>
        )}
        <View style={{ height: 14 }} />
        <Girdi testID="kilo-girdi" etiket={t("Bugünkü kilon (kg)")} value={kiloMetni} keyboardType="decimal-pad"
          onChangeText={(m) => { setKiloMetni(m); setKaydedildi(false); }} />
        <Dugme testID="kilo-kaydet" yazi={t(kaydedildi ? "Kaydedildi" : "Kilomu kaydet")} bas={kaydet} kapali={kaydedildi} />
        {kiloGecmisi.slice(-5).reverse().map((k) => (
          <View key={k.tarih} style={[s.satir, s.kalem]}>
            <Yazi tur="soluk">{new Intl.DateTimeFormat(aktifDil(), { day: "numeric", month: "long" }).format(new Date(k.tarih + "T12:00:00"))}</Yazi>
            <Yazi>{Number(k.kilo).toFixed(1)} kg</Yazi>
          </View>
        ))}
        {kiloGecmisi.length === 0 && <Yazi tur="soluk" s={{ marginTop: 10 }}>{t("Henüz kilo kaydın yok.")}</Yazi>}
      </Kart>

      <Kart>
        <Yazi s={{ fontWeight: "700", fontSize: 17, marginBottom: 12 }}>{t("Ortalama makrolar")}</Yazi>
        {([["Protein", ort((x) => x.protein), (p.hedef * 0.3) / 4, R.protein],
          ["Karbonhidrat", ort((x) => x.karb), (p.hedef * 0.4) / 4, R.karb],
          ["Yağ", ort((x) => x.yag), (p.hedef * 0.3) / 9, R.yag]] as [string, number, number, string][]).map(([ad, g, h, renk]) => (
          <View key={ad} style={{ marginBottom: 12 }}>
            <View style={[s.satir, { marginBottom: 6 }]}><Yazi tur="soluk">{t(ad)}</Yazi><Yazi>{Math.round(g)} / {Math.round(h)} g</Yazi></View>
            <Cubuk oran={g / h} renk={renk} yukseklik={6} />
          </View>
        ))}
      </Kart>
    </View>
  );
}

const s = temali(() => StyleSheet.create({
  satir: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  grafik: { height: 150, flexDirection: "row", alignItems: "flex-end", gap: 3, position: "relative" },
  hedefCizgisi: { position: "absolute", left: 0, right: 0, borderTopWidth: 1, borderStyle: "dashed", borderTopColor: R.su },
  sutunKutu: { flex: 1, height: "100%", alignItems: "center" },
  sutunAlan: { flex: 1, width: "100%", justifyContent: "flex-end" },
  sutun: { width: "100%", borderRadius: 4, minHeight: 2 },
  gunYazi: { fontSize: 10, marginTop: 4 },
  sayi: { fontWeight: "700", fontSize: 18, marginTop: 2 },
  kalem: { marginTop: 10, paddingTop: 10, borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: R.cizgi },
}));
