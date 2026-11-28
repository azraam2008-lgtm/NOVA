// yemekler.ts - Uygulamaya gömülü yemek veritabanında arama (internetsiz çalışır)
// Kaynak: sitenin CSV'si, mobil/yemekleri_aktar.py ile 100 grama indirgenmiş hali.

import ham from "./veri/yemekler.json";

export type Yemek = {
  ad: string; en: string; kat: string; por: string; g: number;
  p: number; k: number; y: number; kaynak: string; ek?: Record<string, number>;
};

const YEMEKLER = ham as Yemek[];

/** Türkçe karakterleri ve büyük/küçük harfi eşitler: "Çiğ Köfte" ~ "cig kofte" */
export function sadelestir(m: string): string {
  return (m ?? "")
    .replace(/İ/g, "i").replace(/I/g, "ı").toLowerCase()
    .replace(/ç/g, "c").replace(/ğ/g, "g").replace(/ı/g, "i").replace(/ö/g, "o").replace(/ş/g, "s").replace(/ü/g, "u")
    .normalize("NFD").replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, " ").trim();
}

const DIZIN = YEMEKLER.map((y) => ({ y, ad: sadelestir(y.ad), en: sadelestir(y.en) }));

export function yemekAra(sorgu: string, sinir = 20): Yemek[] {
  const s = sadelestir(sorgu);
  if (s.length < 2) return [];
  const kelimeler = s.split(" ");
  const puanli: [number, Yemek][] = [];
  for (const { y, ad, en } of DIZIN) {
    let puan = 0;
    for (const metin of [ad, en]) {
      if (!metin) continue;
      if (metin === s) puan = Math.max(puan, 100);
      else if (metin.startsWith(s)) puan = Math.max(puan, 80);
      else if (kelimeler.every((k) => metin.includes(k))) puan = Math.max(puan, 60 - metin.length / 10);
    }
    if (puan > 0) puanli.push([puan, y]);
  }
  return puanli.sort((a, b) => b[0] - a[0]).slice(0, sinir).map(([, y]) => y);
}

export const yemekSayisi = () => YEMEKLER.length;
