// rapor.ts - Diyetisyen raporu (sitedeki paylasim.py rapor_verisi ile aynı biçim)
// Aynı biçim önemli: bağlantı sitedeki ?rapor= sayfasında açılıyor ve o sayfa bu alanları okuyor.
import { bugunMetni, yas, type Veri } from "./hesap";

export function gunListesi(sayi: number, bitis = new Date()): string[] {
  const l: string[] = [];
  for (let i = sayi - 1; i >= 0; i--) { const d = new Date(bitis); d.setDate(d.getDate() - i); l.push(bugunMetni(d)); }
  return l;
}

export function raporVerisi(v: Veri, gunSayisi: number, hedefKalori: number) {
  const p = v.profil;
  const gunler = gunListesi(gunSayisi);
  const kume = new Set(gunler);
  const kayitlar = v.gunluk_kayitlar.filter((k) => kume.has(k.Tarih));
  const sayi = (x: unknown) => Number(x) || 0;

  const gunluk: Record<string, any> = {};
  for (const g of gunler) {
    const gk = kayitlar.filter((k) => k.Tarih === g);
    const a: any = v.aktivite_loglari?.[g] ?? {};
    gunluk[g] = {
      kalori: gk.reduce((s, k) => s + sayi(k.Kalori), 0),
      protein: gk.reduce((s, k) => s + sayi(k.Protein), 0),
      karbonhidrat: gk.reduce((s, k) => s + sayi(k.Karbonhidrat), 0),
      yag: gk.reduce((s, k) => s + sayi(k.Yağ), 0),
      adim: Math.round(sayi(a.adim)), su: sayi(a.su), egzersiz_kalori: sayi(a.egzersiz_kalori),
      ogunler: gk.map((k) => ({ ogun: k.Öğün, ad: k.Tarif, kalori: Math.round(sayi(k.Kalori)) })),
    };
  }
  const kayitliGunler = gunler.filter((g) => gunluk[g].ogunler.length);
  const bolen = Math.max(kayitliGunler.length, 1);
  const ort = (a: string, l: string[], b: number) => l.reduce((s, g) => s + gunluk[g][a], 0) / b;
  const kilolar = [...((p.kilo_gecmisi as any[]) ?? [])].filter((x) => kume.has(x.tarih)).sort((a, b) => a.tarih.localeCompare(b.tarih));

  return {
    ad: String(p.ad ?? "").trim(), olusturma: bugunMetni(), gun_sayisi: gunSayisi, hedef_kalori: Math.round(hedefKalori),
    boy: p.boy, yas: yas(p), cinsiyet: p.cinsiyet, aktivite: p.aktivite, amaclar: p.amaclar ?? [],
    mevcut_kilo: p.mevcut_kilo, hedef_kilo: p.hedef_kilo, gunler, gunluk, kilo_gecmisi: kilolar,
    kayitli_gun: kayitliGunler.length,
    ortalama: {
      kalori: ort("kalori", kayitliGunler, bolen), protein: ort("protein", kayitliGunler, bolen),
      karbonhidrat: ort("karbonhidrat", kayitliGunler, bolen), yag: ort("yag", kayitliGunler, bolen),
      adim: ort("adim", gunler, Math.max(gunler.length, 1)), su: ort("su", gunler, Math.max(gunler.length, 1)),
    },
  };
}

const kac = (s: unknown) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]!));

/** PDF'e dönüşecek sade rapor sayfası. Etiketler kullanıcının dilinde (t ile verilir). */
export function raporHtml(r: ReturnType<typeof raporVerisi>, t: (s: string) => string, dil: string): string {
  const tarih = (g: string) => new Intl.DateTimeFormat(dil, { day: "numeric", month: "short" }).format(new Date(g + "T12:00:00"));
  const satirlar = r.gunler.slice().reverse().map((g) => {
    const x = r.gunluk[g];
    if (!x.ogunler.length && !x.adim && !x.su) return "";
    return `<tr><td>${tarih(g)}</td><td>${Math.round(x.kalori)}</td><td>${Math.round(x.protein)}</td><td>${Math.round(x.karbonhidrat)}</td><td>${Math.round(x.yag)}</td><td>${x.adim || ""}</td><td>${x.su ? x.su.toFixed(2) : ""}</td></tr>
      ${x.ogunler.length ? `<tr class="ogun"><td></td><td colspan="6">${x.ogunler.map((o: any) => `${kac(t(o.ogun))}: ${kac(o.ad)} (${o.kalori})`).join(" · ")}</td></tr>` : ""}`;
  }).join("");
  const kilo = r.kilo_gecmisi.map((k: any) => `${tarih(k.tarih)}: ${Number(k.kilo).toFixed(1)} kg`).join(" · ");
  return `<!doctype html><html lang="${dil}" dir="${dil === "ar" ? "rtl" : "ltr"}"><head><meta charset="utf-8"><style>
    body{font-family:-apple-system,Helvetica,Arial,sans-serif;color:#1d1f23;margin:28px;font-size:12px}
    h1{font-size:22px;margin:0 0 4px} .alt{color:#6b7078;margin-bottom:18px}
    .kutular{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px}
    .kutu{border:1px solid #dfe2e6;border-radius:8px;padding:8px 12px;min-width:110px}
    .kutu b{display:block;font-size:16px} table{width:100%;border-collapse:collapse}
    th,td{text-align:start;padding:5px 6px;border-bottom:1px solid #eceef1} th{color:#6b7078;font-weight:600}
    tr.ogun td{color:#6b7078;font-size:10.5px;padding-top:0} .not{color:#6b7078;margin-top:18px;font-size:10px}
  </style></head><body>
    <h1>${kac(r.ad)} · Nova</h1>
    <div class="alt">${kac(t(`Son ${r.gun_sayisi} gün`))} · ${r.olusturma} · ${t("Kayıt girilen gün")}: ${r.kayitli_gun}/${r.gun_sayisi}</div>
    <div class="kutular">
      <div class="kutu">${t("Günlük hedefin")}<b>${r.hedef_kalori} kcal</b></div>
      <div class="kutu">${t("Ortalama")}<b>${Math.round(r.ortalama.kalori)} kcal</b></div>
      <div class="kutu">${t("Protein")}<b>${Math.round(r.ortalama.protein)} g</b></div>
      <div class="kutu">${t("Karbonhidrat")}<b>${Math.round(r.ortalama.karbonhidrat)} g</b></div>
      <div class="kutu">${t("Yağ")}<b>${Math.round(r.ortalama.yag)} g</b></div>
      <div class="kutu">${t("Kilo")}<b>${r.mevcut_kilo ?? "-"} → ${r.hedef_kilo ?? "-"} kg</b></div>
    </div>
    ${kilo ? `<p><b>${t("Kilo geçmişi")}:</b> ${kilo}</p>` : ""}
    <table><thead><tr><th></th><th>kcal</th><th>${t("Protein")} (g)</th><th>${t("Karbonhidrat")} (g)</th><th>${t("Yağ")} (g)</th><th>${t("Adım")}</th><th>${t("Su")} (L)</th></tr></thead>
    <tbody>${satirlar}</tbody></table>
    <div class="not">${t("Nova bir sağlık uygulaması değildir ve tıbbi tavsiye vermez. Hesaplamalar genel formüllere dayanan tahminlerdir.")}</div>
  </body></html>`;
}
