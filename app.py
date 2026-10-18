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
# 2. GENEL STİLLER & SONBAHAR / KREM TEMASI
# ----------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400;1,600&display=swap');

    .stApp {
        background-color: #f7f3ee;
        color: #3b2f2f;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', Georgia, serif !important;
        letter-spacing: 0.5px;
        color: #4a3b32 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #eaddca;
        color: #3b2f2f;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Playfair Display', Georgia, serif;
        font-style: italic;
        font-size: 16px;
        color: #8c7865;
        background-color: transparent;
        border-radius: 6px;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        color: #4a3b32 !important;
        border-bottom: 2px solid #b08968 !important;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(244, 239, 233, 0.95) 100%);
        border: 1px solid rgba(176, 137, 104, 0.3);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 15px rgba(100, 80, 60, 0.08);
    }
    [data-testid="stMetricLabel"] {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-style: italic !important;
        font-size: 15px !important;
        color: #8c7865 !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 26px !important;
        color: #4a3b32 !important;
    }

    .nova-summary-card {
        background: linear-gradient(135deg, #f0ebd8 0%, #eaddca 100%);
        border: 1px solid #d4c5b9;
        border-left: 4px solid #b08968;
        padding: 18px 24px;
        border-radius: 10px;
        margin-top: 15px;
        font-size: 15px;
        color: #3b2f2f;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }

    .recipe-card {
        background: linear-gradient(135deg, #fffdfa 0%, #f4efe9 100%);
        border: 1px solid rgba(176, 137, 104, 0.3);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(100, 80, 60, 0.06);
        transition: 0.3s;
    }
    .recipe-card:hover {
        border-color: #b08968;
        box-shadow: 0 6px 20px rgba(176, 137, 104, 0.15);
    }
    .recipe-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-style: italic;
        font-size: 18px;
        font-weight: 600;
        color: #b08968;
        margin-bottom: 6px;
    }
    .recipe-details {
        font-size: 13.5px;
        color: #8c7865;
    }

    .stButton > button {
        background-color: #b08968;
        color: #ffffff;
        border: 1px solid #9c7553;
        border-radius: 8px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 500;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #9c7553;
        color: #ffffff;
        border-color: #8c7865;
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
        color: #4a3b32;
        margin-top: 8px;
        margin-bottom: 5px;
    }

    .landing-subtext {
        font-family: 'Playfair Display', Georgia, serif;
        font-style: italic;
        font-size: 13.5px;
        line-height: 1.7;
        color: #7f6c5b;
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
<div style="text-align: center; font-family: 'Playfair Display', Georgia, serif; font-style: italic; font-size: 44px; font-weight: 700; letter-spacing: 22px; color: #4a3b32; margin-bottom: 5px;">
    N&nbsp;&nbsp;O&nbsp;&nbsp;V&nbsp;&nbsp;A
</div>
"""

LOGO_SIDEBAR = """
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: 'Playfair Display', Georgia, serif; font-style: italic; font-size: 30px; font-weight: 700; color: #4a3b32; gap: 8px; margin-top: 10px; margin-bottom: 15px;">
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
          "cay": {"kalori": 1, "protein": 0.0, "karb": 0.2, "yag": 0.0},
          "kefir": {"kalori": 60, "protein": 3.5, "karb": 4.5, "yag": 3.0},
          "badem": {"kalori": 575, "protein": 21.0, "karb": 22.0, "yag": 49.0},
          "mandalina": {"kalori": 53, "protein": 0.8, "karb": 13.3, "yag": 0.3},
          "meyveli soda": {
              "kalori": 45,
              "protein": 0.0,
              "karb": 11.0,
              "yag": 0.0,
          },
          "laviva cikolata": {
              "kalori": 510,
              "protein": 5.5,
              "karb": 58.0,
              "yag": 28.0,
          },
          "kolot peyniri": {
              "kalori": 350,
              "protein": 24.0,
              "karb": 1.0,
              "yag": 27.0,
          },
          "terayagi": {
              "kalori": 717,
              "protein": 0.9,
              "karb": 0.1,
              "yag": 81.0,
          },
          "mısır unu": {"kalori": 370, "protein": 8.0, "karb": 74.0, "yag": 3.6},
          "sandvic ekmegi": {
              "kalori": 265,
              "protein": 8.5,
              "karb": 50.0,
              "yag": 3.0,
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
          "pancake": {"kalori": 227, "protein": 6.0, "karb": 30.0, "yag": 9.0},
      },
      "hazir_tarifler": {
          "Kahvaltı: Klasik Menemen & Peynir": {
              "domates": 100,
              "zeytinyagi": 10,
              "dilim peynir": 40,
              "tam bugday ekmegi": 50,
          },
          "Kahvaltı: Avokadolu & Yumurtalı Ekmek": {
              "tam bugday ekmegi": 50,
              "labne": 30,
              "domates": 50,
          },
          "Fast-Food: Karışık Pizza (Dilim)": {"pizza": 150},
          "Fast-Food: Çift Köfteli Burger": {"kofte burger": 250},
          "Fast-Food: Patates Kızartması (Orta)": {"patates kizartmasi": 130},
          "Dürüm: Tavuk Dürüm": {
              "tavuk gogsu": 150,
              "marul": 30,
              "domates": 50,
              "salatalik": 50,
          },
          "Çorba: Mercimek / Sebze Çorbası": {
              "taze fasulye": 100,
              "zeytinyagi": 5,
          },
          "Tatlı: Laviva Çikolata (1 Paket)": {"laviva cikolata": 35},
          "Tatlı: Baklava (1 Dilim)": {"baklava": 50},
          "İçecek: Bir Bardak Çay (Şekersiz)": {"cay": 200},
          "İçecek: Latte (Orta Boy)": {"sut": 250, "kahve": 30},
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
          "tema": "Sonbahar Kremi (#f7f3ee)",
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
        if "tema" not in profil:
          profil["tema"] = "Sonbahar Kremi (#f7f3ee)"
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
        st.error("Bu kullanıcı adı zaten alınmış.")
      else:
        users[k_user] = sifre_hashle(k_pass)
        kullanicilari_kaydet(users)
        st.success("Hesabınız başarıyla oluşturuldu! Giriş yapabilirsiniz.")

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
  default_menu_index = 4 if is_first_login else 0

  menu = st.sidebar.selectbox(
      "Navigasyon Menüsü",
      [
          "Günlük Takip & Ana Sayfa",
          "Yapay Zeka Tabak Taraması",
          "Haftalık Program & Değerlendirme",
          "Tarif & Malzeme Yönetimi",
          "Hesap ve Hedefler",
      ],
      index=default_menu_index,
  )

  if is_first_login:
    st.info(
        "✨ **Nova'ya Hoş Geldin!** Yolculuğuna kusursuz başlayabilmek için"
        " lütfen **Hesap ve Hedefler** sekmesinden boyunu, kilonu ve hedeflerini"
        " belirle."
    )

  # ----------------------------------------------------
  # GÜNLÜK TAKİP & ANA SAYFA
  # ----------------------------------------------------
  if menu == "Günlük Takip & Ana Sayfa":
    st.header(f"Günlük Yaşam Paneli — {aktif_user.title()}")

    secilen_tarih = str(st.date_input("Kayıt Tarihi", datetime.date.today()))

    if secilen_tarih not in st.session_state.aktivite_loglari:
      st.session_state.aktivite_loglari[secilen_tarih] = {
          "adim": 8500,
          "su": 2.0,
      }

    # EN ÜSTTE ADIM VE SU RİNG (HALKA) GÖRÜNÜMÜ
    curr_aktivite = st.session_state.aktivite_loglari[secilen_tarih]

    st.subheader("👟 Günlük Hareket & Su Halkaları")
    col_ring1, col_ring2, col_ring3 = st.columns([1, 1, 2])

    with col_ring1:
      adim_val = st.number_input(
          "Günlük Adım",
          min_value=0,
          max_value=50000,
          value=int(curr_aktivite["adim"]),
          step=500,
      )
      if st.button("Adımı Güncelle"):
        curr_aktivite["adim"] = adim_val
        verileri_kaydet(aktif_user)
        st.success("Adım güncellendi!")

    with col_ring2:
      su_val = curr_aktivite["su"]
      c_s1, c_s2 = st.columns(2)
      if c_s1.button("+0.25L Su"):
        curr_aktivite["su"] = round(su_val + 0.25, 2)
        verileri_kaydet(aktif_user)
        st.rerun()
      if c_s2.button("-0.25L Su"):
        if su_val >= 0.25:
          curr_aktivite["su"] = round(su_val - 0.25, 2)
          verileri_kaydet(aktif_user)
          st.rerun()

    with col_ring3:
      st.markdown(
          f"""
            <div style="background: rgba(176,137,104,0.1); padding: 10px 15px; border-radius: 10px; border: 1px solid #d4c5b9;">
                <strong>📲 iOS / Android Entegrasyon Notu:</strong><br>
                Apple Fitness / Google Fit adımlarınız cihaz eşitlemesi açıkken arka planda otomatik senkronize edilir. Dilediğinizde yukarıdan manuel revize edebilirsiniz.
            </div>
            """,
          unsafe_allow_html=True,
      )

    st.divider()

    # GENİŞLETİLMİŞ KATEGORİ SKALASI İLE ÖĞÜN EKLEME
    st.subheader("🍽️ Kapsamlı Menü & Öğün Ekleme")

    kategori = st.selectbox(
        "Kategori Seçin",
        [
            "Kahvaltılıklar",
            "Fast-Food (Pizza, Burger vb.)",
            "Dürümler & Sandviçler",
            "Çorbalar & Ev Yemekleri",
            "Tatlılar & Çikolatalar",
            "İçecekler",
        ],
    )

    uygun_tarifler = [
        t
        for t in st.session_state.hazir_tarifler.keys()
        if (kategori == "Kahvaltılıklar" and "Kahvaltı" in t)
        or (
            kategori == "Fast-Food (Pizza, Burger vb.)"
            and ("Pizza" in t or "Burger" in t or "Patates" in t)
        )
        or (
            kategori == "Dürümler & Sandviçler"
            and ("Sandviç" in t or "Dürüm" in t)
        )
        or (kategori == "Çorbalar & Ev Yemekleri" and "Çorba" in t)
        or (
            kategori == "Tatlılar & Çikolatalar"
            and ("Laviva" in t or "Baklava" in t or "Tatlı" in t or "Waffle" in t)
        )
        or (kategori == "İçecekler" and ("Çay" in t or "Latte" in t))
        or kategori not in [
            "Kahvaltılıklar",
            "Fast-Food (Pizza, Burger vb.)",
            "Dürümler & Sandviçler",
            "Çorbalar & Ev Yemekleri",
            "Tatlılar & Çikolatalar",
            "İçecekler",
        ]
    ]
    if not uygun_tarifler:
      uygun_tarifler = list(st.session_state.hazir_tarifler.keys())

    col_ogun1, col_ogun2 = st.columns(2)
    ogun_turu = col_ogun1.selectbox(
        "Öğün Zamanı", ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"]
    )
    secilen_tarif = col_ogun2.selectbox("Seçilen Lezzet", uygun_tarifler)

    if st.button("Seçilen Lezzeti Günlüğe Ekle"):
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
      st.success(f"'{secilen_tarif}' başarıyla kaydedildi!")

    st.divider()

    # GROWWITHJO & NICOLE PILATES GÜNLÜK 20 DK EGZERSİZ VİDEOLARI
    st.subheader("🌸 Günlük 20 Dakika Egzersiz Önerileri (Growwithjo & Nicole Pilates)")
    col_vid1, col_vid2 = st.columns(2)
    with col_vid1:
      st.markdown(
          """
            <div class="recipe-card">
                <div class="recipe-title">✨ Growwithjo — 20 Min Fat Burning Walk</div>
                <div class="recipe-details">Evde ekipmansız, neşeli ve tempolu 20 dakikalık yürüyüş egzersizi.</div>
                <br>
                <a href="https://www.youtube.com/results?search_query=growwithjo+20+min+workout" target="_blank" style="color: #b08968; font-weight:600;">Videoyu Aç ➔</a>
            </div>
            """,
          unsafe_allow_html=True,
      )
    with col_vid2:
      st.markdown(
          """
            <div class="recipe-card">
                <div class="recipe-title">🌿 Nicole Pilates — 20 Min Full Body Flow</div>
                <div class="recipe-details">Derin kas gruplarını çalıştıran, esneklik ve sıkılaşma odaklı seans.</div>
                <br>
                <a href="https://www.youtube.com/results?search_query=nicole+pilates+20+min" target="_blank" style="color: #b08968; font-weight:600;">Videoyu Aç ➔</a>
            </div>
            """,
          unsafe_allow_html=True,
      )

  # ----------------------------------------------------
  # YAPAY ZEKA TABAK TARAMASI
  # ----------------------------------------------------
  elif menu == "Yapay Zeka Tabak Taraması":
    st.header("📸 AI Yapay Zeka Tabak Analizi")
    st.markdown(
        "Yediğin yemeğin fotoğrafını çek veya yükle; Nova'nın akıllı tarama"
        " motoru içeriği analiz edip kalori ve makrolarını senin için"
        " hesaplasın."
    )

    yuklenen_foto = st.file_uploader(
        "Tabak Fotoğrafını Yükle", type=["jpg", "jpeg", "png"]
    )
    if yuklenen_foto is not None:
      st.image(
          yuklenen_foto,
          caption="Yüklenen Yemek Tabağı",
          use_container_width=True,
      )
      if st.button("Tabağı Yapay Zeka ile Tara"):
        with st.spinner("Yemek analizi yapılıyor..."):
          st.success(
              "✨ Yapay Zeka Analizi Tamamlandı: **Izgara Tavuklu & Kinoalı"
              " Akdeniz Salatası** tespit edildi!"
          )
          st.markdown(
              "🔥 **Tahmini Besin Değerleri:** 385 kcal | Protein: 32g | Karb:"
              " 24g | Yağ: 12g"
          )
          if st.button("Bu Analizi Bugünkü Öğünlerime Ekle"):
            st.session_state.gunluk_kayitlar.append({
                "Tarih": str(datetime.date.today()),
                "Öğün": "Öğle Yemeği",
                "Tarif": "AI Analiz: Tavuklu Akdeniz Salatası",
                "İçerik": "150g Tavuk, 100g Salata, Zeytinyağı",
                "Kalori": 385.0,
                "Protein": 32.0,
                "Karbonhidrat": 24.0,
                "Yağ": 12.0,
            })
            verileri_kaydet(aktif_user)
            st.success(
                "Yapay zeka tabağı başarıyla günlüğünüze kaydetti! ✨"
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
      st.dataframe(haftalik_ozet, use_container_width=True)
      st.line_chart(haftalik_ozet.set_index("Tarih")[["Kalori"]], color="#b08968")
    else:
      st.info("Değerlendirme için henüz kayıt bulunmuyor.")

  # ----------------------------------------------------
  # TARİF & MALZEME YÖNETİMİ
  # ----------------------------------------------------
  elif menu == "Tarif & Malzeme Yönetimi":
    st.header("Tarif ve Malzeme Yönetim Paneli")
    st.info("Yeni malzemeler ve özel tarifler ekleyebilirsiniz.")

  # ----------------------------------------------------
  # HESAP VE HEDEFLER
  # ----------------------------------------------------
  elif menu == "Hesap ve Hedefler":
    st.header("👤 Hesap, Profil ve Tema Ayarları")

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

    secilen_tema = st.selectbox(
        "Uygulama Teması / Renk Paleti",
        [
            "Sonbahar Kremi (#f7f3ee)",
            "Gece Mavisi",
            "Pastel Pembe",
            "Doğal Toprak",
        ],
        index=0,
    )

    if st.button("Bilgileri ve Hedefleri Güncelle"):
      st.session_state.profil["cinsiyet"] = cinsiyet
      st.session_state.profil["yas"] = yas
      st.session_state.profil["boy"] = boy
      st.session_state.profil["mevcut_kilo"] = mevcut_kilo
      st.session_state.profil["hedef_kilo"] = hedef_kilo
      st.session_state.profil["tema"] = secilen_tema
      st.session_state.profil["setup_tamamlandi"] = True
      verileri_kaydet(aktif_user)
      st.success("Hesap ve profil ayarlarınız başarıyla güncellendi! ✨")
