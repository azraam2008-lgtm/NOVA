// Denge.tsx - Kaçamak dengeleme kartı ("Bugün" sayfasında)
// Üç hal: plan sürüyorsa durumu; dün hedef aşıldıysa nazik bir öneri; kullanıcı isterse elle giriş.
// Dil hiçbir yerde suçlayıcı değil; "gerek yok" her zaman bir seçenek.
import React, { useEffect, useState } from "react";
import { View } from "react-native";
import { t, tf } from "../dil";
import { gunToplami, type Veri } from "../hesap";
import { ESIK, adimTahmini, gunHedefi, gunOnce, planGunu, planKur, planSuruyor, yalnizHareket, type Denge } from "../denge";
import { Cip, Dugme, Girdi, Kart, Yazi } from "../bilesenler";
import { hareketKalorisi } from "./Bugun";

type Guncelle = (f: (v: Veri) => Veri) => Promise<void>;

function PlanOnizleme(p: { plan: Denge; kisitli: boolean }) {
  const gunler = Object.entries(p.plan.gunler);
  return (
    <View style={{ marginVertical: 8 }} testID="denge-onizleme">
      {gunler.length > 0 && <Yazi s={{ fontSize: 15 }}>
        {tf("Önümüzdeki {g} gün hedefin günde {k} kcal düşük olur.", { g: gunler.length, k: gunler[0][1] })}
      </Yazi>}
      {p.plan.yuruyus_dk > 0 && <Yazi s={{ fontSize: 15, marginTop: 4 }}>
        {tf("Her gün {d} dakika tempolu yürüyüş (yaklaşık {a} adım) kalanını karşılar.", { d: p.plan.yuruyus_dk, a: adimTahmini(p.plan.yuruyus_dk) })}
      </Yazi>}
      {p.plan.birakilan > 0 && <Yazi tur="soluk" s={{ fontSize: 14, marginTop: 4 }}>
        {tf("Kalan {k} kcal için kendini zorlama; tek bir gün haftalık gidişatı pek değiştirmez.", { k: p.plan.birakilan })}
      </Yazi>}
      {p.kisitli && <Yazi tur="soluk" s={{ fontSize: 13, marginTop: 6 }}>{t("Büyüme çağında ve oruçluyken kalori düşürmüyoruz; bunun yerine hareket öneriyorum.")}</Yazi>}
      <Yazi tur="soluk" s={{ fontSize: 12, marginTop: 6 }}>{t("Hedefin hiçbir gün dinlenik metabolizmanın altına inmez.")}</Yazi>
    </View>
  );
}

export function DengeKarti(p: { veri: Veri; tarih: string; guncelle: Guncelle; acTetik?: number }) {
  const pr = p.veri.profil;
  const plan = pr.dengeleme as Denge | undefined;
  const dun = gunOnce(p.tarih, 1);
  const [elle, setElle] = useState(false);
  const [miktar, setMiktar] = useState("");
  const [hangiGun, setHangiGun] = useState<"dun" | "bugun">("dun");

  // Sohbetten "kaçamak yaptım" gelirse elle giriş açılır
  useEffect(() => { if (p.acTetik) setElle(true); }, [p.acTetik]);

  // Dünün fazlası: yenen - (o günün hedefi + hareket). Dün kayıt yoksa hesaplanmaz.
  const dunToplam = gunToplami(p.veri.gunluk_kayitlar, dun);
  const dunFazla = dunToplam.kayitlar.length ? Math.round(dunToplam.kalori - gunHedefi(pr, dun).hedef - hareketKalorisi(p.veri, dun)) : 0;
  const kisitli = yalnizHareket(pr);

  const uygula = (fazla: number, kaynak: string, sadeceHareket = false) => {
    const bas = new Date(kaynak + "T12:00:00"); bas.setDate(bas.getDate() + 1);
    const bugun = new Date(p.tarih + "T12:00:00");
    const yeni = planKur(pr, fazla, kaynak, bas < bugun ? bugun : bas, sadeceHareket);
    setElle(false); setMiktar("");
    return p.guncelle((v) => ({ ...v, profil: { ...v.profil, dengeleme: yeni } }));
  };
  const gec = () => p.guncelle((v) => ({ ...v, profil: { ...v.profil, denge_gecildi: dun } }));
  // Bırakılan plan aynı gün için öneriyi geri getirmesin
  const birak = () => p.guncelle((v) => ({ ...v, profil: { ...v.profil, dengeleme: null, denge_gecildi: plan?.kaynak_gun ?? dun } }));

  // 1) Elle giriş
  if (elle) {
    const n = Math.max(0, Math.min(3000, Math.round(Number(miktar.replace(",", ".")) || 0)));
    const kaynak = hangiGun === "dun" ? dun : p.tarih;
    const onizleme = n >= 50 ? planKur(pr, n, kaynak, new Date(), false) : null;
    return (
      <Kart testID="denge-elle">
        <Yazi s={{ fontWeight: "700", fontSize: 17 }}>{t("Kaçamağı dengele")}</Yazi>
        <Yazi tur="soluk" s={{ marginTop: 4, marginBottom: 10 }}>{t("Herkesin olur. Yaklaşık ne kadar fazla yediğini yaz, Nova birkaç güne yaysın.")}</Yazi>
        <View style={{ flexDirection: "row", gap: 8, marginBottom: 10 }}>
          <Cip yazi={t("Dün")} secili={hangiGun === "dun"} bas={() => setHangiGun("dun")} testID="denge-dun" />
          <Cip yazi={t("Bugün")} secili={hangiGun === "bugun"} bas={() => setHangiGun("bugun")} testID="denge-bugun" />
        </View>
        <Girdi testID="denge-miktar" etiket={t("Fazladan kalori (tahmini)")} value={miktar} onChangeText={setMiktar} keyboardType="number-pad" placeholder="500" />
        {hangiGun === "dun" && dunFazla >= ESIK && !miktar && (
          <Dugme tur="yalin" yazi={tf("Kayıtlarına göre dün: +{k} kcal", { k: dunFazla })} bas={() => setMiktar(String(dunFazla))} s={{ minHeight: 34, marginBottom: 4 }} />
        )}
        {onizleme && <PlanOnizleme plan={onizleme} kisitli={kisitli} />}
        <View style={{ flexDirection: "row", gap: 8, marginTop: 4 }}>
          <Dugme tur="ikincil" yazi={t("Vazgeç")} bas={() => setElle(false)} s={{ flex: 1 }} />
          <Dugme testID="denge-uygula" yazi={t("Planı uygula")} kapali={!onizleme} bas={() => uygula(n, kaynak)} s={{ flex: 1 }} />
        </View>
      </Kart>
    );
  }

  // 2) Süren plan
  if (plan && planSuruyor(plan, p.tarih)) {
    const g = gunHedefi(pr, p.tarih);
    const [kacinci, toplam] = planGunu(plan, p.tarih);
    return (
      <Kart testID="denge-suren">
        <Yazi tur="alt">{t("Dengeleme")} · {kacinci}/{toplam}</Yazi>
        {g.dusus > 0
          ? <Yazi s={{ marginTop: 6, fontSize: 15 }}>{tf("Bugünkü hedefin {h} kcal (normalde {n}).", { h: Math.round(g.hedef), n: Math.round(g.temel) })}</Yazi>
          : <Yazi s={{ marginTop: 6, fontSize: 15 }}>{t("Bugün hedefin değişmedi.")}</Yazi>}
        {plan.yuruyus_dk > 0 && <Yazi s={{ marginTop: 4, fontSize: 15 }}>{tf("Bugün {d} dakika tempolu yürüyüş (yaklaşık {a} adım) iyi gelir.", { d: plan.yuruyus_dk, a: adimTahmini(plan.yuruyus_dk) })}</Yazi>}
        <Dugme tur="yalin" yazi={t("Planı bırak")} bas={birak} s={{ minHeight: 34, marginTop: 6 }} testID="denge-birak" />
      </Kart>
    );
  }

  // 3) Dün hedef aşıldıysa nazik öneri (bir kez; "gerek yok" denirse o gün için bir daha sorulmaz)
  if (dunFazla >= ESIK && plan?.kaynak_gun !== dun && pr.denge_gecildi !== dun) {
    const oneri = planKur(pr, dunFazla, dun, new Date(p.tarih + "T12:00:00"));
    return (
      <Kart testID="denge-oneri">
        <Yazi s={{ fontWeight: "700", fontSize: 17 }}>{tf("Dün hedefinin {k} kcal üstüne çıktın", { k: dunFazla })}</Yazi>
        <Yazi tur="soluk" s={{ marginTop: 4 }}>{t("Olur böyle günler; tek bir gün gidişatı bozmaz. İstersen fazlayı birkaç güne yayarak dengeleyelim.")}</Yazi>
        <PlanOnizleme plan={oneri} kisitli={kisitli} />
        <Dugme testID="denge-oneri-uygula" yazi={t("Planı uygula")} bas={() => uygula(dunFazla, dun)} />
        <View style={{ flexDirection: "row", gap: 8, marginTop: 8 }}>
          {!kisitli && <Dugme tur="ikincil" yazi={t("Sadece hareketle")} bas={() => uygula(dunFazla, dun, true)} s={{ flex: 1 }} testID="denge-hareket" />}
          <Dugme tur="ikincil" yazi={t("Gerek yok")} bas={gec} s={{ flex: 1 }} testID="denge-gec" />
        </View>
      </Kart>
    );
  }

  // 4) Hiçbiri yoksa yalnızca küçük bir bağlantı
  return <Dugme tur="yalin" yazi={t("Kaçamak mı yaptın? Dengeleyelim")} bas={() => setElle(true)} s={{ minHeight: 36, marginBottom: 10 }} testID="denge-ac" />;
}

