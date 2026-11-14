"""
meal_scan.py - Öğün taraması sayfası (fotoğraf, kamera ya da sesle/yazarak anlatım)

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

KAYNAKLAR = ["Galeri", "Kamera", "Anlat"]


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
        satir = {
            "Yemek": item["name"],
            "Gram": grams,
            "Kalori": round(kcal(protein, carbs, fat)),
            "Protein (g)": round(protein, 1),
            "Karb. (g)": round(carbs, 1),
            "Yağ (g)": round(fat, 1),
        }
        # Model biliyorsa lif, şeker ve tuz da taşınır (mikro besin takibi için)
        for alan, ad in (("fiber_per_100g", "Lif (g)"), ("sugar_per_100g", "Şeker (g)"), ("salt_per_100g", "Tuz (g)")):
            if item.get(alan) is not None:
                satir[ad] = round(float(item[alan]) * factor, 2)
        rows.append(satir)

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

    gosterilecek = ["Yemek", "Gram", "Kalori", "Protein (g)", "Karb. (g)", "Yağ (g)"]
    st.dataframe(df[gosterilecek], hide_index=True)

    if data.get("assumptions"):
        st.info(data["assumptions"])
    st.caption("Değerler yapay zekanın tahminidir ve gerçek değerden sapabilir.")

    clicked = st.button("Günlüğe ekle", type="primary", key=f"save_{scan_id}")
    support_slot()
    if clicked:
        totals["items"] = [{k: v for k, v in r.items() if not (isinstance(v, float) and pd.isna(v))} for r in df.to_dict("records")]
        return totals
    return None


def _sonucu_goster(data, scan_id, bos_mesaj):
    if not data["is_food"] or not data["items"]:
        st.info(bos_mesaj)
        return None
    return _render_editor(data, scan_id)


def _anlatim_akisi():
    """Ne yediğini sesle ya da yazarak anlat; yapay zeka kalemlere ayırsın."""
    st.caption("Örn: \"Kahvaltıda iki yumurta, bir dilim tam buğday ekmeği, yarım avuç ceviz ve şekersiz çay\"")
    ses = None
    if hasattr(st, "audio_input"):
        ses = st.audio_input("Sesle anlat", key="ogun_ses")
    yazi = st.text_area("ya da yazarak anlat", max_chars=500, key="ogun_yazi", height=90)
    if not ses and not yazi.strip():
        return None

    ses_bytes = ses.getvalue() if ses else None
    kimlik = hashlib.md5((ses_bytes or b"") + yazi.strip().encode("utf-8")).hexdigest()[:10]

    if st.button("Analiz et", type="primary", key="anlatim_analiz"):
        try:
            with st.spinner("Anlattıkların analiz ediliyor..."):
                metin = yazi.strip() or "Ses kaydında anlattığım öğünü analiz et."
                result = run_mode("voice", metin, audio_bytes=ses_bytes, audio_mime=getattr(ses, "type", None) or "audio/wav")
            st.session_state["anlatim_sonuc"] = result
            st.session_state["anlatim_kimlik"] = kimlik
        except QuotaError as e:
            show_limit_reached(str(e))
            return None
        except Exception as e:  # noqa: BLE001
            st.error(friendly_error(e))
            return None

    data = st.session_state.get("anlatim_sonuc")
    if not data or st.session_state.get("anlatim_kimlik") != kimlik:
        return None
    return _sonucu_goster(data, "a" + kimlik, "Anlattıklarında yiyecek bulamadım. Ne yediğini biraz daha açık anlatıp tekrar dene.")


def _flow():
    source = st.radio("Kaynak", KAYNAKLAR, horizontal=True, label_visibility="collapsed", key="ogun_kaynak")
    if source == "Anlat":
        return _anlatim_akisi()
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
    return _sonucu_goster(data, file_id, "Fotoğrafta yiyecek bulamadım. Daha yakından ve iyi ışıkta çekip tekrar dene.")


def meal_scan_page():
    """Öğün tarama ekranını çizer. 'Günlüğe ekle'ye basılırsa toplamları döndürür."""
    st.subheader("Öğün taraması")
    st.caption("Fotoğraf ya da ses kaydı analiz için Google Gemini'ye gönderilir.")
    quota_slot = st.empty()
    try:
        return _flow()
    finally:
        # Hak sayısı analizden sonra güncellensin diye en sonda çizilir
        with quota_slot.container():
            kaynak = st.session_state.get("ogun_kaynak")
            quota_caption("voice" if kaynak == "Anlat" else "meal")
