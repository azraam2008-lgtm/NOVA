import datetime
import hashlib
import json
import os
import pandas as pd
import requests
import streamlit as st
from PIL import Image

# ----------------------------------------------------
# 1. SAYFA KONFİGÜRASYONU & AMBLEM BAĞLANTISI
# ----------------------------------------------------
AMBLEM_URL = "https://raw.githubusercontent.com/azraam2008-lgtm/NOVA/main/amblem.jpg"

st.set_page_config(
    page_title="Nova — Diyet ve Aktivite Asistanı",
    page_icon=AMBLEM_URL,
    layout="centered",
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
# 2. APPLE / CAL AI TARZI AKICI KAYDIRMA VE ESTETİK CSS
# ----------------------------------------------------
def get_theme_styles(tema_adi):
    if "Gece" in tema_adi or "Mavi" in tema_adi:
        return {"bg": "#0b132b", "card_bg": "linear-gradient(135deg, rgba(28, 37, 65, 0.95) 0%, rgba(11, 19, 43, 0.95) 100%)", "text": "#e0e1dd", "heading": "#ffffff", "accent": "#48cae4", "border": "#3a506b"}
    else:
        return {"bg": "#fcfbf9", "card_bg": "linear-gradient(135deg, #ffffff 0%, #f7f4f0 100%)", "text": "#2d3748", "heading": "#1a202c", "accent": "#b08968", "border": "#e2d9ce"}

def load_user_theme(username):
    user_file = f"veriler_{username.lower().strip()}.json"
    if os.path.exists(user_file):
        try:
            with open(user_file, "r", encoding="utf-8") as f:
                return json.load(f).get("profil", {}).get("tema", "Sonbahar Kremi")
        except: pass
    return "Sonbahar Kremi"

aktif_kullanici_temp = st.session_state.get("aktif_kullanici", "")
secilen_tema_adi = load_user_theme(aktif_kullanici_temp) if aktif_kullanici_temp else "Sonbahar Kremi"
t = get_theme_styles(secilen_tema_adi)

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap');
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; font-family: 'Plus Jakarta Sans', sans-serif; }}
    h1, h2, h3, h4 {{ font-family: 'Playfair Display', Georgia, serif !important; color: {t['heading']} !important; }}
    
    [data-testid="stSidebar"] {{ display: none; }}
    
    .apple-feature-card {{
        background: {t['card_bg']};
        border: 1px solid {t['border']};
        border-radius: 20px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04);
        transition: transform 0.3s ease;
    }}
    .apple-title {{
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 20px;
        font-weight: 600;
        color: {t['heading']};
        margin-bottom: 8px;
    }}
    .apple-desc {{
        font-size: 14.5px;
        color: {t['text']};
        opacity: 0.85;
        line-height: 1.6;
    }}
    .onboarding-box {{
        background: {t['card_bg']};
        border-left: 4px solid {t['accent']};
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }}
    .swan-avatar {{
        width: 45px;
        height: 45px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid {t['accent']};
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}
    </style>
""", unsafe_allow_html=True)

LOGO_MAIN = f"""<div style="text-align: center; font-family: 'Playfair Display', Georgia, serif; font-style: italic; font-size: 44px; font-weight: 700; letter-spacing: 18px; color: {t['heading']}; margin-bottom: 5px;">N&nbsp;&nbsp;O&nbsp;&nbsp;V&nbsp;&nbsp;A</div>"""
USERS_FILE = "kullanicilar.json"

# ----------------------------------------------------
# 3. 29 KATEGORİLİ DEVASA RESTORAN MENÜSÜ (DETAYLI MAKROLAR)
# ----------------------------------------------------
DEVASA_MENU = {
    "1. Kahvaltılıklar 🥐": {
        "Serpme Kahvaltı": {"kalori": 650, "protein": 24, "karb": 55, "yag": 36},
        "Kahvaltı Tabağı": {"kalori": 420, "protein": 18, "karb": 35, "yag": 22},
        "Menemen": {"kalori": 210, "protein": 11, "karb": 9, "yag": 15},
        "Kaşarlı Menemen": {"kalori": 320, "protein": 18, "karb": 10, "yag": 23},
        "Sucuklu Yumurta": {"kalori": 380, "protein": 19, "karb": 3, "yag": 32},
        "Peynirli Omlet": {"kalori": 280, "protein": 17, "karb": 2, "yag": 22},
        "Kaşarlı Tost": {"kalori": 320, "protein": 14, "karb": 30, "yag": 16},
        "Karışık Tost": {"kalori": 350, "protein": 15, "karb": 31, "yag": 18},
        "Avokadolu Tost": {"kalori": 310, "protein": 9, "karb": 28, "yag": 17},
        "Beyaz Peynirli Sandviç": {"kalori": 290, "protein": 12, "karb": 32, "yag": 11},
        "Kruvasan": {"kalori": 270, "protein": 5, "karb": 31, "yag": 14},
        "Çikolatalı Kruvasan": {"kalori": 340, "protein": 6, "karb": 38, "yag": 18},
        "Pancake": {"kalori": 310, "protein": 8, "karb": 45, "yag": 10},
        "Waffle Kahvaltı Tabağı": {"kalori": 450, "protein": 9, "karb": 58, "yag": 20},
        "Granola ve Yoğurt Kasesi": {"kalori": 320, "protein": 14, "karb": 44, "yag": 10},
        "Meyveli Yulaf Lapası": {"kalori": 260, "protein": 8, "karb": 46, "yag": 5},
        "Fransız Tostu": {"kalori": 330, "protein": 10, "karb": 36, "yag": 16},
        "Simit ve Peynir Tabağı": {"kalori": 380, "protein": 13, "karb": 52, "yag": 13},
        "Bagel Sandviç": {"kalori": 360, "protein": 14, "karb": 48, "yag": 12},
        "Kahvaltılık Quesadilla": {"kalori": 410, "protein": 20, "karb": 35, "yag": 22}
    },
    "2. Çorbalar 🍲": {
        "Mercimek Çorbası": {"kalori": 160, "protein": 8, "karb": 22, "yag": 4.5},
        "Ezogelin Çorbası": {"kalori": 170, "protein": 8, "karb": 24, "yag": 5},
        "Domates Çorbası": {"kalori": 140, "protein": 3, "karb": 18, "yag": 6},
        "Kremalı Mantar Çorbası": {"kalori": 190, "protein": 4, "karb": 16, "yag": 12},
        "Tavuk Suyu Çorbası": {"kalori": 110, "protein": 10, "karb": 8, "yag": 4},
        "Yayla Çorbası": {"kalori": 150, "protein": 5, "karb": 18, "yag": 6},
        "Brokoli Çorbası": {"kalori": 130, "protein": 4, "karb": 14, "yag": 7},
        "Balkabağı Çorbası": {"kalori": 120, "protein": 2, "karb": 19, "yag": 4},
        "Tarhana Çorbası": {"kalori": 165, "protein": 6, "karb": 25, "yag": 4},
        "İşkembe Çorbası": {"kalori": 220, "protein": 16, "karb": 6, "yag": 14},
        "Fransız Soğan Çorbası": {"kalori": 210, "protein": 7, "karb": 22, "yag": 10},
        "Sebze Çorbası": {"kalori": 95, "protein": 3, "karb": 16, "yag": 2.5},
        "Mısır Çorbası": {"kalori": 180, "protein": 4, "karb": 26, "yag": 7},
        "Düğün Çorbası": {"kalori": 200, "protein": 12, "karb": 14, "yag": 10},
        "Balık Çorbası": {"kalori": 175, "protein": 15, "karb": 10, "yag": 8}
    },
    "3. Ara Sıcaklar 🧀": {
        "Patates Kızartması": {"kalori": 360, "protein": 4, "karb": 45, "yag": 18},
        "Elma Dilim Patates": {"kalori": 330, "protein": 4, "karb": 42, "yag": 16},
        "Soğan Halkası": {"kalori": 340, "protein": 3, "karb": 38, "yag": 19},
        "Mozzarella Sticks": {"kalori": 390, "protein": 16, "karb": 30, "yag": 23},
        "Çıtır Tavuk Parçaları": {"kalori": 370, "protein": 24, "karb": 22, "yag": 20},
        "Tavuk Nugget": {"kalori": 310, "protein": 16, "karb": 20, "yag": 19},
        "Sigara Böreği": {"kalori": 290, "protein": 9, "karb": 26, "yag": 17},
        "Paçanga Böreği": {"kalori": 350, "protein": 14, "karb": 28, "yag": 20},
        "Mücver": {"kalori": 220, "protein": 6, "karb": 18, "yag": 13},
        "Mücver Topları": {"kalori": 230, "protein": 6, "karb": 19, "yag": 14},
        "Peynirli Börek": {"kalori": 320, "protein": 11, "karb": 32, "yag": 16},
        "Sarımsaklı Ekmek": {"kalori": 280, "protein": 7, "karb": 34, "yag": 12},
        "Nachos": {"kalori": 420, "protein": 9, "karb": 48, "yag": 21},
        "Jalapeño Poppers": {"kalori": 360, "protein": 10, "karb": 26, "yag": 24},
        "Çıtır Karides": {"kalori": 290, "protein": 18, "karb": 22, "yag": 14},
        "Falafel": {"kalori": 330, "protein": 13, "karb": 36, "yag": 15},
        "Humus ve Pita Ekmeği": {"kalori": 340, "protein": 12, "karb": 42, "yag": 14},
        "Patates Kroket": {"kalori": 310, "protein": 4, "karb": 38, "yag": 15},
        "Mantarlı Kaşarlı Fırın": {"kalori": 240, "protein": 12, "karb": 8, "yag": 18},
        "Mini Pizza": {"kalori": 320, "protein": 13, "karb": 36, "yag": 14},
        "Çıtır Kabak Dilimleri": {"kalori": 210, "protein": 5, "karb": 22, "yag": 11},
        "Fırında Kaşarlı Mantar": {"kalori": 220, "protein": 13, "karb": 6, "yag": 16},
        "Çıtır Peynir Topları": {"kalori": 400, "protein": 18, "karb": 28, "yag": 25},
        "Mini İçli Köfte": {"kalori": 340, "protein": 12, "karb": 35, "yag": 16},
        "Çıtır Karnabahar": {"kalori": 200, "protein": 6, "karb": 24, "yag": 9}
    },
    "4. Salatalar 🥗": {
        "Mevsim Salata": {"kalori": 90, "protein": 2, "karb": 8, "yag": 6},
        "Çoban Salata": {"kalori": 110, "protein": 3, "karb": 9, "yag": 7},
        "Akdeniz Salata": {"kalori": 180, "protein": 5, "karb": 10, "yag": 14},
        "Sezar Salata": {"kalori": 250, "protein": 8, "karb": 12, "yag": 19},
        "Tavuklu Sezar Salata": {"kalori": 380, "protein": 32, "karb": 12, "yag": 22},
        "Ton Balıklı Salata": {"kalori": 290, "protein": 28, "karb": 9, "yag": 15},
        "Hellim Peynirli Salata": {"kalori": 340, "protein": 16, "karb": 11, "yag": 26},
        "Izgara Tavuklu Salata": {"kalori": 320, "protein": 30, "karb": 10, "yag": 16},
        "Avokadolu Salata": {"kalori": 280, "protein": 4, "karb": 14, "yag": 23},
        "Kinoa Salatası": {"kalori": 270, "protein": 9, "karb": 35, "yag": 10},
        "Nohut Salatası": {"kalori": 290, "protein": 11, "karb": 40, "yag": 9},
        "Kısır": {"kalori": 280, "protein": 6, "karb": 42, "yag": 10},
        "Roka ve Parmesan Salatası": {"kalori": 210, "protein": 10, "karb": 6, "yag": 17},
        "Caprese Salata": {"kalori": 260, "protein": 14, "karb": 7, "yag": 20},
        "Somonlu Salata": {"kalori": 360, "protein": 26, "karb": 9, "yag": 24},
        "Meksika Fasulyeli Salata": {"kalori": 310, "protein": 12, "karb": 45, "yag": 9},
        "Bulgur Salatası": {"kalori": 250, "protein": 7, "karb": 38, "yag": 8},
        "Peynirli Akdeniz Salatası": {"kalori": 230, "protein": 10, "karb": 10, "yag": 17},
        "Burrata Salatası": {"kalori": 380, "protein": 18, "karb": 9, "yag": 30},
        "Asya Usulü Tavuk Salatası": {"kalori": 340, "protein": 28, "karb": 18, "yag": 17}
    },
    "5. Sandviçler 🥪": {
        "Kaşarlı Sandviç": {"kalori": 340, "protein": 15, "karb": 32, "yag": 17},
        "Karışık Sandviç": {"kalori": 370, "protein": 18, "karb": 33, "yag": 19},
        "Beyaz Peynirli Sandviç": {"kalori": 300, "protein": 13, "karb": 34, "yag": 12},
        "Hindi Fümeli Sandviç": {"kalori": 290, "protein": 20, "karb": 32, "yag": 9},
        "Tavuklu Sandviç": {"kalori": 350, "protein": 26, "karb": 33, "yag": 13},
        "Ton Balıklı Sandviç": {"kalori": 330, "protein": 24, "karb": 31, "yag": 12},
        "Club Sandwich": {"kalori": 520, "protein": 28, "karb": 46, "yag": 26},
        "BLT Sandviç": {"kalori": 410, "protein": 16, "karb": 34, "yag": 24},
        "Mozzarella ve Pesto Sandviç": {"kalori": 430, "protein": 18, "karb": 36, "yag": 25},
        "Avokadolu Sandviç": {"kalori": 360, "protein": 10, "karb": 35, "yag": 20},
        "Füme Etli Sandviç": {"kalori": 380, "protein": 22, "karb": 33, "yag": 18},
        "Roast Beef Sandviç": {"kalori": 420, "protein": 29, "karb": 34, "yag": 20},
        "Köfteli Sandviç": {"kalori": 480, "protein": 27, "karb": 42, "yag": 23},
        "Çıtır Tavuk Sandviç": {"kalori": 490, "protein": 26, "karb": 48, "yag": 22},
        "Yumurtalı Sandviç": {"kalori": 320, "protein": 15, "karb": 30, "yag": 15},
        "Bagel Sandviç": {"kalori": 380, "protein": 16, "karb": 46, "yag": 14},
        "Akdeniz Sandviç": {"kalori": 310, "protein": 11, "karb": 36, "yag": 13},
        "Izgara Sebzeli Sandviç": {"kalori": 280, "protein": 8, "karb": 38, "yag": 11},
        "Somon Füme Sandviç": {"kalori": 350, "protein": 21, "karb": 32, "yag": 15},
        "Philly Cheesesteak Sandviç": {"kalori": 560, "protein": 34, "karb": 44, "yag": 28}
    },
    "6. Dürümler ve Wrapler 🌯": {
        "Tavuklu Wrap": {"kalori": 420, "protein": 30, "karb": 42, "yag": 14},
        "Çıtır Tavuk Wrap": {"kalori": 510, "protein": 28, "karb": 52, "yag": 22},
        "Izgara Tavuklu Wrap": {"kalori": 400, "protein": 32, "karb": 40, "yag": 12},
        "Sezar Wrap": {"kalori": 460, "protein": 29, "karb": 43, "yag": 20},
        "Etli Wrap": {"kalori": 480, "protein": 32, "karb": 44, "yag": 19},
        "Köfteli Wrap": {"kalori": 490, "protein": 29, "karb": 46, "yag": 21},
        "Ton Balıklı Wrap": {"kalori": 410, "protein": 27, "karb": 40, "yag": 16},
        "Somonlu Wrap": {"kalori": 440, "protein": 26, "karb": 41, "yag": 19},
        "Falafel Wrap": {"kalori": 430, "protein": 15, "karb": 54, "yag": 17},
        "Vejetaryen Wrap": {"kalori": 340, "protein": 10, "karb": 48, "yag": 12},
        "Avokadolu Wrap": {"kalori": 400, "protein": 12, "karb": 44, "yag": 20},
        "Meksika Usulü Wrap": {"kalori": 460, "protein": 28, "karb": 48, "yag": 19},
        "Barbekü Tavuk Wrap": {"kalori": 440, "protein": 31, "karb": 46, "yag": 14},
        "Acılı Tavuk Wrap": {"kalori": 430, "protein": 30, "karb": 43, "yag": 15},
        "Cheddar Soslu Tavuk Wrap": {"kalori": 490, "protein": 32, "karb": 44, "yag": 21},
        "Hellim Peynirli Wrap": {"kalori": 450, "protein": 20, "karb": 42, "yag": 23},
        "Hindi Fümeli Wrap": {"kalori": 370, "protein": 25, "karb": 41, "yag": 11},
        "Ranch Soslu Wrap": {"kalori": 470, "protein": 29, "karb": 43, "yag": 21},
        "Teriyaki Tavuk Wrap": {"kalori": 430, "protein": 30, "karb": 49, "yag": 12},
        "Burrito Wrap": {"kalori": 540, "protein": 34, "karb": 60, "yag": 18}
    },
    "7. Burgerler 🍔": {
        "Klasik Hamburger": {"kalori": 520, "protein": 28, "karb": 42, "yag": 26},
        "Cheeseburger": {"kalori": 580, "protein": 32, "karb": 43, "yag": 31},
        "Double Cheeseburger": {"kalori": 750, "protein": 48, "karb": 44, "yag": 43},
        "Smash Burger": {"kalori": 610, "protein": 35, "karb": 42, "yag": 33},
        "Double Smash Burger": {"kalori": 820, "protein": 54, "karb": 43, "yag": 48},
        "Barbekü Burger": {"kalori": 640, "protein": 34, "karb": 52, "yag": 32},
        "Mantarlı Burger": {"kalori": 600, "protein": 33, "karb": 45, "yag": 31},
        "Trüflü Burger": {"kalori": 670, "protein": 36, "karb": 44, "yag": 37},
        "Çıtır Tavuk Burger": {"kalori": 590, "protein": 30, "karb": 56, "yag": 27},
        "Izgara Tavuk Burger": {"kalori": 480, "protein": 36, "karb": 44, "yag": 17},
        "Acılı Chicken Burger": {"kalori": 610, "protein": 31, "karb": 57, "yag": 28},
        "Mexican Burger": {"kalori": 660, "protein": 36, "karb": 48, "yag": 34},
        "Bacon Burger": {"kalori": 690, "protein": 38, "karb": 43, "yag": 40},
        "Füme Etli Burger": {"kalori": 650, "protein": 37, "karb": 43, "yag": 36},
        "Blue Cheese Burger": {"kalori": 680, "protein": 37, "karb": 43, "yag": 39},
        "Onion Ring Burger": {"kalori": 670, "protein": 32, "karb": 58, "yag": 33},
        "Avokadolu Burger": {"kalori": 630, "protein": 31, "karb": 46, "yag": 35},
        "Vegan Burger": {"kalori": 440, "protein": 18, "karb": 54, "yag": 16},
        "Vejetaryen Burger": {"kalori": 470, "protein": 20, "karb": 52, "yag": 20},
        "Mini Burger Tabağı": {"kalori": 720, "protein": 42, "karb": 64, "yag": 34}
    },
    "8. Fast Food 🍟": {
        "Tavuk Nugget Menü": {"kalori": 680, "protein": 28, "karb": 75, "yag": 30},
        "Çıtır Tavuk Menü": {"kalori": 740, "protein": 36, "karb": 78, "yag": 32},
        "Tavuk Kanat": {"kalori": 550, "protein": 35, "karb": 12, "yag": 40},
        "Buffalo Wings": {"kalori": 590, "protein": 36, "karb": 14, "yag": 43},
        "Chicken Tenders": {"kalori": 510, "protein": 38, "karb": 32, "yag": 24},
        "Hot Dog": {"kalori": 420, "protein": 14, "karb": 38, "yag": 24},
        "Corn Dog": {"kalori": 390, "protein": 10, "karb": 44, "yag": 19},
        "Sosisli Sandviç": {"kalori": 430, "protein": 15, "karb": 39, "yag": 25},
        "Tavuk Popcorn": {"kalori": 460, "protein": 22, "karb": 44, "yag": 22},
        "Fish and Chips": {"kalori": 760, "protein": 32, "karb": 76, "yag": 36},
        "Quesadilla": {"kalori": 580, "protein": 30, "karb": 48, "yag": 30},
        "Nachos Tabağı": {"kalori": 650, "protein": 18, "karb": 72, "yag": 34},
        "Tavuklu Nachos": {"kalori": 780, "protein": 45, "karb": 74, "yag": 35},
        "Burrito": {"kalori": 710, "protein": 42, "karb": 78, "yag": 24},
        "Taco": {"kalori": 280, "protein": 14, "karb": 24, "yag": 14},
        "Tavuklu Taco": {"kalori": 310, "protein": 22, "karb": 24, "yag": 13},
        "Etli Taco": {"kalori": 340, "protein": 20, "karb": 25, "yag": 17},
        "Mini Pizza": {"kalori": 350, "protein": 14, "karb": 38, "yag": 15},
        "Patatesli Kumpir": {"kalori": 590, "protein": 18, "karb": 76, "yag": 24},
        "Yüklü Patates (Loaded Fries)": {"kalori": 720, "protein": 22, "karb": 82, "yag": 36}
    },
    "9. Pizzalar 🍕": {
        "Margherita": {"kalori": 760, "protein": 29, "karb": 98, "yag": 27},
        "Karışık Pizza": {"kalori": 910, "protein": 42, "karb": 102, "yag": 38},
        "Dört Peynirli Pizza": {"kalori": 980, "protein": 46, "karb": 96, "yag": 45},
        "Pepperoni Pizza": {"kalori": 940, "protein": 39, "karb": 100, "yag": 42},
        "Sucuklu Pizza": {"kalori": 920, "protein": 40, "karb": 99, "yag": 40},
        "Mantarlı Pizza": {"kalori": 800, "protein": 32, "karb": 101, "yag": 29},
        "Tavuklu Barbekü Pizza": {"kalori": 880, "protein": 52, "karb": 110, "yag": 28},
        "Akdeniz Pizza": {"kalori": 820, "protein": 34, "karb": 98, "yag": 33},
        "Vejetaryen Pizza": {"kalori": 740, "protein": 28, "karb": 104, "yag": 23},
        "Ton Balıklı Pizza": {"kalori": 860, "protein": 48, "karb": 99, "yag": 32},
        "Kavurmalı Pizza": {"kalori": 950, "protein": 49, "karb": 100, "yag": 41},
        "Pesto Tavuk Pizza": {"kalori": 890, "protein": 53, "karb": 102, "yag": 31},
        "Meksika Pizza": {"kalori": 910, "protein": 41, "karb": 106, "yag": 36},
        "Hawaii Pizza": {"kalori": 830, "protein": 33, "karb": 108, "yag": 29},
        "Füme Etli Pizza": {"kalori": 900, "protein": 44, "karb": 99, "yag": 37},
        "Trüflü Mantarlı Pizza": {"kalori": 850, "protein": 35, "karb": 100, "yag": 34},
        "Beyaz Soslu Pizza": {"kalori": 890, "protein": 38, "karb": 96, "yag": 39},
        "Burrata Pizza": {"kalori": 940, "protein": 43, "karb": 98, "yag": 41},
        "Mini Pizza": {"kalori": 360, "protein": 14, "karb": 40, "yag": 15},
        "Calzone": {"kalori": 980, "protein": 46, "karb": 112, "yag": 38}
    },
    "10. Makarnalar 🍝": {
        "Spaghetti Bolognese": {"kalori": 580, "protein": 26, "karb": 76, "yag": 20},
        "Spaghetti Napoliten": {"kalori": 440, "protein": 13, "karb": 80, "yag": 8},
        "Alfredo Tavuklu Makarna": {"kalori": 720, "protein": 44, "karb": 78, "yag": 26},
        "Penne Arrabbiata": {"kalori": 460, "protein": 14, "karb": 82, "yag": 9},
        "Fettuccine Alfredo": {"kalori": 680, "protein": 20, "karb": 76, "yag": 33},
        "Kremalı Mantarlı Makarna": {"kalori": 640, "protein": 18, "karb": 80, "yag": 28},
        "Pesto Soslu Makarna": {"kalori": 590, "protein": 16, "karb": 75, "yag": 25},
        "Dört Peynirli Makarna": {"kalori": 740, "protein": 30, "karb": 78, "yag": 34},
        "Mac and Cheese": {"kalori": 690, "protein": 24, "karb": 82, "yag": 29},
        "Lazanya": {"kalori": 680, "protein": 34, "karb": 64, "yag": 31},
        "Ravioli": {"kalori": 560, "protein": 22, "karb": 68, "yag": 22},
        "Tortellini": {"kalori": 570, "protein": 23, "karb": 69, "yag": 22},
        "Deniz Mahsullü Makarna": {"kalori": 610, "protein": 38, "karb": 74, "yag": 18},
        "Karidesli Linguine": {"kalori": 590, "protein": 36, "karb": 75, "yag": 16},
        "Kıymalı Fırın Makarna": {"kalori": 650, "protein": 30, "karb": 72, "yag": 27},
        "Kremalı Tavuklu Penne": {"kalori": 700, "protein": 42, "karb": 76, "yag": 25},
        "Domates Soslu Fusilli": {"kalori": 450, "protein": 13, "karb": 82, "yag": 8},
        "Trüflü Mantarlı Fettuccine": {"kalori": 710, "protein": 21, "karb": 78, "yag": 36},
        "Ispanaklı Ricotta Ravioli": {"kalori": 540, "protein": 20, "karb": 66, "yag": 22},
        "Ton Balıklı Makarna": {"kalori": 610, "protein": 38, "karb": 76, "yag": 16}
    },
    "11. Ana Yemekler 🍽️": {
        "Izgara Tavuk": {"kalori": 280, "protein": 42, "karb": 0, "yag": 12},
        "Tavuk Şinitzel": {"kalori": 480, "protein": 36, "karb": 32, "yag": 23},
        "Tavuk Parmesan": {"kalori": 560, "protein": 44, "karb": 28, "yag": 30},
        "Tavuk Sote": {"kalori": 360, "protein": 38, "karb": 10, "yag": 18},
        "Kremalı Mantarlı Tavuk": {"kalori": 450, "protein": 40, "karb": 8, "yag": 28},
        "Barbekü Soslu Tavuk": {"kalori": 390, "protein": 39, "karb": 22, "yag": 14},
        "Izgara Köfte": {"kalori": 360, "protein": 28, "karb": 6, "yag": 24},
        "Kasap Köfte": {"kalori": 390, "protein": 27, "karb": 7, "yag": 27},
        "Et Sote": {"kalori": 420, "protein": 36, "karb": 8, "yag": 27},
        "Dana Antrikot": {"kalori": 520, "protein": 44, "karb": 0, "yag": 37},
        "Bonfile": {"kalori": 410, "protein": 48, "karb": 0, "yag": 23},
        "Izgara Somon": {"kalori": 380, "protein": 34, "karb": 0, "yag": 26},
        "Fırında Levrek": {"kalori": 310, "protein": 36, "karb": 2, "yag": 17},
        "Çıtır Balık": {"kalori": 460, "protein": 28, "karb": 34, "yag": 23},
        "Etli Fajita": {"kalori": 540, "protein": 42, "karb": 36, "yag": 24},
        "Tavuk Fajita": {"kalori": 470, "protein": 44, "karb": 35, "yag": 16},
        "Tavuk Teriyaki": {"kalori": 410, "protein": 41, "karb": 24, "yag": 14},
        "Dana Teriyaki": {"kalori": 460, "protein": 39, "karb": 25, "yag": 22},
        "Sebzeli Noodle": {"kalori": 380, "protein": 9, "karb": 62, "yag": 11},
        "Tavuklu Noodle": {"kalori": 510, "protein": 34, "karb": 60, "yag": 15},
        "Etli Noodle": {"kalori": 550, "protein": 36, "karb": 61, "yag": 18},
        "Tavuklu Curry": {"kalori": 480, "protein": 42, "karb": 18, "yag": 26},
        "Etli Güveç": {"kalori": 440, "protein": 38, "karb": 14, "yag": 26},
        "Fırında Sebzeli Tavuk": {"kalori": 370, "protein": 39, "karb": 16, "yag": 17},
        "Izgara Hellim Tabağı": {"kalori": 460, "protein": 24, "karb": 4, "yag": 38}
    },
    "12. Geleneksel Türk Yemekleri 🥘": {
        "Mantı": {"kalori": 480, "protein": 18, "karb": 62, "yag": 18},
        "İskender Kebap": {"kalori": 780, "protein": 46, "karb": 54, "yag": 42},
        "Adana Kebap": {"kalori": 560, "protein": 35, "karb": 10, "yag": 41},
        "Urfa Kebap": {"kalori": 530, "protein": 34, "karb": 10, "yag": 38},
        "Tavuk Şiş": {"kalori": 340, "protein": 40, "karb": 4, "yag": 18},
        "Et Şiş": {"kalori": 410, "protein": 38, "karb": 4, "yag": 26},
        "Lahmacun": {"kalori": 240, "protein": 11, "karb": 30, "yag": 8},
        "Pide": {"kalori": 450, "protein": 18, "karb": 56, "yag": 17},
        "Kaşarlı Pide": {"kalori": 490, "protein": 22, "karb": 54, "yag": 21},
        "Kuşbaşılı Pide": {"kalori": 470, "protein": 25, "karb": 55, "yag": 18},
        "Karışık Pide": {"kalori": 520, "protein": 28, "karb": 55, "yag": 22},
        "İçli Köfte": {"kalori": 310, "protein": 11, "karb": 32, "yag": 15},
        "Yaprak Sarma": {"kalori": 180, "protein": 4, "karb": 24, "yag": 8},
        "Zeytinyağlı Enginar": {"kalori": 160, "protein": 3, "karb": 18, "yag": 9},
        "Karnıyarık": {"kalori": 290, "protein": 14, "karb": 16, "yag": 19},
        "İmam Bayıldı": {"kalori": 220, "protein": 3, "karb": 17, "yag": 15},
        "Kuru Fasulye ve Pilav": {"kalori": 510, "protein": 20, "karb": 82, "yag": 10},
        "Etli Nohut": {"kalori": 380, "protein": 22, "karb": 42, "yag": 14},
        "Tavuklu Pilav": {"kalori": 460, "protein": 26, "karb": 58, "yag": 14},
        "Hünkar Beğendi": {"kalori": 490, "protein": 28, "karb": 26, "yag": 30}
    },
    "13. Pilavlar 🍚": {
        "Sade Pirinç Pilavı": {"kalori": 210, "protein": 3.5, "karb": 44, "yag": 2.5},
        "Tereyağlı Pirinç Pilavı": {"kalori": 250, "protein": 4, "karb": 42, "yag": 7},
        "Şehriyeli Pirinç Pilavı": {"kalori": 230, "protein": 4, "karb": 43, "yag": 5},
        "Sebzeli Pirinç Pilavı": {"kalori": 210, "protein": 4, "karb": 40, "yag": 4},
        "İç Pilav": {"kalori": 290, "protein": 6, "karb": 46, "yag": 9},
        "Tavuklu Pilav": {"kalori": 360, "protein": 22, "karb": 44, "yag": 11},
        "Nohutlu Pilav": {"kalori": 310, "protein": 10, "karb": 54, "yag": 6},
        "Etli Pilav": {"kalori": 380, "protein": 24, "karb": 44, "yag": 13},
        "Özbek Pilavı": {"kalori": 420, "protein": 20, "karb": 48, "yag": 17},
        "İran Usulü Safranlı Pilav": {"kalori": 260, "protein": 5, "karb": 48, "yag": 6},
        "Basmati Pilavı": {"kalori": 200, "protein": 4, "karb": 44, "yag": 1},
        "Yasemin Pirinci Pilavı": {"kalori": 205, "protein": 4, "karb": 45, "yag": 1},
        "Bulgur Pilavı": {"kalori": 170, "protein": 5.5, "karb": 34, "yag": 2},
        "Domatesli Bulgur Pilavı": {"kalori": 190, "protein": 6, "karb": 36, "yag": 3},
        "Sebzeli Bulgur Pilavı": {"kalori": 180, "protein": 6, "karb": 34, "yag": 3},
        "Şehriye Pilavı": {"kalori": 280, "protein": 8, "karb": 48, "yag": 7},
        "Arpa Şehriye Pilavı": {"kalori": 280, "protein": 8, "karb": 48, "yag": 7},
        "Firik Pilavı": {"kalori": 210, "protein": 8, "karb": 38, "yag": 3},
        "Kestaneli İç Pilav": {"kalori": 330, "protein": 6, "karb": 54, "yag": 10},
        "Mantarlı Risotto": {"kalori": 460, "protein": 11, "karb": 68, "yag": 15},
        "Parmesanlı Risotto": {"kalori": 510, "protein": 14, "karb": 65, "yag": 21},
        "Deniz Mahsullü Risotto": {"kalori": 490, "protein": 24, "karb": 66, "yag": 16},
        "Tavuklu Risotto": {"kalori": 530, "protein": 29, "karb": 66, "yag": 17},
        "Sebzeli Risotto": {"kalori": 410, "protein": 9, "karb": 67, "yag": 12},
        "Kinoa Pilavı": {"kalori": 220, "protein": 8, "karb": 39, "yag": 3.5}
    },
    "14. Börekler 🥟": {
        "Su Böreği": {"kalori": 340, "protein": 12, "karb": 36, "yag": 16},
        "Kol Böreği": {"kalori": 360, "protein": 10, "karb": 38, "yag": 19},
        "Sigara Böreği": {"kalori": 290, "protein": 9, "karb": 26, "yag": 17},
        "Paçanga Böreği": {"kalori": 350, "protein": 14, "karb": 28, "yag": 20},
        "Kıymalı Börek": {"kalori": 370, "protein": 15, "karb": 36, "yag": 19},
        "Peynirli Börek": {"kalori": 320, "protein": 11, "karb": 32, "yag": 16},
        "Patatesli Börek": {"kalori": 310, "protein": 7, "karb": 42, "yag": 13},
        "Ispanaklı Börek": {"kalori": 280, "protein": 8, "karb": 34, "yag": 12},
        "Pırasalı Börek": {"kalori": 270, "protein": 7, "karb": 35, "yag": 11},
        "Gül Böreği": {"kalori": 350, "protein": 10, "karb": 37, "yag": 18},
        "Talaş Böreği": {"kalori": 410, "protein": 16, "karb": 33, "yag": 24},
        "Çiğ Börek": {"kalori": 420, "protein": 15, "karb": 39, "yag": 23},
        "Boşnak Böreği": {"kalori": 380, "protein": 12, "karb": 36, "yag": 21},
        "Arnavut Böreği": {"kalori": 360, "protein": 13, "karb": 35, "yag": 19},
        "Laz Böreği": {"kalori": 410, "protein": 7, "karb": 54, "yag": 18},
        "Kürt Böreği": {"kalori": 390, "protein": 6, "karb": 48, "yag": 20},
        "Tepsi Böreği": {"kalori": 340, "protein": 11, "karb": 35, "yag": 17},
        "Sodalı Börek": {"kalori": 330, "protein": 12, "karb": 33, "yag": 16},
        "Tavuklu Börek": {"kalori": 380, "protein": 22, "karb": 34, "yag": 17},
        "Mantarlı Kaşarlı Börek": {"kalori": 350, "protein": 14, "karb": 32, "yag": 19},
        "Kıymalı Kol Böreği": {"kalori": 380, "protein": 16, "karb": 37, "yag": 20},
        "Patatesli Gül Böreği": {"kalori": 320, "protein": 8, "karb": 43, "yag": 14},
        "Peynirli Milföy Böreği": {"kalori": 440, "protein": 12, "karb": 34, "yag": 29},
        "Ispanaklı Peynirli Börek": {"kalori": 300, "protein": 10, "karb": 33, "yag": 14},
        "Mini Börek Tabağı": {"kalori": 610, "protein": 20, "karb": 68, "yag": 30}
    },
    "15. Gözlemeler 🫓": {
        "Sade Gözleme": {"kalori": 340, "protein": 8, "karb": 56, "yag": 9},
        "Peynirli Gözleme": {"kalori": 420, "protein": 18, "karb": 54, "yag": 15},
        "Kaşarlı Gözleme": {"kalori": 460, "protein": 20, "karb": 54, "yag": 19},
        "Patatesli Gözleme": {"kalori": 400, "protein": 10, "karb": 64, "yag": 11},
        "Kıymalı Gözleme": {"kalori": 470, "protein": 24, "karb": 55, "yag": 18},
        "Ispanaklı Gözleme": {"kalori": 370, "protein": 11, "karb": 56, "yag": 11},
        "Ispanaklı Peynirli Gözleme": {"kalori": 410, "protein": 16, "karb": 55, "yag": 14},
        "Patatesli Kaşarlı Gözleme": {"kalori": 480, "protein": 16, "karb": 62, "yag": 19},
        "Sucuklu Kaşarlı Gözleme": {"kalori": 540, "protein": 23, "karb": 55, "yag": 26},
        "Kavurmalı Kaşarlı Gözleme": {"kalori": 560, "protein": 29, "karb": 55, "yag": 26},
        "Mantarlı Kaşarlı Gözleme": {"kalori": 440, "protein": 18, "karb": 53, "yag": 18},
        "Tavuklu Gözleme": {"kalori": 480, "protein": 32, "karb": 54, "yag": 14},
        "Lor Peynirli Gözleme": {"kalori": 390, "protein": 20, "karb": 54, "yag": 11},
        "Otlu Peynirli Gözleme": {"kalori": 410, "protein": 17, "karb": 54, "yag": 14},
        "Pastırmalı Kaşarlı Gözleme": {"kalori": 530, "protein": 26, "karb": 55, "yag": 24},
        "Zeytinli Kaşarlı Gözleme": {"kalori": 470, "protein": 18, "karb": 55, "yag": 21},
        "Sebzeli Gözleme": {"kalori": 360, "protein": 9, "karb": 57, "yag": 10},
        "Çökelekli Gözleme": {"kalori": 380, "protein": 19, "karb": 54, "yag": 10},
        "Karışık Gözleme": {"kalori": 550, "protein": 27, "karb": 56, "yag": 25},
        "Mini Gözleme Tabağı": {"kalori": 680, "protein": 28, "karb": 82, "yag": 27}
    },
    "16. Zeytinyağlılar 🫒": {
        "Zeytinyağlı Yaprak Sarma": {"kalori": 190, "protein": 3, "karb": 22, "yag": 10},
        "Zeytinyağlı Biber Dolması": {"kalori": 210, "protein": 4, "karb": 20, "yag": 12},
        "Zeytinyağlı Enginar": {"kalori": 170, "protein": 3, "karb": 16, "yag": 10},
        "Zeytinyağlı Taze Fasulye": {"kalori": 140, "protein": 2, "karb": 12, "yag": 9},
        "Zeytinyağlı Barbunya": {"kalori": 240, "protein": 8, "karb": 28, "yag": 10},
        "Zeytinyağlı Pırasa": {"kalori": 160, "protein": 2, "karb": 14, "yag": 10},
        "Zeytinyağlı Kereviz": {"kalori": 180, "protein": 3, "karb": 16, "yag": 11},
        "Zeytinyağlı Kabak": {"kalori": 130, "protein": 2, "karb": 10, "yag": 9},
        "Zeytinyağlı Patlıcan": {"kalori": 210, "protein": 2, "karb": 14, "yag": 16},
        "İmam Bayıldı": {"kalori": 220, "protein": 3, "karb": 17, "yag": 15},
        "Zeytinyağlı Bamya": {"kalori": 140, "protein": 3, "karb": 11, "yag": 9},
        "Zeytinyağlı Bezelye": {"kalori": 190, "protein": 6, "karb": 22, "yag": 8},
        "Zeytinyağlı Pazı Sarması": {"kalori": 175, "protein": 4, "karb": 19, "yag": 9},
        "Zeytinyağlı Dolma": {"kalori": 200, "protein": 3, "karb": 21, "yag": 11},
        "Zeytinyağlı Börülce": {"kalori": 190, "protein": 7, "karb": 20, "yag": 9},
        "Zeytinyağlı Brokoli": {"kalori": 130, "protein": 4, "karb": 9, "yag": 9},
        "Zeytinyağlı Karnabahar": {"kalori": 135, "protein": 4, "karb": 10, "yag": 9},
        "Zeytinyağlı Havuç": {"kalori": 150, "protein": 2, "karb": 16, "yag": 9},
        "Zeytinyağlı Kuru Domates": {"kalori": 230, "protein": 4, "karb": 18, "yag": 16},
        "Zeytinyağlı Karışık Sebze Tabağı": {"kalori": 195, "protein": 3, "karb": 15, "yag": 13}
    },
    "17. Fırın Yemekleri 🧑‍🍳": {
        "Lazanya": {"kalori": 680, "protein": 34, "karb": 64, "yag": 31},
        "Kıymalı Fırın Makarna": {"kalori": 650, "protein": 30, "karb": 72, "yag": 27},
        "Beşamel Soslu Fırın Makarna": {"kalori": 670, "protein": 22, "karb": 78, "yag": 30},
        "Fırında Tavuk ve Patates": {"kalori": 490, "protein": 38, "karb": 42, "yag": 19},
        "Fırında Sebzeli Tavuk": {"kalori": 380, "protein": 40, "karb": 16, "yag": 17},
        "Fırında Köfte ve Patates": {"kalori": 540, "protein": 32, "karb": 44, "yag": 26},
        "İzmir Köfte": {"kalori": 480, "protein": 30, "karb": 36, "yag": 24},
        "Fırında Kaşarlı Köfte": {"kalori": 520, "protein": 36, "karb": 24, "yag": 31},
        "Fırında Etli Güveç": {"kalori": 460, "protein": 40, "karb": 15, "yag": 26},
        "Sebzeli Güveç": {"kalori": 210, "protein": 6, "karb": 28, "yag": 9},
        "Fırında Karnabahar Graten": {"kalori": 290, "protein": 12, "karb": 18, "yag": 19},
        "Brokoli Graten": {"kalori": 280, "protein": 13, "karb": 16, "yag": 18},
        "Patates Graten": {"kalori": 390, "protein": 10, "karb": 42, "yag": 21},
        "Fırında Kabak Mücver": {"kalori": 230, "protein": 7, "karb": 19, "yag": 13},
        "Fırında Patlıcan Musakka": {"kalori": 340, "protein": 18, "karb": 20, "yag": 22},
        "Fırında Karnıyarık": {"kalori": 300, "protein": 15, "karb": 17, "yag": 19},
        "Fırında Biber Dolması": {"kalori": 250, "protein": 11, "karb": 22, "yag": 13},
        "Fırında Mantar Dolması": {"kalori": 210, "protein": 12, "karb": 10, "yag": 14},
        "Fırında Somon": {"kalori": 390, "protein": 35, "karb": 2, "yag": 26},
        "Fırında Levrek": {"kalori": 320, "protein": 37, "karb": 2, "yag": 17},
        "Fırında Sebzeli Levrek": {"kalori": 360, "protein": 38, "karb": 10, "yag": 18},
        "Fırında Tavuk Baget": {"kalori": 420, "protein": 41, "karb": 2, "yag": 27},
        "Fırında Hindi": {"kalori": 340, "protein": 52, "karb": 2, "yag": 13},
        "Fırında Kaşarlı Mantar": {"kalori": 230, "protein": 13, "karb": 6, "yag": 17},
        "Fırında Peynirli Gnocchi": {"kalori": 510, "protein": 18, "karb": 68, "yag": 19},
        "Tavuklu Fırın Güveç": {"kalori": 410, "protein": 42, "karb": 14, "yag": 20},
        "Ispanaklı Ricotta Fırın Makarna": {"kalori": 590, "protein": 24, "karb": 66, "yag": 25},
        "Fırında Patatesli Tavuk": {"kalori": 470, "protein": 39, "karb": 38, "yag": 18},
        "Fırında Peynirli Sebze": {"kalori": 270, "protein": 11, "karb": 16, "yag": 18},
        "Fırında Etli Patates": {"kalori": 510, "protein": 34, "karb": 42, "yag": 23}
    },
    "18. Vejetaryen ve Vegan Seçenekler 🌱": {
        "Sebzeli Burger": {"kalori": 440, "protein": 18, "karb": 54, "yag": 16},
        "Vegan Burger": {"kalori": 420, "protein": 17, "karb": 52, "yag": 15},
        "Falafel Tabağı": {"kalori": 480, "protein": 18, "karb": 58, "yag": 20},
        "Sebzeli Noodle": {"kalori": 380, "protein": 9, "karb": 62, "yag": 11},
        "Sebzeli Quesadilla": {"kalori": 490, "protein": 18, "karb": 58, "yag": 22},
        "Vegan Pizza": {"kalori": 680, "protein": 22, "karb": 102, "yag": 21},
        "Sebzeli Wrap": {"kalori": 350, "protein": 10, "karb": 50, "yag": 12},
        "Mercimek Köftesi": {"kalori": 260, "protein": 9, "karb": 42, "yag": 6},
        "Zeytinyağlı Sarma": {"kalori": 180, "protein": 4, "karb": 24, "yag": 8},
        "Fırında Sebze Tabağı": {"kalori": 240, "protein": 5, "karb": 32, "yag": 10},
        "Nohutlu Kinoa Kasesi": {"kalori": 410, "protein": 16, "karb": 62, "yag": 11},
        "Avokadolu Tost": {"kalori": 310, "protein": 9, "karb": 28, "yag": 17},
        "Humus Tabağı": {"kalori": 380, "protein": 14, "karb": 38, "yag": 19},
        "Sebzeli Köri": {"kalori": 390, "protein": 11, "karb": 46, "yag": 18},
        "Tofu Teriyaki": {"kalori": 340, "protein": 22, "karb": 26, "yag": 14},
        "Sebzeli Lazanya": {"kalori": 520, "protein": 20, "karb": 68, "yag": 19},
        "Vegan Mac and Cheese": {"kalori": 540, "protein": 16, "karb": 76, "yag": 20},
        "Mantarlı Risotto": {"kalori": 460, "protein": 11, "karb": 68, "yag": 15},
        "Zeytinyağlı Enginar": {"kalori": 170, "protein": 3, "karb": 16, "yag": 10},
        "Sebzeli Falafel Dürüm": {"kalori": 450, "protein": 16, "karb": 62, "yag": 16}
    },
    "19. Sokak Lezzetleri 🌮": {
        "Islak Hamburger": {"kalori": 440, "protein": 20, "karb": 42, "yag": 22},
        "Kumpir": {"kalori": 610, "protein": 19, "karb": 78, "yag": 26},
        "Kokoreç": {"kalori": 590, "protein": 32, "karb": 24, "yag": 41},
        "Midye Dolma": {"kalori": 65, "protein": 3, "karb": 9, "yag": 2},
        "Midye Tava": {"kalori": 380, "protein": 18, "karb": 34, "yag": 19},
        "Tantuni": {"kalori": 490, "protein": 30, "karb": 38, "yag": 25},
        "Et Döner Dürüm": {"kalori": 540, "protein": 34, "karb": 44, "yag": 26},
        "Tavuk Döner Dürüm": {"kalori": 460, "protein": 35, "karb": 43, "yag": 16},
        "İskender Döner": {"kalori": 780, "protein": 46, "karb": 54, "yag": 42},
        "Çiğ Köfte Dürüm": {"kalori": 390, "protein": 10, "karb": 64, "yag": 10},
        "Balık Ekmek": {"kalori": 480, "protein": 28, "karb": 52, "yag": 18},
        "Kumru": {"kalori": 590, "protein": 26, "karb": 54, "yag": 31},
        "Gözleme": {"kalori": 380, "protein": 12, "karb": 55, "yag": 12},
        "Sucuk Ekmek": {"kalori": 560, "protein": 22, "karb": 45, "yag": 33},
        "Köfte Ekmek": {"kalori": 530, "protein": 28, "karb": 46, "yag": 26},
        "Tavuklu Pilav": {"kalori": 460, "protein": 26, "karb": 58, "yag": 14},
        "Nohutlu Pilav": {"kalori": 380, "protein": 13, "karb": 66, "yag": 7},
        "Kokoreç Ekmek": {"kalori": 680, "protein": 36, "karb": 46, "yag": 40},
        "Ayvalık Tostu": {"kalori": 620, "protein": 28, "karb": 52, "yag": 34},
        "Patso": {"kalori": 490, "protein": 11, "karb": 68, "yag": 19},
        "Yengen Tost": {"kalori": 570, "protein": 30, "karb": 48, "yag": 29},
        "Sosisli Sandviç": {"kalori": 430, "protein": 15, "karb": 39, "yag": 25},
        "Arnavut Ciğeri": {"kalori": 410, "protein": 29, "karb": 18, "yag": 25},
        "Midye Dolma Tabağı": {"kalori": 390, "protein": 18, "karb": 54, "yag": 12},
        "Tavuk Şiş Dürüm": {"kalori": 450, "protein": 38, "karb": 42, "yag": 15},
        "Adana Dürüm": {"kalori": 590, "protein": 35, "karb": 44, "yag": 31},
        "Et Tantuni": {"kalori": 520, "protein": 32, "karb": 38, "yag": 28},
        "Tavuk Tantuni": {"kalori": 440, "protein": 34, "karb": 38, "yag": 16},
        "Çıtır Tavuk Dürüm": {"kalori": 520, "protein": 29, "karb": 52, "yag": 22},
        "Mısır (Haşlanmış veya Bardakta)": {"kalori": 180, "protein": 5, "karb": 38, "yag": 2.5}
    },
    "20. Dünya Mutfağı 🍱": {
        "California Roll": {"kalori": 360, "protein": 10, "karb": 50, "yag": 13},
        "Philadelphia Roll": {"kalori": 410, "protein": 13, "karb": 48, "yag": 18},
        "Somon Nigiri": {"kalori": 140, "protein": 8, "karb": 22, "yag": 2},
        "Karides Tempura Roll": {"kalori": 440, "protein": 14, "karb": 56, "yag": 18},
        "Sashimi": {"kalori": 120, "protein": 22, "karb": 0, "yag": 3},
        "Poke Bowl": {"kalori": 510, "protein": 32, "karb": 62, "yag": 14},
        "Ramen": {"kalori": 580, "protein": 24, "karb": 72, "yag": 22},
        "Udon": {"kalori": 520, "protein": 18, "karb": 82, "yag": 12},
        "Gyoza": {"kalori": 310, "protein": 14, "karb": 36, "yag": 12},
        "Bibimbap": {"kalori": 560, "protein": 28, "karb": 74, "yag": 16},
        "Meksika Taco": {"kalori": 320, "protein": 16, "karb": 28, "yag": 15},
        "Burrito Bowl": {"kalori": 590, "protein": 38, "karb": 72, "yag": 17},
        "Enchilada": {"kalori": 540, "protein": 32, "karb": 52, "yag": 22},
        "İtalyan Risotto": {"kalori": 480, "protein": 12, "karb": 66, "yag": 18},
        "Gnocchi": {"kalori": 450, "protein": 11, "karb": 72, "yag": 13},
        "Hint Butter Chicken": {"kalori": 610, "protein": 42, "karb": 22, "yag": 40},
        "Yunan Gyros": {"kalori": 550, "protein": 34, "karb": 46, "yag": 25},
        "Pad Thai": {"kalori": 590, "protein": 22, "karb": 78, "yag": 21},
        "Çin Usulü Tatlı Ekşi Tavuk": {"kalori": 540, "protein": 36, "karb": 64, "yag": 16},
        "Çin Usulü Sebzeli Noodle": {"kalori": 390, "protein": 10, "karb": 64, "yag": 10}
    },
    "21. Bowl ve Kase Menüler 🥣": {
        "Acai Bowl": {"kalori": 340, "protein": 6, "karb": 62, "yag": 8},
        "Protein Bowl": {"kalori": 520, "protein": 46, "karb": 50, "yag": 16},
        "Tavuklu Pirinç Kasesi": {"kalori": 480, "protein": 38, "karb": 56, "yag": 11},
        "Somonlu Bowl": {"kalori": 490, "protein": 34, "karb": 52, "yag": 17},
        "Meksika Bowl": {"kalori": 510, "protein": 32, "karb": 64, "yag": 14},
        "Teriyaki Bowl": {"kalori": 470, "protein": 36, "karb": 60, "yag": 10},
        "Falafel Bowl": {"kalori": 460, "protein": 16, "karb": 64, "yag": 15},
        "Sebzeli Kinoa Bowl": {"kalori": 390, "protein": 13, "karb": 58, "yag": 11},
        "Yoğurtlu Meyve Kasesi": {"kalori": 280, "protein": 12, "karb": 52, "yag": 4},
        "Granola Bowl": {"kalori": 380, "protein": 12, "karb": 58, "yag": 11},
        "Tavuklu Sezar Bowl": {"kalori": 440, "protein": 38, "karb": 28, "yag": 20},
        "Etli Noodle Bowl": {"kalori": 570, "protein": 38, "karb": 64, "yag": 18},
        "Avokadolu Bowl": {"kalori": 430, "protein": 11, "karb": 48, "yag": 22},
        "Ton Balıklı Bowl": {"kalori": 450, "protein": 34, "karb": 48, "yag": 13},
        "Nohutlu Akdeniz Bowl": {"kalori": 410, "protein": 15, "karb": 56, "yag": 14}
    },
    "22. Atıştırmalıklar 🥨": {
        "Enerji Topları": {"kalori": 210, "protein": 5, "karb": 28, "yag": 9},
        "Protein Bar": {"kalori": 220, "protein": 20, "karb": 22, "yag": 7},
        "Kuruyemiş Karışımı": {"kalori": 310, "protein": 10, "karb": 12, "yag": 26},
        "Pirinç Patlağı": {"kalori": 110, "protein": 2, "karb": 24, "yag": 1},
        "Peynir ve Kraker Tabağı": {"kalori": 340, "protein": 16, "karb": 30, "yag": 18},
        "Mini Sandviçler": {"kalori": 290, "protein": 12, "karb": 30, "yag": 13},
        "Mini Quesadilla": {"kalori": 320, "protein": 14, "karb": 28, "yag": 16},
        "Yoğurtlu Meyve Kasesi": {"kalori": 220, "protein": 10, "karb": 40, "yag": 3},
        "Fırınlanmış Nohut": {"kalori": 240, "protein": 12, "karb": 35, "yag": 6},
        "Sebze ve Dip Sos Tabağı": {"kalori": 160, "protein": 4, "karb": 18, "yag": 8},
        "Patlamış Mısır": {"kalori": 190, "protein": 3, "karb": 28, "yag": 8},
        "Tuzlu Kraker": {"kalori": 210, "protein": 4, "karb": 32, "yag": 7},
        "Grissini": {"kalori": 180, "protein": 5, "karb": 32, "yag": 3},
        "Mini Pizza Dilimleri": {"kalori": 310, "protein": 12, "karb": 35, "yag": 13},
        "Mini Tavuk Nugget": {"kalori": 280, "protein": 15, "karb": 18, "yag": 16},
        "Çıtır Peynir Topları": {"kalori": 360, "protein": 16, "karb": 24, "yag": 22},
        "Nachos ve Salsa": {"kalori": 320, "protein": 5, "karb": 46, "yag": 13},
        "Elma Dilimleri ve Fıstık Ezmesi": {"kalori": 290, "protein": 7, "karb": 32, "yag": 16},
        "Kuru Meyve Tabağı": {"kalori": 260, "protein": 3, "karb": 64, "yag": 1},
        "Humus ve Grissini": {"kalori": 290, "protein": 9, "karb": 38, "yag": 11},
        "Çikolatalı Pirinç Patlağı": {"kalori": 160, "protein": 3, "karb": 26, "yag": 5},
        "Mini Galeta": {"kalori": 170, "protein": 4, "karb": 30, "yag": 3},
        "Baharatlı Leblebi": {"kalori": 230, "protein": 14, "karb": 36, "yag": 4},
        "Meyve Cipsi": {"kalori": 190, "protein": 2, "karb": 44, "yag": 1},
        "Yoğurtlu Granola Kupası": {"kalori": 310, "protein": 11, "karb": 46, "yag": 9}
    },
    "23. Tatlılar 🍰": {
        "San Sebastian Cheesecake": {"kalori": 460, "protein": 8, "karb": 34, "yag": 32},
        "New York Cheesecake": {"kalori": 440, "protein": 7, "karb": 38, "yag": 29},
        "Çikolatalı Sufle": {"kalori": 390, "protein": 6, "karb": 48, "yag": 19},
        "Brownie": {"kalori": 420, "protein": 5, "karb": 54, "yag": 21},
        "Dondurmalı Brownie": {"kalori": 540, "protein": 7, "karb": 68, "yag": 27},
        "Tiramisu": {"kalori": 380, "protein": 7, "karb": 42, "yag": 20},
        "Profiterol": {"kalori": 360, "protein": 6, "karb": 44, "yag": 18},
        "Ekler": {"kalori": 310, "protein": 5, "karb": 38, "yag": 15},
        "Magnolia": {"kalori": 340, "protein": 8, "karb": 46, "yag": 14},
        "Çilekli Magnolia": {"kalori": 330, "protein": 8, "karb": 44, "yag": 13},
        "Oreolu Magnolia": {"kalori": 390, "protein": 7, "karb": 52, "yag": 17},
        "Waffle": {"kalori": 480, "protein": 8, "karb": 64, "yag": 21},
        "Çikolatalı Waffle": {"kalori": 540, "protein": 9, "karb": 72, "yag": 25},
        "Meyveli Waffle": {"kalori": 460, "protein": 8, "karb": 66, "yag": 18},
        "Krep": {"kalori": 270, "protein": 7, "karb": 36, "yag": 11},
        "Çikolatalı Krep": {"kalori": 360, "protein": 8, "karb": 48, "yag": 16},
        "Pancake": {"kalori": 310, "protein": 8, "karb": 45, "yag": 10},
        "Çikolatalı Fondan": {"kalori": 450, "protein": 6, "karb": 52, "yag": 24},
        "Karamelli Trileçe": {"kalori": 350, "protein": 9, "karb": 46, "yag": 14},
        "Fırın Sütlaç": {"kalori": 240, "protein": 6, "karb": 41, "yag": 5.5},
        "Kazandibi": {"kalori": 260, "protein": 6, "karb": 44, "yag": 6},
        "Tavukgöğsü": {"kalori": 230, "protein": 6, "karb": 38, "yag": 5},
        "Baklava": {"kalori": 410, "protein": 6, "karb": 52, "yag": 21},
        "Künefe": {"kalori": 480, "protein": 10, "karb": 54, "yag": 26},
        "Dondurma": {"kalori": 210, "protein": 4, "karb": 24, "yag": 11},
        "Çikolatalı Mousse": {"kalori": 340, "protein": 5, "karb": 36, "yag": 20},
        "Red Velvet Pasta": {"kalori": 460, "protein": 5, "karb": 58, "yag": 23},
        "Havuçlu Kek": {"kalori": 350, "protein": 5, "karb": 48, "yag": 16},
        "Limonlu Tart": {"kalori": 330, "protein": 4, "karb": 44, "yag": 16},
        "Meyveli Tart": {"kalori": 310, "protein": 4, "karb": 42, "yag": 14}
    },
    "24. Pastane Ürünleri 🥯": {
        "Kruvasan": {"kalori": 270, "protein": 5, "karb": 31, "yag": 14},
        "Çikolatalı Kruvasan": {"kalori": 340, "protein": 6, "karb": 38, "yag": 18},
        "Bademli Kruvasan": {"kalori": 410, "protein": 8, "karb": 42, "yag": 23},
        "Pain au Chocolat": {"kalori": 350, "protein": 6, "karb": 39, "yag": 19},
        "Tarçınlı Rulo": {"kalori": 380, "protein": 6, "karb": 56, "yag": 15},
        "Muffin": {"kalori": 340, "protein": 5, "karb": 48, "yag": 15},
        "Çikolatalı Muffin": {"kalori": 390, "protein": 6, "karb": 52, "yag": 18},
        "Donut": {"kalori": 310, "protein": 4, "karb": 36, "yag": 17},
        "Çikolatalı Donut": {"kalori": 370, "protein": 5, "karb": 44, "yag": 20},
        "Berliner": {"kalori": 330, "protein": 6, "karb": 42, "yag": 15},
        "Cookie": {"kalori": 260, "protein": 3, "karb": 34, "yag": 13},
        "Çikolata Parçacıklı Cookie": {"kalori": 290, "protein": 3, "karb": 38, "yag": 14},
        "Brownie Cookie": {"kalori": 320, "protein": 4, "karb": 42, "yag": 16},
        "Havuçlu Kek Dilimi": {"kalori": 350, "protein": 5, "karb": 48, "yag": 16},
        "Muzlu Ekmek": {"kalori": 290, "protein": 4, "karb": 44, "yag": 11},
        "Cheesecake Dilimi": {"kalori": 440, "protein": 7, "karb": 38, "yag": 29},
        "Elmalı Turta": {"kalori": 310, "protein": 3, "karb": 46, "yag": 13},
        "Poğaça": {"kalori": 320, "protein": 7, "karb": 36, "yag": 16},
        "Açma": {"kalori": 340, "protein": 6, "karb": 42, "yag": 16},
        "Tuzlu Kurabiye": {"kalori": 280, "protein": 5, "karb": 30, "yag": 15}
    },
    "25. Dondurmalar 🍨": {
        "Vanilyalı Dondurma": {"kalori": 210, "protein": 3.5, "karb": 24, "yag": 11},
        "Çikolatalı Dondurma": {"kalori": 230, "protein": 4, "karb": 28, "yag": 12},
        "Çilekli Dondurma": {"kalori": 200, "protein": 3, "karb": 25, "yag": 10},
        "Fıstıklı Dondurma": {"kalori": 250, "protein": 5, "karb": 26, "yag": 14},
        "Karamelli Dondurma": {"kalori": 240, "protein": 3.5, "karb": 30, "yag": 12},
        "Mango Sorbe": {"kalori": 140, "protein": 1, "karb": 34, "yag": 0.5},
        "Limon Sorbe": {"kalori": 130, "protein": 0.5, "karb": 32, "yag": 0.2},
        "Oreo Dondurma": {"kalori": 270, "protein": 4, "karb": 32, "yag": 14},
        "Cookie Dough Dondurma": {"kalori": 290, "protein": 4, "karb": 35, "yag": 15},
        "Karışık Dondurma Kasesi": {"kalori": 380, "protein": 7, "karb": 50, "yag": 18},
        "Çikolata Soslu Dondurma": {"kalori": 310, "protein": 5, "karb": 40, "yag": 15},
        "Meyveli Dondurma Kasesi": {"kalori": 280, "protein": 4, "karb": 44, "yag": 10}
    },
    "26. Soğuk İçecekler 🧋": {
        "Su": {"kalori": 0, "protein": 0, "karb": 0, "yag": 0},
        "Maden Suyu": {"kalori": 0, "protein": 0, "karb": 0, "yag": 0},
        "Ayran": {"kalori": 75, "protein": 4, "karb": 5, "yag": 4},
        "Limonata": {"kalori": 110, "protein": 0.2, "karb": 28, "yag": 0.1},
        "Çilekli Limonata": {"kalori": 130, "protein": 0.4, "karb": 32, "yag": 0.2},
        "Naneli Limonata": {"kalori": 115, "protein": 0.3, "karb": 29, "yag": 0.1},
        "Ev Yapımı Soğuk Çay": {"kalori": 90, "protein": 0, "karb": 22, "yag": 0},
        "Şeftalili Ice Tea": {"kalori": 100, "protein": 0, "karb": 25, "yag": 0},
        "Limonlu Ice Tea": {"kalori": 95, "protein": 0, "karb": 24, "yag": 0},
        "Kola": {"kalori": 140, "protein": 0, "karb": 38, "yag": 0},
        "Şekersiz Kola": {"kalori": 1, "protein": 0, "karb": 0, "yag": 0},
        "Fanta": {"kalori": 160, "protein": 0, "karb": 40, "yag": 0},
        "Sprite": {"kalori": 140, "protein": 0, "karb": 36, "yag": 0},
        "Soğuk Kahve": {"kalori": 110, "protein": 4, "karb": 16, "yag": 3.5},
        "Iced Latte": {"kalori": 120, "protein": 6, "karb": 12, "yag": 4.8},
        "Iced Americano": {"kalori": 10, "protein": 0.5, "karb": 2, "yag": 0},
        "Iced Mocha": {"kalori": 240, "protein": 7, "karb": 32, "yag": 9},
        "Frappuccino": {"kalori": 320, "protein": 6, "karb": 52, "yag": 10},
        "Milkshake": {"kalori": 410, "protein": 11, "karb": 64, "yag": 13},
        "Çilekli Milkshake": {"kalori": 420, "protein": 10, "karb": 68, "yag": 12},
        "Çikolatalı Milkshake": {"kalori": 460, "protein": 12, "karb": 72, "yag": 15},
        "Muzlu Milkshake": {"kalori": 440, "protein": 11, "karb": 70, "yag": 13},
        "Meyveli Smoothie": {"kalori": 210, "protein": 3, "karb": 48, "yag": 1.5},
        "Mango Smoothie": {"kalori": 230, "protein": 2, "karb": 54, "yag": 1},
        "Çilekli Smoothie": {"kalori": 200, "protein": 3, "karb": 46, "yag": 1}
    },
    "27. Sıcak İçecekler ☕": {
        "Türk Kahvesi": {"kalori": 7, "protein": 0.3, "karb": 0.9, "yag": 0.2},
        "Espresso": {"kalori": 5, "protein": 0.2, "karb": 1, "yag": 0.1},
        "Americano": {"kalori": 10, "protein": 0.5, "karb": 2, "yag": 0},
        "Latte": {"kalori": 150, "protein": 8, "karb": 14, "yag": 6},
        "Cappuccino": {"kalori": 120, "protein": 7, "karb": 11, "yag": 5},
        "Flat White": {"kalori": 160, "protein": 9, "karb": 15, "yag": 6.5},
        "Mocha": {"kalori": 290, "protein": 9, "karb": 36, "yag": 12},
        "Filtre Kahve": {"kalori": 5, "protein": 0.3, "karb": 1, "yag": 0},
        "Sütlü Filtre Kahve": {"kalori": 60, "protein": 3, "karb": 5, "yag": 3},
        "Sıcak Çikolata": {"kalori": 280, "protein": 8, "karb": 38, "yag": 11},
        "Beyaz Sıcak Çikolata": {"kalori": 310, "protein": 7, "karb": 42, "yag": 13},
        "Chai Latte": {"kalori": 220, "protein": 6, "karb": 38, "yag": 5},
        "Matcha Latte": {"kalori": 180, "protein": 7, "karb": 24, "yag": 6},
        "Salep": {"kalori": 240, "protein": 6, "karb": 40, "yag": 6},
        "Siyah Çay": {"kalori": 2, "protein": 0, "karb": 0.5, "yag": 0},
        "Yeşil Çay": {"kalori": 2, "protein": 0, "karb": 0.5, "yag": 0},
        "Papatya Çayı": {"kalori": 2, "protein": 0, "karb": 0.5, "yag": 0},
        "Nane-Limon": {"kalori": 15, "protein": 0.1, "karb": 3, "yag": 0},
        "Adaçayı": {"kalori": 2, "protein": 0, "karb": 0.5, "yag": 0},
        "Zencefilli Bitki Çayı": {"kalori": 10, "protein": 0.2, "karb": 2, "yag": 0}
    },
    "28. Soslar ve Ekstralar 🥫": {
        "Ketçap": {"kalori": 20, "protein": 0.2, "karb": 5, "yag": 0.1},
        "Mayonez": {"kalori": 100, "protein": 0.1, "karb": 1, "yag": 11},
        "Sarımsaklı Mayonez": {"kalori": 110, "protein": 0.2, "karb": 1.5, "yag": 12},
        "Barbekü Sos": {"kalori": 30, "protein": 0.2, "karb": 7, "yag": 0.2},
        "Ranch Sos": {"kalori": 130, "protein": 1, "karb": 2, "yag": 13},
        "Sezar Sos": {"kalori": 140, "protein": 1, "karb": 1.5, "yag": 14},
        "Acı Sos": {"kalori": 10, "protein": 0.2, "karb": 2, "yag": 0.1},
        "Sweet Chili Sos": {"kalori": 45, "protein": 0.1, "karb": 11, "yag": 0.1},
        "Ballı Hardal": {"kalori": 60, "protein": 0.5, "karb": 8, "yag": 3},
        "Hardal": {"kalori": 15, "protein": 1, "karb": 1, "yag": 1},
        "Cheddar Sos": {"kalori": 90, "protein": 3, "karb": 2, "yag": 8},
        "Pesto Sos": {"kalori": 120, "protein": 2, "karb": 1, "yag": 12},
        "Trüf Mayonez": {"kalori": 130, "protein": 0.2, "karb": 1, "yag": 14},
        "Yoğurtlu Sos": {"kalori": 50, "protein": 3, "karb": 3, "yag": 3},
        "Parmesan Ekstrası": {"kalori": 110, "protein": 10, "karb": 1, "yag": 7},
        "Ekstra Cheddar": {"kalori": 115, "protein": 7, "karb": 0.5, "yag": 9.5},
        "Avokado Ekstrası": {"kalori": 80, "protein": 1, "karb": 4, "yag": 7},
        "Jalapeño": {"kalori": 5, "protein": 0.2, "karb": 1, "yag": 0},
        "Turşu": {"kalori": 10, "protein": 0.3, "karb": 2, "yag": 0.1},
        "Ekstra Patates": {"kalori": 180, "protein": 2, "karb": 22, "yag": 9}
    },
    "29. Menü Kombinasyonları 🎁": {
        "Burger + Patates + İçecek": {"kalori": 880, "protein": 32, "karb": 92, "yag": 45},
        "Tavuk Burger + Patates + İçecek": {"kalori": 790, "protein": 34, "karb": 102, "yag": 32},
        "Pizza + İçecek": {"kalori": 900, "protein": 29, "karb": 136, "yag": 27},
        "Sandviç + Patates + İçecek": {"kalori": 710, "protein": 19, "karb": 84, "yag": 34},
        "Wrap + Patates + İçecek": {"kalori": 760, "protein": 34, "karb": 94, "yag": 31},
        "Tavuk Nugget + Patates + İçecek": {"kalori": 810, "protein": 20, "karb": 102, "yag": 37},
        "Tavuk Kanat + Patates + İçecek": {"kalori": 910, "protein": 39, "karb": 79, "yag": 58},
        "Makarna + İçecek": {"kalori": 720, "protein": 26, "karb": 114, "yag": 20},
        "Salata + İçecek": {"kalori": 390, "protein": 32, "karb": 24, "yag": 22},
        "Kahvaltı Tabağı + Sıcak İçecek": {"kalori": 570, "protein": 26, "karb": 49, "yag": 28},
        "Kruvasan + Latte": {"kalori": 420, "protein": 13, "karb": 45, "yag": 20},
        "Waffle + Kahve": {"kalori": 487, "protein": 8, "karb": 65, "yag": 21},
        "Cheesecake + Americano": {"kalori": 470, "protein": 8, "karb": 36, "yag": 32},
        "Brownie + Dondurma": {"kalori": 630, "protein": 9, "karb": 78, "yag": 32},
        "Pancake + Smoothie": {"kalori": 520, "protein": 11, "karb": 93, "yag": 11.5},
        "Gözleme + Ayran": {"kalori": 495, "protein": 22, "karb": 59, "yag": 19},
        "Lahmacun + Ayran": {"kalori": 315, "protein": 15, "karb": 35, "yag": 12},
        "Döner Dürüm + Patates + İçecek": {"kalori": 880, "protein": 38, "karb": 110, "yag": 43},
        "Pilav + Tavuk + Ayran": {"kalori": 615, "protein": 33, "karb": 67, "yag": 22.5},
        "Börek Tabağı + Çay": {"kalori": 342, "protein": 12, "karb": 36, "yag": 16}
    }
}

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

def verileri_yukle(username):
    user_file = kullanici_veri_dosyasi(username)
    default_data = {
        "besin_veritabani": {}, "hazir_tarifler": {}, "gunluk_kayitlar": [], "aktivite_loglari": {},
        "profil": {"cinsiyet": "Kadın", "yas": 20, "boy": 165, "mevcut_kilo": 58.0, "hedef_kilo": 55.0, "tema": "Sonbahar Kremi", "setup_tamamlandi": False}
    }
    if os.path.exists(user_file):
        try:
            with open(user_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                profil = data.get("profil", {})
                for k, v in default_data["profil"].items():
                    if k not in profil: profil[k] = v
                data["profil"] = profil
                return data
        except: return default_data
    return default_data

def verileri_kaydet(username):
    data = {
        "besin_veritabani": st.session_state.besin_veritabani,
        "hazir_tarifler": st.session_state.hazir_tarifler,
        "gunluk_kayitlar": st.session_state.gunluk_kayitlar,
        "aktivite_loglari": st.session_state.aktivite_loglari,
        "profil": st.session_state.profil
    }
    with open(kullanici_veri_dosyasi(username), "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

def hesapla_bmr(p):
    return (10 * float(p["mevcut_kilo"])) + (6.25 * float(p["boy"])) - (5 * int(p["yas"])) - 161

# ----------------------------------------------------
# 4. OTURUM VE GİRİŞ
# ----------------------------------------------------
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "aktif_kullanici" not in st.session_state: st.session_state.aktif_kullanici = ""
if "onboarding_adim" not in st.session_state: st.session_state.onboarding_adim = 1
if "sayfa_gorunumu" not in st.session_state: st.session_state.sayfa_gorunumu = "ana_sayfa" # ana_sayfa veya hesap

if not st.session_state.giris_yapildi:
    st.markdown(f'<div style="max-width: 600px; margin: 40px auto 20px auto;">{LOGO_MAIN}<p style="text-align: center; font-style: italic; opacity: 0.8; font-size: 15px;">Kendi en büyüleyici versiyonunu baştan yarat.</p></div>', unsafe_allow_html=True)
    tab_giris, tab_kayit = st.tabs(["Giriş Yap", "Yeni Hesap Oluştur"])
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
            else: st.error("Kullanıcı adı veya şifre hatalı!")

    with tab_kayit:
        k_user = st.text_input("Yeni Kullanıcı Adı", key="k_user").strip().lower()
        k_pass = st.text_input("Şifre Oluştur", type="password", key="k_pass")
        if st.button("Kayıt Ol", use_container_width=True):
            if k_user and k_pass:
                users[k_user] = sifre_hashle(k_pass)
                kullanicilari_kaydet(users)
                st.success("Hesap oluşturuldu! Giriş yapabilirsiniz.")

else:
    aktif_user = st.session_state.aktif_kullanici
    p = st.session_state.profil
    bmr_kisi = hesapla_bmr(p)

    # ÜST KISIM: LOGO AMBLEM (PROFİLE GEÇİŞ) VE ÇIKIŞ
    top_col1, top_col2, top_col3 = st.columns([6, 2, 2])
    top_col1.markdown(f"### ✨ {aktif_user.title()}")
    
    # Sağ üst köşede daire amblem butonu
    with top_col2:
        if st.button("🦢 Profil / Hesap", use_container_width=True):
            st.session_state.sayfa_gorunumu = "hesap" if st.session_state.sayfa_gorunumu == "ana_sayfa" else "ana_sayfa"
            st.rerun()
            
    if top_col3.button("Çıkış Yap"):
        st.session_state.giris_yapildi = False
        st.rerun()

    # ----------------------------------------------------
    # 5. İNTERAKTİF ONBOARDING EĞİTİM REHBERİ
    # ----------------------------------------------------
    if not p.get("setup_tamamlandi", False):
        o_adim = st.session_state.onboarding_adim
        if o_adim == 1:
            st.markdown("""
                <div class="onboarding-box">
                    <h3>1️⃣ Adım ve Su Takibi</h3>
                    <p>Aşağıda bulacağın kartlardan günlük adımlarını ve su tüketimini kolayca güncelleyebilir, kalori dengeni anlık takip edebilirsin.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Anladım, Devam Et ➔"):
                st.session_state.onboarding_adim = 2
                st.rerun()
        elif o_adim == 2:
            st.markdown("""
                <div class="onboarding-box">
                    <h3>2️⃣ Cal AI Tarzı Yapay Zeka Öğün Analizi ve Devasa Menü</h3>
                    <p>Yemeğinin fotoğrafını yükleyerek alt sınır analizi yapabilir veya 29 kategorilik restoran menümüzden dilediğin lezzeti günlüğüne ekleyebilirsin.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Anladım, Uygulamayı Keşfet ➔"):
                st.session_state.profil["setup_tamamlandi"] = True
                verileri_kaydet(aktif_user)
                st.rerun()
        st.stop()

    # ----------------------------------------------------
    # 6. HESAP VE HEDEFLER EKRANI (AMBLEME BASINCA AÇILAN KISIM)
    # ----------------------------------------------------
    if st.session_state.sayfa_gorunumu == "hesap":
        st.header("👤 Hesap, Hedefler ve Tema Ayarları")
        
        secilen_tema = st.selectbox("Uygulama Tema Paleti", ["Sonbahar Kremi", "Sıcak Kahve & Toprak", "Gece / Kuğu Mavisi", "Zeytin Yeşili & Doğa", "Karamel Esintisi"], index=0)

        c1, c2, c3 = st.columns(3)
        cinsiyet = c1.selectbox("Cinsiyet", ["Kadın", "Erkek"], index=0 if p["cinsiyet"] == "Kadın" else 1)
        yas = c2.number_input("Yaş", min_value=15, max_value=80, value=int(p["yas"]))
        boy = c3.number_input("Boy (cm)", min_value=120, max_value=210, value=int(p["boy"]))

        c4, c5 = st.columns(2)
        mevcut_kilo = c4.number_input("Mevcut Kilon (kg)", min_value=35.0, value=float(p["mevcut_kilo"]), step=0.5)
        hedef_kilo = c5.number_input("Hedeflenen Kilon (kg)", min_value=30.0, value=float(p["hedef_kilo"]), step=0.5)

        if st.button("Değişiklikleri Kaydet ve Ana Sayfaya Dön", use_container_width=True):
            st.session_state.profil.update({
                "cinsiyet": cinsiyet, "yas": yas, "boy": boy, "mevcut_kilo": mevcut_kilo, "hedef_kilo": hedef_kilo,
                "tema": secilen_tema, "setup_tamamlandi": True
            })
            verileri_kaydet(aktif_user)
            st.session_state.sayfa_gorunumu = "ana_sayfa"
            st.success("✨ Bilgileriniz güncellendi!")
            st.rerun()
            
        if st.button("← Ana Sayfaya Geri Dön"):
            st.session_state.sayfa_gorunumu = "ana_sayfa"
            st.rerun()

    # ----------------------------------------------------
    # 7. APPLE / CAL AI TARZI AKICI TEK SAYFA KAYAN ANA EKRAN
    # ----------------------------------------------------
    else:
        st.markdown(f"<h1 style='text-align: center; margin-top: 10px;'>Nova Yaşam Paneli</h1>", unsafe_allow_html=True)
        
        secilen_tarih = str(st.date_input("Kayıt Tarihi Seç", datetime.date.today()))
        if secilen_tarih not in st.session_state.aktivite_loglari:
            st.session_state.aktivite_loglari[secilen_tarih] = {"adim": 0, "su": 0.0}
        curr_aktivite = st.session_state.aktivite_loglari[secilen_tarih]

        # --- KART 1: SU VE ADIM TAKİBİ ---
        st.markdown("### 💧 Günlük Aktivite ve Hidrasyon")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
                <div class="apple-feature-card">
                    <div class="apple-title">Günlük Adım</div>
                    <div class="apple-desc">Şu anki adımın: <b>{curr_aktivite['adim']}</b> adım.</div>
                </div>
            """, unsafe_allow_html=True)
            yeni_adim = st.number_input("Adım Güncelle", min_value=0, max_value=50000, value=int(curr_aktivite["adim"]), step=500)
            if st.button("Adımı Kaydet"):
                curr_aktivite["adim"] = yeni_adim
                verileri_kaydet(aktif_user)
                st.rerun()

        with c2:
            st.markdown(f"""
                <div class="apple-feature-card">
                    <div class="apple-title">Su Tüketimi</div>
                    <div class="apple-desc">Bugünkü su: <b>{curr_aktivite['su']:.2f} L</b>.</div>
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

        st.markdown("---")

        # --- KART 2: YAPAY ZEKA ÖĞÜN ANALİZİ ---
        st.markdown("### 📸 Yapay Zeka ile Öğün Analizi")
        st.markdown("""
            <div class="apple-feature-card">
                <div class="apple-title">Track Your Food With Just a Picture</div>
                <div class="apple-desc">Yemeğinin fotoğrafını yükle; yapay zeka güvenli alt sınır değerlerini çıkarsın.</div>
            </div>
        """, unsafe_allow_html=True)

        upl = st.file_uploader("Yemek Fotoğrafı Yükle", type=["jpg", "jpeg", "png"])
        if upl:
            image = Image.open(upl)
            st.image(image, caption="Yüklenen Yemek", width=280)
            ogun_turu = st.selectbox("Öğün Seç", ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"])
            
            if st.button("✨ Fotoğrafı Analiz Et ve Alt Sınır Hesapla"):
                with st.spinner("Yapay zeka yemeği inceliyor..."):
                    try:
                        bytes_data = upl.getvalue()
                        files = {"file": ("yemek.jpg", bytes_data, "image/jpeg")}
                        res = requests.post("http://127.0.0.1:8000/api/tara", files=files)
                        if res.status_code == 200:
                            ham_metin = res.json().get("veri", "Analiz tamamlandı.")
                            st.session_state["ai_sonuc"] = {
                                "tarife": "Yapay Zeka Analizli Yemek",
                                "kalori": 350.0, "protein": 15.0, "karb": 30.0, "yag": 10.0, "metin": ham_metin
                            }
                        else: st.error("Sunucu yanıt vermedi.")
                    except Exception as e: st.error(f"Bağlantı hatası: {e}")

            if "ai_sonuc" in st.session_state and st.session_state["ai_sonuc"]:
                r = st.session_state["ai_sonuc"]
                st.info(f"**AI Raporu:**\n\n{r['metin']}")
                ed_isim = st.text_input("Yemek Adı", value=r["tarife"])
                ed_kal = st.number_input("Kalori (kcal)", value=float(r["kalori"]))
                ed_pro = st.number_input("Protein (g)", value=float(r["protein"]))
                ed_karb = st.number_input("Karbonhidrat (g)", value=float(r["karb"]))
                ed_yag = st.number_input("Yağ (g)", value=float(r["yag"]))

                if st.button("✅ Günlüğe Kaydet"):
                    st.session_state.gunluk_kayitlar.append({
                        "Tarih": secilen_tarih, "Öğün": ogun_turu, "Tarif": ed_isim + " (AI)",
                        "Kalori": ed_kal, "Protein": ed_pro, "Karbonhidrat": ed_karb, "Yağ": ed_yag
                    })
                    verileri_kaydet(aktif_user)
                    del st.session_state["ai_sonuc"]
                    st.success("Öğün başarıyla eklendi!")
                    st.rerun()

        st.markdown("---")

        # --- KART 3: 29 KATEGORİLİ DEVASA RESTORAN MENÜSÜ ---
        st.markdown("### 🍽️ 29 Kategorili Devasa Restoran Menüsü")
        m_kat = st.selectbox("Menü Kategorisi Seç", list(DEVASA_MENU.keys()))
        m_yemek = st.selectbox("Yemek Seç", list(DEVASA_MENU[m_kat].keys()))
        detay = DEVASA_MENU[m_kat][m_yemek]
        
        st.markdown(f"**Değerler:** {detay['kalori']} kcal | Protein: {detay['protein']}g | Karb: {detay['karb']}g | Yağ: {detay['yag']}g")
        
        if st.button("Menüden Seçilen Yemeği Ekle"):
            st.session_state.gunluk_kayitlar.append({
                "Tarih": secilen_tarih, "Öğün": "Ana Öğün", "Tarif": m_yemek,
                "Kalori": detay["kalori"], "Protein": detay["protein"], "Karbonhidrat": detay["karb"], "Yağ": detay["yag"]
            })
            verileri_kaydet(aktif_user)
            st.success(f"{m_yemek} günlüğe eklendi!")
            st.rerun()

        st.markdown("---")

        # --- KART 4: YENİ TARİF / MALZEME EKLEME ---
        st.markdown("### 🧑‍🍳 Yeni Tarif veya Malzeme Ekle")
        yeni_tarif_adi = st.text_input("Tarif/Malzeme Adı")
        yt_kal = st.number_input("Kalori (kcal)", min_value=0.0, value=200.0)
        yt_pro = st.number_input("Protein (g)", min_value=0.0, value=10.0)
        yt_karb = st.number_input("Karbonhidrat (g)", min_value=0.0, value=20.0)
        yt_yag = st.number_input("Yağ (g)", min_value=0.0, value=5.0)
        
        if st.button("Özel Tarifi Kaydet ve Ekle"):
            if yeni_tarif_adi.strip():
                st.session_state.gunluk_kayitlar.append({
                    "Tarih": secilen_tarih, "Öğün": "Özel Tarif", "Tarif": yeni_tarif_adi.strip(),
                    "Kalori": yt_kal, "Protein": yt_pro, "Karbonhidrat": yt_karb, "Yağ": yt_yag
                })
                verileri_kaydet(aktif_user)
                st.success("Özel tarif başarıyla eklendi!")
                st.rerun()

        st.markdown("---")

        # --- KART 5: HAFTALIK PROGRAM VE GEÇMİŞ DEĞERLENDİRME ---
        st.markdown("### 📈 Haftalık Program & Değerlendirme")
        if st.session_state.gunluk_kayitlar:
            df_tum = pd.DataFrame(st.session_state.gunluk_kayitlar)
            haftalik_ozet = df_tum.groupby("Tarih")[["Kalori", "Protein", "Karbonhidrat", "Yağ"]].sum().reset_index()
            st.line_chart(haftalik_ozet.set_index("Tarih")[["Kalori"]], color=t["accent"])
            st.dataframe(haftalik_ozet, use_container_width=True)
        else:
            st.info("Henüz geçmiş kayıt bulunmuyor.")

        st.markdown("---")

        # --- KART 6: GÜNLÜK ÖZET VE SİLME ---
        st.markdown(f"### 📋 {secilen_tarih} Tarihli Öğünler")
        bugun_og = [(i, k) for i, k in enumerate(st.session_state.gunluk_kayitlar) if k["Tarih"] == secilen_tarih]
        toplam_alinan = 0
        
        if bugun_og:
            for i, kayit in bugun_og:
                toplam_alinan += kayit["Kalori"]
                cr1, cr2 = st.columns([10, 1])
                cr1.markdown(f"**{kayit['Öğün']}**: {kayit['Tarif']} <span style='color:{t['accent']};'>({kayit['Kalori']} kcal | P:{kayit.get('Protein',0)}g)</span>", unsafe_allow_html=True)
                if cr2.button("🗑️", key=f"sil_{i}"):
                    st.session_state.gunluk_kayitlar.pop(i)
                    verileri_kaydet(aktif_user)
                    st.rerun()
        else: st.info("Bu tarihte henüz yediğiniz bir şey kaydedilmedi.")

        st.markdown("---")

        st.markdown("### 📊 Günlük Özet")
        adim_kal = curr_aktivite["adim"] * 0.04
        toplam_harcanan = bmr_kisi + adim_kal
        net_acik = toplam_harcanan - toplam_alinan

        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Harcanan", f"{round(toplam_harcanan)} kcal")
        col_s2.metric("Alınan", f"{round(toplam_alinan)} kcal")
        col_s3.metric("Net Açık", f"{round(net_acik)} kcal")
