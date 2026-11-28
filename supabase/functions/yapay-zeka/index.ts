// yapay-zeka/index.ts - Supabase sunucu fonksiyonu (Edge Function)
//
// Telefon uygulaması Gemini'yi doğrudan çağırmaz; bu fonksiyonu çağırır.
// Gemini anahtarı yalnızca burada, Supabase'in gizli değişkenlerinde durur:
//   Supabase > Edge Functions > Secrets > GEMINI_API_KEY
//
// İstek:  POST, başlıkta "Authorization: Bearer <kullanıcının giriş belirteci>"
//         gövde: { mod, metin?, baglam?, gorsel_b64?, gorsel_tur?, ses_b64?, ses_tur? }
// Yanıt:  { sonuc, kalan, model }  ya da  { hata, mesaj }

import { createClient } from "npm:@supabase/supabase-js@2";
import { isle, type Modlar } from "./cekirdek.ts";
import modlarJson from "./modlar.json" with { type: "json" };

const modlar = modlarJson as unknown as Modlar;
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
const GEMINI = Deno.env.get("GEMINI_API_KEY") ?? "";

const BASLIK = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Content-Type": "application/json",
};
const yanit = (durum: number, govde: unknown) => new Response(JSON.stringify(govde), { status: durum, headers: BASLIK });

// Günün tarihi siteyle aynı: UTC
const bugun = () => new Date().toISOString().slice(0, 10);

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: BASLIK });
  if (req.method !== "POST") return yanit(405, { hata: "yontem" });
  if (!GEMINI) return yanit(500, { hata: "ayar_eksik", mesaj: "GEMINI_API_KEY tanımlı değil." });

  const db = createClient(URL_, SERVIS, { auth: { persistSession: false } });

  // Kim olduğu belirteçten çözülür; gövdede gelen kullanıcı adına güvenilmez
  const belirtec = (req.headers.get("Authorization") ?? "").replace(/^Bearer\s+/i, "");
  const { data: kim } = await db.auth.getUser(belirtec);
  if (!kim?.user) return yanit(401, { hata: "giris_gerekli", mesaj: "Önce giriş yap." });
  const { data: satir } = await db.from("kullanicilar").select("username").eq("auth_id", kim.user.id).limit(1);
  const kullanici = satir?.[0]?.username;
  if (!kullanici) return yanit(403, { hata: "hesap_yok", mesaj: "Nova hesabı bulunamadı." });

  let istek;
  try {
    istek = await req.json();
  } catch {
    return yanit(400, { hata: "gecersiz_govde" });
  }

  const gun = bugun();
  const sonuc = await isle(istek, modlar, {
    kullanici,
    gun,
    hakKullan: async (k, o) => {
      const { data, error } = await db.rpc("ai_hak_kullan", { p_gun: gun, p_kullanici: k, p_ozellik: o });
      if (error) throw error;
      return Number(data);
    },
    hakIade: async (k, o) => {
      await db.rpc("ai_hak_iade", { p_gun: gun, p_kullanici: k, p_ozellik: o });
    },
    gemini: async (model, govde) => {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "x-goog-api-key": GEMINI },
        body: JSON.stringify(govde),
      });
      let g = null;
      try {
        g = await r.json();
      } catch { /* boş yanıt */ }
      return { durum: r.status, govde: g };
    },
  });
  return yanit(sonuc.durum, sonuc.govde);
});
