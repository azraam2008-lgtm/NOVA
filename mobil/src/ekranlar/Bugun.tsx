// Bugun.tsx - "Bugün" sekmesi: günün özeti, su ve öğünler
// Kalan kalori sitedeki gibi: hedef - yenen + hareketle kazanılan (adım x 0,04 + egzersiz)
import React from "react";
import { Pressable, StyleSheet, View } from "react-native";
import { aktifDil, t } from "../dil";
import { bugunMetni, gunToplami, ogunler, type Kayit, type Veri } from "../hesap";
import { Cubuk, Dugme, Halka, Kart, R, SayfaBasligi, Yazi, temali } from "../bilesenler";
import { MikroKarti, OrucKarti } from "./GunKartlari";
import { DengeKarti } from "./Denge";
import { gunHedefi } from "../denge";
import { type AdimDurumu } from "../adim";

/** Adım kartının altındaki not: sayının nereden geldiği ya da nasıl otomatik alınacağı */
export function adimNotu(d: AdimDurumu | null | undefined): string {
  if (d === "var") return t("iPhone'un hareket sensöründen otomatik alınıyor.");
  if (d === "izin_yok") return t("Adımlarını otomatik almak için iPhone Ayarlar > Gizlilik ve Güvenlik > Hareket ve Fitness'tan izin ver.");
  return t("Adımını Antrenman sekmesinden girebilirsin.");
}

export function hareketKalorisi(v: Veri, tarih: string) {
  const a = v.aktivite_loglari?.[tarih] ?? {};
  return Number(a.adim ?? 0) * 0.04 + Number(a.egzersiz_kalori ?? 0);
}

export function BugunSayfasi(p: { veri: Veri; tarih: string; hedef: number; guncelle: (f: (v: Veri) => Veri) => Promise<void>; dengeTetik?: number; adimDurumu?: AdimDurumu | null }) {
  const pr = p.veri.profil;
  const gun = gunToplami(p.veri.gunluk_kayitlar, p.tarih);
  const hareket = hareketKalorisi(p.veri, p.tarih);
  const kalan = Math.round(p.hedef - gun.kalori + hareket);
  const su = Number(p.veri.aktivite_loglari?.[p.tarih]?.su ?? 0);
  const adim = Number(p.veri.aktivite_loglari?.[p.tarih]?.adim ?? 0);
  const dunTarih = (() => { const d = new Date(p.tarih + "T12:00:00"); d.setDate(d.getDate() - 1); return bugunMetni(d); })();
  const dun = p.veri.gunluk_kayitlar.filter((k) => k.Tarih === dunTarih);
  // Dünkü aynı öğünü bugüne kopyalar (sık yenen kahvaltılar için)
  const kopyala = (o: string) => p.guncelle((v) => ({
    ...v, gunluk_kayitlar: [...v.gunluk_kayitlar, ...v.gunluk_kayitlar.filter((k) => k.Tarih === dunTarih && k.Öğün === o).map((k) => ({ ...k, Tarih: p.tarih }))],
  }));
  const tarihYazisi = new Intl.DateTimeFormat(aktifDil(), { weekday: "long", day: "numeric", month: "long" }).format(new Date());

  const sil = (k: Kayit) => p.guncelle((v) => {
    const i = v.gunluk_kayitlar.findIndex((x) => x.Tarih === k.Tarih && x.Öğün === k.Öğün && x.Tarif === k.Tarif && x.Kalori === k.Kalori);
    return i < 0 ? v : { ...v, gunluk_kayitlar: v.gunluk_kayitlar.filter((_, j) => j !== i) };
  });
  const suDegistir = (fark: number) => p.guncelle((v) => {
    const g = { adim: 0, su: 0, egzersiz_kalori: 0, ...(v.aktivite_loglari?.[p.tarih] ?? {}) };
    g.su = Math.max(0, Math.round((Number(g.su) + fark) * 100) / 100);
    return { ...v, aktivite_loglari: { ...v.aktivite_loglari, [p.tarih]: g } };
  });

  // Makro hedefleri sitedekiyle aynı: %30 protein, %40 karbonhidrat, %30 yağ
  const makro = (ad: string, g: number, hedefG: number, renk: string) => (
    <View style={{ flex: 1 }}>
      <Yazi tur="alt">{t(ad)}</Yazi>
      <Yazi s={{ fontWeight: "700", marginVertical: 4 }}>{Math.round(g)} / {Math.round(hedefG)} g</Yazi>
      <Cubuk oran={g / hedefG} renk={renk} yukseklik={6} />
    </View>
  );
  const satir = (ad: string, deger: string, renk: string) => (
    <View style={s.satir}>
      <View style={{ flexDirection: "row", alignItems: "center", gap: 8, flex: 1 }}>
        <View style={[s.isaret, { backgroundColor: renk }]} />
        <Yazi tur="soluk" s={{ fontSize: 14 }}>{t(ad)}</Yazi>
      </View>
      <Yazi s={{ fontWeight: "700", color: renk }}>{deger}</Yazi>
    </View>
  );

  return (
    <View testID="sayfa-bugun">
      <SayfaBasligi baslik={`${t("Merhaba")}, ${pr.ad ?? ""}`} alt={tarihYazisi} />

      {/* Sitedeki "Günlük Aktivite ve Su Halkaları": 10.000 adım ve 2,5 litre */}
      <Kart testID="halkalar">
        <View style={s.halkalar}>
          <View style={s.halkaSutun}>
            <Halka testID="adim" oran={adim / 10000} renk={R.halkaAdim} deger={adim.toLocaleString(aktifDil())} etiket={t("Adım")} />
          </View>
          <View style={s.halkaSutun}>
            <Halka testID="su" oran={su / 2.5} renk={R.halkaSu} deger={`${su.toFixed(2)} L`} etiket={t("Su")} />
            <View style={{ flexDirection: "row", gap: 8, marginTop: 10 }}>
              <Dugme tur="ikincil" yazi="−" bas={() => suDegistir(-0.25)} kapali={su <= 0} s={s.kare} testID="su-eksi" />
              <Dugme tur="ikincil" yazi="+" bas={() => suDegistir(0.25)} s={s.kare} testID="su-arti" />
            </View>
            <Yazi tur="soluk" s={{ marginTop: 4 }}>{Math.round(su / 0.25)} {t("bardak")}</Yazi>
          </View>
        </View>
        <Yazi tur="soluk" s={{ marginTop: 12, fontSize: 13, textAlign: "center" }}>{adimNotu(p.adimDurumu)}</Yazi>
      </Kart>

      {!!pr.oruc_modu && <OrucKarti profil={pr} su={su} />}

      <Kart testID="ozet">
        <Yazi tur="alt">{t(kalan >= 0 ? "kcal kaldı" : "kcal fazla")}</Yazi>
        <Yazi tur="buyuk" testID="kalan" s={kalan < 0 ? { color: R.hata } : undefined}>{Math.abs(kalan)}</Yazi>
        <View style={{ marginVertical: 12 }}><Cubuk oran={gun.kalori / (p.hedef + hareket)} renk={kalan < 0 ? R.hata : R.murekkep} yukseklik={10} /></View>
        {satir(gunHedefi(pr, p.tarih).dusus > 0 ? "Günlük hedefin (dengeleme)" : "Günlük hedefin", `${Math.round(p.hedef)} kcal`, R.su)}
        {satir("Yediklerin", `− ${Math.round(gun.kalori)} kcal`, R.yag)}
        {satir("Hareketle kazandıkların", `+ ${Math.round(hareket)} kcal`, R.protein)}
      </Kart>

      <DengeKarti veri={p.veri} tarih={p.tarih} guncelle={p.guncelle} acTetik={p.dengeTetik} />

      <Kart>
        <View style={[s.satir, { gap: 14, marginTop: 0 }]}>
          {makro("Protein", gun.protein, (p.hedef * 0.3) / 4, R.protein)}
          {makro("Karbonhidrat", gun.karb, (p.hedef * 0.4) / 4, R.karb)}
          {makro("Yağ", gun.yag, (p.hedef * 0.3) / 9, R.yag)}
        </View>
      </Kart>

      <MikroKarti kayitlar={gun.kayitlar} />

      {ogunler(pr).map((o) => {
        const liste = gun.kayitlar.filter((k) => k.Öğün === o);
        const top = liste.reduce((a, k) => a + Number(k.Kalori || 0), 0);
        return (
          <Kart key={o} testID={`ogun-${o}`}>
            <View style={[s.satir, { marginTop: 0 }]}>
              <Yazi s={{ fontWeight: "700", fontSize: 17 }}>{t(o)}</Yazi>
              <Yazi tur="soluk">{Math.round(top)} kcal</Yazi>
            </View>
            {liste.length === 0 && dun.some((k) => k.Öğün === o) && (
              <Dugme testID={`kopyala-${o}`} tur="ikincil" yazi={`${t("Dünden kopyala")} (${dun.filter((k) => k.Öğün === o).length})`}
                bas={() => kopyala(o)} s={{ marginTop: 10, minHeight: 40 }} />
            )}
            {liste.length === 0
              ? <Yazi tur="soluk" s={{ marginTop: 6 }}>{t("Henüz bir şey eklemedin.")}</Yazi>
              : liste.map((k, i) => (
                <View key={i} style={[s.satir, s.kalem]}>
                  <Yazi s={{ flex: 1, fontSize: 15 }}>{k.Tarif}</Yazi>
                  <Yazi tur="soluk" s={{ marginHorizontal: 8 }}>{Math.round(k.Kalori)} kcal</Yazi>
                  <Pressable onPress={() => sil(k)} accessibilityRole="button" accessibilityLabel={`${t("Sil")}: ${k.Tarif}`} hitSlop={10}>
                    <Yazi s={{ color: R.soluk, fontSize: 20 }}>×</Yazi>
                  </Pressable>
                </View>
              ))}
          </Kart>
        );
      })}
    </View>
  );
}

const s = temali(() => StyleSheet.create({
  satir: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginTop: 8 },
  isaret: { width: 9, height: 9, borderRadius: 2 },
  kalem: { marginTop: 10, paddingTop: 10, borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: R.cizgi },
  kare: { width: 48, minHeight: 44, paddingHorizontal: 0 },
  halkalar: { flexDirection: "row", justifyContent: "space-around", alignItems: "flex-start" },
  halkaSutun: { alignItems: "center", flex: 1 },
}));
