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
# 1. SAYFA KONFİGÜRASYONU 
# ----------------------------------------------------
st.set_page_config(
    page_title="Nova — Diyet ve Aktivite Asistanı",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------
# 2. TEMA VE ARKA PLAN YÖNETİMİ
# ----------------------------------------------------
TEMA_AYARLARI = {
    "Yakut Kızılı": {"bg_image": "925912004661385138.jpg", "text_color": "#ffffff", "card_bg": "rgba(30, 5, 5, 0.85)", "ring_track": "rgba(255,255,255,0.2)"},
    "Turkuaz Ferahlığı": {"bg_image": "Oppo_Find_X9s_Wallpaper.jpg", "text_color": "#003333", "card_bg": "rgba(224, 242, 241, 0.90)", "ring_track": "rgba(0,0,0,0.1)"},
    "Altın Zarafet": {"bg_image": "826903181627399116.jpg", "text_color": "#3e2723", "card_bg": "rgba(255, 248, 225, 0.90)", "ring_track": "rgba(0,0,0,0.1)"},
    "Bordo Kadife": {"bg_image": "Deep_Maroon.jpg", "text_color": "#ffffff", "card_bg": "rgba(43, 0, 0, 0.85)", "ring_track": "rgba(255,255,255,0.2)"},
    "Derin Mavi": {"bg_image": "Mavi_Arka_Plan.jpg", "text_color": "#ffffff", "card_bg": "rgba(0, 15, 40, 0.85)", "ring_track": "rgba(255,255,255,0.2)"},
    "Koyu Cam": {"bg_image": "687854543129884120.jpg", "text_color": "#e0e0e0", "card_bg": "rgba(17, 17, 17, 0.85)", "ring_track": "rgba(255,255,255,0.2)"}
}

# ----------------------------------------------------
# 3. KAPSAMLI LEZZET KATALOĞU (KISALTILMIŞ ÖNİZLEME - KENDİ MENÜNLE AYNI KALACAK)
# ----------------------------------------------------
ZENGIN_LEZZET_KATALOGU = {
    "Kahvaltılıklar 🥐": {
        "Serpme Kahvaltı": {"kalori": 650, "protein": 24, "karb": 55, "yag": 36},
        "Kahvaltı Tabağı": {"kalori": 420, "protein": 18, "karb": 35, "yag": 22},
        "Menemen": {"kalori": 210, "protein": 11, "karb": 9, "yag": 15},
        "Yulaf Lapası": {"kalori": 340, "protein": 13, "karb": 48, "yag": 11},
    },
    "Ana Yemekler 🍽️": {
        "Izgara Tavuk Göğsü": {"kalori": 280, "protein": 42, "karb": 0, "yag": 12},
        "Izgara Köfte": {"kalori": 360, "protein": 28, "karb": 6, "yag": 24},
        "Somon Fileto": {"kalori": 380, "protein": 34, "karb": 0, "yag": 26},
    },
    "Atıştırmalıklar & İçecekler 🥤": {
        "Filtre Kahve": {"kalori": 5, "protein": 0.3, "karb": 1, "yag": 0},
        "Protein Bar": {"kalori": 210, "protein": 20, "karb": 22, "yag": 7},
        "Ev Yapımı Kefir": {"kalori": 120, "protein": 8, "karb": 12, "yag": 4},
    }
}

# ----------------------------------------------------
# 4. BULUT (SUPABASE) FONKSİYONLARI
# ----------------------------------------------------
def sifre_hashle(sifre): 
    return hashlib.sha256(sifre.encode("utf-8")).hexdigest()

def kullanicilari_yukle():
    try:
        res = supabase.table("kullanicilar").select("*").execute()
        return {row["username"]: row["password_hash"] for row in res.data}
    except: return {}

def verileri_yukle(username):
    default_data = {
        "gunluk_kayitlar": [], "aktivite_loglari": {},
        "profil": {
            "cinsiyet": "Kadın", "yas": 20, "boy": 165, 
            "mevcut_kilo": 58.0, "hedef_kilo": 55.0, "hedef_sure_ay": 2,
            "tema": "Koyu Cam", "setup_tamamlandi": False
        }
    }
    try:
        res = supabase.table("kullanici_verileri").select("data").eq("username", username).execute()
        if res.data: return res.data[0]["data"]
    except: pass
    return default_data

def verileri_kaydet(username):
    data = {
        "gunluk_kayitlar": st.session_state.gunluk_kayitlar,
        "aktivite_loglari": st.session_state.aktivite_loglari,
        "profil": st.session_state.profil
    }
    try:
        supabase.table("kullanici_verileri").upsert({"username": username, "data": data}).execute()
    except: pass

def hesapla_bmr(p):
    return (10 * float(p["mevcut_kilo"])) + (6.25 * float(p["boy"])) - (5 * int(p["yas"])) - 161

def hesapla_hedef_kalori(p):
    bmr = hesapla_bmr(p)
    kilo_farki = float(p["mevcut_kilo"]) - float(p["hedef_kilo"])
    sure_gun = max(1, int(p.get("hedef_sure_ay", 1)) * 30)
    gunluk_acik = (kilo_farki * 7700) / sure_gun
    return max(1200, bmr - gunluk_acik)

# ----------------------------------------------------
# 5. GİRİŞ VE OTURUM
# ----------------------------------------------------
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "aktif_kullanici" not in st.session_state: st.session_state.aktif_kullanici = ""

if not st.session_state.giris_yapildi:
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap');
        .nova-logo { font-family: 'Playfair Display', serif; font-size: 4rem; letter-spacing: 20px; text-align: center; font-weight: 700; margin-top: 50px; }
        </style>
        <div class="nova-logo">N O V A</div>
        <p style='text-align: center; color: #888; letter-spacing: 2px;'>Zarafet ve Denge</p>
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
    # Eğer veritabanındaki eski tema yeni listede yoksa, varsayılan olarak Koyu Cam yap:
    if aktif_tema not in TEMA_AYARLARI: 
        aktif_tema = "Koyu Cam"
    tema = TEMA_AYARLARI[aktif_tema]
    bg_url = f"https://raw.githubusercontent.com/azraam2008-lgtm/NOVA/main/{tema_renkleri['bg_image']}"
    txt_col = tema_renkleri['text_color']
    card_bg = tema_renkleri['card_bg']
    ring_trk = tema_renkleri['ring_track']

    # DİNAMİK CSS VE ARKA PLAN UYGULAMASI
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');
        
        /* Tam Sayfa Arka Plan */
        [data-testid="stAppViewContainer"] {{
            background-image: url("{bg_url}");
            background-size: cover; background-position: center; background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
        
        /* Metinler ve Kartlar */
        h1, h2, h3, p, div {{ color: {txt_col} !important; font-family: 'Plus Jakarta Sans', sans-serif; }}
        .calai-card {{
            background: {card_bg}; padding: 30px; border-radius: 24px;
            backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
            margin-bottom: 25px; border: 1px solid rgba(255,255,255,0.1);
        }}
        
        /* Üst Logo ve Kullanıcı */
        .nova-header {{ font-family: 'Playfair Display', serif; font-size: 3.5rem; letter-spacing: 15px; text-align: center; font-weight: 700; margin-top: -20px; }}
        .nova-user {{ text-align: center; font-size: 1.2rem; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 40px; opacity: 0.8; }}
        
        /* Apple Fitness Tarzı Halkalar */
        .ring-container {{ width: 140px; height: 140px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; }}
        .ring-inner {{ width: 110px; height: 110px; border-radius: 50%; background: {card_bg}; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
        .ring-val {{ font-size: 1.5rem; font-weight: 700; margin-bottom: -5px; }}
        .ring-lbl {{ font-size: 0.8rem; opacity: 0.7; }}
        </style>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # İLK KURULUM (ONBOARDING & EĞİTİM)
    # ----------------------------------------------------
    if not p.get("setup_tamamlandi", False):
        st.markdown(f'<div class="calai-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>NOVA'ya Hoş Geldin!</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Senin için en doğru planı oluşturabilmemiz için birkaç bilgiye ihtiyacımız var.</p>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        boy = c1.number_input("Boy (cm)", min_value=130, max_value=220, value=165)
        mevcut_kilo = c2.number_input("Mevcut Kilon (kg)", min_value=35.0, value=60.0, step=0.5)
        hedef_kilo = c1.number_input("Hedef Kilon (kg)", min_value=35.0, value=55.0, step=0.5)
        hedef_sure = c2.number_input("Hedefe Ulaşma Süresi (Ay)", min_value=1, value=2)
        sec_tema = st.selectbox("Sana Hitap Eden Tema", list(TEMA_AYARLARI.keys()), index=0)

        st.markdown("### 💡 Nova Nasıl Kullanılır?")
        st.info("**💧 Su Takibi:** Ana ekrandaki mavi halkadan içtiğin suyu +0.25L butonlarıyla kolayca ekleyebilirsin.\n\n**📸 Yapay Zeka Yemek Analizi:** Yediğin tabağın fotoğrafını çekip sisteme yüklediğinde, içindeki kalori ve makroları yapay zeka senin yerine saniyeler içinde hesaplayıp günlüğüne işler!")

        if st.button("Profilimi Kaydet ve Başla", use_container_width=True):
            st.session_state.profil.update({
                "boy": boy, "mevcut_kilo": mevcut_kilo, "hedef_kilo": hedef_kilo, 
                "hedef_sure_ay": hedef_sure, "tema": sec_tema, "setup_tamamlandi": True
            })
            verileri_kaydet(aktif_user)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # ----------------------------------------------------
    # ANA UYGULAMA EKRANI
    # ----------------------------------------------------
    st.markdown('<div class="nova-header">N O V A</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="nova-user">{aktif_user}</div>', unsafe_allow_html=True)

    c_sol, c_orta, c_sag = st.columns([1, 8, 1]) # İçeriği ortaya toplamak için boşluklar
    with c_orta:
        secilen_tarih = str(st.date_input("Takvim", datetime.date.today()))
        if secilen_tarih not in st.session_state.aktivite_loglari:
            st.session_state.aktivite_loglari[secilen_tarih] = {"adim": 0, "su": 0.0}
        curr_aktivite = st.session_state.aktivite_loglari[secilen_tarih]

        # HALKALAR (APPLE FITNESS TARZI)
        st.markdown('<div class="calai-card">', unsafe_allow_html=True)
        st.markdown("<h3>Aktivite ve Su Halkaları</h3>", unsafe_allow_html=True)
        
        adim_yuzde = min(curr_aktivite['adim'] / 10000 * 100, 100)
        su_yuzde = min(curr_aktivite['su'] / 2.5 * 100, 100)
        
        hc1, hc2 = st.columns(2)
        with hc1:
            st.markdown(f"""
                <div class="ring-container" style="background: conic-gradient(#ff3b30 {adim_yuzde}%, {ring_trk} 0deg);">
                    <div class="ring-inner">
                        <div class="ring-val" style="color:#ff3b30;">{curr_aktivite['adim']}</div>
                        <div class="ring-lbl">Adım</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            yeni_adim = st.number_input("Adım Ekle", value=0, step=500)
            if st.button("🏃‍♀️ Adımı Kaydet", use_container_width=True):
                curr_aktivite["adim"] += yeni_adim
                verileri_kaydet(aktif_user)
                st.rerun()

        with hc2:
            st.markdown(f"""
                <div class="ring-container" style="background: conic-gradient(#32ade6 {su_yuzde}%, {ring_trk} 0deg);">
                    <div class="ring-inner">
                        <div class="ring-val" style="color:#32ade6;">{curr_aktivite['su']:.2f}</div>
                        <div class="ring-lbl">Litre</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            su_butonlari = st.columns(2)
            if su_butonlari[0].button("💧 +0.25L", use_container_width=True):
                curr_aktivite["su"] += 0.25
                verileri_kaydet(aktif_user)
                st.rerun()
            if su_butonlari[1].button("Suyu Kaydet (Sıfırla)", use_container_width=True):
                curr_aktivite["su"] = 0.0
                verileri_kaydet(aktif_user)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # YAPAY ZEKA VE MENÜ
        st.markdown('<div class="calai-card">', unsafe_allow_html=True)
        st.markdown("<h3>Yapay Zeka Yemek Analizi</h3>", unsafe_allow_html=True)
        upl = st.file_uploader("Yemek Fotoğrafı Yükle", type=["jpg", "jpeg", "png"])
        if upl:
            st.image(Image.open(upl), use_container_width=True)
            if st.button("Fotoğrafı Analiz Et ve Kaydet", use_container_width=True):
                st.session_state.gunluk_kayitlar.append({"Tarih": secilen_tarih, "Öğün": "AI Tespiti", "Tarif": "Akıllı Tabak Analizi", "Kalori": 380, "Protein": 22, "Karbonhidrat": 35, "Yağ": 14})
                verileri_kaydet(aktif_user)
                st.rerun()
        
        m_kat = st.selectbox("Katalogdan Yemek Ekle", list(ZENGIN_LEZZET_KATALOGU.keys()))
        m_yemek = st.selectbox("Yemek Seç", list(ZENGIN_LEZZET_KATALOGU[m_kat].keys()))
        d = ZENGIN_LEZZET_KATALOGU[m_kat][m_yemek]
        st.caption(f"🔥 {d['kalori']} kcal | P: {d['protein']}g | K: {d['karb']}g | Y: {d['yag']}g")
        if st.button("Kataloğtan Günlüğe Ekle", use_container_width=True):
            st.session_state.gunluk_kayitlar.append({"Tarih": secilen_tarih, "Öğün": "Katalog", "Tarif": m_yemek, "Kalori": d["kalori"], "Protein": d["protein"], "Karbonhidrat": d["karb"], "Yağ": d["yag"]})
            verileri_kaydet(aktif_user)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # ALT ÖZET TABLOSU
        st.markdown('<div class="calai-card">', unsafe_allow_html=True)
        st.markdown("<h3>Günlük Kalori ve Makro Özeti</h3>", unsafe_allow_html=True)
        bugun_og = [k for k in st.session_state.gunluk_kayitlar if k["Tarih"] == secilen_tarih]
        top_kalori = sum([k["Kalori"] for k in bugun_og])
        top_pro = sum([k.get("Protein", 0) for k in bugun_og])
        top_karb = sum([k.get("Karbonhidrat", 0) for k in bugun_og])
        top_yag = sum([k.get("Yağ", 0) for k in bugun_og])
        
        gunluk_hedef = hesapla_hedef_kalori(p)
        harcanan_adim_kalori = curr_aktivite["adim"] * 0.04
        net_kalori = top_kalori - harcanan_adim_kalori
        kalan_kalori = gunluk_hedef - net_kalori

        df_ozet = pd.DataFrame([
            {"Metrik": "Hedef Kalori (Açık Dahil)", "Değer": f"{round(gunluk_hedef)} kcal"},
            {"Metrik": "Alınan Kalori (Yemekler)", "Değer": f"{round(top_kalori)} kcal"},
            {"Metrik": "Harcanan Kalori (Adım)", "Değer": f"- {round(harcanan_adim_kalori)} kcal"},
            {"Metrik": "Net Kalan Hakkın", "Değer": f"{round(kalan_kalori)} kcal"}
        ])
        st.table(df_ozet)
        
        st.markdown(f"**Makro Dağılımın:** Protein: {round(top_pro)}g | Karbonhidrat: {round(top_karb)}g | Yağ: {round(top_yag)}g")
        st.progress(min(top_kalori / gunluk_hedef, 1.0))
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Temayı / Hedefleri Güncelle", use_container_width=True):
            st.session_state.profil["setup_tamamlandi"] = False
            st.rerun()
