import datetime
import hashlib
import json
import pandas as pd
import streamlit as st
from PIL import Image
from supabase import create_client, Client

# --- YENİ AI MODÜLLERİ ---
from meal_scan import meal_scan_page
from nova_pages import coach_page, ask_page

# Favicon olarak Kuğu (Swan) ikonu ayarlandı
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
def sifre_hashle(sifre): return hashlib.sha256(sifre.encode("utf-8")).hexdigest()

def kullanicilari_yukle():
    try:
        res = supabase.table("kullanicilar").select("*").execute()
        return {row["username"]: row["password_hash"] for row in res.data}
    except: return {}

def verileri_yukle(username):
    default_data = {
        "gunluk_kayitlar": [], "aktivite_loglari": {},
        "profil": {"cinsiyet": "Kadın", "yas": 20, "boy": 165, "mevcut_kilo": 60.0, "hedef_kilo": 55.0, "hedef_sure_ay": 2, "tema": "Koyu Cam", "setup_tamamlandi": False}
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

def hesapla_bmr(p): return (10 * float(p["mevcut_kilo"])) + (6.25 * float(p["boy"])) - (5 * int(p["yas"])) - 161
def hesapla_hedef_kalori(p):
    bmr = hesapla_bmr(p)
    kilo_farki = float(p["mevcut_kilo"]) - float(p["hedef_kilo"])
    gunluk_acik = (kilo_farki * 7700) / max(1, int(p.get("hedef_sure_ay", 1)) * 30)
    return bmr, gunluk_acik, max(1200, bmr - gunluk_acik)

# ----------------------------------------------------
# OTURUM YÖNETİMİ VE ANA AKIŞ
# ----------------------------------------------------
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "aktif_kullanici" not in st.session_state: st.session_state.aktif_kullanici = ""

if not st.session_state.giris_yapildi:
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap');
        [data-testid="stAppViewContainer"] { background-color: #111111; }
        .nova-logo-giris { font-family: 'Playfair Display', serif; font-size: 5rem; letter-spacing: 30px; text-align: center; font-weight: 700; margin-top: 10vh; color: #ffffff;}
        p, label, span { color: #ffffff !important; }
        </style>
        <div class="nova-logo-giris">N O V A</div>
        <p style='text-align: center; color: #aaaaaa !important; font-size: 1.2rem; letter-spacing: 4px; margin-bottom: 50px;'>ZARAFET VE DENGE</p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        tab_giris, tab_kayit = st.tabs(["Giriş Yap", "Kayıt Ol"])
        users = kullanicilari_yukle()
        with tab_giris:
            g_user = st.text_input("Kullanıcı Adı", key="g_user").strip().lower()
            g_pass = st.text_input("Şifre", type="password", key="g_pass")
            if st.button("Giriş Yap", use_container_width=True):
                if g_user in users and users[g_user] == sifre_hashle(g_pass):
                    st.session_state.giris_yapildi = True
                    st.session_state.aktif_kullanici = g_user
                    st.session_state.update(verileri_yukle(g_user))
                    st.rerun()
                else: st.error("Hatalı giriş.")
        with tab_kayit:
            k_user = st.text_input("Yeni Kullanıcı Adı", key="k_user").strip().lower()
            k_pass = st.text_input("Şifre", type="password", key="k_pass")
            if st.button("Hesap Oluştur", use_container_width=True):
                if k_user and k_pass and k_user not in users:
                    supabase.table("kullanicilar").insert({"username": k_user, "password_hash": sifre_hashle(k_pass)}).execute()
                    st.success("Hesap oluşturuldu, giriş yapabilirsiniz.")

else:
    aktif_user = st.session_state.aktif_kullanici
    p = st.session_state.profil
    aktif_tema = p.get("tema", "Koyu Cam")
    if aktif_tema not in TEMA_AYARLARI: aktif_tema = "Koyu Cam"
    tema = TEMA_AYARLARI[aktif_tema]
    bg_url = f"https://raw.githubusercontent.com/azraam2008-lgtm/NOVA/main/{tema['bg_image']}"

    # GÜNCELLENMİŞ TEMA CSS (KESİN YAZI, BUTON VE KUTU İZOLASYONU + TABS STİLİ)
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        
        [data-testid="stAppViewContainer"] {{ background-color: {tema['fallback_bg']}; background-image: url("{bg_url}"); background-size: cover; background-position: center; background-attachment: fixed; }}
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
        
        .nova-header {{ color: {tema['text_color']} !important; font-family: 'Playfair Display', serif; font-size: 5.5rem; letter-spacing: 25px; text-align: center; font-weight: 700; margin-top: -30px; margin-left: 12px; }}
        .nova-user {{ color: {tema['text_color']} !important; text-align: center; font-size: 1.5rem; letter-spacing: 6px; text-transform: uppercase; margin-bottom: 40px; opacity: 0.9; font-weight: 600; }}
        
        /* Kartların içindeki metinler temanın belirlediği renk olacak */
        .calai-card {{ background: {tema['card_bg']}; padding: 40px; border-radius: 32px; backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px); margin-bottom: 35px; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 15px 50px rgba(0,0,0,0.4); }}
        .calai-card p, .calai-card h1, .calai-card h2, .calai-card h3, .calai-card h4, .calai-card td, .calai-card th, .calai-card span, .calai-card label {{ color: {tema['text_color']} !important; font-family: 'Plus Jakarta Sans', sans-serif; }}
        
        /* 🚨 STREAMLİT KUTULARINI BEYAZ/AYDINLIK VE BELİRGİN YAPMA 🚨 */
        div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, input[type="text"], input[type="number"], textarea {{
            background-color: #ffffff !important;
            color: #000000 !important;
            border-radius: 8px !important;
            border: 2px solid rgba(0,0,0,0.2) !important;
        }}
        div[data-baseweb="select"] span {{ color: #000000 !important; font-weight: bold; }}
        
        /* Sekmeler (Tabs) Tasarımı */
        button[data-baseweb="tab"] {{
            background-color: transparent !important;
            color: {tema['text_color']} !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 1.1rem !important;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            border-bottom: 3px solid {tema['text_color']} !important;
            font-weight: 800 !important;
        }}
        
        /* Butonları temaya uyumlu ve çok belirgin hale getir */
        div.stButton > button:first-child {{
            background-color: {tema['fallback_bg']} !important;
            color: {tema['text_color']} !important;
            border: 2px solid {tema['text_color']} !important;
            font-weight: 800 !important;
            border-radius: 12px !important;
            backdrop-filter: blur(10px);
        }}
        div.stButton > button:first-child:hover {{
            background-color: {tema['text_color']} !important;
            color: {tema['fallback_bg']} !important;
            border-color: {tema['fallback_bg']} !important;
        }}
        
        /* Halka Grafikleri */
        .ring-container {{ width: 200px; height: 200px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; }}
        .ring-inner {{ width: 155px; height: 155px; border-radius: 50%; background: {tema['card_bg']}; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
        .ring-val {{ font-size: 2.2rem; font-weight: 800; margin-bottom: -5px; color: {tema['text_color']}; }}
        .ring-lbl {{ font-size: 1.1rem; opacity: 0.8; text-transform: uppercase; letter-spacing: 2px; color: {tema['text_color']}; }}
        
        table {{ width: 100%; font-size: 1.2rem; background: transparent; border-collapse: collapse; }}
        th, td {{ padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.2); text-align: left; }}
        th {{ font-weight: 800; font-size: 1.3rem; opacity: 0.9; }}
        a {{ color: {tema['text_color']} !important; text-decoration: underline !important; font-weight: bold; }}
        </style>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # EĞİTİCİ İLK KURULUM (ONBOARDING)
    # ----------------------------------------------------
    if not p.get("setup_tamamlandi", False):
        st.markdown(f'<div class="calai-card">', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; font-size: 3rem;'>NOVA'ya Hoş Geldin!</h1>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        boy = c1.number_input("Boy (cm)", min_value=130, max_value=220, value=int(p.get("boy", 165)))
        mevcut_kilo = c2.number_input("Mevcut Kilon (kg)", min_value=35.0, value=float(p.get("mevcut_kilo", 60.0)), step=0.5)
        hedef_kilo = c1.number_input("Hedef Kilon (kg)", min_value=35.0, value=float(p.get("hedef_kilo", 55.0)), step=0.5)
        hedef_sure = c2.number_input("Hedefe Ulaşma Süresi (Ay)", min_value=1, value=int(p.get("hedef_sure_ay", 2)))
        sec_tema = st.selectbox("Kişisel Temanı Seç", list(TEMA_AYARLARI.keys()), index=list(TEMA_AYARLARI.keys()).index(aktif_tema))

        if st.button("Profilimi Kaydet ve Başla", use_container_width=True):
            st.session_state.profil.update({"boy": boy, "mevcut_kilo": mevcut_kilo, "hedef_kilo": hedef_kilo, "hedef_sure_ay": hedef_sure, "tema": sec_tema, "setup_tamamlandi": True})
            verileri_kaydet(aktif_user)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # ----------------------------------------------------
    # ANA EKRAN VE SEKMELER (TABS)
    # ----------------------------------------------------
    st.markdown('<div class="nova-header">N O V A</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="nova-user">{aktif_user}</div>', unsafe_allow_html=True)

    c_sol, c_orta, c_sag = st.columns([1, 10, 1])
    with c_orta:
        # ÜST BAR: TARİH VE AYARLAR
        t_col1, t_col2 = st.columns([8, 2])
        with t_col1:
            secilen_tarih = str(st.date_input("🗓️ Tarih Seçimi", datetime.date.today()))
        with t_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⚙️ Ayarlar / Tema", use_container_width=True):
                st.session_state.profil["setup_tamamlandi"] = False
                st.rerun()

        if secilen_tarih not in st.session_state.aktivite_loglari:
            st.session_state.aktivite_loglari[secilen_tarih] = {"adim": 0, "su": 0.0, "egzersiz_kalori": 0}
        curr_aktivite = st.session_state.aktivite_loglari[secilen_tarih]

        # ANA İÇERİK SEKMELERİ
        tab_ozet, tab_ai_ogun, tab_ai_koc, tab_ai_asistan = st.tabs(["📊 Günlük Özet", "📸 AI Öğün Tarama", "🏋️‍♀️ AI Koç", "💬 AI Asistan"])

        # ==========================================
        # 1. SEKME: GÜNLÜK ÖZET (KLASİK EKRAN)
        # ==========================================
        with tab_ozet:
            st.markdown('<div class="calai-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='text-align:center; font-size: 2.2rem; margin-bottom: 30px;'>Günlük Aktivite ve Su Halkaları</h2>", unsafe_allow_html=True)
            
            adim_yuzde = min(curr_aktivite['adim'] / 10000 * 100, 100)
            su_yuzde = min(curr_aktivite['su'] / 2.5 * 100, 100)
            
            hc1, hc2 = st.columns(2)
            with hc1:
                st.markdown(f"""
                    <div class="ring-container" style="background: conic-gradient(#ff3b30 {adim_yuzde}%, {tema['ring_track']} 0deg);">
                        <div class="ring-inner">
                            <div class="ring-val" style="color:#ff3b30;">{curr_aktivite['adim']}</div>
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
                            <div class="ring-val" style="color:#007aff;">{curr_aktivite['su']:.2f}</div>
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

            st.markdown('<div class="calai-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='font-size: 2.2rem;'>🏋️‍♀️ Günün Egzersizi</h2>", unsafe_allow_html=True)
            
            tarih_obj = datetime.datetime.strptime(secilen_tarih, "%Y-%m-%d")
            gun_indeksi = tarih_obj.weekday()
            
            GUNLUK_EGZERSIZLER = {
                0: {"kanal": "Growwithjo", "baslik": "20 Dakika Yoğun Alt Karın Antrenmanı", "link": "https://www.youtube.com/watch?v=2haf-ZqA808", "kalori": 230},
                1: {"kanal": "Nikola's Pilates", "baslik": "20 Dakika Tam Vücut Sıkılaşma Pilatesi", "link": "https://www.youtube.com/watch?v=azvLOvw4NU8", "kalori": 190},
                2: {"kanal": "Growwithjo", "baslik": "20 Dakika Her Sabah Tam Vücut Kardiyo", "link": "https://www.youtube.com/watch?v=m1DBJhxKmiU", "kalori": 250},
                3: {"kanal": "Nikola's Pilates", "baslik": "15 Dakika Yağ Yakıcı ve Şekillendirici", "link": "https://www.youtube.com/watch?v=wNcAYIxlQgM", "kalori": 160},
                4: {"kanal": "Growwithjo", "baslik": "20 Dakika Kas Geliştirme & Yağ Yakımı", "link": "https://www.youtube.com/watch?v=hXBE20_RGfU", "kalori": 240},
                5: {"kanal": "Nikola's Pilates", "baslik": "İnce ve Belirgin Bir Vücut İçin Ev Egzersizi", "link": "https://www.youtube.com/watch?v=TcOa7qlcHA4", "kalori": 180},
                6: {"kanal": "Growwithjo", "baslik": "Karın Kaslarınızı Yakacak 20 Dakika", "link": "https://www.youtube.com/watch?v=jORxpByzIwA", "kalori": 220},
            }
            g_egz = GUNLUK_EGZERSIZLER[gun_indeksi]
            
            st.markdown(f"""
            <div style="background: rgba(0,0,0,0.3); padding: 25px; border-radius: 15px; margin-bottom: 20px; border-left: 5px solid #ff3b30;">
                <h3 style="margin-top:0; color: #ffffff !important;">{g_egz['kanal']}</h3>
                <p style="font-size: 1.2rem; color: #ffffff !important;">{g_egz['baslik']}</p>
                <p style="color: #ffffff !important;">🤖 <b>Yapay Zeka Analizi:</b> Bu videodaki hareket dinamiğine göre <b>{g_egz['kalori']} kcal</b> yakacaksın.</p>
                <a href="{g_egz['link']}" target="_blank" style="display: inline-block; background-color: #ff3b30; color: white !important; padding: 12px 25px; border-radius: 8px; text-decoration: none !important; font-weight: bold; margin-top: 10px;">▶️ YouTube'da Aç ve İzle</a>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("✅ Antrenmanı Tamamladım", use_container_width=True):
                curr_aktivite["egzersiz_kalori"] = g_egz['kalori']
                verileri_kaydet(aktif_user)
                st.rerun()
                
            if curr_aktivite.get("egzersiz_kalori", 0) > 0:
                st.success(f"🔥 Harika iş çıkardın! Tabloya günlük **{curr_aktivite['egzersiz_kalori']} kcal** egzersiz harcaması eklendi.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="calai-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='font-size: 2.2rem;'>Kalori ve Denge Tablosu</h2>", unsafe_allow_html=True)
            
            bugun_og = [k for k in st.session_state.gunluk_kayitlar if k["Tarih"] == secilen_tarih]
            top_kalori = sum([k["Kalori"] for k in bugun_og])
            top_pro = sum([k.get("Protein", 0) for k in bugun_og])
            top_karb = sum([k.get("Karbonhidrat", 0) for k in bugun_og])
            top_yag = sum([k.get("Yağ", 0) for k in bugun_og])
            
            bmr, gunluk_acik, hedef_kalori_alim = hesapla_hedef_kalori(p)
            harcanan_adim_kalori = curr_aktivite["adim"] * 0.04
            harcanan_egzersiz = curr_aktivite.get("egzersiz_kalori", 0)
            aktif_harcanan = harcanan_adim_kalori + harcanan_egzersiz
            kalan_kalori = hedef_kalori_alim - top_kalori + aktif_harcanan
            
            hedef_pro = (hedef_kalori_alim * 0.3) / 4
            hedef_karb = (hedef_kalori_alim * 0.4) / 4
            hedef_yag = (hedef_kalori_alim * 0.3) / 9
            
            st.markdown(f"""
            <table>
                <tr><th>Metrik</th><th style="text-align: right;">Değer</th></tr>
                <tr><td>🎯 Günlük Hedef Kalori Bütçen</td><td style="text-align: right; color: #007aff;"><b>{round(hedef_kalori_alim)} kcal</b></td></tr>
                <tr><td>🍽️ Bugüne Kadar Yediklerin</td><td style="text-align: right; color: #ff3b30;"><b>- {round(top_kalori)} kcal</b></td></tr>
                <tr><td>🏃‍♀️ Hareket ve Egzersizle Kazandıkların</td><td style="text-align: right; color: #34c759;"><b>+ {round(aktif_harcanan)} kcal</b></td></tr>
                <tr style="border-top: 2px solid rgba(255,255,255,0.5);">
                    <td style="font-size: 1.4rem; font-weight: 800;">⚖️ Geriye Kalan Yeme Hakkın</td>
                    <td style="text-align: right; font-size: 1.4rem; font-weight: 800;">{round(kalan_kalori)} kcal</td>
                </tr>
            </table>
            <br>
            """, unsafe_allow_html=True)
            
            if kalan_kalori < 0: 
                st.error(f"⚠️ Limitini {abs(round(kalan_kalori))} kcal aştın. Hedefe dönmek için biraz egzersiz yapmalısın!")
            else: 
                st.success(f"✅ Harika gidiyorsun! Günün geri kalanı için {round(kalan_kalori)} kcal yeme hakkın duruyor.")

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
            st.markdown(render_makro("🥩 Protein", top_pro, hedef_pro, "#ff3b30"), unsafe_allow_html=True)
            st.markdown(render_makro("🍞 Karbonhidrat", top_karb, hedef_karb, "#007aff"), unsafe_allow_html=True)
            st.markdown(render_makro("🥑 Yağ", top_yag, hedef_yag, "#ffcc00"), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="calai-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='font-size: 2.2rem;'>🔎 Yemek Ara & Günlüğüne Ekle (Veritabanı)</h2>", unsafe_allow_html=True)
            
            a_col1, a_col2 = st.columns([3, 1])
            with a_col1:
                yemek_isimleri = df_yemek["Yemek Adı"].tolist()
                secilen_yemek = st.selectbox("Yediğin yemeği seç...", yemek_isimleri, key="db_yemek")
            with a_col2:
                secilen_ogun = st.selectbox("Hangi Öğün?", ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"], key="db_ogun")
                
            if secilen_yemek and secilen_yemek != "Önce CSV'yi GitHub'a Yükleyin":
                detay = df_yemek[df_yemek["Yemek Adı"] == secilen_yemek].iloc[0]
                st.caption(f"🔥 **İçerik:** {detay['Kalori (kcal)']} kcal | P: {detay['Protein (g)']}g | K: {detay['Karbonhidrat (g)']}g | Y: {detay['Yağ (g)']}g")
                if st.button("➕ Günlüğe Ekle", use_container_width=True):
                    st.session_state.gunluk_kayitlar.append({
                        "Tarih": secilen_tarih, "Öğün": secilen_ogun, "Tarif": secilen_yemek,
                        "Kalori": float(detay["Kalori (kcal)"]), "Protein": float(detay["Protein (g)"]), 
                        "Karbonhidrat": float(detay["Karbonhidrat (g)"]), "Yağ": float(detay["Yağ (g)"])
                    })
                    verileri_kaydet(aktif_user)
                    st.rerun()

            st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 30px 0;'>", unsafe_allow_html=True)
            st.markdown("<h3>🍽️ Bugünkü Öğünlerin</h3>", unsafe_allow_html=True)
            for ogun_turu in ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"]:
                ogun_yemekleri = [(i, k) for i, k in enumerate(st.session_state.gunluk_kayitlar) if k.get("Tarih") == secilen_tarih and k.get("Öğün") == ogun_turu]
                if ogun_yemekleri:
                    st.markdown(f"**{ogun_turu}**")
                    for i, k in ogun_yemekleri:
                        c1, c2 = st.columns([10, 1])
                        c1.markdown(f"• {k['Tarif']} — *{k['Kalori']} kcal*")
                        if c2.button("🗑️", key=f"sil_{i}", help="Bu öğünü sil"):
                            st.session_state.gunluk_kayitlar.pop(i)
                            verileri_kaydet(aktif_user)
                            st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="calai-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='font-size: 2.2rem;'>📈 Haftalık Gelişim (Çizgi Grafik)</h2>", unsafe_allow_html=True)
            bugun_tarih = datetime.date.today()
            grafik_data = []
            
            for i in range(6, -1, -1):
                g = str(bugun_tarih - datetime.timedelta(days=i))
                g_ogunler = [k for k in st.session_state.gunluk_kayitlar if k.get("Tarih") == g]
                g_alinan = sum([k["Kalori"] for k in g_ogunler])
                g_akt = st.session_state.aktivite_loglari.get(g, {"adim": 0, "egzersiz_kalori": 0})
                g_harcanan = bmr + (g_akt["adim"] * 0.04) + g_akt.get("egzersiz_kalori", 0)
                grafik_data.append({"Gün": g[5:], "Yediğin Kalori": g_alinan, "Vücudunun Toplam Yaktığı (BMR dahil)": g_harcanan})
            
            df_grafik = pd.DataFrame(grafik_data).set_index("Gün")
            st.line_chart(df_grafik, color=["#ff3b30", "#34c759"])
            st.caption("ℹ️ **Nasıl Okunur:** **Kırmızı Hat** yediğin öğünleri, **Yeşil Hat** ise vücudunun gün içinde tamamen harcadığı (Metabolizma + Egzersiz) enerjiyi gösterir. Yeşil hat kırmızının üstündeyse zayıflıyorsun demektir.")
            st.markdown('</div>', unsafe_allow_html=True)

        # ==========================================
        # 2. SEKME: YZ FOTOĞRAF TABANLI ÖĞÜN TARAMA
        # ==========================================
        with tab_ai_ogun:
            st.markdown('<div class="calai-card">', unsafe_allow_html=True)
            secilen_ogun_ai = st.selectbox("Hangi Öğün İçin Tarama Yapıyorsun?", ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"], key="ai_ogun_sec")
            
            totals = meal_scan_page()
            
            if totals:
                for item in totals["items"]:
                    st.session_state.gunluk_kayitlar.append({
                        "Tarih": secilen_tarih, 
                        "Öğün": secilen_ogun_ai, 
                        "Tarif": f"🤖 {item['Yemek']}",
                        "Kalori": float(item["Kalori"]), 
                        "Protein": float(item["Protein (g)"]), 
                        "Karbonhidrat": float(item["Karb. (g)"]), 
                        "Yağ": float(item["Yağ (g)"])
                    })
                verileri_kaydet(aktif_user)
                st.success(f"{totals['kcal']} kcal başarıyla günlüğüne eklendi!")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ==========================================
        # 3. SEKME: YZ ANTRENMAN KOÇU
        # ==========================================
        with tab_ai_koc:
            st.markdown('<div class="calai-card">', unsafe_allow_html=True)
            log = coach_page()
            
            if log:
                # Modül üzerinden plan başarılı girildiğinde otomatik 250 kcal yaktığı farz edilir
                curr_aktivite["egzersiz_kalori"] += 250
                verileri_kaydet(aktif_user)
                st.success("🤖 Harika! AI Antrenmanını tamamladın, günlüğüne 250 kcal harcama eklendi.")
            st.markdown('</div>', unsafe_allow_html=True)

        # ==========================================
        # 4. SEKME: YZ BESLENME VE SPOR ASİSTANI
        # ==========================================
        with tab_ai_asistan:
            st.markdown('<div class="calai-card">', unsafe_allow_html=True)
            ask_page()
            st.markdown('</div>', unsafe_allow_html=True)
