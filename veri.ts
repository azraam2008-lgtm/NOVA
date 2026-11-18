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

export interface Arka {
  oturumKullanici(): Promise<string | null>;
  girisYap(kullanici: string, sifre: string): Promise<Sonuc<string>>;
  kayitOl(kullanici: string, eposta: string, sifre: string): Promise<Sonuc<string>>;
  cikis(): Promise<void>;
  oku(kullanici: string): Promise<Veri>;
  /** En güncel veriyi okur, değiştirir, yazar. Site aynı anda yazmışsa onu ezmez. */
  guncelle(kullanici: string, degistir: (v: Veri) => Veri): Promise<Veri>;
  yapayZeka(mod: string, metin: string, baglam: string): Promise<Sonuc<any>>;
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
      return { durum: r.status, govde: g ?? {} };
    } catch {
      return { durum: 0, govde: { hata: "baglanti" } };
    }
  }

  private async oturumuKur(g: any): Promise<Sonuc<string>> {
    const { error } = await this.db.auth.setSession({
      access_token: g.oturum.access_token, refresh_token: g.oturum.refresh_token,
    });
    return error ? { tamam: false, hata: "gecici" } : { tamam: true, deger: g.kullanici };
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
    return { tamam: false, hata: r.govde.hata ?? (r.durum === 0 ? "baglanti" : "gecici") };
  }
  async kayitOl(kullanici: string, eposta: string, sifre: string): Promise<Sonuc<string>> {
    const r = await this.fonksiyon("giris", { islem: "kayit", kullanici, eposta, sifre });
    if (r.durum === 200) return this.oturumuKur(r.govde);
    return { tamam: false, hata: r.govde.hata ?? (r.durum === 0 ? "baglanti" : "gecici") };
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
  async yapayZeka(mod: string, metin: string, baglam: string): Promise<Sonuc<any>> {
    const { data } = await this.db.auth.getSession();
    const r = await this.fonksiyon("yapay-zeka", { mod, metin, baglam }, data.session?.access_token);
    if (r.durum === 200) return { tamam: true, deger: r.govde.sonuc };
    return { tamam: false, hata: r.govde.hata ?? "gecici" };
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
  async yapayZeka(mod: string, metin: string): Promise<Sonuc<any>> {
    await new Promise((r) => setTimeout(r, 400));
    if (mod === "voice") {
      return { tamam: true, deger: { is_food: true, assumptions: "Sahte yanıt",
        items: [{ name: "Haşlanmış yumurta", grams: 100, protein_per_100g: 12.6, carbs_per_100g: 1.1, fat_per_100g: 10.6, confidence: 0.8 },
                { name: "Beyaz peynir", grams: 30, protein_per_100g: 17, carbs_per_100g: 1.5, fat_per_100g: 21, confidence: 0.7 }] } };
    }
    return { tamam: true, deger: { text: `(Deneme yanıtı) "${metin.split("Yeni soru: ").pop()}" sorusunu aldım.` } };
  }
}

export const arka: Arka = SAHTE ? new SahteArka() : new SupabaseArka();
export const sahteMi = SAHTE;
export const anahtarVarMi = SAHTE || !!ACIK_ANAHTAR;
