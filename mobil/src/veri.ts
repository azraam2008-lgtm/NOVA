// veri.ts - Uygulamanın dış dünyayla tek bağlantı noktası
//
// Gerçek: Supabase. Uygulama yalnızca HERKESE AÇIK (publishable) anahtarı taşır;
// veritabanı kuralları (RLS) herkese yalnızca kendi satırlarını gösterir.
// Gizli anahtar ve Gemini anahtarı uygulamada YOK; sunucu fonksiyonlarında.
//
// Sahte: EXPO_PUBLIC_SAHTE=1 ile açılır; her şey bellekte. Ekranları anahtarsız
// denemek içindir, mağazaya giden sürümde kapalıdır.

import "react-native-url-polyfill/auto";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { BOS_VERI, type Veri } from "./hesap";

export const SUPABASE_URL = process.env.EXPO_PUBLIC_SUPABASE_URL || "https://klncgexnykfwzpcrijrt.supabase.co";
const ACIK_ANAHTAR = process.env.EXPO_PUBLIC_SUPABASE_KEY || "";
const SAHTE = process.env.EXPO_PUBLIC_SAHTE === "1";

export type Sonuc<T = undefined> = { tamam: true; deger: T } | { tamam: false; hata: string };

/** Sitedeki kullanici_yemekleri.veri biçimi (yemek_arama.py _yemek); değerler 100 gram başına */
export type SiteYemek = {
  ad: string; marka?: string; kaynak?: string; kod?: string;
  p: number; k: number; y: number; kcal?: number; gram?: number; ekstra?: Record<string, number>;
};
export type YemekTuru = "favori" | "kendi";
/** Yapay zekaya giden ek: fotoğraf ya da ses kaydı (sunucu ikisini de kabul eder) */
export type Gorsel = { gorsel_b64?: string; gorsel_tur?: string; ses_b64?: string; ses_tur?: string };

export interface Arka {
  oturumKullanici(): Promise<string | null>;
  girisYap(kullanici: string, sifre: string): Promise<Sonuc<string>>;
  kayitOl(kullanici: string, eposta: string, sifre: string): Promise<Sonuc<string>>;
  cikis(): Promise<void>;
  oku(kullanici: string): Promise<Veri>;
  /** En güncel veriyi okur, değiştirir, yazar. Site aynı anda yazmışsa onu ezmez. */
  guncelle(kullanici: string, degistir: (v: Veri) => Veri): Promise<Veri>;
  yapayZeka(mod: string, metin: string, baglam: string, gorsel?: Gorsel): Promise<Sonuc<any>>;
  /** Favoriler ve kendi yemekleri/tarifleri: sitede de aynı tablo */
  yemekler(kullanici: string, tur: YemekTuru): Promise<SiteYemek[]>;
  yemekKaydet(kullanici: string, tur: YemekTuru, yemek: SiteYemek): Promise<boolean>;
  yemekSil(kullanici: string, tur: YemekTuru, ad: string): Promise<boolean>;
  /** Diyetisyen bağlantısı: rapor sunucuda saklanır, telefona yalnızca belirteç döner */
  paylasimOlustur(veri: unknown, gecerlilikGun: number): Promise<Sonuc<string>>;
  paylasimSayisi(kullanici: string): Promise<number>;
  paylasimlariIptal(kullanici: string): Promise<boolean>;
}

// ------------------------------------------------------------------ gerçek
class SupabaseArka implements Arka {
  db: SupabaseClient;
  constructor() {
    this.db = createClient(SUPABASE_URL, ACIK_ANAHTAR || "eksik-anahtar", {
      auth: { storage: AsyncStorage, persistSession: true, autoRefreshToken: true, detectSessionInUrl: false },
    });
  }

  private async fonksiyon(ad: string, govde: unknown, belirtec?: string) {
    try {
      const r = await fetch(`${SUPABASE_URL}/functions/v1/${ad}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          apikey: ACIK_ANAHTAR,
          Authorization: `Bearer ${belirtec ?? ACIK_ANAHTAR}`,
        },
        body: JSON.stringify(govde),
      });
      let g: any = null;
      try { g = await r.json(); } catch { /* boş */ }
      // Sunucu tanıdık bir hata kodu döndürmediyse en azından durum kodu görünsün (sorun bulmak için)
      if (r.status !== 200 && !g?.hata) g = { ...(g ?? {}), hata: `http_${r.status}` };
      return { durum: r.status, govde: g ?? {} };
    } catch {
      return { durum: 0, govde: { hata: "baglanti" } };
    }
  }

  private async oturumuKur(g: any): Promise<Sonuc<string>> {
    const { error } = await this.db.auth.setSession({
      access_token: g.oturum.access_token, refresh_token: g.oturum.refresh_token,
    });
    // Sunucu girişi onayladı ama telefon oturumu kuramadı: çoğunlukla uygulamadaki herkese açık anahtar geçersiz
    return error ? { tamam: false, hata: `oturum: ${error.message || error.name || "?"}` } : { tamam: true, deger: g.kullanici };
  }

  async oturumKullanici() {
    const { data } = await this.db.auth.getSession();
    if (!data.session) return null;
    const { data: s } = await this.db.from("kullanicilar").select("username").limit(1);
    return s?.[0]?.username ?? null;
  }
  async girisYap(kullanici: string, sifre: string): Promise<Sonuc<string>> {
    const r = await this.fonksiyon("giris", { kullanici, sifre });
    if (r.durum === 200) return this.oturumuKur(r.govde);
    return { tamam: false, hata: r.govde.hata ?? (r.durum === 0 ? "baglanti" : `http_${r.durum}`) };
  }
  async kayitOl(kullanici: string, eposta: string, sifre: string): Promise<Sonuc<string>> {
    const r = await this.fonksiyon("giris", { islem: "kayit", kullanici, eposta, sifre });
    if (r.durum === 200) return this.oturumuKur(r.govde);
    return { tamam: false, hata: r.govde.hata ?? (r.durum === 0 ? "baglanti" : `http_${r.durum}`) };
  }
  async cikis() {
    await this.db.auth.signOut();
  }
  async oku(kullanici: string): Promise<Veri> {
    const { data, error } = await this.db.from("kullanici_verileri").select("data").eq("username", kullanici).limit(1);
    if (error) throw error;
    const v = data?.[0]?.data as Veri | undefined;
    return v ? { ...BOS_VERI(), ...v } : BOS_VERI();
  }
  async guncelle(kullanici: string, degistir: (v: Veri) => Veri) {
    const yeni = degistir(await this.oku(kullanici));
    const { error } = await this.db.from("kullanici_verileri").upsert({ username: kullanici, data: yeni });
    if (error) throw error;
    return yeni;
  }
  async yapayZeka(mod: string, metin: string, baglam: string, gorsel?: Gorsel): Promise<Sonuc<any>> {
    const { data } = await this.db.auth.getSession();
    const r = await this.fonksiyon("yapay-zeka", { mod, metin, baglam, ...(gorsel ?? {}) }, data.session?.access_token);
    if (r.durum === 200) return { tamam: true, deger: r.govde.sonuc };
    return { tamam: false, hata: r.govde.hata ?? "gecici" };
  }
  async yemekler(kullanici: string, tur: YemekTuru) {
    const { data } = await this.db.from("kullanici_yemekleri").select("veri")
      .eq("kullanici", kullanici).eq("tur", tur).order("olusturma", { ascending: false });
    return (data ?? []).map((r: any) => r.veri as SiteYemek).filter((x) => x && x.ad);
  }
  async yemekKaydet(kullanici: string, tur: YemekTuru, yemek: SiteYemek) {
    const { error } = await this.db.from("kullanici_yemekleri")
      .upsert({ kullanici, tur, ad: yemek.ad, veri: yemek }, { onConflict: "kullanici,tur,ad" });
    return !error;
  }
  async yemekSil(kullanici: string, tur: YemekTuru, ad: string) {
    const { error } = await this.db.from("kullanici_yemekleri").delete()
      .eq("kullanici", kullanici).eq("tur", tur).eq("ad", ad);
    return !error;
  }
  async paylasimOlustur(veri: unknown, gecerlilikGun: number): Promise<Sonuc<string>> {
    const { data } = await this.db.auth.getSession();
    const r = await this.fonksiyon("paylasim", { veri, gun: gecerlilikGun }, data.session?.access_token);
    if (r.durum === 200 && r.govde.belirtec) return { tamam: true, deger: String(r.govde.belirtec) };
    return { tamam: false, hata: r.govde.hata ?? "gecici" };
  }
  async paylasimSayisi(kullanici: string) {
    const { data } = await this.db.from("paylasimlar").select("son_kullanma").eq("username", kullanici);
    return (data ?? []).filter((r: any) => new Date(r.son_kullanma) > new Date()).length;
  }
  async paylasimlariIptal(kullanici: string) {
    const { error } = await this.db.from("paylasimlar").delete().eq("username", kullanici);
    return !error;
  }
}

// ------------------------------------------------------------------ sahte
class SahteArka implements Arka {
  private async durum(): Promise<{ hesaplar: Record<string, { sifre: string; veri: Veri }>; oturum: string | null }> {
    try {
      const m = await AsyncStorage.getItem("nova_sahte");
      if (m) return JSON.parse(m);
    } catch { /* boş */ }
    return { hesaplar: { demo: { sifre: "Demo1234", veri: BOS_VERI() } }, oturum: null };
  }
  private async yaz(d: any) {
    try { await AsyncStorage.setItem("nova_sahte", JSON.stringify(d)); } catch { /* boş */ }
  }
  async oturumKullanici() { return (await this.durum()).oturum; }
  async girisYap(k: string, s: string): Promise<Sonuc<string>> {
    const d = await this.durum();
    const ad = k.trim().toLowerCase();
    if (d.hesaplar[ad]?.sifre !== s) return { tamam: false, hata: "hatali_giris" };
    d.oturum = ad; await this.yaz(d);
    return { tamam: true, deger: ad };
  }
  async kayitOl(k: string, _e: string, s: string): Promise<Sonuc<string>> {
    const d = await this.durum();
    const ad = k.trim().toLowerCase();
    if (!/^[a-z0-9._-]{3,30}$/.test(ad)) return { tamam: false, hata: "kullanici_gecersiz" };
    if (d.hesaplar[ad]) return { tamam: false, hata: "kullanici_alinmis" };
    if (s.length < 8) return { tamam: false, hata: "sifre_kisa" };
    if (!/[A-ZÇĞİÖŞÜ]/.test(s)) return { tamam: false, hata: "sifre_buyuk_harf" };
    if (!/[0-9]/.test(s)) return { tamam: false, hata: "sifre_rakam" };
    d.hesaplar[ad] = { sifre: s, veri: BOS_VERI() }; d.oturum = ad; await this.yaz(d);
    return { tamam: true, deger: ad };
  }
  async cikis() { const d = await this.durum(); d.oturum = null; await this.yaz(d); }
  async oku(k: string) { return (await this.durum()).hesaplar[k]?.veri ?? BOS_VERI(); }
  async guncelle(k: string, f: (v: Veri) => Veri) {
    const d = await this.durum();
    const yeni = f(d.hesaplar[k]?.veri ?? BOS_VERI());
    d.hesaplar[k] = { ...(d.hesaplar[k] ?? { sifre: "" }), veri: yeni }; await this.yaz(d);
    return yeni;
  }
  async yemekler(k: string, tur: YemekTuru): Promise<SiteYemek[]> {
    return ((await this.durum()).hesaplar[k] as any)?.yemekler?.[tur] ?? [];
  }
  async yemekKaydet(k: string, tur: YemekTuru, y: SiteYemek) {
    const d: any = await this.durum();
    const h = d.hesaplar[k]; if (!h) return false;
    h.yemekler = h.yemekler ?? { favori: [], kendi: [] };
    h.yemekler[tur] = [y, ...(h.yemekler[tur] ?? []).filter((x: SiteYemek) => x.ad !== y.ad)];
    await this.yaz(d); return true;
  }
  async yemekSil(k: string, tur: YemekTuru, ad: string) {
    const d: any = await this.durum();
    const h = d.hesaplar[k]; if (!h?.yemekler) return true;
    h.yemekler[tur] = (h.yemekler[tur] ?? []).filter((x: SiteYemek) => x.ad !== ad);
    await this.yaz(d); return true;
  }
  async yapayZeka(mod: string, metin: string, _b?: string, gorsel?: Gorsel): Promise<Sonuc<any>> {
    await new Promise((r) => setTimeout(r, 400));
    if (mod === "label") {
      return { tamam: true, deger: { is_label: true, product_name: "Deneme bisküvi", brand: "Örnek", per_100g_protein: 7,
        per_100g_carbs: 68, per_100g_fat: 18, per_100g_kcal: 462, serving_grams: 30, notes: "Sahte yanıt" } };
    }
    if (mod === "meal" && gorsel) {
      return { tamam: true, deger: { is_food: true, assumptions: "Sahte yanıt: tabakta pilav ve tavuk varsayıldı",
        items: [{ name: "Pirinç pilavı", grams: 180, protein_per_100g: 2.7, carbs_per_100g: 28, fat_per_100g: 3.5, confidence: 0.7 },
                { name: "Izgara tavuk göğsü", grams: 120, protein_per_100g: 31, carbs_per_100g: 0, fat_per_100g: 3.6, confidence: 0.8 }] } };
    }
    if (mod === "voice") {
      return { tamam: true, deger: { is_food: true, assumptions: "Sahte yanıt",
        items: [{ name: "Haşlanmış yumurta", grams: 100, protein_per_100g: 12.6, carbs_per_100g: 1.1, fat_per_100g: 10.6, confidence: 0.8 },
                { name: "Beyaz peynir", grams: 30, protein_per_100g: 17, carbs_per_100g: 1.5, fat_per_100g: 21, confidence: 0.7 }] } };
    }
    if (mod === "coach") {
      // Kütüphanedeki ilk birkaç hareketle; biri bilerek uydurma (ayıklandığını sınamak için)
      const idler = [...(_b ?? "").matchAll(/^- ([a-z_]+) \|/gm)].map((m) => m[1]);
      const gun = (i: number) => ({ title: `Gün ${i + 1}`, focus: "Tüm vücut",
        exercises: [...idler.slice(i * 2, i * 2 + 4).map((id) => ({ exercise_id: id, sets: 3, reps: "8-12", rest_sec: 60, note: "Sahte not" })),
          { exercise_id: "uydurma_hareket", sets: 3, reps: "10", rest_sec: 60, note: "" }] });
      return { tamam: true, deger: { summary: "Sahte plan", days: [gun(0), gun(1)], safety_note: "Isın; ağrıda dur." } };
    }
    return { tamam: true, deger: { text: `(Deneme yanıtı) "${metin.split("Yeni soru: ").pop()}" sorusunu aldım.` } };
  }

  private paylasimSay = 0;
  async paylasimOlustur(): Promise<Sonuc<string>> {
    await new Promise((r) => setTimeout(r, 300)); this.paylasimSay++;
    return { tamam: true, deger: "sahte-belirtec-" + this.paylasimSay };
  }
  async paylasimSayisi() { return this.paylasimSay; }
  async paylasimlariIptal() { this.paylasimSay = 0; return true; }
}

export const arka: Arka = SAHTE ? new SahteArka() : new SupabaseArka();
export const sahteMi = SAHTE;
export const anahtarVarMi = SAHTE || !!ACIK_ANAHTAR;
