"""
tarif.py - Tarif ve menü oluşturucu

Birden çok malzemeyi birleştirip tek bir yemek haline getirir. "Hamburger menü"
gibi birden çok parçadan oluşan şeyleri her seferinde tek tek eklemek yerine bir
kez kurup kaydetmeyi sağlar; kaydedilen tarif aramada normal bir yemek gibi çıkar.

Hesap tamamen malzemelerden gelir; hiçbir değer tahmin edilmez.
Tarifin toplamı malzemelerin toplamıdır, porsiyon başı değer de bu toplamın
porsiyon sayısına bölünmesidir.

yemek_arama.py içinden çağrılır: sekme_tarif(...)
"""

import streamlit as st

from diller import t, h, aktif_dil

ANAHTAR = "tarif_malzemeleri"
AD_ANAHTARI = "tarif_adi"


def _malzemeler():
    return st.session_state.setdefault(ANAHTAR, [])


def _toplamlar(malzemeler):
    """Malzeme listesinin toplam gram, protein, karbonhidrat, yağ değeri."""
    gram = sum(m["gram"] for m in malzemeler)
    p = sum(m["p"] * m["gram"] / 100.0 for m in malzemeler)
    k = sum(m["k"] * m["gram"] / 100.0 for m in malzemeler)
    y = sum(m["y"] * m["gram"] / 100.0 for m in malzemeler)
    ekstra = {}
    for m in malzemeler:
        for alan, deger in (m.get("ekstra") or {}).items():
            try:
                ekstra[alan] = ekstra.get(alan, 0.0) + float(deger) * m["gram"] / 100.0
            except (TypeError, ValueError):
                continue
    return gram, p, k, y, ekstra


def sekme_tarif(df, db, kullanici, tarih, ogun, *, ara_fn, liste_ara_fn,
                kullanici_yemekleri_fn, yemek_kaydet_fn, yemek_sil_fn,
                yemek_yap_fn, kayit_yap_fn, kcal_fn, off_ara_fn=None,
                offtan_fn=None, onbellege_yaz_fn=None):
    """Tarif oluşturma sekmesini çizer.

    Dışarıdan işlev alıyor çünkü arama ve kayıt mantığı yemek_arama.py'de
    duruyor; burada kopyalamak yerine ödünç alınıyor.
    """
    st.caption(t("Birden çok parçadan oluşan bir öğünü tek seferde kur. "
                 "Örnek: hamburger menü için ekmek, köfte, peynir, patates ve içecek ekle; "
                 "sonra tarifi kaydet, bir daha tek tek eklemen gerekmesin."))

    malzemeler = _malzemeler()

    # ------------------------------------------------------- Malzeme ekleme
    sorgu = st.text_input(t("Malzeme ara"), key="tarif_arama", max_chars=60,
                          placeholder=t("Örn: hamburger ekmeği, dana köfte, patates kızartması"))

    if len(sorgu.strip()) >= 2:
        sonuclar = ara_fn(df, sorgu, limit=8)
        sonuclar += liste_ara_fn(kullanici_yemekleri_fn(db, kullanici, "kendi"), sorgu, limit=5)
        if off_ara_fn and st.session_state.get("tarif_marka_dahil"):
            try:
                disaridan = off_ara_fn(sorgu, aktif_dil(), (st.session_state.get('profil') or {}).get('ulke', ''))
                if disaridan:
                    if onbellege_yaz_fn:
                        onbellege_yaz_fn(db, disaridan)
                    sonuclar += [offtan_fn(u) for u in disaridan][:5]
            except Exception:  # noqa: BLE001
                st.caption(t("Marka ürünlerine şu an ulaşılamadı."))

        if not sonuclar:
            st.caption(t("Bulamadım. \"Kendi yemeğim\" sekmesinden ekleyip buraya "
                         "malzeme olarak koyabilirsin."))
        for i, y in enumerate(sonuclar[:10]):
            c1, c2, c3 = st.columns([5, 2, 1])
            etiket = y["ad"] + (f" · {y['marka']}" if y.get("marka") else "")
            c1.markdown(f"**{etiket}**  \n{round(y['kcal'])} kcal / 100 g")
            gram = c2.number_input(t("gram"), min_value=1, max_value=3000,
                                   value=int(y.get("gram") or 100), step=5,
                                   key=f"tarif_gram_{i}", label_visibility="collapsed")
            if c3.button(t("Ekle"), key=f"tarif_ekle_{i}", use_container_width=True):
                malzemeler.append({
                    "ad": etiket, "gram": int(gram),
                    "p": y["p"], "k": y["k"], "y": y["y"],
                    "ekstra": y.get("ekstra") or {},
                })
                # Arama kutusu elle temizlenmez: Streamlit, bir aracın değerini
                # çizildikten sonra değiştirmeye izin vermiyor ve hata veriyor.
                # Metin yerinde kalsın, kullanıcı üstüne yazar.
                st.rerun()

    st.checkbox(t("Marka ürünlerinde de ara (Open Food Facts)"), value=False,
                key="tarif_marka_dahil")

    # ------------------------------------------------------- Tarifin içeriği
    if not malzemeler:
        st.info(t("Henüz malzeme eklemedin. Yukarıdan arayıp ekle."))
        return None

    st.divider()
    st.markdown(h("#### Tarifin"))

    for i, m in enumerate(list(malzemeler)):
        kcal = round(kcal_fn(m["p"], m["k"], m["y"]) * m["gram"] / 100)
        c1, c2 = st.columns([8, 1])
        c1.markdown(f"{m['ad']} — **{m['gram']} g** · {kcal} kcal")
        if c2.button(t("Çıkar"), key=f"tarif_cikar_{i}"):
            malzemeler.pop(i)
            st.rerun()

    gram, p, k, y, ekstra = _toplamlar(malzemeler)
    toplam_kcal = round(kcal_fn(p, k, y))
    st.markdown(h(f"**{t('Toplam')}: {int(gram)} g · {toplam_kcal} kcal · "
                  f"{t('Protein')} {p:.1f} g · {t('Karbonhidrat')} {k:.1f} g · {t('Yağ')} {y:.1f} g**"))

    # ------------------------------------------------------------- Porsiyon
    porsiyon_sayisi = st.number_input(
        t("Bu tarif kaç porsiyon?"), min_value=1, max_value=50, value=1, step=1,
        key="tarif_porsiyon",
        help=t("Tek kişilik bir menü için 1 bırak. Dört kişilik bir tencere yemeği "
               "pişirdiysen 4 yaz; Nova porsiyon başı değeri kendi hesaplar."))

    porsiyon_g = gram / porsiyon_sayisi
    porsiyon_kcal = toplam_kcal / porsiyon_sayisi
    if porsiyon_sayisi > 1:
        st.caption(f"{t('Bir porsiyon')}: {int(porsiyon_g)} g · {round(porsiyon_kcal)} kcal · "
                   f"{t('Protein')} {p / porsiyon_sayisi:.1f} g · "
                   f"{t('Karbonhidrat')} {k / porsiyon_sayisi:.1f} g · "
                   f"{t('Yağ')} {y / porsiyon_sayisi:.1f} g")

    ad = st.text_input(t("Tarifin adı"), key=AD_ANAHTARI, max_chars=60,
                       placeholder=t("Örn: Hamburger menü"))

    # ---------------------------------------------------------------- İşlemler
    d1, d2, d3 = st.columns(3)
    sonuc = None

    if d1.button(t("Bugüne ekle"), key="tarif_bugune", use_container_width=True, type="primary"):
        # 100 gram karşılığına çevrilir; içeride her şey böyle tutuluyor
        oran = 100.0 / max(porsiyon_g, 1)
        yemek = yemek_yap_fn(ad.strip() or t("Tarif"), p / porsiyon_sayisi * oran,
                             k / porsiyon_sayisi * oran, y / porsiyon_sayisi * oran,
                             gram=int(porsiyon_g), kaynak=t("Tarifin"),
                             ekstra={a: d / porsiyon_sayisi * oran for a, d in ekstra.items()})
        sonuc = [kayit_yap_fn(yemek, int(porsiyon_g), tarih, ogun,
                              yemek["p"], yemek["k"], yemek["y"])]

    if d2.button(t("Tarifi kaydet"), key="tarif_kaydet", use_container_width=True):
        if not ad.strip():
            st.error(t("Tarifin adını yaz."))
        else:
            oran = 100.0 / max(porsiyon_g, 1)
            yemek = yemek_yap_fn(ad.strip(), p / porsiyon_sayisi * oran,
                                 k / porsiyon_sayisi * oran, y / porsiyon_sayisi * oran,
                                 gram=int(porsiyon_g), kaynak=t("Tarifin"),
                                 ekstra={a: d / porsiyon_sayisi * oran for a, d in ekstra.items()})
            if yemek_kaydet_fn(db, kullanici, "kendi", yemek):
                st.success(f"{ad.strip()} " + t("kaydedildi. Artık aramada çıkacak."))
                st.session_state[ANAHTAR] = []
                st.rerun()
            else:
                st.error(t("Veritabanına bağlanılamadı, kaydedilemedi."))

    if d3.button(t("Tarifi temizle"), key="tarif_temizle", use_container_width=True):
        st.session_state[ANAHTAR] = []
        st.rerun()

    if sonuc:
        st.session_state[ANAHTAR] = []
    return sonuc
