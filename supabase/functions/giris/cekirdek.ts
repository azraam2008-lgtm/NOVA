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
