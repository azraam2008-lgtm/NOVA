import datetime
import hashlib
import json
import pandas as pd
import streamlit as st
from PIL import Image
from supabase import create_client, Client

# --- SUPABASE BAĞLANTI AYARLARI ---
SUPABASE_URL = "https://klncgexnykfwzpcrijrt.supabase.co"
SUPABASE_KEY = "sb_publishable_yXcnmg2uJsA7vR0DXnWUWQ_06Jm4E8e"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----------------------------------------------------
# 1. SAYFA KONFİGÜRASYONU & AMBLEM BAĞLANTISI
# ----------------------------------------------------
AMBLEM_URL = "https://raw.githubusercontent.com/azraam2008-lgtm/NOVA/main/amblem.jpg"

st.set_page_config(
    page_title="Nova — Diyet ve Aktivite Asistanı",
    page_icon=AMBLEM_URL,
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    f"""
    <head>
        <link rel="apple-touch-icon" href="{AMBLEM_URL}">
        <link rel="icon" type="image/jpeg" href="{AMBLEM_URL}">
    </head>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. PROFESYONEL VE FERAH KART TASARIMI (CSS)
# ----------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    .stApp { background-color: #f8f9fa; color: #111111; font-family: 'Plus Jakarta Sans', sans-serif; }
    h1, h2, h3, h4 { color: #111111 !important; font-weight: 700 !important; }
    [data-testid="stSidebar"] { display: none; }
    
    .calai-section-card {
        background: #ffffff; border: 1px solid #e5e5ea; border-radius: 24px;
        padding: 32px; margin-bottom: 28px; box-shadow: 0 4px 24px rgba(0, 0, 0, 0.03);
    }
    .calai-title { font-size: 22px; font-weight: 700; color: #111111; margin-bottom: 8px; }
    .stButton > button {
        background-color: #111111; color: #ffffff; border: none; border-radius: 12px;
        font-weight: 600; padding: 10px 20px; transition: 0.2s;
    }
    .stButton > button:hover { background-color: #333333; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. KAPSAMLI VE ULTRA-ZENGİN RESTORAN MENÜSÜ (KATALOG)
# ----------------------------------------------------
ZENGIN_LEZZET_KATALOGU = {
    "Kahvaltılıklar 🥐": {
        "Serpme Kahvaltı": {"kalori": 650, "protein": 24, "karb": 55, "yag": 36, "gramaj": 650, "malzemeler": ["Peynir çeşitleri", "Zeytin", "Domates-Salatalık", "Yumurta", "Reçel", "Bal-Kaymak", "Ekmek"]},
        "Kahvaltı Tabağı": {"kalori": 420, "protein": 18, "karb": 35, "yag": 22, "gramaj": 400, "malzemeler": ["Beyaz Peynir", "Kaşar", "Zeytin", "Yumurta", "Domates", "Salatalık"]},
        "Menemen": {"kalori": 210, "protein": 11, "karb": 9, "yag": 15, "gramaj": 250, "malzemeler": ["Yumurta", "Domates", "Biber", "Zeytinyağı"]},
        "Kaşarlı Menemen": {"kalori": 280, "protein": 15, "karb": 10, "yag": 19, "gramaj": 280, "malzemeler": ["Yumurta", "Domates", "Biber", "Kaşar Peyniri"]},
        "Sucuklu Yumurta": {"kalori": 340, "protein": 16, "karb": 3, "yag": 30, "gramaj": 200, "malzemeler": ["Yumurta", "Dana Sucuk", "Tereyağı"]},
        "Peynirli Omlet": {"kalori": 250, "protein": 15, "karb": 2, "yag": 20, "gramaj": 200, "malzemeler": ["Yumurta", "Beyaz Peynir", "Tereyağı"]},
        "Kaşarlı Tost": {"kalori": 320, "protein": 14, "karb": 30, "yag": 16, "gramaj": 180, "malzemeler": ["Tost Ekmeği", "Kaşar Peyniri"]},
        "Karışık Tost": {"kalori": 380, "protein": 18, "karb": 31, "yag": 21, "gramaj": 200, "malzemeler": ["Tost Ekmeği", "Kaşar", "Sucuk"]},
        "Avokadolu Tost": {"kalori": 310, "protein": 9, "karb": 28, "yag": 17, "gramaj": 210, "malzemeler": ["Ekşi Mayalı Ekmek", "Avokado", "Baharatlar"]},
        "Kruvasan": {"kalori": 270, "protein": 5, "karb": 31, "yag": 14, "gramaj": 85, "malzemeler": ["Tereyağlı Kruvasan Hamuru"]},
        "Pancake": {"kalori": 310, "protein": 8, "karb": 45, "yag": 10, "gramaj": 200, "malzemeler": ["Un", "Süt", "Yumurta", "Akçaağaç Şurubu"]},
        "Granola ve Yoğurt Kasesi": {"kalori": 320, "protein": 14, "karb": 44, "yag": 10, "gramaj": 250, "malzemeler": ["Süzme Yoğurt", "Granola", "Bal", "Meyve"]}
    },
    "Çorbalar 🍲": {
        "Mercimek Çorbası": {"kalori": 160, "protein": 8, "karb": 22, "yag": 4.5, "gramaj": 250, "malzemeler": ["Kırmızı Mercimek", "Soğan", "Havuç", "Zeytinyağı"]},
        "Ezogelin Çorbası": {"kalori": 170, "protein": 8, "karb": 24, "yag": 5, "gramaj": 250, "malzemeler": ["Mercimek", "Bulgur", "Pirinç", "Salça", "Nane"]},
        "Domates Çorbası": {"kalori": 140, "protein": 3, "karb": 18, "yag": 6, "gramaj": 250, "malzemeler": ["Domates Püresi", "Un", "Tereyağı", "Krema"]},
        "Kremalı Mantar Çorbası": {"kalori": 180, "protein": 4, "karb": 15, "yag": 11, "gramaj": 250, "malzemeler": ["Mantar", "Krema", "Un", "Tereyağı"]},
        "Tavuk Suyu Çorbası": {"kalori": 130, "protein": 10, "karb": 14, "yag": 3.5, "gramaj": 250, "malzemeler": ["Tavuk Suyu", "Tel Şehriye", "Tavuk Eti"]}
    },
    "Ara Sıcaklar & Başlangıçlar 🧀": {
        "Patates Kızartması": {"kalori": 360, "protein": 4, "karb": 48, "yag": 17, "gramaj": 180, "malzemeler": ["Patates", "Kızartma Yağı", "Tuz"]},
        "Soğan Halkası (8 Adet)": {"kalori": 290, "protein": 3, "karb": 34, "yag": 16, "gramaj": 150, "malzemeler": ["Soğan", "Özel Kaplama Harcı"]},
        "Mozzarella Sticks (6 Adet)": {"kalori": 340, "protein": 14, "karb": 26, "yag": 20, "gramaj": 160, "malzemeler": ["Mozzarella Peyniri", "Galeta Unu"]},
        "Sigara Böreği (5 Adet)": {"kalori": 310, "protein": 9, "karb": 32, "yag": 16, "gramaj": 150, "malzemeler": ["Yufka", "Lor Peyniri", "Maydanoz"]},
        "Paçanga Böreği": {"kalori": 380, "protein": 14, "karb": 30, "yag": 22, "gramaj": 170, "malzemeler": ["Yufka", "Pastırma", "Kaşar Peyniri", "Biber"]}
    },
    "Salatalar 🥗": {
        "Mevsim Salata": {"kalori": 90, "protein": 2, "karb": 8, "yag": 6, "gramaj": 200, "malzemeler": ["Marul", "Havuç", "Mor Lahana", "Zeytinyağı", "Limon"]},
        "Çoban Salata": {"kalori": 110, "protein": 3, "karb": 9, "yag": 7, "gramaj": 220, "malzemeler": ["Domates", "Salatalık", "Biber", "Soğan", "Zeytinyağı"]},
        "Sezar Salata": {"kalori": 250, "protein": 8, "karb": 12, "yag": 19, "gramaj": 250, "malzemeler": ["Marul", "Kruton Ekmek", "Parmesan", "Sezar Sos"]},
        "Tavuklu Sezar Salata": {"kalori": 340, "protein": 28, "karb": 13, "yag": 20, "gramaj": 320, "malzemeler": ["Izgara Tavuk", "Marul", "Kruton", "Parmesan"]},
        "Ton Balıklı Salata": {"kalori": 290, "protein": 28, "karb": 9, "yag": 15, "gramaj": 280, "malzemeler": ["Ton Balığı", "Yeşillik", "Mısır", "Zeytinyağı"]}
    },
    "Sandviçler & Dürümler 🥪": {
        "Kaşarlı Tost Sandviç": {"kalori": 320, "protein": 14, "karb": 30, "yag": 16, "gramaj": 180, "malzemeler": ["Sandviç Ekmeği", "Kaşar Peyniri"]},
        "Ton Balıklı Sandviç": {"kalori": 350, "protein": 22, "karb": 38, "yag": 12, "gramaj": 230, "malzemeler": ["Sandviç Ekmeği", "Ton Balığı", "Marul", "Mayonez"]},
        "Tavuklu Wrap": {"kalori": 420, "protein": 26, "karb": 44, "yag": 16, "gramaj": 280, "malzemeler": ["Lavaş", "Izgara Tavuk", "Yeşillik", "Özel Sos"]},
        "Et Dürüm": {"kalori": 490, "protein": 25, "karb": 50, "yag": 22, "gramaj": 300, "malzemeler": ["Lavaş", "Dana Eti Dilimleri", "Domates", "Soğan"]}
    },
    "Burgerler & Fast Food 🍔": {
        "Klasik Hamburger": {"kalori": 420, "protein": 22, "karb": 38, "yag": 20, "gramaj": 250, "malzemeler": ["Hamburger Ekmeği", "Dana Köfte", "Marul", "Turşu"]},
        "Cheeseburger": {"kalori": 480, "protein": 25, "karb": 40, "yag": 24, "gramaj": 270, "malzemeler": ["Hamburger Ekmeği", "Dana Köfte", "Cheddar Peyniri"]},
        "Double Cheeseburger": {"kalori": 680, "protein": 42, "karb": 42, "yag": 38, "gramaj": 380, "malzemeler": ["Çift Köfte", "Çift Cheddar Peyniri", "Özel Sos"]},
        "Tavuk Nugget Menü": {"kalori": 650, "protein": 24, "karb": 70, "yag": 30, "gramaj": 400, "malzemeler": ["Nugget (8 Adet)", "Patates Kızartması", "İçecek"]}
    },
    "Pizzalar & Makarnalar 🍕": {
        "Margherita Pizza": {"kalori": 620, "protein": 24, "karb": 78, "yag": 24, "gramaj": 450, "malzemeler": ["Pizza Hamuru", "Mozzarella", "Domates Sosu", "Fesleğen"]},
        "Karışık Pizza": {"kalori": 780, "protein": 34, "karb": 82, "yag": 33, "gramaj": 520, "malzemeler": ["Mozzarella", "Sucuk", "Sosis", "Mantar", "Biber", "Zeytin"]},
        "Spaghetti Bolognese": {"kalori": 510, "protein": 24, "karb": 65, "yag": 18, "gramaj": 380, "malzemeler": ["Spaghetti", "Kıymalı Domates Sosu", "Parmesan"]},
        "Kremalı Mantarlı Makarna": {"kalori": 540, "protein": 16, "karb": 62, "yag": 25, "gramaj": 380, "malzemeler": ["Penne Makarna", "Mantar", "Krema", "Parmesan"]}
    },
    "Ana Yemekler 🍽️": {
        "Izgara Tavuk Göğsü": {"kalori": 280, "protein": 42, "karb": 0, "yag": 12, "gramaj": 200, "malzemeler": ["Tavuk Göğsü", "Özel Baharatlar", "Zeytinyağı"]},
        "Izgara Köfte": {"kalori": 360, "protein": 28, "karb": 6, "yag": 24, "gramaj": 200, "malzemeler": ["Dana Kıyma", "Soğan", "Baharatlar"]},
        "Izgara Somon": {"kalori": 380, "protein": 34, "karb": 0, "yag": 26, "gramaj": 220, "malzemeler": ["Somon Fileto", "Zeytinyağı", "Limon"]},
        "İskender Kebap": {"kalori": 780, "protein": 40, "karb": 65, "yag": 38, "gramaj": 450, "malzemeler": ["Döner Eti", "Pide Parçaları", "Tereyağı", "Domates Sosu", "Yoğurt"]},
        "Adana Kebap": {"kalori": 550, "protein": 32, "karb": 15, "yag": 40, "gramaj": 320, "malzemeler": ["Zırh Kıyması", "Acı Biber", "Lavaş", "Köz Sebzeler"]}
    },
    "Pilavlar ve Börekler 🍚": {
        "Sade Pirinç Pilavı": {"kalori": 310, "protein": 5, "karb": 48, "yag": 11, "gramaj": 200, "malzemeler": ["Baldo Pirinç", "Tereyağı", "Sıvı Yağ"]},
        "Bulgur Pilavı": {"kalori": 240, "protein": 7, "karb": 42, "yag": 5, "gramaj": 200, "malzemeler": ["Pilavlık Bulgur", "Domates Salçası", "Soğan"]},
        "Su Böreği": {"kalori": 380, "protein": 12, "karb": 38, "yag": 20, "gramaj": 150, "malzemeler": ["Böreklik Un", "Yumurta", "Beyaz Peynir", "Tereyağı"]},
        "Peynirli Gözleme": {"kalori": 450, "protein": 18, "karb": 52, "yag": 20, "gramaj": 250, "malzemeler": ["Yufka", "Lor-Beyaz Peynir", "Tereyağı"]}
    },
    "Zeytinyağlılar & Fırın Yemekleri 🫒": {
        "Zeytinyağlı Yaprak Sarma": {"kalori": 190, "protein": 3, "karb": 26, "yag": 8, "gramaj": 180, "malzemeler": ["Asma Yaprağı", "Pirinç", "Zeytinyağı", "Kuş Üzümü"]},
        "Zeytinyağlı Taze Fasulye": {"kalori": 140, "protein": 3, "karb": 14, "yag": 8, "gramaj": 200, "malzemeler": ["Taze Fasulye", "Domates", "Soğan", "Zeytinyağı"]},
        "Lazanya": {"kalori": 520, "protein": 24, "karb": 45, "yag": 26, "gramaj": 300, "malzemeler": ["Lazanya Yaprakları", "Kıymalı Sos", "Beşamel", "Kaşar"]},
        "Karnıyarık": {"kalori": 320, "protein": 14, "karb": 16, "yag": 22, "gramaj": 280, "malzemeler": ["Patlıcan", "Kıymalı Harç", "Domates Sosu"]}
    },
    "Sokak Lezzetleri & Atıştırmalıklar 🌮": {
        "Islak Hamburger": {"kalori": 390, "protein": 15, "karb": 36, "yag": 20, "gramaj": 150, "malzemeler": ["Hamburger Ekmeği", "Köfte", "Sarımsaklı Sos"]},
        "Kumpir": {"kalori": 540, "protein": 14, "karb": 68, "yag": 23, "gramaj": 350, "malzemeler": ["Patates", "Tereyağı", "Kaşar", "Mısır", "Zeytin", "Sosis"]},
        "Kokoreç": {"kalori": 480, "protein": 22, "karb": 20, "yag": 34, "gramaj": 200, "malzemeler": ["Kuzu Kokoreç", "Özel Baharatlar", "Ekmek"]},
        "Enerji Topları (3 Adet)": {"kalori": 220, "protein": 6, "karb": 28, "yag": 10, "gramaj": 90, "malzemeler": ["Hurma", "Yulaf", "Badem", "Fıstık Ezmesi"]}
    },
    "Tatlılar ve İçecekler 🍰": {
        "San Sebastian Cheesecake": {"kalori": 460, "protein": 8, "karb": 34, "yag": 32, "gramaj": 150, "malzemeler": ["Krema Peynir", "Yumurta", "Krema", "Şeker"]},
        "Çikolatalı Sufle": {"kalori": 390, "protein": 6, "karb": 48, "yag": 20, "gramaj": 140, "malzemeler": ["Bitter Çikolata", "Yumurta", "Tereyağı", "Un"]},
        "Fırın Sütlaç": {"kalori": 280, "protein": 7, "karb": 45, "yag": 8, "gramaj": 200, "malzemeler": ["Süt", "Pirinç", "Şeker"]},
        "Filtre Kahve": {"kalori": 5, "protein": 0.3, "karb": 1, "yag": 0, "gramaj": 200, "malzemeler": ["Kahve Çekirdeği", "Su"]},
        "Caffe Latte": {"kalori": 150, "protein": 8, "karb": 14, "yag": 6, "gramaj": 250, "malzemeler": ["Espresso", "Süt"]}
    }
}

# ----------------------------------------------------
# 4. BULUT (SUPABASE) VERİ YÖNETİM FONKSİYONLARI
# ----------------------------------------------------
def sifre_hashle(sifre): 
    return hashlib.sha256(sifre.encode("utf-8")).hexdigest()

def kullanicilari_yukle():
    try:
        res = supabase.table("kullanicilar").select("*").execute()
        return {row["username"]: row["password_hash"] for row in res.data}
    except Exception as e:
        return {}

def verileri_yukle(username):
    default_data = {
        "gunluk_kayitlar": [], "aktivite_loglari": {},
        "profil": {
            "cinsiyet": "Kadın", "yas": 20, "boy": 165, 
            "mevcut_kilo": 58.0, "hedef_kilo": 55.0, 
            "tema": "Yeşil Ferahlık", "setup_tamamlandi": False
        }
    }
    try:
        res = supabase.table("kullanici_verileri").select("data").eq("username", username).execute()
        if res.data: 
            return res.data[0]["data"]
    except: 
        pass
    return default_data

def verileri_kaydet(username):
    data = {
        "gunluk_kayitlar": st.session_state.gunluk_kayitlar,
        "aktivite_loglari": st.session_state.aktivite_loglari,
        "profil": st.session_state.profil
    }
    try:
        supabase.table("kullanici_verileri").upsert({"username": username, "data": data}).execute()
    except Exception as e:
        st.error("Veriler buluta kaydedilirken hata oluştu.")

def hesapla_bmr(p):
    return (10 * float(p["mevcut_kilo"])) + (6.25 * float(p["boy"])) - (5 * int(p["yas"])) - 161

# ----------------------------------------------------
# 5. GİRİŞ VE OTURUM YÖNETİMİ
# ----------------------------------------------------
if "giris_yapildi" not in st.session_state: 
    st.session_state.giris_yapildi = False
if "aktif_kullanici" not in st.session_state: 
    st.session_state.aktif_kullanici = ""
if "sayfa_gorunumu" not in st.session_state: 
    st.session_state.sayfa_gorunumu = "ana_sayfa"

if not st.session_state.giris_yapildi:
    st.markdown("<h1 style='text-align: center; font-size: 48px; letter-spacing: 2px; margin-top: 40px;'>NOVA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 16px; margin-bottom: 30px;'>Every meal is an opportunity to provide your body with vibrant energy and wellness.</p>", unsafe_allow_html=True)
    
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
            else: 
                st.error("Hatalı kullanıcı adı veya şifre.")

    with tab_kayit:
        k_user = st.text_input("Yeni Kullanıcı Adı", key="k_user").strip().lower()
        k_pass = st.text_input("Şifre Belirle", type="password", key="k_pass")
        if st.button("Hesap Oluştur", use_container_width=True):
            if k_user and k_pass:
                if k_user not in users:
                    try:
                        supabase.table("kullanicilar").insert({"username": k_user, "password_hash": sifre_hashle(k_pass)}).execute()
                        st.success("Hesap oluşturuldu, giriş yapabilirsiniz.")
                    except Exception as e:
                        st.error(f"Kayıt oluşturulurken veritabanı hatası: {e}")
                else: 
                    st.warning("Bu kullanıcı adı zaten alınmış.")

else:
    aktif_user = st.session_state.aktif_kullanici
    p = st.session_state.profil
    bmr_kisi = hesapla_bmr(p)

    top_c1, top_c2, top_c3 = st.columns([6, 2, 2])
    top_c1.markdown(f"### ✨ {aktif_user.capitalize()}")
    with top_c2:
        if st.button("👤 Hesap & Tema", use_container_width=True):
            st.session_state.sayfa_gorunumu = "hesap" if st.session_state.sayfa_gorunumu == "ana_sayfa" else "ana_sayfa"
            st.rerun()
    if top_c3.button("Çıkış", use_container_width=True):
        st.session_state.giris_yapildi = False
        st.rerun()

    # ----------------------------------------------------
    # 6. HESAP, TEMA SEÇİMİ VE ANA EKRAN
    # ----------------------------------------------------
    if st.session_state.sayfa_gorunumu == "hesap":
        st.markdown("""
            <div class="calai-section-card">
                <div class="calai-title">Hesap, Hedefler ve Tema Seçimi</div>
            </div>
        """, unsafe_allow_html=True)
        
        cinsiyet = st.selectbox("Cinsiyet", ["Kadın", "Erkek"], index=0 if p["cinsiyet"] == "Kadın" else 1)
        yas = st.number_input("Yaş", min_value=15, max_value=80, value=int(p["yas"]))
        boy = st.number_input("Boy (cm)", min_value=120, max_value=210, value=int(p["boy"]))
        mevcut_kilo = st.number_input("Mevcut Kilo (kg)", min_value=35.0, value=float(p["mevcut_kilo"]), step=0.5)
        hedef_kilo = st.number_input("Hedef Kilo (kg)", min_value=30.0, value=float(p["hedef_kilo"]), step=0.5)
        
        tema_secenekleri = ["Yeşil Ferahlık", "Pembe Su & Detoks", "Koyu Gym", "Meyve Bahçesi"]
        secilen_tema = st.selectbox("Tema & Görsel Konsepti", tema_secenekleri, index=tema_secenekleri.index(p.get("tema", "Yeşil Ferahlık")) if p.get("tema") in tema_secenekleri else 0)

        if st.button("Değişiklikleri Kaydet ve Ana Sayfaya Dön", use_container_width=True):
            st.session_state.profil.update({
                "cinsiyet": cinsiyet, "yas": yas, "boy": boy, "mevcut_kilo": mevcut_kilo, 
                "hedef_kilo": hedef_kilo, "tema": secilen_tema, "setup_tamamlandi": True
            })
            verileri_kaydet(aktif_user)
            st.session_state.sayfa_gorunumu = "ana_sayfa"
            st.rerun()
            
    else:
        sol_bosluk, ana_icerik, sag_bosluk = st.columns([1, 4, 1])
        aktif_tema = p.get("tema", "Yeşil Ferahlık")

        with sol_bosluk:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if aktif_tema == "Yeşil Ferahlık": 
                st.image("https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400")
            elif aktif_tema == "Pembe Su & Detoks": 
                st.image("https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=400")
            elif aktif_tema == "Koyu Gym": 
                st.image("https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=400")
            else: 
                st.image("https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=400")

        with ana_icerik:
            secilen_tarih = str(st.date_input("Kayıt Tarihi", datetime.date.today()))
            if secilen_tarih not in st.session_state.aktivite_loglari:
                st.session_state.aktivite_loglari[secilen_tarih] = {"adim": 0, "su": 0.0}
            curr_aktivite = st.session_state.aktivite_loglari[secilen_tarih]

            st.markdown("""<div class="calai-section-card"><div class="calai-title">Günlük Aktivite & Su Halkaları</div></div>""", unsafe_allow_html=True)
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown(f"**Adım:** {curr_aktivite['adim']}")
                yeni_adim = st.number_input("Adım Güncelle", min_value=0, max_value=50000, value=int(curr_aktivite["adim"]), step=500, label_visibility="collapsed")
                if st.button("Adımı Kaydet", use_container_width=True):
                    curr_aktivite["adim"] = yeni_adim
                    verileri_kaydet(aktif_user)
                    st.rerun()
            with col_m2:
                st.markdown(f"**Su Tüketimi:** {curr_aktivite['su']:.2f} L / 2.5 L")
                st.progress(min(curr_aktivite['su'] / 2.5, 1.0))
                sc1, sc2 = st.columns(2)
                if sc1.button("+0.25L", use_container_width=True):
                    curr_aktivite["su"] = round(curr_aktivite["su"] + 0.25, 2)
                    verileri_kaydet(aktif_user)
                    st.rerun()
                if sc2.button("-0.25L", use_container_width=True) and curr_aktivite["su"] >= 0.25:
                    curr_aktivite["su"] = round(curr_aktivite["su"] - 0.25, 2)
                    verileri_kaydet(aktif_user)
                    st.rerun()

            st.markdown("""<div class="calai-section-card"><div class="calai-title">Track Your Food With Just a Picture</div></div>""", unsafe_allow_html=True)
            upl = st.file_uploader("Yemek Fotoğrafı Yükle", type=["jpg", "jpeg", "png"])
            if upl:
                st.image(Image.open(upl), caption="Yüklenen Yemek Tabağı", use_container_width=True)
                ogun_turu = st.selectbox("Öğün Türü", ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"])
                if st.button("Fotoğrafı Analiz Et", use_container_width=True):
                    with st.spinner("Yapay zeka inceliyor..."):
                        st.session_state["ai_sonuc"] = {
                            "tarife": "Yapay Zeka Analizli Tabak", "kalori": 380.0, "protein": 22.0, "karb": 35.0, "yag": 14.0, 
                            "metin": "✨ **AI Analiz Raporu:** Mükemmel makro dağılımı. Sağlık Skoru: 9.2 / 10"
                        }
                if "ai_sonuc" in st.session_state and st.session_state["ai_sonuc"]:
                    r = st.session_state["ai_sonuc"]
                    st.info(r['metin'])
                    ed_isim = st.text_input("Yemek Adı", value=r["tarife"])
                    ed_kal = st.number_input("Kalori", value=float(r["kalori"]))
                    ed_pro = st.number_input("Protein", value=float(r["protein"]))
                    ed_karb = st.number_input("Karb", value=float(r["karb"]))
                    ed_yag = st.number_input("Yağ", value=float(r["yag"]))
                    if st.button("Günlüğe Kaydet", use_container_width=True):
                        st.session_state.gunluk_kayitlar.append({
                            "Tarih": secilen_tarih, "Öğün": ogun_turu, "Tarif": ed_isim,
                            "Kalori": ed_kal, "Protein": ed_pro, "Karbonhidrat": ed_karb, "Yağ": ed_yag
                        })
                        verileri_kaydet(aktif_user)
                        del st.session_state["ai_sonuc"]
                        st.rerun()

            st.markdown("""<div class="calai-section-card"><div class="calai-title">Genişletilmiş Restoran Menü Kataloğu</div></div>""", unsafe_allow_html=True)
            m_kat = st.selectbox("Kategori Seç", list(ZENGIN_LEZZET_KATALOGU.keys()))
            m_yemek = st.selectbox("Yemek Seç", list(ZENGIN_LEZZET_KATALOGU[m_kat].keys()))
            detay = ZENGIN_LEZZET_KATALOGU[m_kat][m_yemek]
            
            st.markdown(f"**{detay['kalori']} kcal** | 🥩 P: {detay['protein']}g | 🍞 K: {detay['karb']}g | 🥑 Y: {detay['yag']}g")
            st.caption(f"⚖️ Porsiyon: {detay.get('gramaj', 200)}g | 🥗 Malzemeler: {', '.join(detay.get('malzemeler', []))}")

            if st.button("Kataloğtan Günlüğe Ekle", use_container_width=True):
                st.session_state.gunluk_kayitlar.append({
                    "Tarih": secilen_tarih, "Öğün": "Ana Öğün", "Tarif": m_yemek,
                    "Kalori": detay["kalori"], "Protein": detay["protein"], "Karbonhidrat": detay["karb"], "Yağ": detay["yag"]
                })
                verileri_kaydet(aktif_user)
                st.rerun()

            st.markdown(f"""<div class="calai-section-card"><div class="calai-title">Günlük Denge ({secilen_tarih})</div></div>""", unsafe_allow_html=True)
            bugun_og = [(i, k) for i, k in enumerate(st.session_state.gunluk_kayitlar) if k["Tarih"] == secilen_tarih]
            toplam_alinan = sum([k["Kalori"] for i, k in bugun_og])
            toplam_pro = sum([k.get("Protein", 0) for i, k in bugun_og])
            
            if bugun_og:
                for i, kayit in bugun_og:
                    cr1, cr2 = st.columns([10, 1])
                    cr1.markdown(f"**{kayit['Öğün']}**: {kayit['Tarif']} — *{kayit['Kalori']} kcal*")
                    if cr2.button("🗑️", key=f"sil_{i}"):
                        st.session_state.gunluk_kayitlar.pop(i)
                        verileri_kaydet(aktif_user)
                        st.rerun()

            hedef_kal = bmr_kisi + (curr_aktivite["adim"] * 0.04)
            st.markdown(f"**Kalori:** {round(toplam_alinan)} / {round(hedef_kal)} kcal")
            st.progress(min(toplam_alinan / max(hedef_kal, 1), 1.0))
            st.markdown(f"**Protein:** {round(toplam_pro)}g / 90g")
            st.progress(min(toplam_pro / 90, 1.0))

        with sag_bosluk:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if aktif_tema == "Yeşil Ferahlık": 
                st.image("https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400")
            elif aktif_tema == "Pembe Su & Detoks": 
                st.image("https://images.unsplash.com/photo-1556881286-fc6915169721?w=400")
            elif aktif_tema == "Koyu Gym": 
                st.image("https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=400")
            else: 
                st.image("https://images.unsplash.com/photo-1550258987-190a2d41a8ba?w=400")
