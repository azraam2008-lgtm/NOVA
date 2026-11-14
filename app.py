import datetime
import hashlib
import json
import pandas as pd
import streamlit as st
from PIL import Image
from supabase import create_client, Client

# --- AI MODÜLLERİ ---
from nova_core import cfg
from meal_scan import meal_scan_page
from nova_pages import coach_page, ask_page
from yemek_arama import yemek_arama_sayfasi
from gelisim import gelisim_sayfasi
from hesap import hesap_bolumu

st.set_page_config(page_title="Nova — Diyet ve Aktivite Asistanı", page_icon="", layout="wide", initial_sidebar_state="collapsed")

# --- SUPABASE BAĞLANTI AYARLARI ---
# Streamlit Secrets'ta SUPABASE_URL / SUPABASE_KEY tanımlıysa onlar kullanılır.
SUPABASE_URL = cfg("SUPABASE_URL", "https://klncgexnykfwzpcrijrt.supabase.co")
SUPABASE_KEY = cfg("SUPABASE_KEY", "sb_publishable_yXcnmg2uJsA7vR0DXnWUWQ_06Jm4E8e")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----------------------------------------------------
# DİNAMİK TEMA VE ARKA PLAN YÖNETİMİ
# ----------------------------------------------------
# bg_image: GitHub deposundaki GERÇEK dosya adları.
# scrim: fotoğrafın üstüne serilen perde. Fotoğraf açık renkliyse yazı okunmaz hale
#        gelmesin diye her temaya kendi perdesi var.
TEMA_AYARLARI = {
    "Yakut Kızılı": {"bg_image": "925912004661385138.jpg", "fallback_bg": "#2A0808",
                     "text_color": "#ffffff", "card_bg": "rgba(35, 5, 10, 0.85)",
                     "ring_track": "rgba(255,255,255,0.15)", "scrim": "rgba(0,0,0,0.35)"},
    "Turkuaz Ferahlığı": {"bg_image": "Oppo_Find_X9s_Wallpaper.jpg", "fallback_bg": "#E0F2F1",
                          "text_color": "#06403c", "card_bg": "rgba(240, 253, 250, 0.94)",
                          "ring_track": "rgba(0,0,0,0.12)", "scrim": "rgba(255,255,255,0.55)"},
    "Altın Zarafet": {"bg_image": "826903181627399116.jpg", "fallback_bg": "#3e2723",
                      "text_color": "#ffffff", "card_bg": "rgba(38, 24, 18, 0.88)",
                      "ring_track": "rgba(255,255,255,0.15)", "scrim": "rgba(0,0,0,0.55)"},
    "Bordo Kadife": {"bg_image": "Deep_Maroon.jpg", "fallback_bg": "#310000",
                     "text_color": "#ffebee", "card_bg": "rgba(45, 0, 15, 0.90)",
                     "ring_track": "rgba(255,255,255,0.15)", "scrim": "rgba(0,0,0,0.40)"},
    "Derin Mavi": {"bg_image": "Mavi_Arka_Plan.jpg", "fallback_bg": "#00102A",
                   "text_color": "#e3f2fd", "card_bg": "rgba(0, 15, 45, 0.90)",
                   "ring_track": "rgba(255,255,255,0.15)", "scrim": "rgba(0,0,0,0.30)"},
    "Koyu Cam": {"bg_image": "687854543129884120.jpg", "fallback_bg": "#0f0f0f",
                 "text_color": "#ffffff", "card_bg": "rgba(20, 20, 20, 0.90)",
                 "ring_track": "rgba(255,255,255,0.15)", "scrim": "rgba(0,0,0,0.30)"}
}

# ----------------------------------------------------
# KAPSAMLI YEMEK VERİTABANINI BULUTTAN ÇEKME
# ----------------------------------------------------
@st.cache_data
def yemek_veritabanini_yukle():
    try:
        df = pd.read_csv("https://raw.githubusercontent.com/azraam2008-lgtm/NOVA/main/cok_daha_kapsamli_yemek_veritabani.csv")
        return df
    except:
        return pd.DataFrame({"Yemek Adı": ["Önce CSV'yi GitHub'a Yükleyin"], "Kalori (kcal)": [0], "Protein (g)": [0], "Karbonhidrat (g)": [0], "Yağ (g)": [0]})

df_yemek = yemek_veritabanini_yukle()

# ----------------------------------------------------
# VERİTABANI VE HESAPLAMA FONKSİYONLARI
# ----------------------------------------------------
def sifre_hashle(sifre):
    """Eski (SHA-256) kayıtları doğrulamak için. Yeni şifreler için sifre_olustur kullanılır."""
    return hashlib.sha256(sifre.encode("utf-8")).hexdigest()

def sifre_olustur(sifre):
    """Yeni şifreler bcrypt ile, her biri kendi tuzuyla saklanır."""
    try:
        import bcrypt
        return bcrypt.hashpw(sifre.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    except ImportError:
        return sifre_hashle(sifre)  # bcrypt kurulu değilse eski yönteme düşer

def sifre_dogrula(sifre, kayitli):
    if not kayitli:
        return False
    if kayitli.startswith("$2"):  # bcrypt
        try:
            import bcrypt
            return bcrypt.checkpw(sifre.encode("utf-8"), kayitli.encode("utf-8"))
        except Exception:
            return False
    return kayitli == sifre_hashle(sifre)  # eski SHA-256 kaydı

def sifre_kontrol(sifre):
    if len(sifre) < 8: return "Şifre en az 8 karakter olmalıdır."
    if not any(c.isupper() for c in sifre): return "Şifre en az bir büyük harf içermelidir."
    if not any(c.isdigit() for c in sifre): return "Şifre en az bir rakam içermelidir."
    return None

def kullanicilari_yukle():
    try:
        res = supabase.table("kullanicilar").select("username, password_hash, email").execute()
        return {row["username"]: row for row in res.data}
    except: return {}

def kullanici_sifre_ozeti(username):
    """Hesap silmede şifreyi doğrulamak için. Google ile girenlerde boş döner."""
    try:
        res = supabase.table("kullanicilar").select("password_hash").eq("username", username).limit(1).execute()
        return (res.data[0].get("password_hash") or "") if res.data else ""
    except Exception:
        return ""

def kullanici_bul_eposta(email):
    try:
        res = supabase.table("kullanicilar").select("username").eq("email", email).limit(1).execute()
        return res.data[0]["username"] if res.data else None
    except: return None

def google_hazir_mi():
    """Streamlit'in Google girişi ayarlanmışsa True. Ayar: Secrets içinde [auth] bölümü."""
    try:
        return bool(dict(st.secrets.get("auth", {})).get("redirect_uri"))
    except Exception:
        return False

def verileri_yukle(username):
    default_data = {
        "gunluk_kayitlar": [], "aktivite_loglari": {},
        "profil": {"ad": "", "cinsiyet": "Kadın", "dogum_yili": 2000, "boy": 165, "mevcut_kilo": 60.0, "hedef_kilo": 55.0, "hedef_sure_ay": 2, "tema": "Koyu Cam", "amaclar": [], "setup_tamamlandi": False}
    }
    try:
        res = supabase.table("kullanici_verileri").select("data").eq("username", username).execute()
        if res.data: return res.data[0]["data"]
    except: pass
    return default_data

def verileri_kaydet(username):
    data = {"gunluk_kayitlar": st.session_state.gunluk_kayitlar, "aktivite_loglari": st.session_state.aktivite_loglari, "profil": st.session_state.profil}
    try: supabase.table("kullanici_verileri").upsert({"username": username, "data": data}).execute()
    except: pass

# Aktivite düzeyi çarpanları (yaygın kullanılan Harris-Benedict katsayıları)
AKTIVITE_DUZEYLERI = {
    "Hareketsiz (masa başı, çok az yürüyüş)": 1.2,
    "Az hareketli (haftada 1-3 gün egzersiz)": 1.375,
    "Orta hareketli (haftada 3-5 gün egzersiz)": 1.55,
    "Çok hareketli (haftada 6-7 gün egzersiz)": 1.725,
}

def yas_hesapla(p):
    return datetime.date.today().year - int(p.get("dogum_yili", 2000))

def haftalik_hiz(p):
    """Hedefe göre haftada kaç kilo verilmesi/alınması gerektiği (pozitif = kayıp)."""
    fark = float(p["mevcut_kilo"]) - float(p["hedef_kilo"])
    hafta = max(1.0, int(p.get("hedef_sure_ay", 1)) * 4.345)
    return fark / hafta

def hesapla_bmr_ve_hedef(p):
    yas = yas_hesapla(p)
    if p.get("cinsiyet", "Kadın") == "Kadın":
        bmr = (10 * float(p["mevcut_kilo"])) + (6.25 * float(p["boy"])) - (5 * yas) - 161
    else:
        bmr = (10 * float(p["mevcut_kilo"])) + (6.25 * float(p["boy"])) - (5 * yas) + 5

    # Günlük harcama, amaçtan değil AKTİVİTE DÜZEYİNDEN hesaplanır
    carpan = AKTIVITE_DUZEYLERI.get(p.get("aktivite", ""), 1.375)
    tdee = bmr * carpan

    kilo_farki = float(p["mevcut_kilo"]) - float(p["hedef_kilo"])
    gunluk_acik = (kilo_farki * 7700) / max(1, int(p.get("hedef_sure_ay", 1)) * 30)

    # Güvenli sınır: haftada 1 kilodan (günde ~1100 kcal açık) hızlı hedef kabul edilmez
    gunluk_acik = max(min(gunluk_acik, 1100.0), -700.0)

    hedef_kalori = tdee - gunluk_acik
    taban = 1200 if p.get("cinsiyet") == "Kadın" else 1500
    if yas < 18:
        # Gelişme çağında dinlenik metabolizmanın altına inilmez
        taban = max(taban, bmr)
    hedef_kalori = max(taban, hedef_kalori)
    return bmr, tdee, gunluk_acik, hedef_kalori

def guvenlik_uyarilari(p):
    """Hedefle ilgili gösterilmesi gereken uyarılar."""
    uyarilar = []
    hiz = haftalik_hiz(p)
    if hiz > 1.0:
        uyarilar.append(
            f"Hedefin haftada {hiz:.1f} kilo kayıp anlamına geliyor. Bu hızlı bir tempo; "
            "güvenli kabul edilen aralık genelde haftada 0,5-1 kilodur. Süreyi uzatmanı öneririm."
        )
    elif hiz < -0.75:
        uyarilar.append(
            f"Hedefin haftada {abs(hiz):.1f} kilo alım anlamına geliyor. Kas kazanmak için "
            "haftada 0,25-0,5 kilo daha dengeli bir tempodur."
        )
    if yas_hesapla(p) < 18:
        uyarilar.append(
            "18 yaşından küçüksün. Büyüme çağında kalori kısıtlamak gelişimi etkileyebilir; "
            "kilo hedefi koymadan önce bir doktora ya da diyetisyene danışmanı öneririm."
        )
    return uyarilar

# ----------------------------------------------------
# OTURUM YÖNETİMİ & TERTEMİZ AÇIK TEMA GİRİŞ EKRANI
# ----------------------------------------------------
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "aktif_kullanici" not in st.session_state: st.session_state.aktif_kullanici = ""
if "onboarding_step" not in st.session_state: st.session_state.onboarding_step = 1

# --- GOOGLE İLE GİRİŞ DÖNÜŞÜ ---
# Google'dan dönüldüğünde e-postaya bağlı hesap bulunur, yoksa oluşturulur.
if not st.session_state.giris_yapildi and google_hazir_mi():
    try:
        google_girisli = st.user.is_logged_in
    except Exception:
        google_girisli = False
    if google_girisli:
        g_mail = (getattr(st.user, "email", "") or "").strip().lower()
        if g_mail:
            kullanici_adi = kullanici_bul_eposta(g_mail)
            if not kullanici_adi:
                # E-postanın baş kısmından benzersiz bir kullanıcı adı türetilir
                taban = "".join(c for c in g_mail.split("@")[0] if c.isalnum()) or "kullanici"
                mevcutlar = set(kullanicilari_yukle())
                kullanici_adi = taban
                ek = 1
                while kullanici_adi in mevcutlar:
                    ek += 1
                    kullanici_adi = f"{taban}{ek}"
                try:
                    supabase.table("kullanicilar").insert({
                        "username": kullanici_adi, "password_hash": "", "email": g_mail}).execute()
                except Exception as e:
                    st.error(f"Hesap oluşturulamadı: {e}")
                    kullanici_adi = None
            if kullanici_adi:
                st.session_state.giris_yapildi = True
                st.session_state.aktif_kullanici = kullanici_adi
                st.session_state.update(verileri_yukle(kullanici_adi))
                st.rerun()

if not st.session_state.giris_yapildi:
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        :root { color-scheme: light !important; }
        [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f0 100%) !important; color-scheme: light !important; }
        .nova-logo-giris {
            font-family: 'Playfair Display', serif;
            font-size: clamp(2.1rem, 10.5vw, 5rem);
            letter-spacing: clamp(5px, 3vw, 25px);
            white-space: nowrap; text-align: center; font-weight: 700;
            margin-top: 5vh; color: #1a1a1a !important;
        }
        p, label, span { color: #333333 !important; font-family: 'Plus Jakarta Sans', sans-serif; }
        [class*="st-key-novakart"] { background: rgba(255, 255, 255, 0.95) !important; padding: 32px; border-radius: 28px; border: 1px solid rgba(0,0,0,0.08); box-shadow: 0 20px 40px rgba(0,0,0,0.08); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); }
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
        with st.container(key="novakart1"):
            tab_giris, tab_kayit = st.tabs(["Giriş Yap", "Kayıt Ol"])
            users = kullanicilari_yukle()

            with tab_giris:
                g_user = st.text_input("Kullanıcı Adı", key="g_user").strip().lower()
                g_pass = st.text_input("Şifre", type="password", key="g_pass")
                if st.button("Giriş Yap", key="btn_giris", use_container_width=True):
                    kayit = users.get(g_user)
                    if kayit and sifre_dogrula(g_pass, kayit.get("password_hash")):
                        # Eski SHA-256 kaydı ise sessizce bcrypt'e yükseltilir
                        if not str(kayit.get("password_hash", "")).startswith("$2"):
                            try:
                                supabase.table("kullanicilar").update(
                                    {"password_hash": sifre_olustur(g_pass)}).eq("username", g_user).execute()
                            except Exception:
                                pass
                        st.session_state.giris_yapildi = True
                        st.session_state.aktif_kullanici = g_user
                        st.session_state.update(verileri_yukle(g_user))
                        st.rerun()
                    else: st.error("Hatalı kullanıcı adı veya şifre.")

            with tab_kayit:
                k_user = st.text_input("Yeni Kullanıcı Adı", key="k_user").strip().lower()
                k_mail = st.text_input("E-posta (şifreni unutursan gerekli)", key="k_mail").strip().lower()
                k_pass = st.text_input("Şifre (en az 8 karakter, bir büyük harf ve bir rakam)", type="password", key="k_pass")
                if st.button("Hesap Oluştur", key="btn_kayit", use_container_width=True):
                    hata = sifre_kontrol(k_pass)
                    if hata:
                        st.error(hata)
                    elif not k_user:
                        st.error("Kullanıcı adı boş olamaz.")
                    elif k_user in users:
                        st.error("Bu kullanıcı adı zaten alınmış.")
                    elif k_mail and ("@" not in k_mail or "." not in k_mail.split("@")[-1]):
                        st.error("E-posta adresi geçerli görünmüyor.")
                    else:
                        supabase.table("kullanicilar").insert({
                            "username": k_user, "password_hash": sifre_olustur(k_pass),
                            "email": k_mail or None,
                        }).execute()
                        # Hesap açılır açılmaz içeri al; tekrar giriş yaptırma
                        st.session_state.giris_yapildi = True
                        st.session_state.aktif_kullanici = k_user
                        st.session_state.update(verileri_yukle(k_user))
                        st.rerun()

            if google_hazir_mi():
                st.markdown("<p style='text-align:center; margin:18px 0 8px; color:#888 !important;'>ya da</p>",
                            unsafe_allow_html=True)
                if st.button("Google ile devam et", key="btn_google", use_container_width=True):
                    st.login()

else:
    aktif_user = st.session_state.aktif_kullanici
    p = st.session_state.profil
    aktif_tema = p.get("tema", "Koyu Cam")
    if aktif_tema not in TEMA_AYARLARI: aktif_tema = "Koyu Cam"
    tema = TEMA_AYARLARI[aktif_tema]
    bg_url = f"https://raw.githubusercontent.com/azraam2008-lgtm/NOVA/main/{tema['bg_image']}"

    # STREAMLIT KOYU MOD ÇAKIŞMASINI %100 BİTİREN GÜNCEL CSS EKLENDİ
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        
        /* CİHAZ KOYU MODDA OLSA BİLE TEMA BOZULMASINI ENGELLEYEN KÖK AYAR */
        :root {{ color-scheme: light !important; }}
        
        [data-testid="stAppViewContainer"] {{
            background-color: {tema['fallback_bg']} !important;
            background-image: linear-gradient({tema['scrim']}, {tema['scrim']}), url("{bg_url}") !important;
            background-size: cover; background-position: center; background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0) !important; }}
        
        .nova-header {{
            color: {tema['text_color']} !important; font-family: 'Playfair Display', serif;
            font-size: clamp(2.1rem, 10.5vw, 5rem);
            letter-spacing: clamp(5px, 2.8vw, 20px);
            white-space: nowrap; text-align: center; font-weight: 700; margin-top: -20px;
        }}
        .nova-header.kucuk {{ font-size: clamp(1.8rem, 8vw, 3.5rem); margin-top: 20px; }}
        .nova-user {{
            color: {tema['text_color']} !important; text-align: center;
            font-size: clamp(1rem, 4vw, 1.4rem); letter-spacing: clamp(2px, 1vw, 4px);
            text-transform: uppercase; margin-bottom: 5px; opacity: 0.9; font-weight: 600;
        }}
        .nova-tarih {{
            color: {tema['text_color']} !important; text-align: center;
            font-size: clamp(0.85rem, 3vw, 1rem); letter-spacing: clamp(1px, 0.5vw, 2px);
            margin-bottom: 35px; opacity: 0.7;
        }}
        
        /* KARTLAR: artık gerçek kapsayıcılar, içerik gerçekten kartın içinde */
        [class*="st-key-novakart"] {{
            background: {tema['card_bg']} !important;
            padding: 32px; border-radius: 28px;
            backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px);
            margin-bottom: 28px; border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 15px 50px rgba(0,0,0,0.35);
        }}
        
        .info-box {{ background: rgba(255,255,255,0.1) !important; border-left: 4px solid {tema['text_color']} !important; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: {tema['text_color']} !important; font-weight: 600; }}
        
        /* BÜTÜN YAZILARI TEMA RENGİNE ZORLAMA (KOYU MOD/AÇIK MOD ÇAKIŞMASINI KESİN OLARAK ENGELLER) */
        [class*="st-key-novakart"] p, [class*="st-key-novakart"] h1, [class*="st-key-novakart"] h2,
        [class*="st-key-novakart"] h3, [class*="st-key-novakart"] h4,
        [class*="st-key-novakart"] td, [class*="st-key-novakart"] th,
        [class*="st-key-novakart"] span, [class*="st-key-novakart"] label,
        div[data-testid="stMarkdownContainer"] p, div[data-testid="stMarkdownContainer"] h2, 
        div[data-testid="stMarkdownContainer"] h3, div[data-testid="stMarkdownContainer"] h4,
        div[data-testid="stWidgetLabel"] p, label[data-baseweb="radio"] div,
        [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p,
        [data-testid="stMetricValue"], [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] p, [data-testid="stExpander"] summary p,
        [data-testid="stChatMessageContent"], [data-testid="stChatMessageContent"] p,
        [data-testid="stToggle"] label p, div[data-testid="stMarkdownContainer"] li {{
            color: {tema['text_color']} !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }}

        /* Metrik delta rozetleri koyu zeminde okunsun */
        [data-testid="stMetricDelta"] {{ background: transparent !important; }}
        [data-testid="stMetricDelta"] div {{ font-weight: 700 !important; }}

        /* Sohbet balonları */
        [data-testid="stChatMessage"] {{
            background: rgba(255,255,255,0.07) !important;
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 16px;
        }}

        /* Grafiklerin zemini karta uysun */
        [data-testid="stVegaLiteChart"], [data-testid="stVegaLiteChart"] canvas,
        [data-testid="stVegaLiteChart"] svg {{ background: transparent !important; }}

        /* Bilgi, uyarı ve hata kutuları koyu zeminde okunsun (anlamı renkli kenarla korunur) */
        [data-testid="stAlertContainer"] {{
            background: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.16) !important;
            border-radius: 12px !important;
        }}
        [data-testid="stAlertContainer"] p, [data-testid="stAlertContainer"] div,
        [data-testid="stAlertContainer"] span, [data-testid="stAlertContainer"] li {{
            color: {tema['text_color']} !important;
        }}
        [data-testid="stAlertContentSuccess"] {{ border-left: 4px solid #34c759 !important; padding-left: 12px; }}
        [data-testid="stAlertContentInfo"] {{ border-left: 4px solid #007aff !important; padding-left: 12px; }}
        [data-testid="stAlertContentWarning"] {{ border-left: 4px solid #ffcc00 !important; padding-left: 12px; }}
        [data-testid="stAlertContentError"] {{ border-left: 4px solid #ff3b30 !important; padding-left: 12px; }}
        
        /* GİRİŞ ALANLARI KESİN BEYAZ ZEMİN, SİYAH YAZI OLMALIDIR */
        div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, 
        input[type="text"], input[type="number"], textarea {{ 
            background-color: #ffffff !important; 
            color: #000000 !important; 
            border-radius: 12px !important; 
            border: 2px solid rgba(0,0,0,0.15) !important; 
        }}
        /* İnput içi yazılar ve seçim kutusu etiketleri görünür kılınır */
        div[data-baseweb="select"] span, input, input::placeholder {{ color: #000000 !important; font-weight: bold; }}
        
        /* DROPDOWN (AÇILIR LİSTELER VE POPOVER) KOYU MOD DÜZELTMESİ (Örn: Cinsiyet seçimi kutusu içeriği) */
        div[data-baseweb="popover"], ul[role="listbox"], ul[role="listbox"] li, ul[role="listbox"] span {{
            background-color: #ffffff !important;
            color: #000000 !important;
        }}
        
        /* MULTISELECT (ÇOKLU SEÇİM) TAG'LERİ DÜZELTMESİ (Örn: Amaç seçimindeki butonlar) */
        span[data-baseweb="tag"] {{
            background-color: {tema['text_color']} !important;
            color: {tema['fallback_bg']} !important;
        }}
        span[data-baseweb="tag"] span {{
            color: {tema['fallback_bg']} !important;
        }}
        
        /* Sayı inputlarının yanındaki + ve - tuşları sorununu çözer */
        div[data-baseweb="input"] button {{
            color: #000000 !important;
        }}
        
        /* TAB VE BUTON ESTETİĞİ */
        button[data-baseweb="tab"] {{ background-color: transparent !important; color: {tema['text_color']} !important; font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 1.1rem !important; font-weight: 600 !important; opacity: 0.85; }}
        button[data-baseweb="tab"][aria-selected="true"] {{ border-bottom: 3px solid {tema['text_color']} !important; font-weight: 800 !important; opacity: 1.0 !important; }}
        div.stButton > button:first-child {{ background: {tema['card_bg']} !important; color: {tema['text_color']} !important; border: 1px solid rgba(255,255,255,0.3) !important; font-weight: 700 !important; border-radius: 16px !important; padding: 10px 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.2); backdrop-filter: blur(10px); transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); }}
        div.stButton > button:first-child:hover {{ transform: translateY(-2px); background: {tema['text_color']} !important; color: {tema['fallback_bg']} !important; border-color: {tema['text_color']} !important; box-shadow: 0 12px 30px rgba(0,0,0,0.3); }}
        
        .ring-container {{ width: 180px; height: 180px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; }}
        .ring-inner {{ width: 140px; height: 140px; border-radius: 50%; background: {tema['card_bg']} !important; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
        .ring-val {{ font-size: 2rem; font-weight: 800; margin-bottom: -5px; color: {tema['text_color']} !important; }}
        .ring-lbl {{ font-size: 1rem; opacity: 0.8; text-transform: uppercase; letter-spacing: 2px; color: {tema['text_color']} !important; }}
        table {{ width: 100%; font-size: 1.1rem; background: transparent; border-collapse: collapse; }}

        /* TELEFON BOYUTU */
        @media (max-width: 640px) {{
            [class*="st-key-novakart"] {{ padding: 16px !important; border-radius: 20px !important; margin-bottom: 16px !important; }}
            div[data-testid="stMarkdownContainer"] h2 {{ font-size: 1.4rem !important; }}
            div[data-testid="stMarkdownContainer"] h3 {{ font-size: 1.15rem !important; }}
            table {{ font-size: 0.92rem !important; }}
            th, td {{ padding: 8px 6px !important; }}
            th {{ font-size: 1rem !important; }}
            .ring-container {{ width: 150px !important; height: 150px !important; }}
            .ring-inner {{ width: 116px !important; height: 116px !important; }}
            .ring-val {{ font-size: 1.6rem !important; }}
            .ring-lbl {{ font-size: 0.8rem !important; }}
            [data-testid="stMetricValue"] {{ font-size: 1.4rem !important; }}
            button[data-baseweb="tab"] {{ font-size: 0.9rem !important; padding: 0 8px !important; }}
            [data-testid="stMainBlockContainer"] {{ padding-left: 0.8rem !important; padding-right: 0.8rem !important; }}
        }}
        th, td {{ padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.2); text-align: left; color: {tema['text_color']} !important; }}
        th {{ font-weight: 800; font-size: 1.2rem; opacity: 0.9; }}
        </style>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # FATSECRET TARZI DETAYLI ONBOARDING SÜRECİ
    # ----------------------------------------------------
    if not p.get("setup_tamamlandi", False):
        st.markdown('<div class="nova-header kucuk">N O V A</div>', unsafe_allow_html=True)
        with st.container(key="novakart2"):

            step = st.session_state.onboarding_step

            if step == 1:
                st.markdown("<h2 style='text-align:center;'>Tanıştığımıza memnun oldum,<br>Nova'ya Hoş Geldin! </h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; opacity:0.9;'>Hedeflerine ulaşmanda sana yardımcı olmak için buradayız.<br>Başlamak için birkaç kısa sorumuz olacak.</p>", unsafe_allow_html=True)
                st.markdown('<div class="info-box">Cevapların, hedeflerini anlamamıza ve uygulamayı senin için kişiselleştirmemize yardımcı olacak.</div>', unsafe_allow_html=True)
                if st.button("Başla ", use_container_width=True):
                    st.session_state.onboarding_step = 2
                    st.rerun()

            elif step == 2:
                st.markdown("<h2 style='text-align:center;'>Merhaba! Adın nedir?</h2>", unsafe_allow_html=True)
                ad_input = st.text_input("Adını Gir", value=p.get("ad", ""))
                st.markdown('<div class="info-box">Nova uygulamasını sana özel hale getirmek ve sana hitap edebilmek için adını kullanacağız.</div>', unsafe_allow_html=True)

                b1, b2 = st.columns(2)
                if b1.button("Geri"): st.session_state.onboarding_step = 1; st.rerun()
                if b2.button("İleri "):
                    if ad_input:
                        st.session_state.profil["ad"] = ad_input
                        st.session_state.onboarding_step = 3
                        st.rerun()
                    else: st.error("Lütfen adını gir.")

            elif step == 3:
                st.markdown(f"<h2 style='text-align:center;'>Nova'yı Hangi Amaçla Kullanmak İstiyorsun {p.get('ad', '')}?</h2>", unsafe_allow_html=True)
                amaclar = st.multiselect("Hedeflerin (Birden fazla seçebilirsin)", ["Kilo vermek istiyorum", "Kilomu korumak istiyorum", "Kilo almak istiyorum", "Kas kazanmak istiyorum", "Sağlıklı beslenmek istiyorum"], default=p.get("amaclar", []))

                b1, b2 = st.columns(2)
                if b1.button("Geri"): st.session_state.onboarding_step = 2; st.rerun()
                if b2.button("İleri "):
                    st.session_state.profil["amaclar"] = amaclar
                    st.session_state.onboarding_step = 4
                    st.rerun()

            elif step == 4:
                st.markdown("<h2 style='text-align:center;'>Cinsiyetin nedir?</h2>", unsafe_allow_html=True)
                cinsiyet = st.selectbox("Seçimini yap:", ["Kadın", "Erkek"], index=["Kadın", "Erkek"].index(p.get("cinsiyet", "Kadın")))
                st.markdown('<div class="info-box">Cinsiyetin, vücudunun günlük enerji ihtiyacını hesaplamamızı doğrudan etkiler.</div>', unsafe_allow_html=True)

                b1, b2 = st.columns(2)
                if b1.button("Geri"): st.session_state.onboarding_step = 3; st.rerun()
                if b2.button("İleri "):
                    st.session_state.profil["cinsiyet"] = cinsiyet
                    st.session_state.onboarding_step = 5
                    st.rerun()

            elif step == 5:
                st.markdown("<h2 style='text-align:center;'>Doğum yılın ne?</h2>", unsafe_allow_html=True)
                mevcut_yil = datetime.date.today().year
                dogum_yili = st.number_input("Yıl", min_value=1920, max_value=mevcut_yil-13, value=int(p.get("dogum_yili", 2000)))
                yas = mevcut_yil - dogum_yili
                st.markdown(f"<h4 style='text-align:center;'>Şu an <b>{yas}</b> yaşındasın.</h4>", unsafe_allow_html=True)
                st.markdown('<div class="info-box">Yaşın, vücudunun her gün ne kadar enerjiye (BMR) ihtiyaç duyduğunu etkiler.</div>', unsafe_allow_html=True)
                if yas < 18:
                    st.warning(
                        "18 yaşından küçüksün. Büyüme çağında kalori kısıtlamak gelişimi etkileyebilir. "
                        "Nova senin için günlük hedefi dinlenik metabolizmanın altına indirmeyecek, ama "
                        "kilo hedefi koymadan önce bir doktora ya da diyetisyene danışmanı öneririm."
                    )

                b1, b2 = st.columns(2)
                if b1.button("Geri"): st.session_state.onboarding_step = 4; st.rerun()
                if b2.button("İleri "):
                    st.session_state.profil["dogum_yili"] = dogum_yili
                    st.session_state.onboarding_step = 6
                    st.rerun()

            elif step == 6:
                st.markdown("<h2 style='text-align:center;'>Boyun kaç?</h2>", unsafe_allow_html=True)
                boy = st.number_input("Boy (cm)", min_value=130, max_value=220, value=int(p.get("boy", 165)))
                st.markdown('<div class="info-box">Boyun, vücudunun her gün ne kadar enerji harcadığını etkiler.</div>', unsafe_allow_html=True)

                b1, b2 = st.columns(2)
                if b1.button("Geri"): st.session_state.onboarding_step = 5; st.rerun()
                if b2.button("İleri "):
                    st.session_state.profil["boy"] = boy
                    st.session_state.onboarding_step = 7
                    st.rerun()

            elif step == 7:
                st.markdown("<h2 style='text-align:center;'>Şu andaki kilon ne?</h2>", unsafe_allow_html=True)
                mevcut_kilo = st.number_input("Kilo (kg)", min_value=35.0, max_value=250.0, value=float(p.get("mevcut_kilo", 60.0)), step=0.5)
                st.markdown('<div class="info-box">Bu bilgi, bulunduğun noktaya göre kalori hedefini hesaplamamıza yardımcı olur. Şu anki kilonu tam bilmiyorsan en iyi tahminini gir, daha sonra uygulamada Pazar günleri güncelleyebilirsin.</div>', unsafe_allow_html=True)

                b1, b2 = st.columns(2)
                if b1.button("Geri"): st.session_state.onboarding_step = 6; st.rerun()
                if b2.button("İleri "):
                    st.session_state.profil["mevcut_kilo"] = mevcut_kilo
                    st.session_state.onboarding_step = 8
                    st.rerun()

            elif step == 8:
                st.markdown("<h2 style='text-align:center;'>Hedef kilon nedir?</h2>", unsafe_allow_html=True)
                hedef_kilo = st.number_input("Hedef Kilo (kg)", min_value=35.0, value=float(p.get("hedef_kilo", 55.0)), step=0.5)
                hedef_sure = st.number_input("Hedefe Ulaşma Süresi (Ay)", min_value=1, value=int(p.get("hedef_sure_ay", 2)))

                aktivite_listesi = list(AKTIVITE_DUZEYLERI.keys())
                mevcut_aktivite = p.get("aktivite", aktivite_listesi[1])
                if mevcut_aktivite not in aktivite_listesi:
                    mevcut_aktivite = aktivite_listesi[1]
                aktivite = st.selectbox("Günlük hareket düzeyin", aktivite_listesi,
                                        index=aktivite_listesi.index(mevcut_aktivite))
                st.markdown('<div class="info-box">Hareket düzeyin, günde ne kadar enerji harcadığını belirleyen en önemli etken. Adım ve egzersiz kayıtların bunun üzerine eklenir.</div>', unsafe_allow_html=True)

                sec_tema = st.selectbox("Nova Deneyimin İçin Bir Tema Seç", list(TEMA_AYARLARI.keys()), index=list(TEMA_AYARLARI.keys()).index(aktif_tema))

                # Hedef temposu güvenli mi, daha hesaplamadan göster
                onizleme = dict(p); onizleme.update({"hedef_kilo": hedef_kilo, "hedef_sure_ay": hedef_sure})
                hiz = haftalik_hiz(onizleme)
                if abs(hiz) > 0.05:
                    yon = "kayıp" if hiz > 0 else "alım"
                    st.caption(f"Bu hedef haftada yaklaşık {abs(hiz):.2f} kilo {yon} demek.")
                if hiz > 1.0:
                    st.warning("Bu tempo hızlı. Güvenli aralık genelde haftada 0,5-1 kilodur; süreyi uzatmanı öneririm.")

                b1, b2 = st.columns(2)
                if b1.button("Geri"): st.session_state.onboarding_step = 7; st.rerun()
                if b2.button("Kalori Hedefimi Hesapla "):
                    st.session_state.profil.update({"hedef_kilo": hedef_kilo, "hedef_sure_ay": hedef_sure,
                                                    "aktivite": aktivite, "tema": sec_tema})
                    st.session_state.onboarding_step = 9
                    st.rerun()

            elif step == 9:
                st.markdown(f"<h2 style='text-align:center;'>Paylaştığın için teşekkürler, {p.get('ad', '')} </h2>", unsafe_allow_html=True)
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
                    <p style="opacity:0.8; font-size: 0.9rem; text-align:center;"><i>Nova Kalori Hedefin, amacına ulaşmak için her gün kaç kalori tüketmen gerektiğini gösterir. Her gün bu hedefe yakın miktarda tüketirsen başarıya ulaşırsın.</i></p>
                </div><br>
                """, unsafe_allow_html=True)

                for uyari in guvenlik_uyarilari(p):
                    st.warning(uyari)
                st.caption("Nova bir sağlık uygulaması değildir ve tıbbi tavsiye vermez. "
                           "Hesaplamalar genel formüllere dayanan tahminlerdir.")

                b1, b2 = st.columns(2)
                if b1.button("Geri"): st.session_state.onboarding_step = 8; st.rerun()
                if b2.button("Harika, Uygulamaya Başla!", type="primary"):
                    st.session_state.profil["setup_tamamlandi"] = True
                    verileri_kaydet(aktif_user)
                    st.rerun()

        st.stop()

    # ----------------------------------------------------
    # ANA EKRAN
    # ----------------------------------------------------
    gosterilecek_isim = p.get("ad", aktif_user).capitalize()
    st.markdown('<div class="nova-header">N O V A</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="nova-user">{gosterilecek_isim}</div>', unsafe_allow_html=True)
    
    # Türkçe Tarih Gösterimi
    aylar_tr = {1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"}
    gunler_tr = {0: "Pazartesi", 1: "Salı", 2: "Çarşamba", 3: "Perşembe", 4: "Cuma", 5: "Cumartesi", 6: "Pazar"}
    bugun_dt = datetime.date.today()
    tarih_str = f"{bugun_dt.day} {aylar_tr[bugun_dt.month]} {bugun_dt.year} {gunler_tr[bugun_dt.weekday()]}"
    st.markdown(f'<div class="nova-tarih">{tarih_str}</div>', unsafe_allow_html=True)

    # ----------------------------------------------------
    # PAZAR GÜNÜ TARTI & HEDEF GÜNCELLEME KONTROLÜ
    # ----------------------------------------------------
    bugun_pazar_mu = (bugun_dt.weekday() == 6)
    pazar_guncellendi_key = f"pazar_tartildi_{str(bugun_dt)}"
    son_tarti = p.get("son_tarti_tarihi", "")
    
    if bugun_pazar_mu and son_tarti != str(bugun_dt) and not st.session_state.get(pazar_guncellendi_key, False):
        st.markdown(f"""
            <div class="calai-card" style="border: 2px solid #ffcc00; background: rgba(50, 40, 0, 0.9);">
                <h3 style="color: #ffcc00 !important;">Pazar Günü Tartı ve Durum Güncellemesi!</h3>
                <p>Harika bir hafta geçirdik! Haftayı kapatmadan önce bugün sabah tartıldığın güncel kilonu girerek hedeflerini ve kalori planını yeni kilosuna göre güncelleyebilirsin.</p>
            </div>
        """, unsafe_allow_html=True)
        
        yeni_tartilinan_kilo = st.number_input("Bugünkü Güncel Kilon (kg)", min_value=30.0, max_value=250.0, value=float(p["mevcut_kilo"]), step=0.1, key="pazar_kilo_input")
        if st.button("Kilomu Güncelle ve Hedeflerimi Yenile", use_container_width=True):
            p["mevcut_kilo"] = yeni_tartilinan_kilo
            p["son_tarti_tarihi"] = str(bugun_dt)
            p.setdefault("kilo_gecmisi", []).append({"tarih": str(bugun_dt), "kilo": yeni_tartilinan_kilo})
            st.session_state[pazar_guncellendi_key] = True
            verileri_kaydet(aktif_user)
            st.success("Harika! Kilon güncellendi ve haftalık kalori/makro planın yeni hedeflerine göre yeniden hesaplandı!")
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    c_sol, c_orta, c_sag = st.columns([1, 10, 1])
    with c_orta:
        t_col1, t_col2 = st.columns([8, 2])
        with t_col1:
            secilen_tarih = str(st.date_input("Geçmiş Tarih İnceleme", datetime.date.today()))
        with t_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Ayarlar", use_container_width=True):
                st.session_state.profil["setup_tamamlandi"] = False
                st.session_state.onboarding_step = 2
                st.rerun()

        if secilen_tarih not in st.session_state.aktivite_loglari:
            st.session_state.aktivite_loglari[secilen_tarih] = {"adim": 0, "su": 0.0, "egzersiz_kalori": 0}
        curr_aktivite = st.session_state.aktivite_loglari[secilen_tarih]

        tab_ozet, tab_gelisim, tab_ai_ogun, tab_ai_koc, tab_ai_asistan = st.tabs(
            ["Günlük Özet", "Gelişim", "Öğün Tarama", "Antrenman Koçu", "Asistan"])

        # ==========================================
        # 1. SEKME: GÜNLÜK ÖZET & MANUEL EKLEME
        # ==========================================
        with tab_ozet:
            # KALORİ TABLOSU
            with st.container(key="novakart3"):
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
                    <tr><td><span style="display:inline-block;width:9px;height:9px;border-radius:2px;background:#007aff;margin-right:10px;vertical-align:middle;"></span>Günlük Hedef Kalori Bütçen</td><td style="text-align: right; color: #007aff !important;"><b>{round(hedef_kalori_alim)} kcal</b></td></tr>
                    <tr><td><span style="display:inline-block;width:9px;height:9px;border-radius:2px;background:#ff3b30;margin-right:10px;vertical-align:middle;"></span>Bugüne Kadar Yediklerin</td><td style="text-align: right; color: #ff3b30 !important;"><b>- {round(top_kalori)} kcal</b></td></tr>
                    <tr><td><span style="display:inline-block;width:9px;height:9px;border-radius:2px;background:#34c759;margin-right:10px;vertical-align:middle;"></span>Hareket ve Egzersizle Kazandıkların</td><td style="text-align: right; color: #34c759 !important;"><b>+ {round(aktif_harcanan)} kcal</b></td></tr>
                    <tr style="border-top: 2px solid rgba(255,255,255,0.5);">
                        <td style="font-size: 1.3rem; font-weight: 800;">Geriye Kalan Yeme Hakkın</td>
                        <td style="text-align: right; font-size: 1.3rem; font-weight: 800;">{round(kalan_kalori)} kcal</td>
                    </tr>
                </table><br>
                """, unsafe_allow_html=True)

                if kalan_kalori < 0: 
                    st.error(f"Limitini {abs(round(kalan_kalori))} kcal aştın. Hedefe dönmek için biraz egzersiz yapmalısın!")
                else: 
                    st.success(f"Harika gidiyorsun! Günün geri kalanı için {round(kalan_kalori)} kcal yeme hakkın duruyor.")

                def render_makro(isim, mevcut, hedef, renk):
                    yuzde = min((mevcut / max(hedef, 1)) * 100, 100)
                    return f"""
                    <div style="margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.95rem; margin-bottom: 5px;">
                            <span>{isim}</span>
                            <span>{round(mevcut)}g / {round(hedef)}g</span>
                        </div>
                        <div style="width: 100%; background-color: rgba(255,255,255,0.15); border-radius: 4px; height: 6px;">
                            <div style="width: {yuzde}%; background-color: {renk}; height: 100%; border-radius: 4px;"></div>
                        </div>
                    </div>
                    """
                st.markdown("<h4>Günlük Makro İhtiyaçları</h4>", unsafe_allow_html=True)
                st.markdown(render_makro("Protein", top_pro, hedef_pro, "#ff3b30"), unsafe_allow_html=True)
                st.markdown(render_makro("Karbonhidrat", top_karb, hedef_karb, "#007aff"), unsafe_allow_html=True)
                st.markdown(render_makro("Yağ", top_yag, hedef_yag, "#ffcc00"), unsafe_allow_html=True)


            # YEMEK EKLEME: arama, barkod, favoriler, kendi yemeğin
            with st.container(key="novakart4"):
                st.markdown("<h2 style='font-size: 2rem;'>Yemek Ekle</h2>", unsafe_allow_html=True)

                secilen_ogun = st.selectbox("Hangi öğüne eklenecek?",
                                            ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"], key="db_ogun")
                yeni_kayitlar = yemek_arama_sayfasi(df_yemek, supabase, aktif_user, secilen_tarih,
                                                    secilen_ogun, st.session_state.gunluk_kayitlar)
                if yeni_kayitlar:
                    st.session_state.gunluk_kayitlar.extend(yeni_kayitlar)
                    verileri_kaydet(aktif_user)
                    st.toast(f"{len(yeni_kayitlar)} kalem {secilen_ogun.lower()} öğününe eklendi")
                    st.rerun()

                st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 25px 0;'>", unsafe_allow_html=True)
                st.markdown("<h3>Bugünkü Öğünlerin</h3>", unsafe_allow_html=True)
                for ogun_turu in ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"]:
                    ogun_yemekleri = [(i, k) for i, k in enumerate(st.session_state.gunluk_kayitlar) if k.get("Tarih") == secilen_tarih and k.get("Öğün") == ogun_turu]
                    if ogun_yemekleri:
                        st.markdown(f"**{ogun_turu}**")
                        for i, k in ogun_yemekleri:
                            c1, c2 = st.columns([10, 1])
                            c1.markdown(f"• {k['Tarif']} — *{k['Kalori']} kcal*")
                            if c2.button("Sil", key=f"sil_{i}", help="Bu öğünü günlükten çıkar"):
                                st.session_state.gunluk_kayitlar.pop(i)
                                verileri_kaydet(aktif_user)
                                st.rerun()
            

            # BUGÜNKÜ EGZERSİZİN
            with st.container(key="novakart5"):
                st.markdown("<h2 style='font-size: 2rem;'>Bugünkü Egzersizin</h2>", unsafe_allow_html=True)
                bugunku_antrenmanlar = curr_aktivite.get("antrenmanlar", [])
                if bugunku_antrenmanlar:
                    for a in bugunku_antrenmanlar:
                        hareketler = a.get("hareketler", [])
                        toplam_set = sum(int(h.get("sets_done", 0) or 0) for h in hareketler)
                        st.markdown(f"**{a.get('gun', 'Antrenman')}** - {toplam_set} set")
                        for h in hareketler:
                            tekrar = f" ({h['reps']})" if h.get("reps") else ""
                            st.caption(f"{h.get('name', h.get('id', ''))} - {h.get('sets_done', 0)} set{tekrar}")
                else:
                    st.caption("Bugün kaydedilmiş antrenman yok. Antrenman Koçu sekmesinden plan yapıp tamamladığın setleri girebilirsin.")

                ek_kalori = st.number_input(
                    "Başka bir egzersiz yaptıysan yaktığın tahmini kalori",
                    min_value=0, max_value=2000, value=int(curr_aktivite.get("egzersiz_kalori", 0)), step=25,
                    help="Koştun, yüzdün ya da bisiklete bindiysen buraya yazabilirsin. Üzerine eklemez, bu sayıyı yazar.")
                if st.button("Egzersiz kalorisini kaydet", use_container_width=True):
                    curr_aktivite["egzersiz_kalori"] = int(ek_kalori)
                    verileri_kaydet(aktif_user)
                    st.rerun()


            with st.container(key="novakart6"):
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
                    yeni_adim = st.number_input("Bugünkü toplam adımın", min_value=0, max_value=100000,
                                                value=int(curr_aktivite.get("adim", 0)), step=500,
                                                help="Telefonundaki sağlık uygulamasında yazan günlük toplamı gir. Üzerine eklemez, bu sayıyı yazar.")
                    if st.button("Adımı Kaydet", use_container_width=True):
                        curr_aktivite["adim"] = int(yeni_adim)
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
                    su_secim = st.number_input("Eklenecek su (litre)", min_value=0.0, max_value=3.0,
                                               value=0.25, step=0.25,
                                               help="İçtikçe ekle. Bir bardak yaklaşık 0,25 litredir.")
                    sc1, sc2 = st.columns([3, 1])
                    if sc1.button("Suyu Ekle", use_container_width=True):
                        curr_aktivite["su"] = round(curr_aktivite.get("su", 0.0) + su_secim, 2)
                        verileri_kaydet(aktif_user)
                        st.rerun()
                    if sc2.button("Sıfırla", use_container_width=True, help="Bugünkü su sayacını sıfırla"):
                        curr_aktivite["su"] = 0.0
                        verileri_kaydet(aktif_user)
                        st.rerun()

            # HESAP VE VERİLERİN
            with st.container(key="novakart7"):
                st.markdown("<h2 style='font-size: 2rem;'>Hesap ve Verilerin</h2>", unsafe_allow_html=True)
                hesap_bolumu(supabase, aktif_user, st.session_state.gunluk_kayitlar,
                             st.session_state.aktivite_loglari, p,
                             sifre_dogrula=sifre_dogrula,
                             sifre_ozeti=kullanici_sifre_ozeti(aktif_user))


        with tab_gelisim:
            with st.container(key="novakart8"):
                st.markdown("<h2 style='font-size: 2rem; margin-bottom: 20px;'>Gelişimin</h2>", unsafe_allow_html=True)
                gelisim_sayfasi(st.session_state.gunluk_kayitlar, st.session_state.aktivite_loglari,
                                p, hedef_kalori_alim, bmr, tema)


        with tab_ai_ogun:
            with st.container(key="novakart9"):
                secilen_ogun_ai = st.selectbox("Hangi Öğün İçin Tarama Yapıyorsun?", ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"], key="ai_ogun_sec")
                totals = meal_scan_page()
                if totals:
                    for item in totals["items"]:
                        st.session_state.gunluk_kayitlar.append({
                            "Tarih": secilen_tarih, "Öğün": secilen_ogun_ai, "Tarif": f"{item['Yemek']}",
                            "Kalori": float(item["Kalori"]), "Protein": float(item["Protein (g)"]), 
                            "Karbonhidrat": float(item["Karb. (g)"]), "Yağ": float(item["Yağ (g)"])
                        })
                    st.session_state.pop("scan_result", None)  # aynı tarama ikinci kez eklenmesin
                    verileri_kaydet(aktif_user)
                    st.toast(f"{totals['kcal']} kcal günlüğüne eklendi")
                    st.rerun()

        with tab_ai_koc:
            with st.container(key="novakart10"):
                log = coach_page()
                if log:
                    toplam_set = sum(int(h.get("sets_done", 0)) for h in log["exercises"])
                    tahmini_kcal = int(min(400, max(60, toplam_set * 8)))  # kaba tahmin: set başına ~8 kcal
                    curr_aktivite["egzersiz_kalori"] = curr_aktivite.get("egzersiz_kalori", 0) + tahmini_kcal
                    curr_aktivite.setdefault("antrenmanlar", []).append({"gun": log["day"], "hareketler": log["exercises"]})
                    verileri_kaydet(aktif_user)
                    st.success(f"Antrenman kaydedildi: {toplam_set} set, yaklaşık {tahmini_kcal} kcal günlüğüne eklendi.")

        with tab_ai_asistan:
            with st.container(key="novakart11"):
                ask_page(p)
