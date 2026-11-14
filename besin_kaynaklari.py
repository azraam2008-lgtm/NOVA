"""
besin_kaynaklari.py - Nova'nın dış besin kaynakları

    Open Food Facts araması (marka ürünleri, milyonlarca kayıt)
    Barkod fotoğrafından numara okuma (OpenCV)
    Barkodla ürün bulma
    Bulunan ürünleri Supabase'deki "urun_onbellek" tablosunda saklama

Open Food Facts ücretsiz ve açık bir veritabanıdır; anahtar gerektirmez.
Arama servisi dakikada sınırlı sayıda istek kabul ettiği için sonuçlar hem sunucu belleğinde
hem de Supabase'de saklanır, aynı ürün için ikinci kez dışarıya gidilmez.
"""

import io
import re

import requests
import streamlit as st

KULLANICI_AJANI = "Nova/1.0 (Streamlit diyet ve aktivite uygulamasi)"
ARAMA_URL = "https://search.openfoodfacts.org/search"
ESKI_ARAMA_URL = "https://world.openfoodfacts.org/cgi/search.pl"  # yeni arama servisi cevap vermezse
URUN_URL = "https://world.openfoodfacts.org/api/v2/product/{kod}.json"
ALANLAR = "code,product_name,product_name_tr,brands,nutriments,serving_quantity,countries_tags"
ZAMAN_ASIMI = 10  # saniye


class KaynakHatasi(Exception):
    """Open Food Facts'e ulaşılamadı ya da cevap okunamadı."""


# ------------------------------------------------------------------ Yardımcılar
def _sayi(deger):
    try:
        x = float(deger)
        return x if x >= 0 else None
    except (TypeError, ValueError):
        return None


def _istek(url, params=None):
    """Tek noktadan HTTP isteği (testlerde bu fonksiyon sahtesiyle değiştirilir)."""
    try:
        cevap = requests.get(url, params=params, headers={"User-Agent": KULLANICI_AJANI}, timeout=ZAMAN_ASIMI)
    except requests.RequestException as e:
        raise KaynakHatasi(str(e)) from e
    if cevap.status_code == 404:
        return None
    if cevap.status_code != 200:
        raise KaynakHatasi(f"HTTP {cevap.status_code}")
    try:
        return cevap.json()
    except ValueError as e:
        raise KaynakHatasi("Cevap okunamadı") from e


def _marka(brands):
    if isinstance(brands, list):
        parcalar = brands
    else:
        parcalar = str(brands or "").split(",")
    gorulen, temiz = set(), []
    for p in parcalar:
        p = str(p).strip()
        if p and p.lower() not in gorulen:
            gorulen.add(p.lower())
            temiz.append(p)
    return ", ".join(temiz[:2])


def urun_satiri(p):
    """Open Food Facts ürününü Nova'nın sade biçimine çevirir. Makro değeri eksik ürünler için None döner."""
    n = p.get("nutriments") or {}
    protein, karb, yag = _sayi(n.get("proteins_100g")), _sayi(n.get("carbohydrates_100g")), _sayi(n.get("fat_100g"))
    ad = (p.get("product_name_tr") or p.get("product_name") or "").strip()
    if not ad or None in (protein, karb, yag) or protein + karb + yag > 100.5:
        return None
    kcal = _sayi(n.get("energy-kcal_100g"))
    if kcal is None:
        kcal = protein * 4 + karb * 4 + yag * 9
    tuz = _sayi(n.get("salt_100g"))
    if tuz is None and _sayi(n.get("sodium_100g")) is not None:
        tuz = _sayi(n.get("sodium_100g")) * 2.5
    porsiyon = _sayi(p.get("serving_quantity"))
    ulkeler = " ".join(p.get("countries_tags") or [])
    return {
        "kod": str(p.get("code") or ""),
        "ad": ad[:80],
        "marka": _marka(p.get("brands")),
        "protein": round(protein, 1), "karb": round(karb, 1), "yag": round(yag, 1), "kcal": round(kcal),
        "lif": _sayi(n.get("fiber_100g")), "seker": _sayi(n.get("sugars_100g")),
        "tuz": round(tuz, 2) if tuz is not None else None, "doymus_yag": _sayi(n.get("saturated-fat_100g")),
        "porsiyon": int(porsiyon) if porsiyon and 5 <= porsiyon <= 2000 else None,
        "turkiye": "turkey" in ulkeler or "turkiye" in ulkeler,
    }


# ------------------------------------------------------------------ Open Food Facts
def _ham_ara(sorgu):
    """Önce yeni arama servisi, cevap vermezse eski (cgi) servis denenir."""
    try:
        veri = _istek(ARAMA_URL, {"q": sorgu, "page_size": 40, "langs": "tr", "fields": ALANLAR}) or {}
        if veri.get("hits"):
            return veri["hits"]
    except KaynakHatasi:
        pass  # eski servise düşülür
    veri = _istek(ESKI_ARAMA_URL, {
        "search_terms": sorgu, "search_simple": 1, "action": "process",
        "json": 1, "page_size": 40, "fields": ALANLAR,
    }) or {}
    return veri.get("products", [])


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def _off_ara_onbellekli(sorgu):
    urunler = [u for u in (urun_satiri(p) for p in _ham_ara(sorgu)) if u]
    # Türkiye'de satılan ürünler önce gelsin (diğer ülkelerin ürünleri de listede kalır)
    urunler.sort(key=lambda u: not u["turkiye"])
    return urunler[:25]


def off_ara(sorgu):
    """Marka ürünlerinde arama. Bağlantı sorununda KaynakHatasi fırlatır (hatalar önbelleğe alınmaz)."""
    sorgu = (sorgu or "").strip()
    if len(sorgu) < 2:
        return []
    return _off_ara_onbellekli(sorgu.lower())


@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def _off_barkod_onbellekli(kod):
    veri = _istek(URUN_URL.format(kod=kod), {"fields": ALANLAR})
    if not veri or veri.get("status") != 1:
        return None
    urun = veri.get("product") or {}
    satir = urun_satiri(urun)
    if satir:
        return satir
    # Ürün kayıtlı ama besin değerleri eksik: en azından adını ve markasını döndür (etiketten eklerken hazır gelsin)
    ad = (urun.get("product_name_tr") or urun.get("product_name") or "").strip()
    return {"eksik": True, "kod": kod, "ad": ad[:80], "marka": _marka(urun.get("brands"))} if ad else None


def off_barkod(kod):
    """Barkodla ürün. Bulunamazsa None, besin değerleri eksikse {"eksik": True, "ad", "marka"} döner."""
    return _off_barkod_onbellekli(kod)


# ------------------------------------------------------------------ Barkod
def barkod_gecerli_mi(kod):
    """8-14 haneli sayı ve (EAN-8 / EAN-13 / UPC-A için) kontrol hanesi doğru mu."""
    if not re.fullmatch(r"\d{8,14}", kod or ""):
        return False
    if len(kod) in (8, 12, 13, 14):
        rakamlar = [int(c) for c in kod]
        govde, kontrol = rakamlar[:-1], rakamlar[-1]
        toplam = sum(r * (3 if i % 2 == 0 else 1) for i, r in enumerate(reversed(govde)))
        return (10 - toplam % 10) % 10 == kontrol
    return True


def barkod_oku(goruntu_bytes):
    """Fotoğraftaki barkod numaralarını döndürür. OpenCV kurulu değilse ImportError fırlatır."""
    import cv2
    import numpy as np
    from PIL import Image, ImageOps

    img = ImageOps.exif_transpose(Image.open(io.BytesIO(goruntu_bytes))).convert("RGB")
    img.thumbnail((1600, 1600))
    bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    okuyucu = cv2.barcode.BarcodeDetector()
    bulunan = []
    # Telefonla dik çekilen fotoğraflarda barkod yan durabilir; döndürerek de denenir
    for aci in (None, cv2.ROTATE_90_CLOCKWISE):
        resim = bgr if aci is None else cv2.rotate(bgr, aci)
        sonuc = okuyucu.detectAndDecodeWithType(resim) if hasattr(okuyucu, "detectAndDecodeWithType") else okuyucu.detectAndDecode(resim)
        bilgiler = sonuc[1] if isinstance(sonuc, tuple) and len(sonuc) > 1 else ()
        if isinstance(bilgiler, str):
            bilgiler = (bilgiler,)
        for kod in bilgiler or ():
            kod = (kod or "").strip()
            if barkod_gecerli_mi(kod) and kod not in bulunan:
                bulunan.append(kod)
        if bulunan:
            break
    return bulunan


# ------------------------------------------------------------------ Supabase önbelleği
def _temiz_sorgu(sorgu):
    # PostgREST filtre sözdizimini bozabilecek karakterleri çıkar
    return re.sub(r"[,()%*\\:\"']", " ", sorgu or "").strip()


def onbellekte_ara(db, sorgu, limit=15):
    """Daha önce bulunmuş ürünlerde ad veya markaya göre arar. Tablo yoksa boş liste döner."""
    q = _temiz_sorgu(sorgu)
    if len(q) < 2 or db is None:
        return []
    try:
        res = db.table("urun_onbellek").select("veri").or_(f"ad.ilike.*{q}*,marka.ilike.*{q}*").limit(limit).execute()
        return [r["veri"] for r in (res.data or []) if r.get("veri")]
    except Exception:  # noqa: BLE001
        return []


def onbellekten_barkod(db, kod):
    if db is None:
        return None
    try:
        res = db.table("urun_onbellek").select("veri").eq("kod", kod).limit(1).execute()
        return res.data[0]["veri"] if res.data else None
    except Exception:  # noqa: BLE001
        return None


def onbellege_yaz(db, urunler):
    """Ürünleri ortak önbelleğe ekler/günceller. Hata olursa sessizce geçer (önbellek zorunlu değil)."""
    satirlar = [{"kod": u["kod"], "ad": u["ad"], "marka": u.get("marka") or "", "veri": u} for u in urunler if u.get("kod")]
    if db is None or not satirlar:
        return
    try:
        db.table("urun_onbellek").upsert(satirlar).execute()
    except Exception:  # noqa: BLE001
        pass
