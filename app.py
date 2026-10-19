import datetime
import hashlib
import json
import os
import pandas as pd
import streamlit as st
import google.generativeai as genai
from PIL import Image

# ----------------------------------------------------
# 1. SAYFA KONFİGÜRASYONU & AMBLEM BAĞLANTISI
# ----------------------------------------------------
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
# 2. GELİŞMİŞ 5 FARKLI TEMA YÖNETİMİ VE CSS
# ----------------------------------------------------
def get_theme_styles(tema_adi):
    if "Gece" in tema_adi or "Mavi" in tema_adi:
        return {"bg": "#0b132b", "card_bg": "linear-gradient(135deg, rgba(28, 37, 65, 0.95) 0%, rgba(11, 19, 43, 0.95) 100%)", "text": "#e0e1dd", "heading": "#ffffff", "sidebar_bg": "#1c2541", "accent": "#48cae4", "border": "#3a506b", "ring_adim": "#48cae4", "ring_su": "#90e0ef"}
    elif "Kahve" in tema_adi or "Toprak" in tema_adi:
        return {"bg": "#eedecc", "card_bg": "linear-gradient(135deg, #f7f0ea 0%, #ecdcd0 100%)", "text": "#2c221e", "heading": "#3d2c23", "sidebar_bg": "#d6c2b0", "accent": "#7f5539", "border": "#b08968", "ring_adim": "#9c6644", "ring_su": "#b08968"}
    elif "Yeşil" in tema_adi or "Doğa" in tema_adi:
        return {"bg": "#edf2f4", "card_bg": "linear-gradient(135deg, #f4f7f6 0%, #e2e8e6 100%)", "text": "#2b3a32", "heading": "#1e2923", "sidebar_bg": "#d8e2dc", "accent": "#52796f", "border": "#84a98c", "ring_adim": "#52796f", "ring_su": "#354f52"}
    elif "Karamel" in tema_adi:
        return {"bg": "#fdf0ed", "card_bg": "linear-gradient(135deg, #fff7f5 0%, #fae1dd 100%)", "text": "#4a2e2b", "heading": "#361f1d", "sidebar_bg": "#f5cac3", "accent": "#e07a5f", "border": "#f2cc8f", "ring_adim": "#e07a5f", "ring_su": "#d4a373"}
    else:
        return {"bg": "#f7f3ee", "card_bg": "linear-gradient(135deg, #fffdfa 0%, #f4efe9 100%)", "text": "#3b2f2f", "heading": "#4a3b32", "sidebar_bg": "#eaddca", "accent": "#b08968", "border": "#d4c5b9", "ring_adim": "#b08968", "ring_su": "#9c7553"}

def load_user_theme(username):
    user_file = f"veriler_{username.lower().strip()}.json"
    if os.path.exists(user_file):
        try:
            with open(user_file, "r", encoding="utf-8") as f:
                d = json.load(f)
                return d.get("profil", {}).get("tema", "Sonbahar Kremi")
        except: pass
    return "Sonbahar Kremi"

aktif_kullanici_temp = st.session_state.get("aktif_kullanici", "")
secilen_tema_adi = load_user_theme(aktif_kullanici_temp) if aktif_kullanici_temp else "Sonbahar Kremi"
t = get_theme_styles(secilen_tema_adi)

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400;1,600&display=swap');
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; font-family: 'Plus Jakarta Sans', sans-serif; }}
    h1, h2, h3, h4, h5, h6 {{ font-family: 'Playfair Display', Georgia, serif !important; letter-spacing: 0.5px; color: {t['heading']} !important; }}
    p, span, label, div {{ color: {t['text']}; }}
    [data-testid="stSidebar"] {{ background-color: {t['sidebar_bg']}; color: {t['text']}; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 12px; }}
    .stTabs [data-baseweb="tab"] {{ font-family: 'Playfair Display', Georgia, serif; font-style: italic; font-size: 16px; color: {t['accent']}; background-color: transparent; border-radius: 6px; padding: 8px 16px; }}
    .stTabs [aria-selected="true"] {{ color: {t['heading']} !important; border-bottom: 2px solid {t['accent']} !important; font-weight: 600; }}
    .recipe-card {{ background: {t['card_bg']}; border: 1px solid {t['border']}; border-radius: 12px; padding: 16px 20px; margin-bottom: 14px; box-shadow: 0 4px 12px rgba(100, 80, 60, 0.06); }}
    .recipe-title {{ font-family: 'Playfair Display', Georgia, serif; font-style: italic; font-size: 18px; font-weight: 600; color: {t['accent']}; margin-bottom: 6px; }}
    .recipe-details {{ font-size: 13.5px; color: {t['text']}; opacity: 0.85; }}
    .stButton > button {{ background-color: {t['accent']}; color: #ffffff; border: 1px solid {t['border']}; border-radius: 8px; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 500; transition: 0.3s; }}
    .stButton > button:hover {{ opacity: 0.9; color: #ffffff; }}
    .sidebar-user-card {{ text-align: center; margin-top: 10px; margin-bottom: 15px; }}
    .sidebar-user-name {{ font-family: 'Playfair Display', Georgia, serif; font-style: italic; font-size: 18px; font-weight: 600; color: {t['heading']}; margin-top: 8px; margin-bottom: 5px; }}
    .landing-subtext {{ font-family: 'Playfair Display', Georgia, serif; font-style: italic; font-size: 13.5px; line-height: 1.7; color: {t['text']}; text-align: justify; font-weight: 400; margin-top: 12px; margin-bottom: 20px; letter-spacing: 0.2px; }}
    </style>
""", unsafe_allow_html=True)

LOGO_MAIN = f"""<div style="text-align: center; font-family: 'Playfair Display', Georgia, serif; font-style: italic; font-size: 44px; font-weight: 700; letter-spacing: 22px; color: {t['heading']}; margin-bottom: 5px;">N&nbsp;&nbsp;O&nbsp;&nbsp;V&nbsp;&nbsp;A</div>"""
LOGO_SIDEBAR = f"""<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: 'Playfair Display', Georgia, serif; font-style: italic; font-size: 30px; font-weight: 700; color: {t['heading']}; gap: 8px; margin-top: 10px; margin-bottom: 15px;"><span>N</span><span>O</span><span>V</span><span>A</span></div>"""
USERS_FILE = "kullanicilar.json"

# ----------------------------------------------------
# 3. KULLANICI YÖNETİMİ & VERİTABANI
# ----------------------------------------------------
def sifre_hashle(sifre): return hashlib.sha256(sifre.encode("utf-8")).hexdigest()

def kullanicilari_yukle():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def kullanicilari_kaydet(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f: json.dump(users, f, ensure_ascii=False, indent=4)

def kullanici_veri_dosyasi(username): return f"veriler_{username.lower().strip()}.json"

DEVASA_MENU = {
    "A. 🥐 Kahvaltılıklar ve Sabah Öğünü": {
        "Serpme Kahvaltı (Tek Kişilik)": {"kalori": 650, "protein": 24, "karb": 55, "yag": 36},
        "Serpme Kahvaltı (İki Kişilik)": {"kalori": 1300, "protein": 48, "karb": 110, "yag": 72},
        "Standart Kahvaltı Tabağı": {"kalori": 420, "protein": 18, "karb": 35, "yag": 22},
        "Zenginleştirilmiş Kahvaltı Tabağı": {"kalori": 580, "protein": 25, "karb": 48, "yag": 31},
        "Sade Menemen (Küçük Porsiyon)": {"kalori": 140, "protein": 7, "karb": 6, "yag": 10},
        "Sade Menemen (Orta Porsiyon)": {"kalori": 210, "protein": 11, "karb": 9, "yag": 15},
        "Sade Menemen (Büyük Porsiyon)": {"kalori": 310, "protein": 16, "karb": 13, "yag": 22},
        "Kaşarlı Menemen (Küçük Porsiyon)": {"kalori": 220, "protein": 12, "karb": 7, "yag": 16},
        "Kaşarlı Menemen (Orta Porsiyon)": {"kalori": 320, "protein": 18, "karb": 10, "yag": 23},
        "Kaşarlı Menemen (Büyük Porsiyon)": {"kalori": 450, "protein": 25, "karb": 14, "yag": 33},
        "Sucuklu Yumurta (Standart Porsiyon)": {"kalori": 380, "protein": 19, "karb": 3, "yag": 32},
        "Sucuklu Yumurta (Doyurucu Porsiyon)": {"kalori": 540, "protein": 27, "karb": 4, "yag": 46},
        "Peynirli Omlet (Standart Porsiyon)": {"kalori": 280, "protein": 17, "karb": 2, "yag": 22},
        "Kaşarlı Tost (Tek)": {"kalori": 290, "protein": 12, "karb": 30, "yag": 13},
        "Kaşarlı Tost (Duble)": {"kalori": 440, "protein": 20, "karb": 42, "yag": 21},
        "Karışık Tost (Tek)": {"kalori": 350, "protein": 15, "karb": 31, "yag": 18},
        "Karışık Tost (Duble)": {"kalori": 520, "protein": 24, "karb": 44, "yag": 28},
        "Avokadolu Tost (Standart Porsiyon)": {"kalori": 320, "protein": 9, "karb": 34, "yag": 17},
        "Beyaz Peynirli Sandviç (Standart)": {"kalori": 280, "protein": 13, "karb": 36, "yag": 9},
        "Sade Kruvasan": {"kalori": 270, "protein": 5, "karb": 31, "yag": 14},
        "Çikolatalı Kruvasan": {"kalori": 360, "protein": 6, "karb": 42, "yag": 19},
        "Pancake (3'lü Porsiyon)": {"kalori": 280, "protein": 7, "karb": 45, "yag": 8},
        "Pancake (5'li Porsiyon)": {"kalori": 460, "protein": 12, "karb": 75, "yag": 13},
        "Waffle Kahvaltı Tabağı (Standart)": {"kalori": 520, "protein": 10, "karb": 70, "yag": 22},
        "Granola ve Yoğurt Kasesi (Küçük Boy)": {"kalori": 220, "protein": 9, "karb": 32, "yag": 6},
        "Granola ve Yoğurt Kasesi (Büyük Boy)": {"kalori": 380, "protein": 15, "karb": 56, "yag": 11},
        "Meyveli Yulaf Lapası (Standart)": {"kalori": 260, "protein": 8, "karb": 46, "yag": 5},
        "Fransız Tostu (Standart)": {"kalori": 340, "protein": 10, "karb": 40, "yag": 15},
        "Simit ve Peynir Tabağı (Standart)": {"kalori": 410, "protein": 16, "karb": 52, "yag": 15},
        "Bagel Sandviç (Standart)": {"kalori": 350, "protein": 14, "karb": 48, "yag": 11},
        "Kahvaltılık Quesadilla (Standart)": {"kalori": 430, "protein": 19, "karb": 38, "yag": 22},
    },
    "B. 🥪 Öğle Yemeği ve Pratik Seçenekler": {
        "Mercimek Çorbası (Kase)": {"kalori": 160, "protein": 8, "karb": 22, "yag": 4.5},
        "Ezogelin Çorbası (Kase)": {"kalori": 170, "protein": 7, "karb": 24, "yag": 5},
        "Domates Çorbası (Kase)": {"kalori": 130, "protein": 3, "karb": 18, "yag": 5.5},
        "Kremalı Mantar Çorbası (Kase)": {"kalori": 210, "protein": 4, "karb": 16, "yag": 15},
        "Tavuk Suyu Çorbası (Kase)": {"kalori": 140, "protein": 10, "karb": 12, "yag": 5},
        "Yayla Çorbası (Kase)": {"kalori": 150, "protein": 5, "karb": 20, "yag": 5.5},
        "Brokoli Çorbası (Kase)": {"kalori": 120, "protein": 4, "karb": 14, "yag": 6},
        "Balkabağı Çorbası (Kase)": {"kalori": 110, "protein": 2, "karb": 20, "yag": 3},
        "Tarhana Çorbası (Kase)": {"kalori": 160, "protein": 6, "karb": 24, "yag": 4},
        "İşkembe Çorbası (Kase)": {"kalori": 220, "protein": 15, "karb": 8, "yag": 14},
        "Mevsim Salata (Standart Porsiyon)": {"kalori": 90, "protein": 2, "karb": 8, "yag": 6},
        "Çoban Salata (Standart Porsiyon)": {"kalori": 110, "protein": 2.5, "karb": 9, "yag": 7},
        "Akdeniz Salata (Standart Porsiyon)": {"kalori": 140, "protein": 4, "karb": 8, "yag": 10},
        "Sezar Salata (Standart Porsiyon)": {"kalori": 280, "protein": 10, "karb": 15, "yag": 20},
        "Tavuklu Sezar Salata (Standart Porsiyon)": {"kalori": 380, "protein": 32, "karb": 12, "yag": 22},
        "Ton Balıklı Salata (Standart Porsiyon)": {"kalori": 290, "protein": 28, "karb": 9, "yag": 15},
        "Hellim Peynirli Salata (Standart Porsiyon)": {"kalori": 360, "protein": 18, "karb": 11, "yag": 27},
        "Izgara Tavuklu Salata (Standart Porsiyon)": {"kalori": 310, "protein": 34, "karb": 10, "yag": 14},
        "Avokadolu Salata (Standart Porsiyon)": {"kalori": 240, "protein": 5, "karb": 12, "yag": 19},
        "Kinoa Salatası (Standart Porsiyon)": {"kalori": 220, "protein": 8, "karb": 32, "yag": 8},
        "Nohut Salatası (Standart Porsiyon)": {"kalori": 250, "protein": 12, "karb": 35, "yag": 7},
        "Kısır (Standart Porsiyon)": {"kalori": 270, "protein": 6, "karb": 45, "yag": 8},
        "Kaşarlı Sandviç (Standart)": {"kalori": 310, "protein": 14, "karb": 35, "yag": 12},
        "Karışık Sandviç (Standart)": {"kalori": 340, "protein": 16, "karb": 36, "yag": 15},
        "Beyaz Peynirli Sandviç (Standart)": {"kalori": 280, "protein": 13, "karb": 36, "yag": 9},
        "Hindi Fümeli Sandviç (Standart)": {"kalori": 290, "protein": 18, "karb": 34, "yag": 8},
        "Tavuklu Sandviç (Standart)": {"kalori": 380, "protein": 28, "karb": 38, "yag": 11},
        "Ton Balıklı Sandviç (Standart)": {"kalori": 360, "protein": 26, "karb": 36, "yag": 12},
        "Club Sandwich (Standart)": {"kalori": 540, "protein": 26, "karb": 45, "yag": 28},
        "Tavuklu Wrap (Standart)": {"kalori": 420, "protein": 30, "karb": 42, "yag": 14},
        "Çıtır Tavuk Wrap (Standart)": {"kalori": 530, "protein": 24, "karb": 52, "yag": 25},
        "Etli Wrap (Standart)": {"kalori": 490, "protein": 32, "karb": 44, "yag": 22},
        "Köfteli Wrap (Standart)": {"kalori": 460, "protein": 28, "karb": 40, "yag": 20},
        "Falafel Wrap (Standart)": {"kalori": 450, "protein": 14, "karb": 58, "yag": 18},
        "Acai Bowl (Küçük Boy)": {"kalori": 210, "protein": 4, "karb": 38, "yag": 5},
        "Acai Bowl (Büyük Boy)": {"kalori": 360, "protein": 7, "karb": 64, "yag": 9},
        "Protein Bowl (Küçük Boy)": {"kalori": 310, "protein": 26, "karb": 30, "yag": 9},
        "Protein Bowl (Büyük Boy)": {"kalori": 490, "protein": 42, "karb": 48, "yag": 15},
        "Somonlu Bowl (Standart)": {"kalori": 460, "protein": 31, "karb": 40, "yag": 18},
    },
    "C. 🍽️ Akşam Yemeği ve Ana Yemekler": {
        "Izgara Tavuk (Standart Porsiyon)": {"kalori": 280, "protein": 42, "karb": 0, "yag": 12},
        "Tavuk Şinitzel (Standart Porsiyon)": {"kalori": 420, "protein": 32, "karb": 24, "yag": 22},
        "Tavuk Sote (Standart Porsiyon)": {"kalori": 310, "protein": 38, "karb": 8, "yag": 14},
        "Kremalı Mantarlı Tavuk (Standart Porsiyon)": {"kalori": 450, "protein": 35, "karb": 12, "yag": 28},
        "Izgara Köfte (Standart Porsiyon)": {"kalori": 360, "protein": 28, "karb": 6, "yag": 24},
        "Et Sote (Standart Porsiyon)": {"kalori": 380, "protein": 34, "karb": 10, "yag": 22},
        "Dana Antrikot (Standart Porsiyon)": {"kalori": 450, "protein": 38, "karb": 0, "yag": 32},
        "Bonfile (Standart Porsiyon)": {"kalori": 400, "protein": 42, "karb": 0, "yag": 24},
        "Izgara Somon (Standart Porsiyon)": {"kalori": 380, "protein": 34, "karb": 0, "yag": 26},
        "Fırında Levrek (Standart Porsiyon)": {"kalori": 260, "protein": 30, "karb": 2, "yag": 14},
        "Tavuklu Noodle (Standart Porsiyon)": {"kalori": 420, "protein": 26, "karb": 48, "yag": 14},
        "Mantı (Standart Porsiyon)": {"kalori": 480, "protein": 18, "karb": 62, "yag": 18},
        "İskender Kebap (Standart Porsiyon)": {"kalori": 720, "protein": 36, "karb": 54, "yag": 38},
        "Adana Kebap (Standart Porsiyon)": {"kalori": 550, "protein": 32, "karb": 28, "yag": 35},
        "Urfa Kebap (Standart Porsiyon)": {"kalori": 530, "protein": 32, "karb": 28, "yag": 32},
        "Tavuk Şiş (Standart Porsiyon)": {"kalori": 320, "protein": 38, "karb": 6, "yag": 16},
        "Lahmacun (Tek)": {"kalori": 220, "protein": 9.5, "karb": 28, "yag": 7.5},
        "Lahmacun (Duble)": {"kalori": 440, "protein": 19, "karb": 56, "yag": 15},
        "Pide (Kaşarlı Pide - Standart)": {"kalori": 450, "protein": 18, "karb": 50, "yag": 20},
        "İçli Köfte (2 Adet)": {"kalori": 320, "protein": 12, "karb": 30, "yag": 16},
        "Kuru Fasulye ve Pilav (Standart Porsiyon)": {"kalori": 480, "protein": 16, "karb": 65, "yag": 14},
        "Sade Pirinç Pilavı (Küçük Porsiyon)": {"kalori": 130, "protein": 2, "karb": 28, "yag": 1.5},
        "Sade Pirinç Pilavı (Orta Porsiyon)": {"kalori": 210, "protein": 3.5, "karb": 44, "yag": 2.5},
        "Sade Pirinç Pilavı (Büyük Porsiyon)": {"kalori": 320, "protein": 5, "karb": 68, "yag": 4},
        "Bulgur Pilavı (Küçük Porsiyon)": {"kalori": 110, "protein": 3.5, "karb": 22, "yag": 1.2},
        "Bulgur Pilavı (Orta Porsiyon)": {"kalori": 170, "protein": 5.5, "karb": 34, "yag": 2},
        "Bulgur Pilavı (Büyük Porsiyon)": {"kalori": 260, "protein": 8.5, "karb": 52, "yag": 3},
        "Su Böreği (1 Dilim)": {"kalori": 310, "protein": 11, "karb": 32, "yag": 16},
        "Kıymalı Börek (1 Dilim)": {"kalori": 290, "protein": 9, "karb": 31, "yag": 14},
        "Sade Gözleme": {"kalori": 250, "protein": 8, "karb": 42, "yag": 6},
        "Kıymalı Gözleme": {"kalori": 380, "protein": 16, "karb": 44, "yag": 15},
        "Kıymalı Fırın Makarna (Standart Porsiyon)": {"kalori": 450, "protein": 22, "karb": 52, "yag": 18},
        "Zeytinyağlı Yaprak Sarma (Standart Porsiyon)": {"kalori": 240, "protein": 4, "karb": 36, "yag": 9.5},
        "Zeytinyağlı Enginar (Standart Porsiyon)": {"kalori": 160, "protein": 3, "karb": 18, "yag": 9},
        "Zeytinyağlı Taze Fasulye (Standart Porsiyon)": {"kalori": 140, "protein": 4, "karb": 16, "yag": 7},
        "Margherita Pizza (Küçük Boy / 22cm)": {"kalori": 480, "protein": 18, "karb": 62, "yag": 17},
        "Margherita Pizza (Orta Boy / 28cm)": {"kalori": 760, "protein": 29, "karb": 98, "yag": 27},
        "Margherita Pizza (Büyük Boy / 34cm)": {"kalori": 1120, "protein": 42, "karb": 144, "yag": 40},
        "Klasik Hamburger (Tek Porsiyon / Menü Seçenekli)": {"kalori": 390, "protein": 20, "karb": 38, "yag": 18},
        "Cheeseburger (Tek Porsiyon / Menü Seçenekli)": {"kalori": 450, "protein": 24, "karb": 39, "yag": 22},
        "Double Cheeseburger (Standart)": {"kalori": 640, "protein": 38, "karb": 41, "yag": 36},
    },
    "D. 🌯 Sokak Lezzetleri ve Fast Food": {
        "Islak Hamburger (Tek)": {"kalori": 260, "protein": 11, "karb": 28, "yag": 12},
        "Kumpir (Standart)": {"kalori": 680, "protein": 16, "karb": 82, "yag": 32},
        "Kokoreç (Yarım Ekmek)": {"kalori": 420, "protein": 22, "karb": 38, "yag": 20},
        "Kokoreç (Tam Ekmek)": {"kalori": 780, "protein": 41, "karb": 72, "yag": 36},
        "Midye Dolma (5 Adet)": {"kalori": 150, "protein": 7, "karb": 22, "yag": 4},
        "Midye Dolma (10 Adet)": {"kalori": 300, "protein": 14, "karb": 44, "yag": 8},
        "Tantuni (Et - Dürüm)": {"kalori": 440, "protein": 26, "karb": 40, "yag": 20},
        "Tantuni (Tavuk - Dürüm)": {"kalori": 380, "protein": 28, "karb": 38, "yag": 14},
        "Patates Kızartması (Küçük Boy)": {"kalori": 220, "protein": 2.5, "karb": 29, "yag": 11},
        "Patates Kızartması (Orta Boy)": {"kalori": 330, "protein": 3.8, "karb": 43, "yag": 16},
        "Patates Kızartması (Büyük Boy)": {"kalori": 470, "protein": 5.2, "karb": 61, "yag": 23},
        "Soğan Halkası (6 Adet)": {"kalori": 190, "protein": 2.5, "karb": 24, "yag": 9.5},
        "Çıtır Tavuk Parçaları (6'lı Porsiyon)": {"kalori": 310, "protein": 18, "karb": 22, "yag": 16},
        "Tavuk Nugget (6'lı Porsiyon)": {"kalori": 280, "protein": 14, "karb": 18, "yag": 16},
        "Sigara Böreği (5 Adet)": {"kalori": 300, "protein": 8, "karb": 32, "yag": 15},
    },
    "E. 🍰 Tatlılar, Pastane Ürünleri ve Dondurmalar": {
        "San Sebastian Cheesecake (1 Dilim)": {"kalori": 460, "protein": 8, "karb": 34, "yag": 32},
        "Çikolatalı Sufle (Standart)": {"kalori": 390, "protein": 6, "karb": 48, "yag": 19},
        "Brownie (1 Dilim)": {"kalori": 340, "protein": 4, "karb": 45, "yag": 16},
        "Profiterol (Standart Porsiyon)": {"kalori": 340, "protein": 5, "karb": 42, "yag": 17},
        "Magnolia (Küçük Boy)": {"kalori": 220, "protein": 4, "karb": 32, "yag": 9},
        "Magnolia (Büyük Boy)": {"kalori": 380, "protein": 7, "karb": 56, "yag": 15},
        "Waffle (Standart)": {"kalori": 540, "protein": 9, "karb": 72, "yag": 24},
        "Karamelli Trileçe (1 Dilim)": {"kalori": 310, "protein": 6, "karb": 44, "yag": 12},
        "Fırın Sütlaç (Standart)": {"kalori": 240, "protein": 6, "karb": 41, "yag": 5.5},
        "Baklava (2 Dilim / 4 Dilim)": {"kalori": 330, "protein": 4, "karb": 42, "yag": 16},
        "Künefe (Standart)": {"kalori": 420, "protein": 8, "karb": 55, "yag": 20},
        "Sade Poğaça": {"kalori": 240, "protein": 5, "karb": 26, "yag": 12},
        "Peynirli Poğaça": {"kalori": 260, "protein": 7, "karb": 28, "yag": 13},
        "Açma (Sade / Zeytinli)": {"kalori": 310, "protein": 6, "karb": 38, "yag": 15},
        "Vanilyalı Dondurma (Tek / Çift Top)": {"kalori": 160, "protein": 3, "karb": 20, "yag": 7.6},
        "Çikolatalı Dondurma (Tek / Çift Top)": {"kalori": 180, "protein": 3.6, "karb": 22, "yag": 8.4},
    },
    "F. 🧋 Soğuk İçecekler, Sıcak İçecekler ve Soslar": {
        "Su (500ml Şişe)": {"kalori": 0, "protein": 0, "karb": 0, "yag": 0},
        "Ayran (Küçük Boy / Bardak)": {"kalori": 75, "protein": 4, "karb": 5, "yag": 4},
        "Ayran (Büyük Boy / Yayık)": {"kalori": 130, "protein": 7, "karb": 9, "yag": 7},
        "Limonata (Orta Boy)": {"kalori": 140, "protein": 0.3, "karb": 35, "yag": 0},
        "Kola (Küçük Boy / 330ml Kutu)": {"kalori": 139, "protein": 0, "karb": 35, "yag": 0},
        "Kola (Orta Boy / 500ml)": {"kalori": 210, "protein": 0, "karb": 53, "yag": 0},
        "Şekersiz Kola (Küçük, Orta, Büyük)": {"kalori": 1, "protein": 0, "karb": 0, "yag": 0},
        "Iced Latte (Orta Boy)": {"kalori": 120, "protein": 6, "karb": 12, "yag": 4.8},
        "Türk Kahvesi (Tek)": {"kalori": 7, "protein": 0.3, "karb": 0.9, "yag": 0.2},
        "Filtre Kahve (Küçük, Orta, Büyük)": {"kalori": 5, "protein": 0.1, "karb": 0.5, "yag": 0},
        "Siyah Çay (Bardak / Fincan)": {"kalori": 2, "protein": 0, "karb": 0.4, "yag": 0},
        "Ketçap (Paket / Sosluk)": {"kalori": 20, "protein": 0.2, "karb": 4.8, "yag": 0},
        "Mayonez (Paket / Sosluk)": {"kalori": 90, "protein": 0.1, "karb": 0.5, "yag": 10},
        "Barbekü Sos (Sosluk)": {"kalori": 35, "protein": 0.2, "karb": 8, "yag": 0.1},
        "Cheddar Sos (Sosluk)": {"kalori": 80, "protein": 3, "karb": 2, "yag": 7},
    }
}

def verileri_yukle(username):
    user_file = kullanici_veri_dosyasi(username)
    default_data = {
        "besin_veritabani": {}, "hazir_tarifler": {}, "gunluk_kayitlar": [], "aktivite_loglari": {},
        "profil": {"cinsiyet": "Kadın", "yas": 20, "boy": 165, "mevcut_kilo": 58.0, "hedef_kilo": 55.0, "verilmek_istenen_kilo": 3.0, "hedef_gun": 45, "egzersiz_katsayisi": 1.0, "tema": "Sonbahar Kremi", "gemini_api_key": "", "setup_tamamlandi": False}
    }

    if os.path.exists(user_file):
        try:
            with open(user_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                profil = data.get("profil", {})
                if "egzersiz_katsayisi" not in profil: profil["egzersiz_katsayisi"] = 1.0
                if "gemini_api_key" not in profil: profil["gemini_api_key"] = ""
                if "tema" not in profil: profil["tema"] = "Sonbahar Kremi"
                if "setup_tamamlandi" not in profil: profil["setup_tamamlandi"] = True
                data["profil"] = profil
                return data
        except: return default_data
    return default_data

def verileri_kaydet(username):
    data = {"besin_veritabani": st.session_state.besin_veritabani, "hazir_tarifler": st.session_state.hazir_tarifler, "gunluk_kayitlar": st.session_state.gunluk_kayitlar, "aktivite_loglari": st.session_state.aktivite_loglari, "profil": st.session_state.profil}
    with open(kullanici_veri_dosyasi(username), "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

def hesapla_bmr(p):
    if p["cinsiyet"] == "Kadın": return (10 * float(p["mevcut_kilo"])) + (6.25 * float(p["boy"])) - (5 * int(p["yas"])) - 161
    else: return (10 * float(p["mevcut_kilo"])) + (6.25 * float(p["boy"])) - (5 * int(p["yas"])) + 5

# ----------------------------------------------------
# 4. OTURUM KONTROLÜ VE GİRİŞ EKRANI
# ----------------------------------------------------
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "aktif_kullanici" not in st.session_state: st.session_state.aktif_kullanici = ""

if not st.session_state.giris_yapildi:
    st.markdown(f'<div style="max-width: 760px; margin: 20px auto 0 auto; padding: 0px 15px;">{LOGO_MAIN}<p class="landing-subtext">Gökyüzünün derinliklerinde aniden parlayan bir yıldız gibidir dönüşüm... Karanlık suları aşan bir kuğunun asil zarafeti, pırlanta gibi parlayan yeni bir yaşam iradesiyle buluşur. Nova; kendi potansiyeline uyanmak, bedenine hak ettiği değeri vermek ve her gün biraz daha parlayarak kendi en büyüleyici versiyonunu baştan yaratmak isteyenlerin sığınağıdır. Işıltınla parlamaya hazır mısın?</p></div>', unsafe_allow_html=True)
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
                st.session_state.update(verileri_yukle(g_user))
                st.success(f"Hoş geldin, {g_user.title()}!")
                st.rerun()
            else: st.error("Kullanıcı adı veya şifre hatalı!")

    with tab_kayit:
        st.subheader("Yeni Nova Hesabı Oluştur")
        k_user = st.text_input("Yeni Kullanıcı Adı", key="k_user").strip().lower()
        k_pass = st.text_input("Şifre Oluştur", type="password", key="k_pass")
        k_pass_repeat = st.text_input("Şifreyi Tekrar Girin", type="password", key="k_pass_rep")

        if st.button("Kayıt Ol", key="btn_kayit"):
            if not k_user or not k_pass: st.warning("Lütfen kullanıcı adı ve şifre belirleyin.")
            elif k_pass != k_pass_repeat: st.error("Şifreler birbiriyle eşleşmiyor.")
            elif k_user in users: st.error("Bu kullanıcı adı zaten alınmış.")
            else:
                users[k_user] = sifre_hashle(k_pass)
                kullanicilari_kaydet(users)
                st.success("Hesabınız başarıyla oluşturuldu! Giriş yapabilirsiniz.")

else:
    # ----------------------------------------------------
    # 5. ANA UYGULAMA PANELİ
    # ----------------------------------------------------
    aktif_user = st.session_state.aktif_kullanici
    st.sidebar.markdown(LOGO_SIDEBAR, unsafe_allow_html=True)
    st.sidebar.markdown(f"<div class='sidebar-user-card'><div class='sidebar-user-name'>{aktif_user.title()}</div></div>", unsafe_allow_html=True)

    if st.sidebar.button("Çıkış Yap", use_container_width=True):
        st.session_state.giris_yapildi = False
        st.session_state.aktif_kullanici = ""
        st.rerun()
    st.sidebar.divider()

    is_first_login = not st.session_state.profil.get("setup_tamamlandi", True)
    menu = st.sidebar.selectbox("Navigasyon Menüsü", [
        "Günlük Takip & Ana Sayfa", "Haftalık Program & Değerlendirme", "Tarif & Malzeme Yönetimi", "Hesap ve Hedefler",
    ], index=3 if is_first_login else 0)

    if is_first_login: st.info("✨ **Nova'ya Hoş Geldin!** Yolculuğuna kusursuz başlayabilmek için lütfen **Hesap ve Hedefler** sekmesinden API anahtarını, tema rengini ve hedeflerini tamamla.")

    p = st.session_state.profil
    bmr_kisi = hesapla_bmr(p)

    # =====================================================================
    # 5.1 GÜNLÜK TAKİP & ANA SAYFA
    # =====================================================================
    if menu == "Günlük Takip & Ana Sayfa":
        st.header(f"Günlük Yaşam Paneli — {aktif_user.title()}")

        secilen_tarih = str(st.date_input("Kayıt Tarihi (Geçmişe Gidebilirsiniz)", datetime.date.today()))
        if secilen_tarih not in st.session_state.aktivite_loglari:
            st.session_state.aktivite_loglari[secilen_tarih] = {"adim": 0, "su": 0.0, "video_tamamlandi": False, "manuel_egzersiz_kcal": 0}
        curr_aktivite = st.session_state.aktivite_loglari[secilen_tarih]

        # SU VE ADIM HALKALARI
        st.subheader(f"🍂 {secilen_tarih} Tarihli Su ve Adım Takibi")
        col_ring_sol, col_ring_sag = st.columns(2)
        with col_ring_sol:
            adim_oran, adim_circ = min(1.0, curr_aktivite["adim"] / 10000), 2 * 3.14159 * 42
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.03); padding: 15px; border-radius: 16px; border: 1px solid {t['border']};">
                    <div style="position: relative; width: 110px; height: 110px;">
                        <svg width="110" height="110" style="transform: rotate(-90deg);"><circle cx="55" cy="55" r="42" stroke="rgba(0,0,0,0.1)" stroke-width="10" fill="transparent"/><circle cx="55" cy="55" r="42" stroke="{t['ring_adim']}" stroke-width="10" stroke-dasharray="{adim_circ}" stroke-dashoffset="{adim_circ * (1 - adim_oran)}" stroke-linecap="round" fill="transparent"/></svg>
                        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;"><span style="font-size: 16px; font-weight: 700; color: {t['heading']};">{curr_aktivite['adim']}</span><span style="font-size: 10px; color: {t['ring_adim']}; font-weight: 700;">ADIM RİNGİ</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            yeni_adim = st.number_input("Adım Güncelle", min_value=0, max_value=50000, value=int(curr_aktivite["adim"]), step=500, label_visibility="collapsed")
            if st.button("Adımı Kaydet"):
                curr_aktivite["adim"] = yeni_adim
                verileri_kaydet(aktif_user)
                st.rerun()

        with col_ring_sag:
            su_oran, su_circ = min(1.0, curr_aktivite["su"] / 3.0), 2 * 3.14159 * 42
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.03); padding: 15px; border-radius: 16px; border: 1px solid {t['border']};">
                    <div style="position: relative; width: 110px; height: 110px;">
                        <svg width="110" height="110" style="transform: rotate(-90deg);"><circle cx="55" cy="55" r="42" stroke="rgba(0,0,0,0.1)" stroke-width="10" fill="transparent"/><circle cx="55" cy="55" r="42" stroke="{t['ring_su']}" stroke-width="10" stroke-dasharray="{su_circ}" stroke-dashoffset="{su_circ * (1 - su_oran)}" stroke-linecap="round" fill="transparent"/></svg>
                        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;"><span style="font-size: 16px; font-weight: 700; color: {t['heading']};">{curr_aktivite['su']:.2f}L</span><span style="font-size: 10px; color: {t['ring_su']}; font-weight: 700;">SU RİNGİ</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            sc1, sc2 = st.columns(2)
            if sc1.button("+0.25L Su"):
                curr_aktivite["su"] = round(curr_aktivite["su"] + 0.25, 2)
                verileri_kaydet(aktif_user)
                st.rerun()
            if sc2.button("-0.25L Su") and curr_aktivite["su"] >= 0.25:
                curr_aktivite["su"] = round(curr_aktivite["su"] - 0.25, 2)
                verileri_kaydet(aktif_user)
                st.rerun()
        st.divider()

        # EGZERSİZ VE MANUEL SPOR
        st.subheader(f"📅 {secilen_tarih} Tarihine Özel Günlük Egzersiz")
        hash_gun = int(hashlib.md5(secilen_tarih.encode("utf-8")).hexdigest(), 16) % 3
        if hash_gun == 0: egzersiz_adi, egzersiz_link = "Growwithjo — 20 Min Fat Burning Walk", "https://www.youtube.com/results?search_query=growwithjo+20+min+workout"
        elif hash_gun == 1: egzersiz_adi, egzersiz_link = "Nicole Pilates — 20 Min Full Body Flow", "https://www.youtube.com/results?search_query=nicole+pilates+20+min"
        else: egzersiz_adi, egzersiz_link = "Growwithjo — 20 Min Low Impact Cardio", "https://www.youtube.com/results?search_query=growwithjo+low+impact"

        tahmini_video_kalorisi = round((5.5 * 3.5 * p["mevcut_kilo"] / 200) * 20 * p.get("egzersiz_katsayisi", 1.0))
        st.markdown(f"<div class='recipe-card'><div class='recipe-title'>✨ Günün Önerilen Kanalı: {egzersiz_adi}</div><div style='margin-top:8px; font-weight:600; color:{t['accent']};'>🔥 Bu egzersizi tamamlarsan yaklaşık <strong>{tahmini_video_kalorisi} kcal</strong> harcarsın!</div><a href='{egzersiz_link}' target='_blank' style='color: {t['accent']}; font-weight:600;'>Egzersiz Videosunu Aç ➔</a></div>", unsafe_allow_html=True)
        
        c_vid, c_man = st.columns(2)
        vid_yapildi_mi = c_vid.checkbox(f"✨ Bu egzersizi tamamladım!", value=curr_aktivite.get("video_tamamlandi", False))
        if vid_yapildi_mi != curr_aktivite.get("video_tamamlandi", False):
            curr_aktivite["video_tamamlandi"] = vid_yapildi_mi
            verileri_kaydet(aktif_user)
            st.rerun()
        
        yeni_manuel = c_man.number_input("Ekstra Kendi Yaptığım Spor (Örn: Pilates, Koşu) - Harcanan Kcal:", min_value=0, value=curr_aktivite.get("manuel_egzersiz_kcal", 0), step=50)
        if c_man.button("Ekstra Spor Kalorisini Ekle") and yeni_manuel != curr_aktivite.get("manuel_egzersiz_kcal", 0):
            curr_aktivite["manuel_egzersiz_kcal"] = yeni_manuel
            verileri_kaydet(aktif_user)
            st.rerun()

        st.divider()

        # YAPAY ZEKA GÖRSEL TARAMA (KAMERA KORUMALI & GEMINI 3.8 FLASH)
        st.subheader("📸 Yapay Zeka ile Öğün Tarama (Gemini 3.8 Flash)")
        st.markdown("Yemeğinin fotoğrafını çek veya yükle, yapay zeka senin için kalori ve makrolarını bulup günlüğüne eklesin!")
        
        api_key_gemini = p.get("gemini_api_key", "")
        if not api_key_gemini:
            st.warning("Bu özelliği kullanabilmek için 'Hesap ve Hedefler' sekmesinden Gemini API anahtarınızı (API Key) girmelisiniz.")
        else:
            try:
                genai.configure(api_key=api_key_gemini)
                tab_foto, tab_kamera = st.tabs(["🖼️ Galeriden Yükle", "📷 Kamera ile Çek"])
                img_data = None
                with tab_foto:
                    upl = st.file_uploader("Yemeğinin fotoğrafını seç", type=["jpg", "jpeg", "png"])
                    if upl: img_data = upl
                with tab_kamera:
                    st.caption("🔒 **Gizlilik Koruması:** Kamera arka planda izinsiz ve sürekli çalışmaması için varsayılan olarak kapalıdır.")
                    kamera_aktif = st.checkbox("📷 Kamerayı Aç / Fotoğraf Çek")
                    if kamera_aktif:
                        cam = st.camera_input("Fotoğrafınızı Çekin")
                        if cam: img_data = cam
                    
                if img_data:
                    image = Image.open(img_data)
                    st.image(image, caption="Analiz edilecek yemek görüntüsü", width=300)
                    secilen_ogun_ai = st.selectbox("Hangi Öğün Olarak Eklensin?", ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"])
                    
                    if st.button("✨ Yapay Zeka ile Analiz Et ve Ekle", use_container_width=True):
                        with st.spinner("Gemini yemeğini inceliyor... Lütfen bekle..."):
                            # Güncel Gemini 3.8 Flash Modeli
                            model = genai.GenerativeModel('gemini-3.8-flash')
                            prompt = "Bu fotoğraftaki yemeğin ne olduğunu ve standart bir porsiyonunun tahmini besin değerlerini analiz et. LÜTFEN SADECE GEÇERLİ BİR JSON FORMATINDA YANIT VER. Markdown, açıklama, ek yazı KULLANMA. Format: {\"Tarif\": \"Yemek Adı\", \"Kalori\": 300, \"Protein\": 15, \"Karbonhidrat\": 30, \"Yağ\": 10}"
                            try:
                                response = model.generate_content([prompt, image])
                                res_text = response.text.strip().replace("```json", "").replace("```", "")
                                ai_sonuc = json.loads(res_text)
                                
                                st.session_state.gunluk_kayitlar.append({
                                    "Tarih": secilen_tarih, "Öğün": secilen_ogun_ai,
                                    "Tarif": ai_sonuc.get("Tarif", "Yemek") + " (AI)",
                                    "Kalori": float(ai_sonuc.get("Kalori", 0)),
                                    "Protein": float(ai_sonuc.get("Protein", 0)),
                                    "Karbonhidrat": float(ai_sonuc.get("Karbonhidrat", 0)),
                                    "Yağ": float(ai_sonuc.get("Yağ", 0))
                                })
                                verileri_kaydet(aktif_user)
                                st.success(f"Yapay Zeka yemeği buldu: {ai_sonuc.get('Tarif')} ({ai_sonuc.get('Kalori')} kcal) ve başarıyla günlüğüne eklendi!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Analiz sırasında bir hata oluştu. API anahtarını veya kotanı kontrol et. Hata: {e}")
            except Exception as e:
                st.error("Gerekli yapay zeka kütüphaneleri yüklenemedi. Terminalden çalıştırın: `pip install google-generativeai pillow`")

        st.divider()

        # MANUEL ÖĞÜN EKLEME (Kutucuklu ve Sadece İsimli)
        st.subheader("🍽️ Öğün Ekle")
        cc1, cc2 = st.columns(2)
        sec_kat = cc1.selectbox("Kategori", list(DEVASA_MENU.keys()))
        sec_ogun = cc2.selectbox("Öğün Zamanı (Manuel)", ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"])
        urunler = DEVASA_MENU[sec_kat]
        secili_liste = []
        
        cu1, cu2 = st.columns(2)
        for idx, (u_name, u_data) in enumerate(urunler.items()):
            target_col = cu1 if idx % 2 == 0 else cu2
            if target_col.checkbox(u_name, key=f"chk_{secilen_tarih}_{u_name}"):
                secili_liste.append((u_name, u_data))

        if st.button("Seçili Lezzetleri Günlüğe Ekle", use_container_width=True):
            if secili_liste:
                for ad, data in secili_liste:
                    st.session_state.gunluk_kayitlar.append({
                        "Tarih": secilen_tarih, "Öğün": sec_ogun, "Tarif": ad,
                        "Kalori": data["kalori"], "Protein": data["protein"], "Karbonhidrat": data["karb"], "Yağ": data["yag"]
                    })
                verileri_kaydet(aktif_user)
                st.success("Seçilen ürünler listeye eklendi!")
                st.rerun()
            else: st.warning("Lütfen eklemek istediğiniz ürünleri işaretleyin.")

        st.divider()

        # ÖĞÜN GEÇMİŞİ VE ÇÖP KUTUSU (🗑️)
        st.subheader(f"📋 {secilen_tarih} Tarihinde Yenilenler")
        bugun_og = [(i, k) for i, k in enumerate(st.session_state.gunluk_kayitlar) if k["Tarih"] == secilen_tarih]
        toplam_alinan = 0
        
        if bugun_og:
            for i, kayit in bugun_og:
                toplam_alinan += kayit["Kalori"]
                cr1, cr2 = st.columns([10, 1])
                cr1.markdown(f"**{kayit['Öğün']}**: {kayit['Tarif']} <span style='color:{t['accent']};'>({kayit['Kalori']} kcal)</span>", unsafe_allow_html=True)
                if cr2.button("🗑️", key=f"sil_{i}"):
                    st.session_state.gunluk_kayitlar.pop(i)
                    verileri_kaydet(aktif_user)
                    st.rerun()
        else: st.info("Bu tarihte henüz yediğiniz bir şey kaydedilmedi.")

        st.divider()

        # NET KALORİ AÇIĞI VE GERİ BİLDİRİM
        st.subheader(f"⚖️ Günlük Özet ve Kalori Açığı Analizi")
        adim_kal = curr_aktivite["adim"] * 0.04
        vid_kal = tahmini_video_kalorisi if curr_aktivite.get("video_tamamlandi") else 0
        man_kal = curr_aktivite.get("manuel_egzersiz_kcal", 0)
        toplam_harcanan = bmr_kisi + adim_kal + vid_kal + man_kal
        
        olusturulan_acik = toplam_harcanan - toplam_alinan
        hedeflenen_acik = (p.get("verilmek_istenen_kilo", 3.0) * 7700) / p.get("hedef_gun", 45)

        sum1, sum2, sum3 = st.columns(3)
        sum1.markdown(f"**🔥 Harcanan Kalori**<br>(Bazal + Adım + Spor)<br><h3 style='color:{t['accent']}'>{round(toplam_harcanan)} kcal</h3>", unsafe_allow_html=True)
        sum2.markdown(f"**🍽️ Alınan Kalori**<br>(Yenilen Öğünler)<br><h3>{round(toplam_alinan)} kcal</h3>", unsafe_allow_html=True)
        sum3.markdown(f"**📉 Net Kalori Açığı**<br>(Harcanan - Alınan)<br><h3>{round(olusturulan_acik)} kcal</h3>", unsafe_allow_html=True)

        if olusturulan_acik >= hedeflenen_acik:
            st.success(f"🎉 **Tebrikler!** Doğru kalori açığında ({round(hedeflenen_acik)} kcal hedefini geçtin) ilerliyorsun. Harikasın!")
        elif olusturulan_acik > 0:
            st.info(f"💡 Kalori açığı oluşturdun ({round(olusturulan_acik)} kcal) ancak hedefin olan {round(hedeflenen_acik)} kcal'nin gerisindesin.")
        else:
            st.error(f"⚠️ **Maalesef** bugün hedeflenen kalori açığına ulaşamadın. Alınan kalori harcananı geçmiş durumda.")

    # =====================================================================
    # 5.2 HAFTALIK PROGRAM & DEĞERLENDİRME
    # =====================================================================
    elif menu == "Haftalık Program & Değerlendirme":
        st.header("Haftalık Geçmiş ve Grafikler")
        
        bugun_tarihi = datetime.date.today()
        son_7_gun = [(bugun_tarihi - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

        if st.session_state.gunluk_kayitlar:
            df_tum = pd.DataFrame(st.session_state.gunluk_kayitlar)
            haftalik_ozet = df_tum.groupby("Tarih")[["Kalori", "Protein", "Karbonhidrat", "Yağ"]].sum().reset_index()
            st.subheader("📈 Günlük Kalori Alımı Grafiği")
            st.line_chart(haftalik_ozet.set_index("Tarih")[["Kalori"]], color=t["accent"])
            st.subheader("📊 Besin Değerleri Toplam Tablosu")
            st.dataframe(haftalik_ozet, use_container_width=True)
        st.divider()

        haftalik_alinan, haftalik_harcanan, haftalik_yenenler = 0, 0, []
        for k in st.session_state.gunluk_kayitlar:
            if k["Tarih"] in son_7_gun:
                haftalik_alinan += k["Kalori"]
                haftalik_yenenler.append(f"{k['Tarih']} | {k['Öğün']}: {k['Tarif']} ({k['Kalori']} kcal)")

        for g in son_7_gun:
            if g in st.session_state.aktivite_loglari:
                log = st.session_state.aktivite_loglari[g]
                v_kal = round(((5.5 * 3.5 * p["mevcut_kilo"] / 200) * 20) * p.get("egzersiz_katsayisi", 1.0)) if log.get("video_tamamlandi") else 0
                m_kal = log.get("manuel_egzersiz_kcal", 0)
                haftalik_harcanan += (bmr_kisi + (log["adim"] * 0.04) + v_kal + m_kal)
            else: haftalik_harcanan += bmr_kisi

        haftalik_acik = haftalik_harcanan - haftalik_alinan
        hedef_haftalik_acik = ((p.get("verilmek_istenen_kilo", 3.0) * 7700) / p.get("hedef_gun", 45)) * 7

        st.subheader("📋 Bu Hafta Neler Yedik? (7 Günlük Geçmiş)")
        if haftalik_yenenler:
            for y in sorted(haftalik_yenenler, reverse=True): st.markdown(f"- {y}")
        else: st.info("Bu hafta hiç öğün kaydı girilmedi.")

        st.divider()
        st.markdown(f"""
            <div class="recipe-card">
                <div class="recipe-title">🔥 7 Günlük Total Değerlendirme</div>
                • <strong>Total Alınan Kalori:</strong> {round(haftalik_alinan)} kcal<br>
                • <strong>Total Harcanan Kalori:</strong> {round(haftalik_harcanan)} kcal<br>
                • <strong>Total Oluşturulan Açık:</strong> <span style="font-weight:700; color:{t['accent']};">{round(haftalik_acik)} kcal</span><br>
                • <strong>Haftalık Olması Gereken Açık:</strong> {round(hedef_haftalik_acik)} kcal
            </div>
        """, unsafe_allow_html=True)

        if haftalik_acik >= hedef_haftalik_acik: st.success("🎉 **Aferin!** İstediğin yolda devam ediyorsun. Bu haftaki toplam kalori açığı hedefini başarıyla tutturdun!")
        else: st.warning("⚠️ **Maalesef** bu hafta hedeflenen kadar kalori açığı çıkartmadınız. Önümüzdeki hafta sporu artırmayı deneyin.")

    # =====================================================================
    # 5.3 TARİF & MALZEME YÖNETİMİ
    # =====================================================================
    elif menu == "Tarif & Malzeme Yönetimi":
        st.header("Tarif ve Malzeme Yönetim Paneli")
        tab_m, tab_t = st.tabs(["1. Yeni Malzeme Ekle", "2. Gramaj Esaslı Tarif Oluştur"])
        with tab_m:
            m_ad = st.text_input("Malzeme Adı")
            m_kal = st.number_input("100g Kalori", min_value=0.0, value=100.0)
            m_pro = st.number_input("100g Protein", min_value=0.0, value=10.0)
            if st.button("Malzemeyi Kaydet"):
                if m_ad.strip():
                    st.session_state.besin_veritabani[m_ad.strip().lower()] = {"kalori": m_kal, "protein": m_pro, "karb": 0, "yag": 0}
                    verileri_kaydet(aktif_user)
                    st.success("Malzeme eklendi!")

        with tab_t:
            t_ad = st.text_input("Tarif Adı")
            secilen_malzemeler = st.multiselect("Malzemeleri Seç", list(st.session_state.besin_veritabani.keys()))
            tarif_gramajlari = {}
            for m in secilen_malzemeler: tarif_gramajlari[m] = st.number_input(f"{m.title()} kaç gram/ml?", value=100.0, key=f"g_{m}")
            if st.button("Tarifi Kaydet") and t_ad.strip() and tarif_gramajlari:
                st.session_state.hazir_tarifler[t_ad.strip()] = tarif_gramajlari
                verileri_kaydet(aktif_user)
                st.success("Tarif kaydedildi!")

    # =====================================================================
    # 5.4 HESAP, TEMA SEÇİMİ VE KALORİ AÇIĞI SİHİRBAZI
    # =====================================================================
    elif menu == "Hesap ve Hedefler":
        st.header("👤 Hesap, Kilo Verme Hedefi ve Tema Seçim Sihirbazı")

        secilen_tema = st.selectbox("Uygulama Tema Paleti (5 Seçenek)", ["Sonbahar Kremi", "Sıcak Kahve & Toprak", "Gece / Kuğu Mavisi", "Zeytin Yeşili & Doğa", "Karamel Esintisi"], index=["Sonbahar Kremi", "Sıcak Kahve & Toprak", "Gece / Kuğu Mavisi", "Zeytin Yeşili & Doğa", "Karamel Esintisi"].index(p.get("tema", "Sonbahar Kremi")) if p.get("tema", "Sonbahar Kremi") in ["Sonbahar Kremi", "Sıcak Kahve & Toprak", "Gece / Kuğu Mavisi", "Zeytin Yeşili & Doğa", "Karamel Esintisi"] else 0)

        st.divider()
        st.subheader("🤖 Yapay Zeka Entegrasyonu")
        gemini_key = st.text_input("Gemini API Key (Fotoğraflı Öğün Tarama İçin)", value=p.get("gemini_api_key", ""), type="password")
        st.caption("Eğer API key'iniz yoksa [Google AI Studio](https://aistudio.google.com/app/apikey) adresinden ücretsiz olarak alabilirsiniz.")

        st.divider()
        c1, c2, c3 = st.columns(3)
        cinsiyet = c1.selectbox("Cinsiyet", ["Kadın", "Erkek"], index=0 if p["cinsiyet"] == "Kadın" else 1)
        yas = c2.number_input("Yaş", min_value=15, max_value=80, value=int(p["yas"]))
        boy = c3.number_input("Boy (cm)", min_value=120, max_value=210, value=int(p["boy"]))

        c4, c5 = st.columns(2)
        mevcut_kilo = c4.number_input("Mevcut Kilon (kg)", min_value=35.0, value=float(p["mevcut_kilo"]), step=0.5)
        hedef_kilo = c5.number_input("Hedeflenen Kilon (kg)", min_value=30.0, value=float(p["hedef_kilo"]), step=0.5)

        st.markdown("---")
        ch1, ch2, ch3 = st.columns(3)
        verilmek_istenen = ch1.number_input("Kaç kilo vermek istiyorsun?", min_value=0.5, value=float(p.get("verilmek_istenen_kilo", 3.0)), step=0.5)
        hedef_gun = ch2.number_input("Bu hedefe kaç günde ulaşmak istiyorsun?", min_value=10, value=int(p.get("hedef_gun", 45)), step=5)
        egz_kat = ch3.slider("Egzersiz Çarpan Katsayısı", 0.8, 1.5, value=float(p.get("egzersiz_katsayisi", 1.0)), step=0.05)

        akt_sev = st.selectbox("Aktivite Düzeyi", ["Hareketsiz / Masa Başı", "Hafif Aktif (Haftada 1-3 gün)", "Orta Aktif (Haftada 3-5 gün)", "Çok Aktif"])

        if st.button("Tüm Bilgileri, Temayı ve API'yi Kaydet", use_container_width=True):
            st.session_state.profil.update({
                "cinsiyet": cinsiyet, "yas": yas, "boy": boy, "mevcut_kilo": mevcut_kilo, "hedef_kilo": hedef_kilo,
                "verilmek_istenen_kilo": verilmek_istenen, "hedef_gun": hedef_gun, "egzersiz_katsayisi": egz_kat, 
                "tema": secilen_tema, "gemini_api_key": gemini_key, "setup_tamamlandi": True
            })
            verileri_kaydet(aktif_user)
            st.success("✨ Tüm profilin, teman, API ayarların başarıyla kaydedildi! Sayfa yenileniyor...")
            st.rerun()

        st.divider()
        carpanlar = {"Hareketsiz / Masa Başı": 1.2, "Hafif Aktif (Haftada 1-3 gün)": 1.375, "Orta Aktif (Haftada 3-5 gün)": 1.55, "Çok Aktif": 1.725}
        tdee_g = bmr_kisi * carpanlar[akt_sev]
        gunluk_acik_g = (verilmek_istenen * 7700) / hedef_gun

        st.markdown(f"""
            <div class="recipe-card">
                <div class="recipe-title">💡 Nokta Atışı Kalori Planı</div>
                <div class="recipe-details">
                    • <strong>Günlük Harcanan Enerji (TDEE):</strong> {round(tdee_g)} kcal<br>
                    • <strong>Hedeflenen Sürede Vermen Gereken Günlük Açık:</strong> {round(gunluk_acik_g)} kcal / gün<br>
                    • <strong>Alman Gereken Günlük Kalori:</strong> <strong style="color: {t['accent']}; font-size:16px;">{round(tdee_g - gunluk_acik_g)} kcal</strong><br>
                    <em>{hedef_gun} günde {verilmek_istenen} kg vermek için bu kalori dengesini korumalısın!</em>
                </div>
            </div>
        """, unsafe_allow_html=True)
