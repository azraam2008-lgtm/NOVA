import datetime
import hashlib
import hmac
import html
import json
import os
import re
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from supabase import create_client, Client

# --- AI MODÜLLERİ ---
from meal_scan import meal_scan_page
from nova_pages import coach_page, ask_page

st.set_page_config(page_title="Nova — Diyet ve Aktivite Asistanı", page_icon="🦢", layout="wide", initial_sidebar_state="collapsed")


# ----------------------------------------------------
# SUPABASE BAĞLANTISI
# ----------------------------------------------------
def _gizli_ayar(ad, varsayilan):
    """Streamlit Secrets'tan okur; tanımlı değilse varsayılanı döndürür."""
    try:
        return st.secrets[ad]
    except Exception:
        return varsayilan


# Gizli (secret) anahtar Streamlit Secrets'a girilmelidir; koda ve GitHub'a asla yazılmaz.
# Secrets'ta yoksa geçiş dönemi için herkese açık (publishable) anahtar kullanılır.
SUPABASE_URL = _gizli_ayar("SUPABASE_URL", "https://klncgexnykfwzpcrijrt.supabase.co")
SUPABASE_KEY = _gizli_ayar("SUPABASE_KEY", "sb_publishable_yXcnmg2uJsA7vR0DXnWUWQ_06Jm4E8e")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----------------------------------------------------
# SABİTLER
# ----------------------------------------------------
TEMA_AYARLARI = {
    "Yakut Kızılı": {"bg_image": "925912004661385138.jpg", "fallback_bg": "#2A0808", "text_color": "#ffffff", "card_bg": "rgba(35, 5, 10, 0.86)", "ring_track": "rgba(255,255,255,0.15)", "cizgi": "rgba(255,255,255,0.22)"},
    "Turkuaz Ferahlığı": {"acik": True, "bg_image": "Oppo_Find_X9s_Wallpaper.jpg", "fallback_bg": "#E0F2F1", "text_color": "#00382f", "card_bg": "rgba(236, 250, 247, 0.94)", "ring_track": "rgba(0,0,0,0.08)", "cizgi": "rgba(0,0,0,0.14)"},
    "Altın Zarafet": {"bg_image": "826903181627399116.jpg", "fallback_bg": "#3e2723", "text_color": "#ffffff", "card_bg": "rgba(40, 25, 20, 0.88)", "ring_track": "rgba(255,255,255,0.15)", "cizgi": "rgba(255,255,255,0.22)"},
    "Bordo Kadife": {"bg_image": "Deep_Maroon.jpg", "fallback_bg": "#310000", "text_color": "#ffebee", "card_bg": "rgba(45, 0, 15, 0.90)", "ring_track": "rgba(255,255,255,0.15)", "cizgi": "rgba(255,255,255,0.22)"},
    "Derin Mavi": {"bg_image": "Mavi_Arka_Plan.jpg", "fallback_bg": "#00102A", "text_color": "#e3f2fd", "card_bg": "rgba(0, 15, 45, 0.90)", "ring_track": "rgba(255,255,255,0.15)", "cizgi": "rgba(255,255,255,0.22)"},
    "Koyu Cam": {"bg_image": "687854543129884120.jpg", "fallback_bg": "#0f0f0f", "text_color": "#ffffff", "card_bg": "rgba(20, 20, 20, 0.90)", "ring_track": "rgba(255,255,255,0.15)", "cizgi": "rgba(255,255,255,0.22)"},
}

AMAC_SECENEKLERI = ["Kilo vermek istiyorum", "Kilomu korumak istiyorum", "Kilo almak istiyorum", "Kas kazanmak istiyorum", "Sağlıklı beslenmek istiyorum"]
OGUNLER = ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"]
OGUN_IKONLARI = {"Kahvaltı": "🌅", "Öğle Yemeği": "☀️", "Akşam Yemeği": "🌙", "Ara Öğün": "🍎"}

# Aktivite düzeyi -> (BMR çarpanı, bu düzeyin zaten içerdiği günlük adım)
AKTIVITE_DUZEYLERI = {
    "Hareketsiz (masa başı, spor yok)": (1.2, 3000),
    "Hafif aktif (haftada 1-3 gün hareket)": (1.375, 5000),
    "Orta aktif (haftada 3-5 gün spor)": (1.55, 7500),
    "Çok aktif (haftada 6-7 gün spor)": (1.725, 10000),
}
VARSAYILAN_AKTIVITE = "Hafif aktif (haftada 1-3 gün hareket)"

# Egzersiz günlüğü için MET değerleri (Compendium of Physical Activities'teki yaklaşık değerler)
EGZERSIZ_MET = {
    "🚶 Yürüyüş (orta tempo)": 3.5,
    "🚶‍♀️ Tempolu yürüyüş": 4.3,
    "🏃 Koşu": 9.8,
    "🚴 Bisiklet": 7.5,
    "🏊 Yüzme": 8.0,
    "🏋️ Ağırlık antrenmanı": 5.0,
    "🧘 Yoga / Pilates": 3.0,
    "💃 Dans": 5.0,
    "⚽ Takım sporu": 7.0,
    "🪜 Merdiven çıkma": 8.0,
}

VARSAYILAN_PROFIL = {
    "ad": "", "cinsiyet": "Kadın", "dogum_yili": 2000, "boy": 165, "mevcut_kilo": 60.0, "hedef_kilo": 55.0,
    "hedef_sure_ay": 2, "tema": "Koyu Cam", "amaclar": [], "aktivite_duzeyi": VARSAYILAN_AKTIVITE, "setup_tamamlandi": False,
}

MAKS_GUNLUK_FARK = 1000  # kcal; haftada yaklaşık 1 kg'dan hızlı değişim hedeflenmez
GITHUB_KOK_URL = "https://raw.githubusercontent.com/azraam2008-lgtm/NOVA/main/"
# GitHub deposundaki dosya adı farklı olabildiği için sırayla denenir
YEMEK_CSV_ADLARI = ["cok_daha_kapsamli_yemek_veritabani.csv", "cok_daha_kapsamli_yemek_veritabani_2.csv"]
TURKIYE_SAATI = datetime.timezone(datetime.timedelta(hours=3))


# ----------------------------------------------------
# GENEL YARDIMCILAR
# ----------------------------------------------------
def bugun():
    """Sunucu UTC'de çalışsa bile günü Türkiye saatine göre verir."""
    return datetime.datetime.now(TURKIYE_SAATI).date()


def sinirla(deger, alt, ust):
    return max(alt, min(ust, deger))


def tr_kucuk(metin):
    """Türkçe İ/I harflerini doğru küçültür (arama eşleşmesi için)."""
    return str(metin).replace("İ", "i").replace("I", "ı").lower()


def kart(anahtar):
    """İçindeki Streamlit bileşenlerini gerçekten saran kart kutusu (CSS: st-key-kart_*)."""
    return st.container(key=anahtar)


def guvenli(metin):
    return html.escape(str(metin))


# ----------------------------------------------------
# YEMEK VERİTABANI
# ----------------------------------------------------
GEREKLI_SUTUNLAR = {"Yemek Adı", "Protein (g)", "Karbonhidrat (g)", "Yağ (g)"}


@st.cache_data(ttl=3600, show_spinner=False)
def _yemek_csv_oku():
    """Önce uygulamanın yanındaki dosyayı, sonra GitHub'ı dener. Hiçbiri olmazsa hata fırlatır (önbelleğe alınmaz)."""
    klasor = Path(__file__).parent
    kaynaklar = [klasor / ad for ad in YEMEK_CSV_ADLARI] + [GITHUB_KOK_URL + ad for ad in YEMEK_CSV_ADLARI]
    for kaynak in kaynaklar:
        try:
            df = pd.read_csv(kaynak)
        except Exception:
            continue
        if GEREKLI_SUTUNLAR <= set(df.columns):
            return df
    raise FileNotFoundError("Yemek veritabanı bulunamadı")


def yemek_veritabanini_yukle():
    try:
        return _yemek_csv_oku()
    except Exception:
        return None


# ----------------------------------------------------
# ŞİFRE VE KULLANICI FONKSİYONLARI
# ----------------------------------------------------
PBKDF2_TUR = 600_000


def _pbkdf2(sifre, tuz, tur):
    return hashlib.pbkdf2_hmac("sha256", sifre.encode("utf-8"), tuz, tur).hex()


def sifre_hashle(sifre):
    """Tuzlu PBKDF2-SHA256 hash'i üretir: pbkdf2$<tur>$<tuz>$<hash>"""
    tuz = os.urandom(16)
    return f"pbkdf2${PBKDF2_TUR}${tuz.hex()}${_pbkdf2(sifre, tuz, PBKDF2_TUR)}"


def sifre_dogrula(sifre, kayitli):
    """(doğru_mu, eski_formatta_mı) döndürür. Eski tuzsuz SHA-256 kayıtları da kabul edilir."""
    if not kayitli:
        return False, False
    if kayitli.startswith("pbkdf2$"):
        try:
            _, tur, tuz_hex, ozet_hex = kayitli.split("$")
            return hmac.compare_digest(_pbkdf2(sifre, bytes.fromhex(tuz_hex), int(tur)), ozet_hex), False
        except Exception:
            return False, False
    eski = hashlib.sha256(sifre.encode("utf-8")).hexdigest()
    return hmac.compare_digest(eski, kayitli), True


def sifre_kontrol(sifre):
    if len(sifre) < 6: return "Şifre en az 6 karakter olmalıdır."
    if not any(c.isupper() for c in sifre): return "Şifre en az bir büyük harf içermelidir."
    return None


def kullanici_hash_getir(username):
    """(bağlantı_başarılı_mı, hash veya None) döndürür. Yalnızca istenen kullanıcı sorgulanır."""
    try:
        res = supabase.table("kullanicilar").select("password_hash").eq("username", username).execute()
        return True, (res.data[0]["password_hash"] if res.data else None)
    except Exception:
        return False, None


def verileri_yukle(username):
    """Kullanıcı verisini döndürür. Bağlantı hatasında None döner (boş veriyle üzerine yazmamak için)."""
    try:
        res = supabase.table("kullanici_verileri").select("data").eq("username", username).execute()
    except Exception:
        return None
    d = (res.data[0].get("data") if res.data else None) or {}
    return {
        "gunluk_kayitlar": d.get("gunluk_kayitlar") or [],
        "aktivite_loglari": d.get("aktivite_loglari") or {},
        "kilo_gecmisi": d.get("kilo_gecmisi") or [],
        "ozel_yemekler": d.get("ozel_yemekler") or [],
        "profil": {**VARSAYILAN_PROFIL, **(d.get("profil") or {})},
    }


def verileri_kaydet(username):
    data = {"gunluk_kayitlar": st.session_state.gunluk_kayitlar, "aktivite_loglari": st.session_state.aktivite_loglari, "kilo_gecmisi": st.session_state.kilo_gecmisi,
            "ozel_yemekler": st.session_state.get("ozel_yemekler", []), "profil": st.session_state.profil}
    try:
        supabase.table("kullanici_verileri").upsert({"username": username, "data": data}).execute()
        return True
    except Exception:
        st.session_state["_hata"] = "⚠️ Son değişiklik buluta kaydedilemedi. İnternet bağlantını kontrol edip tekrar dene."
        return False


def oturumu_baslat(username, veriler):
    st.session_state.giris_yapildi = True
    st.session_state.aktif_kullanici = username
    st.session_state.onboarding_step = 1
    for anahtar, deger in veriler.items():
        st.session_state[anahtar] = deger


def bildir(mesaj):
    """st.rerun() sonrasında da görünen başarı mesajı."""
    st.session_state["_bildirim"] = mesaj


def bildirimleri_goster():
    hata = st.session_state.pop("_hata", None)
    if hata: st.error(hata)
    mesaj = st.session_state.pop("_bildirim", None)
    if mesaj: st.success(mesaj)


# ----------------------------------------------------
# HESAPLAMA
# ----------------------------------------------------
def yas_hesapla(p):
    return bugun().year - int(p.get("dogum_yili", 2000))


def aktivite_bilgisi(p):
    return AKTIVITE_DUZEYLERI.get(p.get("aktivite_duzeyi"), AKTIVITE_DUZEYLERI[VARSAYILAN_AKTIVITE])


def hesapla_bmr_ve_hedef(p):
    kilo = float(p.get("mevcut_kilo", 60.0))
    boy = float(p.get("boy", 165))
    hedef_kilo = float(p.get("hedef_kilo", kilo))
    kadin = p.get("cinsiyet", "Kadın") == "Kadın"

    bmr = (10 * kilo) + (6.25 * boy) - (5 * yas_hesapla(p)) + (-161 if kadin else 5)
    carpan, _ = aktivite_bilgisi(p)
    tdee = bmr * carpan

    # Pozitif: açık (kilo verme), negatif: fazla (kilo alma). Her iki yönde de sınırlandırılır.
    gunluk_acik = ((kilo - hedef_kilo) * 7700) / max(1, int(p.get("hedef_sure_ay", 1)) * 30)
    gunluk_acik = sinirla(gunluk_acik, -MAKS_GUNLUK_FARK, MAKS_GUNLUK_FARK)

    hedef_kalori = max(1200 if kadin else 1500, tdee - gunluk_acik)
    return bmr, tdee, gunluk_acik, hedef_kalori


def adim_kalorisi(p, adim):
    """Aktivite düzeyinin zaten içerdiği adımlar tekrar sayılmaz; yalnızca fazlası eklenir."""
    _, taban_adim = aktivite_bilgisi(p)
    return max(0, adim - taban_adim) * 0.04


def egzersiz_kalorisi(met, dakika, kilo):
    """Net harcama: dinlenme harcaması (1 MET) zaten günlük hedefte olduğu için çıkarılır."""
    return max(0.0, (met - 1) * kilo * dakika / 60)


def gunun_egzersiz_kalorisi(kayit):
    return kayit.get("egzersiz_kalori", 0) + sum(e.get("kcal", 0) for e in kayit.get("egzersizler", []))


# ----------------------------------------------------
# GÖRÜNÜM (CSS)
# ----------------------------------------------------
FONT_IMPORT = "@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');"

# Tüm temalarda ortak kurallar. Renkler, tema_css_uygula() içinde tanımlanan CSS değişkenlerinden gelir.
ORTAK_CSS = """
:root { color-scheme: light; }
html, body, [data-testid="stAppViewContainer"] { font-family: 'Plus Jakarta Sans', sans-serif; }
[data-testid="stAppViewContainer"] { background-color: var(--nv-bg) !important; background-image: var(--nv-img) !important; background-size: cover; background-position: center; background-attachment: fixed; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stMainBlockContainer"] { max-width: 1100px; padding-top: 2.5rem; padding-bottom: 4rem; }

.nova-header { color: var(--nv-text) !important; font-family: 'Playfair Display', serif; font-size: 5rem; letter-spacing: 20px; text-align: center; font-weight: 700; margin-top: -20px; line-height: 1.1; }
.nova-header.kucuk { font-size: 3.5rem; margin-top: 10px; }
.nova-user { color: var(--nv-text) !important; text-align: center; font-size: 1.4rem; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 5px; opacity: 0.9; font-weight: 600; }
.nova-tarih { color: var(--nv-text) !important; text-align: center; font-size: 1rem; letter-spacing: 2px; margin-bottom: 30px; opacity: 0.9; font-weight: 600; }
.nova-header, .nova-user, .nova-tarih { text-shadow: var(--nv-golge); }

/* ---------- KARTLAR ---------- */
div[class*="st-key-kart_"] { background: var(--nv-card) !important; padding: 32px; border-radius: 28px; backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px); margin-bottom: 26px; border: 1px solid var(--nv-line); box-shadow: 0 15px 50px rgba(0,0,0,0.35); }
.info-box { background: var(--nv-track) !important; border-left: 4px solid var(--nv-text) !important; padding: 15px; border-radius: 10px; margin-bottom: 22px; color: var(--nv-text) !important; font-weight: 600; }
.sonuc-kutu { background: var(--nv-track); padding: 25px; border-radius: 16px; margin-top: 20px; }
hr.nova-cizgi { border: none; border-top: 1px solid var(--nv-line); margin: 22px 0; }
.kart-baslik { font-size: 1.6rem !important; font-weight: 800 !important; margin: 0 0 14px 0 !important; }

/* ---------- YAZILAR: her temada temanın yazı rengi ---------- */
[data-testid="stMain"] :is(h1, h2, h3, h4, h5, h6, p, li, label, small, td, th, strong, em, b),
[data-testid="stMain"] [data-testid="stMarkdownContainer"] span:not([data-baseweb]),
[data-testid="stMain"] [data-testid="stCaptionContainer"],
[data-testid="stMain"] [data-testid="stMetricValue"], [data-testid="stMain"] [data-testid="stMetricValue"] *,
[data-testid="stMain"] [data-testid="stMetricLabel"] *,
[data-testid="stMain"] [data-testid="stSliderThumbValue"],
[data-testid="stMain"] [data-testid="stSliderTickBarMin"], [data-testid="stMain"] [data-testid="stSliderTickBarMax"],
[data-testid="stMain"] [data-testid="stExpander"] summary, [data-testid="stMain"] [data-testid="stExpander"] summary *,
[data-testid="stMain"] [data-testid="stWidgetLabel"] *,
[data-testid="stMain"] [data-testid="stFileUploaderFileName"], [data-testid="stMain"] [data-testid="stFileUploaderFile"] small {
    color: var(--nv-text) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stMain"] [data-testid="stCaptionContainer"] { opacity: 0.8; }
/* Simge yazı tipini koru (yoksa "keyboard_arrow_right" gibi yazılar görünür) ve başlık bağlantı simgelerini gizle */
[data-testid="stMain"] [data-testid="stIconMaterial"][data-testid="stIconMaterial"][data-testid="stIconMaterial"] { font-family: 'Material Symbols Rounded' !important; }
[data-testid="stHeaderActionElements"] { display: none !important; }
[data-testid="stMain"] [data-testid="stMarkdownContainer"] a { color: var(--nv-text) !important; text-decoration: underline; font-weight: 700; }
[data-testid="stMain"] svg[data-testid="stExpanderToggleIcon"], [data-testid="stMain"] [data-testid="stExpander"] summary svg { color: var(--nv-text) !important; fill: var(--nv-text) !important; }
[data-testid="stMain"] [data-testid="stFileUploaderFile"] svg, [data-testid="stMain"] [data-testid="stFileUploaderDeleteBtn"] svg { color: var(--nv-text) !important; }

/* ---------- GİRİŞ ALANLARI: beyaz zemin, siyah yazı ---------- */
div[data-baseweb="select"] > div, div[data-baseweb="input"], div[data-baseweb="input"] > div, div[data-baseweb="textarea"], div[data-baseweb="base-input"],
[data-testid="stNumberInputContainer"], input[type="text"], input[type="number"], input[type="password"], textarea {
    background-color: #ffffff !important; color: #000000 !important; border-radius: 12px !important;
}
div[data-baseweb="select"] > div, div[data-baseweb="input"], div[data-baseweb="textarea"] { border: 2px solid rgba(0,0,0,0.15) !important; border-radius: 12px !important; }
[data-testid="stMain"] :is(input, textarea), div[data-baseweb="select"] *, input::placeholder, textarea::placeholder {
    color: #000000 !important; -webkit-text-fill-color: #000000 !important; caret-color: #000000 !important; font-weight: 600;
}
input::placeholder, textarea::placeholder { opacity: 0.45 !important; }
[data-testid="stNumberInputContainer"] button { background: #f1f3f6 !important; color: #000000 !important; border: none !important; }
[data-testid="stNumberInputContainer"] button svg { fill: #000000 !important; color: #000000 !important; }
div[data-baseweb="input"] button { color: #000000 !important; }
[data-testid="InputInstructions"] { color: #555555 !important; }
div[data-baseweb="popover"], ul[role="listbox"], ul[role="listbox"] li, ul[role="listbox"] span { background-color: #ffffff !important; color: #000000 !important; }
span[data-baseweb="tag"] { background-color: var(--nv-text) !important; }
span[data-baseweb="tag"], span[data-baseweb="tag"] * { color: var(--nv-on-accent) !important; -webkit-text-fill-color: var(--nv-on-accent) !important; fill: var(--nv-on-accent) !important; }

/* ---------- UYARI KUTULARI: her temada açık zemin, koyu yazı ---------- */
[data-testid="stAlertContainer"] { background-color: rgba(255,255,255,0.95) !important; border-radius: 14px !important; border-left: 5px solid #1a73e8 !important; }
[data-testid="stAlert"] :is(p, span, li, strong, b, em, div, code), [data-testid="stAlertContainer"] * { color: #1a1a1a !important; font-weight: 600; }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) { border-left-color: #1f9d55 !important; }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) { border-left-color: #d93025 !important; }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) { border-left-color: #f2a600 !important; }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) { border-left-color: #1a73e8 !important; }

/* ---------- AÇILIR PANEL, DOSYA YÜKLEME, FORM, ÇERÇEVELİ KUTU ---------- */
[data-testid="stExpander"] details { background-color: var(--nv-track) !important; border: 1px solid var(--nv-line) !important; border-radius: 14px !important; }
[data-testid="stFileUploaderDropzone"] { background-color: #ffffff !important; border-radius: 14px !important; border: 2px dashed rgba(0,0,0,0.2) !important; }
[data-testid="stFileUploaderDropzone"] :is(span, small, p, div), [data-testid="stFileUploaderDropzoneInstructions"] * { color: #1a1a1a !important; }
[data-testid="stFileUploaderDropzone"] svg { color: #1a1a1a !important; fill: #1a1a1a !important; }
[data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] { border-color: var(--nv-line) !important; border-radius: 18px !important; }
[data-testid="stCameraInput"] button { color: #1a1a1a !important; }

/* ---------- SEKMELER ---------- */
div[data-testid="stTabs"] div[role="tablist"] {
    background: var(--nv-card) !important; padding: 8px !important; border-radius: 24px !important; gap: 10px !important;
    border: 1px solid var(--nv-line) !important; box-shadow: 0 8px 20px rgba(0,0,0,0.12) !important;
    margin-bottom: 22px !important; display: flex; justify-content: center; flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none;
}
div[data-testid="stTabs"] div[role="tablist"]::-webkit-scrollbar { display: none; }
button[data-baseweb="tab"] {
    background-color: transparent !important; font-size: 1.05rem !important; font-weight: 600 !important;
    padding: 12px 26px !important; margin: 0 !important; border-radius: 18px !important; border: none !important;
    opacity: 0.75; white-space: nowrap; flex-shrink: 0; transition: all 0.25s ease !important;
}
button[data-baseweb="tab"], button[data-baseweb="tab"] p { color: var(--nv-text) !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }
button[data-baseweb="tab"]:hover { opacity: 1 !important; background-color: var(--nv-track) !important; }
button[data-baseweb="tab"][aria-selected="true"] { background-color: var(--nv-text) !important; opacity: 1 !important; box-shadow: 0 6px 15px rgba(0,0,0,0.15) !important; }
button[data-baseweb="tab"][aria-selected="true"], button[data-baseweb="tab"][aria-selected="true"] p { color: var(--nv-on-accent) !important; font-weight: 800 !important; }
div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] { display: none !important; }

/* ---------- DÜĞMELER ---------- */
[data-testid="stMain"] :is(.stButton, .stDownloadButton, .stFormSubmitButton, .stLinkButton) :is(button, a) {
    background: var(--nv-card) !important; border: 1px solid var(--nv-line) !important; font-weight: 700 !important;
    border-radius: 16px !important; padding: 10px 18px; min-height: 44px; box-shadow: 0 8px 22px rgba(0,0,0,0.18);
    backdrop-filter: blur(10px); transition: all 0.25s ease;
}
[data-testid="stMain"] :is(.stButton, .stDownloadButton, .stFormSubmitButton, .stLinkButton) :is(button, a),
[data-testid="stMain"] :is(.stButton, .stDownloadButton, .stFormSubmitButton, .stLinkButton) :is(button, a) * { color: var(--nv-text) !important; }
[data-testid="stMain"] :is(.stButton, .stDownloadButton, .stFormSubmitButton, .stLinkButton) :is(button, a):hover {
    transform: translateY(-2px); background: var(--nv-text) !important; border-color: var(--nv-text) !important; box-shadow: 0 12px 28px rgba(0,0,0,0.28);
}
[data-testid="stMain"] :is(.stButton, .stDownloadButton, .stFormSubmitButton, .stLinkButton) :is(button, a):hover * { color: var(--nv-on-accent) !important; }
[data-testid="stMain"] :is(.stButton, .stFormSubmitButton) button:disabled { opacity: 0.4 !important; transform: none !important; cursor: not-allowed; }
/* Birincil düğmeler (Analiz et, Günlüğe ekle, Sor...) dolu renkte */
[data-testid="stMain"] button[kind="primary"], [data-testid="stMain"] button[kind="primaryFormSubmit"] { background: var(--nv-text) !important; border-color: var(--nv-text) !important; }
[data-testid="stMain"] button[kind="primary"] *, [data-testid="stMain"] button[kind="primaryFormSubmit"] * { color: var(--nv-on-accent) !important; }

/* Dönem seçici (7 gün / 30 gün / ...): yatay radyo düğmeleri bölmeli düğme gibi görünür */
.st-key-donem_secici { background: var(--nv-card); border: 1px solid var(--nv-line); border-radius: 18px; padding: 6px; margin-bottom: 18px; }
.st-key-donem_secici [role="radiogroup"] { display: flex; flex-wrap: nowrap; gap: 6px; width: 100%; }
.st-key-donem_secici [role="radiogroup"] label { flex: 1 1 0; justify-content: center; margin: 0 !important; padding: 9px 4px !important; border-radius: 12px !important; border: none !important; background: transparent !important; cursor: pointer; }
.st-key-donem_secici [role="radiogroup"] label > div:first-child { display: none !important; }
.st-key-donem_secici [role="radiogroup"] label p { font-weight: 700 !important; white-space: nowrap; }
.st-key-donem_secici [role="radiogroup"] label:has(input:checked) { background: var(--nv-text) !important; }
.st-key-donem_secici [role="radiogroup"] label:has(input:checked) p { color: var(--nv-on-accent) !important; }
/* Toggle, radyo ve kaydırıcı vurgu rengi */
[data-testid="stMain"] [role="radiogroup"] label { background: var(--nv-track); padding: 6px 14px; border-radius: 999px; border: 1px solid var(--nv-line); }

/* ---------- HALKALAR, TABLOLAR, GÜNLÜK ---------- */
.ring-container { width: 180px; height: 180px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; }
.ring-inner { width: 140px; height: 140px; border-radius: 50%; background: var(--nv-card) !important; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.ring-val { font-size: 2rem; font-weight: 800; margin-bottom: -5px; }
.ring-val.kirmizi { color: var(--nv-kirmizi) !important; }
.ring-val.mavi { color: var(--nv-mavi) !important; }
.ring-lbl { font-size: 1rem; opacity: 0.8; text-transform: uppercase; letter-spacing: 2px; color: var(--nv-text) !important; }
table.nova-tablo { width: 100%; font-size: 1.1rem; background: transparent; border-collapse: collapse; }
table.nova-tablo th, table.nova-tablo td { padding: 12px; border-bottom: 1px solid var(--nv-line); text-align: left; color: var(--nv-text) !important; }
table.nova-tablo th { font-weight: 800; font-size: 1.15rem; opacity: 0.9; }
table.nova-tablo, table.nova-tablo tr, table.nova-tablo td, table.nova-tablo th { border-left: none !important; border-right: none !important; border-top: none !important; background: transparent !important; }
table.nova-tablo td { border-bottom: 1px solid var(--nv-line) !important; }
table.nova-tablo td.sag { text-align: right; white-space: nowrap; }
table.nova-tablo td.mavi, table.nova-tablo td.mavi b { color: var(--nv-mavi) !important; }
table.nova-tablo td.kirmizi, table.nova-tablo td.kirmizi b { color: var(--nv-kirmizi) !important; }
table.nova-tablo td.yesil, table.nova-tablo td.yesil b { color: var(--nv-yesil) !important; }
table.nova-tablo tr.toplam-satir td { font-size: 1.2rem; font-weight: 800; border-top: 2px solid var(--nv-text) !important; border-bottom: none !important; }
.st-key-ust_bar { background: var(--nv-card); border: 1px solid var(--nv-line); border-radius: 20px; padding: 12px 14px 14px 14px; margin-bottom: 18px; backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); }
.makro-iz { width: 100%; background-color: var(--nv-track); border-radius: 4px; height: 7px; }
.ogun-baslik { display: flex; justify-content: space-between; align-items: baseline; padding: 10px 0 6px 0; border-bottom: 1px solid var(--nv-line); margin-top: 10px; }
.ogun-baslik span { color: var(--nv-text) !important; font-weight: 800; font-size: 1.1rem; }
.ogun-baslik .ogun-kcal { font-size: 1rem; opacity: 0.85; }
.ogun-satir { color: var(--nv-text) !important; line-height: 1.35; }
.ogun-satir small { opacity: 0.75; }
.dagilim { display: flex; height: 10px; border-radius: 6px; overflow: hidden; margin: 6px 0 4px 0; background: var(--nv-track); }

/* Mobilde de yan yana kalması gereken satırlar */
div[class*="st-key-metrik_satiri"] [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 0.5rem !important; }
div[class*="st-key-metrik_satiri"] [data-testid="stColumn"] { min-width: 0 !important; background: var(--nv-track); border-radius: 14px; padding: 10px 12px; }
div[class*="st-key-metrik_satiri"] [data-testid="stMetricValue"] { font-size: 1.6rem; }
:is(.st-key-ogun_listesi, .st-key-egzersiz_listesi, .st-key-ozel_liste, .st-key-gezinme) [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 0.6rem !important; }
:is(.st-key-ogun_listesi, .st-key-egzersiz_listesi, .st-key-ozel_liste, .st-key-gezinme) [data-testid="stColumn"] { min-width: 0 !important; }
:is(.st-key-ogun_listesi, .st-key-egzersiz_listesi, .st-key-ozel_liste) [data-testid="stColumn"]:last-child { flex: 0 0 52px !important; }
:is(.st-key-ogun_listesi, .st-key-egzersiz_listesi, .st-key-ozel_liste) .stButton button { min-height: 36px !important; padding: 4px 8px !important; box-shadow: none !important; }

/* ---------- AI SOHBET ---------- */
.nova-sohbet-baslik { display: flex; gap: 14px; align-items: center; margin-bottom: 14px; }
.nova-sohbet-logo { width: 48px; height: 48px; flex-shrink: 0; border-radius: 50%; display: grid; place-items: center; background: var(--nv-text); font-size: 1.5rem; box-shadow: 0 6px 16px rgba(0,0,0,0.25); }
.nova-sohbet-baslik b { display: block; font-size: 1.2rem; color: var(--nv-text) !important; }
.nova-sohbet-baslik small { display: block; opacity: 0.75; color: var(--nv-text) !important; }
.st-key-nova_sohbet { background: var(--nv-track) !important; border: 1px solid var(--nv-line) !important; border-radius: 22px !important; padding: 14px !important; }
.st-key-nova_sohbet [data-testid="stChatMessage"] {
    background: var(--nv-card) !important; border: 1px solid var(--nv-line); border-radius: 20px 20px 20px 6px;
    padding: 10px 14px !important; max-width: 88%; width: fit-content; gap: 10px; box-shadow: 0 4px 14px rgba(0,0,0,0.12); margin-bottom: 10px;
}
.st-key-nova_sohbet [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    margin-left: auto; flex-direction: row-reverse; background: var(--nv-text) !important; border-color: var(--nv-text); border-radius: 20px 20px 6px 20px;
}
.st-key-nova_sohbet [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) :is(p, li, strong, em, span, b) { color: var(--nv-on-accent) !important; }
.st-key-nova_sohbet [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] { text-align: right; }
[data-testid="stChatMessageAvatarUser"] { background: var(--nv-on-accent) !important; color: var(--nv-text) !important; }
[data-testid="stChatMessageAvatarCustom"] { background: var(--nv-text) !important; border-radius: 50% !important; }
[data-testid="stChatInput"] { background: #ffffff !important; border-radius: 999px !important; border: 2px solid var(--nv-line) !important; box-shadow: 0 8px 22px rgba(0,0,0,0.18); }
[data-testid="stChatInput"] > div { background: #ffffff !important; border-radius: 999px !important; }
[data-testid="stChatInput"] textarea { background: transparent !important; color: #000000 !important; -webkit-text-fill-color: #000000 !important; }
[data-testid="stChatInputSubmitButton"] { background: var(--nv-bg) !important; border-radius: 50% !important; }
[data-testid="stChatInputSubmitButton"] svg { color: #ffffff !important; fill: #ffffff !important; }
.st-key-nova_oneriler .stButton button { border-radius: 999px !important; text-align: left; justify-content: flex-start; font-weight: 600 !important; min-height: 40px; }
.st-key-nova_oneriler .stButton button p { font-size: 0.92rem !important; }

/* ---------- TELEFON EKRANI ---------- */
@media (max-width: 640px) {
    [data-testid="stMainBlockContainer"] { padding: 3rem 0.7rem 3rem 0.7rem !important; }
    .nova-header { font-size: 2.6rem !important; letter-spacing: 10px; margin-top: 0; }
    .nova-header.kucuk { font-size: 2.3rem !important; }
    .nova-user { font-size: 1.05rem; letter-spacing: 3px; }
    .nova-tarih { font-size: 0.85rem; letter-spacing: 1px; margin-bottom: 18px; }
    div[class*="st-key-kart_"] { padding: 18px 14px; border-radius: 20px; margin-bottom: 16px; }
    [data-testid="stMain"] h2, .kart-baslik { font-size: 1.35rem !important; }
    [data-testid="stMain"] h3 { font-size: 1.15rem !important; }
    div[data-testid="stTabs"] div[role="tablist"] { justify-content: flex-start; gap: 4px !important; padding: 6px !important; border-radius: 18px !important; }
    button[data-baseweb="tab"] { padding: 9px 13px !important; border-radius: 14px !important; }
    button[data-baseweb="tab"] p { font-size: 0.88rem !important; }
    table.nova-tablo { font-size: 0.92rem; }
    table.nova-tablo th, table.nova-tablo td { padding: 8px 4px; }
    table.nova-tablo th { font-size: 0.98rem; }
    div[class*="st-key-metrik_satiri"] [data-testid="stMetricValue"] { font-size: 1.15rem !important; }
    div[class*="st-key-metrik_satiri"] [data-testid="stMetricLabel"] p { font-size: 0.75rem !important; }
    div[class*="st-key-metrik_satiri"] [data-testid="stColumn"] { padding: 8px 8px; }
    .ring-container { width: 150px; height: 150px; }
    .ring-inner { width: 116px; height: 116px; }
    .ring-val { font-size: 1.6rem; }
    .info-box { padding: 12px; font-size: 0.92rem; }
    .st-key-nova_sohbet [data-testid="stChatMessage"] { max-width: 96%; }
    .st-key-ust_bar [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: 0.6rem !important; }
    .st-key-ust_bar [data-testid="stColumn"] { min-width: 0 !important; flex: 1 1 calc(50% - 0.6rem) !important; }
    .st-key-ust_bar [data-testid="stColumn"]:first-child { flex: 1 1 100% !important; }
}
"""


def tema_css_uygula(tema):
    bg_url = GITHUB_KOK_URL + tema["bg_image"]
    # Açık zeminde vurgu renkleri koyulaştırılır ki okunabilsin
    renkler = ("#0b5fb8", "#c62828", "#1b7f3b") if tema.get("acik") else ("#5aaeff", "#ff6b61", "#4cd474")
    degiskenler = f"""
    :root {{
        --nv-text: {tema['text_color']};
        --nv-on-accent: {tema['fallback_bg']};
        --nv-bg: {tema['fallback_bg']};
        --nv-card: {tema['card_bg']};
        --nv-track: {tema['ring_track']};
        --nv-line: {tema['cizgi']};
        --nv-img: url("{bg_url}");
        --nv-mavi: {renkler[0]};
        --nv-kirmizi: {renkler[1]};
        --nv-yesil: {renkler[2]};
        --nv-golge: {"0 1px 10px rgba(255,255,255,0.9)" if tema.get("acik") else "0 2px 14px rgba(0,0,0,0.85)"};
    }}"""
    st.markdown(f"<style>{FONT_IMPORT}{degiskenler}{ORTAK_CSS}</style>", unsafe_allow_html=True)


GIRIS_CSS = """
:root { color-scheme: light; --nv-text: #1a1a1a; --nv-on-accent: #ffffff; --nv-line: rgba(0,0,0,0.12); --nv-track: rgba(0,0,0,0.05); }
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f0 100%) !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stMainBlockContainer"] { max-width: 560px; padding-top: 2rem; }
.nova-logo-giris { font-family: 'Playfair Display', serif; font-size: 5rem; letter-spacing: 25px; text-align: center; font-weight: 700; margin-top: 4vh; color: #1a1a1a !important; line-height: 1.1; }
.nova-slogan { text-align: center; color: #666666 !important; font-size: 1.05rem; letter-spacing: 5px; margin-bottom: 28px; }
[data-testid="stMain"] :is(p, label, span, small) { color: #333333 !important; font-family: 'Plus Jakarta Sans', sans-serif; }
.st-key-kart_giris { background: rgba(255, 255, 255, 0.95) !important; padding: 36px; border-radius: 28px; border: 1px solid rgba(0,0,0,0.08); box-shadow: 0 20px 40px rgba(0,0,0,0.08); }
button[data-baseweb="tab"] p { font-size: 1.05rem !important; font-weight: 700 !important; }
div.stButton > button { background: linear-gradient(180deg, #ffffff 0%, #f0f2f5) !important; font-weight: 700 !important; border-radius: 14px !important; width: 100%; padding: 12px; min-height: 46px; border: 1px solid rgba(0,0,0,0.12) !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: all 0.25s ease; }
div.stButton > button, div.stButton > button * { color: #1a1a1a !important; }
div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.1); border-color: rgba(0,0,0,0.25) !important; }
div[data-baseweb="input"] { border: 1px solid rgba(0,0,0,0.15) !important; border-radius: 12px !important; }
div[data-baseweb="input"], div[data-baseweb="input"] > div, div[data-baseweb="base-input"] { background-color: #ffffff !important; }
[data-testid="stMain"] input { color: #000000 !important; background-color: #ffffff !important; caret-color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-weight: 600 !important; }
div[data-baseweb="input"] button, div[data-baseweb="input"] button svg { color: #333333 !important; fill: #333333 !important; }
input:-webkit-autofill, input:-webkit-autofill:hover, input:-webkit-autofill:focus, input:-webkit-autofill:active { -webkit-box-shadow: 0 0 0 30px white inset !important; -webkit-text-fill-color: #000000 !important; transition: background-color 5000s ease-in-out 0s; }
[data-testid="stAlertContainer"] { background-color: #ffffff !important; border-radius: 12px !important; }
[data-testid="stAlertContainer"] * { color: #1a1a1a !important; font-weight: 600; }
@media (max-width: 640px) {
    [data-testid="stMainBlockContainer"] { padding: 1rem 0.8rem 2rem 0.8rem !important; }
    .nova-logo-giris { font-size: 2.9rem; letter-spacing: 12px; margin-top: 2vh; }
    .nova-slogan { font-size: 0.85rem; letter-spacing: 3px; margin-bottom: 18px; }
    .st-key-kart_giris { padding: 20px 16px; border-radius: 22px; }
}
"""


def grafik_temasi(grafik, tema):
    """Altair grafiklerinin eksen ve yazı renklerini temaya uydurur (her temada okunur)."""
    renk = tema["text_color"]
    return (grafik.configure(background="transparent")
            .configure_view(strokeWidth=0)
            .configure_axis(labelColor=renk, titleColor=renk, gridColor=tema["cizgi"], domainColor=tema["cizgi"], tickColor=tema["cizgi"], labelFontSize=12, titleFontSize=12)
            .configure_legend(labelColor=renk, titleColor=renk))


# ----------------------------------------------------
# GİRİŞ EKRANI
# ----------------------------------------------------
def giris_ekrani():
    st.markdown(f"<style>{FONT_IMPORT}{GIRIS_CSS}</style>", unsafe_allow_html=True)
    st.markdown('<div class="nova-logo-giris">N O V A</div>', unsafe_allow_html=True)
    st.markdown("<p class='nova-slogan'>ZARAFET VE DENGE</p>", unsafe_allow_html=True)
    veda = st.session_state.pop("_veda", None)
    if veda:
        st.success(veda)

    with kart("kart_giris"):
        tab_giris, tab_kayit = st.tabs(["Giriş Yap", "Kayıt Ol"])

        with tab_giris:
            g_user = st.text_input("Kullanıcı Adı", key="g_user").strip().lower()
            g_pass = st.text_input("Şifre", type="password", key="g_pass")
            if st.button("Giriş Yap", key="btn_giris", width="stretch"):
                baglandi, kayitli_hash = kullanici_hash_getir(g_user) if g_user else (True, None)
                dogru, eski_format = sifre_dogrula(g_pass, kayitli_hash)
                if not baglandi:
                    st.error("Sunucuya bağlanılamadı. Lütfen biraz sonra tekrar dene.")
                elif not dogru:
                    st.error("Hatalı kullanıcı adı veya şifre.")
                else:
                    veriler = verileri_yukle(g_user)
                    if veriler is None:
                        st.error("Verilerin yüklenemedi. Kayıtlarını korumak için giriş yapılmadı, lütfen tekrar dene.")
                    else:
                        if eski_format:
                            # Eski tuzsuz hash'i sessizce güvenli formata yükselt
                            try: supabase.table("kullanicilar").update({"password_hash": sifre_hashle(g_pass)}).eq("username", g_user).execute()
                            except Exception: pass
                        oturumu_baslat(g_user, veriler)
                        st.rerun()

        with tab_kayit:
            k_user = st.text_input("Yeni Kullanıcı Adı", key="k_user").strip().lower()
            k_pass = st.text_input("Şifre (En az 6 karakter ve bir büyük harf)", type="password", key="k_pass")
            k_pass2 = st.text_input("Şifre (Tekrar)", type="password", key="k_pass2")
            if st.button("Hesap Oluştur", key="btn_kayit", width="stretch"):
                hata = sifre_kontrol(k_pass)
                if not re.fullmatch(r"[a-z0-9_.]{3,30}", k_user):
                    st.error("Kullanıcı adı 3-30 karakter olmalı; yalnızca İngilizce harf, rakam, nokta ve alt çizgi içerebilir.")
                elif hata:
                    st.error(hata)
                elif k_pass != k_pass2:
                    st.error("Şifreler birbiriyle aynı değil.")
                else:
                    baglandi, mevcut = kullanici_hash_getir(k_user)
                    if not baglandi:
                        st.error("Sunucuya bağlanılamadı. Lütfen biraz sonra tekrar dene.")
                    elif mevcut is not None:
                        st.error("Bu kullanıcı adı zaten kullanımda.")
                    else:
                        try:
                            supabase.table("kullanicilar").insert({"username": k_user, "password_hash": sifre_hashle(k_pass)}).execute()
                        except Exception:
                            st.error("Hesap oluşturulamadı. Kullanıcı adı alınmış olabilir, lütfen tekrar dene.")
                        else:
                            # Yeni hesapla tekrar giriş yapmaya gerek kalmadan doğrudan uygulamaya geç
                            veriler = verileri_yukle(k_user)
                            if veriler is None:
                                st.success("Hesap oluşturuldu. Bağlantı sorunu nedeniyle otomatik giriş yapılamadı; Giriş Yap sekmesinden girebilirsin.")
                            else:
                                oturumu_baslat(k_user, veriler)
                                bildir("🎉 Hesabın oluşturuldu, Nova'ya hoş geldin!")
                                st.rerun()


# ----------------------------------------------------
# ONBOARDING (KURULUM) SÜRECİ
# ----------------------------------------------------
def adima_git(adim):
    st.session_state.onboarding_step = adim
    st.rerun()


def geri_ileri(geri_adim, ileri_etiketi="İleri ➔"):
    """Geri/İleri düğmelerini (telefonda da yan yana) çizer. İleri'ye basıldıysa True döndürür."""
    with st.container(key="gezinme"):
        b1, b2 = st.columns(2)
        if b1.button("⬅️ Geri", width="stretch"): adima_git(geri_adim)
        return b2.button(ileri_etiketi, width="stretch", type="primary")


def bilgi_kutusu(metin):
    st.markdown(f'<div class="info-box">ℹ️ {metin}</div>', unsafe_allow_html=True)


def baslik(metin):
    st.markdown(f"<h2 style='text-align:center;'>{metin}</h2>", unsafe_allow_html=True)


def onboarding(aktif_user, aktif_tema):
    p = st.session_state.profil
    ad_guvenli = guvenli(p.get("ad", ""))
    st.markdown('<div class="nova-header kucuk">N O V A</div>', unsafe_allow_html=True)
    bildirimleri_goster()

    with kart("kart_onboarding"):
        step = st.session_state.onboarding_step
        st.progress(min(step, 10) / 10, text=f"Adım {min(step, 10)} / 10")

        if step == 1:
            baslik("Tanıştığımıza memnun oldum,<br>Nova'ya Hoş Geldin! 🦢")
            st.markdown("<p style='text-align:center; opacity:0.9;'>Hedeflerine ulaşmanda sana yardımcı olmak için buradayız.<br>Başlamak için birkaç kısa sorumuz olacak.</p>", unsafe_allow_html=True)
            bilgi_kutusu("Cevapların, hedeflerini anlamamıza ve uygulamayı senin için kişiselleştirmemize yardımcı olacak.")
            if st.button("Başla ➔", width="stretch", type="primary"): adima_git(2)

        elif step == 2:
            baslik("Merhaba! Adın nedir?")
            ad_input = st.text_input("Adını Gir", value=p.get("ad", ""), max_chars=40).strip()
            bilgi_kutusu("Nova uygulamasını sana özel hale getirmek ve sana hitap edebilmek için adını kullanacağız.")
            if geri_ileri(1):
                if ad_input:
                    p["ad"] = ad_input
                    adima_git(3)
                else: st.error("Lütfen adını gir.")

        elif step == 3:
            baslik(f"Nova'yı Hangi Amaçla Kullanmak İstiyorsun {ad_guvenli}?")
            kayitli = [a for a in p.get("amaclar", []) if a in AMAC_SECENEKLERI]
            amaclar = st.multiselect("Hedeflerin (Birden fazla seçebilirsin)", AMAC_SECENEKLERI, default=kayitli)
            if geri_ileri(2):
                p["amaclar"] = amaclar
                adima_git(4)

        elif step == 4:
            baslik("Cinsiyetin nedir?")
            secenekler = ["Kadın", "Erkek"]
            cinsiyet = st.selectbox("Seçimini yap:", secenekler, index=secenekler.index(p["cinsiyet"]) if p.get("cinsiyet") in secenekler else 0)
            bilgi_kutusu("Cinsiyetin, vücudunun günlük enerji ihtiyacını hesaplamamızı doğrudan etkiler.")
            if geri_ileri(3):
                p["cinsiyet"] = cinsiyet
                adima_git(5)

        elif step == 5:
            baslik("Doğum yılın ne?")
            mevcut_yil = bugun().year
            dogum_yili = st.number_input("Yıl", min_value=1920, max_value=mevcut_yil - 10, value=sinirla(int(p.get("dogum_yili", 2000)), 1920, mevcut_yil - 10))
            st.markdown(f"<h4 style='text-align:center;'>Şu an <b>{mevcut_yil - dogum_yili}</b> yaşındasın.</h4>", unsafe_allow_html=True)
            bilgi_kutusu("Yaşın, vücudunun her gün ne kadar enerjiye (BMR) ihtiyaç duyduğunu etkiler.")
            if geri_ileri(4):
                p["dogum_yili"] = int(dogum_yili)
                adima_git(6)

        elif step == 6:
            baslik("Boyun kaç?")
            boy = st.number_input("Boy (cm)", min_value=130, max_value=220, value=sinirla(int(p.get("boy", 165)), 130, 220))
            bilgi_kutusu("Boyun, vücudunun her gün ne kadar enerji harcadığını etkiler.")
            if geri_ileri(5):
                p["boy"] = int(boy)
                adima_git(7)

        elif step == 7:
            baslik("Şu andaki kilon ne?")
            mevcut_kilo = st.number_input("Kilo (kg)", min_value=35.0, max_value=250.0, value=sinirla(float(p.get("mevcut_kilo", 60.0)), 35.0, 250.0), step=0.5)
            bilgi_kutusu("Bu bilgi, bulunduğun noktaya göre kalori hedefini hesaplamamıza yardımcı olur. İleride Gelişim sekmesinden her zaman güncelleyebilirsin.")
            if geri_ileri(6):
                p["mevcut_kilo"] = float(mevcut_kilo)
                adima_git(8)

        elif step == 8:
            baslik("Günlük hayatın ne kadar hareketli?")
            duzeyler = list(AKTIVITE_DUZEYLERI.keys())
            kayitli = p.get("aktivite_duzeyi", VARSAYILAN_AKTIVITE)
            duzey = st.selectbox("Aktivite düzeyin:", duzeyler, index=duzeyler.index(kayitli) if kayitli in duzeyler else 1)
            bilgi_kutusu("Günlük harcadığın enerjiyi amacına göre değil, gerçekte ne kadar hareket ettiğine göre hesaplıyoruz.")
            if geri_ileri(7):
                p["aktivite_duzeyi"] = duzey
                adima_git(9)

        elif step == 9:
            baslik("Hedef kilon nedir?")
            hedef_kilo = st.number_input("Hedef Kilo (kg)", min_value=35.0, max_value=250.0, value=sinirla(float(p.get("hedef_kilo", 55.0)), 35.0, 250.0), step=0.5)
            hedef_sure = st.number_input("Hedefe Ulaşma Süresi (Ay)", min_value=1, max_value=60, value=sinirla(int(p.get("hedef_sure_ay", 2)), 1, 60))
            temalar = list(TEMA_AYARLARI.keys())
            sec_tema = st.selectbox("Nova Deneyimin İçin Bir Tema Seç", temalar, index=temalar.index(aktif_tema))
            if geri_ileri(8, "Hesapla ➔"):
                p.update({"hedef_kilo": float(hedef_kilo), "hedef_sure_ay": int(hedef_sure), "tema": sec_tema})
                adima_git(10)

        elif step == 10:
            baslik(f"Paylaştığın için teşekkürler, {ad_guvenli} 🎉")
            st.markdown("<p style='text-align:center; font-size:1.1rem; opacity:0.9;'>Bize söylediklerin, seni nasıl destekleyeceğimizi şekillendirmemize yardımcı olacak.</p>", unsafe_allow_html=True)
            bmr, tdee, gunluk_acik, hedef_kalori = hesapla_bmr_ve_hedef(p)
            st.markdown(f"""
            <div class="sonuc-kutu">
                <h3 style="text-align:center; margin-bottom: 20px;">İşte Kişisel Kalori Hedefin</h3>
                <p><b>Amacın:</b> {guvenli(', '.join(p.get('amaclar') or ['Belirtilmedi']))}</p>
                <p><b>Dinlenik Metabolizman (BMR):</b> {round(bmr)} kcal</p>
                <p><b>Tahmini Günlük Harcaman:</b> {round(tdee)} kcal</p>
                <hr class="nova-cizgi">
                <h2 style="text-align:center;">Günlük Hedefin: {round(hedef_kalori)} kcal</h2>
            </div><br>
            """, unsafe_allow_html=True)
            if abs(gunluk_acik) >= MAKS_GUNLUK_FARK:
                st.warning("Seçtiğin süre bu hedef için çok kısa. Sağlıklı sınırda kalmak için günlük fark 1000 kcal ile sınırlandırıldı; hedefe ulaşman planladığından uzun sürebilir.")
            if yas_hesapla(p) < 18:
                st.warning("18 yaşından küçüksün. Kalori kısıtlaması büyüme çağında sakıncalı olabilir; bu hedefi uygulamadan önce bir doktora veya diyetisyene danış.")

            if geri_ileri(9, "🚀 Başla!"):
                p["setup_tamamlandi"] = True

                # Bugünün tartı kaydını güncel kiloyla ekle ya da güncelle
                tarih_str = str(bugun())
                kayit = next((k for k in st.session_state.kilo_gecmisi if k.get("Tarih") == tarih_str), None)
                if kayit: kayit["Kilo"] = float(p["mevcut_kilo"])
                else: st.session_state.kilo_gecmisi.append({"Tarih": tarih_str, "Kilo": float(p["mevcut_kilo"])})
                st.session_state.kilo_gecmisi.sort(key=lambda x: x["Tarih"])

                verileri_kaydet(aktif_user)
                st.rerun()


# ----------------------------------------------------
# ANA EKRAN: ORTAK PARÇALAR
# ----------------------------------------------------
def aktivite_kaydi(tarih):
    """Yalnızca yazarken kayıt oluşturur; bir tarihe bakmak boş kayıt üretmez."""
    return st.session_state.aktivite_loglari.setdefault(tarih, {"adim": 0, "su": 0.0, "egzersiz_kalori": 0})


def gunun_kayitlari(tarih):
    return [k for k in st.session_state.gunluk_kayitlar if k.get("Tarih") == tarih]


def toplamlar(kayitlar):
    return {
        "kcal": sum(k.get("Kalori", 0) for k in kayitlar),
        "p": sum(k.get("Protein", 0) for k in kayitlar),
        "k": sum(k.get("Karbonhidrat", 0) for k in kayitlar),
        "y": sum(k.get("Yağ", 0) for k in kayitlar),
    }


def render_makro(isim, mevcut, hedef, renk):
    yuzde = min((mevcut / max(hedef, 1)) * 100, 100)
    return f"""
    <div style="margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; font-size: 0.95rem; margin-bottom: 5px; font-weight: 600;">
            <span>{isim}</span><span>{round(mevcut)}g / {round(hedef)}g</span>
        </div>
        <div class="makro-iz"><div style="width: {yuzde}%; background-color: {renk}; height: 100%; border-radius: 4px;"></div></div>
    </div>
    """


def gunluge_ekle(aktif_user, tarih, ogun, ad, kcal, protein, karb, yag, gram=None):
    kayit = {"Tarih": tarih, "Öğün": ogun, "Tarif": ad, "Kalori": round(kcal), "Protein": round(protein, 1), "Karbonhidrat": round(karb, 1), "Yağ": round(yag, 1)}
    if gram: kayit["Gram"] = int(gram)
    st.session_state.gunluk_kayitlar.append(kayit)
    return verileri_kaydet(aktif_user)


def son_eklenenler(limit=8):
    """Tüm geçmişten en son eklenen benzersiz yemekler (FatSecret'taki 'Son Yenenler' gibi)."""
    gorulen, sonuc = set(), []
    for k in reversed(st.session_state.gunluk_kayitlar):
        ad = k.get("Tarif")
        if ad and ad not in gorulen:
            gorulen.add(ad)
            sonuc.append(k)
        if len(sonuc) >= limit:
            break
    return sonuc


# ----------------------------------------------------
# 1. SEKME: GÜNLÜK
# ----------------------------------------------------
def kart_kalori_ozeti(p, tema, secilen_tarih):
    okunan = st.session_state.aktivite_loglari.get(secilen_tarih, {})
    t = toplamlar(gunun_kayitlari(secilen_tarih))
    _, _, _, hedef = hesapla_bmr_ve_hedef(p)
    _, taban_adim = aktivite_bilgisi(p)
    egz = gunun_egzersiz_kalorisi(okunan)
    adim_kcal = adim_kalorisi(p, okunan.get("adim", 0))
    kalan = hedef - t["kcal"] + adim_kcal + egz

    with kart("kart_kalori"):
        st.markdown("<h2 class='kart-baslik'>🎯 Kalori ve Denge</h2>", unsafe_allow_html=True)
        st.markdown(f"""
        <table class="nova-tablo">
            <tr><td>🎯 Günlük hedef</td><td class="sag mavi"><b>{round(hedef)} kcal</b></td></tr>
            <tr><td>🍽️ Yediklerin</td><td class="sag kirmizi"><b>− {round(t['kcal'])} kcal</b></td></tr>
            <tr><td>👟 Ekstra adımlar</td><td class="sag yesil"><b>+ {round(adim_kcal)} kcal</b></td></tr>
            <tr><td>🏃‍♀️ Egzersizler</td><td class="sag yesil"><b>+ {round(egz)} kcal</b></td></tr>
            <tr class="toplam-satir">
                <td>⚖️ Kalan</td>
                <td class="sag">{round(kalan)} kcal</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        st.caption(f"Aktivite düzeyin günde yaklaşık {taban_adim} adımı zaten içeriyor; yalnızca bunun üzerindeki adımlar ek kalori sayılır.")
        if kalan < 0: st.error(f"⚠️ Limitini {abs(round(kalan))} kcal aştın.")
        else: st.success(f"✅ Harika gidiyorsun! {round(kalan)} kcal yeme hakkın duruyor.")

        st.markdown("<h4>Makrolar</h4>", unsafe_allow_html=True)
        st.markdown(render_makro("🥩 Protein", t["p"], hedef * 0.3 / 4, "#ff5a4f"), unsafe_allow_html=True)
        st.markdown(render_makro("🍞 Karbonhidrat", t["k"], hedef * 0.4 / 4, "#3b9cff"), unsafe_allow_html=True)
        st.markdown(render_makro("🥑 Yağ", t["y"], hedef * 0.3 / 9, "#ffcc00"), unsafe_allow_html=True)

        # Kalorinin makrolara dağılımı (FatSecret'taki yüzde dağılım gibi)
        makro_kcal = {"Protein": t["p"] * 4, "Karbonhidrat": t["k"] * 4, "Yağ": t["y"] * 9}
        toplam = sum(makro_kcal.values())
        if toplam > 0:
            yuzde = {ad: round(v / toplam * 100) for ad, v in makro_kcal.items()}
            st.markdown(f"""
            <div class="dagilim">
                <div style="width:{yuzde['Protein']}%; background:#ff5a4f;"></div>
                <div style="width:{yuzde['Karbonhidrat']}%; background:#3b9cff;"></div>
                <div style="width:{yuzde['Yağ']}%; background:#ffcc00;"></div>
            </div>""", unsafe_allow_html=True)
            st.caption(f"Kalorinin dağılımı: Protein %{yuzde['Protein']} · Karbonhidrat %{yuzde['Karbonhidrat']} · Yağ %{yuzde['Yağ']}  (önerilen: %30 · %40 · %30)")


def kart_yemek_gunlugu(aktif_user, secilen_tarih):
    """FatSecret tarzı günlük: her öğün başlığında toplam kalori, altında yemekler."""
    with kart("kart_gunluk"):
        st.markdown("<h2 class='kart-baslik'>🍽️ Yemek Günlüğün</h2>", unsafe_allow_html=True)
        with st.container(key="ogun_listesi"):
            for ogun_turu in OGUNLER:
                ogun_yemekleri = [(i, k) for i, k in enumerate(st.session_state.gunluk_kayitlar) if k.get("Tarih") == secilen_tarih and k.get("Öğün") == ogun_turu]
                t = toplamlar([k for _, k in ogun_yemekleri])
                st.markdown(f"<div class='ogun-baslik'><span>{OGUN_IKONLARI[ogun_turu]} {ogun_turu}</span><span class='ogun-kcal'>{round(t['kcal'])} kcal</span></div>", unsafe_allow_html=True)
                if not ogun_yemekleri:
                    st.caption("Henüz bir şey eklemedin.")
                    continue
                for i, k in ogun_yemekleri:
                    c1, c2 = st.columns([10, 1], vertical_alignment="center")
                    gram = f" · {k['Gram']} g" if k.get("Gram") else ""
                    c1.markdown(
                        f"<div class='ogun-satir'><b>{guvenli(k.get('Tarif', '?'))}</b>{gram} — {round(k.get('Kalori', 0))} kcal<br>"
                        f"<small>P {k.get('Protein', 0):g} g · K {k.get('Karbonhidrat', 0):g} g · Y {k.get('Yağ', 0):g} g</small></div>",
                        unsafe_allow_html=True)
                    if c2.button("🗑️", key=f"sil_{i}", help="Sil"):
                        st.session_state.gunluk_kayitlar.pop(i)
                        verileri_kaydet(aktif_user)
                        st.rerun()


def kart_yemek_ekle(aktif_user, secilen_tarih, df_yemek):
    with kart("kart_yemek"):
        st.markdown("<h2 class='kart-baslik'>➕ Yemek Ekle</h2>", unsafe_allow_html=True)
        secilen_ogun = st.selectbox("Hangi öğüne eklensin?", OGUNLER, key="db_ogun")

        # Son eklenenlerden tek dokunuşla tekrar ekleme
        sonlar = son_eklenenler()
        if sonlar:
            with st.expander("⏱️ Son eklediklerinden hızlıca ekle"):
                secim = st.selectbox("Yemek", range(len(sonlar)), key="son_yemek",
                                     format_func=lambda i: f"{sonlar[i].get('Tarif', '?')} — {round(sonlar[i].get('Kalori', 0))} kcal")
                if st.button("➕ Tekrar Ekle", width="stretch", key="btn_tekrar_ekle"):
                    k = sonlar[secim]
                    if gunluge_ekle(aktif_user, secilen_tarih, secilen_ogun, k.get("Tarif", "?"), k.get("Kalori", 0), k.get("Protein", 0), k.get("Karbonhidrat", 0), k.get("Yağ", 0), k.get("Gram")):
                        bildir(f"✅ {k.get('Tarif', 'Yemek')} {secilen_ogun.lower()} öğününe eklendi.")
                    st.rerun()

        kart_ozel_yemek_olustur(aktif_user)

        ozel = ozel_yemek_tablosu()
        if df_yemek is None:
            st.warning("Yemek veritabanı şu anda yüklenemedi. Biraz sonra sayfayı yenileyip tekrar dene.")
            if ozel.empty:
                return
            tablo = ozel
        else:
            tablo = df_yemek if ozel.empty else pd.concat([ozel, df_yemek], ignore_index=True)

        arama_metni = st.text_input("🔍 Yemek ara", placeholder="Örn: Tavuk, Yumurta, Pilav...").strip()
        isimler = tablo["Yemek Adı"].dropna().astype(str)
        if arama_metni:
            isimler = isimler[isimler.map(tr_kucuk).str.contains(tr_kucuk(arama_metni), regex=False)]
        yemek_isimleri = isimler.tolist()

        if not yemek_isimleri:
            st.warning("Bu kelimeyle eşleşen yemek bulunamadı.")
            return

        secilen_yemek = st.selectbox(f"Sonuçlar ({len(yemek_isimleri)})", yemek_isimleri, key="db_yemek")
        detay = tablo[tablo["Yemek Adı"] == secilen_yemek].iloc[0]
        ozel_mi = secilen_yemek.startswith(OZEL_ON_EK)
        varsayilan_porsiyon = int(detay["Porsiyon_g"]) if ozel_mi and pd.notna(detay.get("Porsiyon_g")) else 100
        sayilar = pd.to_numeric(detay[["Protein (g)", "Karbonhidrat (g)", "Yağ (g)"]], errors="coerce").fillna(0.0)
        base_p, base_c, base_f = (float(v) for v in sayilar)

        st.caption(f"100 g için: Protein {base_p} g · Karbonhidrat {base_c} g · Yağ {base_f} g")
        porsiyon_g = st.number_input("Porsiyon (gram)", min_value=10, max_value=2000, value=sinirla(varsayilan_porsiyon, 10, 2000), step=10)
        carp = porsiyon_g / 100.0
        deger_p, deger_c, deger_f = round(base_p * carp, 1), round(base_c * carp, 1), round(base_f * carp, 1)

        with st.expander("🛠️ İçeriği kendine göre ayarla (isteğe bağlı)"):
            # Üst sınır porsiyonla birlikte büyür; büyük porsiyonlarda slider taşmaz
            new_p = st.slider("Protein (g)", 0.0, max(150.0, float(round(deger_p * 1.5))), deger_p, 0.1)
            new_c = st.slider("Karbonhidrat (g)", 0.0, max(300.0, float(round(deger_c * 1.5))), deger_c, 0.1)
            new_f = st.slider("Yağ (g)", 0.0, max(150.0, float(round(deger_f * 1.5))), deger_f, 0.1)

        new_kcal = round((new_p * 4) + (new_c * 4) + (new_f * 9))
        st.info(f"🔥 Hesaplanan kalori: **{new_kcal} kcal**")

        if st.button("➕ Günlüğe Ekle", width="stretch", type="primary", key="btn_gunluge_ekle"):
            ad = secilen_yemek[len(OZEL_ON_EK):] if ozel_mi else secilen_yemek
            if gunluge_ekle(aktif_user, secilen_tarih, secilen_ogun, ad, new_kcal, new_p, new_c, new_f, porsiyon_g):
                bildir(f"✅ {ad} günlüğüne eklendi.")
            st.rerun()


OZEL_ON_EK = "⭐ "


def ozel_yemek_tablosu():
    """Kullanıcının kendi eklediği yemekler; aramada en üstte ⭐ ile görünür."""
    satirlar = [{"Yemek Adı": OZEL_ON_EK + y["ad"], "Protein (g)": y.get("protein", 0), "Karbonhidrat (g)": y.get("karb", 0),
                 "Yağ (g)": y.get("yag", 0), "Porsiyon_g": y.get("porsiyon", 100)} for y in st.session_state.get("ozel_yemekler", [])]
    return pd.DataFrame(satirlar, columns=["Yemek Adı", "Protein (g)", "Karbonhidrat (g)", "Yağ (g)", "Porsiyon_g"])


def kart_ozel_yemek_olustur(aktif_user):
    ozeller = st.session_state.setdefault("ozel_yemekler", [])
    with st.expander(f"⭐ Kendi yemeğini oluştur ({len(ozeller)} kayıtlı)"):
        st.caption("Veritabanında bulamadığın bir yemeği ya da ürünü paketindeki 100 g değerleriyle kaydet. Aramada ⭐ ile en üstte çıkar.")
        with st.form("ozel_yemek_formu", clear_on_submit=True, border=False):
            ad = st.text_input("Yemek adı", max_chars=60, placeholder="Örn: Annemin kısırı")
            o1, o2, o3 = st.columns(3)
            protein = o1.number_input("Protein (g)", min_value=0.0, max_value=100.0, value=0.0, step=0.5, help="100 g'daki miktar")
            karb = o2.number_input("Karb. (g)", min_value=0.0, max_value=100.0, value=0.0, step=0.5, help="100 g'daki miktar")
            yag = o3.number_input("Yağ (g)", min_value=0.0, max_value=100.0, value=0.0, step=0.5, help="100 g'daki miktar")
            porsiyon = st.number_input("Her zamanki porsiyonun (gram)", min_value=10, max_value=2000, value=100, step=10)
            kaydet = st.form_submit_button("⭐ Yemeği Kaydet", width="stretch")
        if kaydet:
            ad = ad.strip()
            if not ad:
                st.error("Yemeğe bir ad ver.")
            elif any(tr_kucuk(y["ad"]) == tr_kucuk(ad) for y in ozeller):
                st.error("Bu adla kayıtlı bir yemeğin zaten var.")
            elif protein + karb + yag > 100:
                st.error("100 g'daki protein, karbonhidrat ve yağın toplamı 100 g'ı geçemez.")
            elif protein + karb + yag == 0:
                st.error("En az bir besin değeri gir.")
            else:
                ozeller.append({"ad": ad, "protein": round(protein, 1), "karb": round(karb, 1), "yag": round(yag, 1), "porsiyon": int(porsiyon)})
                if verileri_kaydet(aktif_user):
                    kcal100 = round(protein * 4 + karb * 4 + yag * 9)
                    bildir(f"⭐ {ad} kaydedildi ({kcal100} kcal / 100 g). Artık aramada en üstte çıkacak.")
                st.rerun()

        if ozeller:
            st.markdown("<hr class='nova-cizgi'>", unsafe_allow_html=True)
            with st.container(key="ozel_liste"):
                for i, y in enumerate(ozeller):
                    c1, c2 = st.columns([10, 1], vertical_alignment="center")
                    kcal100 = round(y.get("protein", 0) * 4 + y.get("karb", 0) * 4 + y.get("yag", 0) * 9)
                    c1.markdown(f"<div class='ogun-satir'><b>{guvenli(y['ad'])}</b> — {kcal100} kcal / 100 g<br>"
                                f"<small>P {y.get('protein', 0):g} g · K {y.get('karb', 0):g} g · Y {y.get('yag', 0):g} g · porsiyon {y.get('porsiyon', 100)} g</small></div>",
                                unsafe_allow_html=True)
                    if c2.button("🗑️", key=f"ozel_sil_{i}", help="Sil"):
                        ozeller.pop(i)
                        verileri_kaydet(aktif_user)
                        st.rerun()


def kart_hareket(aktif_user, p, tema, secilen_tarih):
    okunan = st.session_state.aktivite_loglari.get(secilen_tarih, {})
    adim = okunan.get("adim", 0)
    su = okunan.get("su", 0.0)

    with kart("kart_halkalar"):
        st.markdown("<h2 class='kart-baslik' style='text-align:center;'>💧 Adım ve Su</h2>", unsafe_allow_html=True)
        adim_yuzde = min(adim / 10000 * 100, 100)
        su_yuzde = min(su / 2.5 * 100, 100)
        hc1, hc2 = st.columns(2)
        with hc1:
            st.markdown(f"""
                <div class="ring-container" style="background: conic-gradient(#ff5a4f {adim_yuzde}%, {tema['ring_track']} 0deg);">
                    <div class="ring-inner">
                        <div class="ring-val kirmizi">{adim}</div>
                        <div class="ring-lbl">ADIM</div>
                    </div>
                </div><br>
            """, unsafe_allow_html=True)
            yeni_adim = st.number_input("Eklenecek adım", value=0, step=1000, help="Yanlış girişi düzeltmek için eksi değer girebilirsin.")
            if st.button("🔴 Adımı Kaydet", width="stretch"):
                kayit = aktivite_kaydi(secilen_tarih)
                kayit["adim"] = max(0, int(kayit.get("adim", 0) + yeni_adim))
                verileri_kaydet(aktif_user)
                st.rerun()
        with hc2:
            st.markdown(f"""
                <div class="ring-container" style="background: conic-gradient(#3b9cff {su_yuzde}%, {tema['ring_track']} 0deg);">
                    <div class="ring-inner">
                        <div class="ring-val mavi">{su:.2f}</div>
                        <div class="ring-lbl">LİTRE</div>
                    </div>
                </div><br>
            """, unsafe_allow_html=True)
            su_secim = st.number_input("Eklenecek su (litre)", value=0.25, step=0.25, help="Yanlış girişi düzeltmek için eksi değer girebilirsin.")
            if st.button("🔵 Suyu Kaydet", width="stretch"):
                kayit = aktivite_kaydi(secilen_tarih)
                kayit["su"] = max(0.0, round(kayit.get("su", 0.0) + su_secim, 2))
                verileri_kaydet(aktif_user)
                st.rerun()

    # FatSecret tarzı egzersiz günlüğü: aktivite + süre -> kalori
    with kart("kart_egzersiz"):
        st.markdown("<h2 class='kart-baslik'>🏃‍♀️ Egzersiz Günlüğü</h2>", unsafe_allow_html=True)
        kilo = float(p.get("mevcut_kilo", 60.0))
        e1, e2 = st.columns([2, 1])
        tur = e1.selectbox("Aktivite", list(EGZERSIZ_MET), key="egz_tur")
        dakika = e2.number_input("Süre (dk)", min_value=5, max_value=300, value=30, step=5, key="egz_dk")
        tahmin = egzersiz_kalorisi(EGZERSIZ_MET[tur], dakika, kilo)
        st.caption(f"Tahmini net harcama: **{round(tahmin)} kcal** ({kilo:g} kg için)")
        if st.button("➕ Egzersizi Ekle", width="stretch", key="btn_egz_ekle"):
            kayit = aktivite_kaydi(secilen_tarih)
            kayit.setdefault("egzersizler", []).append({"ad": tur, "dk": int(dakika), "kcal": round(tahmin)})
            if verileri_kaydet(aktif_user): bildir(f"✅ {tur} ({dakika} dk) eklendi: +{round(tahmin)} kcal")
            st.rerun()

        egzersizler = okunan.get("egzersizler", [])
        ai_kcal = okunan.get("egzersiz_kalori", 0)
        if egzersizler or ai_kcal:
            st.markdown("<hr class='nova-cizgi'>", unsafe_allow_html=True)
            with st.container(key="egzersiz_listesi"):
                if ai_kcal:
                    st.markdown(f"<div class='ogun-satir'><b>🤖 AI Koç antrenmanı</b> — {round(ai_kcal)} kcal</div>", unsafe_allow_html=True)
                for i, e in enumerate(egzersizler):
                    c1, c2 = st.columns([10, 1], vertical_alignment="center")
                    c1.markdown(f"<div class='ogun-satir'><b>{guvenli(e.get('ad', '?'))}</b> · {e.get('dk', 0)} dk — {round(e.get('kcal', 0))} kcal</div>", unsafe_allow_html=True)
                    if c2.button("🗑️", key=f"egz_sil_{i}", help="Sil"):
                        aktivite_kaydi(secilen_tarih)["egzersizler"].pop(i)
                        verileri_kaydet(aktif_user)
                        st.rerun()


def sekme_gunluk(aktif_user, p, tema, secilen_tarih, df_yemek):
    kart_kalori_ozeti(p, tema, secilen_tarih)
    kart_yemek_gunlugu(aktif_user, secilen_tarih)
    kart_yemek_ekle(aktif_user, secilen_tarih, df_yemek)
    kart_hareket(aktif_user, p, tema, secilen_tarih)


# ----------------------------------------------------
# 2. SEKME: GELİŞİM (KİLO, EĞİLİM, RAPOR, HESAP)
# ----------------------------------------------------
DONEMLER = {"7 gün": 7, "30 gün": 30, "90 gün": 90, "Tümü": None}
AYLAR_KISA = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
AYLAR_UZUN = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def sayi(x, basamak=1, isaret=False):
    """Türkçe ondalık gösterim: 0.4 -> 0,4"""
    metin = f"{x:+.{basamak}f}" if isaret else f"{x:.{basamak}f}"
    return metin.replace(".", ",").replace("-", "−")


def kilo_egilimi(gecmis, hedef_kilo, gun_sayisi=28):
    """Son ~4 haftadaki tartılara doğru bir çizgi oturtur; haftalık değişimi ve hedefe ulaşma tarihini tahmin eder."""
    if len(gecmis) < 3:
        return {"durum": "az_veri"}
    df = pd.DataFrame(gecmis)
    df["Tarih"] = pd.to_datetime(df["Tarih"])
    df = df.sort_values("Tarih")
    son_tarih = df["Tarih"].max()
    pencere = df[df["Tarih"] >= son_tarih - pd.Timedelta(days=gun_sayisi)]
    if len(pencere) < 3 or (pencere["Tarih"].max() - pencere["Tarih"].min()).days < 7:
        return {"durum": "az_veri"}

    x = (pencere["Tarih"] - pencere["Tarih"].min()).dt.days.to_numpy(dtype=float)
    egim, kesisim = np.polyfit(x, pencere["Kilo"].to_numpy(dtype=float), 1)  # kg / gün
    simdi = kesisim + egim * x.max()
    sonuc = {"haftalik": egim * 7, "simdi": simdi,
             "hizli": abs(egim * 7) > 0.01 * simdi}  # haftada vücut ağırlığının %1'inden hızlı
    fark = hedef_kilo - simdi
    if abs(fark) <= 0.5:
        sonuc["durum"] = "hedefte"
    elif abs(egim) < 0.005:
        sonuc["durum"] = "sabit"
    elif (fark > 0) != (egim > 0):
        sonuc["durum"] = "uzaklasiyor"
    else:
        gun = fark / egim
        if gun > 730:
            sonuc["durum"] = "cok_uzun"
        else:
            sonuc["durum"] = "tahmin"
            sonuc["tarih"] = son_tarih.date() + datetime.timedelta(days=int(np.ceil(gun)))
    return sonuc


def egilim_mesaji(e):
    durum = e["durum"]
    if durum == "az_veri":
        st.caption("📅 Hedef tarihi tahmini için son 4 hafta içinde, aralarında en az 1 hafta olan en az 3 tartı gerekiyor.")
        return
    haftalik = f"haftada {sayi(e['haftalik'], isaret=True)} kg"
    if durum == "hedefte":
        st.success("🎉 Hedef kilona ulaştın! İstersen Ayarlar'dan yeni bir hedef belirleyebilirsin.")
    elif durum == "sabit":
        st.info(f"⚖️ Kilon son haftalarda sabit ({haftalik}). Bu hızla hedefe ulaşma tarihi hesaplanamıyor.")
    elif durum == "uzaklasiyor":
        st.warning(f"↩️ Son haftalarda hedefinden uzaklaşıyorsun ({haftalik}).")
    elif durum == "cok_uzun":
        st.info(f"🐢 Bu hızla ({haftalik}) hedefe ulaşman 2 yıldan uzun sürer.")
    else:
        t = e["tarih"]
        st.success(f"📅 Bu hızla ({haftalik}) hedefine yaklaşık **{t.day} {AYLAR_UZUN[t.month - 1]} {t.year}** tarihinde ulaşırsın.")
    if e.get("hizli"):
        st.warning("⚠️ Kilon haftada vücut ağırlığının %1'inden hızlı değişiyor. Sağlıklı bir hız için bir uzmana danışmanı öneririz.")


def donem_baslangici(gun_sayisi):
    if gun_sayisi:
        return bugun() - datetime.timedelta(days=gun_sayisi - 1)
    tarihler = [k.get("Tarih") for k in st.session_state.gunluk_kayitlar] + [k.get("Tarih") for k in st.session_state.kilo_gecmisi]
    tarihler = [t for t in tarihler if t]
    ilk = datetime.date.fromisoformat(min(tarihler)) if tarihler else bugun()
    return max(ilk, bugun() - datetime.timedelta(days=364))  # en fazla 1 yıl


def kart_kilo(aktif_user, p, tema, baslangic):
    bugun_dt = bugun()
    with kart("kart_kilo"):
        st.markdown("<h2 class='kart-baslik'>⚖️ Kilo Takibi</h2>", unsafe_allow_html=True)
        st.markdown("İstediğin gün için kilonu gir; kalori hedefin en güncel tartına göre otomatik hesaplanır.")

        k_col1, k_col2 = st.columns(2)
        with k_col1:
            kilo_tarihi = st.date_input("Tartım tarihi", bugun_dt, max_value=bugun_dt, key="kilo_tarih_giris", format="DD.MM.YYYY")
        with k_col2:
            yeni_kilo = st.number_input("Kilon (kg)", min_value=30.0, max_value=250.0, value=sinirla(float(p.get("mevcut_kilo", 60.0)), 30.0, 250.0), step=0.1)

        if st.button("⚖️ Kilomu Kaydet", width="stretch", type="primary"):
            tarih_metin = str(kilo_tarihi)
            kayit = next((k for k in st.session_state.kilo_gecmisi if k.get("Tarih") == tarih_metin), None)
            if kayit: kayit["Kilo"] = float(yeni_kilo)
            else: st.session_state.kilo_gecmisi.append({"Tarih": tarih_metin, "Kilo": float(yeni_kilo)})

            st.session_state.kilo_gecmisi.sort(key=lambda x: x["Tarih"])
            # Güncel kilo, girilen değer değil en yeni tarihli tartıdır (geçmişe kayıt girmek profili bozmaz)
            p["mevcut_kilo"] = float(st.session_state.kilo_gecmisi[-1]["Kilo"])
            if verileri_kaydet(aktif_user):
                bildir("🎉 Kilon kaydedildi! Kalori hedefin en güncel tartına göre hesaplanıyor.")
            st.rerun()

        gecmis = st.session_state.kilo_gecmisi
        if not gecmis:
            return
        ilk, son = gecmis[0]["Kilo"], gecmis[-1]["Kilo"]
        hedef_kilo = float(p.get("hedef_kilo", son))
        g1, g2, g3 = st.container(key="metrik_satiri_kilo").columns(3)
        g1.metric("Güncel", f"{son:g} kg", f"{son - ilk:+.1f} kg", delta_color="off")
        g2.metric("Hedef", f"{hedef_kilo:g} kg")
        g3.metric("Kalan", f"{abs(son - hedef_kilo):.1f} kg")

        egilim_mesaji(kilo_egilimi(gecmis, hedef_kilo))

        # Tartılar ve 7 günlük ortalama (günlük su/tuz dalgalanmaları yanıltmasın diye)
        df_kilo = pd.DataFrame(gecmis)
        df_kilo["Tarih"] = pd.to_datetime(df_kilo["Tarih"])
        df_kilo = df_kilo.sort_values("Tarih").set_index("Tarih")
        df_kilo["Ortalama"] = df_kilo["Kilo"].rolling("7D").mean().round(1)
        df_kilo = df_kilo.reset_index()
        gorunen = df_kilo[df_kilo["Tarih"] >= pd.Timestamp(baslangic)]
        if gorunen.empty:
            gorunen = df_kilo.tail(1)

        noktalar = alt.Chart(gorunen).mark_circle(size=55, color="#3b9cff", opacity=0.55).encode(
            x=alt.X("Tarih:T", title=None, axis=alt.Axis(format="%d.%m", labelOverlap=True)),
            y=alt.Y("Kilo:Q", title="kg", scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip("Tarih:T", format="%d.%m.%Y", title="Tarih"), alt.Tooltip("Kilo:Q", title="Tartı")],
        )
        ortalama = alt.Chart(gorunen).mark_line(color="#3b9cff", strokeWidth=3).encode(
            x="Tarih:T", y="Ortalama:Q", tooltip=[alt.Tooltip("Tarih:T", format="%d.%m.%Y", title="Tarih"), alt.Tooltip("Ortalama:Q", title="7 günlük ort.")])
        hedef_cizgisi = alt.Chart(pd.DataFrame({"hedef": [hedef_kilo]})).mark_rule(strokeDash=[6, 4], color=tema["text_color"]).encode(y="hedef:Q")
        st.altair_chart(grafik_temasi((noktalar + ortalama + hedef_cizgisi).properties(height=260), tema), use_container_width=True)
        st.caption("Noktalar tartıların, çizgi 7 günlük ortalaman, kesikli çizgi hedefin.")


def kart_rapor(p, tema, baslangic, donem_adi):
    """FatSecret'taki rapor ekranı gibi: seçilen dönemde günlük kalori, hedefle birlikte."""
    _, _, _, hedef = hesapla_bmr_ve_hedef(p)
    gun_sayisi = (bugun() - baslangic).days + 1
    satirlar = []
    for i in range(gun_sayisi):
        gun = baslangic + datetime.timedelta(days=i)
        t = toplamlar(gunun_kayitlari(str(gun)))
        akt = st.session_state.aktivite_loglari.get(str(gun), {})
        satirlar.append({"Tarih": pd.Timestamp(gun), "Kalori": round(t["kcal"]), "Su": akt.get("su", 0.0), "Adım": akt.get("adim", 0)})
    df = pd.DataFrame(satirlar)
    girilen = df[df["Kalori"] > 0]

    with kart("kart_rapor"):
        st.markdown(f"<h2 class='kart-baslik'>📊 Rapor · {donem_adi}</h2>", unsafe_allow_html=True)
        m1, m2, m3 = st.container(key="metrik_satiri_rapor").columns(3)
        m1.metric("Ort. kalori", f"{round(girilen['Kalori'].mean()) if len(girilen) else 0} kcal")
        m2.metric("Hedefte gün", f"{int((girilen['Kalori'] <= hedef).sum())} / {len(girilen)}")
        m3.metric("Ort. su", f"{sayi(df['Su'].mean())} L")

        if girilen.empty:
            st.info("Bu dönemde henüz yemek kaydın yok.")
            return

        # Uzun dönemlerde günlük çubuklar okunmaz; haftalık ortalamaya geçilir
        haftalik = gun_sayisi > 45
        if haftalik:
            grafik_df = girilen.set_index("Tarih").resample("W-MON", label="left", closed="left")["Kalori"].mean().dropna().round().reset_index()
            baslik_x = "Hafta"
        else:
            grafik_df = df.copy()
            baslik_x = None
        grafik_df["Durum"] = np.where(grafik_df["Kalori"] > hedef, "Hedefi aştı", "Hedef içinde")

        etiket = "%d.%m" if gun_sayisi > 7 else "%a %d"
        cubuklar = alt.Chart(grafik_df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("yearmonthdate(Tarih):O" if not haftalik else "Tarih:T", title=baslik_x,
                    axis=alt.Axis(format=etiket, labelAngle=0 if gun_sayisi <= 14 else -45, labelOverlap=True)),
            y=alt.Y("Kalori:Q", title="kcal" + (" (haftalık ort.)" if haftalik else "")),
            color=alt.Color("Durum:N", scale=alt.Scale(domain=["Hedef içinde", "Hedefi aştı"], range=["#34c759", "#ff5a4f"]), legend=alt.Legend(orient="bottom", title=None)),
            tooltip=[alt.Tooltip("Tarih:T", format="%d.%m.%Y", title="Hafta başı" if haftalik else "Gün"), alt.Tooltip("Kalori:Q", title="kcal")],
        )
        hedef_cizgisi = alt.Chart(pd.DataFrame({"hedef": [hedef]})).mark_rule(strokeDash=[6, 4], color=tema["text_color"], strokeWidth=2).encode(y="hedef:Q")
        st.altair_chart(grafik_temasi((cubuklar + hedef_cizgisi).properties(height=260), tema), use_container_width=True)
        st.caption(f"Kesikli çizgi günlük hedefin: {round(hedef)} kcal. Kayıt girilmeyen günler ortalamaya katılmaz."
                   + (" Uzun dönemde çubuklar haftalık ortalamayı gösterir." if haftalik else ""))


def hesabi_sil(username):
    """Kullanıcının tüm kayıtlarını siler. Önce veriler, en son giriş bilgisi silinir."""
    try:
        supabase.table("kullanici_verileri").delete().eq("username", username).execute()
        try:
            supabase.table("ai_kullanim").delete().eq("kullanici", f"user:{username}").execute()
        except Exception:
            pass  # sayaç tablosu yoksa sorun değil
        supabase.table("kullanicilar").delete().eq("username", username).execute()
        return True
    except Exception:
        return False


def kart_hesap(aktif_user):
    with kart("kart_hesap"):
        st.markdown("<h2 class='kart-baslik'>👤 Hesap ve Veriler</h2>", unsafe_allow_html=True)
        st.markdown("Yemek geçmişini Excel uyumlu CSV olarak indirip doktorunla veya diyetisyeninle paylaşabilirsin. Tüm verilerinin bir kopyasını da JSON olarak alabilirsin.")
        if st.session_state.gunluk_kayitlar:
            # utf-8-sig: Excel'in Türkçe karakterleri doğru göstermesi için
            csv_data = pd.DataFrame(st.session_state.gunluk_kayitlar).to_csv(index=False).encode("utf-8-sig")
            st.download_button(label="🍽️ Yemek Günlüğünü İndir (.CSV)", data=csv_data, file_name=f"nova_yemek_gunlugu_{aktif_user}.csv", mime="text/csv", width="stretch")
        tum_veri = {
            "kullanici": aktif_user, "indirme_tarihi": str(bugun()), "profil": st.session_state.profil,
            "gunluk_kayitlar": st.session_state.gunluk_kayitlar, "aktivite_loglari": st.session_state.aktivite_loglari,
            "kilo_gecmisi": st.session_state.kilo_gecmisi, "ozel_yemekler": st.session_state.get("ozel_yemekler", []),
        }
        st.download_button(label="🗂️ Tüm Verilerimi İndir (.JSON)", data=json.dumps(tum_veri, ensure_ascii=False, indent=2).encode("utf-8"),
                           file_name=f"nova_verilerim_{aktif_user}.json", mime="application/json", width="stretch")

        with st.expander("🗑️ Hesabımı sil"):
            st.warning("Bu işlem geri alınamaz. Profilin, tüm günlük kayıtların, kilo geçmişin ve kendi yemeklerin kalıcı olarak silinir. Silmeden önce yukarıdan verilerini indirebilirsin.")
            sifre = st.text_input("Onaylamak için şifreni gir", type="password", key="sil_sifre")
            onay = st.checkbox("Hesabımın ve tüm verilerimin kalıcı olarak silineceğini anlıyorum.", key="sil_onay")
            if st.button("Hesabımı kalıcı olarak sil", key="btn_hesap_sil", disabled=not onay, width="stretch"):
                baglandi, kayitli_hash = kullanici_hash_getir(aktif_user)
                dogru, _ = sifre_dogrula(sifre, kayitli_hash)
                if not baglandi:
                    st.error("Sunucuya bağlanılamadı. Hesabın silinmedi, lütfen tekrar dene.")
                elif not dogru:
                    st.error("Şifre yanlış. Hesabın silinmedi.")
                elif hesabi_sil(aktif_user):
                    cikis_yap("Hesabın ve tüm verilerin kalıcı olarak silindi. Nova'yı kullandığın için teşekkürler.")
                else:
                    st.error("Silme sırasında bir sorun oluştu. Lütfen tekrar dene.")


def sekme_gelisim(aktif_user, p, tema):
    with st.container(key="donem_secici"):
        donem_adi = st.radio("Dönem", list(DONEMLER), index=1, key="donem", horizontal=True, label_visibility="collapsed")
    baslangic = donem_baslangici(DONEMLER[donem_adi])
    kart_kilo(aktif_user, p, tema, baslangic)
    kart_rapor(p, tema, baslangic, donem_adi)
    kart_hesap(aktif_user)


# ----------------------------------------------------
# AI SEKMELERİ
# ----------------------------------------------------
def sekme_ai_ogun(aktif_user, secilen_tarih):
    with kart("kart_ai_ogun"):
        secilen_ogun_ai = st.selectbox("Hangi öğün için tarama yapıyorsun?", OGUNLER, key="ai_ogun_sec")
        totals = meal_scan_page()
        if totals:
            for item in totals["items"]:
                st.session_state.gunluk_kayitlar.append({
                    "Tarih": secilen_tarih, "Öğün": secilen_ogun_ai, "Tarif": f"🤖 {item['Yemek']}",
                    "Kalori": round(float(item["Kalori"])), "Protein": float(item["Protein (g)"]),
                    "Karbonhidrat": float(item["Karb. (g)"]), "Yağ": float(item["Yağ (g)"]), "Gram": int(item.get("Gram", 0)) or None,
                })
            if verileri_kaydet(aktif_user): bildir(f"✅ {totals['kcal']} kcal başarıyla günlüğüne eklendi!")
            st.rerun()


def sekme_ai_koc(aktif_user, secilen_tarih):
    with kart("kart_ai_koc"):
        log = coach_page()
        if log:
            kayit = aktivite_kaydi(secilen_tarih)
            kayit["egzersiz_kalori"] = kayit.get("egzersiz_kalori", 0) + 250
            if verileri_kaydet(aktif_user): bildir("🤖 Harika! AI Antrenmanını tamamladın, günlüğüne 250 kcal harcama eklendi.")
            st.rerun()


def sekme_ai_asistan():
    with kart("kart_ai_asistan"):
        ask_page()


# ----------------------------------------------------
# ANA EKRAN
# ----------------------------------------------------
def cikis_yap(mesaj=None):
    for anahtar in list(st.session_state.keys()):
        del st.session_state[anahtar]
    if mesaj:
        st.session_state["_veda"] = mesaj
    st.rerun()


def ana_ekran(aktif_user, tema):
    p = st.session_state.profil
    gosterilecek_isim = guvenli(p.get("ad") or aktif_user)
    st.markdown('<div class="nova-header">N O V A</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="nova-user">{gosterilecek_isim}</div>', unsafe_allow_html=True)

    aylar_tr = {1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"}
    gunler_tr = {0: "Pazartesi", 1: "Salı", 2: "Çarşamba", 3: "Perşembe", 4: "Cuma", 5: "Cumartesi", 6: "Pazar"}
    bugun_dt = bugun()
    tarih_str = f"{bugun_dt.day} {aylar_tr[bugun_dt.month]} {bugun_dt.year} {gunler_tr[bugun_dt.weekday()]}"
    st.markdown(f'<div class="nova-tarih">📅 {tarih_str}</div>', unsafe_allow_html=True)

    with st.container(key="ust_bar"):
        t_col1, t_col2, t_col3 = st.columns([6, 2, 2], vertical_alignment="bottom")
        with t_col1:
            secilen_tarih = str(st.date_input("🗓️ Gün seç", bugun_dt, max_value=bugun_dt, format="DD.MM.YYYY"))
        with t_col2:
            if st.button("⚙️ Ayarlar", width="stretch"):
                p["setup_tamamlandi"] = False
                st.session_state.onboarding_step = 2
                st.rerun()
        with t_col3:
            if st.button("🚪 Çıkış", width="stretch"):
                cikis_yap()

    bildirimleri_goster()
    df_yemek = yemek_veritabanini_yukle()

    tab_gunluk, tab_gelisim, tab_ai_ogun, tab_ai_koc, tab_ai_asistan = st.tabs(["📊 Günlük", "📈 Gelişim", "📸 AI Öğün", "🏋️ AI Koç", "💬 Asistan"])
    with tab_gunluk: sekme_gunluk(aktif_user, p, tema, secilen_tarih, df_yemek)
    with tab_gelisim: sekme_gelisim(aktif_user, p, tema)
    with tab_ai_ogun: sekme_ai_ogun(aktif_user, secilen_tarih)
    with tab_ai_koc: sekme_ai_koc(aktif_user, secilen_tarih)
    with tab_ai_asistan: sekme_ai_asistan()


# ----------------------------------------------------
# YÖNLENDİRME
# ----------------------------------------------------
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "aktif_kullanici" not in st.session_state: st.session_state.aktif_kullanici = ""
if "onboarding_step" not in st.session_state: st.session_state.onboarding_step = 1

if not st.session_state.giris_yapildi:
    giris_ekrani()
else:
    aktif_user = st.session_state.aktif_kullanici
    aktif_tema = st.session_state.profil.get("tema", "Koyu Cam")
    if aktif_tema not in TEMA_AYARLARI: aktif_tema = "Koyu Cam"
    tema = TEMA_AYARLARI[aktif_tema]
    tema_css_uygula(tema)

    if not st.session_state.profil.get("setup_tamamlandi", False):
        onboarding(aktif_user, aktif_tema)
    else:
        ana_ekran(aktif_user, tema)
