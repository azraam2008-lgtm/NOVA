// oruc.ts - Oruç modu (sitedeki ramazan.py ile aynı kurallar)
//
// Saatler Aladhan'dan gelir (ücretsiz, dünya geneli, anahtarsız). Servise ulaşılamazsa
// kullanıcının elle girdiği saatler kullanılır. Profil alanları siteyle ortak:
// oruc_modu, sehir, ulke, namaz_metodu, elle_imsak, elle_iftar.
import type { Profil } from "./hesap";

const API = "https://api.aladhan.com/v1/timingsByCity";

export const METOTLAR: [number, string][] = [
  [13, "Diyanet İşleri Başkanlığı (Türkiye)"],
  [3, "Muslim World League"],
  [2, "Islamic Society of North America"],
  [4, "Umm Al-Qura (Mekke)"],
  [5, "Egyptian General Authority of Survey"],
  [1, "University of Islamic Sciences, Karachi"],
  [12, "Union Organization Islamic de France"],
  [11, "Majlis Ugama Islam Singapura"],
  [17, "JAKIM (Malezya)"],
  [20, "Kemenag (Endonezya)"],
];
export const VARSAYILAN_METOT = 3;
export const RAMAZAN_AYI = 9;
export const SU_HEDEFI = 2.5;

export type Saatler = {
  imsak: string; iftar: string; hicriAy: number; hicriGun: number; hicriAyAdi: string; elle?: boolean;
};

const temiz = (d: unknown) => (d ? String(d).split(" ")[0].trim() : null); // "05:12 (+03)" -> "05:12"
const onbellek = new Map<string, { zaman: number; saatler: Saatler | null }>();

export function saatAyikla(ham: any): Saatler | null {
  try {
    const v = ham?.data ?? {};
    const s = v.timings ?? {};
    const hicri = v.date?.hijri ?? {};
    const imsak = temiz(s.Imsak) ?? temiz(s.Fajr);
    const iftar = temiz(s.Maghrib) ?? temiz(s.Sunset);
    if (!imsak || !iftar) return null;
    return {
      imsak, iftar, hicriAy: Number(hicri.month?.number ?? 0), hicriGun: Number(hicri.day ?? 0),
      hicriAyAdi: String(hicri.month?.en ?? "").trim(),
    };
  } catch {
    return null;
  }
}

const gunMetni = (d: Date) => `${String(d.getDate()).padStart(2, "0")}-${String(d.getMonth() + 1).padStart(2, "0")}-${d.getFullYear()}`;

/** Şehre göre günün imsak ve iftarı; olmazsa elle girilenler; o da yoksa null */
export async function saatleriAl(p: Profil, gun = new Date()): Promise<Saatler | null> {
  const sehir = String(p.sehir ?? "").trim(), ulke = String(p.ulke ?? "").trim();
  if (sehir && ulke) {
    const metot = Number(p.namaz_metodu ?? VARSAYILAN_METOT);
    const anahtar = `${sehir}|${ulke}|${metot}|${gunMetni(gun)}`;
    const o = onbellek.get(anahtar);
    if (o && Date.now() - o.zaman < 6 * 3600e3 && o.saatler) return o.saatler;
    try {
      const url = `${API}/${gunMetni(gun)}?city=${encodeURIComponent(sehir)}&country=${encodeURIComponent(ulke)}&method=${metot}`;
      const r = await fetch(url);
      if (r.ok) {
        const s = saatAyikla(await r.json());
        onbellek.set(anahtar, { zaman: Date.now(), saatler: s });
        if (s) return s;
      }
    } catch { /* elle girilene düş */ }
  }
  const ei = String(p.elle_imsak ?? "").trim(), ef = String(p.elle_iftar ?? "").trim();
  if (/^\d{1,2}:\d{2}$/.test(ei) && /^\d{1,2}:\d{2}$/.test(ef)) {
    return { imsak: ei, iftar: ef, hicriAy: 0, hicriGun: 0, hicriAyAdi: "", elle: true };
  }
  return null;
}

const bugunSaat = (metin: string, gun: Date) => {
  const [s, d] = metin.split(":").map(Number);
  const x = new Date(gun); x.setHours(s, d, 0, 0); return x;
};

/** Sıradaki olay ve kalan milisaniye: imsaktan önce "sahur", iftara kadar "iftar", sonra yarının sahuru */
export function sonrakiOlay(s: Saatler, simdi = new Date()): ["sahur" | "iftar", number] {
  const imsak = bugunSaat(s.imsak, simdi), iftar = bugunSaat(s.iftar, simdi);
  if (simdi < imsak) return ["sahur", +imsak - +simdi];
  if (simdi < iftar) return ["iftar", +iftar - +simdi];
  return ["sahur", +imsak + 864e5 - +simdi];
}

/** 1:59 biçimi: altı dilde de doğru ve kısa (kelimeyle yazmak tekil/çoğul sorunu çıkarıyor) */
export function sureMetni(ms: number): string {
  const dk = Math.max(0, Math.floor(ms / 60000));
  return `${Math.floor(dk / 60)}:${String(dk % 60).padStart(2, "0")}`;
}

export function orucluMu(s: Saatler, simdi = new Date()): boolean {
  return bugunSaat(s.imsak, simdi) <= simdi && simdi < bugunSaat(s.iftar, simdi);
}

// Sitedeki ONERILER ile aynı metinler (çevirileri dil.ts'de)
export const ONERILER: Record<"sahur" | "iftar" | "su" | "egzersiz", string[]> = {
  sahur: [
    "Sahurda protein ve lif birlikte olsun: yumurta, peynir, yulaf, tam tahıllı ekmek, zeytin ve bol sebze uzun süre tok tutar.",
    "Çok tuzlu yiyecekler gün içinde susatır; sahurda turşu, salam ve hazır çorbadan uzak dur.",
    "Sahuru atlama. Atlanan sahur, iftarda aşırı yemeye ve ertesi gün halsizliğe yol açıyor.",
  ],
  iftar: [
    "İftarı hafif aç: su, hurma ya da çorba. Mideyi birden doldurmak şişkinlik ve ani şeker yükselmesi yapıyor.",
    "Ana yemeğe birkaç dakika ara verdikten sonra geç; tokluk hissi beyne yaklaşık yirmi dakikada ulaşıyor.",
    "Tatlıyı iftarın hemen üstüne değil, bir iki saat sonra ve küçük porsiyon olarak ye.",
  ],
  su: [
    "Günlük suyunu iftar ile sahur arasına yay. Bir seferde çok su içmek işe yaramıyor, vücut fazlasını atıyor.",
    "Çay ve kahve idrar söktürüyor; iftardan sonra ikisini de ölçülü tut.",
  ],
  egzersiz: [
    "Ağır antrenmanı iftardan bir iki saat sonraya al. Aç karnına ağır çalışmak kas kaybını hızlandırıyor.",
    "Gün içinde hafif yürüyüş sorun değil, ama sıcakta ve öğle saatlerinde kaçın.",
  ],
};
