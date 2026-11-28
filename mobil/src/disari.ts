// disari.ts - Barkod araması, fotoğraf hazırlama ve yemek biçimi dönüşümleri
//
// Barkod: Open Food Facts (açık, ücretsiz, dünya geneli). Değer yoksa uydurulmaz:
// protein, karbonhidrat ya da yağdan biri eksikse ürün "bulunamadı" sayılır ve
// kullanıcıya etiketi fotoğraflaması önerilir.
import * as ImagePicker from "expo-image-picker";
import { SaveFormat, manipulateAsync } from "expo-image-manipulator";
import { kcal } from "./hesap";
import type { Yemek } from "./yemekler";
import type { SiteYemek } from "./veri";

const OFF = "https://world.openfoodfacts.org/api/v2/product";
const ALANLAR = "code,product_name,product_name_tr,product_name_en,brands,nutriments,serving_quantity";

const sayi = (x: unknown): number | null => {
  const n = typeof x === "string" ? Number(x.replace(",", ".")) : Number(x);
  return Number.isFinite(n) ? n : null;
};
const yuvarla = (n: number, b = 1) => Math.round(n * 10 ** b) / 10 ** b;

export function siteYemegi(ad: string, p: number, k: number, y: number, o: Partial<SiteYemek> = {}): SiteYemek {
  p = Math.max(0, p); k = Math.max(0, k); y = Math.max(0, y);
  const ekstra: Record<string, number> = {};
  for (const [a, d] of Object.entries(o.ekstra ?? {})) if (d != null && Number.isFinite(d)) ekstra[a] = d;
  return {
    ad, marka: o.marka ?? "", kaynak: o.kaynak ?? "", kod: o.kod ?? "",
    p: yuvarla(p), k: yuvarla(k), y: yuvarla(y), kcal: Math.round(kcal(p, k, y)),
    gram: Math.round(o.gram || 100), ekstra,
  };
}

/** Gömülü veritabanındaki yemeği sitedeki biçime çevirir */
export const yereldenSite = (x: Yemek) => siteYemegi(x.ad, x.p, x.k, x.y, { kaynak: x.kaynak, gram: x.g, ekstra: x.ek });

export async function barkodAra(kod: string, dil: string): Promise<SiteYemek | "yok" | "baglanti"> {
  const temiz = kod.replace(/\D/g, "");
  if (temiz.length < 8) return "yok";
  try {
    const r = await fetch(`${OFF}/${temiz}.json?fields=${ALANLAR}`, { headers: { "User-Agent": "Nova/1.0 (mobil)" } });
    if (r.status === 404) return "yok";
    if (!r.ok) return "baglanti";
    const j = await r.json();
    const u = j?.product;
    if (j?.status !== 1 || !u) return "yok";
    const n = u.nutriments ?? {};
    const p = sayi(n.proteins_100g), k = sayi(n.carbohydrates_100g), y = sayi(n.fat_100g);
    if (p == null || k == null || y == null) return "yok"; // eksik değer uydurulmaz
    const ad = String(u[`product_name_${dil}`] || u.product_name || u.product_name_en || temiz).trim();
    const ekstra: Record<string, number> = {};
    for (const [anahtar, alan] of [["Lif (g)", "fiber_100g"], ["Şeker (g)", "sugars_100g"], ["Tuz (g)", "salt_100g"], ["Doymuş yağ (g)", "saturated-fat_100g"]] as const) {
      const d = sayi(n[alan]);
      if (d != null) ekstra[anahtar] = yuvarla(d, 2);
    }
    // Sitedeki MIKRO_ESLEME ile aynı: OFF gram verir, mg ya da µg'ye çevrilir
    for (const [anahtar, alan, carpan] of [
      ["Demir (mg)", "iron_100g", 1e3], ["Kalsiyum (mg)", "calcium_100g", 1e3], ["Magnezyum (mg)", "magnesium_100g", 1e3],
      ["Çinko (mg)", "zinc_100g", 1e3], ["Potasyum (mg)", "potassium_100g", 1e3], ["C vitamini (mg)", "vitamin-c_100g", 1e3],
      ["D vitamini (µg)", "vitamin-d_100g", 1e6], ["B12 vitamini (µg)", "vitamin-b12_100g", 1e6],
    ] as const) {
      const d = sayi(n[alan]);
      if (d != null) ekstra[anahtar] = yuvarla(d * carpan, 3);
    }
    return siteYemegi(ad, p, k, y, {
      marka: String(u.brands ?? "").split(",")[0].trim(), kaynak: "Open Food Facts", kod: temiz,
      gram: sayi(u.serving_quantity) || 100, ekstra,
    });
  } catch {
    return "baglanti";
  }
}

/** Yapay zekanın okuduğu besin etiketini yemeğe çevirir; değer eksikse null */
export function etikettenSite(e: any): SiteYemek | null {
  if (!e?.is_label) return null;
  const p = sayi(e.per_100g_protein), k = sayi(e.per_100g_carbs), y = sayi(e.per_100g_fat);
  if (p == null || k == null || y == null) return null;
  const ekstra: Record<string, number> = {};
  for (const [anahtar, alan] of [["Lif (g)", "per_100g_fiber"], ["Şeker (g)", "per_100g_sugar"], ["Tuz (g)", "per_100g_salt"], ["Doymuş yağ (g)", "per_100g_saturated_fat"]] as const) {
    const d = sayi(e[alan]);
    if (d != null) ekstra[anahtar] = d;
  }
  return siteYemegi(String(e.product_name || "Ürün").trim(), p, k, y, {
    marka: String(e.brand ?? "").trim(), kaynak: "Etiket", gram: sayi(e.serving_grams) || 100, ekstra,
  });
}

/**
 * Kamerayla çeker ya da galeriden seçer; 1024 piksele küçültüp JPEG olarak döndürür.
 * Küçültme hem yüklemeyi hızlandırır hem yapay zeka hakkını boşa harcamaz.
 * null: kullanıcı vazgeçti; "izin": kamera/galeri izni verilmedi.
 */
export async function fotografAl(kaynak: "kamera" | "galeri"): Promise<{ b64: string; uri: string } | null | "izin"> {
  const izin = kaynak === "kamera"
    ? await ImagePicker.requestCameraPermissionsAsync()
    : await ImagePicker.requestMediaLibraryPermissionsAsync();
  if (!izin.granted) return "izin";
  const secenek: ImagePicker.ImagePickerOptions = { mediaTypes: ["images"], quality: 0.8, allowsEditing: false };
  const r = kaynak === "kamera" ? await ImagePicker.launchCameraAsync(secenek) : await ImagePicker.launchImageLibraryAsync(secenek);
  if (r.canceled || !r.assets?.[0]) return null;
  const k = await manipulateAsync(r.assets[0].uri, [{ resize: { width: 1024 } }], { compress: 0.6, format: SaveFormat.JPEG, base64: true });
  return k.base64 ? { b64: k.base64, uri: k.uri } : null;
}
