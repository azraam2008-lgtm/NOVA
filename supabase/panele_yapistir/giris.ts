// giris - Supabase paneline yapıştırılacak tek dosya. ELLE DÜZENLEME;
// supabase/functions altındaki dosyaları değiştirip modlari_aktar.py'yi çalıştır.

import { createClient } from "npm:@supabase/supabase-js@2";
import bcrypt from "npm:bcryptjs@2.4.3";

// giris/cekirdek.ts
// Telefon uygulamasında kullanıcı adıyla (ya da e-postayla) giriş.
//
// Supabase'in kendi girişi e-posta ister; Nova'da insanlar kullanıcı adıyla
// giriyor ve bazılarının e-postası yok. Bu fonksiyon kullanıcı adını sunucuda
// Auth e-postasına çevirir, girişi yapar ve uygulamaya oturum belirtecini verir.
//
// Siteye hiç girmemiş eski hesaplar burada, ilk girişte taşınır: eski şifre
// özeti doğrulanır, Auth hesabı girilen şifreyle açılır.
//
// Güvenlik:
//  - "Böyle kullanıcı yok" ile "şifre yanlış" aynı yanıtı verir (hesap avı olmaz).
//  - Bir hesaba günde en fazla HATA_SINIRI yanlış deneme; sonra o gün kilitlenir.

export const HATA_SINIRI = 10;
export const SAHTE_ALAN = "hesap.nova.invalid";

export type Kayit = { username: string; email: string | null; password_hash: string | null; auth_id: string | null };
export type Oturum = { access_token: string; refresh_token: string; expires_in: number };

export type Ortam = {
  kayitBul: (alan: "username" | "email", deger: string) => Promise<Kayit | null>;
  authEposta: (authId: string) => Promise<string | null>;
  oturumAc: (eposta: string, sifre: string) => Promise<Oturum | null>;
  authOlustur: (eposta: string, sifre: string, kullanici: string) => Promise<string | null>;
  authBagla: (kullanici: string, authId: string) => Promise<boolean>;
  authSil: (authId: string) => Promise<void>;
  bcryptDogru: (sifre: string, ozet: string) => Promise<boolean>;
  sha256: (metin: string) => Promise<string>;
  hataSayisi: (kullanici: string) => Promise<number>;
  hataEkle: (kullanici: string) => Promise<void>;
};

export type Sonuc = { durum: number; govde: Record<string, unknown> };

const RET: Sonuc = { durum: 401, govde: { hata: "hatali_giris", mesaj: "Hatalı kullanıcı adı veya şifre." } };

export function girisEpostasi(kullanici: string, eposta: string | null): string {
  const e = (eposta ?? "").trim().toLowerCase();
  if (e && e.includes("@")) return e;
  const temiz = (kullanici ?? "").toLowerCase().replace(/[^a-z0-9._-]/g, "") || "kullanici";
  return `${temiz}@${SAHTE_ALAN}`;
}

async function eskiOzetDogru(o: Ortam, sifre: string, ozet: string | null): Promise<boolean> {
  if (!ozet) return false; // Google ile açılmış hesap: şifresi yok
  if (ozet.startsWith("$2")) return await o.bcryptDogru(sifre, ozet);
  return ozet === (await o.sha256(sifre));
}

export async function girisYap(istek: { kullanici?: string; sifre?: string }, o: Ortam): Promise<Sonuc> {
  const girdi = (istek.kullanici ?? "").trim().toLowerCase();
  const sifre = istek.sifre ?? "";
  if (!girdi || !sifre || girdi.length > 120 || sifre.length > 200) return RET;

  const kayit = await o.kayitBul(girdi.includes("@") ? "email" : "username", girdi);
  if (!kayit) return RET;

  if ((await o.hataSayisi(kayit.username)) >= HATA_SINIRI) {
    return { durum: 429, govde: { hata: "kilitli", mesaj: "Çok fazla yanlış deneme. Yarın tekrar dene ya da şifreni sıfırla." } };
  }
  const basarisiz = async () => {
    await o.hataEkle(kayit.username);
    return RET;
  };

  // --------------------------------------------- Zaten taşınmış hesap
  if (kayit.auth_id) {
    const eposta = (await o.authEposta(kayit.auth_id)) ?? girisEpostasi(kayit.username, kayit.email);
    const oturum = await o.oturumAc(eposta, sifre);
    return oturum ? { durum: 200, govde: { oturum, kullanici: kayit.username } } : await basarisiz();
  }

  // --------------------------------------------- İlk kez: taşı, sonra gir
  if (!(await eskiOzetDogru(o, sifre, kayit.password_hash))) return await basarisiz();

  const eposta = girisEpostasi(kayit.username, kayit.email);
  const yeniId = await o.authOlustur(eposta, sifre, kayit.username);
  if (!yeniId) {
    // Çoğu zaman: aynı e-postayla Google üzerinden açılmış bir giriş zaten var
    return { durum: 409, govde: { hata: "tasinamadi", mesaj: "Hesabın hazırlanamadı. Bir kez siteden giriş yapıp tekrar dene." } };
  }
  if (!(await o.authBagla(kayit.username, yeniId))) {
    await o.authSil(yeniId); // yarım kalmasın
    return { durum: 503, govde: { hata: "gecici", mesaj: "Giriş şu an tamamlanamadı. Biraz sonra tekrar dene." } };
  }
  const oturum = await o.oturumAc(eposta, sifre);
  return oturum
    ? { durum: 200, govde: { oturum, kullanici: kayit.username, tasindi: true } }
    : { durum: 503, govde: { hata: "gecici", mesaj: "Giriş şu an tamamlanamadı. Biraz sonra tekrar dene." } };
}

// ---------------------------------------------------------------- Kayıt
// Kurallar sitedekiyle aynı: en az 8 karakter, bir büyük harf, bir rakam.

export type KayitOrtami = Ortam & {
  kayitEkle: (satir: { username: string; email: string | null; password_hash: string }) => Promise<boolean>;
  kayitSil: (kullanici: string) => Promise<void>;
  bcryptOzet: (sifre: string) => Promise<string>;
};

export function sifreHatasi(sifre: string): string | null {
  if (sifre.length < 8) return "sifre_kisa";
  if (!/[A-ZÇĞİÖŞÜ]/.test(sifre)) return "sifre_buyuk_harf";
  if (!/[0-9]/.test(sifre)) return "sifre_rakam";
  return null;
}

export async function kayitOl(
  istek: { kullanici?: string; eposta?: string; sifre?: string },
  o: KayitOrtami,
): Promise<Sonuc> {
  const kullanici = (istek.kullanici ?? "").trim().toLowerCase();
  const eposta = (istek.eposta ?? "").trim().toLowerCase() || null;
  const sifre = istek.sifre ?? "";
  const red = (kod: string) => ({ durum: 400, govde: { hata: kod } });

  if (!/^[a-z0-9._-]{3,30}$/.test(kullanici)) return red("kullanici_gecersiz");
  if (eposta && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(eposta)) return red("eposta_gecersiz");
  if (sifre.length > 200) return red("sifre_uzun");
  const sh = sifreHatasi(sifre);
  if (sh) return red(sh);

  if (await o.kayitBul("username", kullanici)) return { durum: 409, govde: { hata: "kullanici_alinmis" } };
  if (eposta && (await o.kayitBul("email", eposta))) return { durum: 409, govde: { hata: "eposta_kayitli" } };

  if (!(await o.kayitEkle({ username: kullanici, email: eposta, password_hash: await o.bcryptOzet(sifre) }))) {
    return { durum: 409, govde: { hata: "kullanici_alinmis" } }; // aynı anda aynı adla kayıt
  }
  const authEposta = girisEpostasi(kullanici, eposta);
  const id = await o.authOlustur(authEposta, sifre, kullanici);
  if (!id) {
    await o.kayitSil(kullanici); // yarım hesap kalmasın
    return { durum: 409, govde: { hata: "eposta_kayitli" } };
  }
  if (!(await o.authBagla(kullanici, id))) {
    await o.authSil(id);
    await o.kayitSil(kullanici);
    return { durum: 503, govde: { hata: "gecici" } };
  }
  const oturum = await o.oturumAc(authEposta, sifre);
  return oturum
    ? { durum: 200, govde: { oturum, kullanici, yeni: true } }
    : { durum: 503, govde: { hata: "gecici" } };
}

// ---- index.ts
// giris/index.ts - Supabase sunucu fonksiyonu (Edge Function)
//
// İstek:  POST { kullanici, sifre }   (kullanici: kullanıcı adı ya da e-posta)
//         POST { islem: "kayit", kullanici, eposta?, sifre }   (yeni hesap)
// Yanıt:  { oturum: { access_token, refresh_token, expires_in }, kullanici }
//         Uygulama bunu supabase.auth.setSession(...) ile kullanır.
//
// Bu fonksiyon giriş yapmamış kişilerce çağrılır; panelde
// "Verify JWT" (JWT doğrulama) KAPALI olmalı. Kendi sınırlamasını yapar.


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
