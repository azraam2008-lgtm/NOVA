// EklePaneli.tsx - Tek "Ekle" düğmesinin açtığı panel
// Bütün ekleme yolları burada: Ara, Barkod, Fotoğraf, Yazarak anlat, Kayıtlılarım, Tarif.
// Favoriler ve tarifler sitedeki kullanici_yemekleri tablosunda; iki tarafta aynı görünür.
import React, { useEffect, useMemo, useRef, useState } from "react";
import { ActivityIndicator, Image, Modal, Platform, Pressable, ScrollView, StyleSheet, View } from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { aktifDil, t } from "../dil";
import { kayitYap, kcal, ogunler, type Kayit, type Profil } from "../hesap";
import { sadelestir, yemekAra } from "../yemekler";
import { arka, type SiteYemek, type YemekTuru } from "../veri";
import { barkodAra, etikettenSite, fotografAl, siteYemegi, yereldenSite } from "../disari";
import { Cip, Dugme, Girdi, Hata, R, Yazi, hataMetni, temali } from "../bilesenler";

type Kip = "menu" | "ara" | "barkod" | "fotograf" | "anlat" | "kayitli" | "tarif";
type Tahmin = { ad: string; gram: string; p: number; k: number; y: number; ekstra?: Record<string, number> };

export function varsayilanOgun(p: Profil, saat = new Date().getHours()): string {
  const l = ogunler(p);
  if (p.oruc_modu) return saat < 12 ? l[0] : saat < 22 ? l[1] : l[2];
  return saat < 11 ? l[0] : saat < 16 ? l[1] : saat < 21 ? l[2] : l[3];
}

const sayiOku = (m: string) => Number(String(m).replace(",", ".")) || 0;

function OgunSecici(p: { profil: Profil; ogun: string; sec: (o: string) => void }) {
  return (
    <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 6 }}>
      {ogunler(p.profil).map((o) => <Cip key={o} yazi={t(o)} secili={p.ogun === o} bas={() => p.sec(o)} />)}
    </View>
  );
}

function YemekSatiri(p: { y: SiteYemek; bas: () => void; sag?: React.ReactNode; testID?: string }) {
  const g = p.y.gram || 100;
  return (
    <Pressable testID={p.testID} style={s.sonuc} onPress={p.bas} accessibilityRole="button">
      <View style={{ flex: 1 }}>
        <Yazi s={{ fontWeight: "600" }}>{p.y.ad}{p.y.marka ? ` · ${p.y.marka}` : ""}</Yazi>
        <Yazi tur="soluk">{g} g · {Math.round(kcal(p.y.p, p.y.k, p.y.y) * g / 100)} kcal</Yazi>
      </View>
      {p.sag}
    </Pressable>
  );
}

export function EklePaneli(p: {
  acik: boolean; kapat: () => void; profil: Profil; tarih: string; baglam: string; kullanici: string;
  ekle: (kayitlar: Kayit[]) => Promise<void>;
}) {
  const ic = useSafeAreaInsets();
  const [kip, setKip] = useState<Kip>("menu");
  const [ogun, setOgun] = useState(varsayilanOgun(p.profil));
  const [sorgu, setSorgu] = useState("");
  const [secilen, setSecilen] = useState<SiteYemek | null>(null);
  const [gram, setGram] = useState("100");
  const [anlatim, setAnlatim] = useState("");
  const [tahmin, setTahmin] = useState<Tahmin[] | null>(null);
  const [varsayim, setVarsayim] = useState("");
  const [foto, setFoto] = useState<string | null>(null);
  const [bekle, setBekle] = useState(false);
  const [hata, setHata] = useState<string | null>(null);
  const [kayitli, setKayitli] = useState<Record<YemekTuru, SiteYemek[]>>({ favori: [], kendi: [] });
  const [kayitliTur, setKayitliTur] = useState<YemekTuru>("favori");
  const [barkodMetni, setBarkodMetni] = useState("");
  const [barkodYok, setBarkodYok] = useState(false);
  const okundu = useRef(false);
  const [kameraIzni, kameraIzniIste] = useCameraPermissions();

  const yukle = async () => {
    try {
      const [favori, kendi] = await Promise.all([arka.yemekler(p.kullanici, "favori"), arka.yemekler(p.kullanici, "kendi")]);
      setKayitli({ favori, kendi });
    } catch { /* bağlantı yoksa liste boş kalır */ }
  };
  useEffect(() => { if (p.acik) { yukle(); setOgun(varsayilanOgun(p.profil)); } }, [p.acik]);

  const sifirla = () => {
    setKip("menu"); setSorgu(""); setSecilen(null); setAnlatim(""); setTahmin(null); setVarsayim(""); setFoto(null);
    setHata(null); setBarkodMetni(""); setBarkodYok(false); okundu.current = false;
  };
  const kapat = () => { sifirla(); p.kapat(); };
  const sec = (y: SiteYemek) => { setSecilen(y); setGram(String(y.gram || 100)); setHata(null); };

  const ekleVeKapat = async (k: Kayit[]) => {
    setBekle(true); setHata(null);
    try { await p.ekle(k); kapat(); } catch { setHata(t("Bir sorun çıktı. Biraz sonra tekrar dene.")); }
    setBekle(false);
  };

  // ------------------------------------------------------------- arama
  const kayitliEslesen = (sorgu: string) => {
    const q = sadelestir(sorgu);
    if (q.length < 2) return [];
    const hepsi = [...kayitli.kendi, ...kayitli.favori];
    const gorulen = new Set<string>();
    return hepsi.filter((y) => sadelestir(y.ad).includes(q) && !gorulen.has(y.ad) && gorulen.add(y.ad));
  };
  const sonuclar = useMemo(() => (kip === "ara" ? [...kayitliEslesen(sorgu), ...yemekAra(sorgu).map(yereldenSite)] : []),
    [kip, sorgu, kayitli]);

  // ------------------------------------------------------------- favori
  const favoriMi = (ad: string) => kayitli.favori.some((x) => x.ad === ad);
  const favoriDegistir = async (y: SiteYemek) => {
    const ok = favoriMi(y.ad) ? await arka.yemekSil(p.kullanici, "favori", y.ad) : await arka.yemekKaydet(p.kullanici, "favori", y);
    if (ok) yukle(); else setHata(t("Bir sorun çıktı. Biraz sonra tekrar dene."));
  };

  // ------------------------------------------------------------- barkod
  const barkodla = async (kod: string) => {
    if (okundu.current || bekle) return;
    okundu.current = true; setBekle(true); setHata(null); setBarkodYok(false);
    const r = await barkodAra(kod, aktifDil());
    setBekle(false);
    if (r === "yok") { setBarkodYok(true); okundu.current = false; return; }
    if (r === "baglanti") { setHata(t("Ürün bilgisine şu an ulaşılamadı. Biraz sonra tekrar dene.")); okundu.current = false; return; }
    sec(r);
  };

  // ------------------------------------------------------------- yapay zeka
  const tahminiGoster = (deger: any) => {
    if (!deger?.is_food || !(deger.items ?? []).length) return setHata(t("Bu bir yiyecek gibi görünmüyor."));
    setVarsayim(String(deger.assumptions ?? ""));
    setTahmin(deger.items.map((it: any) => ({
      ad: String(it.name), gram: String(Math.round(Number(it.grams) || 100)),
      p: Number(it.protein_per_100g) || 0, k: Number(it.carbs_per_100g) || 0, y: Number(it.fat_per_100g) || 0,
      ekstra: Object.fromEntries(([["Lif (g)", it.fiber_per_100g], ["Şeker (g)", it.sugar_per_100g], ["Tuz (g)", it.salt_per_100g]] as [string, any][])
        .filter(([, d]) => d != null && Number.isFinite(Number(d))).map(([a, d]) => [a, Number(d)])),
    })));
  };
  const anlat = async () => {
    setBekle(true); setHata(null); setTahmin(null);
    const r = await arka.yapayZeka("voice", anlatim, p.baglam);
    setBekle(false);
    if (!r.tamam) return setHata(hataMetni(r.hata));
    tahminiGoster(r.deger);
  };
  const fotografla = async (kaynak: "kamera" | "galeri", mod: "meal" | "label") => {
    setHata(null); setTahmin(null);
    let f;
    try { f = await fotografAl(kaynak); } catch { f = null; }
    if (f === "izin") return setHata(t("Kamera ya da fotoğraf izni verilmedi. iPhone Ayarlar > Expo Go bölümünden açabilirsin."));
    if (!f) return;
    setFoto(f.uri); setBekle(true);
    const r = await arka.yapayZeka(mod, "", p.baglam, { gorsel_b64: f.b64, gorsel_tur: "image/jpeg" });
    setBekle(false);
    if (!r.tamam) return setHata(hataMetni(r.hata));
    if (mod === "meal") return tahminiGoster(r.deger);
    const y = etikettenSite(r.deger);
    if (!y) return setHata(t("Etiketteki besin değerleri okunamadı. Daha yakından ve net çekmeyi dene."));
    setBarkodYok(false);
    sec(y);
  };

  const MENU: { kip: Kip; yazi: string; alt: string }[] = [
    { kip: "ara", yazi: "Ara", alt: "Yemek veritabanında" },
    { kip: "barkod", yazi: "Barkod", alt: "Paketli ürünler" },
    { kip: "fotograf", yazi: "Fotoğraf", alt: "Tabağını çek, Nova hesaplasın" },
    { kip: "anlat", yazi: "Yazarak anlat", alt: "Ne yediğini yaz" },
    { kip: "kayitli", yazi: "Kayıtlılarım", alt: "Favoriler ve tariflerin" },
    { kip: "tarif", yazi: "Tarif", alt: "Malzemelerden kur" },
  ];
  const BASLIK: Record<Kip, string> = {
    menu: "Ne eklemek istersin?", ara: "Yemek ara", barkod: "Barkod", fotograf: "Fotoğraf",
    anlat: "Ne yediğini anlat", kayitli: "Kayıtlılarım", tarif: "Tarif",
  };
  const geri = () => {
    if (secilen) { setSecilen(null); okundu.current = false; return; }
    if (kip === "menu") return kapat();
    sifirla();
  };

  // ------------------------------------------------------------- ortak görünümler
  const ayrinti = secilen && (() => {
    const g = sayiOku(gram);
    const k = kayitYap(secilen.ad, g, p.tarih, ogun, secilen.p, secilen.k, secilen.y, secilen.ekstra);
    const fav = favoriMi(secilen.ad);
    return (
      <View testID="secilen-yemek">
        <View style={{ flexDirection: "row", alignItems: "flex-start", gap: 8 }}>
          <Yazi tur="baslik" s={{ fontSize: 20, flex: 1 }}>{secilen.ad}</Yazi>
          <Dugme testID="favori" tur="ikincil" yazi={fav ? `★ ${t("Favori")}` : `☆ ${t("Favorilere ekle")}`}
            bas={() => favoriDegistir(secilen)} s={{ minHeight: 36, paddingHorizontal: 12 }} />
        </View>
        <Yazi tur="soluk" s={{ marginBottom: 12 }}>{[secilen.marka, secilen.kaynak].filter(Boolean).join(" · ")}</Yazi>
        <Girdi testID="gram-girdi" etiket={t("gram")} value={gram} onChangeText={setGram} keyboardType="decimal-pad" />
        <Yazi s={{ marginBottom: 12 }}>{k.Kalori} kcal · {t("Protein")} {k.Protein} g · {t("Karbonhidrat")} {k.Karbonhidrat} g · {t("Yağ")} {k.Yağ} g</Yazi>
        <Yazi tur="alt" s={{ marginBottom: 8 }}>{t("Hangi öğün?")}</Yazi>
        <OgunSecici profil={p.profil} ogun={ogun} sec={setOgun} />
        <Hata metin={hata} />
        <Dugme testID="yemek-ekle" yazi={t("Ekle")} bas={() => ekleVeKapat([k])} kapali={g <= 0} yukleniyor={bekle} s={{ marginTop: 8 }} />
      </View>
    );
  })();

  const tahminGorunumu = tahmin && (() => {
    const kayitlar = tahmin.map((it) => kayitYap(it.ad, sayiOku(it.gram), p.tarih, ogun, it.p, it.k, it.y, it.ekstra));
    const top = kayitlar.reduce((a, k) => a + k.Kalori, 0);
    return (
      <View testID="tahmin">
        <Yazi tur="alt" s={{ marginVertical: 8 }}>{t("Tahmin")}: {top} kcal</Yazi>
        {tahmin.map((it, i) => (
          <View key={i} style={s.tahminSatiri}>
            <View style={{ flex: 1 }}>
              <Yazi s={{ fontWeight: "600" }}>{it.ad}</Yazi>
              <Yazi tur="soluk">{kayitlar[i].Kalori} kcal</Yazi>
            </View>
            <View style={{ width: 92 }}>
              <Girdi testID={`tahmin-gram-${i}`} value={it.gram} keyboardType="decimal-pad" accessibilityLabel={`${it.ad} ${t("gram")}`}
                onChangeText={(m) => setTahmin(tahmin.map((x, j) => (j === i ? { ...x, gram: m } : x)))} />
            </View>
            <Pressable onPress={() => setTahmin(tahmin.filter((_, j) => j !== i))} hitSlop={10} accessibilityRole="button" accessibilityLabel={`${t("Sil")}: ${it.ad}`}>
              <Yazi s={{ color: R.soluk, fontSize: 20, marginLeft: 8 }}>×</Yazi>
            </Pressable>
          </View>
        ))}
        {varsayim ? <Yazi tur="soluk" s={{ marginBottom: 8 }}>{varsayim}</Yazi> : null}
        <Yazi tur="soluk" s={{ marginBottom: 8 }}>{t("Gramları düzeltebilirsin; yanlış kalemi × ile çıkar.")}</Yazi>
        <Yazi tur="alt" s={{ marginVertical: 8 }}>{t("Hangi öğün?")}</Yazi>
        <OgunSecici profil={p.profil} ogun={ogun} sec={setOgun} />
        <Dugme testID="tahmin-ekle" yazi={t("Bunları ekle")} bas={() => ekleVeKapat(kayitlar.filter((k) => k.Kalori >= 0))}
          kapali={!kayitlar.length} yukleniyor={bekle} s={{ marginTop: 8 }} />
      </View>
    );
  })();

  const yukleniyor = bekle && !tahmin && (
    <View style={{ flexDirection: "row", gap: 8, marginVertical: 10, alignItems: "center" }}>
      <ActivityIndicator color={R.murekkep} /><Yazi tur="soluk">{t("Nova hesaplıyor...")}</Yazi>
    </View>
  );

  let govde: React.ReactNode = null;
  if (secilen) govde = ayrinti;
  else if (kip === "menu") govde = (
    <View style={s.izgara}>
      {MENU.map((m) => (
        <Pressable key={m.kip} testID={`ekle-${m.kip}`} onPress={() => setKip(m.kip)} accessibilityRole="button"
          style={({ pressed }) => [s.kutu, pressed && { opacity: 0.8 }]}>
          <Yazi s={{ fontSize: 16, fontWeight: "700" }}>{t(m.yazi)}</Yazi>
          <Yazi tur="soluk">{t(m.alt)}</Yazi>
        </Pressable>
      ))}
    </View>
  );
  else if (kip === "ara") govde = <>
    <Girdi testID="arama-girdi" value={sorgu} onChangeText={setSorgu} placeholder={t("Yemek ara")} autoFocus autoCorrect={false} />
    {sorgu.trim().length >= 2 && sonuclar.length === 0 && <Yazi tur="soluk">{t("Bulamadım. \"Yazarak anlat\" seçeneğini dene.")}</Yazi>}
    {sonuclar.map((y, i) => <YemekSatiri key={`${y.ad}-${i}`} testID={`sonuc-${i}`} y={y} bas={() => sec(y)}
      sag={favoriMi(y.ad) ? <Yazi s={{ color: R.karb }}>★</Yazi> : undefined} />)}
  </>;
  else if (kip === "barkod") govde = <>
    {Platform.OS !== "web" && (kameraIzni?.granted ? (
      <View style={s.kamera}>
        <CameraView style={{ flex: 1 }} facing="back"
          barcodeScannerSettings={{ barcodeTypes: ["ean13", "ean8", "upc_a", "upc_e"] }}
          onBarcodeScanned={bekle || barkodYok ? undefined : (r) => barkodla(r.data)} />
        <View pointerEvents="none" style={s.nisan} />
      </View>
    ) : (
      <Dugme testID="kamera-izni" yazi={t("Kamerayı aç")} bas={() => kameraIzniIste()} s={{ marginBottom: 12 }} />
    ))}
    <Yazi tur="soluk" s={{ marginVertical: 8 }}>{t("Kamerayı ürünün barkoduna tut. Okumazsa numarayı elle yaz.")}</Yazi>
    <View style={{ flexDirection: "row", gap: 8, alignItems: "flex-start" }}>
      <View style={{ flex: 1 }}>
        <Girdi testID="barkod-girdi" value={barkodMetni} onChangeText={setBarkodMetni} keyboardType="number-pad" placeholder="8690000000000" />
      </View>
      <Dugme testID="barkod-ara" yazi={t("Ara")} bas={() => { okundu.current = false; barkodla(barkodMetni); }}
        kapali={barkodMetni.replace(/\D/g, "").length < 8} yukleniyor={bekle} />
    </View>
    {barkodYok && (
      <View testID="barkod-yok">
        <Yazi s={{ marginVertical: 8 }}>{t("Bu ürün açık veritabanında yok ya da besin değerleri eksik. Arka yüzdeki besin değerleri tablosunun fotoğrafını çekersen Nova okusun.")}</Yazi>
        <Dugme testID="etiket-cek" yazi={t("Etiketi fotoğrafla")} bas={() => fotografla("kamera", "label")} yukleniyor={bekle} />
      </View>
    )}
    <Hata metin={hata} />
  </>;
  else if (kip === "fotograf") govde = <>
    {!tahmin && (
      <View style={{ flexDirection: "row", gap: 8 }}>
        <Dugme testID="foto-cek" yazi={t("Fotoğraf çek")} bas={() => fotografla("kamera", "meal")} s={{ flex: 1 }} kapali={bekle} />
        <Dugme testID="foto-sec" tur="ikincil" yazi={t("Galeriden seç")} bas={() => fotografla("galeri", "meal")} s={{ flex: 1 }} kapali={bekle} />
      </View>
    )}
    {foto && <Image source={{ uri: foto }} style={s.foto} resizeMode="cover" />}
    {!foto && <Yazi tur="soluk" s={{ marginTop: 10 }}>{t("Tabağın tamamı görünsün; yanında çatal ya da bardak varsa Nova porsiyonu daha iyi tahmin eder.")}</Yazi>}
    {yukleniyor}
    <Hata metin={hata} />
    {tahminGorunumu}
  </>;
  else if (kip === "anlat") govde = <>
    <Girdi testID="anlat-girdi" value={anlatim} onChangeText={setAnlatim} multiline maxLength={600}
      placeholder={t("Örnek: 2 yumurta, 1 dilim peynir ve bir bardak çay")} style={{ minHeight: 90, paddingTop: 12, textAlignVertical: "top" }} />
    {!tahmin && <Dugme testID="anlat-hesapla" yazi={t("Hesapla")} bas={anlat} yukleniyor={bekle} kapali={anlatim.trim().length < 3} />}
    {yukleniyor}
    <Hata metin={hata} />
    {tahminGorunumu}
  </>;
  else if (kip === "kayitli") govde = <>
    <View style={{ flexDirection: "row", gap: 8, marginBottom: 12 }}>
      <Cip testID="kayitli-favori" yazi={`${t("Favoriler")} (${kayitli.favori.length})`} secili={kayitliTur === "favori"} bas={() => setKayitliTur("favori")} />
      <Cip testID="kayitli-kendi" yazi={`${t("Tariflerim")} (${kayitli.kendi.length})`} secili={kayitliTur === "kendi"} bas={() => setKayitliTur("kendi")} />
    </View>
    {kayitli[kayitliTur].length === 0 && <Yazi tur="soluk">{t(kayitliTur === "favori"
      ? "Henüz favorin yok. Bir yemeği seçince yıldıza dokunarak favorilere ekleyebilirsin."
      : "Henüz kayıtlı tarifin yok. Tarif bölümünden kurabilirsin.")}</Yazi>}
    {kayitli[kayitliTur].map((y, i) => (
      <YemekSatiri key={y.ad} testID={`kayitli-${i}`} y={y} bas={() => sec(y)} sag={
        <Pressable onPress={async () => { await arka.yemekSil(p.kullanici, kayitliTur, y.ad); yukle(); }} hitSlop={10}
          accessibilityRole="button" accessibilityLabel={`${t("Sil")}: ${y.ad}`}>
          <Yazi s={{ color: R.soluk, fontSize: 20, marginLeft: 8 }}>×</Yazi>
        </Pressable>} />
    ))}
  </>;
  else if (kip === "tarif") govde = (
    <TarifKurucu kayitli={kayitli.kendi} profil={p.profil} tarih={p.tarih} ogun={ogun} setOgun={setOgun}
      bugune={ekleVeKapat} kaydet={async (y) => { const ok = await arka.yemekKaydet(p.kullanici, "kendi", y); if (ok) await yukle(); return ok; }} />
  );

  return (
    <Modal visible={p.acik} transparent animationType="slide" onRequestClose={kapat}>
      <Pressable style={s.perde} onPress={kapat} accessibilityLabel={t("Kapat")} />
      <View style={[s.panel, { paddingBottom: ic.bottom + 16 }]} testID="ekle-paneli">
        <View style={s.tutamac} />
        <View style={s.ust}>
          <Yazi tur="baslik" s={{ fontSize: 20, flex: 1 }}>{t(BASLIK[kip])}</Yazi>
          <Dugme tur="yalin" testID="panel-geri" yazi={kip === "menu" && !secilen ? t("Kapat") : t("Geri")} bas={geri} s={{ minHeight: 36 }} />
        </View>
        <ScrollView keyboardShouldPersistTaps="handled" style={{ maxHeight: 560 }}>{govde}</ScrollView>
      </View>
    </Modal>
  );
}

// ------------------------------------------------------------------ tarif
// Sitedeki tarif.py ile aynı hesap: toplam = malzemelerin toplamı, porsiyon = toplam / porsiyon sayısı.
type Malzeme = { y: SiteYemek; gram: string };

function TarifKurucu(p: {
  kayitli: SiteYemek[]; profil: Profil; tarih: string; ogun: string; setOgun: (o: string) => void;
  bugune: (k: Kayit[]) => Promise<void>; kaydet: (y: SiteYemek) => Promise<boolean>;
}) {
  const [sorgu, setSorgu] = useState("");
  const [malzemeler, setMalzemeler] = useState<Malzeme[]>([]);
  const [porsiyon, setPorsiyon] = useState("1");
  const [ad, setAd] = useState("");
  const [mesaj, setMesaj] = useState<string | null>(null);
  const [hata, setHata] = useState<string | null>(null);

  const q = sadelestir(sorgu);
  const sonuc = q.length < 2 ? [] : [
    ...p.kayitli.filter((y) => sadelestir(y.ad).includes(q)),
    ...yemekAra(sorgu, 8).map(yereldenSite),
  ].slice(0, 8);

  let gram = 0, pr = 0, kb = 0, yg = 0;
  const ekstra: Record<string, number> = {};
  for (const m of malzemeler) {
    const g = sayiOku(m.gram), o = g / 100;
    gram += g; pr += m.y.p * o; kb += m.y.k * o; yg += m.y.y * o;
    for (const [a, d] of Object.entries(m.y.ekstra ?? {})) ekstra[a] = (ekstra[a] ?? 0) + d * o;
  }
  const n = Math.max(1, Math.round(sayiOku(porsiyon)) || 1);
  const porsiyonG = gram / n;
  // Porsiyon başı değer, içeride her şey gibi 100 grama çevrilir
  const yuz = porsiyonG > 0 ? 100 / porsiyonG : 0;
  const tarifYemegi = () => siteYemegi(ad.trim() || t("Tarif"), (pr / n) * yuz, (kb / n) * yuz, (yg / n) * yuz, {
    kaynak: t("Tarifin"), gram: porsiyonG, ekstra: Object.fromEntries(Object.entries(ekstra).map(([a, d]) => [a, (d / n) * yuz])),
  });
  const toplamKcal = Math.round(kcal(pr, kb, yg));

  return (
    <View testID="tarif">
      <Yazi tur="soluk" s={{ marginBottom: 10 }}>{t("Birden çok parçadan oluşan bir yemeği bir kez kur, kaydet; sonra tek dokunuşla ekle.")}</Yazi>
      <Girdi testID="tarif-ara" value={sorgu} onChangeText={setSorgu} placeholder={t("Malzeme ara")} autoCorrect={false} />
      {sonuc.map((y, i) => (
        <YemekSatiri key={`${y.ad}-${i}`} testID={`tarif-sonuc-${i}`} y={y}
          bas={() => { setMalzemeler([...malzemeler, { y, gram: String(y.gram || 100) }]); setSorgu(""); setMesaj(null); }}
          sag={<Yazi s={{ fontWeight: "700" }}>+</Yazi>} />
      ))}
      {malzemeler.length > 0 && (
        <View style={{ marginTop: 10 }}>
          <Yazi tur="alt" s={{ marginBottom: 6 }}>{t("Tarifin")}</Yazi>
          {malzemeler.map((m, i) => (
            <View key={i} style={s.tahminSatiri}>
              <Yazi s={{ flex: 1 }}>{m.y.ad}</Yazi>
              <View style={{ width: 92 }}>
                <Girdi testID={`malzeme-gram-${i}`} value={m.gram} keyboardType="decimal-pad"
                  onChangeText={(v) => setMalzemeler(malzemeler.map((x, j) => (j === i ? { ...x, gram: v } : x)))} />
              </View>
              <Pressable onPress={() => setMalzemeler(malzemeler.filter((_, j) => j !== i))} hitSlop={10} accessibilityRole="button" accessibilityLabel={`${t("Sil")}: ${m.y.ad}`}>
                <Yazi s={{ color: R.soluk, fontSize: 20, marginLeft: 8 }}>×</Yazi>
              </Pressable>
            </View>
          ))}
          <Yazi s={{ fontWeight: "700", marginVertical: 8 }} testID="tarif-toplam">
            {t("Toplam")}: {Math.round(gram)} g · {toplamKcal} kcal
          </Yazi>
          <View style={{ flexDirection: "row", gap: 10 }}>
            <View style={{ flex: 1 }}><Girdi testID="tarif-porsiyon" etiket={t("Kaç porsiyon?")} value={porsiyon} onChangeText={setPorsiyon} keyboardType="number-pad" /></View>
            <View style={{ flex: 2 }}><Girdi testID="tarif-ad" etiket={t("Tarifin adı")} value={ad} onChangeText={setAd} maxLength={60} /></View>
          </View>
          {n > 1 && <Yazi tur="soluk" s={{ marginBottom: 8 }}>{t("Bir porsiyon")}: {Math.round(porsiyonG)} g · {Math.round(toplamKcal / n)} kcal</Yazi>}
          <Yazi tur="alt" s={{ marginBottom: 8 }}>{t("Hangi öğün?")}</Yazi>
          <OgunSecici profil={p.profil} ogun={p.ogun} sec={p.setOgun} />
          <Hata metin={hata} />
          {mesaj && <Yazi s={{ color: R.iyi, marginBottom: 8 }}>{mesaj}</Yazi>}
          <View style={{ flexDirection: "row", gap: 8 }}>
            <Dugme testID="tarif-bugune" yazi={t("Bugüne ekle")} s={{ flex: 1 }} kapali={gram <= 0}
              bas={() => { const y = tarifYemegi(); p.bugune([kayitYap(y.ad, porsiyonG, p.tarih, p.ogun, y.p, y.k, y.y, y.ekstra)]); }} />
            <Dugme testID="tarif-kaydet" tur="ikincil" yazi={t("Tarifi kaydet")} s={{ flex: 1 }} kapali={gram <= 0}
              bas={async () => {
                setHata(null);
                if (!ad.trim()) return setHata(t("Tarifin adını yaz."));
                if (await p.kaydet(tarifYemegi())) { setMesaj(`${ad.trim()} ${t("kaydedildi. Artık aramada çıkacak.")}`); setMalzemeler([]); setAd(""); }
                else setHata(t("Bir sorun çıktı. Biraz sonra tekrar dene."));
              }} />
          </View>
        </View>
      )}
      {malzemeler.length === 0 && mesaj && <Yazi s={{ color: R.iyi, marginTop: 8 }}>{mesaj}</Yazi>}
    </View>
  );
}

const s = temali(() => StyleSheet.create({
  perde: { flex: 1, backgroundColor: "rgba(10,12,16,0.35)" },
  panel: { backgroundColor: R.panel, borderTopLeftRadius: 24, borderTopRightRadius: 24, paddingHorizontal: 20, paddingTop: 10 },
  tutamac: { alignSelf: "center", width: 40, height: 5, borderRadius: 3, backgroundColor: R.cizgi, marginBottom: 10 },
  ust: { flexDirection: "row", alignItems: "center", marginBottom: 12 },
  izgara: { flexDirection: "row", flexWrap: "wrap", gap: 10 },
  kutu: { width: "48%", minHeight: 84, backgroundColor: R.girdi, borderRadius: 16, padding: 14, justifyContent: "center", gap: 4, borderWidth: StyleSheet.hairlineWidth, borderColor: R.cizgi },
  sonuc: { flexDirection: "row", alignItems: "center", backgroundColor: R.girdi, borderRadius: 12, padding: 14, marginBottom: 8, borderWidth: StyleSheet.hairlineWidth, borderColor: R.cizgi },
  tahminSatiri: { flexDirection: "row", alignItems: "center", gap: 8 },
  kamera: { height: 240, borderRadius: 16, overflow: "hidden", backgroundColor: "#000", marginBottom: 4 },
  nisan: { position: "absolute", left: "12%", right: "12%", top: "38%", height: 70, borderWidth: 2, borderColor: "rgba(255,255,255,0.85)", borderRadius: 12 },
  foto: { width: "100%", height: 200, borderRadius: 16, marginTop: 12 },
}));
