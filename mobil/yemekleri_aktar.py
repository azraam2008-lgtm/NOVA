"""
yemekleri_aktar.py - Sitenin yemek veritabanını uygulamaya aktarır

Site ve uygulama aynı CSV'yi kullanır; tek doğru odur. CSV değişince:
    python mobil/yemekleri_aktar.py
Değerler 100 grama indirgenir (sitedeki _yerelden ile aynı kural).
"""
import csv, json, os

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(KOK, "cok_daha_kapsamli_yemek_veritabani.csv")
HEDEF = os.path.join(KOK, "mobil", "src", "veri", "yemekler.json")


def sayi(x):
    try:
        x = float(str(x).strip())
        return x if x == x else None   # NaN değilse
    except (TypeError, ValueError):
        return None


cikti = []
with open(CSV, encoding="utf-8") as f:
    for s in csv.DictReader(f):
        ref = sayi(s.get("Gramaj (g/ml)")) or 100.0
        if ref <= 0:
            ref = 100.0
        o = 100.0 / ref
        p, k, y = (sayi(s.get(a)) for a in ("Protein (g)", "Karbonhidrat (g)", "Yağ (g)"))
        if p is None or k is None or y is None:
            continue
        kayit = {
            "ad": s["Yemek Adı"].strip(),
            "en": (s.get("Yemek Adı (EN)") or "").strip(),
            "kat": (s.get("Kategori") or "").strip(),
            "por": (s.get("Porsiyon") or "").strip(),
            "g": round(ref),
            "p": round(p * o, 2), "k": round(k * o, 2), "y": round(y * o, 2),
            "kaynak": (s.get("Kaynak") or "").strip() or "Nova",
        }
        ek = {}
        for sutun in ("Lif (g)", "Şeker (g)", "Demir (mg)", "Kalsiyum (mg)", "Potasyum (mg)"):
            v = sayi(s.get(sutun))
            if v is not None:
                ek[sutun] = round(v * o, 3)
        na = sayi(s.get("Sodyum (mg)"))
        if na is not None:
            ek["Tuz (g)"] = round(na * 2.5 / 1000.0 * o, 3)
        if ek:
            kayit["ek"] = ek
        cikti.append(kayit)

with open(HEDEF, "w", encoding="utf-8") as f:
    json.dump(cikti, f, ensure_ascii=False, separators=(",", ":"))
print(f"{len(cikti)} yemek -> {HEDEF} ({os.path.getsize(HEDEF)//1024} KB)")
