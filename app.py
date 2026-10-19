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
# 2. A'DAN F'YE KAPSAMLI HİYERARŞİK MENÜ VERİTABANI
# ----------------------------------------------------
GENIS_MENU_VERITABASI = {
    "A. 🥐 Kahvaltılıklar ve Sabah Öğünü": {
        "Serpme Kahvaltı (Tek Kişilik)": {
            "kalori": 650,
            "protein": 24.0,
            "karb": 55.0,
            "yag": 36.0,
        },
        "Serpme Kahvaltı (İki Kişilik)": {
            "kalori": 1300,
            "protein": 48.0,
            "karb": 110.0,
            "yag": 72.0,
        },
        "Standart Kahvaltı Tabağı": {
            "kalori": 420,
            "protein": 18.0,
            "karb": 35.0,
            "yag": 22.0,
        },
        "Zenginleştirilmiş Kahvaltı Tabağı": {
            "kalori": 580,
            "protein": 25.0,
            "karb": 48.0,
            "yag": 31.0,
        },
        "Sade Menemen (Küçük Porsiyon)": {
            "kalori": 140,
            "protein": 7.0,
            "karb": 6.0,
            "yag": 10.0,
        },
        "Sade Menemen (Orta Porsiyon)": {
            "kalori": 210,
            "protein": 11.0,
            "karb": 9.0,
            "yag": 15.0,
        },
        "Sade Menemen (Büyük Porsiyon)": {
            "kalori": 310,
            "protein": 16.0,
            "karb": 13.0,
            "yag": 22.0,
        },
        "Kaşarlı Menemen (Küçük Porsiyon)": {
            "kalori": 220,
            "protein": 12.0,
            "karb": 7.0,
            "yag": 16.0,
        },
        "Kaşarlı Menemen (Orta Porsiyon)": {
            "kalori": 320,
            "protein": 18.0,
            "karb": 10.0,
            "yag": 23.0,
        },
        "Kaşarlı Menemen (Büyük Porsiyon)": {
            "kalori": 450,
            "protein": 25.0,
            "karb": 14.0,
            "yag": 33.0,
        },
        "Sucuklu Yumurta (Standart Porsiyon)": {
            "kalori": 380,
            "protein": 19.0,
            "karb": 3.0,
            "yag": 32.0,
        },
        "Sucuklu Yumurta (Doyurucu Porsiyon)": {
            "kalori": 540,
            "protein": 27.0,
            "karb": 4.0,
            "yag": 46.0,
        },
        "Peynirli Omlet (Standart Porsiyon)": {
            "kalori": 280,
            "protein": 17.0,
            "karb": 2.0,
            "yag": 22.0,
        },
        "Kaşarlı Tost (Tek)": {
            "kalori": 290,
            "protein": 12.0,
            "karb": 30.0,
            "yag": 13.0,
        },
        "Kaşarlı Tost (Duble)": {
            "kalori": 440,
            "protein": 20.0,
            "karb": 42.0,
            "yag": 21.0,
        },
        "Karışık Tost (Tek)": {
            "kalori": 350,
            "protein": 15.0,
            "karb": 31.0,
            "yag": 18.0,
        },
        "Karışık Tost (Duble)": {
            "kalori": 520,
            "protein": 24.0,
            "karb": 44.0,
            "yag": 28.0,
        },
        "Avokadolu Tost (Standart Porsiyon)": {
            "kalori": 320,
            "protein": 9.0,
            "karb": 34.0,
            "yag": 17.0,
        },
        "Beyaz Peynirli Sandviç (Standart)": {
            "kalori": 280,
            "protein": 13.0,
            "karb": 36.0,
            "yag": 9.0,
        },
        "Sade Kruvasan": {
            "kalori": 270,
            "protein": 5.0,
            "karb": 31.0,
            "yag": 14.0,
        },
        "Çikolatalı Kruvasan": {
            "kalori": 360,
            "protein": 6.0,
            "karb": 42.0,
            "yag": 19.0,
        },
        "Pancake (3'lü Porsiyon)": {
            "kalori": 280,
            "protein": 7.0,
            "karb": 45.0,
            "yag": 8.0,
        },
        "Pancake (5'li Porsiyon)": {
            "kalori": 460,
            "protein": 12.0,
            "karb": 75.0,
            "yag": 13.0,
        },
        "Waffle Kahvaltı Tabağı (Standart)": {
            "kalori": 520,
            "protein": 10.0,
            "karb": 70.0,
            "yag": 22.0,
        },
        "Granola ve Yoğurt Kasesi (Küçük Boy)": {
            "kalori": 220,
            "protein": 9.0,
            "karb": 32.0,
            "yag": 6.0,
        },
        "Granola ve Yoğurt Kasesi (Büyük Boy)": {
            "kalori": 380,
            "protein": 15.0,
            "karb": 56.0,
            "yag": 11.0,
        },
        "Meyveli Yulaf Lapası (Standart)": {
            "kalori": 260,
            "protein": 8.0,
            "karb": 46.0,
            "yag": 5.0,
        },
        "Fransız Tostu (Standart)": {
            "kalori": 340,
            "protein": 10.0,
            "karb": 40.0,
            "yag": 15.0,
        },
        "Simit ve Peynir Tabağı (Standart)": {
            "kalori": 410,
            "protein": 16.0,
            "karb": 52.0,
            "yag": 15.0,
        },
        "Bagel Sandviç (Standart)": {
            "kalori": 350,
            "protein": 14.0,
            "karb": 48.0,
            "yag": 11.0,
        },
        "Kahvaltılık Quesadilla (Standart)": {
            "kalori": 430,
            "protein": 19.0,
            "karb": 38.0,
            "yag": 22.0,
        },
    },
    "B. 🥪 Öğle Yemeği ve Pratik Seçenekler": {
        "Mercimek Çorbası (Kase)": {
            "kalori": 160,
            "protein": 8.0,
            "karb": 22.0,
            "yag": 4.5,
        },
        "Ezogelin Çorbası (Kase)": {
            "kalori": 170,
            "protein": 7.0,
            "karb": 24.0,
            "yag": 5.0,
        },
        "Domates Çorbası (Kase)": {
            "kalori": 130,
            "protein": 3.0,
            "karb": 18.0,
            "yag": 5.5,
        },
        "Kremalı Mantar Çorbası (Kase)": {
            "kalori": 210,
            "protein": 4.0,
            "karb": 16.0,
            "yag": 15.0,
        },
        "Tavuk Suyu Çorbası (Kase)": {
            "kalori": 140,
            "protein": 10.0,
            "karb": 12.0,
            "yag": 5.0,
        },
        "Yayla Çorbası (Kase)": {
            "kalori": 150,
            "protein": 5.0,
            "karb": 20.0,
            "yag": 5.5,
        },
        "Mevsim Salata (Standart Porsiyon)": {
            "kalori": 90,
            "protein": 2.0,
            "karb": 8.0,
            "yag": 6.0,
        },
        "Tavuklu Sezar Salata (Standart Porsiyon)": {
            "kalori": 380,
            "protein": 32.0,
            "karb": 12.0,
            "yag": 22.0,
        },
        "Ton Balıklı Salata (Standart Porsiyon)": {
            "kalori": 290,
            "protein": 28.0,
            "karb": 9.0,
            "yag": 15.0,
        },
        "Hellim Peynirli Salata (Standart Porsiyon)": {
            "kalori": 360,
            "protein": 18.0,
            "karb": 11.0,
            "yag": 27.0,
        },
        "Izgara Tavuklu Wrap (Standart)": {
            "kalori": 420,
            "protein": 30.0,
            "karb": 42.0,
            "yag": 14.0,
        },
        "Çıtır Tavuk Wrap (Standart)": {
            "kalori": 530,
            "protein": 24.0,
            "karb": 52.0,
            "yag": 25.0,
        },
        "Falafel Wrap (Standart)": {
            "kalori": 450,
            "protein": 14.0,
            "karb": 58.0,
            "yag": 18.0,
        },
        "Acai Bowl (Küçük Boy)": {
            "kalori": 210,
            "protein": 4.0,
            "karb": 38.0,
            "yag": 5.0,
        },
        "Acai Bowl (Büyük Boy)": {
            "kalori": 360,
            "protein": 7.0,
            "karb": 64.0,
            "yag": 9.0,
        },
        "Protein Bowl (Küçük Boy)": {
            "kalori": 310,
            "protein": 26.0,
            "karb": 30.0,
            "yag": 9.0,
        },
        "Protein Bowl (Büyük Boy)": {
            "kalori": 490,
            "protein": 42.0,
            "karb": 48.0,
            "yag": 15.0,
        },
        "Somonlu Bowl (Standart)": {
            "kalori": 460,
            "protein": 31.0,
            "karb": 40.0,
            "yag": 18.0,
        },
        "Hindi Fümeli Sandviç (Standart)": {
            "kalori": 310,
            "protein": 20.0,
            "karb": 38.0,
            "yag": 8.0,
        },
        "Club Sandwich (Standart)": {
            "kalori": 540,
            "protein": 26.0,
            "karb": 45.0,
            "yag": 28.0,
        },
    },
    "C. 🍽️ Akşam Yemeği ve Ana Yemekler": {
        "Izgara Tavuk (Standart Porsiyon)": {
            "kalori": 280,
            "protein": 42.0,
            "karb": 0.0,
            "yag": 12.0,
        },
        "Tavuk Şinitzel (Standart Porsiyon)": {
            "kalori": 420,
            "protein": 32.0,
            "karb": 24.0,
            "yag": 22.0,
        },
        "Izgara Köfte (Standart Porsiyon)": {
            "kalori": 360,
            "protein": 28.0,
            "karb": 6.0,
            "yag": 24.0,
        },
        "Dana Antrikot (Standart Porsiyon)": {
            "kalori": 450,
            "protein": 38.0,
            "karb": 0.0,
            "yag": 32.0,
        },
        "Izgara Somon (Standart Porsiyon)": {
            "kalori": 380,
            "protein": 34.0,
            "karb": 0.0,
            "yag": 26.0,
        },
        "Mantı (Standart Porsiyon)": {
            "kalori": 480,
            "protein": 18.0,
            "karb": 62.0,
            "yag": 18.0,
        },
        "İskender Kebap (Standart Porsiyon)": {
            "kalori": 720,
            "protein": 36.0,
            "karb": 54.0,
            "yag": 38.0,
        },
        "Lahmacun (Tek)": {
            "kalori": 220,
            "protein": 9.5,
            "karb": 28.0,
            "yag": 7.5,
        },
        "Lahmacun (Duble)": {
            "kalori": 440,
            "protein": 19.0,
            "karb": 56.0,
            "yag": 15.0,
        },
        "Sade Pirinç Pilavı (Küçük Porsiyon)": {
            "kalori": 130,
            "protein": 2.2,
            "karb": 28.0,
            "yag": 1.5,
        },
        "Sade Pirinç Pilavı (Orta Porsiyon)": {
            "kalori": 210,
            "protein": 3.5,
            "karb": 44.0,
            "yag": 2.5,
        },
        "Sade Pirinç Pilavı (Büyük Porsiyon)": {
            "kalori": 320,
            "protein": 5.2,
            "karb": 68.0,
            "yag": 3.8,
        },
        "Bulgur Pilavı (Küçük Porsiyon)": {
            "kalori": 110,
            "protein": 3.5,
            "karb": 22.0,
            "yag": 1.2,
        },
        "Bulgur Pilavı (Orta Porsiyon)": {
            "kalori": 170,
            "protein": 5.5,
            "karb": 34.0,
            "yag": 2.0,
        },
        "Bulgur Pilavı (Büyük Porsiyon)": {
            "kalori": 260,
            "protein": 8.5,
            "karb": 52.0,
            "yag": 3.0,
        },
        "Su Böreği (1 Dilim)": {
            "kalori": 310,
            "protein": 11.0,
            "karb": 32.0,
            "yag": 16.0,
        },
        "Kıymalı Börek (1 Dilim)": {
            "kalori": 290,
            "protein": 9.0,
            "karb": 31.0,
            "yag": 14.0,
        },
        "Peynirli Gözleme": {
            "kalori": 380,
            "protein": 14.0,
            "karb": 46.0,
            "yag": 16.0,
        },
        "Patatesli Gözleme": {
            "kalori": 360,
            "protein": 8.0,
            "karb": 54.0,
            "yag": 13.0,
        },
        "Zeytinyağlı Enginar (Standart Porsiyon)": {
            "kalori": 160,
            "protein": 3.0,
            "karb": 18.0,
            "yag": 9.0,
        },
        "Zeytinyağlı Yaprak Sarma (Standart Porsiyon)": {
            "kalori": 240,
            "protein": 4.0,
            "karb": 36.0,
            "yag": 9.5,
        },
    },
    "D. 🌯 Sokak Lezzetleri ve Fast Food": {
        "Islak Hamburger (Tek)": {
            "kalori": 260,
            "protein": 11.0,
            "karb": 28.0,
            "yag": 12.0,
        },
        "Kumpir (Standart)": {
            "kalori": 680,
            "protein": 16.0,
            "karb": 82.0,
            "yag": 32.0,
        },
        "Kokoreç (Yarım Ekmek)": {
            "kalori": 420,
            "protein": 22.0,
            "karb": 38.0,
            "yag": 20.0,
        },
        "Kokoreç (Tam Ekmek)": {
            "kalori": 780,
            "protein": 41.0,
            "karb": 72.0,
            "yag": 36.0,
        },
        "Midye Dolma (5 Adet)": {
            "kalori": 150,
            "protein": 7.0,
            "karb": 22.0,
            "yag": 4.0,
        },
        "Midye Dolma (10 Adet)": {
            "kalori": 300,
            "protein": 14.0,
            "karb": 44.0,
            "yag": 8.0,
        },
        "Tantuni (Et - Dürüm)": {
            "kalori": 440,
            "protein": 26.0,
            "karb": 40.0,
            "yag": 20.0,
        },
        "Tantuni (Tavuk - Dürüm)": {
            "kalori": 380,
            "protein": 28.0,
            "karb": 38.0,
            "yag": 14.0,
        },
        "Patates Kızartması (Küçük Boy)": {
            "kalori": 220,
            "protein": 2.5,
            "karb": 29.0,
            "yag": 11.0,
        },
        "Patates Kızartması (Orta Boy)": {
            "kalori": 330,
            "protein": 3.8,
            "karb": 43.0,
            "yag": 16.0,
        },
        "Patates Kızartması (Büyük Boy)": {
            "kalori": 470,
            "protein": 5.2,
            "karb": 61.0,
            "yag": 23.0,
        },
        "Klasik Hamburger (Tek Porsiyon)": {
            "kalori": 390,
            "protein": 20.0,
            "karb": 38.0,
            "yag": 18.0,
        },
        "Cheeseburger (Tek Porsiyon)": {
            "kalori": 450,
            "protein": 24.0,
            "karb": 39.0,
            "yag": 22.0,
        },
        "Double Cheeseburger (Standart)": {
            "kalori": 640,
            "protein": 38.0,
            "karb": 41.0,
            "yag": 36.0,
        },
        "Margherita Pizza (Küçük Boy / 22cm)": {
            "kalori": 480,
            "protein": 18.0,
            "karb": 62.0,
            "yag": 17.0,
        },
        "Margherita Pizza (Orta Boy / 28cm)": {
            "kalori": 760,
            "protein": 29.0,
            "karb": 98.0,
            "yag": 27.0,
        },
        "Margherita Pizza (Büyük Boy / 34cm)": {
            "kalori": 1120,
            "protein": 42.0,
            "karb": 144.0,
            "yag": 40.0,
        },
        "Soğan Halkası (6 Adet)": {
            "kalori": 190,
            "protein": 2.5,
            "karb": 24.0,
            "yag": 9.5,
        },
        "Soğan Halkası (12 Adet)": {
            "kalori": 380,
            "protein": 5.0,
            "karb": 48.0,
            "yag": 19.0,
        },
    },
    "E. 🍰 Tatlılar, Pastane Ürünleri ve Dondurmalar": {
        "San Sebastian Cheesecake (1 Dilim)": {
            "kalori": 460,
            "protein": 8.0,
            "karb": 34.0,
            "yag": 32.0,
        },
        "Çikolatalı Sufle (Standart)": {
            "kalori": 390,
            "protein": 6.0,
            "karb": 48.0,
            "yag": 19.0,
        },
        "Profiterol (Standart Porsiyon)": {
            "kalori": 340,
            "protein": 5.0,
            "karb": 42.0,
            "yag": 17.0,
        },
        "Magnolia (Küçük Boy)": {
            "kalori": 220,
            "protein": 4.0,
            "karb": 32.0,
            "yag": 9.0,
        },
        "Magnolia (Büyük Boy)": {
            "kalori": 380,
            "protein": 7.0,
            "karb": 56.0,
            "yag": 15.0,
        },
        "Waffle (Standart)": {
            "kalori": 540,
            "protein": 9.0,
            "karb": 72.0,
            "yag": 24.0,
        },
        "Karamelli Trileçe (1 Dilim)": {
            "kalori": 310,
            "protein": 6.0,
            "karb": 44.0,
            "yag": 12.0,
        },
        "Fırın Sütlaç (Standart)": {
            "kalori": 240,
            "protein": 6.0,
            "karb": 41.0,
            "yag": 5.5,
        },
        "Baklava (2 Dilim)": {
            "kalori": 330,
            "protein": 4.0,
            "karb": 42.0,
            "yag": 16.0,
        },
        "Baklava (4 Dilim)": {
            "kalori": 660,
            "protein": 8.0,
            "karb": 84.0,
            "yag": 32.0,
        },
        "Vanilyalı Dondurma (Tek Top)": {
            "kalori": 80,
            "protein": 1.5,
            "karb": 10.0,
            "yag": 3.8,
        },
        "Vanilyalı Dondurma (Çift Top)": {
            "kalori": 160,
            "protein": 3.0,
            "karb": 20.0,
            "yag": 7.6,
        },
        "Çikolatalı Dondurma (Tek Top)": {
            "kalori": 90,
            "protein": 1.8,
            "karb": 11.0,
            "yag": 4.2,
        },
        "Çikolatalı Dondurma (Çift Top)": {
            "kalori": 180,
            "protein": 3.6,
            "karb": 22.0,
            "yag": 8.4,
        },
        "Poğaça (Peynirli)": {
            "kalori": 260,
            "protein": 7.0,
            "karb": 28.0,
            "yag": 13.0,
        },
        "Açma (Zeytinli)": {
            "kalori": 310,
            "protein": 6.0,
            "karb": 38.0,
            "yag": 15.0,
        },
    },
    "F. 🧋 Soğuk İçecekler, Sıcak İçecekler ve Soslar": {
        "Su (330ml Şişe)": {
            "kalori": 0,
            "protein": 0.0,
            "karb": 0.0,
            "yag": 0.0,
        },
        "Su (500ml Şişe)": {
            "kalori": 0,
            "protein": 0.0,
            "karb": 0.0,
            "yag": 0.0,
        },
        "Maden Suyu (Küçük Şişe)": {
            "kalori": 0,
            "protein": 0.0,
            "karb": 0.0,
            "yag": 0.0,
        },
        "Ayran (Küçük Boy / Bardak)": {
            "kalori": 75,
            "protein": 4.0,
            "karb": 5.0,
            "yag": 4.0,
        },
        "Ayran (Büyük Boy / Yayık)": {
            "kalori": 130,
            "protein": 7.0,
            "karb": 9.0,
            "yag": 7.0,
        },
        "Limonata (Küçük Boy)": {
            "kalori": 90,
            "protein": 0.2,
            "karb": 22.0,
            "yag": 0.0,
        },
        "Limonata (Orta Boy)": {
            "kalori": 140,
            "protein": 0.3,
            "karb": 35.0,
            "yag": 0.0,
        },
        "Limonata (Büyük Boy)": {
            "kalori": 210,
            "protein": 0.5,
            "karb": 52.0,
            "yag": 0.0,
        },
        "Kola (Küçük Boy / 330ml Kutu)": {
            "kalori": 139,
            "protein": 0.0,
            "karb": 35.0,
            "yag": 0.0,
        },
        "Kola (Orta Boy / 500ml)": {
            "kalori": 210,
            "protein": 0.0,
            "karb": 53.0,
            "yag": 0.0,
        },
        "Kola (Büyük Boy / 1 Litre)": {
            "kalori": 420,
            "protein": 0.0,
            "karb": 106.0,
            "yag": 0.0,
        },
        "Şekersiz Kola (Küçük Boy)": {
            "kalori": 1,
            "protein": 0.0,
            "karb": 0.0,
            "yag": 0.0,
        },
        "Iced Latte (Küçük Boy)": {
            "kalori": 90,
            "protein": 4.5,
            "karb": 9.0,
            "yag": 3.8,
        },
        "Iced Latte (Büyük Boy)": {
            "kalori": 160,
            "protein": 8.0,
            "karb": 16.0,
            "yag": 6.8,
        },
        "Türk Kahvesi (Tek)": {
            "kalori": 7,
            "protein": 0.3,
            "karb": 0.9,
            "yag": 0.2,
        },
        "Türk Kahvesi (Çift)": {
            "kalori": 14,
            "protein": 0.6,
            "karb": 1.8,
            "yag": 0.4,
        },
        "Espresso (Tek / Single)": {
            "kalori": 3,
            "protein": 0.1,
            "karb": 0.5,
            "yag": 0.0,
        },
        "Espresso (Çift / Double)": {
            "kalori": 6,
            "protein": 0.2,
            "karb": 1.0,
            "yag": 0.0,
        },
        "Americano (Küçük Boy)": {
            "kalori": 10,
            "protein": 0.2,
            "karb": 1.5,
            "yag": 0.0,
        },
        "Americano (Büyük Boy)": {
            "kalori": 18,
            "protein": 0.4,
            "karb": 2.8,
            "yag": 0.0,
        },
        "Ketçap (Paket / Sosluk)": {
            "kalori": 20,
            "protein": 0.2,
            "karb": 4.8,
            "yag": 0.0,
        },
        "Mayonez (Paket / Sosluk)": {
            "kalori": 90,
            "protein": 0.1,
            "karb": 0.5,
            "yag": 10.0,
        },
        "Barbekü Sos (Sosluk)": {
            "kalori": 35,
            "protein": 0.2,
            "karb": 8.0,
            "yag": 0.1,
        },
        "Cheddar Sos (Sosluk)": {
            "kalori": 80,
            "protein": 3.0,
            "karb": 2.0,
            "yag": 7.0,
        },
    },
}


# ----------------------------------------------------
# 3. KİŞİSELLEŞTİRİLEBİLİR TEMA TONLARI VE DİNAMİK CSS
# ----------------------------------------------------
def get_theme_styles(tema_adi):
  if "Gece" in tema_adi or "Mavi" in tema_adi:
    return {
        "bg": "#0b132b",
        "card_bg": "linear-gradient(135deg, rgba(28, 37, 65, 0.95) 0%, rgba(11, 19, 43, 0.95) 100%)",
        "text": "#e0e1dd",
        "heading": "#ffffff",
        "sidebar_bg": "#1c2541",
        "accent": "#48cae4",
        "border": "#3a506b",
        "ring_adim": "#48cae4",
        "ring_su": "#90e0ef",
    }
  elif "Kahve" in tema_adi or "Toprak" in tema_adi:
    return {
        "bg": "#eedecc",
        "card_bg": "linear-gradient(135deg, #f7f0ea 0%, #ecdcd0 100%)",
        "text": "#2c221e",
        "heading": "#3d2c23",
        "sidebar_bg": "#d6c2b0",
        "accent": "#7f5539",
        "border": "#b08968",
        "ring_adim": "#9c6644",
        "ring_su": "#b08968",
    }
  elif "Yeşil" in tema_adi or "Doğa" in tema_adi:
    return {
        "bg": "#edf2f4",
        "card_bg": "linear-gradient(135deg, #f4f7f6 0%, #e2e8e6 100%)",
        "text": "#2b3a32",
        "heading": "#1e2923",
        "sidebar_bg": "#d8e2dc",
        "accent": "#52796f",
        "border": "#84a98c",
        "ring_adim": "#52796f",
        "ring_su": "#354f52",
    }
  elif "Karamel" in tema_adi:
    return {
        "bg": "#fdf0ed",
        "card_bg": "linear-gradient(135deg, #fff7f5 0%, #fae1dd 100%)",
        "text": "#4a2e2b",
        "heading": "#361f1d",
        "sidebar_bg": "#f5cac3",
        "accent": "#e07a5f",
        "border": "#f2cc8f",
        "ring_adim": "#e07a5f",
        "ring_su": "#d4a373",
    }
  else:
    # Sonbahar Kremi (Varsayılan)
    return {
        "bg": "#f7f3ee",
        "card_bg": "linear-gradient(135deg, #fffdfa 0%, #f4efe9 100%)",
        "text": "#3b2f2f",
        "heading": "#4a3b32",
        "sidebar_bg": "#eaddca",
        "accent": "#b08968",
        "border": "#d4c5b9",
        "ring_adim": "#b08968",
        "ring_su": "#9c7553",
    }


def load_user_theme(username):
  user_file = f"veriler_{username.lower().strip()}.json"
  if os.path.exists(user_file):
    try:
      with open(user_file, "r", encoding="utf-8") as f:
        d = json.load(f)
        return d.get("profil", {}).get("tema", "Sonbahar Kremi")
    except:
      pass
  return "Sonbahar Kremi"


aktif_kullanici_temp = st.session_state.get("aktif_kullanici", "")
secilen_tema_adi = (
    load_user_theme(aktif_kullanici_temp) if aktif_kullanici_temp else "Sonbahar Kremi"
)
t = get_theme_styles(secilen_tema_adi)

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400;1,600&display=swap');

    .stApp {{
        background-color: {t['bg']};
        color: {t['text']};
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Playfair Display', Georgia, serif !important;
        letter-spacing: 0.5px;
        color: {t['heading']} !important;
    }}

    p, span, label, div {{
        color: {t['text']};
    }}

    [data-testid="stSidebar"] {{
        background-color: {t['sidebar_bg']};
        color: {t['text']};
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 12px;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: 'Playfair Display', Georgia, serif;
        font-style: italic;
        font-size: 16px;
        color: {t['accent']};
        background-color: transparent;
        border-radius: 6px;
        padding: 8px 16px;
    }}
    .stTabs [aria-selected="true"] {{
        color: {t['heading']} !important;
        border-bottom: 2px solid {t['accent']} !important;
        font-weight: 600;
    }}

    .recipe-card {{
        background: {t['card_bg']};
        border: 1px solid {t['border']};
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(100, 80, 60, 0.06);
    }}
    .recipe-title {{
        font-family: 'Playfair Display', Georgia, serif;
        font-style: italic;
        font-size: 18px;
        font-weight: 600;
        color: {t['accent']};
        margin-bottom: 6px;
    }}
    .recipe-details {{
        font-size: 13.5px;
        color: {t['text']};
        opacity: 0.85;
    }}

    .stButton > button {{
        background-color: {t['accent']};
        color: #ffffff;
        border: 1px solid {t['border']};
        border-radius: 8px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 500;
        transition: 0.3s;
    }}
    .stButton > button:hover {{
        opacity: 0.9;
        color: #ffffff;
    }}

    .sidebar-user-card {{
        text-align: center;
        margin-top: 10px;
        margin-bottom: 15px;
    }}
    .sidebar-user-name {{
        font-family: 'Playfair Display', Georgia, serif;
        font-style: italic;
        font-size: 18px;
        font-weight: 600;
        color: {t['heading']};
        margin-top: 8px;
        margin-bottom: 5px;
    }}

    .landing-subtext {{
        font-family: 'Playfair Display', Georgia, serif;
        font-style: italic;
        font-size: 13.5px;
        line-height: 1.7;
        color: {t['text']};
        text-align: justify;
        font-weight: 400;
        margin-top: 12px;
        margin-bottom: 20px;
        letter-spacing: 0.2px;
    }}
    </style>
""",
    unsafe_allow_html=True,
)

USERS_FILE = "kullanicilar.json"

LOGO_MAIN = f"""
<div style="text-align: center; font-family: 'Playfair Display', Georgia, serif; font-style: italic; font-size: 44px; font-weight: 700; letter-spacing: 22px; color: {t['heading']}; margin-bottom: 5px;">
    N&nbsp;&nbsp;O&nbsp;&nbsp;V&nbsp;&nbsp;A
</div>
"""

LOGO_SIDEBAR = f"""
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: 'Playfair Display', Georgia, serif; font-style: italic; font-size: 30px; font-weight: 700; color: {t['heading']}; gap: 8px; margin-top: 10px; margin-bottom: 15px;">
    <span>N</span>
    <span>O</span>
    <span>V</span>
    <span>A</span>
</div>
"""


# ----------------------------------------------------
# 4. KULLANICI YÖNETİMİ VE DOSYA İŞLEMLERİ
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

  # Varsayılan düz besin kütüphanesi
  duz_besinler = {}
  for kat_adi, urunler in GENIS_MENU_VERITABASI.items():
    for u_adi, u_vals in urunler.items():
      duz_besinler[u_adi.lower()] = u_vals

  default_data = {
      "besin_veritabani": duz_besinler,
      "hazir_tarifler": {},
      "gunluk_kayitlar": [],
      "aktivite_loglari": {},
      "profil": {
          "cinsiyet": "Kadın",
          "yas": 20,
          "boy": 165,
          "mevcut_kilo": 58.0,
          "hedef_kilo": 55.0,
          "verilmek_istenen_kilo": 3.0,
          "hedef_gun": 45,
          "egzersiz_katsayisi": 1.0,
          "tema": "Sonbahar Kremi",
          "setup_tamamlandi": False,
      },
  }

  if os.path.exists(user_file):
    try:
      with open(user_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        profil = data.get("profil", {})
        if "egzersiz_katsayisi" not in profil:
          profil["egzersiz_katsayisi"] = 1.0
        if "tema" not in profil:
          profil["tema"] = "Sonbahar Kremi"
        if "setup_tamamlandi" not in profil:
          profil["setup_tamamlandi"] = True
        data["profil"] = profil

        for k, v in duz_besinler.items():
          if k not in data["besin_veritabani"]:
            data["besin_veritabani"][k] = v

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
# 5. OTURUM KONTROLÜ VE GİRİŞ EKRANI
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
  # 6. ANA UYGULAMA PANELİ
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
          "Günlük Takip & Ana Sayfa",
          "Haftalık Program & Değerlendirme",
          "Tarif & Malzeme Yönetimi",
          "Hesap ve Hedefler",
      ],
      index=default_menu_index,
  )

  if is_first_login:
    st.info(
        "✨ **Nova'ya Hoş Geldin!** Yolculuğuna kusursuz başlayabilmek için"
        " lütfen **Hesap ve Hedefler** sekmesinden hedeflediğin kilo verme"
        " miktarını, egzersiz katsayını ve temanı belirle."
    )

  # ----------------------------------------------------
  # GÜNLÜK TAKİP & ANA SAYFA (CHECKBOX'LI ÖĞÜN EKLEME & MÜKEMMEL MENÜ)
  # ----------------------------------------------------
  if menu == "Günlük Takip & Ana Sayfa":
    st.header(f"Günlük Yaşam Paneli — {aktif_user.title()}")

    secilen_tarih = str(st.date_input("Kayıt Tarihi", datetime.date.today()))

    if secilen_tarih not in st.session_state.aktivite_loglari:
      st.session_state.aktivite_loglari[secilen_tarih] = {
          "adim": 8500,
          "su": 2.0,
          "video_tamamlandi": False,
      }

    curr_aktivite = st.session_state.aktivite_loglari[secilen_tarih]

    # --- RİNGS (ADIM VE SU) ---
    st.subheader("🍂 Günlük Su ve Adım Takibi")
    col_ring_sol, col_ring_sag = st.columns(2)

    with col_ring_sol:
      adim_hedef = 10000
      adim_oran = min(1.0, curr_aktivite["adim"] / adim_hedef)
      adim_circ = 2 * 3.14159 * 42
      adim_offset = adim_circ * (1 - adim_oran)

      st.markdown(
          f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.03); padding: 15px; border-radius: 16px; border: 1px solid {t['border']};">
                <div style="position: relative; width: 110px; height: 110px;">
                    <svg width="110" height="110" style="transform: rotate(-90deg);">
                        <circle cx="55" cy="55" r="42" stroke="rgba(0,0,0,0.1)" stroke-width="10" fill="transparent"/>
                        <circle cx="55" cy="55" r="42" stroke="{t['ring_adim']}" stroke-width="10" stroke-dasharray="{adim_circ}" stroke-dashoffset="{adim_offset}" stroke-linecap="round" fill="transparent"/>
                    </svg>
                    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <span style="font-size: 16px; font-weight: 700; color: {t['heading']};">{curr_aktivite['adim']}</span>
                        <span style="font-size: 10px; color: {t['ring_adim']}; font-weight: 700; letter-spacing: 0.5px;">ADIM RİNGİ</span>
                    </div>
                </div>
            </div>
            """,
          unsafe_allow_html=True,
      )
      yeni_adim = st.number_input(
          "Adım Güncelle",
          min_value=0,
          max_value=50000,
          value=int(curr_aktivite["adim"]),
          step=500,
          key="inp_adim_ring",
      )
      if st.button("Adımı Kaydet"):
        curr_aktivite["adim"] = yeni_adim
        verileri_kaydet(aktif_user)
        st.success("Adım halkası güncellendi!")

    with col_ring_sag:
      su_hedef = 3.0
      su_oran = min(1.0, curr_aktivite["su"] / su_hedef)
      su_circ = 2 * 3.14159 * 42
      su_offset = su_circ * (1 - su_oran)

      st.markdown(
          f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.03); padding: 15px; border-radius: 16px; border: 1px solid {t['border']};">
                <div style="position: relative; width: 110px; height: 110px;">
                    <svg width="110" height="110" style="transform: rotate(-90deg);">
                        <circle cx="55" cy="55" r="42" stroke="rgba(0,0,0,0.1)" stroke-width="10" fill="transparent"/>
                        <circle cx="55" cy="55" r="42" stroke="{t['ring_su']}" stroke-width="10" stroke-dasharray="{su_circ}" stroke-dashoffset="{su_offset}" stroke-linecap="round" fill="transparent"/>
                    </svg>
                    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <span style="font-size: 16px; font-weight: 700; color: {t['heading']};">{curr_aktivite['su']:.2f}L</span>
                        <span style="font-size: 10px; color: {t['ring_su']}; font-weight: 700; letter-spacing: 0.5px;">SU RİNGİ</span>
                    </div>
                </div>
            </div>
            """,
          unsafe_allow_html=True,
      )
      sc1, sc2 = st.columns(2)
      if sc1.button("+0.25L Su"):
        curr_aktivite["su"] = round(curr_aktivite["su"] + 0.25, 2)
        verileri_kaydet(aktif_user)
        st.rerun()
      if sc2.button("-0.25L Su"):
        if curr_aktivite["su"] >= 0.25:
          curr_aktivite["su"] = round(curr_aktivite["su"] - 0.25, 2)
          verileri_kaydet(aktif_user)
          st.rerun()

    st.divider()

    # --- TAKVİME VE HASSAS KATSAYIYA GÖRE EGZERSİZ VİDEOLARI ---
    st.subheader(
        f"📅 {secilen_tarih} Tarihine Özel Günlük 20 Min Egzersiz Reçetesi"
    )

    hash_gun = int(hashlib.md5(secilen_tarih.encode("utf-8")).hexdigest(), 16) % 3
    if hash_gun == 0:
      egzersiz_adi = "Growwithjo — 20 Min Fat Burning Walk"
      egzersiz_detay = "Tempolu ev yürüyüşü ve yağ yakıcı kardiyo seansı."
      egzersiz_link = (
          "https://www.youtube.com/results?search_query=growwithjo+20+min+workout"
      )
      met_val = 5.5
    elif hash_gun == 1:
      egzersiz_adi = "Nicole Pilates — 20 Min Full Body Flow"
      egzersiz_detay = "Tüm vücut esneme, sıkılaşma ve core odaklı akış."
      egzersiz_link = (
          "https://www.youtube.com/results?search_query=nicole+pilates+20+min"
      )
      met_val = 4.0
    else:
      egzersiz_adi = "Growwithjo — 20 Min Low Impact Cardio"
      egzersiz_detay = "Eklem dostu, terletici ve neşeli danslı kardiyo."
      egzersiz_link = (
          "https://www.youtube.com/results?search_query=growwithjo+low+impact"
      )
      met_val = 5.0

    kilo_suan = st.session_state.profil["mevcut_kilo"]
    katsayi = st.session_state.profil.get("egzersiz_katsayisi", 1.0)
    tahmini_video_kalorisi = round(
        ((met_val * 3.5 * kilo_suan / 200) * 20) * katsayi
    )

    st.markdown(
        f"""
        <div class="recipe-card">
            <div class="recipe-title">✨ Günün Önerilen Kanalı: {egzersiz_adi}</div>
            <div class="recipe-details">{egzersiz_detay}</div>
            <div style="margin-top:8px; font-weight:600; color:{t['accent']};">🔥 Bu egzersizi tamamlarsan kişisel katsayına göre yaklaşık <strong>{tahmini_video_kalorisi} kcal</strong> harcarsın!</div>
            <br>
            <a href="{egzersiz_link}" target="_blank" style="color: {t['accent']}; font-weight:600;">Egzersiz Videosunu Aç ➔</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    video_yapildi_mi = st.checkbox(
        f"✨ {secilen_tarih} tarihli 20 dakikalık bu egzersizi tamamladım!",
        value=curr_aktivite.get("video_tamamlandi", False),
    )
    if video_yapildi_mi != curr_aktivite.get("video_tamamlandi", False):
      curr_aktivite["video_tamamlandi"] = video_yapildi_mi
      verileri_kaydet(aktif_user)
      st.rerun()

    st.divider()

    # --- KUTUCUKLU (CHECKBOX) HİYERARŞİK ÖĞÜN EKLEME ALANI ---
    st.subheader("🍽️ Günlük Öğün Ekleme (A-F Kapsamlı Menü Listesi)")
    st.markdown(
        "Kategoriyi seçin, yediğiniz lezzetlerin yanındaki **kutucukları"
        " (checkbox)** işaretleyin ve 'Öğün Ekle' butonuna basın!"
    )

    col_cat1, col_cat2 = st.columns(2)
    secilen_kategori_adi = col_cat1.selectbox(
        "Menü Kategorisi Seçin", list(GENIS_MENU_VERITABASI.keys())
    )
    secilen_ogun_zamani = col_cat2.selectbox(
        "Öğün Zamanı", ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"]
    )

    kategori_urunleri = GENIS_MENU_VERITABASI[secilen_kategori_adi]

    st.markdown(
        f"**{secilen_kategori_adi}** altındaki lezzetler:",
        unsafe_allow_html=True,
    )

    secilen_urunler_listesi = []

    # Izgara şeklinde kutucuklu gösterim
    col_u1, col_u2 = st.columns(2)
    u_keys = list(kategori_urunleri.keys())

    for idx, u_name in enumerate(u_keys):
      u_data = kategori_urunleri[u_name]
      label_text = f"{u_name} — {u_data['kalori']} kcal (P:{u_data['protein']}g | K:{u_data['karb']}g | Y:{u_data['yag']}g)"

      target_col = col_u1 if idx % 2 == 0 else col_u2
      is_checked = target_col.checkbox(label_text, key=f"chk_{idx}_{u_name}")

      if is_checked:
        secilen_urunler_listesi.append((u_name, u_data))

    if st.button("Seçili Lezzetleri Öğünüme Ekle", use_container_width=True):
      if secilen_urunler_listesi:
        top_k, top_p, top_c, top_y = 0, 0, 0, 0
        eklenen_isimler = []

        for item_name, item_vals in secilen_urunler_listesi:
          top_k += item_vals["kalori"]
          top_p += item_vals["protein"]
          top_c += item_vals["karb"]
          top_y += item_vals["yag"]
          eklenen_isimler.append(item_name)

        st.session_state.gunluk_kayitlar.append({
            "Tarih": secilen_tarih,
            "Öğün": secilen_ogun_zamani,
            "Tarif": ", ".join(eklenen_isimler),
            "İçerik": f"{len(eklenen_isimler)} çeşit menü seçimi",
            "Kalori": round(top_k, 1),
            "Protein": round(top_p, 1),
            "Karbonhidrat": round(top_c, 1),
            "Yağ": round(top_y, 1),
        })
        verileri_kaydet(aktif_user)
        st.success(
            f"✨ {len(eklenen_isimler)} adet lezzet günlüğünüze eklendi!"
            f" Toplam: **{round(top_k)} kcal**"
        )
      else:
        st.warning("Lütfen eklemek istediğiniz ürünlerin kutucuğunu işaretleyin.")

    st.divider()

    # --- SEÇİLEN TARİHE AİT ÖĞÜN ÖZET TABLOSU ---
    st.subheader(f"📋 {secilen_tarih} Tarihli Öğün ve Besin Özeti")
    bugun_kayitlar = [
        k
        for k in st.session_state.gunluk_kayitlar
        if k["Tarih"] == secilen_tarih
    ]

    if bugun_kayitlar:
      df_bugun = pd.DataFrame(bugun_kayitlar)
      st.dataframe(
          df_bugun[
              [
                  "Öğün",
                  "Tarif",
                  "Kalori",
                  "Protein",
                  "Karbonhidrat",
                  "Yağ",
              ]
          ],
          use_container_width=True,
      )

      sum_k = df_bugun["Kalori"].sum()
      sum_p = df_bugun["Protein"].sum()
      sum_c = df_bugun["Karbonhidrat"].sum()
      sum_y = df_bugun["Yağ"].sum()

      st.markdown(
          f"""
            <div class="recipe-card">
                <div class="recipe-title">🔥 Günlük Toplam Makro İcmali</div>
                <div class="recipe-details">
                    • <strong>Toplam Kalori:</strong> <span style="font-weight:700; color:{t['accent']};">{round(sum_k, 1)} kcal</span><br>
                    • <strong>Toplam Protein:</strong> {round(sum_p, 1)} g<br>
                    • <strong>Toplam Karbonhidrat:</strong> {round(sum_c, 1)} g<br>
                    • <strong>Toplam Yağ:</strong> {round(sum_y, 1)} g
                </div>
            </div>
            """,
          unsafe_allow_html=True,
      )
    else:
      st.info("Bu tarihe ait henüz öğün kaydı bulunmuyor.")

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
      st.line_chart(
          haftalik_ozet.set_index("Tarih")[["Kalori"]], color=t["accent"]
      )
    else:
      st.info("Kayıt bulunmuyor.")

  # ----------------------------------------------------
  # TARİF & MALZEME YÖNETİMİ
  # ----------------------------------------------------
  elif menu == "Tarif & Malzeme Yönetimi":
    st.header("Tarif ve Malzeme Yönetim Paneli")
    tab_m, tab_t = st.tabs(
        ["1. Yeni Malzeme Ekle", "2. Gramaj Esaslı Tarif Oluştur"]
    )
    with tab_m:
      m_ad = st.text_input("Malzeme Adı")
      m_kal = st.number_input("100g Kalori", min_value=0.0, value=100.0)
      m_pro = st.number_input("100g Protein", min_value=0.0, value=10.0)
      m_kar = st.number_input("100g Karb", min_value=0.0, value=5.0)
      m_yag = st.number_input("100g Yağ", min_value=0.0, value=3.0)
      if st.button("Malzemeyi Kaydet"):
        if m_ad.strip():
          st.session_state.besin_veritabani[m_ad.strip().lower()] = {
              "kalori": m_kal,
              "protein": m_pro,
              "karb": m_kar,
              "yag": m_yag,
          }
          verileri_kaydet(aktif_user)
          st.success("Malzeme eklendi!")

    with tab_t:
      t_ad = st.text_input("Tarif Adı")
      secilen_malzemeler = st.multiselect(
          "Malzemeleri Seç", list(st.session_state.besin_veritabani.keys())
      )
      tarif_gramajlari = {}
      for m in secilen_malzemeler:
        gr = st.number_input(
            f"{m.title()} kaç gram/ml?",
            min_value=1.0,
            value=100.0,
            key=f"g_{m}",
        )
        tarif_gramajlari[m] = gr
      if st.button("Tarifi Kaydet"):
        if t_ad.strip() and tarif_gramajlari:
          st.session_state.hazir_tarifler[t_ad.strip()] = tarif_gramajlari
          verileri_kaydet(aktif_user)
          st.success("Tarif kaydedildi!")

  # ----------------------------------------------------
  # HESAP, TEMA SEÇİMİ, KALORİ AÇIĞI VEM EGZERSİZ KATSAYISI SİHİRBAZI
  # ----------------------------------------------------
  elif menu == "Hesap ve Hedefler":
    st.header("👤 Hesap, Tema Tonları ve Kalori Açığı Sihirbazı")

    p = st.session_state.profil

    mevcut_tema = p.get("tema", "Sonbahar Kremi")
    secilen_tema = st.selectbox(
        "Uygulama Tema Paleti Tonları",
        [
            "Sonbahar Kremi",
            "Sıcak Kahve & Toprak",
            "Gece / Kuğu Mavisi",
            "Zeytin Yeşili & Doğa",
            "Karamel Esintisi",
        ],
        index=[
            "Sonbahar Kremi",
            "Sıcak Kahve & Toprak",
            "Gece / Kuğu Mavisi",
            "Zeytin Yeşili & Doğa",
            "Karamel Esintisi",
        ].index(mevcut_tema)
        if mevcut_tema
        in [
            "Sonbahar Kremi",
            "Sıcak Kahve & Toprak",
            "Gece / Kuğu Mavisi",
            "Zeytin Yeşili & Doğa",
            "Karamel Esintisi",
        ]
        else 0,
    )

    st.divider()

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

    st.markdown("---")
    st.subheader("🎯 Kilo Verme / Alma Hedef Sihirbazı")
    c_h1, c_h2, c_h3 = st.columns(3)
    verilmek_istenen = c_h1.number_input(
        "Hedef Kilo Değişimi (kg)",
        min_value=0.5,
        max_value=50.0,
        value=float(p.get("verilmek_istenen_kilo", 3.0)),
        step=0.5,
    )
    hedef_gun = c_h2.number_input(
        "Hedeflenen Süre (Gün)",
        min_value=10,
        max_value=365,
        value=int(p.get("hedef_gun", 45)),
        step=5,
    )
    egzersiz_katsayi = c_h3.slider(
        "Egzersiz Kalori Katsayısı",
        min_value=0.8,
        max_value=1.5,
        value=float(p.get("egzersiz_katsayisi", 1.0)),
        step=0.05,
        help=(
            "Antrenman temponuza göre harcanan egzersiz kalorisini artırıp"
            " azaltır."
        ),
    )

    aktivite_seviyesi = st.selectbox(
        "Aktivite Düzeyi",
        [
            "Hareketsiz / Masa Başı",
            "Hafif Aktif (Haftada 1-3 gün)",
            "Orta Aktif (Haftada 3-5 gün)",
            "Çok Aktif",
        ],
    )

    if st.button("Bilgileri, Temayı ve Kalori Açığını Güncelle"):
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
      tdee = bmr * carpanlar[aktivite_seviyesi]

      toplam_verilecek_kcal = verilmek_istenen * 7700
      gunluk_acik = toplam_verilecek_kcal / hedef_gun
      tavsiye_edilen_kalori = tdee - gunluk_acik

      st.session_state.profil["cinsiyet"] = cinsiyet
      st.session_state.profil["yas"] = yas
      st.session_state.profil["boy"] = boy
      st.session_state.profil["mevcut_kilo"] = mevcut_kilo
      st.session_state.profil["hedef_kilo"] = hedef_kilo
      st.session_state.profil["verilmek_istenen_kilo"] = verilmek_istenen
      st.session_state.profil["hedef_gun"] = hedef_gun
      st.session_state.profil["egzersiz_katsayisi"] = egzersiz_katsayi
      st.session_state.profil["hedef_kalori"] = round(tavsiye_edilen_kalori)
      st.session_state.profil["tema"] = secilen_tema
      st.session_state.profil["setup_tamamlandi"] = True

      verileri_kaydet(aktif_user)
      st.success("✨ Tüm ayarlarınız kaydedildi! Yenileniyor...")
      st.rerun()

    st.markdown("---")
    st.subheader("📊 Kişiselleştirilmiş Kalori Açığı Raporu")
    if cinsiyet == "Kadın":
      bmr_k = (10 * mevcut_kilo) + (6.25 * boy) - (5 * yas) - 161
    else:
      bmr_k = (10 * mevcut_kilo) + (6.25 * boy) - (5 * yas) + 5
    tdee_k = bmr_k * 1.375
    toplam_kcal_ornek = verilmek_istenen * 7700
    gereken_acik = toplam_kcal_ornek / hedef_gun
    sonuc_kalori = tdee_k - gereken_acik

    st.markdown(
        f"""
        <div class="recipe-card">
            <div class="recipe-title">💡 Nokta Atışı Kalori Planı</div>
            <div class="recipe-details">
                • <strong>Günlük Harcanan Enerji (TDEE):</strong> {round(tdee_k)} kcal<br>
                • <strong>Hedeflenen Sürede Vermen Gereken Günlük Açık:</strong> {round(gereken_acik)} kcal / gün<br>
                • <strong>Alman Gereken Günlük Kalori:</strong> <strong style="color: {t['accent']}; font-size:16px;">{round(sonuc_kalori)} kcal</strong><br>
                • <strong>Egzersiz Kalori Katsayısı:</strong> {egzersiz_katsayi}x<br>
                <em>{hedef_gun} günde {verilmek_istenen} kg vermek için bu kalori dengesini korumalısın!</em>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
