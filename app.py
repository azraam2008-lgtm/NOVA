import datetime
import hashlib
import hmac
import html
import os
import re
from pathlib import Path

import pandas as pd
import streamlit as st
from supabase import create_client, Client

# --- AI MODÜLLERİ ---
from meal_scan import meal_scan_page
from nova_pages import coach_page, ask_page

st.set_page_config(page_title="Nova — Diyet ve Aktivite Asistanı", page_icon="🦢", layout="wide", initial_sidebar_state="collapsed")

# --- SUPABASE BAĞLANTI AYARLARI ---
# NOT: Bu anahtar herkese açıktır. Tabloların güvenliği Supabase tarafında RLS ile sağlanmalıdır.
SUPABASE_URL = "https://klncgexnykfwzpcrijrt.supabase.co"
SUPABASE_KEY = "sb_publishable_yXcnmg2uJsA7vR0DXnWUWQ_06Jm4E8e"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----------------------------------------------------
# SABİTLER
# ----------------------------------------------------
TEMA_AYARLARI = {
    "Yakut Kızılı": {"bg_image": "tema_kirmizi.jpg", "fallback_bg": "#2A0808", "text_color": "#ffffff", "card_bg": "rgba(35, 5, 10, 0.85)", "ring_track": "rgba(255,255,255,0.15)", "cizgi": "rgba(255,255,255,0.2)"},
    "Turkuaz Ferahlığı": {"bg_image": "tema_turkuaz.jpg", "fallback_bg": "#E0F2F1", "text_color": "#004d40", "card_bg": "rgba(230, 250, 245, 0.95)", "ring_track": "rgba(0,0,0,0.1)", "cizgi": "rgba(0,0,0,0.15)"},
    "Altın Zarafet": {"bg_image": "tema_altin.jpg", "fallback_bg": "#3e2723", "text_color": "#ffffff", "card_bg": "rgba(40, 25, 20, 0.85)", "ring_track": "rgba(255,255,255,0.15)", "cizgi": "rgba(255,255,255,0.2)"},
    "Bordo Kadife": {"bg_image": "tema_bordo.jpg", "fallback_bg": "#310000", "text_color": "#ffebee", "card_bg": "rgba(45, 0, 15, 0.90)", "ring_track": "rgba(255,255,255,0.15)", "cizgi": "rgba(255,255,255,0.2)"},
    "Derin Mavi": {"bg_image": "tema_mavi.jpg", "fallback_bg": "#00102A", "text_color": "#e3f2fd", "card_bg": "rgba(0, 15, 45, 0.90)", "ring_track": "rgba(255,255,255,0.15)", "cizgi": "rgba(255,255,255,0.2)"},
    "Koyu Cam": {"bg_image": "tema_siyah.jpg", "fallback_bg": "#0f0f0f", "text_color": "#ffffff", "card_bg": "rgba(20, 20, 20, 0.90)", "ring_track": "rgba(255,255,255,0.15)", "cizgi": "rgba(255,255,255,0.2)"},
}

AMAC_SECENEKLERI = ["Kilo vermek istiyorum", "Kilomu korumak istiyorum", "Kilo almak istiyorum", "Kas kazanmak istiyorum", "Sağlıklı beslenmek istiyorum"]
OGUNLER = ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"]

# Aktivite düzeyi -> (BMR çarpanı, bu düzeyin zaten içerdiği günlük adım)
AKTIVITE_DUZEYLERI = {
    "Hareketsiz (masa başı, spor yok)": (1.2, 3000),
    "Hafif aktif (haftada 1-3 gün hareket)": (1.375, 5000),
    "Orta aktif (haftada 3-5 gün spor)": (1.55, 7500),
    "Çok aktif (haftada 6-7 gün spor)": (1.725, 10000),
}
VARSAYILAN_AKTIVITE = "Hafif aktif (haftada 1-3 gün hareket)"

VARSAYILAN_PROFIL = {
    "ad": "", "cinsiyet": "Kadın", "dogum_yili": 2000, "boy": 165, "mevcut_kilo": 60.0, "hedef_kilo": 55.0,
    "hedef_sure_ay": 2, "tema": "Koyu Cam", "amaclar": [], "aktivite_duzeyi": VARSAYILAN_AKTIVITE, "setup_tamamlandi": False,
}

MAKS_GUNLUK_FARK = 1000  # kcal; haftada yaklaşık 1 kg'dan hızlı değişim hedeflenmez
YEMEK_CSV_ADI = "cok_daha_kapsamli_yemek_veritabani.csv"
YEMEK_CSV_URL = f"https://raw.githubusercontent.com/azraam2008-lgtm/NOVA/main/{YEMEK_CSV_ADI}"
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
    try:
        return st.container(key=anahtar)
    except TypeError:  # çok eski Streamlit sürümleri
        return st.container()


# ----------------------------------------------------
# YEMEK VERİTABANI
# ----------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def _yemek_csv_indir():
    # Hata fırlatırsa önbelleğe alınmaz; bir sonraki çalıştırmada yeniden denenir.
    return pd.read_csv(YEMEK_CSV_URL)


def yemek_veritabanini_yukle():
    try:
        return _yemek_csv_indir()
    except Exception:
        pass
    try:
        return pd.read_csv(Path(__file__).parent / YEMEK_CSV_ADI)
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
        "profil": {**VARSAYILAN_PROFIL, **(d.get("profil") or {})},
    }


def verileri_kaydet(username):
    data = {"gunluk_kayitlar": st.session_state.gunluk_kayitlar, "aktivite_loglari": st.session_state.aktivite_loglari, "kilo_gecmisi": st.session_state.kilo_gecmisi, "profil": st.session_state.profil}
    try:
        supabase.table("kullanici_verileri").upsert({"username": username, "data": data}).execute()
        return True
    except Exception:
        st.session_state["_hata"] = "⚠️ Son değişiklik buluta kaydedilemedi. İnternet bağlantını kontrol edip tekrar dene."
        return False


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


# ----------------------------------------------------
# GİRİŞ EKRANI
# ----------------------------------------------------
def giris_ekrani():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        :root { color-scheme: light !important; }
        [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f0 100%) !important; color-scheme: light !important; }
        .nova-logo-giris { font-family: 'Playfair Display', serif; font-size: 5rem; letter-spacing: 25px; text-align: center; font-weight: 700; margin-top: 5vh; color: #1a1a1a !important;}
        p, label, span { color: #333333 !important; font-family: 'Plus Jakarta Sans', sans-serif; }
        .st-key-kart_giris { background: rgba(255, 255, 255, 0.95) !important; padding: 40px; border-radius: 28px; border: 1px solid rgba(0,0,0,0.08); box-shadow: 0 20px 40px rgba(0,0,0,0.08); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); }
        div.stButton > button:first-child { background: linear-gradient(180deg, #ffffff 0%, #f0f2f5) !important; color: #1a1a1a !important; font-weight: 700 !important; border-radius: 14px !important; width: 100%; padding: 12px; border: 1px solid rgba(0,0,0,0.12) !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); }
        div.stButton > button:first-child:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.1); background: linear-gradient(180deg, #ffffff 0%, #e2e6eb) !important; border-color: rgba(0,0,0,0.2) !important; }
        .stTextInput > div > div > div, div[data-baseweb="input"] > div, div[data-baseweb="input"] > div:focus-within { background-color: #ffffff !important; border-radius: 12px !important; border: 1px solid rgba(0,0,0,0.15) !important; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important; }
        .stTextInput input, .stTextInput input:focus, .stTextInput input:active, input, input:focus, input:active { color: #000000 !important; background-color: #ffffff !important; caret-color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-weight: 600 !important; }
        input:-webkit-autofill, input:-webkit-autofill:hover, input:-webkit-autofill:focus, input:-webkit-autofill:active { -webkit-box-shadow: 0 0 0 30px white inset !important; -webkit-text-fill-color: #000000 !important; transition: background-color 5000s ease-in-out 0s; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nova-logo-giris">N O V A</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666666 !important; font-size: 1.1rem; letter-spacing: 5px; margin-bottom: 30px;'>ZARAFET VE DENGE</p>", unsafe_allow_html=True)

    _, c2, _ = st.columns([1, 1.5, 1])
    with c2, kart("kart_giris"):
        tab_giris, tab_kayit = st.tabs(["Giriş Yap", "Kayıt Ol"])

        with tab_giris:
            g_user = st.text_input("Kullanıcı Adı", key="g_user").strip().lower()
            g_pass = st.text_input("Şifre", type="password", key="g_pass")
            if st.button("Giriş Yap", key="btn_giris"):
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
                        st.session_state.giris_yapildi = True
                        st.session_state.aktif_kullanici = g_user
                        st.session_state.onboarding_step = 1
                        for anahtar, deger in veriler.items():
                            st.session_state[anahtar] = deger
                        st.rerun()

        with tab_kayit:
            k_user = st.text_input("Yeni Kullanıcı Adı", key="k_user").strip().lower()
            k_pass = st.text_input("Şifre (En az 6 karakter ve bir büyük harf)", type="password", key="k_pass")
            k_pass2 = st.text_input("Şifre (Tekrar)", type="password", key="k_pass2")
            if st.button("Hesap Oluştur", key="btn_kayit"):
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
                            st.success("Hesap oluşturuldu, giriş yapabilirsiniz.")
                        except Exception:
                            st.error("Hesap oluşturulamadı. Kullanıcı adı alınmış olabilir, lütfen tekrar dene.")


# ----------------------------------------------------
# TEMA CSS
# ----------------------------------------------------
def tema_css_uygula(tema):
    bg_url = f"https://raw.githubusercontent.com/azraam2008-lgtm/NOVA/main/{tema['bg_image']}"
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        :root {{ color-scheme: light !important; }}
        [data-testid="stAppViewContainer"] {{ background-color: {tema['fallback_bg']} !important; background-image: url("{bg_url}") !important; background-size: cover; background-position: center; background-attachment: fixed; }}
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0) !important; }}

        .nova-header {{ color: {tema['text_color']} !important; font-family: 'Playfair Display', serif; font-size: 5rem; letter-spacing: 20px; text-align: center; font-weight: 700; margin-top: -20px; }}
        .nova-user {{ color: {tema['text_color']} !important; text-align: center; font-size: 1.4rem; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 5px; opacity: 0.9; font-weight: 600; }}
        .nova-tarih {{ color: {tema['text_color']} !important; text-align: center; font-size: 1rem; letter-spacing: 2px; margin-bottom: 35px; opacity: 0.7; }}

        /* Kartlar: st.container(key="kart_...") ile oluşturulur, içindeki bileşenleri gerçekten sarar */
        div[class*="st-key-kart_"] {{ background: {tema['card_bg']} !important; padding: 35px; border-radius: 28px; backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px); margin-bottom: 30px; border: 1px solid {tema['cizgi']}; box-shadow: 0 15px 50px rgba(0,0,0,0.4); }}
        .info-box {{ background: {tema['ring_track']} !important; border-left: 4px solid {tema['text_color']} !important; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: {tema['text_color']} !important; font-weight: 600; }}
        .sonuc-kutu {{ background: {tema['ring_track']}; padding: 25px; border-radius: 15px; margin-top: 20px; }}
        hr.nova-cizgi {{ border: none; border-top: 1px solid {tema['cizgi']}; margin: 25px 0; }}

        div[class*="st-key-kart_"] p, div[class*="st-key-kart_"] h1, div[class*="st-key-kart_"] h2, div[class*="st-key-kart_"] h3, div[class*="st-key-kart_"] h4,
        div[class*="st-key-kart_"] td, div[class*="st-key-kart_"] th, div[class*="st-key-kart_"] span, div[class*="st-key-kart_"] label,
        div[data-testid="stMarkdownContainer"] p, div[data-testid="stMarkdownContainer"] h2,
        div[data-testid="stMarkdownContainer"] h3, div[data-testid="stMarkdownContainer"] h4,
        div[data-testid="stWidgetLabel"] p, label[data-baseweb="radio"] div,
        div[data-testid="stMetricValue"], div[data-testid="stMetricLabel"] {{ color: {tema['text_color']} !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }}

        div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, input[type="text"], input[type="number"], textarea {{ background-color: #ffffff !important; color: #000000 !important; border-radius: 12px !important; border: 2px solid rgba(0,0,0,0.15) !important; }}
        div[data-baseweb="select"] span, input, input::placeholder {{ color: #000000 !important; font-weight: bold; }}
        div[data-baseweb="popover"], ul[role="listbox"], ul[role="listbox"] li, ul[role="listbox"] span {{ background-color: #ffffff !important; color: #000000 !important; }}
        span[data-baseweb="tag"] {{ background-color: {tema['text_color']} !important; color: {tema['fallback_bg']} !important; }}
        span[data-baseweb="tag"] span {{ color: {tema['fallback_bg']} !important; }}
        div[data-baseweb="input"] button {{ color: #000000 !important; }}

        /* Sekme tasarımı */
        div[data-testid="stTabs"] > div > div[role="tablist"] {{
            background: {tema['card_bg']} !important;
            padding: 10px !important;
            border-radius: 24px !important;
            gap: 25px !important;
            border: 1px solid {tema['cizgi']} !important;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1) !important;
            margin-bottom: 25px !important;
            display: flex;
            justify-content: center;
        }}
        button[data-baseweb="tab"] {{
            background-color: transparent !important;
            color: {tema['text_color']} !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            padding: 12px 30px !important;
            margin: 0 5px !important;
            border-radius: 18px !important;
            border: none !important;
            opacity: 0.70;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        }}
        button[data-baseweb="tab"]:hover {{
            opacity: 1 !important;
            background-color: {tema['ring_track']} !important;
            transform: translateY(-1px);
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            background-color: {tema['text_color']} !important;
            color: {tema['fallback_bg']} !important;
            font-weight: 800 !important;
            opacity: 1.0 !important;
            box-shadow: 0 6px 15px rgba(0,0,0,0.15) !important;
            transform: translateY(0);
        }}
        button[data-baseweb="tab"][aria-selected="true"] p {{ color: {tema['fallback_bg']} !important; }}
        div[data-baseweb="tab-highlight"] {{ display: none !important; }}

        div.stButton > button:first-child {{ background: {tema['card_bg']} !important; color: {tema['text_color']} !important; border: 1px solid {tema['cizgi']} !important; font-weight: 700 !important; border-radius: 16px !important; padding: 10px 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.2); backdrop-filter: blur(10px); transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); }}
        div.stButton > button:first-child:hover {{ transform: translateY(-2px); background: {tema['text_color']} !important; color: {tema['fallback_bg']} !important; border-color: {tema['text_color']} !important; box-shadow: 0 12px 30px rgba(0,0,0,0.3); }}
        div.stButton > button:first-child:hover p {{ color: {tema['fallback_bg']} !important; }}

        .ring-container {{ width: 180px; height: 180px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; }}
        .ring-inner {{ width: 140px; height: 140px; border-radius: 50%; background: {tema['card_bg']} !important; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
        .ring-val {{ font-size: 2rem; font-weight: 800; margin-bottom: -5px; color: {tema['text_color']} !important; }}
        .ring-lbl {{ font-size: 1rem; opacity: 0.8; text-transform: uppercase; letter-spacing: 2px; color: {tema['text_color']} !important; }}
        table {{ width: 100%; font-size: 1.1rem; background: transparent; border-collapse: collapse; }}
        th, td {{ padding: 12px; border-bottom: 1px solid {tema['cizgi']}; text-align: left; color: {tema['text_color']} !important; }}
        th {{ font-weight: 800; font-size: 1.2rem; opacity: 0.9; }}
        </style>
    """, unsafe_allow_html=True)


# ----------------------------------------------------
# ONBOARDING (KURULUM) SÜRECİ
# ----------------------------------------------------
def adima_git(adim):
    st.session_state.onboarding_step = adim
    st.rerun()


def geri_ileri(geri_adim, ileri_etiketi="İleri ➔"):
    """Geri/İleri düğmelerini çizer. Geri'ye basılırsa o adıma döner; İleri'ye basıldıysa True döndürür."""
    b1, b2 = st.columns(2)
    if b1.button("⬅️ Geri"): adima_git(geri_adim)
    return b2.button(ileri_etiketi)


def bilgi_kutusu(metin):
    st.markdown(f'<div class="info-box">ℹ️ {metin}</div>', unsafe_allow_html=True)


def baslik(metin):
    st.markdown(f"<h2 style='text-align:center;'>{metin}</h2>", unsafe_allow_html=True)


def onboarding(aktif_user, aktif_tema):
    p = st.session_state.profil
    ad_guvenli = html.escape(p.get("ad", ""))
    st.markdown('<div class="nova-header" style="font-size:3.5rem; margin-top:20px;">N O V A</div>', unsafe_allow_html=True)

    with kart("kart_onboarding"):
        step = st.session_state.onboarding_step

        if step == 1:
            baslik("Tanıştığımıza memnun oldum,<br>Nova'ya Hoş Geldin! 🦢")
            st.markdown("<p style='text-align:center; opacity:0.9;'>Hedeflerine ulaşmanda sana yardımcı olmak için buradayız.<br>Başlamak için birkaç kısa sorumuz olacak.</p>", unsafe_allow_html=True)
            bilgi_kutusu("Cevapların, hedeflerini anlamamıza ve uygulamayı senin için kişiselleştirmemize yardımcı olacak.")
            if st.button("Başla ➔", width="stretch"): adima_git(2)

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
            bilgi_kutusu("Bu bilgi, bulunduğun noktaya göre kalori hedefini hesaplamamıza yardımcı olur. İleride kilo sekmesinden her zaman güncelleyebilirsin.")
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
            if geri_ileri(8, "Kalori Hedefimi Hesapla ➔"):
                p.update({"hedef_kilo": float(hedef_kilo), "hedef_sure_ay": int(hedef_sure), "tema": sec_tema})
                adima_git(10)

        elif step == 10:
            baslik(f"Paylaştığın için teşekkürler, {ad_guvenli} 🎉")
            st.markdown("<p style='text-align:center; font-size:1.2rem; opacity:0.9;'>Bize söylediklerin, seni nasıl destekleyeceğimizi şekillendirmemize yardımcı olacak.</p>", unsafe_allow_html=True)
            bmr, tdee, gunluk_acik, hedef_kalori = hesapla_bmr_ve_hedef(p)
            st.markdown(f"""
            <div class="sonuc-kutu">
                <h3 style="text-align:center; margin-bottom: 20px;">İşte Kişisel Kalori Hedefin</h3>
                <p><b>Amacın:</b> {html.escape(', '.join(p.get('amaclar') or ['Belirtilmedi']))}</p>
                <p><b>Dinlenik Metabolizman (BMR):</b> {round(bmr)} kcal</p>
                <p><b>Tahmini Günlük Harcaman:</b> {round(tdee)} kcal</p>
                <hr class="nova-cizgi">
                <h2 style="color: #007aff !important; text-align:center;">Günlük Hedefin: {round(hedef_kalori)} kcal</h2>
            </div><br>
            """, unsafe_allow_html=True)
            if abs(gunluk_acik) >= MAKS_GUNLUK_FARK:
                st.warning("Seçtiğin süre bu hedef için çok kısa. Sağlıklı sınırda kalmak için günlük fark 1000 kcal ile sınırlandırıldı; hedefe ulaşman planladığından uzun sürebilir.")
            if yas_hesapla(p) < 18:
                st.warning("18 yaşından küçüksün. Kalori kısıtlaması büyüme çağında sakıncalı olabilir; bu hedefi uygulamadan önce bir doktora veya diyetisyene danış.")

            if geri_ileri(9, "🚀 Harika, Uygulamaya Başla!"):
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
# ANA EKRAN SEKMELERİ
# ----------------------------------------------------
def aktivite_kaydi(tarih):
    """Yalnızca yazarken kayıt oluşturur; bir tarihe bakmak boş kayıt üretmez."""
    return st.session_state.aktivite_loglari.setdefault(tarih, {"adim": 0, "su": 0.0, "egzersiz_kalori": 0})


def render_makro(isim, mevcut, hedef, renk, iz_rengi):
    yuzde = min((mevcut / max(hedef, 1)) * 100, 100)
    return f"""
    <div style="margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; font-size: 0.95rem; margin-bottom: 5px;">
            <span>{isim}</span><span>{round(mevcut)}g / {round(hedef)}g</span>
        </div>
        <div style="width: 100%; background-color: {iz_rengi}; border-radius: 4px; height: 6px;">
            <div style="width: {yuzde}%; background-color: {renk}; height: 100%; border-radius: 4px;"></div>
        </div>
    </div>
    """


def sekme_ozet(aktif_user, p, tema, secilen_tarih, df_yemek):
    okunan = st.session_state.aktivite_loglari.get(secilen_tarih, {})
    adim = okunan.get("adim", 0)
    su = okunan.get("su", 0.0)
    egzersiz_kalori = okunan.get("egzersiz_kalori", 0)

    # --- HALKALAR ---
    with kart("kart_halkalar"):
        st.markdown("<h2 style='text-align:center; font-size: 2rem; margin-bottom: 25px;'>Günlük Aktivite ve Su Halkaları</h2>", unsafe_allow_html=True)
        adim_yuzde = min(adim / 10000 * 100, 100)
        su_yuzde = min(su / 2.5 * 100, 100)
        hc1, hc2 = st.columns(2)
        with hc1:
            st.markdown(f"""
                <div class="ring-container" style="background: conic-gradient(#ff3b30 {adim_yuzde}%, {tema['ring_track']} 0deg);">
                    <div class="ring-inner">
                        <div class="ring-val" style="color:#ff3b30 !important;">{adim}</div>
                        <div class="ring-lbl">ADIM</div>
                    </div>
                </div><br>
            """, unsafe_allow_html=True)
            yeni_adim = st.number_input("Eklenecek Adım:", value=0, step=1000, help="Yanlış girişi düzeltmek için eksi değer girebilirsin.")
            if st.button("🔴 Adımı Kaydet", width="stretch"):
                kayit = aktivite_kaydi(secilen_tarih)
                kayit["adim"] = max(0, int(kayit.get("adim", 0) + yeni_adim))
                verileri_kaydet(aktif_user)
                st.rerun()
        with hc2:
            st.markdown(f"""
                <div class="ring-container" style="background: conic-gradient(#007aff {su_yuzde}%, {tema['ring_track']} 0deg);">
                    <div class="ring-inner">
                        <div class="ring-val" style="color:#007aff !important;">{su:.2f}</div>
                        <div class="ring-lbl">LİTRE</div>
                    </div>
                </div><br>
            """, unsafe_allow_html=True)
            su_secim = st.number_input("Eklenecek Su (Litre):", value=0.25, step=0.25, help="Yanlış girişi düzeltmek için eksi değer girebilirsin.")
            if st.button("🔵 Suyu Kaydet", width="stretch"):
                kayit = aktivite_kaydi(secilen_tarih)
                kayit["su"] = max(0.0, round(kayit.get("su", 0.0) + su_secim, 2))
                verileri_kaydet(aktif_user)
                st.rerun()

    # --- KALORİ TABLOSU ---
    with kart("kart_kalori"):
        st.markdown("<h2 style='font-size: 2rem;'>Kalori ve Denge Tablosu</h2>", unsafe_allow_html=True)

        bugun_og = [k for k in st.session_state.gunluk_kayitlar if k.get("Tarih") == secilen_tarih]
        top_kalori = sum(k.get("Kalori", 0) for k in bugun_og)
        top_pro = sum(k.get("Protein", 0) for k in bugun_og)
        top_karb = sum(k.get("Karbonhidrat", 0) for k in bugun_og)
        top_yag = sum(k.get("Yağ", 0) for k in bugun_og)

        _, _, _, hedef_kalori_alim = hesapla_bmr_ve_hedef(p)
        _, taban_adim = aktivite_bilgisi(p)
        aktif_harcanan = adim_kalorisi(p, adim) + egzersiz_kalori
        kalan_kalori = hedef_kalori_alim - top_kalori + aktif_harcanan

        hedef_pro = (hedef_kalori_alim * 0.3) / 4
        hedef_karb = (hedef_kalori_alim * 0.4) / 4
        hedef_yag = (hedef_kalori_alim * 0.3) / 9

        st.markdown(f"""
        <table>
            <tr><th>Metrik</th><th style="text-align: right;">Değer</th></tr>
            <tr><td>🎯 Günlük Hedef Kalori Bütçen</td><td style="text-align: right; color: #007aff !important;"><b>{round(hedef_kalori_alim)} kcal</b></td></tr>
            <tr><td>🍽️ Bugüne Kadar Yediklerin</td><td style="text-align: right; color: #ff3b30 !important;"><b>- {round(top_kalori)} kcal</b></td></tr>
            <tr><td>🏃‍♀️ Ekstra Hareket ve Egzersizle Kazandıkların</td><td style="text-align: right; color: #34c759 !important;"><b>+ {round(aktif_harcanan)} kcal</b></td></tr>
            <tr style="border-top: 2px solid {tema['text_color']};">
                <td style="font-size: 1.3rem; font-weight: 800;">⚖️ Geriye Kalan Yeme Hakkın</td>
                <td style="text-align: right; font-size: 1.3rem; font-weight: 800;">{round(kalan_kalori)} kcal</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        st.caption(f"Aktivite düzeyin günde yaklaşık {taban_adim} adımı zaten içeriyor; yalnızca bunun üzerindeki adımlar ek kalori olarak sayılır.")
        if kalan_kalori < 0: st.error(f"⚠️ Limitini {abs(round(kalan_kalori))} kcal aştın.")
        else: st.success(f"✅ Harika gidiyorsun! {round(kalan_kalori)} kcal yeme hakkın duruyor.")

        st.markdown("<h4>Günlük Makro İhtiyaçları</h4>", unsafe_allow_html=True)
        st.markdown(render_makro("🥩 Protein", top_pro, hedef_pro, "#ff3b30", tema["ring_track"]), unsafe_allow_html=True)
        st.markdown(render_makro("🍞 Karbonhidrat", top_karb, hedef_karb, "#007aff", tema["ring_track"]), unsafe_allow_html=True)
        st.markdown(render_makro("🥑 Yağ", top_yag, hedef_yag, "#ffcc00", tema["ring_track"]), unsafe_allow_html=True)

    # --- YEMEK ARAMA ---
    with kart("kart_yemek"):
        st.markdown("<h2 style='font-size: 2rem;'>🔎 Akıllı Yemek Arama & İnce Ayar</h2>", unsafe_allow_html=True)

        if df_yemek is None:
            st.warning("Yemek veritabanı şu anda yüklenemedi. Biraz sonra sayfayı yenileyip tekrar dene.")
        else:
            arama_metni = st.text_input("🔍 Hangi yemeği arıyorsun? (Kelime girerek filtrele)", placeholder="Örn: Tavuk, Yumurta, Pilav...").strip()
            isimler = df_yemek["Yemek Adı"].dropna().astype(str)
            if arama_metni:
                isimler = isimler[isimler.map(tr_kucuk).str.contains(tr_kucuk(arama_metni), regex=False)]
            yemek_isimleri = isimler.tolist()

            if not yemek_isimleri:
                st.warning("Bu kelimeyle eşleşen yemek bulunamadı.")
            else:
                a_col1, a_col2 = st.columns([3, 1])
                with a_col1:
                    secilen_yemek = st.selectbox("Arama Sonuçlarından Seç...", yemek_isimleri, key="db_yemek")
                with a_col2:
                    secilen_ogun = st.selectbox("Hangi Öğün?", OGUNLER, key="db_ogun")

                if secilen_yemek:
                    detay = df_yemek[df_yemek["Yemek Adı"] == secilen_yemek].iloc[0]
                    sayilar = pd.to_numeric(detay[["Protein (g)", "Karbonhidrat (g)", "Yağ (g)"]], errors="coerce").fillna(0.0)
                    base_p, base_c, base_f = (float(v) for v in sayilar)

                    st.caption(f"100g Standart Değerleri: P: {base_p}g | K: {base_c}g | Y: {base_f}g")
                    porsiyon_g = st.number_input("Porsiyon (Gram)", min_value=10, max_value=2000, value=100, step=10)
                    carp = porsiyon_g / 100.0
                    deger_p, deger_c, deger_f = round(base_p * carp, 1), round(base_c * carp, 1), round(base_f * carp, 1)

                    with st.expander("🛠️ İçeriği Kendine Göre Ayarla (İsteğe Bağlı)"):
                        # Üst sınır porsiyonla birlikte büyür; büyük porsiyonlarda slider taşmaz
                        new_p = st.slider("Protein (g)", 0.0, max(150.0, float(round(deger_p * 1.5))), deger_p, 0.1)
                        new_c = st.slider("Karbonhidrat (g)", 0.0, max(300.0, float(round(deger_c * 1.5))), deger_c, 0.1)
                        new_f = st.slider("Yağ (g)", 0.0, max(150.0, float(round(deger_f * 1.5))), deger_f, 0.1)

                    new_kcal = round((new_p * 4) + (new_c * 4) + (new_f * 9))
                    st.info(f"🔥 Hesaplanmış Son Kalori: **{new_kcal} kcal**")

                    if st.button("➕ Günlüğe Ekle", width="stretch"):
                        st.session_state.gunluk_kayitlar.append({
                            "Tarih": secilen_tarih, "Öğün": secilen_ogun, "Tarif": secilen_yemek,
                            "Kalori": new_kcal, "Protein": round(new_p, 1),
                            "Karbonhidrat": round(new_c, 1), "Yağ": round(new_f, 1)
                        })
                        if verileri_kaydet(aktif_user): bildir(f"✅ {secilen_yemek} günlüğüne eklendi.")
                        st.rerun()

        st.markdown('<hr class="nova-cizgi">', unsafe_allow_html=True)
        st.markdown("<h3>🍽️ Bugünkü Öğünlerin</h3>", unsafe_allow_html=True)
        for ogun_turu in OGUNLER:
            ogun_yemekleri = [(i, k) for i, k in enumerate(st.session_state.gunluk_kayitlar) if k.get("Tarih") == secilen_tarih and k.get("Öğün") == ogun_turu]
            if ogun_yemekleri:
                st.markdown(f"**{ogun_turu}**")
                for i, k in ogun_yemekleri:
                    c1, c2 = st.columns([10, 1])
                    c1.markdown(f"• {k.get('Tarif', '?')} — *{round(k.get('Kalori', 0))} kcal*")
                    if c2.button("🗑️", key=f"sil_{i}"):
                        st.session_state.gunluk_kayitlar.pop(i)
                        verileri_kaydet(aktif_user)
                        st.rerun()


def sekme_kilo(aktif_user, p):
    bugun_dt = bugun()
    with kart("kart_kilo"):
        st.markdown("<h2 style='font-size: 2rem;'>📈 Kilo Takibi ve Gelişim</h2>", unsafe_allow_html=True)
        st.markdown("İstediğin gün için güncel kilonu gir, geçmişini gör ve kalori hedeflerini otomatik olarak güncelle.")

        k_col1, k_col2 = st.columns(2)
        with k_col1:
            kilo_tarihi = st.date_input("Tartım Tarihi", bugun_dt, max_value=bugun_dt, key="kilo_tarih_giris")
        with k_col2:
            yeni_kilo = st.number_input("Kilon (kg)", min_value=30.0, max_value=250.0, value=sinirla(float(p.get("mevcut_kilo", 60.0)), 30.0, 250.0), step=0.1)

        if st.button("⚖️ Kilomu Kaydet ve Grafiğe Ekle", width="stretch"):
            tarih_metin = str(kilo_tarihi)
            kayit = next((k for k in st.session_state.kilo_gecmisi if k.get("Tarih") == tarih_metin), None)
            if kayit: kayit["Kilo"] = float(yeni_kilo)
            else: st.session_state.kilo_gecmisi.append({"Tarih": tarih_metin, "Kilo": float(yeni_kilo)})

            st.session_state.kilo_gecmisi.sort(key=lambda x: x["Tarih"])
            # Güncel kilo, girilen değer değil en yeni tarihli tartıdır (geçmişe kayıt girmek profili bozmaz)
            p["mevcut_kilo"] = float(st.session_state.kilo_gecmisi[-1]["Kilo"])
            if verileri_kaydet(aktif_user):
                bildir("🎉 Kilon başarıyla kaydedildi! Kalori hedeflerin en güncel tartına göre hesaplanıyor.")
            st.rerun()

        if st.session_state.kilo_gecmisi:
            st.markdown('<hr class="nova-cizgi">', unsafe_allow_html=True)
            st.markdown("<h3>Zaman İçindeki Kilo Değişimin</h3>", unsafe_allow_html=True)
            df_kilo = pd.DataFrame(st.session_state.kilo_gecmisi).set_index("Tarih")
            st.line_chart(df_kilo, color=["#007aff"])

        st.markdown('<hr class="nova-cizgi">', unsafe_allow_html=True)
        st.markdown("<h3>📥 Verilerini İndir (Diyetisyenim İçin)</h3>", unsafe_allow_html=True)
        st.markdown("Tüm yemek yeme geçmişini ve makro dökümlerini tek bir tuşla Excel uyumlu CSV formatında indirerek doktorunla veya diyetisyeninle kolayca paylaşabilirsin.")
        if st.session_state.gunluk_kayitlar:
            # utf-8-sig: Excel'in Türkçe karakterleri doğru göstermesi için
            csv_data = pd.DataFrame(st.session_state.gunluk_kayitlar).to_csv(index=False).encode("utf-8-sig")
            st.download_button(label="🍽️ Yemek Günlüğünü İndir (.CSV)", data=csv_data, file_name=f"nova_yemek_gunlugu_{aktif_user}.csv", mime="text/csv", width="stretch")
        else:
            st.info("Henüz dışa aktarılacak bir yemek kaydın bulunmuyor.")


def sekme_ai_ogun(aktif_user, secilen_tarih):
    with kart("kart_ai_ogun"):
        secilen_ogun_ai = st.selectbox("Hangi Öğün İçin Tarama Yapıyorsun?", OGUNLER, key="ai_ogun_sec")
        totals = meal_scan_page()
        if totals:
            for item in totals["items"]:
                st.session_state.gunluk_kayitlar.append({
                    "Tarih": secilen_tarih, "Öğün": secilen_ogun_ai, "Tarif": f"🤖 {item['Yemek']}",
                    "Kalori": round(float(item["Kalori"])), "Protein": float(item["Protein (g)"]),
                    "Karbonhidrat": float(item["Karb. (g)"]), "Yağ": float(item["Yağ (g)"])
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
def cikis_yap():
    for anahtar in list(st.session_state.keys()):
        del st.session_state[anahtar]
    st.rerun()


def ana_ekran(aktif_user, tema):
    p = st.session_state.profil
    gosterilecek_isim = html.escape(p.get("ad") or aktif_user)
    st.markdown('<div class="nova-header">N O V A</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="nova-user">{gosterilecek_isim}</div>', unsafe_allow_html=True)

    aylar_tr = {1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"}
    gunler_tr = {0: "Pazartesi", 1: "Salı", 2: "Çarşamba", 3: "Perşembe", 4: "Cuma", 5: "Cumartesi", 6: "Pazar"}
    bugun_dt = bugun()
    tarih_str = f"{bugun_dt.day} {aylar_tr[bugun_dt.month]} {bugun_dt.year} {gunler_tr[bugun_dt.weekday()]}"
    st.markdown(f'<div class="nova-tarih">📅 {tarih_str}</div>', unsafe_allow_html=True)

    _, c_orta, _ = st.columns([1, 10, 1])
    with c_orta:
        t_col1, t_col2, t_col3 = st.columns([6, 2, 2])
        with t_col1:
            secilen_tarih = str(st.date_input("🗓️ Geçmiş Tarih İnceleme", bugun_dt))
        with t_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⚙️ Ayarlar", width="stretch"):
                p["setup_tamamlandi"] = False
                st.session_state.onboarding_step = 2
                st.rerun()
        with t_col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪 Çıkış Yap", width="stretch"):
                cikis_yap()

        bildirimleri_goster()
        df_yemek = yemek_veritabanini_yukle()

        tab_ozet, tab_kilo, tab_ai_ogun, tab_ai_koc, tab_ai_asistan = st.tabs(["📊 Günlük Özet", "⚖️ Kilo & Gelişim", "📸 AI Öğün", "🏋️‍♀️ AI Koç", "💬 AI Asistan"])
        with tab_ozet: sekme_ozet(aktif_user, p, tema, secilen_tarih, df_yemek)
        with tab_kilo: sekme_kilo(aktif_user, p)
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
