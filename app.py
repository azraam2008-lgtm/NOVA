import datetime
import hashlib
import json
import os
import pandas as pd
import streamlit as st

# 1. SAYFA KONFİGÜRASYONU & AMBLEM BAĞLANTISI
AMBLEM_URL = "https://raw.githubusercontent.com/azraam2008-lgtm/NOVA/main/amblem.jpg"

st.set_page_config(
    page_title="Nova — Diyet ve Aktivite Asistanı",
    page_icon=AMBLEM_URL,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
    <head>
        <link rel="apple-touch-icon" href="{AMBLEM_URL}">
        <link rel="icon" type="image/jpeg" href="{AMBLEM_URL}">
    </head>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------
# 2. GENEL STİLLER & CSS
# ----------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400;1,600&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');

    .stApp {
        background-color: #0b132b;
        color: #e0e1dd;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', Georgia, serif !important;
        letter-spacing: 0.5px;
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] {
        background-color: #1c2541;
        color: #e0e1dd;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Playfair Display', Georgia, serif;
        font-style: italic;
        font-size: 16px;
        color: #a0aab8;
        background-color: transparent;
        border-radius: 6px;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        border-bottom: 2px solid #48cae4 !important;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(28, 37, 65, 0.9) 0%, rgba(11, 19, 43, 0.95) 100%);
        border: 1px solid rgba(72, 202, 228, 0.25);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    [data-testid="stMetricLabel"] {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-style: italic !important;
        font-size: 15px !important;
        color: #a0aab8 !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 26px !important;
        color: #ffffff !important;
    }

    .nova-summary-card {
        background: linear-gradient(135deg, #1c2541 0%, #0b132b 100%);
        border: 1px solid #3a506b;
        border-left: 4px solid #48cae4;
        padding: 18px 24px;
        border-radius: 10px;
        margin-top: 15px;
        font-size: 15px;
        color: #e0e1dd;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }

    .recipe-card {
        background: linear-gradient(135deg, #1c2541 0%, #0b132b 100%);
        border: 1px solid rgba(72, 202, 228, 0.3);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        transition: 0.3s;
    }
    .recipe-card:hover {
        border-color: #48cae4;
        box-shadow: 0 6px 20px rgba(72, 202, 228, 0.2);
    }
    .recipe-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-style: italic;
        font-size: 18px;
        font-weight: 600;
        color: #48cae4;
        margin-bottom: 6px;
    }
    .recipe-details {
        font-size: 13.5px;
        color: #a0aab8;
    }

    .stButton > button {
        background-color: #3a506b;
        color: #ffffff;
        border: 1px solid #48cae4;
        border-radius: 8px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 500;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #48cae4;
        color: #0b132b;
        border-color: #48cae4;
    }

    .sidebar-user-card {
        text-align: center;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .sidebar-user-name {
        font-family: 'Playfair Display', Georgia, serif;
        font-style: italic;
        font-size: 18px;
        font-weight: 600;
        color: #ffffff;
        margin-top: 8px;
        margin-bottom: 5px;
    }

    .landing-subtext {
        font-family: 'Playfair Display', Georgia, serif;
        font-style: italic;
        font-size: 13.5px;
        line-height: 1.7;
        color: #9da8b5;
        text-align: justify;
        font-weight: 400;
        margin-top: 12px;
        margin-bottom: 20px;
        letter-spacing: 0.2px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

USERS_FILE = "kullanicilar.json"

LOGO_MAIN = """
<div style="text-align: center; font-family: 'Playfair Display', Georgia, serif; font-style: italic; font-size: 44px; font-weight: 700; letter-spacing: 22px; color: #ffffff; margin-bottom: 5px;">
    N&nbsp;&nbsp;O&nbsp;&nbsp;V&nbsp;&nbsp;A
</div>
"""

LOGO_SIDEBAR = """
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: 'Playfair Display', Georgia, serif; font-style: italic; font-size: 30px; font-weight: 700; color: #ffffff; gap: 8px; margin-top: 10px; margin-bottom: 15px;">
    <span>N</span>
    <span>O</span>
    <span>V</span>
    <span>A</span>
</div>
"""


# ----------------------------------------------------
# KULLANICI YÖNETİMİ & VERİTABANI
# ----------------------------------------------------
def sifre_hashle(sifre):
  return hashlib.sha256(sifre.encode("utf-8")).hexdigest()


def kullanicilari_yukle():
  if os.path.exists(USERS_FILE):
    try:
      with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return {}
  return {}


def kullanicilari_kaydet(users):
  with open(USERS_FILE, "w", encoding="utf-8") as f:
    json.dump(users, f, ensure_ascii=False, indent=4)


def kullanici_veri_dosyasi(username):
  return f"veriler_{username.lower().strip()}.json"


def verileri_yukle(username):
  user_file = kullanici_veri_dosyasi(username)
  default_data = {
      "besin_veritabani": {
          "tavuk gogsu": {
              "kalori": 165,
              "protein": 31.0,
              "karb": 0.0,
              "yag": 3.6,
          },
          "kofte": {"kalori": 220, "protein": 24.0, "karb": 2.0, "yag": 13.0},
          "ton baligi": {
              "kalori": 110,
              "protein": 25.0,
              "karb": 0.0,
              "yag": 1.0,
          },
          "marul": {"kalori": 15, "protein": 1.4, "karb": 2.9, "yag": 0.2},
          "salatalik": {"kalori": 15, "protein": 0.7, "karb": 3.6, "yag": 0.1},
          "domates": {"kalori": 18, "protein": 0.9, "karb": 3.9, "yag": 0.2},
          "zeytinyagi": {
              "kalori": 884,
              "protein": 0.0,
              "karb": 0.0,
              "yag": 100.0,
          },
          "dilim peynir": {
              "kalori": 320,
              "protein": 22.0,
              "karb": 1.5,
              "yag": 25.0,
          },
          "tam bugday ekmegi": {
              "kalori": 247,
              "protein": 13.0,
              "karb": 41.0,
              "yag": 3.4,
          },
          "labne": {"kalori": 210, "protein": 6.0, "karb": 4.0, "yag": 20.0},
          "sut": {"kalori": 50, "protein": 3.4, "karb": 4.8, "yag": 1.5},
          "kahve": {"kalori": 2, "protein": 0.1, "karb": 0.3, "yag": 0.0},
          "kefir": {"kalori": 60, "protein": 3.5, "karb": 4.5, "yag": 3.0},
          "x-lim toz": {"kalori": 20, "protein": 0.0, "karb": 5.0, "yag": 0.0},
          "badem": {"kalori": 575, "protein": 21.0, "karb": 22.0, "yag": 49.0},
          "mandalina": {"kalori": 53, "protein": 0.8, "karb": 13.3, "yag": 0.3},
          "meyveli soda": {
              "kalori": 45,
              "protein": 0.0,
              "karb": 11.0,
              "yag": 0.0,
          },
          "lahmacun": {
              "kalori": 220,
              "protein": 9.5,
              "karb": 28.0,
              "yag": 7.5,
          },
          "kiymali borek": {
              "kalori": 290,
              "protein": 9.0,
              "karb": 32.0,
              "yag": 14.0,
          },
          "taze fasulye": {
              "kalori": 45,
              "protein": 2.0,
              "karb": 7.0,
              "yag": 1.5,
          },
          "pirinc pilavi": {
              "kalori": 180,
              "protein": 3.0,
              "karb": 38.0,
              "yag": 2.5,
          },
          "bulgur pilavi": {
              "kalori": 150,
              "protein": 4.5,
              "karb": 30.0,
              "yag": 1.8,
          },
          "pirasa": {"kalori": 61, "protein": 1.5, "karb": 14.0, "yag": 0.3},
          "yulaf": {"kalori": 389, "protein": 16.9, "karb": 66.3, "yag": 6.9},
          "orman meyveleri": {
              "kalori": 57,
              "protein": 0.7,
              "karb": 13.6,
              "yag": 0.3,
          },
          "findik ezmesi": {
              "kalori": 628,
              "protein": 15.0,
              "karb": 17.0,
              "yag": 54.0,
          },
          "kofte burger": {
              "kalori": 250,
              "protein": 12.0,
              "karb": 25.0,
              "yag": 11.0,
          },
          "tavuk burger": {
              "kalori": 230,
              "protein": 13.0,
              "karb": 24.0,
              "yag": 9.0,
          },
          "patates kizartmasi": {
              "kalori": 312,
              "protein": 3.4,
              "karb": 41.0,
              "yag": 15.0,
          },
          "kola": {"kalori": 42, "protein": 0.0, "karb": 10.6, "yag": 0.0},
          "pizza": {"kalori": 266, "protein": 11.0, "karb": 33.0, "yag": 10.0},
          "elma": {"kalori": 52, "protein": 0.3, "karb": 14.0, "yag": 0.2},
          "baklava": {"kalori": 400, "protein": 5.0, "karb": 50.0, "yag": 20.0},
          "sutlac": {"kalori": 130, "protein": 3.5, "karb": 22.0, "yag": 3.0},
          "waffle": {"kalori": 350, "protein": 6.0, "karb": 45.0, "yag": 16.0},
          "spoonful tatlisi": {
              "kalori": 380,
              "protein": 4.0,
              "karb": 48.0,
              "yag": 18.0,
          },
          "pancake": {"kalori": 227, "protein": 6.0, "karb": 30.0, "yag": 9.0},
      },
      "hazir_tarifler": {
          "Tavuklu Salata": {
              "tavuk gogsu": 200,
              "marul": 30,
              "domates": 100,
              "salatalik": 100,
              "zeytinyagi": 10,
              "dilim peynir": 30,
              "tam bugday ekmegi": 25,
              "labne": 15,
          },
          "Köfteli Salata": {
              "kofte": 150,
              "marul": 30,
              "domates": 100,
              "salatalik": 100,
              "zeytinyagi": 10,
              "dilim peynir": 30,
              "tam bugday ekmegi": 25,
              "labne": 15,
          },
          "Ton Balıklı Salata": {
              "ton baligi": 110,
              "marul": 30,
              "domates": 100,
              "salatalik": 100,
              "zeytinyagi": 10,
              "dilim peynir": 30,
              "tam bugday ekmegi": 25,
              "labne": 15,
          },
          "Latte (Orta Boy)": {"sut": 250, "kahve": 30},
          "Americano (Orta Boy)": {"kahve": 20},
          "Kefir Karışımı": {"kefir": 200, "x-lim toz": 5},
          "Badem (1 Avuç)": {"badem": 30},
          "Mandalina (3 Adet)": {"mandalina": 300},
          "Meyveli Soda": {"meyveli soda": 200},
          "Standart Lahmacun (1 Adet)": {"lahmacun": 150},
          "Kıymalı Börek (Yarım Porsiyon)": {"kiymali borek": 100},
          "Taze Fasulye (1 Porsiyon)": {"taze fasulye": 200},
          "Pirinç Pilavı (1 Porsiyon)": {"pirinc pilavi": 150},
          "Bulgur Pilavı (1 Porsiyon)": {"bulgur pilavi": 150},
          "Pırasa (1 Porsiyon)": {"pirasa": 200},
          "Orman Meyveli Fındıklı Yulaf Lapası": {
              "sut": 200,
              "yulaf": 30,
              "orman meyveleri": 50,
              "findik ezmesi": 15,
          },
          "Standart Köfte Burger (1 Adet)": {"kofte burger": 200},
          "Tavuk Burger (1 Adet)": {"tavuk burger": 180},
          "Küçük Patates Kızartması": {"patates kizartmasi": 90},
          "Orta Patates Kızartması": {"patates kizartmasi": 130},
          "Büyük Patates Kızartması": {"patates kizartmasi": 180},
          "Orta Boy Kola (330ml)": {"kola": 330},
          "Büyük Boy Kola (500ml)": {"kola": 500},
          "Orta Boy Pizza (~300g)": {"pizza": 300},
          "Büyük Boy Pizza (~500g)": {"pizza": 500},
          "Elma (1 Adet)": {"elma": 150},
          "Baklava (1 Dilim)": {"baklava": 50},
          "Sütlaç (1 Porsiyon)": {"sutlac": 200},
          "Waffle (Standart Porsiyon)": {"waffle": 250},
          "Spoonful Tatlisi (1 Porsiyon)": {"spoonful tatlisi": 150},
          "Küçük Boy Pancake": {"pancake": 100},
      },
      "gunluk_kayitlar": [],
      "aktivite_loglari": {},
      "profil": {
          "cinsiyet": "Kadın",
          "yas": 20,
          "boy": 165,
          "mevcut_kilo": 58.0,
          "hedef_kilo": 55.0,
          "hedef_kalori": 1800,
          "hedef_protein": 90,
          "hedef_karb": 200,
          "hedef_yag": 60,
          "setup_tamamlandi": False,
      },
  }

  if os.path.exists(user_file):
    try:
      with open(user_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        profil = data.get("profil", {})
        if "mevcut_kilo" not in profil:
          profil["mevcut_kilo"] = profil.get("kilo", 58.0)
        if "hedef_kilo" not in profil:
          profil["hedef_kilo"] = 55.0
        if "setup_tamamlandi" not in profil:
          profil["setup_tamamlandi"] = True
        data["profil"] = profil

        for k, v in default_data["besin_veritabani"].items():
          if k not in data["besin_veritabani"]:
            data["besin_veritabani"][k] = v

        for k, v in default_data["hazir_tarifler"].items():
          if k not in data["hazir_tarifler"]:
            data["hazir_tarifler"][k] = v

        return data
    except:
      return default_data
  return default_data


def verileri_kaydet(username):
  user_file = kullanici_veri_dosyasi(username)
  data = {
      "besin_veritabani": st.session_state.besin_veritabani,
      "hazir_tarifler": st.session_state.hazir_tarifler,
      "gunluk_kayitlar": st.session_state.gunluk_kayitlar,
      "aktivite_loglari": st.session_state.aktivite_loglari,
      "profil": st.session_state.profil,
  }
  with open(user_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# ----------------------------------------------------
# 3. OTURUM KONTROLÜ VE GİRİŞ EKRANI
# ----------------------------------------------------
if "giris_yapildi" not in st.session_state:
  st.session_state.giris_yapildi = False
if "aktif_kullanici" not in st.session_state:
  st.session_state.aktif_kullanici = ""

if not st.session_state.giris_yapildi:
  st.markdown(
      '<div style="max-width: 760px; margin: 20px auto 0 auto; padding: 0px 15px;">'
      + LOGO_MAIN
      + '<p class="landing-subtext">Gökyüzünün derinliklerinde aniden parlayan'
      " bir yıldız gibidir dönüşüm... Karanlık suları aşan bir kuğunun asil"
      " zarafeti, pırlanta gibi parlayan yeni bir yaşam iradesiyle buluşur."
      " Nova; kendi potansiyeline uyanmak, bedenine hak ettiği değeri vermek ve"
      " her gün biraz daha parlayarak kendi en büyüleyici versiyonunu baştan"
      " yaratmak isteyenlerin sığınağıdır. Işıltınla parlamaya hazır"
      " mısın?</p></div>",
      unsafe_allow_html=True,
  )

  tab_giris, tab_kayit = st.tabs(["Giriş Yap", "Yeni Hesap Oluştur"])
  users = kullanicilari_yukle()

  with tab_giris:
    st.subheader("Hesabınıza Giriş Yapın")
    g_user = st.text_input("Kullanıcı Adı", key="g_user").strip().lower()
    g_pass = st.text_input("Şifre", type="password", key="g_pass")

    if st.button("Giriş Yap", key="btn_giris"):
      if g_user in users and users[g_user] == sifre_hashle(g_pass):
        st.session_state.giris_yapildi = True
        st.session_state.aktif_kullanici = g_user

        u_data = verileri_yukle(g_user)
        st.session_state.besin_veritabani = u_data["besin_veritabani"]
        st.session_state.hazir_tarifler = u_data["hazir_tarifler"]
        st.session_state.gunluk_kayitlar = u_data["gunluk_kayitlar"]
        st.session_state.aktivite_loglari = u_data["aktivite_loglari"]
        st.session_state.profil = u_data["profil"]

        st.success(f"Hoş geldin, {g_user.title()}!")
        st.rerun()
      else:
        st.error("Kullanıcı adı veya şifre hatalı!")

  with tab_kayit:
    st.subheader("Yeni Nova Hesabı Oluştur")
    k_user = st.text_input("Yeni Kullanıcı Adı", key="k_user").strip().lower()
    k_pass = st.text_input("Şifre Oluştur", type="password", key="k_pass")
    k_pass_repeat = st.text_input(
        "Şifreyi Tekrar Girin", type="password", key="k_pass_rep"
    )

    if st.button("Kayıt Ol", key="btn_kayit"):
      if not k_user or not k_pass:
        st.warning("Lütfen kullanıcı adı ve şifre belirleyin.")
      elif k_pass != k_pass_repeat:
        st.error("Şifreler birbiriyle eşleşmiyor.")
      elif k_user in users:
        st.error(
            "Bu kullanıcı adı zaten alınmış. Lütfen başka bir kullanıcı adı"
            " seçin."
        )
      else:
        users[k_user] = sifre_hashle(k_pass)
        kullanicilari_kaydet(users)
        st.success(
            "Hesabınız başarıyla oluşturuldu! Şimdi 'Giriş Yap' sekmesinden"
            " giriş yapabilirsiniz."
        )

else:
  # ----------------------------------------------------
  # 4. ANA UYGULAMA PANELİ
  # ----------------------------------------------------
  aktif_user = st.session_state.aktif_kullanici

  st.sidebar.markdown(LOGO_SIDEBAR, unsafe_allow_html=True)

  st.sidebar.markdown(
      f"""
      <div class="sidebar-user-card">
          <div class="sidebar-user-name">{aktif_user.title()}</div>
      </div>
  """,
      unsafe_allow_html=True,
  )

  if st.sidebar.button("Çıkış Yap", use_container_width=True):
    st.session_state.giris_yapildi = False
    st.session_state.aktif_kullanici = ""
    st.rerun()

  st.sidebar.divider()

  is_first_login = not st.session_state.profil.get("setup_tamamlandi", True)
  default_menu_index = 3 if is_first_login else 0

  menu = st.sidebar.selectbox(
      "Navigasyon Menüsü",
      [
          "Günlük Takip Paneli",
          "Haftalık Program & Değerlendirme",
          "Tarif & Malzeme Yönetimi",
          "Hedef & Kilo Analiz Sihirbazı",
      ],
      index=default_menu_index,
  )

  if is_first_login:
    st.info(
        "✨ **Nova'ya Hoş Geldin!** Yolculuğuna kusursuz başlayabilmek için"
        " lütfen aşağıdaki **Hedef & Kilo Analiz Sihirbazı** ekranından"
        " boyunu, kilonu, aktivite düzeyini ve hedeflerini belirle."
    )

  # ----------------------------------------------------
  # GÜNLÜK TAKİP PANELİ
  # ----------------------------------------------------
  if menu == "Günlük Takip Paneli":
    st.header(f"Günlük Beslenme ve Aktivite — {aktif_user.title()}")

    secilen_tarih = str(st.date_input("Kayıt Tarihi", datetime.date.today()))

    if secilen_tarih not in st.session_state.aktivite_loglari:
      st.session_state.aktivite_loglari[secilen_tarih] = {
          "adim": 10000,
          "su": 2.0,
          "pilates_tur": "Mat Pilates",
          "pilates_sure": 45,
          "yuruyus_tur": "Orta Tempo (5 km/s)",
          "yuruyus_sure": 30,
      }

    col1, col2 = st.columns(2)

    with col1:
      st.subheader("Öğün Girişi")
      ogun_turu = st.selectbox(
          "Öğün Türü", ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"]
      )
      secilen_tarif = st.selectbox(
          "Mevcut Tarifler", list(st.session_state.hazir_tarifler.keys())
      )

      if st.button("Öğüne Ekle"):
        malzemeler = st.session_state.hazir_tarifler[secilen_tarif]
        t_kalori, t_protein, t_karb, t_yag = 0, 0, 0, 0
        detaylar = []

        for m, gram in malzemeler.items():
          if m in st.session_state.besin_veritabani:
            b = st.session_state.besin_veritabani[m]
            oran = gram / 100.0
            t_kalori += b["kalori"] * oran
            t_protein += b["protein"] * oran
            t_karb += b["karb"] * oran
            t_yag += b["yag"] * oran
            detaylar.append(f"{gram}g {m}")

        st.session_state.gunluk_kayitlar.append({
            "Tarih": secilen_tarih,
            "Öğün": ogun_turu,
            "Tarif": secilen_tarif,
            "İçerik": ", ".join(detaylar),
            "Kalori": round(t_kalori, 1),
            "Protein": round(t_protein, 1),
            "Karbonhidrat": round(t_karb, 1),
            "Yağ": round(t_yag, 1),
        })
        verileri_kaydet(aktif_user)
        st.success(f"'{secilen_tarif}' öğüne eklendi.")

    with col2:
      st.subheader("Günlük Aktivite ve Hareket")
      curr_aktivite = st.session_state.aktivite_loglari[secilen_tarih]

      adim_sayisi = st.number_input(
          "Günlük Adım Sayısı",
          min_value=0,
          max_value=60000,
          value=int(curr_aktivite["adim"]),
          step=500,
      )

      su_miktari = curr_aktivite["su"]

      st.markdown(
          "<div style='text-align: center; font-family: \"Playfair"
          " Display\"; font-style: italic; color: #48cae4; font-size: 15px;"
          " margin-top: 10px; margin-bottom: 2px;'>Su Tüketim Halkası</div>",
          unsafe_allow_html=True,
      )

      max_su = 3.0
      su_oran = min(1.0, su_miktari / max_su)
      c_circumference = 2 * 3.14159 * 38
      c_offset = c_circumference * (1 - su_oran)

      st.markdown(
          f"""
            <div style="display: flex; align-items: center; justify-content: center; margin: 5px 0 10px 0;">
                <div style="position: relative; width: 100px; height: 100px;">
                    <svg width="100" height="100" style="transform: rotate(-90deg);">
                        <circle cx="50" cy="50" r="38" stroke="#1c2541" stroke-width="8" fill="transparent"/>
                        <circle cx="50" cy="50" r="38" stroke="#48cae4" stroke-width="8" stroke-dasharray="{c_circumference}" stroke-dashoffset="{c_offset}" stroke-linecap="round" fill="transparent"/>
                    </svg>
                    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: 'Plus Jakarta Sans', sans-serif;">
                        <span style="font-size: 18px; font-weight: 700; color: #ffffff;">{su_miktari:.1f}L</span>
                        <span style="font-size: 9px; color: #a0aab8; letter-spacing: 1px;">SU RİNGİ</span>
                    </div>
                </div>
            </div>
            """,
          unsafe_allow_html=True,
      )

      c_s1, c_s2, c_s3, c_s4 = st.columns(4)
      if c_s1.button("-0.5L", key="su_az_05"):
        if su_miktari >= 0.5:
          su_miktari = round(su_miktari - 0.5, 1)
          curr_aktivite["su"] = su_miktari
          verileri_kaydet(aktif_user)
          st.rerun()
      if c_s2.button("-0.25L", key="su_az_025"):
        if su_miktari >= 0.25:
          su_miktari = round(su_miktari - 0.25, 2)
          curr_aktivite["su"] = su_miktari
          verileri_kaydet(aktif_user)
          st.rerun()
      if c_s3.button("+0.25L", key="su_art_025"):
        su_miktari = round(su_miktari + 0.25, 2)
        curr_aktivite["su"] = su_miktari
        verileri_kaydet(aktif_user)
        st.rerun()
      if c_s4.button("+0.5L", key="su_art_05"):
        su_miktari = round(su_miktari + 0.5, 1)
        curr_aktivite["su"] = su_miktari
        verileri_kaydet(aktif_user)
        st.rerun()

      pilates_secenekleri = [
          "Mat Pilates",
          "Reformer Pilates",
          "Yoğun / Klinik Pilates",
      ]
      p_tur_idx = (
          pilates_secenekleri.index(curr_aktivite["pilates_tur"])
          if curr_aktivite["pilates_tur"] in pilates_secenekleri
          else 0
      )
      p_tur = st.selectbox(
          "Pilates Türü", pilates_secenekleri, index=p_tur_idx
      )
      p_sure = st.number_input(
          "Pilates Süresi (Dakika)",
          min_value=0,
          value=int(curr_aktivite["pilates_sure"]),
          step=5,
      )

      yuruyus_secenekleri = [
          "Hafif Tempo (4 km/s)",
          "Orta Tempo (5 km/s)",
          "Tempolu / Eğimli (6.5 km/s)",
      ]
      y_tur_idx = (
          yuruyus_secenekleri.index(curr_aktivite["yuruyus_tur"])
          if curr_aktivite["yuruyus_tur"] in yuruyus_secenekleri
          else 0
      )
      y_tur = st.selectbox(
          "Yürüyüş Temposu", yuruyus_secenekleri, index=y_tur_idx
      )
      y_sure = st.number_input(
          "Yürüyüş Süresi (Dakika)",
          min_value=0,
          value=int(curr_aktivite["yuruyus_sure"]),
          step=5,
      )

      if st.button("Aktiviteleri Güncelle"):
        st.session_state.aktivite_loglari[secilen_tarih] = {
            "adim": adim_sayisi,
            "su": su_miktari,
            "pilates_tur": p_tur,
            "pilates_sure": p_sure,
            "yuruyus_tur": y_tur,
            "yuruyus_sure": y_sure,
        }
        verileri_kaydet(aktif_user)
        st.success("Aktivite bilgileri kaydedildi.")

    st.markdown("---")
    st.subheader(f"✨ {secilen_tarih} Tarihli Öğünler ve Denge")

    kilo_val = st.session_state.profil["mevcut_kilo"]
    boy_val = st.session_state.profil["boy"]
    yas_val = st.session_state.profil["yas"]
    cins_val = st.session_state.profil["cinsiyet"]

    if cins_val == "Kadın":
      bmr = (10 * kilo_val) + (6.25 * boy_val) - (5 * yas_val) - 161
    else:
      bmr = (10 * kilo_val) + (6.25 * boy_val) - (5 * yas_val) + 5

    met_p = {
        "Mat Pilates": 3.0,
        "Reformer Pilates": 4.0,
        "Yoğun / Klinik Pilates": 5.0,
    }
    met_y = {
        "Hafif Tempo (4 km/s)": 2.9,
        "Orta Tempo (5 km/s)": 3.5,
        "Tempolu / Eğimli (6.5 km/s)": 5.0,
    }

    aktivite_guncel = st.session_state.aktivite_loglari[secilen_tarih]
    pilates_kalori = (
        met_p.get(aktivite_guncel["pilates_tur"], 3.0) * 3.5 * kilo_val / 200
    ) * aktivite_guncel["pilates_sure"]
    yuruyus_kalori = (
        met_y.get(aktivite_guncel["yuruyus_tur"], 3.5) * 3.5 * kilo_val / 200
    ) * aktivite_guncel["yuruyus_sure"]
    adim_kalorisi = (aktivite_guncel["adim"] / 1000) * 40

    toplam_harcanan = bmr + pilates_kalori + yuruyus_kalori + adim_kalorisi

    bugun_kayitlari = [
        (idx, item)
        for idx, item in enumerate(st.session_state.gunluk_kayitlar)
        if item.get("Tarih") == secilen_tarih
    ]

    if bugun_kayitlari:
      toplam_alinan = sum(item["Kalori"] for _, item in bugun_kayitlari)
      toplam_protein = sum(item["Protein"] for _, item in bugun_kayitlari)
      toplam_karb = sum(item["Karbonhidrat"] for _, item in bugun_kayitlari)
      toplam_yag = sum(item["Yağ"] for _, item in bugun_kayitlari)

      st.markdown(
          "<div style='margin-bottom: 12px; font-style: italic; color:"
          " #a0aab8; font-size: 14px;'>Seçilen tarihe ait kayıtlı öğünleriniz"
          " aşağıda renkli kartlar halinde listelenmektedir:</div>",
          unsafe_allow_html=True,
      )

      ogun_renkleri = {
          "Kahvaltı": {
              "bg": "linear-gradient(135deg, rgba(28, 37, 65, 0.95) 0%, rgba(72, 202, 228, 0.15) 100%)",
              "border": "#48cae4",
              "badge": "#48cae4",
          },
          "Öğle Yemeği": {
              "bg": "linear-gradient(135deg, rgba(28, 37, 65, 0.95) 0%, rgba(144, 224, 239, 0.15) 100%)",
              "border": "#90e0ef",
              "badge": "#90e0ef",
          },
          "Akşam Yemeği": {
              "bg": "linear-gradient(135deg, rgba(28, 37, 65, 0.95) 0%, rgba(0, 150, 199, 0.15) 100%)",
              "border": "#0096c7",
              "badge": "#0096c7",
          },
          "Ara Öğün": {
              "bg": "linear-gradient(135deg, rgba(28, 37, 65, 0.95) 0%, rgba(202, 240, 248, 0.15) 100%)",
              "border": "#caf0f8",
              "badge": "#caf0f8",
          },
      }

      for idx, item in bugun_kayitlari:
        o_turu = item.get("Öğün", "Ara Öğün")
        tema = ogun_renkleri.get(
            o_turu,
            {
                "bg": "linear-gradient(135deg, #1c2541 0%, #0b132b 100%)",
                "border": "#48cae4",
                "badge": "#48cae4",
            },
        )

        col_card, col_btn = st.columns([12, 1])
        with col_card:
          st.markdown(
              f"""
                <div style="background: {tema['bg']}; border: 1px solid {tema['border']}; border-left: 5px solid {tema['badge']}; border-radius: 12px; padding: 16px 20px; margin-bottom: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); transition: 0.3s;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <span style="background-color: {tema['badge']}; color: #0b132b; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">{o_turu}</span>
                            <strong style="color: #ffffff; margin-left: 10px; font-size: 17px; font-family: 'Playfair Display', Georgia, serif; font-style: italic;">{item['Tarif']}</strong>
                        </div>
                        <div style="font-size: 14px;">
                            <span style="color: #48cae4; font-weight: 700;">🔥 {item['Kalori']} kcal</span> &nbsp;|&nbsp; 
                            <span style="color: #a0aab8;">P: <strong>{item['Protein']}g</strong> &nbsp;|&nbsp; K: <strong>{item['Karbonhidrat']}g</strong> &nbsp;|&nbsp; Y: <strong>{item['Yağ']}g</strong></span>
                        </div>
                    </div>
                    <div style="font-size: 13.5px; color: #cbd5e1; margin-top: 8px; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 8px;">
                        🥗 <strong>İçerik:</strong> {item['İçerik']}
                    </div>
                </div>
                """,
              unsafe_allow_html=True,
          )
        with col_btn:
          st.write("")
          if st.button("🗑️", key=f"del_{idx}", help="Bu öğünü sil"):
            st.session_state.gunluk_kayitlar.pop(idx)
            verileri_kaydet(aktif_user)
            st.rerun()
    else:
      toplam_alinan, toplam_protein, toplam_karb, toplam_yag = 0.0, 0.0, 0.0, 0.0
      st.info(
          f"📅 {secilen_tarih} tarihinde henüz kaydedilmiş bir öğün bulunmuyor."
      )

    net_fark = toplam_alinan - toplam_harcanan

    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    c_m1.metric("Alınan Kalori", f"{toplam_alinan:.1f} kcal")
    c_m2.metric("Harcanan Kalori", f"{toplam_harcanan:.1f} kcal")
    c_m3.metric("Net Kalori Dengesi", f"{net_fark:+.1f} kcal")
    c_m4.metric("Su Tüketimi", f"{aktivite_guncel['su']} Liter")

    st.markdown(
        f"""
        <div class="nova-summary-card">
            <span>✨ <strong>Makro Dağılımı:</strong> Protein: <strong>{toplam_protein:.1f}g</strong> | Karbonhidrat: <strong>{toplam_karb:.1f}g</strong> | Yağ: <strong>{toplam_yag:.1f}g</strong></span>
            <span>👟 <strong>Adım Hedefi:</strong> <strong>{aktivite_guncel['adim']} adım</strong></span>
        </div>
    """,
        unsafe_allow_html=True,
    )

  # ----------------------------------------------------
  # HAFTALIK PROGRAM & DEĞERLENDİRME
  # ----------------------------------------------------
  elif menu == "Haftalık Program & Değerlendirme":
    st.header("Haftalık Program ve Kalori Değerlendirmesi")

    if st.session_state.gunluk_kayitlar:
      df_tum = pd.DataFrame(st.session_state.gunluk_kayitlar)
      haftalik_ozet = (
          df_tum.groupby("Tarih")[["Kalori", "Protein", "Karbonhidrat", "Yağ"]]
          .sum()
          .reset_index()
      )
      haftalik_ozet = haftalik_ozet.sort_values("Tarih")

      st.subheader("📅 Gün Bazlı Geçmiş Dökümü")
      st.dataframe(haftalik_ozet, use_container_width=True)

      hedef_k = st.session_state.profil.get("hedef_kalori", 1800)
      haftalik_ozet["Hedef Kalori"] = hedef_k
      haftalik_ozet["Fark (Alınan - Hedef)"] = (
          haftalik_ozet["Kalori"] - haftalik_ozet["Hedef Kalori"]
      )

      st.subheader("📊 Haftalık Alınan Kalori Trendi")
      st.markdown(
          "<span style='color: #a0aab8; font-size: 13.5px;'>Günlere göre"
          " aldığın kalori miktarları aşağıda çizgi grafiği olarak"
          " gösterilmektedir.</span>",
          unsafe_allow_html=True,
      )

      chart_df = haftalik_ozet.set_index("Tarih")[["Kalori"]]
      st.line_chart(chart_df, color="#48cae4")

      ortalama_kalori = haftalik_ozet["Kalori"].mean()

      st.markdown(
          f"**Haftalık Ortalama Alınan Kalori:** {ortalama_kalori:.1f} kcal"
          f" (Sihirbaz Hedefiniz: {hedef_k} kcal)"
      )
      if ortalama_kalori > hedef_k + 50:
        st.warning(
            f"⚠️ Haftalık ortalamanız ({ortalama_kalori:.1f} kcal), hedef"
            f" kalori aralığınızın ({hedef_k} kcal) üzerindedir."
        )
      elif ortalama_kalori < hedef_k - 100:
        st.info(
            f"💡 Haftalık ortalamanız ({ortalama_kalori:.1f} kcal), hedef"
            f" kalorinizin ({hedef_k} kcal) altındadır."
        )
      else:
        st.success(
            f"✨ Mükemmel! Haftalık ortalamanız ({ortalama_kalori:.1f} kcal),"
            f" hedef kalori aralığı ile tam uyumludur."
        )
    else:
      st.info("Değerlendirme yapabilmek için günlük kayıtlar eklemelisiniz.")

  # ----------------------------------------------------
  # TARİF & MALZEME YÖNETİMİ
  # ----------------------------------------------------
  elif menu == "Tarif & Malzeme Yönetimi":
    st.header("Tarif ve Malzeme Yönetim Paneli")

    tab1, tab2 = st.tabs(
        ["1. Yeni Malzeme Ekle", "2. Gramaj Esaslı Estetik Tarif Kütüphanesi"]
    )

    with tab1:
      st.subheader("Veritabanına Yeni Malzeme Tanımla (100g / ml Başına)")
      m_ad = st.text_input("Malzeme Adı (Örn: Lor Peyniri, Yulaf vb.)")
      m_kal = st.number_input(
          "100 gramdaki Kalori (kcal)", min_value=0.0, value=100.0, step=5.0
      )
      m_pro = st.number_input(
          "100 gramdaki Protein (g)", min_value=0.0, value=10.0, step=1.0
      )
      m_kar = st.number_input(
          "100 gramdaki Karbonhidrat (g)", min_value=0.0, value=5.0, step=1.0
      )
      m_yag = st.number_input(
          "100 gramdaki Yağ (g)", min_value=0.0, value=3.0, step=1.0
      )

      if st.button("Malzemeyi Veritabanına Kaydet"):
        if m_ad.strip():
          temiz_ad = m_ad.strip().lower()
          st.session_state.besin_veritabani[temiz_ad] = {
              "kalori": m_kal,
              "protein": m_pro,
              "karb": m_kar,
              "yag": m_yag,
          }
          verileri_kaydet(aktif_user)
          st.success(f"'{m_ad}' başarıyla veritabanınıza eklendi!")
        else:
          st.warning("Lütfen geçerli bir malzeme adı girin.")

      st.markdown("---")
      st.subheader("🥗 Mevcut Malzeme Listesi")
      df_malzeme = pd.DataFrame([
          {
              "Malzeme Adı": k.title(),
              "Kalori (100g/ml)": v["kalori"],
              "Protein (g)": v["protein"],
              "Karb (g)": v["karb"],
              "Yağ (g)": v["yag"],
          }
          for k, v in st.session_state.besin_veritabani.items()
      ])
      st.dataframe(df_malzeme, use_container_width=True)

    with tab2:
      st.subheader("Gramaj Esaslı Yeni Tarif / Yemek Oluştur")
      t_ad = st.text_input("Tarif / Yemek Adı (Örn: Omlet, Yulaf Lapası vb.)")

      secilen_malzemeler = st.multiselect(
          "Tarifte Kullanılacak Malzemeleri Seç",
          list(st.session_state.besin_veritabani.keys()),
      )

      tarif_gramajlari = {}
      if secilen_malzemeler:
        st.markdown("**Seçilen Malzemelerin Miktarları (Gram / ml):**")
        for m in secilen_malzemeler:
          gr = st.number_input(
              f"{m.title()} kaç gram/ml?",
              min_value=1.0,
              value=100.0,
              step=5.0,
              key=f"gram_{m}",
          )
          tarif_gramajlari[m] = gr

      if st.button("Bu Tarifi Kütüphaneye Kaydet"):
        if t_ad.strip() and tarif_gramajlari:
          st.session_state.hazir_tarifler[t_ad.strip()] = tarif_gramajlari
          verileri_kaydet(aktif_user)
          st.success(f"'{t_ad}' tarifi kütüphanenize kaydedildi!")
        else:
          st.warning("Lütfen tarif adı yazın ve en az bir malzeme seçin.")

      st.markdown("---")
      st.subheader("✨ Kayıtlı Tarifleriniz ve Lezzet Kartları")

      for tarif_adi, icerik in st.session_state.hazir_tarifler.items():
        t_kal, t_pro, t_kar, t_yag = 0, 0, 0, 0
        detay_listesi = []
        for m, gr in icerik.items():
          detay_listesi.append(f"{gr}g {m.title()}")
          if m in st.session_state.besin_veritabani:
            b = st.session_state.besin_veritabani[m]
            oran = gr / 100.0
            t_kal += b["kalori"] * oran
            t_pro += b["protein"] * oran
            t_kar += b["karb"] * oran
            t_yag += b["yag"] * oran

        detay_str = ", ".join(detay_listesi)
        st.markdown(
            f"""
            <div class="recipe-card">
                <div class="recipe-title">🔹 {tarif_adi}</div>
                <div class="recipe-details"><strong>İçerik:</strong> {detay_str}</div>
                <div style="margin-top: 8px; font-size: 13px; color: #ffffff;">
                    🔥 <strong>{t_kal:.1f} kcal</strong> &nbsp;|&nbsp; 
                    P: <strong>{t_pro:.1f}g</strong> &nbsp;|&nbsp; 
                    K: <strong>{t_kar:.1f}g</strong> &nbsp;|&nbsp; 
                    Y: <strong>{t_yag:.1f}g</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

  # ----------------------------------------------------
  # HEDEF & KİLO ANALİZ SİHİRBAZI
  # ----------------------------------------------------
  elif menu == "Hedef & Kilo Analiz Sihirbazı":
    st.header("Kişiselleştirilmiş Hedef, Kilo ve Kalori Açığı Sihirbazı")

    p = st.session_state.profil

    c1, c2, c3 = st.columns(3)
    cinsiyet = c1.selectbox(
        "Cinsiyet",
        ["Kadın", "Erkek"],
        index=0 if p["cinsiyet"] == "Kadın" else 1,
    )
    yas = c2.number_input(
        "Yaş", min_value=15, max_value=80, value=int(p["yas"])
    )
    boy = c3.number_input(
        "Boy (cm)", min_value=120, max_value=210, value=int(p["boy"])
    )

    c4, c5 = st.columns(2)
    mevcut_kilo = c4.number_input(
        "Mevcut Kilon (kg)",
        min_value=35.0,
        max_value=160.0,
        value=float(p["mevcut_kilo"]),
        step=0.5,
    )
    hedef_kilo = c5.number_input(
        "Hedeflenen Kilon (kg)",
        min_value=30.0,
        max_value=150.0,
        value=float(p["hedef_kilo"]),
        step=0.5,
    )

    aktivite = st.selectbox(
        "Aktivite Düzeyi",
        [
            "Hareketsiz / Masa Başı",
            "Hafif Aktif (Haftada 1-3 gün)",
            "Orta Aktif (Haftada 3-5 gün)",
            "Çok Aktif",
        ],
    )

    if st.button("Hedeflerimi ve Süreyi Hesapla"):
      if cinsiyet == "Kadın":
        bmr = (10 * mevcut_kilo) + (6.25 * boy) - (5 * yas) - 161
      else:
        bmr = (10 * mevcut_kilo) + (6.25 * boy) - (5 * yas) + 5

      carpanlar = {
          "Hareketsiz / Masa Başı": 1.2,
          "Hafif Aktif (Haftada 1-3 gün)": 1.375,
          "Orta Aktif (Haftada 3-5 gün)": 1.55,
          "Çok Aktif": 1.725,
      }

      tdee = bmr * carpanlar[aktivite]
      kilo_farki = mevcut_kilo - hedef_kilo

      st.session_state.profil["cinsiyet"] = cinsiyet
      st.session_state.profil["yas"] = yas
      st.session_state.profil["boy"] = boy
      st.session_state.profil["mevcut_kilo"] = mevcut_kilo
      st.session_state.profil["hedef_kilo"] = hedef_kilo
      st.session_state.profil["setup_tamamlandi"] = True

      if kilo_farki > 0:
        hedef_kalori = tdee - 500
        st.session_state.profil["hedef_kalori"] = round(hedef_kalori)

        toplam_yakilacak_yag_kcal = kilo_farki * 7700
        tahmini_gun = toplam_yakilacak_yag_kcal / 500
        tahmini_hafta = tahmini_gun / 7

        st.success(
            "Hedefleriniz başarıyla hesaplandı, kaydedildi ve ilk kurulum"
            " tamamlandı!"
        )
        st.markdown("---")
        st.subheader("📊 Analiz ve Tahmin Sonuçları")
        st.metric("Mevcut Kilo", f"{mevcut_kilo} kg")
        st.metric("Hedef Kilo", f"{hedef_kilo} kg")
        st.metric("Kilo Farkı", f"-{kilo_farki:.1f} kg (Verilmesi Gereken)")
        st.metric(
            "Günlük Harcanan Toplam Enerji (TDEE)", f"{round(tdee)} kcal"
        )
        st.metric("Önerilen Günlük Kalori Alımı", f"{round(hedef_kalori)} kcal")
        st.markdown(
            "💡 **Kalori Açığı:** Kilo verebilmek için günlük harcamanızın"
            f" altında, **{round(hedef_kalori)} kcal** beslenmeli ve günde"
            " yaklaşık **500 kcal açık** oluşturmalısınız."
        )
        st.markdown(
            "⏱️ **Tahmini Süre:** Haftada ortalama 0.5 kg vererek bu hedefe"
            f" **yaklaşık {tahmini_hafta:.1f} haftada (yaklaşık"
            f" {round(tahmini_gun)} günde)** ulaşabilirsiniz."
        )

      elif kilo_farki < 0:
        hedef_kalori = tdee + 300
        st.session_state.profil["hedef_kalori"] = round(hedef_kalori)

        tahmini_gun = abs(kilo_farki * 7700) / 300
        tahmini_hafta = tahmini_gun / 7

        st.success(
            "Hedefleriniz başarıyla hesaplandı, kaydedildi ve ilk kurulum"
            " tamamlandı!"
        )
        st.markdown("---")
        st.subheader("📊 Analiz ve Tahmin Sonuçları")
        st.metric("Mevcut Kilo", f"{mevcut_kilo} kg")
        st.metric("Hedef Kilo", f"{hedef_kilo} kg")
        st.metric("Kilo Farkı", f"+{abs(kilo_farki):.1f} kg (Alınması Gereken)")
        st.metric(
            "Günlük Harcanan Toplam Enerji (TDEE)", f"{round(tdee)} kcal"
        )
        st.metric("Önerilen Günlük Kalori Alımı", f"{round(hedef_kalori)} kcal")
        st.markdown(
            "💡 **Kalori Fazlası:** Kilo alabilmek için günlük harcamanızın"
            " üzerinde, günde yaklaşık **300 kcal fazlalık** oluşturmalısınız."
        )
        st.markdown(
            f"⏱️ **Tahmini Süre:** Bu hedefe **yaklaşık {tahmini_hafta:.1f}"
            f" haftada (yaklaşık {round(tahmini_gun)} günde)** ulaşabilirsiniz."
        )
      else:
        st.session_state.profil["hedef_kalori"] = round(tdee)
        st.session_state.profil["setup_tamamlandi"] = True
        st.success(
            "Mevcut kilonuz ve hedef kilonuz aynı! Kilonuzu korumak için"
            " günlük kalori hedefiniz TDEE ile aynı ayarlandı."
        )

      st.session_state.profil["hedef_protein"] = round(
          (st.session_state.profil["hedef_kalori"] * 0.20) / 4
      )
      st.session_state.profil["hedef_karb"] = round(
          (st.session_state.profil["hedef_kalori"] * 0.50) / 4
      )
      st.session_state.profil["hedef_yag"] = round(
          (st.session_state.profil["hedef_kalori"] * 0.30) / 9
      )
      verileri_kaydet(aktif_user)
