// Koc.tsx - Antrenman koçu (sitedeki nova_pages.py coach ile aynı akış)
// 1. Kullanıcının ekipmanı ve seviyesiyle yapabileceği hareketler süzülür
// 2. Nova yalnızca bu listeden plan kurar; listede olmayan hareket gelirse atılır
// 3. Plan profile kaydedilir (site oturumda tutuyor; telefonda kapatınca kaybolmasın)
// 4. Tamamlanan setler kaydedilince egzersiz kalorisi: set x 8, en az 60, en fazla 400
import React, { useState } from "react";
import { View } from "react-native";
import { aktifDil, t } from "../dil";
import { bugunMetni, type Veri } from "../hesap";
import { EGZERSIZLER, egzersizAdi, type Egzersiz } from "../egzersizler";
import { arka } from "../veri";
import { Cip, Dugme, Girdi, Hata, Kart, R, Yazi, hataMetni } from "../bilesenler";

const SEVIYELER = { "başlangıç": 0, orta: 1, ileri: 2 } as const;
type Seviye = keyof typeof SEVIYELER;
const EKIPMAN: [string, string][] = [["Dambıl", "dambıl"], ["Bank", "bank"], ["Bar", "bar"], ["Barfiks demiri", "barfiks"]];
const HEDEFLER = ["Kas kazanmak", "Genel kondisyon", "Güçlenmek"];
const SURELER = [20, 30, 45, 60, 75, 90];
const DIL_ADI: Record<string, string> = { tr: "Türkçe", en: "English", de: "Deutsch", es: "Español", fr: "Français", ar: "العربية" };

type PlanHareket = { exercise_id: string; sets: number; reps: string; rest_sec: number; note?: string };
type Plan = { summary: string; days: { title: string; focus: string; exercises: PlanHareket[] }[]; safety_note: string };

export const kullanilabilir = (ekipman: Set<string>, seviye: Seviye) =>
  EGZERSIZLER.filter((e) => e.ekipman.every((x) => ekipman.has(x)) && SEVIYELER[e.seviye] <= SEVIYELER[seviye]);

// Sitedeki library_context ile aynı satırlar (Türkçe ad, model kullanıcının dilinde yanıtlıyor)
export const kutuphaneBaglami = (l: Egzersiz[]) =>
  ["Egzersiz kütüphanesi (id | ad | kas | seviye):", ...l.map((e) => `- ${e.id} | ${e.ad[0]} | ${e.kas.join(", ")} | ${e.seviye}`)].join("\n");

export function planiSuz(plan: any, gecerli: Set<string>): Plan {
  const days = (Array.isArray(plan?.days) ? plan.days : [])
    .map((d: any) => ({ ...d, exercises: (d.exercises ?? []).filter((x: any) => gecerli.has(x?.exercise_id)) }))
    .filter((d: any) => d.exercises.length);
  return { summary: String(plan?.summary ?? ""), days, safety_note: String(plan?.safety_note ?? "") };
}

export function KocKarti(p: { veri: Veri; tarih: string; guncelle: (f: (v: Veri) => Veri) => Promise<void>; kaydedildi: () => void }) {
  const kayitli = p.veri.profil.antrenman_plani as { plan: Plan; olusturma: string } | undefined;
  const [form, setForm] = useState(!kayitli);
  const [hedef, setHedef] = useState(HEDEFLER[1]);
  const [seviye, setSeviye] = useState<Seviye>("başlangıç");
  const [ekipman, setEkipman] = useState<Set<string>>(new Set());
  const [gun, setGun] = useState(3);
  const [dakika, setDakika] = useState(45);
  const [sinir, setSinir] = useState("");
  const [bekle, setBekle] = useState(false);
  const [hata, setHata] = useState<string | null>(null);
  const [secGun, setSecGun] = useState(0);
  const [yapilan, setYapilan] = useState<Record<number, number>>({});
  const [mesaj, setMesaj] = useState<string | null>(null);

  const hazirla = async () => {
    setHata(null); setBekle(true);
    const havuz = kullanilabilir(ekipman, seviye);
    const ekipAd = EKIPMAN.filter(([, k]) => ekipman.has(k)).map(([a]) => a);
    const istek = `Hedef: ${hedef}\nSeviye: ${seviye}\nHaftada ${gun} gün\nAntrenman süresi: ${dakika} dakika\n`
      + `Ekipman: ${ekipAd.length ? ekipAd.join(", ") : "ekipmansız"}\nAğrı veya sınırlama: ${sinir.trim() || "yok"}`;
    const r = await arka.yapayZeka("coach", istek, `${kutuphaneBaglami(havuz)}\nYanıt dili: ${DIL_ADI[aktifDil()]}`);
    setBekle(false);
    if (!r.tamam) return setHata(hataMetni(r.hata));
    const plan = planiSuz(r.deger, new Set(havuz.map((e) => e.id)));
    if (!plan.days.length) return setHata(t("Plan oluşturulamadı. Tekrar dene."));
    await p.guncelle((v) => ({ ...v, profil: { ...v.profil, antrenman_plani: { plan, olusturma: bugunMetni() } } }));
    setSecGun(0); setYapilan({}); setForm(false); setMesaj(null);
  };

  const kaydet = async (plan: Plan) => {
    const gunPlan = plan.days[secGun];
    const hareketler = gunPlan.exercises.map((x, i) => ({ x, i })).filter(({ i }) => (yapilan[i] ?? 0) > 0).map(({ x, i }) => {
      const e = EGZERSIZLER.find((z) => z.id === x.exercise_id)!;
      return { id: x.exercise_id, name: e.ad[0], sets_planned: x.sets, sets_done: yapilan[i], reps: "" };
    });
    if (!hareketler.length) return setHata(t("Önce tamamladığın setleri gir."));
    const toplamSet = hareketler.reduce((s, h) => s + h.sets_done, 0);
    const kcal = Math.round(Math.min(400, Math.max(60, toplamSet * 8)));
    await p.guncelle((v) => {
      const g: any = { adim: 0, su: 0, egzersiz_kalori: 0, ...(v.aktivite_loglari?.[p.tarih] ?? {}) };
      g.egzersiz_kalori = Number(g.egzersiz_kalori || 0) + kcal;
      g.antrenmanlar = [...(g.antrenmanlar ?? []), { gun: gunPlan.title, hareketler }];
      return { ...v, aktivite_loglari: { ...v.aktivite_loglari, [p.tarih]: g } };
    });
    setYapilan({}); setHata(null);
    setMesaj(`${t("Antrenman kaydedildi")}: ${toplamSet} ${t("set")}, ~${kcal} kcal`);
    p.kaydedildi();
  };

  if (form || !kayitli) return (
    <Kart testID="koc-form">
      <Yazi s={{ fontWeight: "700", fontSize: 17 }}>{t("Antrenman koçu")}</Yazi>
      <Yazi tur="soluk" s={{ marginTop: 4, marginBottom: 12 }}>{t("Nova, yalnızca kütüphanedeki ve senin yapabileceğin hareketlerden haftalık plan kurar.")}</Yazi>
      <Yazi tur="alt" s={{ marginBottom: 8 }}>{t("Hedefin")}</Yazi>
      <View style={sira}>{HEDEFLER.map((h) => <Cip key={h} yazi={t(h)} secili={hedef === h} bas={() => setHedef(h)} />)}</View>
      <Yazi tur="alt" s={{ marginBottom: 8 }}>{t("Seviyen")}</Yazi>
      <View style={sira}>{(Object.keys(SEVIYELER) as Seviye[]).map((s) =>
        <Cip key={s} testID={`seviye-${s}`} yazi={t(s === "başlangıç" ? "Başlangıç" : s === "orta" ? "Orta" : "İleri seviye")} secili={seviye === s} bas={() => setSeviye(s)} />)}</View>
      <Yazi tur="alt" s={{ marginBottom: 8 }}>{t("Elindeki ekipman (boşsa ekipmansız)")}</Yazi>
      <View style={sira}>{EKIPMAN.map(([ad, k]) => <Cip key={k} testID={`ekipman-${k}`} yazi={t(ad)} secili={ekipman.has(k)}
        bas={() => { const y = new Set(ekipman); y.has(k) ? y.delete(k) : y.add(k); setEkipman(y); }} />)}</View>
      <Yazi tur="alt" s={{ marginBottom: 8 }}>{t("Haftada kaç gün?")}</Yazi>
      <View style={sira}>{[2, 3, 4, 5, 6].map((g) => <Cip key={g} testID={`gun-${g}`} yazi={String(g)} secili={gun === g} bas={() => setGun(g)} />)}</View>
      <Yazi tur="alt" s={{ marginBottom: 8 }}>{t("Antrenman süresi (dakika)")}</Yazi>
      <View style={sira}>{SURELER.map((d) => <Cip key={d} yazi={String(d)} secili={dakika === d} bas={() => setDakika(d)} />)}</View>
      <Girdi testID="koc-sinir" etiket={t("Ağrı ya da sınırlaman var mı? (isteğe bağlı)")} value={sinir} onChangeText={setSinir} maxLength={200} />
      <Yazi tur="soluk" s={{ marginBottom: 10, fontSize: 13 }}>{t("Uygun hareket")}: {kullanilabilir(ekipman, seviye).length}</Yazi>
      <Hata metin={hata} />
      <View style={{ flexDirection: "row", gap: 8 }}>
        {kayitli && <Dugme tur="ikincil" yazi={t("Vazgeç")} bas={() => { setForm(false); setHata(null); }} s={{ flex: 1 }} />}
        <Dugme testID="plan-hazirla" yazi={t("Plan hazırla")} bas={hazirla} yukleniyor={bekle} s={{ flex: 2 }} />
      </View>
    </Kart>
  );

  const plan = kayitli.plan;
  const gunPlan = plan.days[Math.min(secGun, plan.days.length - 1)];
  return (
    <Kart testID="koc-plan">
      <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
        <Yazi s={{ fontWeight: "700", fontSize: 17 }}>{t("Haftalık planın")}</Yazi>
        <Dugme tur="yalin" yazi={t("Yeni plan")} bas={() => { setForm(true); setMesaj(null); }} s={{ minHeight: 34, paddingHorizontal: 8 }} testID="yeni-plan" />
      </View>
      {!!plan.summary && <Yazi tur="soluk" s={{ marginTop: 4, marginBottom: 10 }}>{plan.summary}</Yazi>}
      <View style={sira}>{plan.days.map((d, i) => <Cip key={i} testID={`plan-gun-${i}`} yazi={d.title} secili={i === secGun} bas={() => { setSecGun(i); setYapilan({}); setMesaj(null); }} />)}</View>
      {!!gunPlan.focus && <Yazi tur="alt" s={{ marginBottom: 6 }}>{gunPlan.focus}</Yazi>}
      {gunPlan.exercises.map((x, i) => {
        const e = EGZERSIZLER.find((z) => z.id === x.exercise_id)!;
        const tamam = yapilan[i] ?? 0;
        const sinirSet = Math.max(1, Math.min(10, Number(x.sets) || 1));
        return (
          <View key={i} testID={`plan-hareket-${x.exercise_id}`} style={{ paddingVertical: 10, borderTopWidth: 0.5, borderTopColor: R.cizgi }}>
            <Yazi s={{ fontWeight: "700" }}>{egzersizAdi(e)}</Yazi>
            <Yazi tur="soluk" s={{ fontSize: 14 }}>{x.sets} {t("set")} × {x.reps} · {t("dinlenme")} {x.rest_sec} {t("sn")}</Yazi>
            {!!x.note && <Yazi tur="soluk" s={{ fontSize: 13, marginTop: 2 }}>{x.note}</Yazi>}
            <View style={{ flexDirection: "row", alignItems: "center", gap: 8, marginTop: 8 }}>
              <Yazi tur="soluk" s={{ fontSize: 13, flex: 1 }}>{t("Tamamlanan set")}</Yazi>
              <Dugme tur="ikincil" yazi="−" kapali={tamam <= 0} bas={() => setYapilan({ ...yapilan, [i]: tamam - 1 })} s={{ width: 40, minHeight: 36, paddingHorizontal: 0 }} />
              <Yazi s={{ fontWeight: "700", minWidth: 36, textAlign: "center" }} testID={`set-${i}`}>{tamam}/{sinirSet}</Yazi>
              <Dugme tur="ikincil" yazi="+" kapali={tamam >= sinirSet} bas={() => { setYapilan({ ...yapilan, [i]: tamam + 1 }); setMesaj(null); }} s={{ width: 40, minHeight: 36, paddingHorizontal: 0 }} testID={`set-arti-${i}`} />
            </View>
          </View>
        );
      })}
      <Hata metin={hata} />
      {mesaj && <Yazi s={{ color: R.iyi, marginVertical: 8 }} testID="antrenman-mesaj">{mesaj}</Yazi>}
      <Dugme testID="antrenman-kaydet" yazi={t("Antrenmanı kaydet")} bas={() => kaydet(plan)} />
      {!!plan.safety_note && <Yazi tur="soluk" s={{ marginTop: 10, fontSize: 13 }}>{plan.safety_note}</Yazi>}
    </Kart>
  );
}

const sira = { flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 12 } as const;
