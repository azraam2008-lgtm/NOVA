"""
app_example.py - Nova'nın üç özelliğini sekmelerde birleştiren örnek.
Kendi app.py'ne şu parçaları taşı. Bu dosyayı olduğu gibi de çalıştırabilirsin:
    streamlit run app_example.py
"""
import streamlit as st

from meal_scan import meal_scan_page
from nova_pages import ask_page, coach_page

st.set_page_config(page_title="Nova")
st.title("Nova")

tab_meal, tab_coach, tab_ask = st.tabs(["Öğün taraması", "Antrenman koçu", "Soru sor"])

with tab_meal:
    totals = meal_scan_page()
    if totals:
        # Kendi kayıt sistemine bağla (veritabanı, dosya vb.)
        st.toast(f'{totals["kcal"]} kcal günlüğe eklendi')

with tab_coach:
    workout = coach_page()
    if workout:
        # Kendi antrenman günlüğüne kaydet
        pass

with tab_ask:
    ask_page()
