// denge.ts - Kaçamak dengeleme
//
// Kurallar (yol haritasındaki gibi):
//  - Fazla tek güne yıkılmaz: 600 kcal'e kadar 2 güne, üstü 3 güne yayılır.
//  - Bir günde hedef en fazla 300 kcal düşer.
//  - Yeni hedef hiçbir gün dinlenik metabolizmanın (BMR) ve güvenli tabanın altına inmez.
//  - 18 yaş altında ve oruç modunda kalori düşürülmez; yalnızca hareket önerilir.
//  - Yemekle karşılanamayan kısım için yürüyüş önerilir, ama günde en fazla 45 dakika.
//    Kalanı "bırak gitsin" denir: bir günlük fazla haftalık gidişatı pek değiştirmez,
//    ve telafi için zorlamak sağlıksız bir döngü başlatabilir.
//
// Yürüyüş kalorisi: orta tempo yürüyüş 3,5 MET (Compendium of Physical Activities, kod 17190).
// Hedef zaten dinlenme harcamasını içerdiği için yalnızca fazladan yakılan sayılır: (MET - 1) x kg x saat.
import { bugunMetni, hedefHesapla, yas, type Profil } from "./hesap";

export const GUNLUK_EN_FAZLA = 300;
export const ESIK = 150; // bunun altındaki fazlalık için öneri gösterilmez
const YURUYUS_MET = 3.5;
const YURUYUS_DK_SINIR = 45;
const ADIM_DK = 100; // orta tempoda dakikada yaklaşık 100 adım

export type Denge = {
  kaynak_gun: string; // fazlanın olduğu gün
  fazla: number;
  gunler: Record<string, number>; // tarih -> o gün hedeften düşülen kcal
  yuruyus_dk: number; // her gün için önerilen yürüyüş
  birakilan: number; // dengelenmeyen kısım
  olusturma: string;
  bitis: string; // planın son günü
};

export const yuruyusKcalDk = (kilo: number) => ((YURUYUS_MET - 1) * kilo) / 60;
export const adimTahmini = (dk: number) => Math.round((dk * ADIM_DK) / 100) * 100;

/** Kalori düşürmenin uygun olmadığı durumlar */
export const yalnizHareket = (p: Profil) => yas(p) < 18 || !!p.oruc_modu;

/** Bir günün dengelemeden önceki ve sonraki hedefi; taban: max(BMR, cinsiyete göre güvenli taban) */
export function gunHedefi(p: Profil, tarih = bugunMetni()) {
  const h = hedefHesapla(p);
  const taban = Math.max(h.bmr, p.cinsiyet === "Kadın" ? 1200 : 1500);
  const d = (p.dengeleme as Denge | undefined)?.gunler?.[tarih] ?? 0;
  const hedef = Math.max(Math.min(h.hedef, taban), h.hedef - d);
  return { temel: h.hedef, hedef, dusus: h.hedef - hedef, taban, bmr: h.bmr };
}

/** Fazladan plan: hangi gün ne kadar düşülür, kaç dakika yürüyüş önerilir */
export function planKur(p: Profil, fazla: number, kaynakGun: string, baslangic = new Date(), sadeceHareket = false): Denge {
  fazla = Math.max(0, Math.round(fazla));
  const gunSayisi = fazla <= 600 ? 2 : 3;
  const { temel, taban } = gunHedefi({ ...p, dengeleme: undefined });
  const payGun = yalnizHareket(p) || sadeceHareket ? 0 : Math.max(0, Math.min(GUNLUK_EN_FAZLA, Math.floor(temel - taban), Math.ceil(fazla / gunSayisi)));
  const gunler: Record<string, number> = {};
  let kalan = fazla;
  let bitis = bugunMetni(baslangic);
  for (let i = 0; i < gunSayisi; i++) {
    const d = new Date(baslangic); d.setDate(d.getDate() + i);
    bitis = bugunMetni(d);
    const x = Math.min(payGun, kalan);
    if (x > 0) gunler[bugunMetni(d)] = x;
    kalan -= x;
  }
  const kgDk = yuruyusKcalDk(Number(p.mevcut_kilo) || 70);
  const dk = kalan > 0 ? Math.min(YURUYUS_DK_SINIR, Math.ceil(kalan / gunSayisi / kgDk / 5) * 5) : 0;
  const birakilan = Math.max(0, Math.round(kalan - dk * kgDk * gunSayisi));
  return { kaynak_gun: kaynakGun, fazla, gunler, yuruyus_dk: dk, birakilan, olusturma: bugunMetni(baslangic), bitis };
}

/** Plan hâlâ sürüyor mu (bugün ya da sonrası için düşüş var mı) */
export function planSuruyor(d: Denge | undefined, tarih = bugunMetni()): boolean {
  return !!d && d.olusturma <= tarih && d.bitis >= tarih;
}

/** Planın kaçıncı günü (1'den başlar) ve toplam gün */
export function planGunu(d: Denge, tarih = bugunMetni()): [number, number] {
  const fark = (a: string, b: string) => Math.round((+new Date(b + "T12:00:00") - +new Date(a + "T12:00:00")) / 864e5);
  return [fark(d.olusturma, tarih) + 1, fark(d.olusturma, d.bitis) + 1];
}

export function gunOnce(tarih: string, n: number) {
  const d = new Date(tarih + "T12:00:00"); d.setDate(d.getDate() - n); return bugunMetni(d);
}

/** Kullanıcı sohbette kaçamaktan söz ediyor mu (altı dilde, kaba bir yakalama) */
export const kacamakMi = (metin: string) =>
  /kaçamak|kacamak|fazla ye|çok ye|cok ye|abarttım|abarttim|cheat|overate|over-ate|ate too much|ausrutscher|zu viel gegessen|me pasé|me pase|comí demasiado|comi demasiado|écart|ecart|trop mangé|trop mange|craqué|أفرطت|أكلت كثير/i.test(metin);
