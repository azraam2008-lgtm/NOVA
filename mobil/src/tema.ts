// tema.ts - Sitedeki altı tema, aynı fotoğraflar ve aynı renkler
// Kaynak: app.py TEMA_AYARLARI. Tema adları veride Türkçe tutulur (site ile ortak).

export type TemaAyari = {
  ad: string;
  resim: number; // require() ile gelen yerel fotoğraf
  zemin: string; // fotoğraf yüklenmeden görünen renk
  yazi: string;
  kart: string;
  cizgi: string;
  vurgu: string;
  perde: string; // fotoğrafın üstüne serilen, yazıyı okunur kılan katman
  acik: boolean; // açık renkli tema mı (durum çubuğu ve giriş kutuları için)
};

export const TEMALAR: TemaAyari[] = [
  { ad: "Koyu Cam", resim: require("../assets/arkaplan/koyu_cam.jpg"), zemin: "#0f0f0f", yazi: "#ffffff",
    kart: "rgba(20, 20, 20, 0.90)", cizgi: "rgba(255,255,255,0.15)", vurgu: "#5A6B7C", perde: "rgba(0,0,0,0.30)", acik: false },
  { ad: "Yakut Kızılı", resim: require("../assets/arkaplan/yakut.jpg"), zemin: "#2A0808", yazi: "#ffffff",
    kart: "rgba(35, 5, 10, 0.85)", cizgi: "rgba(255,255,255,0.15)", vurgu: "#B03A4A", perde: "rgba(0,0,0,0.35)", acik: false },
  { ad: "Turkuaz Ferahlığı", resim: require("../assets/arkaplan/turkuaz.jpg"), zemin: "#E0F2F1", yazi: "#06403c",
    kart: "rgba(240, 253, 250, 0.94)", cizgi: "rgba(0,0,0,0.12)", vurgu: "#2A9D8F", perde: "rgba(255,255,255,0.55)", acik: true },
  { ad: "Altın Zarafet", resim: require("../assets/arkaplan/altin.jpg"), zemin: "#3e2723", yazi: "#ffffff",
    kart: "rgba(38, 24, 18, 0.88)", cizgi: "rgba(255,255,255,0.15)", vurgu: "#C9A227", perde: "rgba(0,0,0,0.55)", acik: false },
  { ad: "Bordo Kadife", resim: require("../assets/arkaplan/bordo.jpg"), zemin: "#310000", yazi: "#ffebee",
    kart: "rgba(45, 0, 15, 0.90)", cizgi: "rgba(255,255,255,0.15)", vurgu: "#7B2D3B", perde: "rgba(0,0,0,0.40)", acik: false },
  { ad: "Derin Mavi", resim: require("../assets/arkaplan/derin_mavi.jpg"), zemin: "#00102A", yazi: "#e3f2fd",
    kart: "rgba(0, 15, 45, 0.90)", cizgi: "rgba(255,255,255,0.15)", vurgu: "#2F6DA8", perde: "rgba(0,0,0,0.30)", acik: false },
];

export const VARSAYILAN_TEMA = "Koyu Cam";

export const temaBul = (ad?: string | null): TemaAyari =>
  TEMALAR.find((x) => x.ad === ad) ?? TEMALAR[0];

/** #rrggbb rengine saydamlık ekler */
export function saydam(hex: string, alfa: number): string {
  const h = hex.replace("#", "");
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
  return `rgba(${r}, ${g}, ${b}, ${alfa})`;
}

/** rgba(...) kart rengini neredeyse opak yapar (açılır paneller için) */
export function opak(rgba: string, alfa = 0.97): string {
  return rgba.replace(/rgba\(([^,]+),([^,]+),([^,]+),[^)]+\)/, `rgba($1,$2,$3, ${alfa})`);
}
