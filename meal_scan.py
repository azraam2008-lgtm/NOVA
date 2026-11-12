"""
meal_scan.py - Öğün taraması sayfası

    from meal_scan import meal_scan_page
    totals = meal_scan_page()
    if totals:        # kullanıcı "Günlüğe ekle"ye bastıysa
        kaydet(totals)   # {"kcal", "protein", "carbs", "fat", "grams", "items"}
"""

import hashlib

import pandas as pd
import streamlit as st

from nova_core import (
    QuotaError,
    friendly_error,
    prepare_image,
    quota_caption,
    run_mode,
    show_limit_reached,
    support_slot,
)
from nutrition_check import kcal, verify


def _render_editor(data: dict, scan_id: str):
    st.markdown("#### Değerleri düzenle")
    st.caption("Gramajı kaydırarak değiştir. Bir kalemi çıkarmak için 0'a çek.")
    prefer_ref = st.toggle(
        "Referans değerlerle doğrula",
        value=True,
        help="Yumurta, elma gibi basit besinlerde model değeri referanstan çok sapıyorsa referansı kullanır.",
        key="meal_verify_toggle",
    )

    rows = []
    for i, item in enumerate(data["items"]):
        check = verify(
            item["name"],
            item["protein_per_100g"],
            item["carbs_per_100g"],
            item["fat_per_100g"],
            prefer_reference=prefer_ref,
        )
        p100, c100, f100 = check.values

        start = max(5, min(int(round(item["grams"] / 5) * 5), 2000))
        grams = st.slider(
            item["name"],
            min_value=0,
            max_value=max(300, start * 3),
            value=start,
            step=5,
            key=f"grams_{scan_id}_{i}",
        )
        for message in check.messages:
            st.caption(message)
        if item["confidence"] < 0.6:
            st.caption("Bu kalemden emin değilim. Gramajı kontrol et.")

        factor = grams / 100
        protein, carbs, fat = p100 * factor, c100 * factor, f100 * factor
        rows.append(
            {
                "Yemek": item["name"],
                "Gram": grams,
                "Kalori": round(kcal(protein, carbs, fat)),
                "Protein (g)": round(protein, 1),
                "Karb. (g)": round(carbs, 1),
                "Yağ (g)": round(fat, 1),
            }
        )

    df = pd.DataFrame(rows)
    df = df[df["Gram"] > 0]
    if df.empty:
        st.info("Tüm kalemler 0 gram. En az birini artır.")
        return None

    totals = {
        "kcal": int(df["Kalori"].sum()),
        "protein": round(df["Protein (g)"].sum(), 1),
        "carbs": round(df["Karb. (g)"].sum(), 1),
        "fat": round(df["Yağ (g)"].sum(), 1),
        "grams": int(df["Gram"].sum()),
    }

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kalori", f'{totals["kcal"]} kcal')
    c2.metric("Protein", f'{totals["protein"]} g')
    c3.metric("Karbonhidrat", f'{totals["carbs"]} g')
    c4.metric("Yağ", f'{totals["fat"]} g')

    st.dataframe(df, hide_index=True)

    if data.get("assumptions"):
        st.info(data["assumptions"])
    st.caption("Değerler fotoğraftan yapılan tahmindir ve gerçek değerden sapabilir.")

    clicked = st.button("Günlüğe ekle", type="primary", key=f"save_{scan_id}")
    support_slot()
    if clicked:
        totals["items"] = df.to_dict("records")
        return totals
    return None


def _flow():
    source = st.radio("Kaynak", ["Galeri", "Kamera"], horizontal=True, label_visibility="collapsed")
    if source == "Kamera":
        file = st.camera_input("Yemeğin fotoğrafını çek")
    else:
        file = st.file_uploader("Yemeğin fotoğrafını seç", type=["jpg", "jpeg", "png", "webp"])

    hint = st.text_input(
        "Not (isteğe bağlı)",
        placeholder="Örn: 1 yemek kaşığı zeytinyağı kullandım",
        max_chars=200,
    )
    if not file:
        return None

    file_id = hashlib.md5(file.getvalue()).hexdigest()[:10]
    st.image(file, width=320)

    if st.button("Analiz et", type="primary"):
        try:
            with st.spinner("Öğün analiz ediliyor..."):
                image_bytes = prepare_image(file)
                result = run_mode("meal", hint.strip(), image_bytes=image_bytes)
            st.session_state["scan_result"] = result
            st.session_state["scan_file"] = file_id
        except QuotaError as e:
            show_limit_reached(str(e))
            return None
        except Exception as e:  # noqa: BLE001
            st.error(friendly_error(e))
            return None

    # Sonuç sadece analiz edilen fotoğraf hâlâ seçiliyse gösterilir
    data = st.session_state.get("scan_result")
    if not data or st.session_state.get("scan_file") != file_id:
        return None
    if not data["is_food"] or not data["items"]:
        st.info("Fotoğrafta yiyecek bulamadım. Daha yakından ve iyi ışıkta çekip tekrar dene.")
        return None
    return _render_editor(data, file_id)


def meal_scan_page():
    """Öğün tarama ekranını çizer. 'Günlüğe ekle'ye basılırsa toplamları döndürür."""
    st.subheader("Öğün taraması")
    st.caption("Fotoğraf analiz için Google Gemini'ye gönderilir.")
    quota_slot = st.empty()
    try:
        return _flow()
    finally:
        # Hak sayısı analizden sonra güncellensin diye en sonda çizilir
        with quota_slot.container():
            quota_caption("meal")
