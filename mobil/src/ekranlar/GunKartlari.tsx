// GunKartlari.tsx - "Bugün" sayfasındaki vitamin-mineral ve oruç kartları
import React, { useEffect, useState } from "react";
import { Pressable, View } from "react-native";
import { t } from "../dil";
import type { Kayit, Profil } from "../hesap";
import { BESINLER, asilanlar, eksikler, kapsama, renk, topla } from "../mikro";
import { ONERILER, RAMAZAN_AYI, SU_HEDEFI, orucluMu, saatleriAl, sonrakiOlay, sureMetni, type Saatler } from "../oruc";
import { Cubuk, Kart, R, Yazi } from "../bilesenler";

const sayiYaz = (n: number) => (n >= 100 ? String(Math.round(n)) : String(Number(n.toFixed(n >= 10 ? 1 : 2))));

export function MikroKarti(p: { kayitlar: Kayit[] }) {
  const [acik, setAcik] = useState(false);
  const toplam = topla(p.kayitlar);
  const [varOlan, hepsi] = kapsama(p.kayitlar);
  const az = eksikler(toplam), fazla = asilanlar(toplam);

  return (
    <Kart testID="mikro-kart">
      <Pressable onPress={() => setAcik(!acik)} accessibilityRole="button" testID="mikro-ac">
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
          <Yazi s={{ fontWeight: "700", fontSize: 17 }}>{t("Vitamin ve mineraller")}</Yazi>
          <Yazi tur="soluk">{acik ? "−" : "+"}</Yazi>
        </View>
        <Yazi tur="soluk" s={{ marginTop: 4 }}>
          {hepsi === 0
            ? t("Bugün bir şey eklediğinde vitamin, mineral ve tuz burada görünür.")
            : varOlan === 0
            ? t("Bugünkü kayıtlarında vitamin ve mineral bilgisi yok. Paketli ürünler ve etiket fotoğrafı bu bilgiyi getirir.")
            : `${t("Bilgisi olan kayıt")}: ${varOlan}/${hepsi}. ${t("Toplam yalnızca bunlardan hesaplanır.")}`}
        </Yazi>
        {!acik && toplam["Tuz (g)"] != null && (
          <Yazi s={{ marginTop: 6, fontSize: 14 }} testID="mikro-tuz">
            {t("Tuz")}: {sayiYaz(toplam["Tuz (g)"])} / 6 g
          </Yazi>
        )}
        {varOlan > 0 && !acik && (fazla.length > 0 || az.length > 0) && (
          <Yazi s={{ marginTop: 6, fontSize: 14 }}>
            {fazla.length > 0 && <Yazi s={{ color: R.hata, fontSize: 14 }}>{t("Sınırı aşan")}: {fazla.map(t).join(", ")}. </Yazi>}
            {az.length > 0 && <Yazi tur="soluk" s={{ fontSize: 14 }}>{t("Düşük kalan")}: {az.map(t).join(", ")}</Yazi>}
          </Yazi>
        )}
      </Pressable>
      {acik && varOlan > 0 && BESINLER.map(([ad, alan, birim, ref, sinir]) => {
        const d = toplam[alan];
        const yok = d == null;
        const yuzde = yok ? 0 : (d / ref) * 100;
        return (
          <View key={alan} style={{ marginTop: 12 }} testID={`mikro-${alan}`}>
            <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 5 }}>
              <Yazi s={{ fontSize: 14 }}>{t(ad)}{sinir ? ` (${t("sınır")})` : ""}</Yazi>
              <Yazi tur="soluk" s={{ fontSize: 14 }}>{yok ? t("veri yok") : `${sayiYaz(d)} / ${sayiYaz(ref)} ${birim} · %${Math.round(yuzde)}`}</Yazi>
            </View>
            {!yok && <Cubuk oran={yuzde / 100} renk={renk(yuzde, sinir)} yukseklik={6} />}
          </View>
        );
      })}
      {acik && varOlan > 0 && <Yazi tur="soluk" s={{ marginTop: 12, fontSize: 12 }}>{t("Referans: AB günlük besin referans değerleri (yetişkin).")}</Yazi>}
    </Kart>
  );
}

export function OrucKarti(p: { profil: Profil; su: number }) {
  const [saatler, setSaatler] = useState<Saatler | null | "yukleniyor">("yukleniyor");
  const [simdi, setSimdi] = useState(new Date());
  const { sehir, ulke, namaz_metodu, elle_imsak, elle_iftar } = p.profil;
  useEffect(() => {
    let iptal = false;
    setSaatler("yukleniyor");
    saatleriAl(p.profil).then((s) => { if (!iptal) setSaatler(s); });
    return () => { iptal = true; };
  }, [sehir, ulke, namaz_metodu, elle_imsak, elle_iftar]);
  useEffect(() => { const z = setInterval(() => setSimdi(new Date()), 30000); return () => clearInterval(z); }, []);

  if (saatler === "yukleniyor") return <Kart testID="oruc-kart"><Yazi tur="soluk">{t("Yükleniyor...")}</Yazi></Kart>;
  if (!saatler) return (
    <Kart testID="oruc-kart">
      <Yazi s={{ fontWeight: "700", fontSize: 17 }}>{t("Oruç modu")}</Yazi>
      <Yazi tur="soluk" s={{ marginTop: 6 }}>{t("Sahur ve iftar saatleri için Profil sayfasındaki Oruç modu bölümüne şehrini ve ülkeni yaz.")}</Yazi>
    </Kart>
  );
  const [olay, kalan] = sonrakiOlay(saatler, simdi);
  const gunNo = Math.floor(+simdi / 864e5);
  const grup = olay === "iftar" ? (gunNo % 2 ? "iftar" : "egzersiz") : (gunNo % 2 ? "sahur" : "su");
  const oneri = ONERILER[grup][gunNo % ONERILER[grup].length];

  return (
    <Kart testID="oruc-kart">
      <Yazi tur="alt">{t(olay === "iftar" ? "İftara kalan" : "Sahurun bitmesine kalan")}</Yazi>
      <Yazi tur="buyuk" testID="oruc-kalan">{sureMetni(kalan)}</Yazi>
      <View style={{ flexDirection: "row", gap: 18, marginTop: 6 }}>
        <Yazi tur="soluk">{t("İmsak")} <Yazi s={{ fontWeight: "700" }}>{saatler.imsak}</Yazi></Yazi>
        <Yazi tur="soluk">{t("İftar")} <Yazi s={{ fontWeight: "700" }}>{saatler.iftar}</Yazi></Yazi>
      </View>
      {saatler.hicriAy === RAMAZAN_AYI && <Yazi tur="soluk" s={{ marginTop: 4 }}>{t("Ramazan")} {saatler.hicriGun}</Yazi>}
      {saatler.elle && <Yazi tur="soluk" s={{ marginTop: 4, fontSize: 12 }}>{t("Saatler elle girdiğin değerlerden alınıyor.")}</Yazi>}
      <View style={{ marginTop: 12 }}>
        <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 5 }}>
          <Yazi tur="soluk" s={{ fontSize: 14 }}>{t("Su")}</Yazi>
          <Yazi s={{ fontSize: 14, fontWeight: "700" }}>{p.su.toFixed(2)} / {SU_HEDEFI} L</Yazi>
        </View>
        <Cubuk oran={p.su / SU_HEDEFI} renk={R.su} yukseklik={6} />
        <Yazi tur="soluk" s={{ fontSize: 13, marginTop: 5 }}>{orucluMu(saatler, simdi) ? t("Şu an oruçlusun. Günlük su hedefini iftar ile sahur arasına yayman gerekiyor.") : `${t("Su içme vakti. Hedefin")}: ${SU_HEDEFI} L`}</Yazi>
      </View>
      <Yazi s={{ marginTop: 12, fontSize: 14 }}>{t(oneri)}</Yazi>
      <Yazi tur="soluk" s={{ marginTop: 8, fontSize: 12 }}>{t("Bunlar genel bilgidir, tıbbi tavsiye değildir. Şeker hastalığın, tansiyon sorunun ya da düzenli kullandığın bir ilacın varsa oruç tutmadan önce doktoruna danış.")}</Yazi>
    </Kart>
  );
}
