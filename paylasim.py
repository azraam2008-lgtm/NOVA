"""
paylasim.py - Diyetisyen paylaşımı

Kullanıcının seçtiği dönemin özetini iki şekilde dışarı verir:
  1. PDF olarak indirilir, diyetisyene e-postayla gönderilir
  2. Bağlantı olarak paylaşılır; diyetisyen uygulamaya girmeden, hesap açmadan
     raporu görür

Bağlantıda kullanıcının adı, kayıtları ve kilosu görünür. Bu yüzden:
  - Bağlantı tahmin edilemez bir belirteç taşır (32 baytlık rastgele)
  - Her bağlantının son kullanma tarihi vardır
  - Kullanıcı istediği an iptal edebilir
  - Sadece seçilen dönem görünür, bütün geçmiş değil
  - E-posta, şifre ve hesap ayarları hiçbir zaman paylaşılmaz

Gerekli tablo: paylasimlar (supabase_kurulum.sql)
"""

import datetime
import hashlib
import io
import secrets

import streamlit as st

from diller import t, h

GUN_SECENEKLERI = {"Son 7 gün": 7, "Son 30 gün": 30, "Son 90 gün": 90}
VARSAYILAN_GECERLILIK = 30


# ----------------------------------------------------------------- Veri
def _gun_listesi(gun_sayisi, bitis=None):
    bitis = bitis or datetime.date.today()
    return [str(bitis - datetime.timedelta(days=i)) for i in range(gun_sayisi - 1, -1, -1)]


def rapor_verisi(profil, gunluk_kayitlar, aktivite_loglari, gun_sayisi, hedef_kalori):
    """Diyetisyene gidecek özeti hazırlar. Hesap bilgisi taşımaz."""
    gunler = _gun_listesi(gun_sayisi)
    kume = set(gunler)
    kayitlar = [k for k in (gunluk_kayitlar or []) if k.get("Tarih") in kume]

    gunluk = {}
    for g in gunler:
        gun_kayitlari = [k for k in kayitlar if k.get("Tarih") == g]
        akt = (aktivite_loglari or {}).get(g, {}) or {}
        gunluk[g] = {
            "kalori": sum(float(k.get("Kalori", 0) or 0) for k in gun_kayitlari),
            "protein": sum(float(k.get("Protein", 0) or 0) for k in gun_kayitlari),
            "karbonhidrat": sum(float(k.get("Karbonhidrat", 0) or 0) for k in gun_kayitlari),
            "yag": sum(float(k.get("Yağ", 0) or 0) for k in gun_kayitlari),
            "adim": int(akt.get("adim", 0) or 0),
            "su": float(akt.get("su", 0) or 0),
            "egzersiz_kalori": float(akt.get("egzersiz_kalori", 0) or 0),
            "ogunler": [
                {"ogun": k.get("Öğün", ""), "ad": k.get("Tarif", ""),
                 "kalori": round(float(k.get("Kalori", 0) or 0))}
                for k in gun_kayitlari
            ],
        }

    kayitli_gunler = [g for g in gunler if gunluk[g]["ogunler"]]
    bolen = max(len(kayitli_gunler), 1)

    kilolar = [x for x in sorted(profil.get("kilo_gecmisi", []), key=lambda y: y.get("tarih", ""))
               if x.get("tarih") in kume]

    return {
        "ad": (profil.get("ad") or "").strip(),
        "olusturma": datetime.date.today().isoformat(),
        "gun_sayisi": gun_sayisi,
        "hedef_kalori": round(float(hedef_kalori or 0)),
        "boy": profil.get("boy"),
        "yas": _yas(profil),
        "cinsiyet": profil.get("cinsiyet"),
        "aktivite": profil.get("aktivite"),
        "amaclar": profil.get("amaclar", []),
        "mevcut_kilo": profil.get("mevcut_kilo"),
        "hedef_kilo": profil.get("hedef_kilo"),
        "gunler": gunler,
        "gunluk": gunluk,
        "kilo_gecmisi": kilolar,
        "kayitli_gun": len(kayitli_gunler),
        "ortalama": {
            "kalori": sum(gunluk[g]["kalori"] for g in kayitli_gunler) / bolen,
            "protein": sum(gunluk[g]["protein"] for g in kayitli_gunler) / bolen,
            "karbonhidrat": sum(gunluk[g]["karbonhidrat"] for g in kayitli_gunler) / bolen,
            "yag": sum(gunluk[g]["yag"] for g in kayitli_gunler) / bolen,
            "adim": sum(gunluk[g]["adim"] for g in gunler) / max(len(gunler), 1),
            "su": sum(gunluk[g]["su"] for g in gunler) / max(len(gunler), 1),
        },
    }


def _yas(profil):
    try:
        return datetime.date.today().year - int(profil.get("dogum_yili"))
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------- Bağlantı
def _ozet(belirtec):
    return hashlib.sha256(str(belirtec).encode("utf-8")).hexdigest()


def baglanti_olustur(db, kullanici, veri, gecerlilik_gun=VARSAYILAN_GECERLILIK):
    """Paylaşım kaydı açar, bağlantıdaki belirteci döndürür. Hata olursa None."""
    if db is None:
        return None
    belirtec = secrets.token_urlsafe(24)
    son = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=gecerlilik_gun)
    try:
        db.table("paylasimlar").insert({
            "belirtec_ozeti": _ozet(belirtec),
            "username": kullanici,
            "veri": veri,
            "son_kullanma": son.isoformat(),
        }).execute()
    except Exception:  # noqa: BLE001
        return None
    return belirtec


def baglanti_oku(db, belirtec):
    """Belirtece karşılık gelen raporu döndürür. Süresi geçmişse None."""
    if db is None or not belirtec:
        return None
    try:
        res = (db.table("paylasimlar").select("veri, son_kullanma")
               .eq("belirtec_ozeti", _ozet(belirtec)).limit(1).execute())
    except Exception:  # noqa: BLE001
        return None
    if not res.data:
        return None
    satir = res.data[0]
    try:
        son = datetime.datetime.fromisoformat(str(satir["son_kullanma"]).replace("Z", "+00:00"))
        if son.tzinfo is None:
            son = son.replace(tzinfo=datetime.timezone.utc)
        if datetime.datetime.now(datetime.timezone.utc) > son:
            return None
    except (ValueError, KeyError):
        return None
    return satir.get("veri")


def baglantilari_listele(db, kullanici):
    if db is None:
        return []
    try:
        res = (db.table("paylasimlar").select("belirtec_ozeti, son_kullanma, olusturma")
               .eq("username", kullanici).execute())
        return res.data or []
    except Exception:  # noqa: BLE001
        return []


def baglantilari_iptal(db, kullanici):
    if db is None:
        return False
    try:
        db.table("paylasimlar").delete().eq("username", kullanici).execute()
        return True
    except Exception:  # noqa: BLE001
        return False


# ------------------------------------------------------------------ PDF
# Varsayılan Helvetica Türkçe harfleri (ş, ı, ğ, İ) çizemiyor; PDF'te siyah
# kutu çıkıyor. Bu yüzden Unicode kapsayan bir yazı tipi kaydediliyor.
# Vera, reportlab'ın içinde geldiği için her ortamda bulunur; sistemde daha
# geniş kapsamlı bir yazı tipi varsa o tercih edilir.
_YAZI_ADAYLARI = [
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
     "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    ("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
     "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"),
]
_yazi_tipi = None


def _yazi_kaydet():
    """Türkçe harfleri çizebilen bir yazı tipi kaydeder, adını döndürür."""
    global _yazi_tipi
    if _yazi_tipi:
        return _yazi_tipi
    import os
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.fonts import addMapping

    adaylar = list(_YAZI_ADAYLARI)
    try:  # reportlab ile gelen Vera: her zaman var, Türkçeyi kapsıyor
        import reportlab
        kok = os.path.join(os.path.dirname(reportlab.__file__), "fonts")
        adaylar.append((os.path.join(kok, "Vera.ttf"), os.path.join(kok, "VeraBd.ttf")))
    except Exception:  # noqa: BLE001
        pass

    for duz, kalin in adaylar:
        if not os.path.exists(duz):
            continue
        try:
            pdfmetrics.registerFont(TTFont("NovaYazi", duz))
            if os.path.exists(kalin):
                pdfmetrics.registerFont(TTFont("NovaYazi-Bold", kalin))
                addMapping("NovaYazi", 0, 0, "NovaYazi")
                addMapping("NovaYazi", 1, 0, "NovaYazi-Bold")
            _yazi_tipi = "NovaYazi"
            return _yazi_tipi
        except Exception:  # noqa: BLE001
            continue
    _yazi_tipi = "Helvetica"      # son çare: Türkçe harfler bozuk çıkar
    return _yazi_tipi


def pdf_olustur(veri):
    """Raporu PDF olarak üretir. reportlab yoksa None döner."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                        TableStyle, PageBreak)
    except ImportError:
        return None

    tampon = io.BytesIO()
    belge = SimpleDocTemplate(tampon, pagesize=A4,
                              leftMargin=18 * mm, rightMargin=18 * mm,
                              topMargin=18 * mm, bottomMargin=18 * mm,
                              title="Nova beslenme raporu")
    yazi = _yazi_kaydet()
    kalin_yazi = "NovaYazi-Bold" if yazi == "NovaYazi" else "Helvetica-Bold"
    stiller = getSampleStyleSheet()
    for _ad in ("Normal", "Title", "Heading2"):
        stiller[_ad].fontName = kalin_yazi if _ad != "Normal" else yazi
    baslik = ParagraphStyle("baslik", parent=stiller["Title"], fontSize=20, spaceAfter=4)
    alt = ParagraphStyle("alt", parent=stiller["Normal"], fontSize=9,
                         textColor=colors.HexColor("#666666"), spaceAfter=14)
    bolum = ParagraphStyle("bolum", parent=stiller["Heading2"], fontSize=12, spaceBefore=12,
                           spaceAfter=6, textColor=colors.HexColor("#222222"))
    normal = stiller["Normal"]

    icerik = []
    ad = veri.get("ad") or t("Kullanıcı")
    icerik.append(Paragraph(f"{ad} — {t('beslenme raporu')}", baslik))
    icerik.append(Paragraph(
        f"{t('Son')} {veri['gun_sayisi']} {t('gün')} · "
        f"{t('Hazırlanma tarihi')}: {veri['olusturma']} · Nova", alt))

    # --- Kişi bilgileri
    kisi = []
    for etiket, deger in (
            (t("Yaş"), veri.get("yas")),
            (t("Cinsiyet"), t(veri.get("cinsiyet") or "")),
            (t("Boy (cm)"), veri.get("boy")),
            (t("Şu anki kilo (kg)"), veri.get("mevcut_kilo")),
            (t("Hedef kilo (kg)"), veri.get("hedef_kilo")),
            (t("Hareket düzeyi"), t(veri.get("aktivite") or "")),
            (t("Günlük kalori hedefi"), f"{veri['hedef_kalori']} kcal"),
    ):
        if deger not in (None, "", "None"):
            kisi.append([etiket, str(deger)])
    if veri.get("amaclar"):
        kisi.append([t("Hedefleri"), ", ".join(t(a) for a in veri["amaclar"])])

    if kisi:
        icerik.append(Paragraph(t("Kişi bilgileri"), bolum))
        tablo = Table(kisi, colWidths=[55 * mm, 105 * mm])
        tablo.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), yazi),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#555555")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#DDDDDD")),
        ]))
        icerik.append(tablo)

    # --- Dönem ortalaması
    o = veri["ortalama"]
    icerik.append(Paragraph(t("Dönem ortalaması"), bolum))
    icerik.append(Paragraph(
        f"{t('Kayıt girilen gün sayısı')}: {veri['kayitli_gun']} / {veri['gun_sayisi']}", normal))
    ort = [[t("Ölçüt"), t("Günlük ortalama"), t("Hedef")],
           [t("Kalori"), f"{round(o['kalori'])} kcal", f"{veri['hedef_kalori']} kcal"],
           [t("Protein"), f"{o['protein']:.1f} g", "-"],
           [t("Karbonhidrat"), f"{o['karbonhidrat']:.1f} g", "-"],
           [t("Yağ"), f"{o['yag']:.1f} g", "-"],
           [t("Adım"), f"{round(o['adim'])}", "-"],
           [t("Su"), f"{o['su']:.2f} L", "-"]]
    tablo = Table(ort, colWidths=[55 * mm, 55 * mm, 50 * mm])
    tablo.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), yazi),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F2F2")),
        ("FONTNAME", (0, 0), (-1, 0), kalin_yazi),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDDDDD")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    icerik.append(Spacer(1, 4))
    icerik.append(tablo)

    # --- Kilo seyri
    if veri.get("kilo_gecmisi"):
        icerik.append(Paragraph(t("Kilo kayıtları"), bolum))
        satirlar = [[t("Tarih"), t("Kilo (kg)")]]
        satirlar += [[x.get("tarih", ""), str(x.get("kilo", ""))] for x in veri["kilo_gecmisi"]]
        tablo = Table(satirlar, colWidths=[55 * mm, 55 * mm])
        tablo.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), yazi),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F2F2")),
            ("FONTNAME", (0, 0), (-1, 0), kalin_yazi),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDDDDD")),
        ]))
        icerik.append(tablo)

    # --- Günlük döküm
    icerik.append(PageBreak())
    icerik.append(Paragraph(t("Günlük döküm"), bolum))
    for gun in veri["gunler"]:
        g = veri["gunluk"][gun]
        if not g["ogunler"] and not g["adim"] and not g["su"]:
            continue
        icerik.append(Spacer(1, 6))
        ustbilgi = (f"<b>{gun}</b> — {round(g['kalori'])} kcal · "
                    f"P {g['protein']:.0f} g · {t('K')} {g['karbonhidrat']:.0f} g · "
                    f"{t('Y')} {g['yag']:.0f} g")
        if g["adim"]:
            ustbilgi += f" · {t('Adım')} {g['adim']}"
        if g["su"]:
            ustbilgi += f" · {t('Su')} {g['su']:.2f} L"
        icerik.append(Paragraph(ustbilgi, normal))
        if g["ogunler"]:
            satirlar = [[t(o["ogun"]), o["ad"], f"{o['kalori']} kcal"] for o in g["ogunler"]]
            tablo = Table(satirlar, colWidths=[30 * mm, 100 * mm, 30 * mm])
            tablo.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), yazi),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#666666")),
                ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
            ]))
            icerik.append(tablo)

    icerik.append(Spacer(1, 14))
    icerik.append(Paragraph(
        t("Bu rapor kullanıcının kendi girdiği kayıtlardan üretilmiştir. "
          "Nova bir sağlık uygulaması değildir ve tıbbi tavsiye vermez."),
        ParagraphStyle("not", parent=normal, fontSize=8,
                       textColor=colors.HexColor("#888888"))))

    belge.build(icerik)
    return tampon.getvalue()


# ------------------------------------------------------- Okuma ekranı
def rapor_goster(veri):
    """Bağlantıyla gelen diyetisyen için salt okunur rapor ekranı."""
    ad = veri.get("ad") or t("Kullanıcı")
    st.markdown(h(f"<h2>{ad} — {t('beslenme raporu')}</h2>"), unsafe_allow_html=True)
    st.caption(f"{t('Son')} {veri['gun_sayisi']} {t('gün')} · "
               f"{t('Hazırlanma tarihi')}: {veri['olusturma']}")

    s1, s2, s3, s4 = st.columns(4)
    o = veri["ortalama"]
    s1.metric(t("Günlük ortalama kalori"), f"{round(o['kalori'])}")
    s2.metric(t("Kalori hedefi"), f"{veri['hedef_kalori']}")
    s3.metric(t("Kayıtlı gün"), f"{veri['kayitli_gun']} / {veri['gun_sayisi']}")
    s4.metric(t("Ortalama adım"), f"{round(o['adim'])}")

    st.divider()
    st.markdown(h(f"#### {t('Dönem ortalaması')}"))
    st.table({
        t("Ölçüt"): [t("Protein"), t("Karbonhidrat"), t("Yağ"), t("Su")],
        t("Günlük ortalama"): [f"{o['protein']:.1f} g", f"{o['karbonhidrat']:.1f} g",
                               f"{o['yag']:.1f} g", f"{o['su']:.2f} L"],
    })

    if veri.get("kilo_gecmisi"):
        st.markdown(h(f"#### {t('Kilo kayıtları')}"))
        st.table({t("Tarih"): [x.get("tarih", "") for x in veri["kilo_gecmisi"]],
                  t("Kilo (kg)"): [x.get("kilo", "") for x in veri["kilo_gecmisi"]]})

    st.markdown(h(f"#### {t('Günlük döküm')}"))
    for gun in veri["gunler"]:
        g = veri["gunluk"][gun]
        if not g["ogunler"] and not g["adim"] and not g["su"]:
            continue
        with st.expander(f"{gun} — {round(g['kalori'])} kcal"):
            for ogun in g["ogunler"]:
                st.write(f"{t(ogun['ogun'])} · {ogun['ad']} · {ogun['kalori']} kcal")
            if g["adim"] or g["su"]:
                st.caption(f"{t('Adım')}: {g['adim']} · {t('Su')}: {g['su']:.2f} L")

    st.divider()
    st.caption(t("Bu rapor kullanıcının kendi girdiği kayıtlardan üretilmiştir. "
                 "Nova bir sağlık uygulaması değildir ve tıbbi tavsiye vermez."))


# ------------------------------------------------------- Paylaşım bölümü
def paylasim_bolumu(db, kullanici, profil, gunluk_kayitlar, aktivite_loglari, hedef_kalori,
                    site_adresi=""):
    """Kullanıcının gördüğü paylaşım arayüzü."""
    st.markdown(h(f"#### {t('Diyetisyenine gönder')}"))
    st.caption(t("Seçtiğin dönemin özetini PDF olarak indirebilir ya da bağlantı olarak "
                 "paylaşabilirsin. Bağlantıyı açan kişi hesabına giremez, sadece bu raporu görür."))

    donem = st.selectbox(t("Hangi dönem"), list(GUN_SECENEKLERI.keys()), key="paylasim_donem")
    veri = rapor_verisi(profil, gunluk_kayitlar, aktivite_loglari,
                        GUN_SECENEKLERI[donem], hedef_kalori)

    if veri["kayitli_gun"] == 0:
        st.info(t("Bu dönemde kayıt yok. Rapor boş çıkar."))

    pdf = pdf_olustur(veri)
    if pdf:
        st.download_button(
            t("PDF olarak indir"), pdf,
            file_name=f"nova_rapor_{kullanici}_{datetime.date.today()}.pdf",
            mime="application/pdf", use_container_width=True)
    else:
        st.caption(t("PDF için reportlab gerekli. requirements.txt dosyasına reportlab ekle."))

    st.divider()
    st.markdown(h(f"##### {t('Bağlantıyla paylaş')}"))
    gecerlilik = st.slider(t("Bağlantı kaç gün geçerli olsun?"), 1, 90, VARSAYILAN_GECERLILIK,
                           key="paylasim_gun")

    if st.button(t("Bağlantı oluştur"), use_container_width=True, key="paylasim_olustur"):
        belirtec = baglanti_olustur(db, kullanici, veri, gecerlilik)
        if belirtec:
            st.session_state["son_paylasim"] = belirtec
            st.rerun()
        else:
            st.error(t("Bağlantı oluşturulamadı. Veritabanına bağlanılamadı."))

    if st.session_state.get("son_paylasim"):
        adres = (site_adresi or "").rstrip("/")
        baglanti = f"{adres}/?rapor={st.session_state['son_paylasim']}" if adres \
            else f"?rapor={st.session_state['son_paylasim']}"
        st.success(t("Bağlantı hazır. Kopyalayıp diyetisyenine gönderebilirsin."))
        st.code(baglanti, language=None)
        if not adres:
            st.caption(t("Site adresini Secrets içine SITE_ADRESI olarak eklersen "
                         "bağlantı tam adresle çıkar."))

    mevcut = baglantilari_listele(db, kullanici)
    if mevcut:
        st.caption(f"{t('Açık paylaşım bağlantısı')}: {len(mevcut)}")
        if st.button(t("Bütün bağlantıları iptal et"), key="paylasim_iptal",
                     use_container_width=True):
            if baglantilari_iptal(db, kullanici):
                st.session_state.pop("son_paylasim", None)
                st.success(t("Bütün paylaşım bağlantıları iptal edildi."))
                st.rerun()
