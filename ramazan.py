"""
ramazan.py - Oruç modu

Ramazan'a özel değil, oruç tutan herkese çalışan bir mod. Saatler dünya
genelinde çalışan Aladhan servisinden geliyor; Türkiye'ye özel bir kaynak
kullanılmıyor, çünkü Nova altı dilde ve her ülkede çalışıyor.

Modun yaptıkları:
  - Öğün adları sahur / iftar / gece ara öğünü olur
  - Ana ekranda iftara (ya da sahura) kalan süre görünür
  - Su hedefi iftar ile sahur arasına sıkışır
  - Oruçluyken kalori açığı daraltılır; oruç üstüne sert açık sağlıksız
  - Ramazan başladığında mod kendiliğinden önerilir

Servis: https://api.aladhan.com  (anahtar istemiyor)
Çevrimdışı kalınırsa kullanıcı saatleri elle girebilir.
"""

import datetime

import streamlit as st

from diller import t, h

API = "https://api.aladhan.com/v1/timingsByCity"
ZAMAN_ASIMI = 8

# Aladhan hesaplama yöntemleri. Numaralar servisin kendi numaraları.
METOTLAR = {
    13: "Diyanet İşleri Başkanlığı (Türkiye)",
    3: "Muslim World League",
    2: "Islamic Society of North America",
    4: "Umm Al-Qura (Mekke)",
    5: "Egyptian General Authority of Survey",
    1: "University of Islamic Sciences, Karachi",
    12: "Union Organization Islamic de France",
    11: "Majlis Ugama Islam Singapura",
    17: "JAKIM (Malezya)",
    20: "Kemenag (Endonezya)",
}
VARSAYILAN_METOT = 3        # dünya geneli varsayılan; Türkiye seçilirse 13 önerilir

RAMAZAN_AYI = 9             # hicri takvimde Ramazan dokuzuncu ay
SU_HEDEFI = 2.5


# --------------------------------------------------------------- Saatler
@st.cache_data(ttl=6 * 3600, show_spinner=False)
def _servisten(sehir, ulke, metot, tarih_metni):
    """Aladhan'dan bir günün saatlerini alır. Altı saat önbellekte tutulur."""
    import requests
    # Tarih adresin parçası olarak gidiyor: /timingsByCity/GG-AA-YYYY
    cevap = requests.get(
        f"{API}/{tarih_metni}",
        params={"city": sehir, "country": ulke, "method": int(metot)},
        timeout=ZAMAN_ASIMI,
        headers={"User-Agent": "Nova/1.0"},
    )
    cevap.raise_for_status()
    return cevap.json()


def _saat_ayikla(ham):
    """Servisin yanıtından yalnızca gereken alanları çıkarır.

    Yanıt biçimi değişebileceği için her alan tek tek ve savunmacı okunuyor;
    beklenmeyen bir şey gelirse çökmek yerine None dönüyor.
    """
    try:
        veri = ham.get("data") or {}
        saatler = veri.get("timings") or {}
        tarih = veri.get("date") or {}
        hicri = tarih.get("hijri") or {}
        ay = hicri.get("month") or {}

        def temiz(deger):
            # "05:12 (+03)" gibi gelebiliyor; sadece saati al
            if not deger:
                return None
            return str(deger).split(" ")[0].strip()

        imsak = temiz(saatler.get("Imsak")) or temiz(saatler.get("Fajr"))
        iftar = temiz(saatler.get("Maghrib")) or temiz(saatler.get("Sunset"))
        if not imsak or not iftar:
            return None
        return {
            "imsak": imsak,
            "iftar": iftar,
            "hicri_ay": int(ay.get("number") or 0),
            "hicri_gun": int(hicri.get("day") or 0),
            "hicri_ay_adi": (ay.get("en") or "").strip(),
            "zaman_dilimi": ((veri.get("meta") or {}).get("timezone") or "").strip(),
        }
    except (AttributeError, TypeError, ValueError):
        return None


def saatleri_al(profil, gun=None):
    """Kullanıcının şehrine göre o günün imsak ve iftar saatini döndürür.

    Servise ulaşılamazsa, kullanıcı elle girmişse onu kullanır; o da yoksa None.
    """
    gun = gun or datetime.date.today()
    sehir = (profil.get("sehir") or "").strip()
    ulke = (profil.get("ulke") or "").strip()

    if sehir and ulke:
        try:
            ham = _servisten(sehir, ulke, profil.get("namaz_metodu", VARSAYILAN_METOT),
                             gun.strftime("%d-%m-%Y"))
            sonuc = _saat_ayikla(ham)
            if sonuc:
                return sonuc
        except Exception:  # noqa: BLE001
            pass

    elle_imsak = (profil.get("elle_imsak") or "").strip()
    elle_iftar = (profil.get("elle_iftar") or "").strip()
    if elle_imsak and elle_iftar:
        return {"imsak": elle_imsak, "iftar": elle_iftar, "hicri_ay": 0,
                "hicri_gun": 0, "hicri_ay_adi": "", "zaman_dilimi": "", "elle": True}
    return None


def ramazan_mi(saatler):
    return bool(saatler) and saatler.get("hicri_ay") == RAMAZAN_AYI


def oruc_acik_mi(profil):
    return bool(profil.get("oruc_modu"))


# ---------------------------------------------------------------- Süre
def _bugun_saat(metin, gun=None):
    """'05:12' metnini bugünün tarihiyle birleştirip zaman nesnesi yapar."""
    gun = gun or datetime.date.today()
    try:
        s, d = str(metin).split(":")[:2]
        return datetime.datetime.combine(gun, datetime.time(int(s), int(d)))
    except (ValueError, TypeError):
        return None


def sonraki_olay(saatler, simdi=None):
    """Şimdiye göre sıradaki olayı ve kalan süreyi döndürür.

    ("iftar", kalan) ya da ("sahur", kalan). Kalan bir timedelta.
    """
    if not saatler:
        return None, None
    simdi = simdi or datetime.datetime.now()
    bugun = simdi.date()
    imsak = _bugun_saat(saatler["imsak"], bugun)
    iftar = _bugun_saat(saatler["iftar"], bugun)
    if not imsak or not iftar:
        return None, None

    if simdi < imsak:
        # Gece; sahur vakti henüz kapanmadı
        return "sahur", imsak - simdi
    if simdi < iftar:
        return "iftar", iftar - simdi
    # İftar geçti; sıradaki sahur yarın
    yarin_imsak = imsak + datetime.timedelta(days=1)
    return "sahur", yarin_imsak - simdi


def sure_metni(fark):
    """Kalan süreyi 1:59 biçiminde yazar.

    Kelimeyle yazmak altı dilde tekil/çoğul sorunu çıkarıyordu
    ("1 hours" gibi). Rakam biçimi her dilde doğru ve kısa.
    """
    if not fark:
        return ""
    toplam = int(fark.total_seconds())
    saat, kalan = divmod(max(toplam, 0), 3600)
    dakika = kalan // 60
    return f"{saat}:{dakika:02d}"


def oruclu_mu_su_an(saatler, simdi=None):
    """Şu an oruç saatleri içinde mi (imsak ile iftar arası)?"""
    if not saatler:
        return False
    simdi = simdi or datetime.datetime.now()
    imsak = _bugun_saat(saatler["imsak"], simdi.date())
    iftar = _bugun_saat(saatler["iftar"], simdi.date())
    if not imsak or not iftar:
        return False
    return imsak <= simdi < iftar


# ---------------------------------------------------------------- Öğünler
OGUNLER_NORMAL = ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"]
OGUNLER_ORUC = ["Sahur", "İftar", "Gece Ara Öğünü"]


def ogunler(profil):
    return OGUNLER_ORUC if oruc_acik_mi(profil) else OGUNLER_NORMAL


# ------------------------------------------------------------- Güvenlik
def guvenli_acik(profil, gunluk_acik):
    """Oruçluyken kalori açığını daraltır.

    Oruç zaten öğün sayısını ve su alımını kısıtlıyor; üstüne sert bir açık
    koymak baş dönmesi, halsizlik ve kas kaybı riskini artırır. Bu yüzden
    oruç modunda açık en fazla 500 kcal ile sınırlanıyor.
    """
    if not oruc_acik_mi(profil):
        return gunluk_acik, None
    if gunluk_acik <= 500:
        return gunluk_acik, None
    return 500, t("Oruçluyken günlük kalori açığın 500 kcal ile sınırlandı. "
                  "Oruç zaten öğünleri ve suyu kısıtlıyor; üstüne sert bir açık "
                  "koymak halsizlik ve kas kaybı riskini artırır.")


ONERILER = {
    "sahur": [
        "Sahurda protein ve lif birlikte olsun: yumurta, peynir, yulaf, tam tahıllı ekmek, "
        "zeytin ve bol sebze uzun süre tok tutar.",
        "Çok tuzlu yiyecekler gün içinde susatır; sahurda turşu, salam ve hazır çorbadan uzak dur.",
        "Sahuru atlama. Atlanan sahur, iftarda aşırı yemeye ve ertesi gün halsizliğe yol açıyor.",
    ],
    "iftar": [
        "İftarı hafif aç: su, hurma ya da çorba. Mideyi birden doldurmak şişkinlik ve "
        "ani şeker yükselmesi yapıyor.",
        "Ana yemeğe birkaç dakika ara verdikten sonra geç; tokluk hissi beyne yaklaşık "
        "yirmi dakikada ulaşıyor.",
        "Tatlıyı iftarın hemen üstüne değil, bir iki saat sonra ve küçük porsiyon olarak ye.",
    ],
    "su": [
        "Günlük suyunu iftar ile sahur arasına yay. Bir seferde çok su içmek işe yaramıyor, "
        "vücut fazlasını atıyor.",
        "Çay ve kahve idrar söktürüyor; iftardan sonra ikisini de ölçülü tut.",
    ],
    "egzersiz": [
        "Ağır antrenmanı iftardan bir iki saat sonraya al. Aç karnına ağır çalışmak "
        "kas kaybını hızlandırıyor.",
        "Gün içinde hafif yürüyüş sorun değil, ama sıcakta ve öğle saatlerinde kaçın.",
    ],
}


# ------------------------------------------------------------------ UI
def ramazan_karti(profil, saatler):
    """Ana ekranda iftara/sahura kalan süreyi gösterir."""
    if not oruc_acik_mi(profil) or not saatler:
        return
    olay, kalan = sonraki_olay(saatler)
    if not olay:
        return

    etiket = t("İftara kalan") if olay == "iftar" else t("Sahurun bitmesine kalan")
    hedef = saatler["iftar"] if olay == "iftar" else saatler["imsak"]
    st.markdown(h(
        f"""<div class="info-box" style="text-align:center;">
        <div style="font-size:0.9rem; opacity:0.85;">{etiket}</div>
        <div style="font-size:1.6rem; font-weight:700; margin:4px 0;">{sure_metni(kalan)}</div>
        <div style="font-size:0.85rem; opacity:0.75;">
        {t('İmsak')} {saatler['imsak']} · {t('İftar')} {saatler['iftar']}</div>
        </div>"""), unsafe_allow_html=True)

    if saatler.get("elle"):
        st.caption(t("Saatler elle girdiğin değerlerden alınıyor."))


def su_notu(profil, saatler):
    """Oruçluyken su hedefi uyarısı."""
    if not oruc_acik_mi(profil) or not saatler:
        return
    if oruclu_mu_su_an(saatler):
        st.caption(t("Şu an oruçlusun. Günlük su hedefini iftar ile sahur arasına yayman gerekiyor."))
    else:
        st.caption(f"{t('Su içme vakti. Hedefin')}: {SU_HEDEFI} L")


def oneri_bolumu():
    st.markdown(h(f"#### {t('Oruç önerileri')}"))
    for baslik, anahtar in ((t("Sahur"), "sahur"), (t("İftar"), "iftar"),
                            (t("Su"), "su"), (t("Egzersiz"), "egzersiz")):
        with st.expander(baslik):
            for satir in ONERILER[anahtar]:
                st.write("- " + t(satir))
    st.caption(t("Bunlar genel bilgidir, tıbbi tavsiye değildir. Şeker hastalığın, "
                 "tansiyon sorunun ya da düzenli kullandığın bir ilacın varsa oruç "
                 "tutmadan önce doktoruna danış."))


def ayarlar(profil, kaydet):
    """Ayarlar panelindeki oruç modu bölümü."""
    st.markdown(h(f"#### {t('Oruç modu')}"))

    acik = st.toggle(t("Oruç modunu aç"), value=oruc_acik_mi(profil), key="oruc_toggle",
                     help=t("Öğünler sahur ve iftar olarak değişir, iftara kalan süre "
                            "ana ekranda görünür, su hedefi oruç saatlerine göre ayarlanır."))
    if acik != oruc_acik_mi(profil):
        profil["oruc_modu"] = acik
        kaydet()
        st.rerun()

    if not acik:
        return

    c1, c2 = st.columns(2)
    sehir = c1.text_input(t("Şehir"), value=profil.get("sehir", ""), key="oruc_sehir",
                          placeholder="İstanbul")
    ulke = c2.text_input(t("Ülke"), value=profil.get("ulke", ""), key="oruc_ulke",
                         placeholder="Turkey")

    metot_listesi = list(METOTLAR.keys())
    mevcut = profil.get("namaz_metodu", VARSAYILAN_METOT)
    if mevcut not in metot_listesi:
        mevcut = VARSAYILAN_METOT
    metot = st.selectbox(t("Hesaplama yöntemi"), metot_listesi,
                         index=metot_listesi.index(mevcut),
                         format_func=lambda k: METOTLAR[k], key="oruc_metot",
                         help=t("Ülkenin resmi kurumunu seç. Emin değilsen "
                                "Muslim World League genel bir seçimdir."))

    if st.button(t("Kaydet ve saatleri getir"), key="oruc_kaydet", use_container_width=True):
        profil.update({"sehir": sehir.strip(), "ulke": ulke.strip(), "namaz_metodu": metot})
        kaydet()
        st.rerun()

    saatler = saatleri_al(profil)
    if saatler and not saatler.get("elle"):
        st.success(f"{t('İmsak')} {saatler['imsak']} · {t('İftar')} {saatler['iftar']}")
        if saatler.get("hicri_ay_adi"):
            st.caption(f"{t('Hicri ay')}: {saatler['hicri_ay_adi']} "
                       f"{saatler.get('hicri_gun') or ''}")
    elif sehir and ulke:
        st.warning(t("Saatler alınamadı. Şehir ve ülke adını İngilizce yazmayı dene "
                     "(örnek: Istanbul / Turkey) ya da aşağıdan elle gir."))

    with st.expander(t("Saatleri elle gir")):
        st.caption(t("Servise ulaşılamazsa ya da kendi takvimini kullanmak istersen."))
        e1, e2 = st.columns(2)
        elle_imsak = e1.text_input(t("İmsak"), value=profil.get("elle_imsak", ""),
                                   placeholder="05:12", key="oruc_elle_imsak")
        elle_iftar = e2.text_input(t("İftar"), value=profil.get("elle_iftar", ""),
                                   placeholder="17:30", key="oruc_elle_iftar")
        if st.button(t("Elle girilen saatleri kaydet"), key="oruc_elle_kaydet",
                     use_container_width=True):
            profil["elle_imsak"] = elle_imsak.strip()
            profil["elle_iftar"] = elle_iftar.strip()
            kaydet()
            st.rerun()


def otomatik_oneri(profil, saatler):
    """Ramazan başladıysa ve mod kapalıysa bir kez önerir."""
    if oruc_acik_mi(profil) or not ramazan_mi(saatler):
        return
    if st.session_state.get("_ramazan_onerildi"):
        return
    st.session_state["_ramazan_onerildi"] = True
    st.info(t("Ramazan başladı. Oruç modunu açmak ister misin? "
              "Ayarlardan açabilirsin; öğünler sahur ve iftara döner."))
