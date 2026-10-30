"""
nutrition_check.py - Doğrulama katmanı (Streamlit'e bağımlı değil)

Modelin verdiği "100 gramdaki protein / karbonhidrat / yağ" değerlerini iki şekilde kontrol eder:

1) Akla yatkınlık: negatif değer olamaz, 100 g'da makroların toplamı 100 g'ı aşamaz.
   Aşıyorsa değerler düzeltilir (ya da referans varsa referans kullanılır).
2) Referans karşılaştırma: Yumurta, haşlanmış pirinç, elma gibi tek bileşenli besinlerde
   model değeri referanstan çok sapıyorsa uyarır, istenirse referansı kullanır.

ÖNEMLİ: REFERENCE tablosundaki sayılar USDA FoodData Central'daki genel değerlere yakın,
yuvarlanmış değerlerdir. Üretimde TürKomp veya USDA verisiyle genişletip kendin doğrula.
Karma yemeklerde (pilav, köfte, soslu, kızartma vb.) karşılaştırma yapılmaz; orada modele güvenilir.
"""

from dataclasses import dataclass, field
from difflib import get_close_matches
from typing import List, Optional, Tuple

Macros = Tuple[float, float, float]  # (protein, karbonhidrat, yağ) - 100 g başına

# (kabul edilen adlar), (protein, karbonhidrat, yağ)
REFERENCE = [
    (("tavuk göğsü", "haşlanmış tavuk göğsü", "ızgara tavuk göğsü"), (31.0, 0.0, 3.6)),
    (("yumurta", "haşlanmış yumurta"), (12.6, 1.1, 10.6)),
    (("haşlanmış pirinç", "sade pirinç", "pişmiş pirinç"), (2.7, 28.2, 0.3)),
    (("haşlanmış makarna", "sade makarna", "pişmiş makarna"), (5.8, 30.9, 0.9)),
    (("beyaz ekmek", "ekmek"), (9.4, 49.2, 3.6)),
    (("haşlanmış patates", "patates haşlama"), (1.7, 20.1, 0.1)),
    (("zeytinyağı",), (0.0, 0.0, 100.0)),
    (("tereyağı",), (0.9, 0.1, 81.1)),
    (("yoğurt", "tam yağlı yoğurt"), (3.5, 4.7, 3.3)),
    (("süt", "tam yağlı süt"), (3.2, 4.8, 3.3)),
    (("domates",), (0.9, 3.9, 0.2)),
    (("salatalık",), (0.7, 3.6, 0.1)),
    (("elma",), (0.3, 13.8, 0.2)),
    (("muz",), (1.1, 22.8, 0.3)),
    (("haşlanmış mercimek", "pişmiş mercimek"), (9.0, 20.1, 0.4)),
    (("haşlanmış nohut", "pişmiş nohut"), (8.9, 27.4, 2.6)),
    (("haşlanmış bulgur", "pişmiş bulgur"), (3.1, 18.6, 0.2)),
    (("ceviz",), (15.2, 13.7, 65.2)),
    (("badem",), (21.2, 21.6, 49.9)),
]

MAX_MACRO_SUM = 105.0      # 100 g'da makro toplamı (küçük yuvarlama payıyla)
MAX_KCAL_PER_100G = 930.0  # saf yağ 900 kcal
KCAL_TOLERANCE = 0.35      # referanstan %35'ten fazla sapma uyarı üretir
MIN_KCAL_GAP = 25.0        # küçük sayılarda (domates gibi) gürültüyü yok say

# Bu kelimeleri içeren adlar karma yemek sayılır, referansla karşılaştırılmaz
_COMPLEX_WORDS = (
    "kizart", "sos", "yagda", "kremali", "tereyagli", "salca", "kori", "firin",
    "kavur", "soteli", "graten", "borek", "corba", "pilav", "kofte", "dolma", "tatli",
)

_TR = str.maketrans("çğıöşüÇĞİÖŞÜâîû", "cgiosuCGIOSUaiu")


def _norm(text: str) -> str:
    """Küçük harfe çevir, Türkçe karakterleri sadeleştir, noktalamayı at."""
    text = text.replace("İ", "i").replace("I", "ı").lower().translate(_TR)
    text = "".join(ch if ch.isalnum() or ch == " " else " " for ch in text)
    return " ".join(text.split())


_INDEX = {_norm(name): (vals, name) for names, vals in REFERENCE for name in names}


def kcal(protein: float, carbs: float, fat: float) -> float:
    """Kaloriyi makrolardan hesapla (4/4/9)."""
    return 4 * protein + 4 * carbs + 9 * fat


def find_reference(name: str) -> Tuple[Optional[Macros], Optional[str]]:
    key = _norm(name)
    if not key or any(word in key for word in _COMPLEX_WORDS):
        return None, None
    hit = _INDEX.get(key)
    if hit is None:
        close = get_close_matches(key, list(_INDEX), n=1, cutoff=0.88)
        hit = _INDEX[close[0]] if close else None
    return (hit[0], hit[1]) if hit else (None, None)


@dataclass
class Check:
    values: Macros                       # kullanılması önerilen (protein, karb, yağ) / 100 g
    changed: bool = False                # model değerinden farklı mı
    messages: List[str] = field(default_factory=list)
    ref_name: Optional[str] = None


def _repair(p: float, c: float, f: float) -> Macros:
    """Negatifleri sıfırla, toplam 100 g'ı aşıyorsa orantılı küçült."""
    p, c, f = max(p, 0.0), max(c, 0.0), max(f, 0.0)
    total = p + c + f
    if total > 100.0:
        scale = 100.0 / total
        p, c, f = p * scale, c * scale, f * scale
    return round(p, 1), round(c, 1), round(f, 1)


def verify(name: str, protein: float, carbs: float, fat: float,
           prefer_reference: bool = True) -> Check:
    p, c, f = float(protein), float(carbs), float(fat)
    ref, ref_name = find_reference(name)

    problem = None
    if min(p, c, f) < 0:
        problem = "Negatif değer çıktı."
    elif p + c + f > MAX_MACRO_SUM:
        problem = "100 g'da makro toplamı 100 g'ı aşıyor."
    elif kcal(p, c, f) > MAX_KCAL_PER_100G:
        problem = "Kalori yoğunluğu mümkün olandan yüksek."

    if problem:
        if ref and prefer_reference:
            return Check(ref, True, [f"{problem} Referans değer kullanıldı ({ref_name})."], ref_name)
        return Check(_repair(p, c, f), True,
                     [f"{problem} Değerler düzeltildi, içeriği kontrol et."], None)

    if ref:
        model_kcal, ref_kcal = kcal(p, c, f), kcal(*ref)
        gap = abs(model_kcal - ref_kcal)
        if gap > MIN_KCAL_GAP and gap / max(ref_kcal, 1.0) > KCAL_TOLERANCE:
            if prefer_reference:
                return Check(ref, True,
                             [f"Model değeri referanstan çok farklıydı ({ref_name}), referans kullanıldı."],
                             ref_name)
            return Check((p, c, f), False,
                         [f"Model değeri referanstan çok farklı ({ref_name})."], ref_name)

    return Check((round(p, 1), round(c, 1), round(f, 1)), False, [], ref_name)
