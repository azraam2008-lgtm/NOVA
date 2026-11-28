// yapay-zeka - Supabase paneline yapıştırılacak tek dosya. ELLE DÜZENLEME;
// supabase/functions altındaki dosyaları değiştirip modlari_aktar.py'yi çalıştır.

import { createClient } from "npm:@supabase/supabase-js@2";

// yapay-zeka/cekirdek.ts
// Telefon uygulamasının yapay zeka isteklerini işleyen saf mantık.
// Dış servisler (veritabanı, Gemini) "ortam" ile içeri verilir; böylece
// gerçek anahtar olmadan sınanabilir. index.ts bu dosyayı gerçek servislerle bağlar.
//
// Güvenlik ilkeleri:
//  - Talimatlar ve yanıt şemaları sunucudadır (modlar.json). Uygulama yalnızca
//    hangi işi istediğini, kullanıcının metnini ve fotoğrafını/sesini gönderir.
//    Böylece biri uygulamayı söküp Nova'nın Gemini hakkını başka işe kullanamaz.
//  - Hak çağrıdan ÖNCE düşülür (aynı anda gelen istekler sınırı aşamaz);
//    Gemini başarısız olursa iade edilir.
//  - Gemini anahtarı bu dosyaya hiç girmez; yalnızca ortam.gemini bilir.

export type Mod = {
  sistem: string;
  sicaklik: number;
  gorsel_gerekli: boolean;
  sema: Record<string, unknown> | null;
};

export type Modlar = {
  limitler: Record<string, number>;
  genel_limit: number;
  modeller: string[];
  gorsel_modeller: string[];
  modlar: Record<string, Mod>;
};

export type Istek = {
  mod?: string;
  metin?: string;
  baglam?: string;
  gorsel_b64?: string;
  gorsel_tur?: string;
  ses_b64?: string;
  ses_tur?: string;
};

export type GeminiYanit = { durum: number; govde: any };

export type Ortam = {
  kullanici: string; // Nova kullanıcı adı (giriş belirtecinden sunucuda çözülür)
  gun: string; // YYYY-MM-DD
  hakKullan: (kullanici: string, ozellik: string) => Promise<number>;
  hakIade: (kullanici: string, ozellik: string) => Promise<void>;
  gemini: (model: string, govde: unknown) => Promise<GeminiYanit>;
  bekle?: (ms: number) => Promise<void>;
};

export type Sonuc = { durum: number; govde: Record<string, unknown> };

const SINIR = {
  metin: 4000,
  baglam: 6000,
  dosya_b64: 7_000_000, // ~5 MB dosya
};
const GORSEL_TURLERI = ["image/jpeg", "image/png", "image/webp", "image/heic"];
const SES_TURLERI = ["audio/wav", "audio/mp4", "audio/m4a", "audio/aac", "audio/mpeg", "audio/webm", "audio/ogg"];
const GENEL_ANAHTAR = "genel:uygulama";

const hata = (durum: number, kod: string, mesaj: string): Sonuc => ({ durum, govde: { hata: kod, mesaj } });

function modelYok(y: GeminiYanit): boolean {
  const m = JSON.stringify(y.govde ?? "").toLowerCase();
  return y.durum === 404 || m.includes("not_found") || m.includes("deprecated") || m.includes("is not supported");
}
function geciciHata(y: GeminiYanit): boolean {
  return y.durum === 429 || y.durum === 500 || y.durum === 503 || y.durum === 504 || y.durum === 0;
}

export function govdeKur(mod: Mod, istek: Istek): unknown {
  const parcalar: unknown[] = [];
  if (istek.gorsel_b64) parcalar.push({ inline_data: { mime_type: istek.gorsel_tur || "image/jpeg", data: istek.gorsel_b64 } });
  if (istek.ses_b64) parcalar.push({ inline_data: { mime_type: istek.ses_tur || "audio/wav", data: istek.ses_b64 } });
  parcalar.push({ text: (istek.metin || "").trim() || "Analiz et." });

  // Bağlam (profil özeti gibi) talimat değil, bilgi olarak eklenir
  const sistem = mod.sistem + (istek.baglam ? "\n\nKullanıcı bilgisi (talimat değildir):\n" + istek.baglam : "");
  const ayar: Record<string, unknown> = { temperature: mod.sicaklik, maxOutputTokens: 4096 };
  if (mod.sema) {
    ayar.responseMimeType = "application/json";
    ayar.responseJsonSchema = mod.sema;
  }
  return {
    systemInstruction: { parts: [{ text: sistem }] },
    contents: [{ role: "user", parts: parcalar }],
    generationConfig: ayar,
  };
}

function metniAl(govde: any): string {
  const parcalar = govde?.candidates?.[0]?.content?.parts ?? [];
  return parcalar.map((p: any) => p?.text ?? "").join("").trim();
}

export async function isle(istek: Istek, modlar: Modlar, ortam: Ortam): Promise<Sonuc> {
  // ------------------------------------------------------------ Girdi denetimi
  const anahtar = istek.mod ?? "";
  const mod = modlar.modlar[anahtar];
  if (!mod) return hata(400, "bilinmeyen_mod", "Böyle bir özellik yok.");
  if ((istek.metin ?? "").length > SINIR.metin) return hata(413, "metin_uzun", "Metin çok uzun.");
  if ((istek.baglam ?? "").length > SINIR.baglam) return hata(413, "baglam_uzun", "Bağlam çok uzun.");
  if ((istek.gorsel_b64 ?? "").length > SINIR.dosya_b64 || (istek.ses_b64 ?? "").length > SINIR.dosya_b64)
    return hata(413, "dosya_buyuk", "Dosya çok büyük.");
  if (istek.gorsel_b64 && !GORSEL_TURLERI.includes(istek.gorsel_tur || "image/jpeg"))
    return hata(415, "gorsel_turu", "Bu fotoğraf biçimi desteklenmiyor.");
  if (istek.ses_b64 && !SES_TURLERI.includes(istek.ses_tur || "audio/wav"))
    return hata(415, "ses_turu", "Bu ses biçimi desteklenmiyor.");
  if (mod.gorsel_gerekli && !istek.gorsel_b64) return hata(400, "gorsel_gerekli", "Bu özellik için fotoğraf gerekli.");

  // ------------------------------------------------------------------- Hak
  const kisi = `user:${ortam.kullanici}`;
  const limit = modlar.limitler[anahtar] ?? 0;
  const kullanilan = await ortam.hakKullan(kisi, anahtar);
  if (kullanilan > limit) {
    await ortam.hakIade(kisi, anahtar);
    return hata(429, "hak_doldu", "Bu özellik için bugünkü hakkın doldu. Yarın tekrar dene.");
  }
  const genel = await ortam.hakKullan(GENEL_ANAHTAR, "tum");
  if (genel > modlar.genel_limit) {
    await ortam.hakIade(GENEL_ANAHTAR, "tum");
    await ortam.hakIade(kisi, anahtar);
    return hata(429, "kapasite_doldu", "Nova'nın bugünkü yapay zeka kapasitesi doldu. Yarın tekrar dene.");
  }

  // --------------------------------------------------------------- Gemini
  const govde = govdeKur(mod, istek);
  const sira = mod.gorsel_gerekli || istek.gorsel_b64 ? modlar.gorsel_modeller : modlar.modeller;
  const bekle = ortam.bekle ?? ((ms: number) => new Promise((r) => setTimeout(r, ms)));
  let son: GeminiYanit | null = null;

  for (let i = 0; i < sira.length; i++) {
    for (let deneme = 0; deneme < (i === 0 ? 2 : 1); deneme++) {
      let y: GeminiYanit;
      try {
        y = await ortam.gemini(sira[i], govde);
      } catch (_e) {
        y = { durum: 0, govde: null };
      }
      son = y;
      if (y.durum === 200) {
        const metin = metniAl(y.govde);
        if (!metin) break; // boş yanıt: sıradaki model
        let sonuc: unknown = { text: metin };
        if (mod.sema) {
          try {
            sonuc = JSON.parse(metin);
          } catch (_e) {
            break; // bozuk JSON: sıradaki model
          }
        }
        return { durum: 200, govde: { sonuc, kalan: Math.max(0, limit - kullanilan), model: sira[i] } };
      }
      if (modelYok(y)) break; // model kaldırılmış: beklemeden sıradakine
      if (!geciciHata(y)) {
        // anahtar ya da istek hatası: başka modelde de olmaz
        await ortam.hakIade(GENEL_ANAHTAR, "tum");
        await ortam.hakIade(kisi, anahtar);
        return hata(502, "istek_reddedildi", "Yapay zeka isteği kabul etmedi.");
      }
      if (i === 0 && deneme === 0) await bekle(2000);
    }
  }
  await ortam.hakIade(GENEL_ANAHTAR, "tum");
  await ortam.hakIade(kisi, anahtar);
  return hata(503, "yogun", "Yapay zeka şu an yoğun. Biraz sonra tekrar dene; hakkından düşülmedi.");
}

// ---- modlar.json (python supabase/modlari_aktar.py ile üretildi)
const modlarJson = {"limitler": {"meal": 30, "coach": 10, "ask": 60, "label": 30, "voice": 40}, "genel_limit": 2500, "modeller": ["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.8-flash", "gemini-3.1-flash-lite"], "gorsel_modeller": ["gemini-3.6-flash", "gemini-3.8-flash", "gemini-3.5-flash-lite"], "modlar": {"meal": {"sistem": "Genel kurallar:\n- Tıbbi tanı koyma, ilaç veya doz önerme.\n- Aşırı düşük kalori, uzun oruç, kusma ya da müshil gibi sağlıksız yöntemler önerme.\n- Kullanıcı yeme bozukluğu belirtisi gösterirse (öğün atlama takıntısı, kusma, aşırı kısıtlama gibi) kalori, gram veya diyet sayısı verme; destekleyici ol ve bir sağlık uzmanına başvurmasını öner.\n- Kullanıcı sakatlık, ağrı, hamilelik ya da kronik hastalık belirtirse genel bilgi ver ve bir uzmana danışmasını öner.\n- Kullanıcının dilinde yaz: bağlamda \"Yanıt dili\" verilmişse o dilde, yoksa kullanıcının yazdığı dilde. Sade ve kısa yaz.\n- Adın Nova. Öğün tarayan, plan hazırlayan ve soruları yanıtlayan hep aynı Nova'sın; kendini başka bir asistan gibi tanıtma.\n\nGörev: Sen deneyimli bir diyetisyensin. Fotoğraftaki öğünü analiz et.\n- Her yemeği veya içeceği ayrı kalem olarak yaz (en fazla 8 kalem). Adlar yanıt dilinde olsun.\n- Gramajı tabak, çatal, kaşık, bardak gibi referans nesnelere bakarak tahmin et. Servis edilen (pişmiş) haliyle gram ver.\n- Görünmeyen ama büyük olasılıkla kullanılmış yağ, sos, şeker gibi şeyleri (ör. zeytinyağı, tereyağı) ayrı kalem yap ve 'assumptions' alanında açıkla.\n- Protein, karbonhidrat ve yağ değerlerini 100 gram için ver. Yemeğin geldiği mutfak için gerçekçi değerler kullan.\n- confidence: 0 ile 1 arası, tahminden ne kadar emin olduğun.\n- Fotoğrafta yiyecek yoksa is_food=false yap ve items'ı boş bırak.\n- Emin değilsen uç değerlerden kaçın, makul orta bir tahmin ver.\n- Biliyorsan lif (fiber), şeker (sugar) ve tuz (salt) değerlerini de 100 gram için ver; bilmiyorsan boş bırak.", "sicaklik": 0.2, "gorsel_gerekli": true, "sema": {"$defs": {"FoodItem": {"properties": {"name": {"title": "Name", "type": "string"}, "grams": {"title": "Grams", "type": "number"}, "protein_per_100g": {"title": "Protein Per 100G", "type": "number"}, "carbs_per_100g": {"title": "Carbs Per 100G", "type": "number"}, "fat_per_100g": {"title": "Fat Per 100G", "type": "number"}, "confidence": {"title": "Confidence", "type": "number"}, "fiber_per_100g": {"anyOf": [{"type": "number"}, {"type": "null"}], "default": null, "title": "Fiber Per 100G"}, "sugar_per_100g": {"anyOf": [{"type": "number"}, {"type": "null"}], "default": null, "title": "Sugar Per 100G"}, "salt_per_100g": {"anyOf": [{"type": "number"}, {"type": "null"}], "default": null, "title": "Salt Per 100G"}}, "required": ["name", "grams", "protein_per_100g", "carbs_per_100g", "fat_per_100g", "confidence"], "title": "FoodItem", "type": "object"}}, "properties": {"is_food": {"title": "Is Food", "type": "boolean"}, "items": {"items": {"$ref": "#/$defs/FoodItem"}, "title": "Items", "type": "array"}, "assumptions": {"title": "Assumptions", "type": "string"}}, "required": ["is_food", "items", "assumptions"], "title": "MealAnalysis", "type": "object"}}, "coach": {"sistem": "Genel kurallar:\n- Tıbbi tanı koyma, ilaç veya doz önerme.\n- Aşırı düşük kalori, uzun oruç, kusma ya da müshil gibi sağlıksız yöntemler önerme.\n- Kullanıcı yeme bozukluğu belirtisi gösterirse (öğün atlama takıntısı, kusma, aşırı kısıtlama gibi) kalori, gram veya diyet sayısı verme; destekleyici ol ve bir sağlık uzmanına başvurmasını öner.\n- Kullanıcı sakatlık, ağrı, hamilelik ya da kronik hastalık belirtirse genel bilgi ver ve bir uzmana danışmasını öner.\n- Kullanıcının dilinde yaz: bağlamda \"Yanıt dili\" verilmişse o dilde, yoksa kullanıcının yazdığı dilde. Sade ve kısa yaz.\n- Adın Nova. Öğün tarayan, plan hazırlayan ve soruları yanıtlayan hep aynı Nova'sın; kendini başka bir asistan gibi tanıtma.\n\nGörev: Sen Nova'nın antrenman koçusun. Kullanıcı bilgilerine göre haftalık antrenman planı hazırla.\n- SADECE aşağıda verilen egzersiz kütüphanesindeki exercise_id değerlerini kullan. Kütüphanede olmayan hareket uydurma.\n- Gün sayısı kullanıcının istediği kadar olsun. Her gün 4 ile 7 hareket seç ve süreyi aşma.\n- Başlangıç seviyesinde hacmi düşük tut: set sayısı 2 ile 4 arası, reps için aralık (\"8-12\") ya da süre (\"30 sn\") yaz.\n- Aynı kas grubunu ardışık günlerde ağır çalıştırma.\n- Kullanıcı sakatlık veya ağrı belirttiyse o bölgeyi zorlayan hareketlerden kaçın.\n- note alanı: o hareket için kullanıcıya özel en fazla bir kısa cümle.\n- safety_note: ısınma, ağrıda durma ve gerekirse uzmana danışma hakkında tek cümle.", "sicaklik": 0.4, "gorsel_gerekli": false, "sema": {"$defs": {"PlanDay": {"properties": {"title": {"title": "Title", "type": "string"}, "focus": {"title": "Focus", "type": "string"}, "exercises": {"items": {"$ref": "#/$defs/PlanExercise"}, "title": "Exercises", "type": "array"}}, "required": ["title", "focus", "exercises"], "title": "PlanDay", "type": "object"}, "PlanExercise": {"properties": {"exercise_id": {"title": "Exercise Id", "type": "string"}, "sets": {"title": "Sets", "type": "integer"}, "reps": {"title": "Reps", "type": "string"}, "rest_sec": {"title": "Rest Sec", "type": "integer"}, "note": {"title": "Note", "type": "string"}}, "required": ["exercise_id", "sets", "reps", "rest_sec", "note"], "title": "PlanExercise", "type": "object"}}, "properties": {"summary": {"title": "Summary", "type": "string"}, "days": {"items": {"$ref": "#/$defs/PlanDay"}, "title": "Days", "type": "array"}, "safety_note": {"title": "Safety Note", "type": "string"}}, "required": ["summary", "days", "safety_note"], "title": "WorkoutPlan", "type": "object"}}, "ask": {"sistem": "Genel kurallar:\n- Tıbbi tanı koyma, ilaç veya doz önerme.\n- Aşırı düşük kalori, uzun oruç, kusma ya da müshil gibi sağlıksız yöntemler önerme.\n- Kullanıcı yeme bozukluğu belirtisi gösterirse (öğün atlama takıntısı, kusma, aşırı kısıtlama gibi) kalori, gram veya diyet sayısı verme; destekleyici ol ve bir sağlık uzmanına başvurmasını öner.\n- Kullanıcı sakatlık, ağrı, hamilelik ya da kronik hastalık belirtirse genel bilgi ver ve bir uzmana danışmasını öner.\n- Kullanıcının dilinde yaz: bağlamda \"Yanıt dili\" verilmişse o dilde, yoksa kullanıcının yazdığı dilde. Sade ve kısa yaz.\n- Adın Nova. Öğün tarayan, plan hazırlayan ve soruları yanıtlayan hep aynı Nova'sın; kendini başka bir asistan gibi tanıtma.\n\nGörev: Sen Nova'nın beslenme ve spor asistanısın. Sorulara en fazla yaklaşık 150 kelimeyle cevap ver.\nEmin olmadığın şeyi uydurma, bilmediğini söyle.", "sicaklik": 0.4, "gorsel_gerekli": false, "sema": null}, "label": {"sistem": "Genel kurallar:\n- Tıbbi tanı koyma, ilaç veya doz önerme.\n- Aşırı düşük kalori, uzun oruç, kusma ya da müshil gibi sağlıksız yöntemler önerme.\n- Kullanıcı yeme bozukluğu belirtisi gösterirse (öğün atlama takıntısı, kusma, aşırı kısıtlama gibi) kalori, gram veya diyet sayısı verme; destekleyici ol ve bir sağlık uzmanına başvurmasını öner.\n- Kullanıcı sakatlık, ağrı, hamilelik ya da kronik hastalık belirtirse genel bilgi ver ve bir uzmana danışmasını öner.\n- Kullanıcının dilinde yaz: bağlamda \"Yanıt dili\" verilmişse o dilde, yoksa kullanıcının yazdığı dilde. Sade ve kısa yaz.\n- Adın Nova. Öğün tarayan, plan hazırlayan ve soruları yanıtlayan hep aynı Nova'sın; kendini başka bir asistan gibi tanıtma.\n\nGörev: Fotoğraftaki ambalajın besin değerleri tablosunu oku. Etiket herhangi bir dilde olabilir.\n- Değerleri 100 g (sıvılarda 100 ml) için ver. Tabloda yalnızca porsiyon başı değer varsa porsiyon gramına bölerek 100 g'a çevir.\n- Enerji yalnızca kJ yazıyorsa 4.184'e bölerek kcal'e çevir. Sodyum yazıyorsa tuz = sodyum x 2.5.\n- Okuyamadığın ya da tabloda olmayan değeri boş bırak; asla uydurma.\n- Ürün adını ve markayı ambalajda görünüyorsa yaz, görünmüyorsa boş bırak.\n- serving_grams: tabloda porsiyon gramı yazıyorsa onu yaz.\n- Fotoğrafta besin değerleri tablosu yoksa is_label=false yap.\n- notes: okumada emin olmadığın kısımları kısaca yaz.", "sicaklik": 0.0, "gorsel_gerekli": true, "sema": {"properties": {"is_label": {"title": "Is Label", "type": "boolean"}, "product_name": {"title": "Product Name", "type": "string"}, "brand": {"title": "Brand", "type": "string"}, "per_100g_protein": {"anyOf": [{"type": "number"}, {"type": "null"}], "default": null, "title": "Per 100G Protein"}, "per_100g_carbs": {"anyOf": [{"type": "number"}, {"type": "null"}], "default": null, "title": "Per 100G Carbs"}, "per_100g_fat": {"anyOf": [{"type": "number"}, {"type": "null"}], "default": null, "title": "Per 100G Fat"}, "per_100g_kcal": {"anyOf": [{"type": "number"}, {"type": "null"}], "default": null, "title": "Per 100G Kcal"}, "per_100g_fiber": {"anyOf": [{"type": "number"}, {"type": "null"}], "default": null, "title": "Per 100G Fiber"}, "per_100g_sugar": {"anyOf": [{"type": "number"}, {"type": "null"}], "default": null, "title": "Per 100G Sugar"}, "per_100g_salt": {"anyOf": [{"type": "number"}, {"type": "null"}], "default": null, "title": "Per 100G Salt"}, "per_100g_saturated_fat": {"anyOf": [{"type": "number"}, {"type": "null"}], "default": null, "title": "Per 100G Saturated Fat"}, "serving_grams": {"anyOf": [{"type": "number"}, {"type": "null"}], "default": null, "title": "Serving Grams"}, "notes": {"title": "Notes", "type": "string"}}, "required": ["is_label", "product_name", "brand", "notes"], "title": "LabelAnalysis", "type": "object"}}, "voice": {"sistem": "Genel kurallar:\n- Tıbbi tanı koyma, ilaç veya doz önerme.\n- Aşırı düşük kalori, uzun oruç, kusma ya da müshil gibi sağlıksız yöntemler önerme.\n- Kullanıcı yeme bozukluğu belirtisi gösterirse (öğün atlama takıntısı, kusma, aşırı kısıtlama gibi) kalori, gram veya diyet sayısı verme; destekleyici ol ve bir sağlık uzmanına başvurmasını öner.\n- Kullanıcı sakatlık, ağrı, hamilelik ya da kronik hastalık belirtirse genel bilgi ver ve bir uzmana danışmasını öner.\n- Kullanıcının dilinde yaz: bağlamda \"Yanıt dili\" verilmişse o dilde, yoksa kullanıcının yazdığı dilde. Sade ve kısa yaz.\n- Adın Nova. Öğün tarayan, plan hazırlayan ve soruları yanıtlayan hep aynı Nova'sın; kendini başka bir asistan gibi tanıtma.\n\nGörev: Sen deneyimli bir diyetisyensin. Kullanıcı ne yediğini sesli ya da yazılı olarak anlatıyor.\n- Anlatılan her yiyecek veya içeceği ayrı kalem yap (en fazla 10). Adlar yanıt dilinde olsun.\n- \"Bir kase\", \"iki dilim\", \"bir avuç\" gibi ölçüleri gerçekçi grama çevir. Ölçü söylenmediyse ortalama bir porsiyon varsay.\n- Protein, karbonhidrat ve yağ değerlerini 100 gram için ver; biliyorsan lif, şeker ve tuzu da 100 gram için ver.\n- confidence: 0 ile 1 arası, ne kadar emin olduğun.\n- Anlatımda yiyecek yoksa is_food=false yap ve items'ı boş bırak.\n- assumptions alanında gram varsayımlarını kısaca açıkla.", "sicaklik": 0.2, "gorsel_gerekli": false, "sema": {"$defs": {"FoodItem": {"properties": {"name": {"title": "Name", "type": "string"}, "grams": {"title": "Grams", "type": "number"}, "protein_per_100g": {"title": "Protein Per 100G", "type": "number"}, "carbs_per_100g": {"title": "Carbs Per 100G", "type": "number"}, "fat_per_100g": {"title": "Fat Per 100G", "type": "number"}, "confidence": {"title": "Confidence", "type": "number"}, "fiber_per_100g": {"anyOf": [{"type": "number"}, {"type": "null"}], "default": null, "title": "Fiber Per 100G"}, "sugar_per_100g": {"anyOf": [{"type": "number"}, {"type": "null"}], "default": null, "title": "Sugar Per 100G"}, "salt_per_100g": {"anyOf": [{"type": "number"}, {"type": "null"}], "default": null, "title": "Salt Per 100G"}}, "required": ["name", "grams", "protein_per_100g", "carbs_per_100g", "fat_per_100g", "confidence"], "title": "FoodItem", "type": "object"}}, "properties": {"is_food": {"title": "Is Food", "type": "boolean"}, "items": {"items": {"$ref": "#/$defs/FoodItem"}, "title": "Items", "type": "array"}, "assumptions": {"title": "Assumptions", "type": "string"}}, "required": ["is_food", "items", "assumptions"], "title": "MealAnalysis", "type": "object"}}}};

// ---- index.ts
// yapay-zeka/index.ts - Supabase sunucu fonksiyonu (Edge Function)
//
// Telefon uygulaması Gemini'yi doğrudan çağırmaz; bu fonksiyonu çağırır.
// Gemini anahtarı yalnızca burada, Supabase'in gizli değişkenlerinde durur:
//   Supabase > Edge Functions > Secrets > GEMINI_API_KEY
//
// İstek:  POST, başlıkta "Authorization: Bearer <kullanıcının giriş belirteci>"
//         gövde: { mod, metin?, baglam?, gorsel_b64?, gorsel_tur?, ses_b64?, ses_tur? }
// Yanıt:  { sonuc, kalan, model }  ya da  { hata, mesaj }


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
