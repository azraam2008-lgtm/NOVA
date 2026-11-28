// mikro.ts - Vitamin ve mineraller (sitedeki mikro.py ile birebir)
//
// Kaynak: AB 1169/2011 Ek XIII besin referans değerleri (NRV); lif için EFSA'nın 25 g'ı.
// Nova mikro besin değeri UYDURMAZ: yalnızca gerçek kaynaktan gelen değerler toplanır
// (paketli ürünler, etiket fotoğrafı, veritabanındaki USDA kayıtları). Veri yoksa
// "veri yok" denir; sıfır yazmak yanıltıcı olurdu, çünkü "yok" ile "sıfır" aynı şey değil.
import type { Kayit } from "./hesap";

// [ad, kayıttaki alan, birim, günlük referans, sınır mı (az olması iyi)]
export const BESINLER: [string, string, string, number, boolean][] = [
  ["Lif", "Lif (g)", "g", 25, false],
  ["Şeker", "Şeker (g)", "g", 90, true],
  ["Doymuş yağ", "Doymuş yağ (g)", "g", 20, true],
  ["Tuz", "Tuz (g)", "g", 6, true],
  ["Demir", "Demir (mg)", "mg", 14, false],
  ["Kalsiyum", "Kalsiyum (mg)", "mg", 800, false],
  ["Magnezyum", "Magnezyum (mg)", "mg", 375, false],
  ["Çinko", "Çinko (mg)", "mg", 10, false],
  ["Potasyum", "Potasyum (mg)", "mg", 2000, false],
  ["C vitamini", "C vitamini (mg)", "mg", 80, false],
  ["D vitamini", "D vitamini (µg)", "µg", 5, false],
  ["B12 vitamini", "B12 vitamini (µg)", "µg", 2.5, false],
];
const ALANLAR = BESINLER.map((b) => b[1]);

/** Yalnızca en az bir kayıtta gerçekten verisi olan besinler döner */
export function topla(kayitlar: Kayit[]): Record<string, number> {
  const toplam: Record<string, number> = {};
  for (const k of kayitlar) {
    for (const alan of ALANLAR) {
      const d = k[alan];
      if (d == null) continue;
      const n = Number(d);
      if (Number.isFinite(n)) toplam[alan] = (toplam[alan] ?? 0) + n;
    }
  }
  return toplam;
}

/** Kaç kayıtta mikro besin verisi var: [var, toplam] */
export const kapsama = (kayitlar: Kayit[]): [number, number] =>
  [kayitlar.filter((k) => ALANLAR.some((a) => k[a] != null)).length, kayitlar.length];

/** Yüzdeye göre renk: sınır besinlerinde aşmak kötü, diğerlerinde az kalmak */
export function renk(yuzde: number, sinir: boolean): string {
  if (sinir) return yuzde > 100 ? "#FF6B5E" : yuzde > 75 ? "#F2B233" : "#34C77B";
  return yuzde >= 100 ? "#34C77B" : yuzde >= 50 ? "#F2B233" : "#FF9F43";
}

export const eksikler = (toplam: Record<string, number>, esik = 50) =>
  BESINLER.filter(([, alan, , ref, sinir]) => !sinir && alan in toplam && (toplam[alan] / ref) * 100 < esik).map((b) => b[0]);

export const asilanlar = (toplam: Record<string, number>) =>
  BESINLER.filter(([, alan, , ref, sinir]) => sinir && alan in toplam && toplam[alan] > ref).map((b) => b[0]);
