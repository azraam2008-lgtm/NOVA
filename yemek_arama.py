"""
yemek_arama.py - Nova'nın yemek bulma ekranı

Dört yol bir arada:
    Ara        : yazdıkça filtreleyen arama (kendi veritabanın + kendi yemeklerin + marka ürünleri)
    Barkod     : fotoğraftan ya da elle barkod -> önbellek -> Open Food Facts -> yapay zekayla etiket okuma
    Favoriler  : yıldızladıkların, son yedikleri ve "dünkü öğünü kopyala"
    Kendi yemeğim : veritabanında olmayan bir yemeği 100 g değerleriyle kaydet

app.py içinde kullanım:

    from yemek_arama import yemek_arama_sayfasi

    kayitlar = yemek_arama_sayfasi(df_yemek, supabase, aktif_user, secilen_tarih, secilen_ogun,
                                   st.session_state.gunluk_kayitlar)
    if kayitlar:
        st.session_state.gunluk_kayitlar.extend(kayitlar)
        verileri_kaydet(aktif_user)
        st.rerun()

Gerekli Supabase tabloları: urun_onbellek, kullanici_yemekleri (supabase_kurulum.sql)
"""

import unicodedata

import streamlit as st

import besin_kaynaklari as bk
from nutrition_check import kcal as kcal_hesapla
from nutrition_check import verify

_TR = str.maketrans("çğıöşüÇĞİÖŞÜâîû", "cgiosuCGIOSUaiu")


def _norm(metin):
    metin = (metin or "").replace("İ", "i").replace("I", "ı").lower().translate(_TR)
    return " ".join("".join(c if c.isalnum() else " " for c in metin).split())


# ----------------------------------------------------------- Ortak yemek biçimi
# Her kaynak bu biçime çevrilir. Değerler 100 GRAM içindir.
#   {"ad", "marka", "kaynak", "p", "k", "y", "kcal", "gram", "kod", "ekstra": {...}}
def _yemek(ad, p, k, y, gram=100, marka="", kaynak="", kod="", ekstra=None):
    p, k, y = max(float(p), 0.0), max(float(k), 0.0), max(float(y), 0.0)
    return {
        "ad": ad, "marka": marka or "", "kaynak": kaynak, "kod": kod or "",
        "p": round(p, 1), "k": round(k, 1), "y": round(y, 1),
        "kcal": round(kcal_hesapla(p, k, y)),
        "gram": int(gram) if gram else 100,
        "ekstra": {a: b for a, b in (ekstra or {}).items() if b is not None},
    }


def _yerelden(satir):
    """CSV satırı porsiyon başına değer taşır; 100 grama indirgenir."""
    try:
        ref = float(satir.get("Gramaj (g/ml)", 100) or 100)
    except (TypeError, ValueError):
        ref = 100.0
    if ref <= 0:
        ref = 100.0
    oran = 100.0 / ref
    return _yemek(
        str(satir["Yemek Adı"]),
        float(satir["Protein (g)"]) * oran,
        float(satir["Karbonhidrat (g)"]) * oran,
        float(satir["Yağ (g)"]) * oran,
        gram=ref,
        kaynak="Nova",
    )


def _offtan(u):
    return _yemek(
        u["ad"], u["protein"], u["karb"], u["yag"],
        gram=u.get("porsiyon") or 100,
        marka=u.get("marka", ""),
        kaynak="Marka ürünü",
        kod=u.get("kod", ""),
        ekstra={"Lif (g)": u.get("lif"), "Şeker (g)": u.get("seker"),
                "Tuz (g)": u.get("tuz"), "Doymuş yağ (g)": u.get("doymus_yag")},
    )


# ------------------------------------------------------- Kullanıcının yemekleri
def _kullanici_yemekleri(db, kullanici, tur):
    if db is None or not kullanici:
        return []
    anahtar = f"_ky_{tur}"
    if anahtar not in st.session_state:
        try:
            res = db.table("kullanici_yemekleri").select("ad, veri").eq("kullanici", kullanici).eq("tur", tur).execute()
            st.session_state[anahtar] = [r["veri"] for r in (res.data or []) if r.get("veri")]
        except Exception:  # noqa: BLE001
            st.session_state[anahtar] = []
    return st.session_state[anahtar]


def _yemek_kaydet(db, kullanici, tur, yemek):
    if db is None or not kullanici:
        st.warning("Veritabanına bağlanılamadı, kaydedilemedi.")
        return False
    try:
        db.table("kullanici_yemekleri").upsert(
            {"kullanici": kullanici, "tur": tur, "ad": yemek["ad"], "veri": yemek},
            on_conflict="kullanici,tur,ad",
        ).execute()
        st.session_state.pop(f"_ky_{tur}", None)
        return True
    except Exception as e:  # noqa: BLE001
        st.warning(f"Kaydedilemedi: {e}")
        return False


def _yemek_sil(db, kullanici, tur, ad):
    if db is None:
        return
    try:
        db.table("kullanici_yemekleri").delete().eq("kullanici", kullanici).eq("tur", tur).eq("ad", ad).execute()
        st.session_state.pop(f"_ky_{tur}", None)
    except Exception:  # noqa: BLE001
        pass


# ----------------------------------------------------------------- Arama
@st.cache_data(show_spinner=False)
def _yerel_dizin(adlar):
    return [_norm(a) for a in adlar]


def _yerel_ara(df, sorgu, limit=25):
    if df is None or df.empty or "Yemek Adı" not in df.columns:
        return []
    adlar = df["Yemek Adı"].astype(str).tolist()
    dizin = _yerel_dizin(tuple(adlar))
    q = _norm(sorgu)
    if not q:
        return []
    bulunan = []
    for konum, anahtar in enumerate(dizin):
        if q in anahtar:
            # Baştan eşleşen önce gelsin
            bulunan.append((0 if anahtar.startswith(q) else 1, len(anahtar), konum))
    bulunan.sort()
    return [_yerelden(df.iloc[k[2]]) for k in bulunan[:limit]]


def _liste_ara(yemekler, sorgu, limit=15):
    q = _norm(sorgu)
    if not q:
        return []
    return [y for y in yemekler if q in _norm(y["ad"]) or q in _norm(y.get("marka", ""))][:limit]


# ------------------------------------------------------------- Ekleme paneli
def _etiket(y):
    parcalar = [y["ad"]]
    if y.get("marka"):
        parcalar.append(y["marka"])
    parcalar.append(f'{y["kcal"]} kcal/100 g')
    if y.get("kaynak"):
        parcalar.append(y["kaynak"])
    return " · ".join(parcalar)


def _kayit_yap(y, gram, tarih, ogun, p100, k100, y100):
    oran = gram / 100.0
    protein, karb, yag = p100 * oran, k100 * oran, y100 * oran
    ad = y["ad"] if not y.get("marka") else f'{y["ad"]} ({y["marka"]})'
    kayit = {
        "Tarih": tarih, "Öğün": ogun, "Tarif": f"{ad} ({int(gram)} g)",
        "Kalori": round(kcal_hesapla(protein, karb, yag)),
        "Protein": round(protein, 1), "Karbonhidrat": round(karb, 1), "Yağ": round(yag, 1),
    }
    for alan, deger in (y.get("ekstra") or {}).items():
        try:
            kayit[alan] = round(float(deger) * oran, 2)
        except (TypeError, ValueError):
            pass
    return kayit


def _ekle_paneli(y, anahtar, db, kullanici, tarih, ogun):
    """Seçilen yemek için gram girişi, ince ayar ve ekleme. Eklenirse kayıt sözlüğü döner."""
    st.markdown(f"**{y['ad']}**" + (f" · {y['marka']}" if y.get("marka") else ""))

    kontrol = verify(y["ad"], y["p"], y["k"], y["y"])
    p100, k100, y100 = kontrol.values
    for mesaj in kontrol.messages:
        st.caption(mesaj)

    st.caption(f"100 g: {round(kcal_hesapla(p100, k100, y100))} kcal · P {p100} g · K {k100} g · Y {y100} g"
               + (f" · kaynak: {y['kaynak']}" if y.get("kaynak") else ""))

    c1, c2 = st.columns([2, 1])
    gram = c1.number_input("Yediğin miktar (gram)", min_value=5, max_value=3000,
                           value=int(y.get("gram") or 100), step=5, key=f"gram_{anahtar}")

    with st.expander("İçeriği kendine göre ayarla"):
        oran = gram / 100.0
        pp = st.number_input("Protein (g)", 0.0, 400.0, float(round(p100 * oran, 1)), 0.5, key=f"p_{anahtar}")
        kk = st.number_input("Karbonhidrat (g)", 0.0, 600.0, float(round(k100 * oran, 1)), 0.5, key=f"k_{anahtar}")
        yy = st.number_input("Yağ (g)", 0.0, 400.0, float(round(y100 * oran, 1)), 0.5, key=f"y_{anahtar}")
        elle = (abs(pp - p100 * oran) > 0.05 or abs(kk - k100 * oran) > 0.05 or abs(yy - y100 * oran) > 0.05)

    if elle:
        toplam_kcal = round(kcal_hesapla(pp, kk, yy))
        p_kullan, k_kullan, y_kullan = (pp / max(oran, 0.0001), kk / max(oran, 0.0001), yy / max(oran, 0.0001))
    else:
        toplam_kcal = round(kcal_hesapla(p100, k100, y100) * gram / 100.0)
        p_kullan, k_kullan, y_kullan = p100, k100, y100

    c2.metric("Toplam", f"{toplam_kcal} kcal")

    b1, b2 = st.columns([3, 1])
    eklendi = b1.button("Günlüğe ekle", type="primary", use_container_width=True, key=f"ekle_{anahtar}")
    if b2.button("Favorilere ekle", use_container_width=True, key=f"fav_{anahtar}"):
        kaydedilecek = dict(y)
        kaydedilecek.update({"p": round(p_kullan, 1), "k": round(k_kullan, 1), "y": round(y_kullan, 1), "gram": int(gram)})
        if _yemek_kaydet(db, kullanici, "favori", kaydedilecek):
            st.toast(f"{y['ad']} favorilere eklendi")

    if eklendi:
        return _kayit_yap(y, gram, tarih, ogun, p_kullan, k_kullan, y_kullan)
    return None


def _sonuc_listesi(sonuclar, on_ek, db, kullanici, tarih, ogun):
    """Sonuçları radio ile listeler, seçilen için ekleme panelini açar."""
    if not sonuclar:
        return None
    secenekler = list(range(len(sonuclar)))
    secim = st.radio(
        "Sonuçlar", secenekler,
        format_func=lambda i: _etiket(sonuclar[i]),
        key=f"secim_{on_ek}", label_visibility="collapsed",
    )
    st.divider()
    y = sonuclar[secim]
    return _ekle_paneli(y, f"{on_ek}_{_norm(y['ad'])[:20]}_{y.get('kod','')}", db, kullanici, tarih, ogun)


# ------------------------------------------------------------------ Sekmeler
def _sekme_ara(df, db, kullanici, tarih, ogun):
    sorgu = st.text_input("Yemek ara", placeholder="Örn: mercimek çorbası, yoğurt, Eti kraker",
                          key="arama_sorgu", max_chars=60)
    marka_dahil = st.checkbox("Marka ürünlerinde de ara (Open Food Facts)", value=True, key="arama_marka")

    if len(sorgu.strip()) < 2:
        st.caption("Aramak için en az iki harf yaz.")
        return None

    sonuclar = _yerel_ara(df, sorgu)
    sonuclar += _liste_ara(_kullanici_yemekleri(db, kullanici, "kendi"), sorgu)
    sonuclar += [u for u in bk.onbellekte_ara(db, sorgu)]

    if marka_dahil:
        try:
            with st.spinner("Marka ürünlerinde aranıyor..."):
                disaridan = bk.off_ara(sorgu)
            if disaridan:
                bk.onbellege_yaz(db, disaridan)
                sonuclar += [_offtan(u) for u in disaridan]
        except bk.KaynakHatasi:
            st.caption("Marka ürünlerine şu an ulaşılamadı. Kendi veritabanındaki sonuçlar aşağıda.")

    # Aynı yemek birden çok kaynaktan gelebilir
    benzersiz, gorulen = [], set()
    for y in sonuclar:
        anahtar = (_norm(y["ad"]), _norm(y.get("marka", "")))
        if anahtar not in gorulen:
            gorulen.add(anahtar)
            benzersiz.append(y)

    if not benzersiz:
        st.info("Bulamadım. \"Kendi yemeğim\" sekmesinden kendin ekleyebilirsin.")
        return None

    st.caption(f"{len(benzersiz)} sonuç")
    return _sonuc_listesi(benzersiz[:30], "ara", db, kullanici, tarih, ogun)


def _etiketten_oku(foto_bytes):
    """Barkodla bulunamayan ürünün besin tablosunu yapay zekayla okur."""
    from nova_core import QuotaError, friendly_error, prepare_image, run_mode, show_limit_reached
    try:
        with st.spinner("Etiket okunuyor..."):
            return run_mode("label", "", image_bytes=prepare_image(foto_bytes))
    except QuotaError as e:
        show_limit_reached(str(e))
    except Exception as e:  # noqa: BLE001
        st.error(friendly_error(e))
    return None


def _etiket_sonucu(veri, kod=""):
    if not veri or not veri.get("is_label"):
        return None
    p, k, y = veri.get("per_100g_protein"), veri.get("per_100g_carbs"), veri.get("per_100g_fat")
    if None in (p, k, y):
        st.warning("Etiketteki protein, karbonhidrat ve yağ değerlerinin hepsi okunamadı. Daha net bir fotoğraf dene.")
        return None
    return _yemek(
        veri.get("product_name") or "Etiketten okunan ürün", p, k, y,
        gram=veri.get("serving_grams") or 100,
        marka=veri.get("brand") or "", kaynak="Etiketten okundu", kod=kod,
        ekstra={"Lif (g)": veri.get("per_100g_fiber"), "Şeker (g)": veri.get("per_100g_sugar"),
                "Tuz (g)": veri.get("per_100g_salt"), "Doymuş yağ (g)": veri.get("per_100g_saturated_fat")},
    )


def _sekme_barkod(db, kullanici, tarih, ogun):
    st.caption("Paketin arkasındaki barkodu okut. Bulunamazsa besin değerleri tablosunun fotoğrafından okuyabilirim.")

    yol = st.radio("Nasıl?", ["Fotoğraf çek", "Numarayı yaz"], horizontal=True,
                   key="barkod_yol", label_visibility="collapsed")

    kod = ""
    if yol == "Numarayı yaz":
        girilen = st.text_input("Barkod numarası", max_chars=14, key="barkod_elle").strip()
        if girilen:
            if bk.barkod_gecerli_mi(girilen):
                kod = girilen
            else:
                st.warning("Bu numara geçerli bir barkod gibi görünmüyor. Rakamları kontrol et.")
    else:
        foto = st.camera_input("Barkodu ortala ve çek", key="barkod_foto")
        if foto is None:
            foto = st.file_uploader("ya da bir fotoğraf seç", type=["jpg", "jpeg", "png", "webp"], key="barkod_dosya")
        if foto is not None:
            try:
                kodlar = bk.barkod_oku(foto.getvalue())
            except ImportError:
                st.error("Barkod okuyucu kurulu değil. requirements.txt dosyasına opencv-python-headless ekle.")
                kodlar = []
            except Exception:  # noqa: BLE001
                kodlar = []
            if kodlar:
                kod = kodlar[0]
                st.success(f"Barkod okundu: {kod}")
            else:
                st.warning("Barkodu okuyamadım. Daha yakın, net ve düz çekmeyi dene ya da numarayı elle yaz.")
                st.session_state["barkod_foto_yedek"] = foto.getvalue()

    # Barkod okunamadıysa etiketten okuma teklifi
    if not kod and st.session_state.get("barkod_foto_yedek"):
        if st.button("Bunun yerine besin değerleri tablosunu oku", key="etiket_oku_yedek"):
            veri = _etiketten_oku(__import__("io").BytesIO(st.session_state["barkod_foto_yedek"]))
            st.session_state["etiket_sonuc"] = veri
        veri = st.session_state.get("etiket_sonuc")
        y = _etiket_sonucu(veri)
        if y:
            return _ekle_paneli(y, "etiket_yedek", db, kullanici, tarih, ogun)
        return None

    if not kod:
        return None

    urun = bk.onbellekten_barkod(db, kod)
    if urun is None:
        try:
            with st.spinner("Ürün aranıyor..."):
                urun = bk.off_barkod(kod)
        except bk.KaynakHatasi:
            st.error("Ürün veritabanına şu an ulaşılamadı. Biraz sonra tekrar dene.")
            return None
        if urun and not urun.get("eksik"):
            bk.onbellege_yaz(db, [urun])

    if urun is None:
        st.info("Bu barkod veritabanında yok. Paketin besin değerleri tablosunu çekersen okuyabilirim.")
    elif urun.get("eksik"):
        st.info(f"**{urun['ad']}** bulundu ama besin değerleri kayıtlı değil. Besin tablosunu çekersen okuyabilirim.")
    else:
        return _ekle_paneli(_offtan(urun), f"bk_{kod}", db, kullanici, tarih, ogun)

    tablo_foto = st.file_uploader("Besin değerleri tablosunun fotoğrafı", type=["jpg", "jpeg", "png", "webp"],
                                  key=f"etiket_foto_{kod}")
    if tablo_foto is not None and st.button("Etiketi oku", type="primary", key=f"etiket_btn_{kod}"):
        st.session_state[f"etiket_{kod}"] = _etiketten_oku(tablo_foto)
    veri = st.session_state.get(f"etiket_{kod}")
    y = _etiket_sonucu(veri, kod)
    if y:
        st.caption("Okunan değerleri kontrol et, yanlışsa aşağıdan düzelt.")
        return _ekle_paneli(y, f"etiket_{kod}", db, kullanici, tarih, ogun)
    return None


def _son_yenenler(gunluk_kayitlar, limit=12):
    """Günlükten son eklenen farklı yemekler."""
    gorulen, liste = set(), []
    for k in reversed(gunluk_kayitlar or []):
        ad = k.get("Tarif", "")
        anahtar = _norm(ad)
        if ad and anahtar not in gorulen:
            gorulen.add(anahtar)
            liste.append(k)
        if len(liste) >= limit:
            break
    return liste


def _sekme_favoriler(db, kullanici, tarih, ogun, gunluk_kayitlar):
    kayitlar = []

    favoriler = _kullanici_yemekleri(db, kullanici, "favori")
    st.markdown("#### Favorilerin")
    if not favoriler:
        st.caption("Henüz favorin yok. Bir yemek eklerken \"Favorilere ekle\" düğmesini kullan.")
    else:
        for i, y in enumerate(favoriler):
            c1, c2, c3 = st.columns([6, 2, 1])
            c1.markdown(f"**{y['ad']}**" + (f" · {y['marka']}" if y.get("marka") else "")
                        + f"  \n{y['kcal']} kcal/100 g · varsayılan {y.get('gram', 100)} g")
            if c2.button("Ekle", key=f"favekle_{i}", use_container_width=True):
                kayitlar.append(_kayit_yap(y, y.get("gram", 100), tarih, ogun, y["p"], y["k"], y["y"]))
            if c3.button("✕", key=f"favsil_{i}", help="Favorilerden çıkar"):
                _yemek_sil(db, kullanici, "favori", y["ad"])
                st.rerun()

    st.divider()
    st.markdown("#### Son yedikleri")
    sonlar = _son_yenenler(gunluk_kayitlar)
    if not sonlar:
        st.caption("Henüz kayıt yok.")
    for i, k in enumerate(sonlar):
        c1, c2 = st.columns([8, 2])
        c1.markdown(f"{k['Tarif']} — *{round(k.get('Kalori', 0))} kcal*")
        if c2.button("Tekrar ekle", key=f"son_{i}", use_container_width=True):
            yeni = dict(k)
            yeni["Tarih"], yeni["Öğün"] = tarih, ogun
            kayitlar.append(yeni)

    st.divider()
    st.markdown("#### Önceki bir öğünü kopyala")
    tarihler = sorted({k.get("Tarih") for k in (gunluk_kayitlar or []) if k.get("Tarih") and k.get("Tarih") != tarih},
                      reverse=True)[:14]
    if not tarihler:
        st.caption("Kopyalanacak başka gün yok.")
    else:
        c1, c2, c3 = st.columns([3, 3, 2])
        kaynak_tarih = c1.selectbox("Hangi gün", tarihler, key="kopya_tarih")
        kaynak_ogun = c2.selectbox("Hangi öğün", ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"],
                                   key="kopya_ogun")
        adaylar = [k for k in gunluk_kayitlar
                   if k.get("Tarih") == kaynak_tarih and k.get("Öğün") == kaynak_ogun]
        c3.markdown("<br>", unsafe_allow_html=True)
        if adaylar:
            st.caption(" · ".join(k["Tarif"] for k in adaylar[:6]))
            if c3.button(f"{len(adaylar)} kalemi kopyala", key="kopyala", use_container_width=True):
                for k in adaylar:
                    yeni = dict(k)
                    yeni["Tarih"], yeni["Öğün"] = tarih, ogun
                    kayitlar.append(yeni)
        else:
            st.caption("O gün o öğünde kayıt yok.")

    return kayitlar or None


def _sekme_kendi(db, kullanici, tarih, ogun):
    st.caption("Veritabanında olmayan bir yemeği bir kez kaydet, sonra aramada çıksın.")
    kendi = _kullanici_yemekleri(db, kullanici, "kendi")

    with st.form("kendi_yemek_formu"):
        ad = st.text_input("Yemeğin adı", max_chars=60)
        c1, c2, c3, c4 = st.columns(4)
        p = c1.number_input("Protein (100 g)", 0.0, 100.0, 0.0, 0.1)
        k = c2.number_input("Karbonhidrat (100 g)", 0.0, 100.0, 0.0, 0.1)
        y = c3.number_input("Yağ (100 g)", 0.0, 100.0, 0.0, 0.1)
        gram = c4.number_input("Normal porsiyon (g)", 5, 2000, 100, 5)
        st.caption(f"Hesaplanan: {round(kcal_hesapla(p, k, y))} kcal / 100 g")
        kaydet = st.form_submit_button("Kaydet", type="primary")

    if kaydet:
        if not ad.strip():
            st.error("Yemeğin adını yaz.")
        elif p + k + y > 100.5:
            st.error("100 gramda protein, karbonhidrat ve yağ toplamı 100 gramı geçemez. Değerleri kontrol et.")
        elif p + k + y == 0:
            st.error("En az bir besin değeri gir.")
        else:
            if _yemek_kaydet(db, kullanici, "kendi",
                             _yemek(ad.strip(), p, k, y, gram=gram, kaynak="Kendi yemeğin")):
                st.success(f"{ad.strip()} kaydedildi. Artık aramada çıkacak.")
                st.rerun()

    if kendi:
        st.divider()
        st.markdown("#### Kaydettiklerin")
        for i, y in enumerate(kendi):
            c1, c2, c3 = st.columns([6, 2, 1])
            c1.markdown(f"**{y['ad']}** · {y['kcal']} kcal/100 g")
            if c2.button("Ekle", key=f"kendiekle_{i}", use_container_width=True):
                return [_kayit_yap(y, y.get("gram", 100), tarih, ogun, y["p"], y["k"], y["y"])]
            if c3.button("✕", key=f"kendisil_{i}", help="Sil"):
                _yemek_sil(db, kullanici, "kendi", y["ad"])
                st.rerun()
    return None


# -------------------------------------------------------------------- Giriş
def yemek_arama_sayfasi(df_yemek, db, kullanici, tarih, ogun, gunluk_kayitlar):
    """Yemek bulma ekranını çizer. Eklenecek kayıtların listesini ya da None döner."""
    sekmeler = st.tabs(["Ara", "Barkod", "Favoriler", "Kendi yemeğim"])

    with sekmeler[0]:
        kayit = _sekme_ara(df_yemek, db, kullanici, tarih, ogun)
        if kayit:
            return [kayit]

    with sekmeler[1]:
        kayit = _sekme_barkod(db, kullanici, tarih, ogun)
        if kayit:
            return [kayit]

    with sekmeler[2]:
        kayitlar = _sekme_favoriler(db, kullanici, tarih, ogun, gunluk_kayitlar)
        if kayitlar:
            return kayitlar

    with sekmeler[3]:
        kayitlar = _sekme_kendi(db, kullanici, tarih, ogun)
        if kayitlar:
            return kayitlar

    return None
