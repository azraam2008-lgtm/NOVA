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
# 2. CAL AI TARZI PROFESYONEL, FERAH VE BÜYÜK KART TASARIMI (CSS)
# ----------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    .stApp { background-color: #f8f9fa; color: #111111; font-family: 'Plus Jakarta Sans', sans-serif; }
    h1, h2, h3, h4 { color: #111111 !important; font-weight: 700 !important; }
    
    [data-testid="stSidebar"] { display: none; }
    
    .calai-section-card {
        background: #ffffff;
        border: 1px solid #e5e5ea;
        border-radius: 24px;
        padding: 32px;
        margin-bottom: 28px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.03);
    }
    .calai-title {
        font-size: 22px;
        font-weight: 700;
        color: #111111;
        margin-bottom: 8px;
    }
    .calai-desc {
        font-size: 15px;
        color: #666666;
        line-height: 1.5;
        margin-bottom: 20px;
    }
    .stButton > button {
        background-color: #111111;
        color: #ffffff;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        padding: 10px 20px;
        transition: 0.2s;
    }
    .stButton > button:hover {
        background-color: #333333;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

USERS_FILE = "kullanicilar.json"

# Hiçbir şeyin eksiltilmediği tam kadro devasa lezzet kataloğu
ZENGIN_LEZZET_KATALOGU = {
    "Kahvaltılıklar 🥐": {
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
    "Çorbalar 🍲": {
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
    "Ara Sıcaklar 🧀": {
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
        "Mini Pizza": {"kalori": 320, "protein": 13, "karb": 36, "yag": 14}
    },
    "Salatalar 🥗": {
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
    "Sandviçler ve Wrapler 🥪": {
        "Kaşarlı Sandviç": {"kalori": 340, "protein": 15, "karb": 32, "yag": 17},
        "Karışık Sandviç": {"kalori": 370, "protein": 18, "karb": 33, "yag": 19},
        "Beyaz Peynirli Sandviç": {"kalori": 300, "protein": 13, "karb": 34, "yag": 12},
        "Hindi Fümeli Sandviç": {"kalori": 290, "protein": 20, "karb": 32, "yag": 9},
        "Tavuklu Sandviç": {"kalori": 350, "protein": 26, "karb": 33, "yag": 13},
        "Ton Balıklı Sandviç": {"kalori": 330, "protein": 24, "karb": 31, "yag": 12},
        "Club Sandwich": {"kalori": 520, "protein": 28, "karb": 46, "yag": 26},
        "Tavuklu Wrap": {"kalori": 420, "protein": 30, "karb": 42, "yag": 14},
        "Çıtır Tavuk Wrap": {"kalori": 510, "protein": 28, "karb": 52, "yag": 22},
        "Etli Wrap": {"kalori": 480, "protein": 32, "karb": 44, "yag": 19},
        "Köfteli Wrap": {"kalori": 490, "protein": 29, "karb": 46, "yag": 21},
        "Ton Balıklı Wrap": {"kalori": 410, "protein": 27, "karb": 40, "yag": 16},
        "Falafel Wrap": {"kalori": 430, "protein": 15, "karb": 54, "yag": 17},
        "Avokadolu Wrap": {"kalori": 400, "protein": 12, "karb": 44, "yag": 20},
        "Burrito Wrap": {"kalori": 540, "protein": 34, "karb": 60, "yag": 18}
    },
    "Burgerler 🍔": {
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
        "Mexican Burger": {"kalori": 660, "protein": 36, "karb": 48, "yag": 34},
        "Bacon Burger": {"kalori": 690, "protein": 38, "karb": 43, "yag": 40},
        "Avokadolu Burger": {"kalori": 630, "protein": 31, "karb": 46, "yag": 35},
        "Vegan Burger": {"kalori": 440, "protein": 18, "karb": 54, "yag": 16},
        "Mini Burger Tabağı": {"kalori": 720, "protein": 42, "karb": 64, "yag": 34}
    },
    "Pizzalar 🍕": {
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
        "Meksika Pizza": {"kalori": 910, "protein": 41, "karb": 106, "yag": 36},
        "Hawaii Pizza": {"kalori": 830, "protein": 33, "karb": 108, "yag": 29},
        "Burrata Pizza": {"kalori": 940, "protein": 43, "karb": 98, "yag": 41},
        "Calzone": {"kalori": 980, "protein": 46, "karb": 112, "yag": 38}
    },
    "Makarnalar 🍝": {
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
        "Deniz Mahsullü Makarna": {"kalori": 610, "protein": 38, "karb": 74, "yag": 18},
        "Karidesli Linguine": {"kalori": 590, "protein": 36, "karb": 75, "yag": 16},
        "Kıymalı Fırın Makarna": {"kalori": 650, "protein": 30, "karb": 72, "yag": 27},
        "Ton Balıklı Makarna": {"kalori": 610, "protein": 38, "karb": 76, "yag": 16}
    },
    "Ana Yemekler 🍽️": {
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
        "Tavuklu Noodle": {"kalori": 510, "protein": 34, "karb": 60, "yag": 15},
        "Etli Noodle": {"kalori": 550, "protein": 36, "karb": 61, "yag": 18},
        "Izgara Hellim Tabağı": {"kalori": 460, "protein": 24, "karb": 4, "yag": 38}
    },
    "Geleneksel Türk Yemekleri 🥘": {
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
    "Pilavlar ve Börekler 🍚": {
        "Sade Pirinç Pilavı": {"kalori": 210, "protein": 3.5, "karb": 44, "yag": 2.5},
        "Tereyağlı Pirinç Pilavı": {"kalori": 250, "protein": 4, "karb": 42, "yag": 7},
        "Tavuklu Pilav": {"kalori": 360, "protein": 22, "karb": 44, "yag": 11},
        "Bulgur Pilavı": {"kalori": 170, "protein": 5.5, "karb": 34, "yag": 2},
        "Mantarlı Risotto": {"kalori": 460, "protein": 11, "karb": 68, "yag": 15},
        "Su Böreği": {"kalori": 340, "protein": 12, "karb": 36, "yag": 16},
        "Kol Böreği": {"kalori": 360, "protein": 10, "karb": 38, "yag": 19},
        "Sigara Böreği": {"kalori": 290, "protein": 9, "karb": 26, "yag": 17},
        "Paçanga Böreği": {"kalori": 350, "protein": 14, "karb": 28, "yag": 20},
        "Kıymalı Börek": {"kalori": 370, "protein": 15, "karb": 36, "yag": 19},
        "Peynirli Börek": {"kalori": 320, "protein": 11, "karb": 32, "yag": 16},
        "Ispanaklı Börek": {"kalori": 280, "protein": 8, "karb": 34, "yag": 12},
        "Peynirli Gözleme": {"kalori": 420, "protein": 18, "karb": 54, "yag": 15},
        "Kaşarlı Gözleme": {"kalori": 460, "protein": 20, "karb": 54, "yag": 19},
        "Patatesli Gözleme": {"kalori": 400, "protein": 10, "karb": 64, "yag": 11},
        "Kıymalı Gözleme": {"kalori": 470, "protein": 24, "karb": 55, "yag": 18}
    },
    "Sokak Lezzetleri ve Fast Food 🌮": {
        "Islak Hamburger": {"kalori": 440, "protein": 20, "karb": 42, "yag": 22},
        "Kumpir": {"kalori": 610, "protein": 19, "karb": 78, "yag": 26},
        "Kokoreç": {"kalori": 590, "protein": 32, "karb": 24, "yag": 41},
        "Midye Dolma": {"kalori": 65, "protein": 3, "karb": 9, "yag": 2},
        "Tantuni": {"kalori": 490, "protein": 30, "karb": 38, "yag": 25},
        "Et Döner Dürüm": {"kalori": 540, "protein": 34, "karb": 44, "yag": 26},
        "Tavuk Döner Dürüm": {"kalori": 460, "protein": 35, "karb": 43, "yag": 16},
        "Balık Ekmek": {"kalori": 480, "protein": 28, "karb": 52, "yag": 18},
        "Kumru": {"kalori": 590, "protein": 26, "karb": 54, "yag": 31},
        "Ayvalık Tostu": {"kalori": 620, "protein": 28, "karb": 52, "yag": 34},
        "Tavuk Nugget Menü": {"kalori": 680, "protein": 28, "karb": 75, "yag": 30},
        "Tavuk Kanat": {"kalori": 550, "protein": 35, "karb": 12, "yag": 40},
        "Fish and Chips": {"kalori": 760, "protein": 32, "karb": 76, "yag": 36},
        "Quesadilla": {"kalori": 580, "protein": 30, "karb": 48, "yag": 30},
        "Burrito": {"kalori": 710, "protein": 42, "karb": 78, "yag": 24}
    },
    "Tatlılar ve Pastane 🍰": {
        "San Sebastian Cheesecake": {"kalori": 460, "protein": 8, "karb": 34, "yag": 32},
        "New York Cheesecake": {"kalori": 440, "protein": 7, "karb": 38, "yag": 29},
        "Çikolatalı Sufle": {"kalori": 390, "protein": 6, "karb": 48, "yag": 19},
        "Brownie": {"kalori": 420, "protein": 5, "karb": 54, "yag": 21},
        "Dondurmalı Brownie": {"kalori": 540, "protein": 7, "karb": 68, "yag": 27},
        "Tiramisu": {"kalori": 380, "protein": 7, "karb": 42, "yag": 20},
        "Profiterol": {"kalori": 360, "protein": 6, "karb": 44, "yag": 18},
        "Ekler": {"kalori": 310, "protein": 5, "karb": 38, "yag": 15},
        "Magnolia": {"kalori": 340, "protein": 8, "karb": 46, "yag": 14},
        "Waffle": {"kalori": 480, "protein": 8, "karb": 64, "yag": 21},
        "Karamelli Trileçe": {"kalori": 350, "protein": 9, "karb": 46, "yag": 14},
        "Fırın Sütlaç": {"kalori": 240, "protein": 6, "karb": 41, "yag": 5.5},
        "Baklava": {"kalori": 410, "protein": 6, "karb": 52, "yag": 21},
        "Künefe": {"kalori": 480, "protein": 10, "karb": 54, "yag": 26},
        "Dondurma": {"kalori": 210, "protein": 4, "karb": 24, "yag": 11},
        "Kruvasan": {"kalori": 270, "protein": 5, "karb": 31, "yag": 14},
        "Tarçınlı Rulo": {"kalori": 380, "protein": 6, "karb": 56, "yag": 15},
        "Muffin": {"kalori": 340, "protein": 5, "karb": 48, "yag": 15},
        "Donut": {"kalori": 310, "protein": 4, "karb": 36, "yag": 17},
        "Cookie": {"kalori": 260, "protein": 3, "karb": 34, "yag": 13}
    },
    "İçecekler ☕": {
        "Su": {"kalori": 0, "protein": 0, "karb": 0, "yag": 0},
        "Maden Suyu": {"kalori": 0, "protein": 0, "karb": 0, "yag": 0},
        "Ayran": {"kalori": 75, "protein": 4, "karb": 5, "yag": 4},
        "Limonata": {"kalori": 110, "protein": 0.2, "karb": 28, "yag": 0.1},
        "Soğuk Çay (Ice Tea)": {"kalori": 95, "protein": 0, "karb": 24, "yag": 0},
        "Kola": {"kalori": 140, "protein": 0, "karb": 38, "yag": 0},
        "Şekersiz Kola": {"kalori": 1, "protein": 0, "karb": 0, "yag": 0},
        "Fanta": {"kalori": 160, "protein": 0, "karb": 40, "yag": 0},
        "Sprite": {"kalori": 140, "protein": 0, "karb": 36, "yag": 0},
        "Iced Latte": {"kalori": 120, "protein": 6, "karb": 12, "yag": 4.8},
        "Milkshake": {"kalori": 410, "protein": 11, "karb": 64, "yag": 13},
        "Türk Kahvesi": {"kalori": 7, "protein": 0.3, "karb": 0.9, "yag": 0.2},
        "Espresso": {"kalori": 5, "protein": 0.2, "karb": 1, "yag": 0.1},
        "Americano": {"kalori": 10, "protein": 0.5, "karb": 2, "yag": 0},
        "Latte": {"kalori": 150, "protein": 8, "karb": 14, "yag": 6},
        "Cappuccino": {"kalori": 120, "protein": 7, "karb": 11, "yag": 5},
        "Mocha": {"kalori": 290, "protein": 9, "karb": 36, "yag": 12},
        "Filtre Kahve": {"kalori": 5, "protein": 0.3, "karb": 1, "yag": 0},
        "Sıcak Çikolata": {"kalori": 280, "protein": 8, "karb": 38, "yag": 11},
        "Siyah Çay": {"kalori": 2, "protein": 0, "karb": 0.5, "yag": 0}
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
        "gunluk_kayitlar": [], "aktivite_loglari": {},
        "profil": {
            "cinsiyet": "Kadın", "yas": 20, "boy": 165, 
            "mevcut_kilo": 58.0, "hedef_kilo": 55.0, 
            "tema": "Yeşil Ferahlık", "setup_tamamlandi": False
        }
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
        "gunluk_kayitlar": st.session_state.gunluk_kayitlar,
        "aktivite_loglari": st.session_state.aktivite_loglari,
        "profil": st.session_state.profil
    }
    with open(kullanici_veri_dosyasi(username), "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

def hesapla_bmr(p):
    return (10 * float(p["mevcut_kilo"])) + (6.25 * float(p["boy"])) - (5 * int(p["yas"])) - 161

# ----------------------------------------------------
# 3. GİRİŞ VE OTURUM YÖNETİMİ
# ----------------------------------------------------
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "aktif_kullanici" not in st.session_state: st.session_state.aktif_kullanici = ""
if "sayfa_gorunumu" not in st.session_state: st.session_state.sayfa_gorunumu = "ana_sayfa"

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
            else: st.error("Hatalı kullanıcı adı veya şifre.")

    with tab_kayit:
        k_user = st.text_input("Yeni Kullanıcı Adı", key="k_user").strip().lower()
        k_pass = st.text_input("Şifre Belirle", type="password", key="k_pass")
        if st.button("Hesap Oluştur", use_container_width=True):
            if k_user and k_pass:
                users[k_user] = sifre_hashle(k_pass)
                kullanicilari_kaydet(users)
                st.success("Hesap oluşturuldu, giriş yapabilirsiniz.")

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
    # 4. HESAP, TEMA SEÇİMİ VE PROFİL AYARLARI SAYFASI
    # ----------------------------------------------------
    if st.session_state.sayfa_gorunumu == "hesap":
        st.markdown("""
            <div class="calai-section-card">
                <div class="calai-title">Hesap, Hedefler ve Tema Seçimi</div>
                <div class="calai-desc">Vücut ölçülerinizi, kalori parametrelerinizi ve site tema görsellerini buradan yönetebilirsiniz.</div>
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
            st.success("Ayarlar ve tema kaydedildi!")
            st.rerun()
            
        if st.button("← Ana Sayfaya Dön", use_container_width=True):
            st.session_state.sayfa_gorunumu = "ana_sayfa"
            st.rerun()

    # ----------------------------------------------------
    # 5. CAL AI TARZI BÜYÜK, FERAH VE GÖRSEL DESTEKLİ ANA EKRAN
    # ----------------------------------------------------
    else:
        sol_bosluk, ana_icerik, sag_bosluk = st.columns([1, 4, 1])

        aktif_tema = p.get("tema", "Yeşil Ferahlık")

        with sol_bosluk:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if aktif_tema == "Yeşil Ferahlık":
                st.image("https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400", caption="Zinde Yaşam")
            elif aktif_tema == "Pembe Su & Detoks":
                st.image("https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=400", caption="Ferahlatan Detoks")
            elif aktif_tema == "Koyu Gym":
                st.image("https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=400", caption="Güç ve Odak")
            else:
                st.image("https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=400", caption="Doğal Lezzetler")

        with ana_icerik:
            secilen_tarih = str(st.date_input("Kayıt Tarihi", datetime.date.today()))
            if secilen_tarih not in st.session_state.aktivite_loglari:
                st.session_state.aktivite_loglari[secilen_tarih] = {"adim": 0, "su": 0.0}
            curr_aktivite = st.session_state.aktivite_loglari[secilen_tarih]

            # --- BÖLÜM 1: ADIM VE SU HAREKET KARTI ---
            st.markdown(f"""
                <div class="calai-section-card">
                    <div class="calai-title">Günlük Aktivite & Su Halkaları</div>
                    <div class="calai-desc">Su tüketim ring tasarımı ve günlük adım takibiniz.</div>
                </div>
            """, unsafe_allow_html=True)
            
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
                if sc1.button("+0.25L Su Ekle", use_container_width=True):
                    curr_aktivite["su"] = round(curr_aktivite["su"] + 0.25, 2)
                    verileri_kaydet(aktif_user)
                    st.rerun()
                if sc2.button("-0.25L", use_container_width=True) and curr_aktivite["su"] >= 0.25:
                    curr_aktivite["su"] = round(curr_aktivite["su"] - 0.25, 2)
                    verileri_kaydet(aktif_user)
                    st.rerun()

            # --- BÖLÜM 2: YAPAY ZEKA FOTOĞRAF ANALİZİ ---
            st.markdown(f"""
                <div class="calai-section-card">
                    <div class="calai-title">Track Your Food With Just a Picture</div>
                    <div class="calai-desc">Yemeğinizin fotoğrafını yükleyin; arka planda yemek kalırken yapay zeka analiz raporunu ve makroları çıkarsın.</div>
                </div>
            """, unsafe_allow_html=True)

            upl = st.file_uploader("Yemek Fotoğrafı Yükle", type=["jpg", "jpeg", "png"])
            if upl:
                st.image(image := Image.open(upl), caption="Yüklenen Yemek", use_container_width=True)
                ogun_turu = st.selectbox("Öğün Türü", ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"])
                
                if st.button("Fotoğrafı Analiz Et ve Sağlık Skorunu Gör", use_container_width=True):
                    with st.spinner("Yapay zeka tabağınızı inceliyor..."):
                        try:
                            bytes_data = upl.getvalue()
                            files = {"file": ("yemek.jpg", bytes_data, "image/jpeg")}
                            res = requests.post("http://127.0.0.1:8000/api/tara", files=files)
                            if res.status_code == 200:
                                ham_metin = res.json().get("veri", "Analiz tamamlandı.")
                                st.session_state["ai_sonuc"] = {
                                    "tarife": "Yapay Zeka Analizli Yemek",
                                    "kalori": 350.0, "protein": 18.0, "karb": 32.0, "yag": 12.0, "metin": ham_metin
                                }
                            else: st.error("Sunucu yanıt vermedi.")
                        except Exception as e: st.error(f"Bağlantı hatası: {e}")

                if "ai_sonuc" in st.session_state and st.session_state["ai_sonuc"]:
                    r = st.session_state["ai_sonuc"]
                    st.info(f"**AI Sağlık Skoru & Raporu:**\n\n{r['metin']}")
                    ed_isim = st.text_input("Yemek Adı", value=r["tarife"])
                    ed_kal = st.number_input("Kalori (kcal)", value=float(r["kalori"]))
                    ed_pro = st.number_input("Protein (g)", value=float(r["protein"]))
                    ed_karb = st.number_input("Karbonhidrat (g)", value=float(r["karb"]))
                    ed_yag = st.number_input("Yağ (g)", value=float(r["yag"]))

                    if st.button("Günlüğe Kaydet", use_container_width=True):
                        st.session_state.gunluk_kayitlar.append({
                            "Tarih": secilen_tarih, "Öğün": ogun_turu, "Tarif": ed_isim + " (AI)",
                            "Kalori": ed_kal, "Protein": ed_pro, "Karbonhidrat": ed_karb, "Yağ": ed_yag
                        })
                        verileri_kaydet(aktif_user)
                        del st.session_state["ai_sonuc"]
                        st.success("Kaydedildi!")
                        st.rerun()

            # --- BÖLÜM 3: ZENGİN LEZZET KATALOĞU (TAM KADRO) ---
            st.markdown(f"""
                <div class="calai-section-card">
                    <div class="calai-title">Zengin Lezzet Kataloğu</div>
                    <div class="calai-desc">Geniş menü alternatiflerinden dilediğin lezzeti seçerek makrolarıyla birlikte ekle.</div>
                </div>
            """, unsafe_allow_html=True)
            
            m_kat = st.selectbox("Menü Kategorisi", list(ZENGIN_LEZZET_KATALOGU.keys()))
            m_yemek = st.selectbox("Yemek Seçimi", list(ZENGIN_LEZZET_KATALOGU[m_kat].keys()))
            detay = ZENGIN_LEZZET_KATALOGU[m_kat][m_yemek]
            st.markdown(f"**Değerler:** {detay['kalori']} kcal | P: {detay['protein']}g | K: {detay['karb']}g | Y: {detay['yag']}g")
            
            if st.button("Kataloğtan Seçilen Yemeği Ekle", use_container_width=True):
                st.session_state.gunluk_kayitlar.append({
                    "Tarih": secilen_tarih, "Öğün": "Ana Öğün", "Tarif": m_yemek,
                    "Kalori": detay["kalori"], "Protein": detay["protein"], "Karbonhidrat": detay["karb"], "Yağ": detay["yag"]
                })
                verileri_kaydet(aktif_user)
                st.success(f"{m_yemek} eklendi!")
                st.rerun()

            # --- BÖLÜM 4: GÜNLÜK ÖZET VE MAKRO HEDEF ÇUBUKLARI ---
            st.markdown(f"""
                <div class="calai-section-card">
                    <div class="calai-title">Günlük Denge & Hedef Çubukları ({secilen_tarih})</div>
                </div>
            """, unsafe_allow_html=True)
            
            bugun_og = [(i, k) for i, k in enumerate(st.session_state.gunluk_kayitlar) if k["Tarih"] == secilen_tarih]
            toplam_alinan = 0
            toplam_pro = 0
            toplam_karb = 0
            toplam_yag = 0
            
            if bugun_og:
                for i, kayit in bugun_og:
                    toplam_alinan += kayit["Kalori"]
                    toplam_pro += kayit.get("Protein", 0)
                    toplam_karb += kayit.get("Karbonhidrat", 0)
                    toplam_yag += kayit.get("Yağ", 0)
                    
                    cr1, cr2 = st.columns([10, 1])
                    cr1.markdown(f"**{kayit['Öğün']}**: {kayit['Tarif']} — *{kayit['Kalori']} kcal* (P:{kayit.get('Protein',0)}g, K:{kayit.get('Karbonhidrat',0)}g, Y:{kayit.get('Yağ',0)}g)")
                    if cr2.button("🗑️", key=f"sil_{i}"):
                        st.session_state.gunluk_kayitlar.pop(i)
                        verileri_kaydet(aktif_user)
                        st.rerun()
            else:
                st.info("Bu tarihte henüz bir kayıt bulunmuyor.")

            hedef_kalori_1 = bmr_kisi + (curr_aktivite["adim"] * 0.04)
            
            st.markdown(f"**Günlük Alınan Kalori:** {round(toplam_alinan)} / {round(hedef_kalori_1)} kcal")
            st.progress(min(toplam_alinan / max(hedef_kalori_1, 1), 1.0))

            st.markdown(f"**Protein:** {round(toplam_pro)}g / 90g Hedef")
            st.progress(min(toplam_pro / 90, 1.0))

            st.markdown(f"**Karbonhidrat:** {round(toplam_karb)}g / 150g Hedef")
            st.progress(min(toplam_karb / 150, 1.0))

            st.markdown(f"**Yağ:** {round(toplam_yag)}g / 50g Hedef")
            st.progress(min(toplam_yag / 50, 1.0))

            # --- BÖLÜM 5: HAFTALIK PROGRAM & ANALİZ ---
            st.markdown(f"""
                <div class="calai-section-card">
                    <div class="calai-title">Haftalık Program ve Analiz Akışı</div>
                    <div class="calai-desc">Geçmiş günlere ait kalori ve makro tüketim trendleriniz.</div>
                </div>
            """, unsafe_allow_html=True)
            if st.session_state.gunluk_kayitlar:
                df_tum = pd.DataFrame(st.session_state.gunluk_kayitlar)
                haftalik_ozet = df_tum.groupby("Tarih")[["Kalori", "Protein", "Karbonhidrat", "Yağ"]].sum().reset_index()
                st.line_chart(haftalik_ozet.set_index("Tarih")[["Kalori"]])
                st.dataframe(haftalik_ozet, use_container_width=True)
            else:
                st.info("Haftalık analiz için yeterli veri bulunmuyor.")

        with sag_bosluk:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if aktif_tema == "Yeşil Ferahlık":
                st.image("https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400", caption="Sağlıklı Tabaklar")
            elif aktif_tema == "Pembe Su & Detoks":
                st.image("https://images.unsplash.com/photo-1556881286-fc6915169721?w=400", caption="Vitamin Deposu")
            elif aktif_tema == "Koyu Gym":
                st.image("https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=400", caption="Performans")
            else:
                st.image("https://images.unsplash.com/photo-1550258987-190a2d41a8ba?w=400", caption="Tatlı Kaçamakları")
