// paylasim/index.ts - Diyetisyen bağlantısı açan sunucu fonksiyonu (Edge Function)
//
// Telefon raporu hazırlar ve buraya gönderir. Fonksiyon:
//   1. Kim olduğunu giriş belirtecinden çözer (gövdedeki kullanıcı adına güvenmez)
//   2. Rastgele bir belirteç üretir; veritabanına yalnızca SHA-256 özetini yazar
//   3. Belirteci telefona döndürür. Bağlantı: https://azzzrss.streamlit.app/?rapor=<belirteç>
// Sitedeki paylasim.py ile aynı tablo ve aynı biçim; site bağlantıyı aynen açar.
//
// İstek:  POST, "Authorization: Bearer <kullanıcının giriş belirteci>", gövde { veri, gun }
// Yanıt:  { belirtec, son_kullanma }  ya da  { hata }
// Supabase'te "Verify JWT" KAPALI olmalı (kimliği kendisi doğruluyor).

import { createClient } from "npm:@supabase/supabase-js@2";

const URL_ = Deno.env.get("SUPABASE_URL")!;
const anahtarSec = (yeniAd: string, eskiAd: string) => {
  try {
    const sozluk = JSON.parse(Deno.env.get(yeniAd) ?? "{}");
    if (sozluk.default) return String(sozluk.default);
  } catch { /* eski düzen */ }
  return Deno.env.get(eskiAd) ?? "";
};
const SERVIS = anahtarSec("SUPABASE_SECRET_KEYS", "SUPABASE_SERVICE_ROLE_KEY");

const BASLIK = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Content-Type": "application/json",
};
const yanit = (durum: number, govde: unknown) => new Response(JSON.stringify(govde), { status: durum, headers: BASLIK });

const EN_FAZLA_BOYUT = 300_000; // 90 günlük rapor bile bunun çok altında
const GUNLUK_SINIR = 20; // kötüye kullanıma karşı: kişi başı günde en fazla 20 bağlantı

// Python'daki secrets.token_urlsafe(24) ile aynı: 24 rastgele bayt, base64url, dolgusuz
function belirtecUret(): string {
  const b = crypto.getRandomValues(new Uint8Array(24));
  return btoa(String.fromCharCode(...b)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
async function ozet(metin: string): Promise<string> {
  const h = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(metin));
  return [...new Uint8Array(h)].map((x) => x.toString(16).padStart(2, "0")).join("");
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: BASLIK });
  if (req.method !== "POST") return yanit(405, { hata: "yontem" });

  const db = createClient(URL_, SERVIS, { auth: { persistSession: false } });
  const giris = (req.headers.get("Authorization") ?? "").replace(/^Bearer\s+/i, "");
  const { data: kim } = await db.auth.getUser(giris);
  if (!kim?.user) return yanit(401, { hata: "giris_gerekli" });
  const { data: satir } = await db.from("kullanicilar").select("username").eq("auth_id", kim.user.id).limit(1);
  const kullanici = satir?.[0]?.username;
  if (!kullanici) return yanit(403, { hata: "hesap_yok" });

  let istek: any;
  try {
    istek = await req.json();
  } catch {
    return yanit(400, { hata: "gecersiz_govde" });
  }
  const veri = istek?.veri;
  if (!veri || typeof veri !== "object" || !Array.isArray(veri.gunler)) return yanit(400, { hata: "gecersiz_govde" });
  if (JSON.stringify(veri).length > EN_FAZLA_BOYUT) return yanit(413, { hata: "cok_buyuk" });
  const gun = Math.min(90, Math.max(1, Math.round(Number(istek.gun) || 30)));

  const dun = new Date(Date.now() - 864e5).toISOString();
  const { count } = await db.from("paylasimlar").select("belirtec_ozeti", { count: "exact", head: true })
    .eq("username", kullanici).gte("olusturma", dun);
  if ((count ?? 0) >= GUNLUK_SINIR) return yanit(429, { hata: "limit" });

  const belirtec = belirtecUret();
  const son = new Date(Date.now() + gun * 864e5).toISOString();
  const { error } = await db.from("paylasimlar").insert({
    belirtec_ozeti: await ozet(belirtec), username: kullanici, veri, son_kullanma: son,
  });
  if (error) return yanit(500, { hata: "gecici" });
  return yanit(200, { belirtec, son_kullanma: son });
});
