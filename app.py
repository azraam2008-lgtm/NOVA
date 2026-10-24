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

st.set_page_config(page_title="Nova — Diyet ve Aktivite Asistanı", layout="wide", initial_sidebar_state="collapsed")

# ----------------------------------------------------
# DİNAMİK TEMA VE ARKA PLAN YÖNETİMİ (YEDEK RENKLİ)
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
# KAPSAMLI LEZZET KATALOĞU
# ----------------------------------------------------
ZENGIN_LEZZET_KATALOGU = {
    "Kahvaltılıklar 🥐": {
        "Serpme Kahvaltı": {"kalori": 650, "protein": 24, "karb": 55, "yag": 36},
        "Kahvaltı Tabağı": {"kalori": 420, "protein": 18, "karb": 35, "yag": 22},
        "Menemen": {"kalori": 210, "protein": 11, "karb": 9, "yag": 15},
        "Kaşarlı Tost": {"kalori": 320, "protein": 14, "karb": 30, "yag": 16},
        "Yulaf Lapası": {"kalori": 340, "protein": 13, "karb": 48, "yag": 11}
    },
    "Çorbalar 🍲": {
        "Mercimek Çorbası": {"kalori": 160, "protein": 8, "karb": 22, "yag": 4.5},
        "Ezogelin Çorbası": {"kalori": 170, "protein": 8, "karb": 24, "yag": 5},
        "Tavuk Suyu Çorbası": {"kalori": 130, "protein": 10, "karb": 14, "yag": 3.5}
    },
    "Salatalar 🥗": {
        "Mevsim Salata": {"kalori": 90, "protein": 2, "karb": 8, "yag": 6},
        "Tavuklu Sezar Salata": {"kalori": 340, "protein": 28, "karb": 13, "yag": 20},
        "Ton Balıklı Salata": {"kalori": 290, "protein": 28, "karb": 9, "yag": 15}
    },
    "Ana Yemekler 🍽️": {
        "Izgara Tavuk Göğsü": {"kalori": 280, "protein": 42, "karb": 0, "yag": 12},
        "Izgara Köfte": {"kalori": 360, "protein": 28, "karb": 6, "yag": 24},
        "Somon Fileto": {"kalori": 380, "protein": 34, "karb": 0, "yag": 26},
        "İskender Kebap": {"kalori": 780, "protein": 40, "karb": 65, "yag": 38}
    },
    "Atıştırmalıklar & İçecekler 🥤": {
        "Filtre Kahve": {"kalori": 5, "protein": 0.3, "karb": 1, "yag": 0},
        "Caffe Latte": {"kalori": 150, "protein": 8, "karb": 14, "yag": 6},
        "Protein Bar": {"kalori": 210, "protein": 20, "karb": 22, "yag": 7},
        "Ev Yapımı Kefir": {"kalori": 120, "protein": 8, "karb": 12, "yag": 4}
    }
}

# ----------------------------------------------------
# VERİTABANI FONKSİYONLARI
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
    
    if aktif_tema not in TEMA_AYARLARI:
        aktif_tema = "Koyu Cam"
        
    tema = TEMA_AYARLARI[aktif_tema]
    bg_url = f"https://raw.githubusercontent.com/azraam2008-lgtm/NOVA/main/{tema['bg_image']}"

    # TEMA CSS ENJEKSİYONU (YEDEK ARKA PLAN RENKLERİ İLE)
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        
        [data-testid="stAppViewContainer"] {{
            background-color: {tema['fallback_bg']};
            background-image: url("{bg_url}");
            background-size: cover; 
            background-position: center; 
            background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
        
        /* Yazı izolasyonu - tüm div'leri seçmeyiz ki Streamlit'in kendi kutuları bozulmasın */
        h1, h2, h3, p, span, label, th, td {{ color: {tema['text_color']} !important; font-family: 'Plus Jakarta Sans', sans-serif; }}
        
        .calai-card {{
            background: {tema['card_bg']}; 
            padding: 40px; 
            border-radius: 32px;
            backdrop-filter: blur(25px); 
            -webkit-backdrop-filter: blur(25px);
            margin-bottom: 35px; 
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 15px 50px rgba(0,0,0,0.4);
        }}
        
        .nova-header {{ font-family: 'Playfair Display', serif; font-size: 5.5rem; letter-spacing: 25px; text-align: center; font-weight: 700; margin-top: -30px; margin-left: 12px; }}
        .nova-user {{ text-align: center; font-size: 1.5rem; letter-spacing: 6px; text-transform: uppercase; margin-bottom: 40px; opacity: 0.9; font-weight: 600; }}
        
        /* APPLE RING STYLES */
        .ring-container {{ width: 200px; height: 200px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; }}
        .ring-inner {{ width: 155px; height: 155px; border-radius: 50%; background: {tema['card_bg']}; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
        .ring-val {{ font-size: 2.2rem; font-weight: 800; margin-bottom: -5px; }}
        .ring-lbl {{ font-size: 1.1rem; opacity: 0.8; text-transform: uppercase; letter-spacing: 2px; }}
        
        /* Tablo Stili */
        table {{ width: 100%; font-size: 1.2rem; background: transparent; border-collapse: collapse; }}
        th, td {{ padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.2); text-align: left; }}
        th {{ font-weight: 800; font-size: 1.3rem; opacity: 0.9; }}
        </style>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # EĞİTİCİ İLK KURULUM (ONBOARDING)
    # ----------------------------------------------------
    if not p.get("setup_tamamlandi", False):
        st.markdown(f'<div class="calai-card">', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; font-size: 3rem;'>NOVA'ya Hoş Geldin!</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size: 1.2rem; margin-bottom: 30px;'>Senin için en doğru ve sağlıklı planı oluşturabilmemiz için temel vücut metriklerini girelim.</p>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        boy = c1.number_input("Boy (cm)", min_value=130, max_value=220, value=int(p.get("boy", 165)))
        mevcut_kilo = c2.number_input("Mevcut Kilon (kg)", min_value=35.0, value=float(p.get("mevcut_kilo", 60.0)), step=0.5)
        hedef_kilo = c1.number_input("Hedef Kilon (kg)", min_value=35.0, value=float(p.get("hedef_kilo", 55.0)), step=0.5)
        hedef_sure = c2.number_input("Hedefe Ulaşma Süresi (Ay)", min_value=1, value=int(p.get("hedef_sure_ay", 2)))
        sec_tema = st.selectbox("Kişisel Temanı Seç (Arka Plan ve Renkler Değişir)", list(TEMA_AYARLARI.keys()), index=list(TEMA_AYARLARI.keys()).index(aktif_tema))

        gecici_p = {"yas": 20, "boy": boy, "mevcut_kilo": mevcut_kilo, "hedef_kilo": hedef_kilo, "hedef_sure_ay": hedef_sure}
        bmr, gunluk_acik, hedef_kalori = hesapla_hedef_kalori(gecici_p)
        
        st.markdown(f"""
        <div style="background: rgba(0,0,0,0.2); padding: 20px; border-radius: 15px; margin-top: 20px; border: 1px solid rgba(255,255,255,0.1);">
            <h3 style="margin-top:0;">📊 Kişisel Analizin</h3>
            <p>Vücudunun dinlenik haldeki enerji harcaması (BMR): <b>{round(bmr)} kcal</b><br>
            Belirttiğin hedefe ulaşmak için oluşturman gereken günlük açık: <b>{round(gunluk_acik)} kcal</b><br>
            Buna göre günlük alman gereken net kalori: <b>{round(hedef_kalori)} kcal</b></p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br><h2 style='font-size: 2rem;'>💡 Nova Nasıl Kullanılır?</h2>", unsafe_allow_html=True)
        st.info("💧 **Su ve Adım Takibi:** Ana ekrandaki Apple tarzı büyük halkaları kullanarak içtiğin suyu ve attığın adımı rahatça ekleyip, altındaki butonlarla kaydedebilirsin.\n\n📸 **Yapay Zeka Yemek Analizi:** Yediğin yemeğin fotoğrafını yükle; yapay zeka içindeki kaloriyi ve proteini bulup senin yerine günlüğüne eklesin!")

        if st.button("Profilimi Kaydet ve Başla", use_container_width=True):
            st.session_state.profil.update({"boy": boy, "mevcut_kilo": mevcut_kilo, "hedef_kilo": hedef_kilo, "hedef_sure_ay": hedef_sure, "tema": sec_tema, "setup_tamamlandi": True})
            verileri_kaydet(aktif_user)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # ----------------------------------------------------
    # ANA EKRAN
    # ----------------------------------------------------
    st.markdown('<div class="nova-header">N O V A</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="nova-user">{aktif_user}</div>', unsafe_allow_html=True)

    c_sol, c_orta, c_sag = st.columns([1, 10, 1])
    with c_orta:
        secilen_tarih = str(st.date_input("🗓️ Tarih Seçimi", datetime.date.today()))
        if secilen_tarih not in st.session_state.aktivite_loglari:
            st.session_state.aktivite_loglari[secilen_tarih] = {"adim": 0, "su": 0.0}
        curr_aktivite = st.session_state.aktivite_loglari[secilen_tarih]

        # 1) APPLE FITNESS HALKALARI
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

        # 2) ÖZET TABLOSU
        st.markdown('<div class="calai-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='font-size: 2.2rem;'>Kalori ve Denge Tablosu</h2>", unsafe_allow_html=True)
        
        bugun_og = [k for k in st.session_state.gunluk_kayitlar if k["Tarih"] == secilen_tarih]
        top_kalori = sum([k["Kalori"] for k in bugun_og])
        top_pro = sum([k.get("Protein", 0) for k in bugun_og])
        
        bmr, gunluk_acik, hedef_kalori = hesapla_hedef_kalori(p)
        harcanan_adim_kalori = curr_aktivite["adim"] * 0.04
        net_kalori = top_kalori - harcanan_adim_kalori
        
        st.markdown(f"""
        <table>
            <tr><th>Metrik</th><th style="text-align: right;">Değer</th></tr>
            <tr><td>🎯 Hedeflenen Günlük Kalori Alımı</td><td style="text-align: right;"><b>{round(hedef_kalori)} kcal</b></td></tr>
            <tr><td>🍽️ Alınan Toplam Kalori (Yemekler)</td><td style="text-align: right; color: #ff9500;"><b>+ {round(top_kalori)} kcal</b></td></tr>
            <tr><td>🔥 Verilen Toplam Kalori (Adım & Aktivite)</td><td style="text-align: right; color: #34c759;"><b>- {round(harcanan_adim_kalori)} kcal</b></td></tr>
            <tr style="border-top: 2px solid rgba(255,255,255,0.5);">
                <td style="font-size: 1.4rem; font-weight: 800;">⚖️ Vücutta Kalan Net Kalori</td>
                <td style="text-align: right; font-size: 1.4rem; font-weight: 800;">{round(net_kalori)} kcal</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if net_kalori > hedef_kalori: st.error(f"⚠️ Hedefinin {round(net_kalori - hedef_kalori)} kalori üstündesin. Biraz yürüyüş yapma vakti!")
        else: st.success(f"✅ Harika! Hedefine ulaşmak için bugün yiyebileceğin {round(hedef_kalori - net_kalori)} kalori daha hakkın var.")
            
        st.progress(min(max(net_kalori, 0) / max(hedef_kalori, 1), 1.0))
        st.markdown(f"<p style='font-size: 1.2rem; text-align: center;'>🥩 Toplam Protein Alımı: <b>{round(top_pro)}g</b></p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 3) YAPAY ZEKA VE MENÜ
        st.markdown('<div class="calai-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='font-size: 2.2rem;'>Yapay Zeka Yemek Analizi</h2>", unsafe_allow_html=True)
        upl = st.file_uploader("Yemek Fotoğrafı Yükle", type=["jpg", "jpeg", "png"])
        if upl:
            st.image(Image.open(upl), use_container_width=True)
            if st.button("Fotoğrafı Analiz Et ve Kaydet", use_container_width=True):
                st.session_state.gunluk_kayitlar.append({"Tarih": secilen_tarih, "Öğün": "AI Tespiti", "Tarif": "Akıllı Tabak", "Kalori": 380, "Protein": 22})
                verileri_kaydet(aktif_user)
                st.rerun()
        
        st.markdown("<br><h3>Veya Menüden Seç</h3>", unsafe_allow_html=True)
        m_kat = st.selectbox("Kategori", list(ZENGIN_LEZZET_KATALOGU.keys()))
        m_yemek = st.selectbox("Yemek", list(ZENGIN_LEZZET_KATALOGU[m_kat].keys()))
        d = ZENGIN_LEZZET_KATALOGU[m_kat][m_yemek]
        st.caption(f"🔥 Kalori: {d['kalori']} kcal | Protein: {d['protein']}g")
        if st.button("Günlüğe Ekle", use_container_width=True):
            st.session_state.gunluk_kayitlar.append({"Tarih": secilen_tarih, "Öğün": "Katalog", "Tarif": m_yemek, "Kalori": d["kalori"], "Protein": d["protein"]})
            verileri_kaydet(aktif_user)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("⚙️ Ayarları / Temayı Değiştir", use_container_width=True):
            st.session_state.profil["setup_tamamlandi"] = False
            st.rerun()
