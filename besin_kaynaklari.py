{\rtf1\ansi\ansicpg1254\cocoartf2870
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 """\
besin_kaynaklari.py - Nova'n\uc0\u305 n d\u305 \u351  besin kaynaklar\u305 \
\
    Open Food Facts aramas\uc0\u305  (marka \'fcr\'fcnleri, milyonlarca kay\u305 t)\
    Barkod foto\uc0\u287 raf\u305 ndan numara okuma (OpenCV)\
    Barkodla \'fcr\'fcn bulma\
    Bulunan \'fcr\'fcnleri Supabase'deki "urun_onbellek" tablosunda saklama\
\
Open Food Facts \'fccretsiz ve a\'e7\uc0\u305 k bir veritaban\u305 d\u305 r; anahtar gerektirmez.\
Arama servisi dakikada s\uc0\u305 n\u305 rl\u305  say\u305 da istek kabul etti\u287 i i\'e7in sonu\'e7lar hem sunucu belle\u287 inde\
hem de Supabase'de saklan\uc0\u305 r, ayn\u305  \'fcr\'fcn i\'e7in ikinci kez d\u305 \u351 ar\u305 ya gidilmez.\
"""\
\
import io\
import re\
\
import requests\
import streamlit as st\
\
KULLANICI_AJANI = "Nova/1.0 (Streamlit diyet ve aktivite uygulamasi)"\
ARAMA_URL = "https://search.openfoodfacts.org/search"\
URUN_URL = "https://world.openfoodfacts.org/api/v2/product/\{kod\}.json"\
ALANLAR = "code,product_name,product_name_tr,brands,nutriments,serving_quantity,countries_tags"\
ZAMAN_ASIMI = 10  # saniye\
\
\
class KaynakHatasi(Exception):\
    """Open Food Facts'e ula\uc0\u351 \u305 lamad\u305  ya da cevap okunamad\u305 ."""\
\
\
# ------------------------------------------------------------------ Yard\uc0\u305 mc\u305 lar\
def _sayi(deger):\
    try:\
        x = float(deger)\
        return x if x >= 0 else None\
    except (TypeError, ValueError):\
        return None\
\
\
def _istek(url, params=None):\
    """Tek noktadan HTTP iste\uc0\u287 i (testlerde bu fonksiyon sahtesiyle de\u287 i\u351 tirilir)."""\
    try:\
        cevap = requests.get(url, params=params, headers=\{"User-Agent": KULLANICI_AJANI\}, timeout=ZAMAN_ASIMI)\
    except requests.RequestException as e:\
        raise KaynakHatasi(str(e)) from e\
    if cevap.status_code == 404:\
        return None\
    if cevap.status_code != 200:\
        raise KaynakHatasi(f"HTTP \{cevap.status_code\}")\
    try:\
        return cevap.json()\
    except ValueError as e:\
        raise KaynakHatasi("Cevap okunamad\uc0\u305 ") from e\
\
\
def _marka(brands):\
    if isinstance(brands, list):\
        parcalar = brands\
    else:\
        parcalar = str(brands or "").split(",")\
    gorulen, temiz = set(), []\
    for p in parcalar:\
        p = str(p).strip()\
        if p and p.lower() not in gorulen:\
            gorulen.add(p.lower())\
            temiz.append(p)\
    return ", ".join(temiz[:2])\
\
\
def urun_satiri(p):\
    """Open Food Facts \'fcr\'fcn\'fcn\'fc Nova'n\uc0\u305 n sade bi\'e7imine \'e7evirir. Makro de\u287 eri eksik \'fcr\'fcnler i\'e7in None d\'f6ner."""\
    n = p.get("nutriments") or \{\}\
    protein, karb, yag = _sayi(n.get("proteins_100g")), _sayi(n.get("carbohydrates_100g")), _sayi(n.get("fat_100g"))\
    ad = (p.get("product_name_tr") or p.get("product_name") or "").strip()\
    if not ad or None in (protein, karb, yag) or protein + karb + yag > 100.5:\
        return None\
    kcal = _sayi(n.get("energy-kcal_100g"))\
    if kcal is None:\
        kcal = protein * 4 + karb * 4 + yag * 9\
    tuz = _sayi(n.get("salt_100g"))\
    if tuz is None and _sayi(n.get("sodium_100g")) is not None:\
        tuz = _sayi(n.get("sodium_100g")) * 2.5\
    porsiyon = _sayi(p.get("serving_quantity"))\
    ulkeler = " ".join(p.get("countries_tags") or [])\
    return \{\
        "kod": str(p.get("code") or ""),\
        "ad": ad[:80],\
        "marka": _marka(p.get("brands")),\
        "protein": round(protein, 1), "karb": round(karb, 1), "yag": round(yag, 1), "kcal": round(kcal),\
        "lif": _sayi(n.get("fiber_100g")), "seker": _sayi(n.get("sugars_100g")),\
        "tuz": round(tuz, 2) if tuz is not None else None, "doymus_yag": _sayi(n.get("saturated-fat_100g")),\
        "porsiyon": int(porsiyon) if porsiyon and 5 <= porsiyon <= 2000 else None,\
        "turkiye": "turkey" in ulkeler or "turkiye" in ulkeler,\
    \}\
\
\
# ------------------------------------------------------------------ Open Food Facts\
@st.cache_data(ttl=24 * 3600, show_spinner=False)\
def _off_ara_onbellekli(sorgu):\
    veri = _istek(ARAMA_URL, \{"q": sorgu, "page_size": 40, "langs": "tr", "fields": ALANLAR\}) or \{\}\
    urunler = [u for u in (urun_satiri(p) for p in veri.get("hits", [])) if u]\
    # T\'fcrkiye'de sat\uc0\u305 lan \'fcr\'fcnler \'f6nce gelsin\
    urunler.sort(key=lambda u: not u["turkiye"])\
    return urunler[:25]\
\
\
def off_ara(sorgu):\
    """Marka \'fcr\'fcnlerinde arama. Ba\uc0\u287 lant\u305  sorununda KaynakHatasi f\u305 rlat\u305 r (hatalar \'f6nbelle\u287 e al\u305 nmaz)."""\
    sorgu = (sorgu or "").strip()\
    if len(sorgu) < 2:\
        return []\
    return _off_ara_onbellekli(sorgu.lower())\
\
\
@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)\
def _off_barkod_onbellekli(kod):\
    veri = _istek(URUN_URL.format(kod=kod), \{"fields": ALANLAR\})\
    if not veri or veri.get("status") != 1:\
        return None\
    return urun_satiri(veri.get("product") or \{\})\
\
\
def off_barkod(kod):\
    """Barkodla \'fcr\'fcn. Bulunamazsa ya da besin de\uc0\u287 erleri eksikse None d\'f6ner."""\
    return _off_barkod_onbellekli(kod)\
\
\
# ------------------------------------------------------------------ Barkod\
def barkod_gecerli_mi(kod):\
    """8-14 haneli say\uc0\u305  ve (EAN-8 / EAN-13 / UPC-A i\'e7in) kontrol hanesi do\u287 ru mu."""\
    if not re.fullmatch(r"\\d\{8,14\}", kod or ""):\
        return False\
    if len(kod) in (8, 12, 13, 14):\
        rakamlar = [int(c) for c in kod]\
        govde, kontrol = rakamlar[:-1], rakamlar[-1]\
        toplam = sum(r * (3 if i % 2 == 0 else 1) for i, r in enumerate(reversed(govde)))\
        return (10 - toplam % 10) % 10 == kontrol\
    return True\
\
\
def barkod_oku(goruntu_bytes):\
    """Foto\uc0\u287 raftaki barkod numaralar\u305 n\u305  d\'f6nd\'fcr\'fcr. OpenCV kurulu de\u287 ilse ImportError f\u305 rlat\u305 r."""\
    import cv2\
    import numpy as np\
    from PIL import Image, ImageOps\
\
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(goruntu_bytes))).convert("RGB")\
    img.thumbnail((1600, 1600))\
    bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)\
    okuyucu = cv2.barcode.BarcodeDetector()\
    bulunan = []\
    # Telefonla dik \'e7ekilen foto\uc0\u287 raflarda barkod yan durabilir; d\'f6nd\'fcrerek de denenir\
    for aci in (None, cv2.ROTATE_90_CLOCKWISE):\
        resim = bgr if aci is None else cv2.rotate(bgr, aci)\
        sonuc = okuyucu.detectAndDecodeWithType(resim) if hasattr(okuyucu, "detectAndDecodeWithType") else okuyucu.detectAndDecode(resim)\
        bilgiler = sonuc[1] if isinstance(sonuc, tuple) and len(sonuc) > 1 else ()\
        if isinstance(bilgiler, str):\
            bilgiler = (bilgiler,)\
        for kod in bilgiler or ():\
            kod = (kod or "").strip()\
            if barkod_gecerli_mi(kod) and kod not in bulunan:\
                bulunan.append(kod)\
        if bulunan:\
            break\
    return bulunan\
\
\
# ------------------------------------------------------------------ Supabase \'f6nbelle\uc0\u287 i\
def _temiz_sorgu(sorgu):\
    # PostgREST filtre s\'f6zdizimini bozabilecek karakterleri \'e7\uc0\u305 kar\
    return re.sub(r"[,()%*\\\\:\\"']", " ", sorgu or "").strip()\
\
\
def onbellekte_ara(db, sorgu, limit=15):\
    """Daha \'f6nce bulunmu\uc0\u351  \'fcr\'fcnlerde ad veya markaya g\'f6re arar. Tablo yoksa bo\u351  liste d\'f6ner."""\
    q = _temiz_sorgu(sorgu)\
    if len(q) < 2 or db is None:\
        return []\
    try:\
        res = db.table("urun_onbellek").select("veri").or_(f"ad.ilike.*\{q\}*,marka.ilike.*\{q\}*").limit(limit).execute()\
        return [r["veri"] for r in (res.data or []) if r.get("veri")]\
    except Exception:  # noqa: BLE001\
        return []\
\
\
def onbellekten_barkod(db, kod):\
    if db is None:\
        return None\
    try:\
        res = db.table("urun_onbellek").select("veri").eq("kod", kod).limit(1).execute()\
        return res.data[0]["veri"] if res.data else None\
    except Exception:  # noqa: BLE001\
        return None\
\
\
def onbellege_yaz(db, urunler):\
    """\'dcr\'fcnleri ortak \'f6nbelle\uc0\u287 e ekler/g\'fcnceller. Hata olursa sessizce ge\'e7er (\'f6nbellek zorunlu de\u287 il)."""\
    satirlar = [\{"kod": u["kod"], "ad": u["ad"], "marka": u.get("marka") or "", "veri": u\} for u in urunler if u.get("kod")]\
    if db is None or not satirlar:\
        return\
    try:\
        db.table("urun_onbellek").upsert(satirlar).execute()\
    except Exception:  # noqa: BLE001\
        pass\
}