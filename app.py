import datetime
import hashlib
import json
import pandas as pd
import streamlit as st
from PIL import Image
from supabase import create_client, Client

# --- AI MODÜLLERİ ---
from meal_scan import meal_scan_page
from nova_pages import coach_page, ask_page

st.set_page_config(page_title="Nova — Diyet ve Aktivite Asistanı", page_icon="🦢", layout="wide", initial_sidebar_state="collapsed")

# --- SUPABASE BAĞLANTI AYARLARI ---
SUPABASE_URL = "https://klncgexnykfwzpcrijrt.supabase.co"
SUPABASE_KEY = "sb_publishable_yXcnmg2uJsA7vR0DXnWUWQ_06Jm4E8e"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----------------------------------------------------
# DİNAMİK TEMA VE ARKA PLAN YÖNETİMİ
# ----------------------------------------------------
TEMA_AYARLARI = {
    "Yakut Kızılı": {"bg_image": "tema_kirmizi.jpg", "fallback_bg": "#2A0808", "text_color": "#ffffff", "card_bg": "rgba(35, 5, 10, 0.85)", "ring_track": "rgba(255,255,255,0.15)"},
    "Turkuaz Ferahlığı": {"bg_image": "tema_turkuaz.jpg", "fallback_bg": "#E0F2F1", "text_color": "#004d40", "card_bg": "rgba(230, 250, 245, 0.95)", "ring_track": "rgba(0,0,0,0.1)"},
    "Altın Zarafet": {"bg_image": "tema_altin.jpg", "fallback_bg": "#3e2723", "text_color": "#ffffff", "card_bg": "rgba(40, 25, 20, 0.85)", "ring_track": "rgba(255,255,255,0.15)"},
    "Bordo Kadife": {"bg_image": "tema_bordo.jpg", "fallback_bg": "#310000", "text_color": "#ffebee", "card_bg": "rgba(45, 0, 15, 0.90)", "ring_track": "rgba(255,255,255,0.15)"},
    "Derin Mavi": {"bg_image": "tema_mavi.jpg", "fallback_bg": "#00102A", "text_color": "#e3f2fd", "card_bg": "rgba(0, 15, 45, 0.90)", "ring_track": "rgba(255,255,255,0.15)"},
    "Koyu Cam": {"bg_image": "tema_siyah.jpg", "fallback_bg": "#0f0f0f", "text_color": "#ffffff", "card_bg": "rgba(20, 20, 20, 0.90)", "ring_track": "rgba(255,255,255,0.15)"}
}

# ----------------------------------------------------
# KAPSAMLI YEMEK VERİTABANINI LOKALDEN YÜKLEME 
# ----------------------------------------------------
@st.cache_data
def yemek_veritabanini_yukle():
    try:
        df = pd.read_csv("cok_daha_kapsamli_yemek_veritabani.csv")
        return df
    except Exception:
        # Sarı uyarıyı kaldırdık, tasarımı bozmaması için sessizce varsayılan değeri döndürüyoruz.
        return pd.DataFrame({"Yemek Adı": ["Önce CSV'yi GitHub'a Yükleyin"], "Kalori (kcal)": [0], "Protein (g)": [0], "Karbonhidrat (g)": [0], "Yağ (g)": [0]})

df_yemek = yemek_veritabanini_yukle()

# ----------------------------------------------------
# VERİTABANI VE HESAPLAMA FONKSİYONLARI
# ----------------------------------------------------
def sifre_hashle(sifre): return hashlib.sha256(sifre.encode("utf-8")).hexdigest()

def sifre_kontrol(sifre):
    if len(sifre) < 6: return "Şifre en az 6 karakter olmalıdır."
    if not any(c.isupper() for c in sifre): return "Şifre en az bir büyük harf içermelidir."
    if not any(c.isalpha() for c in sifre): return "Şifre en az bir harf içermelidir."
    return None

def kullanicilari_yukle():
    try:
        res = supabase.table("kullanicilar").select("*").execute()
        return {row["username"]: row["password_hash"] for row in res.data}
    except: return {}

def verileri_yukle(username):
    default_data = {
        "gunluk_kayitlar": [], "aktivite_loglari": {}, "kilo_gecmisi": [],
        "profil": {"ad": "", "cinsiyet": "Kadın", "dogum_yili": 2000, "boy": 165, "mevcut_kilo": 60.0, "hedef_kilo": 55.0, "hedef_sure_ay": 2, "tema": "Koyu Cam", "amaclar": [], "setup_tamamlandi": False}
    }
    try:
        res = supabase.table("kullanici_verileri").select("data").eq("username", username).execute()
        if res.data: 
            d = res.data[0]["data"]
            if "kilo_gecmisi" not in d: d["kilo_gecmisi"] = []
            return d
    except: pass
    return default_data

def verileri_kaydet(username):
    data = {"gunluk_kayitlar": st.session_state.gunluk_kayitlar, "aktivite_loglari": st.session_state.aktivite_loglari, "kilo_gecmisi": st.session_state.kilo_gecmisi, "profil": st.session_state.profil}
    try: supabase.table("kullanici_verileri").upsert({"username": username, "data": data}).execute()
    except: pass

def hesapla_bmr_ve_hedef(p):
    yas = datetime.date.today().year - int(p.get("dogum_yili", 2000))
    if p.get("cinsiyet", "Kadın") == "Kadın":
        bmr = (10 * float(p["mevcut_kilo"])) + (6.25 * float(p["boy"])) - (5 * yas) - 161
    else:
        bmr = (10 * float(p["mevcut_kilo"])) + (6.25 * float(p["boy"])) - (5 * yas) + 5

    amaclar = p.get("amaclar", [])
    if "Kas kazanmak istiyorum" in amaclar: tdee = bmr * 1.55
    elif "Kilo vermek istiyorum" in amaclar: tdee = bmr * 1.35
    else: tdee = bmr * 1.2

    kilo_farki = float(p["mevcut_kilo"]) - float(p["hedef_kilo"])
    gunluk_acik = (kilo_farki * 7700) / max(1, int(p.get("hedef_sure_ay", 1)) * 30)
    
    hedef_kalori = tdee - gunluk_acik
    hedef_kalori = max(1200 if p.get("cinsiyet") == "Kadın" else 1500, hedef_kalori)
    return bmr, tdee, gunluk_acik, hedef_kalori

# ----------------------------------------------------
# OTURUM YÖNETİMİ & GİRİŞ EKRANI
# ----------------------------------------------------
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "aktif_kullanici" not in st.session_state: st.session_state.aktif_kullanici = ""
if "onboarding_step" not in st.session_state: st.session_state.onboarding_step = 1

if not st.session_state.giris_yapildi:
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        :root { color-scheme: light !important; }
        [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f0 100%) !important; color-scheme: light !important; }
        .nova-logo-giris { font-family: 'Playfair Display', serif; font-size: 5rem; letter-spacing: 25px; text-align: center; font-weight: 700; margin-top: 5vh; color: #1a1a1a !important;}
        p, label, span { color: #333333 !important; font-family: 'Plus Jakarta Sans', sans-serif; }
        
        /* GİRİŞ KARTI (BEYAZ BLOK VE KAYMA HATASI DÜZELTİLDİ) */
        div[data-testid="stTabs"] {
            background: rgba(255, 255, 255, 0.95) !important; 
            padding: 40px !important; 
            border-radius: 28px !important; 
            border: 1px solid rgba(0,0,0,0.08) !important; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.08) !important; 
            backdrop-filter: blur(20px) !important;
        }
        div[data-testid="stTabs"] button { font-size: 1.1rem; font-weight: 600; }
        
        div.stButton > button:first-child { background: linear-gradient(180deg, #ffffff 0%, #f0f2f5) !important; color: #1a1a1a !important; font-weight: 700 !important; border-radius: 14px !important; width: 100%; padding: 12px; border: 1px solid rgba(0,0,0,0.12) !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); }
        div.stButton > button:first-child:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.1); background: linear-gradient(180deg, #ffffff 0%, #e2e6eb) !important; border-color: rgba(0,0,0,0.2) !important; }
        .stTextInput > div > div > div, div[data-baseweb="input"] > div, div[data-baseweb="input"] > div:focus-within { background-color: #ffffff !important; border-radius: 12px !important; border: 1px solid rgba(0,0,0,0.15) !important; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important; }
        .stTextInput input, .stTextInput input:focus, .stTextInput input:active, input, input:focus, input:active { color: #000000 !important; background-color: #ffffff !important; caret-color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-weight: 600 !important; }
        input:-webkit-autofill, input:-webkit-autofill:hover, input:-webkit-autofill:focus, input:-webkit-autofill:active { -webkit-box-shadow: 0 0 0 30px white inset !important; -webkit-text-fill-color: #000000 !important; transition: background-color 5000s ease-in-out 0s; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="nova-logo-giris">N O V A</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666666 !important; font-size: 1.1rem; letter-spacing: 5px; margin-bottom: 30px;'>ZARAFET VE DENGE</p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        tab_giris, tab_kayit = st.tabs(["Giriş Yap", "Kayıt Ol"])
        users = kullanicilari_yukle()
        
        with tab_giris:
            g_user = st.text_input("Kullanıcı Adı", key="g_user").strip().lower()
            g_pass = st.text_input("Şifre", type="password", key="g_pass")
            if st.button("Giriş Yap", key="btn_giris"):
                if g_user in users and users[g_user] == sifre_hashle(g_pass):
                    st.session_state.giris_yapildi = True
                    st.session_state.aktif_kullanici = g_user
                    st.session_state.update(verileri_yukle(g_user))
                    st.rerun()
                else: st.error("Hatalı kullanıcı adı veya şifre.")
        with tab_kayit:
            k_user = st.text_input("Yeni Kullanıcı Adı", key="k_user").strip().lower()
            k_pass = st.text_input("Şifre (En az 6 karakter, büyük harf ve harf içermeli)", type="password", key="k_pass")
            if st.button("Hesap Oluştur", key="btn_kayit"):
                hata = sifre_kontrol(k_pass)
                if hata:
                    st.error(hata)
                elif k_user and k_user not in users:
                    supabase.table("kullanicilar").insert({"username": k_user, "password_hash": sifre_hashle(k_pass)}).execute()
                    st.success("Hesap oluşturuldu, giriş yapabilirsiniz.")
                else:
                    st.error("Kullanıcı adı boş olamaz veya zaten kullanımda.")

else:
    aktif_user = st.session_state.aktif_kullanici
    p = st.session_state.profil
    aktif_tema = p.get("tema", "Koyu Cam")
    if aktif_tema not in TEMA_AYARLARI: aktif_tema = "Koyu Cam"
    tema = TEMA_AYARLARI[aktif_tema]
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
        
        .calai-card {{ background: {tema['card_bg']} !important; padding: 35px; border-radius: 28px; backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px); margin-bottom: 30px; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 15px 50px rgba(0,0,0,0.4); }}
        .info-box {{ background: rgba(255,255,255,0.1) !important; border-left: 4px solid {tema['text_color']} !important; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: {tema['text_color']} !important; font-weight: 600; }}
        
        .calai-card p, .calai-card h1, .calai-card h2, .calai-card h3, .calai-card h4, 
        .calai-card td, .calai-card th, .calai-card span, .calai-card label,
        div[data-testid="stMarkdownContainer"] p, div[data-testid="stMarkdownContainer"] h2, 
        div[data-testid="stMarkdownContainer"] h3, div[data-testid="stMarkdownContainer"] h4,
        div[data-testid="stWidgetLabel"] p, label[data-baseweb="radio"] div {{ color: {tema['text_color']} !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }}
        
        div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, input[type="text"], input[type="number"], textarea {{ background-color: #ffffff !important; color: #000000 !important; border-radius: 12px !important; border: 2px solid rgba(0,0,0,0.15) !important; }}
        div[data-baseweb="select"] span, input, input::placeholder {{ color: #000000 !important; font-weight: bold; }}
        div[data-baseweb="popover"], ul[role="listbox"], ul[role="listbox"] li, ul[role="listbox"] span {{ background-color: #ffffff !important; color: #000000 !important; }}
        span[data-baseweb="tag"] {{ background-color: {tema['text_color']} !important; color: {tema['fallback_bg']} !important; }}
        span[data-baseweb="tag"] span {{ color: {tema['fallback_bg']} !important; }}
        div[data-baseweb="input"] button {{ color: #000000 !important; }}
        
        /* ------------------------------------------------------------------ */
        /* DAHA GENİŞ, DAHA FERAH SQUIRCLE SEKME (TAB) TASARIMI               */
        /* ------------------------------------------------------------------ */
        div[data-testid="stTabs"] > div > div[role="tablist"] {{
            background: {tema['card_bg']} !important;
            padding: 10px !important; 
            border-radius: 24px !important;
            gap: 25px !important; 
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
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
            background-color: rgba(255,255,255,0.08) !important;
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
        
        div[data-baseweb="tab-highlight"] {{ display: none !important; }}
        /* ------------------------------------------------------------------ */
        
        div.stButton > button:first-child {{ background: {tema['card_bg']} !important; color: {tema['text_color']} !important; border: 1px solid rgba(255,255,255,0.3) !important; font-weight: 700 !important; border-radius: 16px !important; padding: 10px 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.2); backdrop-filter: blur(10px); transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); }}
        div.stButton > button:first-child:hover {{ transform: translateY(-2px); background: {tema['text_color']} !important; color: {tema['fallback_bg']} !important; border-color: {tema['text_color']} !important; box-shadow: 0 12px 30px rgba(0,0,0,0.3); }}
        
        .ring-container {{ width: 180px; height: 180px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; }}
        .ring-inner {{ width: 140px; height: 140px; border-radius: 50%; background: {tema['card_bg']} !important; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
        .ring-val {{ font-size: 2rem; font-weight: 800; margin-bottom: -5px; color: {tema['text_color']} !important; }}
        .ring-lbl {{ font-size: 1rem; opacity: 0.8; text-transform: uppercase; letter-spacing: 2px; color: {tema['text_color']} !important; }}
        table {{ width: 100%; font-size: 1.1rem; background: transparent; border-collapse: collapse; }}
        th, td {{ padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.2); text-align: left; color: {tema['text_color']} !important; }}
        th {{ font-weight: 800; font-size: 1.2rem; opacity: 0.9; }}
        </style>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # FATSECRET TARZI DETAYLI ONBOARDING SÜRECİ
    # ----------------------------------------------------
    if not p.get("setup_tamamlandi", False):
        st.markdown('<div class="nova-header" style="font-size:3.5rem; margin-top:20px;">N O V A</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="calai-card">', unsafe_allow_html=True)
        
        step = st.session_state.onboarding_step
        
        if step == 1:
            st.markdown("<h2 style='text-align:center;'>Tanıştığımıza memnun oldum,<br>Nova'ya Hoş Geldin! 🦢</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; opacity:0.9;'>Hedeflerine ulaşmanda sana yardımcı olmak için buradayız.<br>Başlamak için birkaç kısa sorumuz olacak.</p>", unsafe_allow_html=True)
            st.markdown('<div class="info-box">ℹ️ Cevapların, hedeflerini anlamamıza ve uygulamayı senin için kişiselleştirmemize yardımcı olacak.</div>', unsafe_allow_html=True)
            if st.button("Başla ➔", use_container_width=True):
                st.session_state.onboarding_step = 2
                st.rerun()

        elif step == 2:
            st.markdown("<h2 style='text-align:center;'>Merhaba! Adın nedir?</h2>", unsafe_allow_html=True)
            ad_input = st.text_input("Adını Gir", value=p.get("ad", ""))
            st.markdown('<div class="info-box">ℹ️ Nova uygulamasını sana özel hale getirmek ve sana hitap edebilmek için adını kullanacağız.</div>', unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            if b1.button("⬅️ Geri"): st.session_state.onboarding_step = 1; st.rerun()
            if b2.button("İleri ➔"):
                if ad_input:
                    st.session_state.profil["ad"] = ad_input
                    st.session_state.onboarding_step = 3
                    st.rerun()
                else: st.error("Lütfen adını gir.")

        elif step == 3:
            st.markdown(f"<h2 style='text-align:center;'>Nova'yı Hangi Amaçla Kullanmak İstiyorsun {p.get('ad', '')}?</h2>", unsafe_allow_html=True)
            amaclar = st.multiselect("Hedeflerin (Birden fazla seçebilirsin)", ["Kilo vermek istiyorum", "Kilomu korumak istiyorum", "Kilo almak istiyorum", "Kas kazanmak istiyorum", "Sağlıklı beslenmek istiyorum"], default=p.get("amaclar", []))
            b1, b2 = st.columns(2)
            if b1.button("⬅️ Geri"): st.session_state.onboarding_step = 2; st.rerun()
            if b2.button("İleri ➔"):
                st.session_state.profil["amaclar"] = amaclar
                st.session_state.onboarding_step = 4
                st.rerun()

        elif step == 4:
            st.markdown("<h2 style='text-align:center;'>Cinsiyetin nedir?</h2>", unsafe_allow_html=True)
            cinsiyet = st.selectbox("Seçimini yap:", ["Kadın", "Erkek"], index=["Kadın", "Erkek"].index(p.get("cinsiyet", "Kadın")))
            st.markdown('<div class="info-box">ℹ️ Cinsiyetin, vücudunun günlük enerji ihtiyacını hesaplamamızı doğrudan etkiler.</div>', unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            if b1.button("⬅️ Geri"): st.session_state.onboarding_step = 3; st.rerun()
            if b2.button("İleri ➔"):
                st.session_state.profil["cinsiyet"] = cinsiyet
                st.session_state.onboarding_step = 5
                st.rerun()

        elif step == 5:
            st.markdown("<h2 style='text-align:center;'>Doğum yılın ne?</h2>", unsafe_allow_html=True)
            mevcut_yil = datetime.date.today().year
            dogum_yili = st.number_input("Yıl", min_value=1920, max_value=mevcut_yil-10, value=int(p.get("dogum_yili", 2000)))
            yas = mevcut_yil - dogum_yili
            st.markdown(f"<h4 style='text-align:center;'>Şu an <b>{yas}</b> yaşındasın.</h4>", unsafe_allow_html=True)
            st.markdown('<div class="info-box">ℹ️ Yaşın, vücudunun her gün ne kadar enerjiye (BMR) ihtiyaç duyduğunu etkiler.</div>', unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            if b1.button("⬅️ Geri"): st.session_state.onboarding_step = 4; st.rerun()
            if b2.button("İleri ➔"):
                st.session_state.profil["dogum_yili"] = dogum_yili
                st.session_state.onboarding_step = 6
                st.rerun()

        elif step == 6:
            st.markdown("<h2 style='text-align:center;'>Boyun kaç?</h2>", unsafe_allow_html=True)
            boy = st.number_input("Boy (cm)", min_value=130, max_value=220, value=int(p.get("boy", 165)))
            st.markdown('<div class="info-box">ℹ️ Boyun, vücudunun her gün ne kadar enerji harcadığını etkiler.</div>', unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            if b1.button("⬅️ Geri"): st.session_state.onboarding_step = 5; st.rerun()
            if b2.button("İleri ➔"):
                st.session_state.profil["boy"] = boy
                st.session_state.onboarding_step = 7
                st.rerun()

        elif step == 7:
            st.markdown("<h2 style='text-align:center;'>Şu andaki kilon ne?</h2>", unsafe_allow_html=True)
            mevcut_kilo = st.number_input("Kilo (kg)", min_value=35.0, max_value=250.0, value=float(p.get("mevcut_kilo", 60.0)), step=0.5)
            st.markdown('<div class="info-box">ℹ️ Bu bilgi, bulunduğun noktaya göre kalori hedefini hesaplamamıza yardımcı olur. İleride kilo sekmesinden her zaman güncelleyebilirsin.</div>', unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            if b1.button("⬅️ Geri"): st.session_state.onboarding_step = 6; st.rerun()
            if b2.button("İleri ➔"):
                st.session_state.profil["mevcut_kilo"] = mevcut_kilo
                st.session_state.onboarding_step = 8
                st.rerun()

        elif step == 8:
            st.markdown("<h2 style='text-align:center;'>Hedef kilon nedir?</h2>", unsafe_allow_html=True)
            hedef_kilo = st.number_input("Hedef Kilo (kg)", min_value=35.0, value=float(p.get("hedef_kilo", 55.0)), step=0.5)
            hedef_sure = st.number_input("Hedefe Ulaşma Süresi (Ay)", min_value=1, value=int(p.get("hedef_sure_ay", 2)))
            sec_tema = st.selectbox("Nova Deneyimin İçin Bir Tema Seç", list(TEMA_AYARLARI.keys()), index=list(TEMA_AYARLARI.keys()).index(aktif_tema))
            b1, b2 = st.columns(2)
            if b1.button("⬅️ Geri"): st.session_state.onboarding_step = 7; st.rerun()
            if b2.button("Kalori Hedefimi Hesapla ➔"):
                st.session_state.profil.update({"hedef_kilo": hedef_kilo, "hedef_sure_ay": hedef_sure, "tema": sec_tema})
                st.session_state.onboarding_step = 9
                st.rerun()

        elif step == 9:
            st.markdown(f"<h2 style='text-align:center;'>Paylaştığın için teşekkürler, {p.get('ad', '')} 🎉</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; font-size:1.2rem; opacity:0.9;'>Bize söylediklerin, seni nasıl destekleyeceğimizi şekillendirmemize yardımcı olacak.</p>", unsafe_allow_html=True)
            bmr, tdee, gunluk_acik, hedef_kalori = hesapla_bmr_ve_hedef(p)
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); padding: 25px; border-radius: 15px; margin-top:20px;">
                <h3 style="text-align:center; margin-bottom: 20px;">İşte Kişisel Kalori Hedefin</h3>
                <p><b>Amacın:</b> {', '.join(p.get('amaclar', ['Belirtilmedi']))}</p>
                <p><b>Dinlenik Metabolizman (BMR):</b> {round(bmr)} kcal</p>
                <p><b>Tahmini Günlük Harcaman:</b> {round(tdee)} kcal</p>
                <hr>
                <h2 style="color: #007aff !important; text-align:center;">Günlük Hedefin: {round(hedef_kalori)} kcal</h2>
            </div><br>
            """, unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            if b1.button("⬅️ Geri"): st.session_state.onboarding_step = 8; st.rerun()
            if b2.button("🚀 Harika, Uygulamaya Başla!", type="primary"):
                st.session_state.profil["setup_tamamlandi"] = True
                
                # İlk kurulumda güncel kiloyu geçmişe ekle
                tarih_str = str(datetime.date.today())
                if not any(k["Tarih"] == tarih_str for k in st.session_state.kilo_gecmisi):
                    st.session_state.kilo_gecmisi.append({"Tarih": tarih_str, "Kilo": float(p["mevcut_kilo"])})
                
                verileri_kaydet(aktif_user)
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # ----------------------------------------------------
    # ANA EKRAN
    # ----------------------------------------------------
    gosterilecek_isim = p.get("ad", aktif_user).capitalize()
    st.markdown('<div class="nova-header">N O V A</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="nova-user">{gosterilecek_isim}</div>', unsafe_allow_html=True)
    
    aylar_tr = {1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"}
    gunler_tr = {0: "Pazartesi", 1: "Salı", 2: "Çarşamba", 3: "Perşembe", 4: "Cuma", 5: "Cumartesi", 6: "Pazar"}
    bugun_dt = datetime.date.today()
    tarih_str = f"{bugun_dt.day} {aylar_tr[bugun_dt.month]} {bugun_dt.year} {gunler_tr[bugun_dt.weekday()]}"
    st.markdown(f'<div class="nova-tarih">📅 {tarih_str}</div>', unsafe_allow_html=True)

    c_sol, c_orta, c_sag = st.columns([1, 10, 1])
    with c_orta:
        t_col1, t_col2 = st.columns([8, 2])
        with t_col1:
            secilen_tarih = str(st.date_input("🗓️ Geçmiş Tarih İnceleme", bugun_dt))
        with t_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⚙️ Ayarlar", use_container_width=True):
                st.session_state.profil["setup_tamamlandi"] = False
                st.session_state.onboarding_step = 2
                st.rerun()

        if secilen_tarih not in st.session_state.aktivite_loglari:
            st.session_state.aktivite_loglari[secilen_tarih] = {"adim": 0, "su": 0.0, "egzersiz_kalori": 0}
        curr_aktivite = st.session_state.aktivite_loglari[secilen_tarih]

        tab_ozet, tab_kilo, tab_ai_ogun, tab_ai_koc, tab_ai_asistan = st.tabs(["📊 Günlük Özet", "⚖️ Kilo & Gelişim", "📸 AI Öğün", "🏋️‍♀️ AI Koç", "💬 AI Asistan"])

        # ==========================================
        # 1. SEKME: GÜNLÜK ÖZET & MANUEL EKLEME
        # ==========================================
        with tab_ozet:
            st.markdown('<div class="calai-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='text-align:center; font-size: 2rem; margin-bottom: 25px;'>Günlük Aktivite ve Su Halkaları</h2>", unsafe_allow_html=True)
            adim_yuzde = min(curr_aktivite['adim'] / 10000 * 100, 100)
            su_yuzde = min(curr_aktivite['su'] / 2.5 * 100, 100)
            hc1, hc2 = st.columns(2)
            with hc1:
                st.markdown(f"""
                    <div class="ring-container" style="background: conic-gradient(#ff3b30 {adim_yuzde}%, {tema['ring_track']} 0deg);">
                        <div class="ring-inner">
                            <div class="ring-val" style="color:#ff3b30 !important;">{curr_aktivite['adim']}</div>
                            <div class="ring-lbl">ADIM</div>
                        </div>
                    </div><br>
                """, unsafe_allow_html=True)
                yeni_adim = st.number_input("Eklenecek Adım:", value=0, step=1000)
                if st.button("🔴 Adımı Kaydet", use_container_width=True):
                    curr_aktivite["adim"] += yeni_adim
                    verileri_kaydet(aktif_user)
                    st.rerun()
            with hc2:
                st.markdown(f"""
                    <div class="ring-container" style="background: conic-gradient(#007aff {su_yuzde}%, {tema['ring_track']} 0deg);">
                        <div class="ring-inner">
                            <div class="ring-val" style="color:#007aff !important;">{curr_aktivite['su']:.2f}</div>
                            <div class="ring-lbl">LİTRE</div>
                        </div>
                    </div><br>
                """, unsafe_allow_html=True)
                su_secim = st.number_input("Eklenecek Su (Litre):", value=0.25, step=0.25)
                if st.button("🔵 Suyu Kaydet", use_container_width=True):
                    curr_aktivite["su"] += su_secim
                    verileri_kaydet(aktif_user)
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            # KALORİ TABLOSU
            st.markdown('<div class="calai-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='font-size: 2rem;'>Kalori ve Denge Tablosu</h2>", unsafe_allow_html=True)
            
            bugun_og = [k for k in st.session_state.gunluk_kayitlar if k["Tarih"] == secilen_tarih]
            top_kalori = sum([k["Kalori"] for k in bugun_og])
            top_pro = sum([k.get("Protein", 0) for k in bugun_og])
            top_karb = sum([k.get("Karbonhidrat", 0) for k in bugun_og])
            top_yag = sum([k.get("Yağ", 0) for k in bugun_og])
            
            bmr, tdee, gunluk_acik, hedef_kalori_alim = hesapla_bmr_ve_hedef(p)
            aktif_harcanan = (curr_aktivite["adim"] * 0.04) + curr_aktivite.get("egzersiz_kalori", 0)
            kalan_kalori = hedef_kalori_alim - top_kalori + aktif_harcanan
            
            hedef_pro = (hedef_kalori_alim * 0.3) / 4
            hedef_karb = (hedef_kalori_alim * 0.4) / 4
            hedef_yag = (hedef_kalori_alim * 0.3) / 9
            
            st.markdown(f"""
            <table>
                <tr><th>Metrik</th><th style="text-align: right;">Değer</th></tr>
                <tr><td>🎯 Günlük Hedef Kalori Bütçen</td><td style="text-align: right; color: #007aff !important;"><b>{round(hedef_kalori_alim)} kcal</b></td></tr>
                <tr><td>🍽️ Bugüne Kadar Yediklerin</td><td style="text-align: right; color: #ff3b30 !important;"><b>- {round(top_kalori)} kcal</b></td></tr>
                <tr><td>🏃‍♀️ Hareket ve Egzersizle Kazandıkların</td><td style="text-align: right; color: #34c759 !important;"><b>+ {round(aktif_harcanan)} kcal</b></td></tr>
                <tr style="border-top: 2px solid rgba(255,255,255,0.5);">
                    <td style="font-size: 1.3rem; font-weight: 800;">⚖️ Geriye Kalan Yeme Hakkın</td>
                    <td style="text-align: right; font-size: 1.3rem; font-weight: 800;">{round(kalan_kalori)} kcal</td>
                </tr>
            </table><br>
            """, unsafe_allow_html=True)
            if kalan_kalori < 0: st.error(f"⚠️ Limitini {abs(round(kalan_kalori))} kcal aştın.")
            else: st.success(f"✅ Harika gidiyorsun! {round(kalan_kalori)} kcal yeme hakkın duruyor.")

            def render_makro(isim, mevcut, hedef, renk):
                yuzde = min((mevcut / max(hedef, 1)) * 100, 100)
                return f"""
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.95rem; margin-bottom: 5px;">
                        <span>{isim}</span><span>{round(mevcut)}g / {round(hedef)}g</span>
                    </div>
                    <div style="width: 100%; background-color: rgba(255,255,255,0.15); border-radius: 4px; height: 6px;">
                        <div style="width: {yuzde}%; background-color: {renk}; height: 100%; border-radius: 4px;"></div>
                    </div>
                </div>
                """
            st.markdown("<h4>Günlük Makro İhtiyaçları</h4>", unsafe_allow_html=True)
            st.markdown(render_makro("🥩 Protein", top_pro, hedef_pro, "#ff3b30"), unsafe_allow_html=True)
            st.markdown(render_makro("🍞 Karbonhidrat", top_karb, hedef_karb, "#007aff"), unsafe_allow_html=True)
            st.markdown(render_makro("🥑 Yağ", top_yag, hedef_yag, "#ffcc00"), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # GELİŞMİŞ YAZARAK ARAMA
            st.markdown('<div class="calai-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='font-size: 2rem;'>🔎 Akıllı Yemek Arama & İnce Ayar</h2>", unsafe_allow_html=True)
            
            arama_metni = st.text_input("🔍 Hangi yemeği arıyorsun? (Kelime girerek filtrele)", placeholder="Örn: Tavuk, Yumurta, Pilav...")
            
            if arama_metni:
                filtrelenmis_df = df_yemek[df_yemek['Yemek Adı'].str.contains(arama_metni, case=False, na=False)]
                yemek_isimleri = filtrelenmis_df["Yemek Adı"].tolist()
            else:
                yemek_isimleri = df_yemek["Yemek Adı"].tolist()
                
            if not yemek_isimleri:
                st.warning("Bu kelimeyle eşleşen yemek bulunamadı.")
            else:
                a_col1, a_col2 = st.columns([3, 1])
                with a_col1:
                    secilen_yemek = st.selectbox("Arama Sonuçlarından Seç...", yemek_isimleri, key="db_yemek")
                with a_col2:
                    secilen_ogun = st.selectbox("Hangi Öğün?", ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"], key="db_ogun")
                    
                if secilen_yemek and not df_yemek.empty and secilen_yemek != "Önce CSV'yi GitHub'a Yükleyin":
                    detay = df_yemek[df_yemek["Yemek Adı"] == secilen_yemek].iloc[0]
                    base_p = float(detay['Protein (g)'])
                    base_c = float(detay['Karbonhidrat (g)'])
                    base_f = float(detay['Yağ (g)'])
                    
                    st.caption(f"100g Standart Değerleri: P: {base_p}g | K: {base_c}g | Y: {base_f}g")
                    porsiyon_g = st.number_input("Porsiyon (Gram)", min_value=10, max_value=2000, value=100, step=10)
                    carp = porsiyon_g / 100.0
                    
                    with st.expander("🛠️ İçeriği Kendine Göre Ayarla (İsteğe Bağlı)"):
                        new_p = st.slider("Protein (g)", 0.0, 150.0, float(base_p * carp), 0.1)
                        new_c = st.slider("Karbonhidrat (g)", 0.0, 300.0, float(base_c * carp), 0.1)
                        new_f = st.slider("Yağ (g)", 0.0, 150.0, float(base_f * carp), 0.1)
                    
                    new_kcal = round((new_p * 4) + (new_c * 4) + (new_f * 9))
                    st.info(f"🔥 Hesaplanmış Son Kalori: **{new_kcal} kcal**")
                    
                    if st.button("➕ Günlüğe Ekle", use_container_width=True):
                        st.session_state.gunluk_kayitlar.append({
                            "Tarih": secilen_tarih, "Öğün": secilen_ogun, "Tarif": secilen_yemek,
                            "Kalori": new_kcal, "Protein": round(new_p, 1), 
                            "Karbonhidrat": round(new_c, 1), "Yağ": round(new_f, 1)
                        })
                        verileri_kaydet(aktif_user)
                        st.rerun()

            st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 25px 0;'>", unsafe_allow_html=True)
            st.markdown("<h3>🍽️ Bugünkü Öğünlerin</h3>", unsafe_allow_html=True)
            for ogun_turu in ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"]:
                ogun_yemekleri = [(i, k) for i, k in enumerate(st.session_state.gunluk_kayitlar) if k.get("Tarih") == secilen_tarih and k.get("Öğün") == ogun_turu]
                if ogun_yemekleri:
                    st.markdown(f"**{ogun_turu}**")
                    for i, k in ogun_yemekleri:
                        c1, c2 = st.columns([10, 1])
                        c1.markdown(f"• {k['Tarif']} — *{k['Kalori']} kcal*")
                        if c2.button("🗑️", key=f"sil_{i}"):
                            st.session_state.gunluk_kayitlar.pop(i)
                            verileri_kaydet(aktif_user)
                            st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ==========================================
        # 2. SEKME: KİLO TAKİBİ VE DİYETİSYEN ÇIKTISI
        # ==========================================
        with tab_kilo:
            st.markdown('<div class="calai-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='font-size: 2rem;'>📈 Kilo Takibi ve Gelişim</h2>", unsafe_allow_html=True)
            st.markdown("İstediğin gün için güncel kilonu gir, geçmişini gör ve kalori hedeflerini otomatik olarak güncelle.", unsafe_allow_html=True)
            
            k_col1, k_col2 = st.columns(2)
            with k_col1:
                kilo_tarihi = st.date_input("Tartım Tarihi", bugun_dt, key="kilo_tarih_giris")
            with k_col2:
                yeni_kilo = st.number_input("Kilon (kg)", min_value=30.0, max_value=250.0, value=float(p["mevcut_kilo"]), step=0.1)
                
            if st.button("⚖️ Kilomu Kaydet ve Grafiğe Ekle", use_container_width=True):
                tarih_metin = str(kilo_tarihi)
                kayit_var_mi = False
                for log in st.session_state.kilo_gecmisi:
                    if log["Tarih"] == tarih_metin:
                        log["Kilo"] = yeni_kilo
                        kayit_var_mi = True
                        break
                if not kayit_var_mi:
                    st.session_state.kilo_gecmisi.append({"Tarih": tarih_metin, "Kilo": yeni_kilo})
                
                st.session_state.kilo_gecmisi.sort(key=lambda x: x["Tarih"])
                p["mevcut_kilo"] = yeni_kilo
                verileri_kaydet(aktif_user)
                st.success("🎉 Kilon başarıyla kaydedildi! Kalori hedeflerin bu yeni kiloya göre güncellendi.")
                st.rerun()
                
            if st.session_state.kilo_gecmisi:
                st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 25px 0;'>", unsafe_allow_html=True)
                st.markdown("<h3>Zaman İçindeki Kilo Değişimin</h3>", unsafe_allow_html=True)
                df_kilo = pd.DataFrame(st.session_state.kilo_gecmisi)
                df_kilo = df_kilo.set_index("Tarih")
                st.line_chart(df_kilo, color=["#007aff"], use_container_width=True)

            st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 25px 0;'>", unsafe_allow_html=True)
            st.markdown("<h3>📥 Verilerini İndir (Diyetisyenim İçin)</h3>", unsafe_allow_html=True)
            st.markdown("Tüm yemek yeme geçmişini ve makro dökümlerini tek bir tuşla Excel uyumlu CSV formatında indirerek doktorunla veya diyetisyeninle kolayca paylaşabilirsin.", unsafe_allow_html=True)
            if st.session_state.gunluk_kayitlar:
                df_export = pd.DataFrame(st.session_state.gunluk_kayitlar)
                csv_data = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(label="🍽️ Yemek Günlüğünü İndir (.CSV)", data=csv_data, file_name=f"nova_yemek_gunlugu_{aktif_user}.csv", mime="text/csv", use_container_width=True)
            else:
                st.info("Henüz dışa aktarılacak bir yemek kaydın bulunmuyor.")
                
            st.markdown('</div>', unsafe_allow_html=True)

        with tab_ai_ogun:
            st.markdown('<div class="calai-card">', unsafe_allow_html=True)
            secilen_ogun_ai = st.selectbox("Hangi Öğün İçin Tarama Yapıyorsun?", ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"], key="ai_ogun_sec")
            totals = meal_scan_page()
            if totals:
                for item in totals["items"]:
                    st.session_state.gunluk_kayitlar.append({
                        "Tarih": secilen_tarih, "Öğün": secilen_ogun_ai, "Tarif": f"🤖 {item['Yemek']}",
                        "Kalori": float(item["Kalori"]), "Protein": float(item["Protein (g)"]), 
                        "Karbonhidrat": float(item["Karb. (g)"]), "Yağ": float(item["Yağ (g)"])
                    })
                verileri_kaydet(aktif_user)
                st.success(f"{totals['kcal']} kcal başarıyla günlüğüne eklendi!")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with tab_ai_koc:
            st.markdown('<div class="calai-card">', unsafe_allow_html=True)
            log = coach_page()
            if log:
                curr_aktivite["egzersiz_kalori"] += 250
                verileri_kaydet(aktif_user)
                st.success("🤖 Harika! AI Antrenmanını tamamladın, günlüğüne 250 kcal harcama eklendi.")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab_ai_asistan:
            st.markdown('<div class="calai-card">', unsafe_allow_html=True)
            ask_page()
            st.markdown('</div>', unsafe_allow_html=True)
