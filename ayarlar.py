"""
ayarlar.py - Tek sayfalık ayarlar paneli

Eskiden "Ayarlar" düğmesi 9 adımlık kurulum sihirbazını baştan başlatıyordu;
kullanıcı sadece temasını değiştirmek isterken bütün soruları tekrar
cevaplamak zorunda kalıyordu. Bu panel mevcut değerleri tek ekranda gösterir
ve istediğini değiştirip kaydetmesine izin verir.

app.py içinde:
    from ayarlar import ayarlar_paneli
    if st.session_state.get("ayarlar_acik"):
        ayarlar_paneli(...); st.stop()
"""

import datetime

import streamlit as st

from diller import DIL_LISTESI, t, dil_ayarla


def ayarlar_paneli(profil, temalar, aktivite_duzeyleri, kaydet,
                   hesapla_bmr_ve_hedef, haftalik_hiz, guvenlik_uyarilari):
    """Ayarlar ekranını çizer. Kapatıldığında True döner."""
    st.markdown(f'<div class="nova-header kucuk">N O V A</div>', unsafe_allow_html=True)

    with st.container(key="novakart2"):
        st.markdown(f"<h2 style='text-align:center;'>{t('Ayarlar')}</h2>", unsafe_allow_html=True)

        # ---------------------------------------------------------- Dil
        st.markdown(f"#### {t('Dil')}")
        kodlar = list(DIL_LISTESI.keys())
        mevcut_dil = profil.get("dil", "tr")
        if mevcut_dil not in kodlar:
            mevcut_dil = "tr"
        yeni_dil = st.selectbox(
            t("Dil"), kodlar, index=kodlar.index(mevcut_dil),
            format_func=lambda k: DIL_LISTESI[k], key="ayar_dil",
            label_visibility="collapsed")

        st.divider()

        # ------------------------------------------------------ Bilgilerin
        st.markdown(f"#### {t('Bilgilerin')}")
        ad = st.text_input(t("Adın"), value=profil.get("ad", ""), key="ayar_ad")

        c1, c2 = st.columns(2)
        with c1:
            cinsiyetler = ["Kadın", "Erkek"]
            mevcut_c = profil.get("cinsiyet", "Kadın")
            if mevcut_c not in cinsiyetler:
                mevcut_c = "Kadın"
            cinsiyet = st.selectbox(
                t("Cinsiyetin nedir?"), cinsiyetler,
                index=cinsiyetler.index(mevcut_c),
                format_func=t, key="ayar_cinsiyet")
            boy = st.number_input(t("Boy (cm)"), min_value=100, max_value=250,
                                  value=int(profil.get("boy", 165)), key="ayar_boy")
        with c2:
            bu_yil = datetime.date.today().year
            dogum = st.number_input(t("Yıl"), min_value=bu_yil - 100, max_value=bu_yil - 10,
                                    value=int(profil.get("dogum_yili", 2000)), key="ayar_dogum")
            kilo = st.number_input(t("Kilo (kg)"), min_value=30.0, max_value=300.0,
                                   value=float(profil.get("mevcut_kilo", 60.0)),
                                   step=0.1, key="ayar_kilo")

        st.divider()

        # --------------------------------------------------------- Hedefin
        st.markdown(f"#### {t('Hedefin')}")
        amac_secenekleri = ["Kilo vermek istiyorum", "Kilomu korumak istiyorum",
                            "Kilo almak istiyorum", "Kas kazanmak istiyorum",
                            "Sağlıklı beslenmek istiyorum"]
        amaclar = st.multiselect(
            t("Hedeflerin (Birden fazla seçebilirsin)"), amac_secenekleri,
            default=[a for a in profil.get("amaclar", []) if a in amac_secenekleri],
            format_func=t, key="ayar_amaclar")

        h1, h2 = st.columns(2)
        with h1:
            hedef_kilo = st.number_input(t("Hedef Kilo (kg)"), min_value=35.0, max_value=300.0,
                                         value=float(profil.get("hedef_kilo", 55.0)),
                                         step=0.5, key="ayar_hedef_kilo")
        with h2:
            hedef_sure = st.number_input(t("Hedefe Ulaşma Süresi (Ay)"), min_value=1, max_value=60,
                                         value=int(profil.get("hedef_sure_ay", 2)),
                                         key="ayar_hedef_sure")

        akt_listesi = list(aktivite_duzeyleri.keys())
        mevcut_akt = profil.get("aktivite", akt_listesi[1])
        if mevcut_akt not in akt_listesi:
            mevcut_akt = akt_listesi[1]
        aktivite = st.selectbox(t("Günlük hareket düzeyin"), akt_listesi,
                                index=akt_listesi.index(mevcut_akt),
                                format_func=t, key="ayar_aktivite")

        # Değişikliklerin sonucunu kaydetmeden önce göster
        onizleme = dict(profil)
        onizleme.update({"cinsiyet": cinsiyet, "boy": boy, "dogum_yili": dogum,
                         "mevcut_kilo": kilo, "hedef_kilo": hedef_kilo,
                         "hedef_sure_ay": hedef_sure, "aktivite": aktivite,
                         "amaclar": amaclar})
        try:
            _, _, _, yeni_hedef = hesapla_bmr_ve_hedef(onizleme)
            st.info(f"{t('Günlük Hedefin')}: {round(yeni_hedef)} kcal")
        except Exception:  # noqa: BLE001
            pass

        hiz = haftalik_hiz(onizleme)
        if hiz > 1.0:
            st.warning(t("Bu tempo hızlı. Güvenli aralık genelde haftada 0,5-1 kilodur; "
                         "süreyi uzatmanı öneririm."))
        for uyari in guvenlik_uyarilari(onizleme):
            st.warning(uyari)

        st.divider()

        # --------------------------------------------------------- Görünüm
        st.markdown(f"#### {t('Görünüm')}")
        tema_listesi = list(temalar.keys())
        mevcut_tema = profil.get("tema", tema_listesi[0])
        if mevcut_tema not in tema_listesi:
            mevcut_tema = tema_listesi[0]
        tema = st.selectbox(t("Nova Deneyimin İçin Bir Tema Seç"), tema_listesi,
                            index=tema_listesi.index(mevcut_tema), key="ayar_tema")

        st.divider()

        # ---------------------------------------------------------- Kaydet
        k1, k2 = st.columns(2)
        if k1.button(t("Kaydet"), use_container_width=True, type="primary", key="ayar_kaydet"):
            profil.update({
                "dil": yeni_dil, "ad": ad, "cinsiyet": cinsiyet, "boy": boy,
                "dogum_yili": dogum, "mevcut_kilo": kilo, "hedef_kilo": hedef_kilo,
                "hedef_sure_ay": hedef_sure, "aktivite": aktivite,
                "amaclar": amaclar, "tema": tema,
            })
            dil_ayarla(yeni_dil)
            kaydet()
            st.session_state["ayarlar_acik"] = False
            st.success(t("Değişikliklerin kaydedildi."))
            st.rerun()

        if k2.button(t("Ayarlardan çık"), use_container_width=True, key="ayar_kapat"):
            st.session_state["ayarlar_acik"] = False
            st.rerun()

        # Kurulumu baştan yapmak isteyen için ayrı ve gizli bir yol
        with st.expander(t("Kurulum sorularını baştan cevapla")):
            if st.button(t("Kurulum sorularını baştan cevapla"),
                         key="ayar_kurulum_sifirla", use_container_width=True):
                profil["setup_tamamlandi"] = False
                st.session_state["onboarding_step"] = 1
                st.session_state["ayarlar_acik"] = False
                kaydet()
                st.rerun()
