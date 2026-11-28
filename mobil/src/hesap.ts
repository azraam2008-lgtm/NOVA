// hesap.ts - Kalori hedefi ve günlük toplamlar
// Sitedeki app.py hesapla_bmr_ve_hedef ile birebir aynı kurallar; iki tarafta
// aynı kişi için farklı hedef çıkmasın. Değiştirirsen ikisini birlikte değiştir.

export type Profil = {
  dil?: string;
  ad?: string;
  amaclar?: string[];
  cinsiyet?: "Kadın" | "Erkek";
  dogum_yili?: number;
  boy?: number;
  mevcut_kilo?: number;
  hedef_kilo?: number;
  hedef_sure_ay?: number;
  aktivite?: string;
  tema?: string;
  oruc_modu?: boolean;
  setup_tamamlandi?: boolean;
  [k: string]: unknown;
};

export type Kayit = {
  Tarih: string; // YYYY-MM-DD
  Öğün: string;
  Tarif: string;
  Kalori: number;
  Protein: number;
  Karbonhidrat: number;
  Yağ: number;
  [k: string]: unknown;
};

export type Veri = {
  gunluk_kayitlar: Kayit[];
  aktivite_loglari: Record<string, { adim?: number; su?: number; egzersiz_kalori?: number; antrenmanlar?: any[]; [k: string]: unknown }>;
  profil: Profil;
};

// Harris-Benedict katsayıları (sitedeki AKTIVITE_DUZEYLERI)
export const AKTIVITE: [string, number][] = [
  ["Hareketsiz (masa başı, çok az yürüyüş)", 1.2],
  ["Az hareketli (haftada 1-3 gün egzersiz)", 1.375],
  ["Orta hareketli (haftada 3-5 gün egzersiz)", 1.55],
  ["Çok hareketli (haftada 6-7 gün egzersiz)", 1.725],
];
export const AMACLAR = [
  "Kilo vermek istiyorum",
  "Kilomu korumak istiyorum",
  "Kilo almak istiyorum",
  "Kas kazanmak istiyorum",
  "Sağlıklı beslenmek istiyorum",
];
export const OGUNLER_NORMAL = ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"];
export const OGUNLER_ORUC = ["Sahur", "İftar", "Gece Ara Öğünü"];

export const ogunler = (p: Profil) => (p.oruc_modu ? OGUNLER_ORUC : OGUNLER_NORMAL);

export const yas = (p: Profil, bugun = new Date()) => bugun.getFullYear() - Number(p.dogum_yili ?? 2000);

/** 4/4/9 kuralı (sitedeki nutrition_check.kcal) */
export const kcal = (p: number, k: number, y: number) => 4 * p + 4 * k + 9 * y;

export function haftalikHiz(p: Profil): number {
  const fark = Number(p.mevcut_kilo) - Number(p.hedef_kilo);
  const hafta = Math.max(1, Number(p.hedef_sure_ay ?? 1) * 4.345);
  return fark / hafta;
}

export function hedefHesapla(p: Profil, bugun = new Date()) {
  const y = yas(p, bugun);
  const kilo = Number(p.mevcut_kilo), boy = Number(p.boy);
  const bmr = 10 * kilo + 6.25 * boy - 5 * y + (p.cinsiyet === "Erkek" ? 5 : -161);
  const carpan = AKTIVITE.find(([a]) => a === p.aktivite)?.[1] ?? 1.375;
  const tdee = bmr * carpan;

  let acik = ((kilo - Number(p.hedef_kilo)) * 7700) / (Math.max(1, Number(p.hedef_sure_ay ?? 1)) * 30);
  acik = Math.max(Math.min(acik, 1100), -700); // haftada ~1 kilodan hızlı hedef yok
  if (p.oruc_modu && acik > 500) acik = 500; // oruçluyken açık en fazla 500

  let taban = p.cinsiyet === "Kadın" ? 1200 : 1500;
  if (y < 18) taban = Math.max(taban, bmr); // gelişme çağında BMR'nin altına inilmez
  const hedef = Math.max(taban, tdee - acik);
  return { bmr, tdee, acik, hedef };
}

export function gunToplami(kayitlar: Kayit[], tarih: string) {
  const g = kayitlar.filter((k) => k.Tarih === tarih);
  const top = (a: keyof Kayit) => g.reduce((s, k) => s + (Number(k[a]) || 0), 0);
  return { kayitlar: g, kalori: top("Kalori"), protein: top("Protein"), karb: top("Karbonhidrat"), yag: top("Yağ") };
}

/** Yerel saatle YYYY-MM-DD (site str(date.today()) ile aynı biçim) */
export function bugunMetni(d = new Date()): string {
  const iki = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${iki(d.getMonth() + 1)}-${iki(d.getDate())}`;
}

/** 100 gram değerlerinden, yenen grama göre kayıt (sitedeki _kayit_yap ile aynı) */
export function kayitYap(
  ad: string, gram: number, tarih: string, ogun: string,
  p100: number, k100: number, y100: number, ek?: Record<string, number>,
): Kayit {
  const o = gram / 100;
  const p = p100 * o, k = k100 * o, y = y100 * o;
  const kayit: Kayit = {
    Tarih: tarih, Öğün: ogun, Tarif: `${ad} (${Math.round(gram)} g)`,
    Kalori: Math.round(kcal(p, k, y)),
    Protein: Math.round(p * 10) / 10, Karbonhidrat: Math.round(k * 10) / 10, Yağ: Math.round(y * 10) / 10,
  };
  for (const [a, d] of Object.entries(ek ?? {})) kayit[a] = Math.round(d * o * 100) / 100;
  return kayit;
}

export const BOS_VERI = (): Veri => ({ gunluk_kayitlar: [], aktivite_loglari: {}, profil: { setup_tamamlandi: false } });
