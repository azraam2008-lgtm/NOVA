// giris/index.ts - Supabase sunucu fonksiyonu (Edge Function)
//
// İstek:  POST { kullanici, sifre }   (kullanici: kullanıcı adı ya da e-posta)
//         POST { islem: "kayit", kullanici, eposta?, sifre }   (yeni hesap)
// Yanıt:  { oturum: { access_token, refresh_token, expires_in }, kullanici }
//         Uygulama bunu supabase.auth.setSession(...) ile kullanır.
//
// Bu fonksiyon giriş yapmamış kişilerce çağrılır; panelde
// "Verify JWT" (JWT doğrulama) KAPALI olmalı. Kendi sınırlamasını yapar.

import { createClient } from "npm:@supabase/supabase-js@2";
import bcrypt from "npm:bcryptjs@2.4.3";
import { girisYap, kayitOl } from "./cekirdek.ts";

const URL_ = Deno.env.get("SUPABASE_URL")!;
// Supabase'in yeni anahtarları (sb_publishable_ / sb_secret_) varsa onlar, yoksa eskileri
const anahtarSec = (yeniAd: string, eskiAd: string) => {
  try {
    const sozluk = JSON.parse(Deno.env.get(yeniAd) ?? "{}");
    if (sozluk.default) return String(sozluk.default);
  } catch { /* eski düzen */ }
  return Deno.env.get(eskiAd) ?? "";
};
const SERVIS = anahtarSec("SUPABASE_SECRET_KEYS", "SUPABASE_SERVICE_ROLE_KEY");
const ACIK = anahtarSec("SUPABASE_PUBLISHABLE_KEYS", "SUPABASE_ANON_KEY");

const BASLIK = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Content-Type": "application/json",
};
const yanit = (durum: number, govde: unknown) => new Response(JSON.stringify(govde), { status: durum, headers: BASLIK });
const bugun = () => new Date().toISOString().slice(0, 10);

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: BASLIK });
  if (req.method !== "POST") return yanit(405, { hata: "yontem" });

  let istek;
  try {
    istek = await req.json();
  } catch {
    return yanit(400, { hata: "gecersiz_govde" });
  }

  const db = createClient(URL_, SERVIS, { auth: { persistSession: false } });
  const gun = bugun();

  const ortam = {
    kayitBul: async (alan, deger) => {
      const { data } = await db.from("kullanicilar")
        .select("username, email, password_hash, auth_id").eq(alan, deger).limit(1);
      return data?.[0] ?? null;
    },
    authEposta: async (id) => {
      const { data } = await db.auth.admin.getUserById(id);
      return data?.user?.email ?? null;
    },
    oturumAc: async (eposta, sifre) => {
      // Herkese açık anahtarla, ayrı bir istemcide
      const acik = createClient(URL_, ACIK, { auth: { persistSession: false } });
      const { data } = await acik.auth.signInWithPassword({ email: eposta, password: sifre });
      const s = data?.session;
      return s ? { access_token: s.access_token, refresh_token: s.refresh_token, expires_in: s.expires_in } : null;
    },
    authOlustur: async (eposta, sifre, kullanici) => {
      const { data } = await db.auth.admin.createUser({
        email: eposta, password: sifre, email_confirm: true, user_metadata: { username: kullanici },
      });
      return data?.user?.id ?? null;
    },
    authBagla: async (kullanici, id) => {
      const { error } = await db.from("kullanicilar").update({ auth_id: id }).eq("username", kullanici);
      return !error;
    },
    authSil: async (id) => {
      await db.auth.admin.deleteUser(id);
    },
    bcryptDogru: async (sifre, ozet) => bcrypt.compareSync(sifre, ozet),
    sha256: async (metin) => {
      const ozet = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(metin));
      return Array.from(new Uint8Array(ozet)).map((b) => b.toString(16).padStart(2, "0")).join("");
    },
    // Yanlış denemeler yapay zeka sayacının tablosunda tutulur (ayrı tablo gerekmez)
    hataSayisi: async (k) => {
      const { data } = await db.from("ai_kullanim").select("adet")
        .eq("gun", gun).eq("kullanici", `giris:${k}`).eq("ozellik", "hata").limit(1);
      return Number(data?.[0]?.adet ?? 0);
    },
    hataEkle: async (k: string) => {
      await db.rpc("ai_hak_kullan", { p_gun: gun, p_kullanici: `giris:${k}`, p_ozellik: "hata" });
    },
    kayitEkle: async (satir: { username: string; email: string | null; password_hash: string }) => {
      const { error } = await db.from("kullanicilar").insert(satir);
      return !error;
    },
    kayitSil: async (k: string) => {
      await db.from("kullanicilar").delete().eq("username", k);
    },
    bcryptOzet: async (sifre: string) => bcrypt.hashSync(sifre, 10),
  };
  const sonuc = istek?.islem === "kayit" ? await kayitOl(istek, ortam) : await girisYap(istek, ortam);
  return yanit(sonuc.durum, sonuc.govde);
});
