"""
oturum.py - "Beni hatırla" kalıcı oturum

Sayfa yenilenince çıkış yapılmasını engeller. Tarayıcıya bir çerez yazılır,
çerezin yalnızca özeti veritabanındaki "oturumlar" tablosunda tutulur.

Streamlit'in kendi st.context.cookies özelliği Community Cloud'da çalışmıyor
(proxy çerezleri filtreliyor), o yüzden extra-streamlit-components kullanılıyor.

app.py içinde:
    from oturum import cerezden_giris, oturum_baslat, oturum_bitir, cikis_dugmesi

Gerekli tablo: oturumlar (supabase_kurulum.sql)
Gerekli paket: extra-streamlit-components (requirements.txt)
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import streamlit as st

CEREZ_ADI = "nova_oturum"
GUN = 30


def _ozet(belirtec):
    return hashlib.sha256(str(belirtec).encode("utf-8")).hexdigest()


def _yonetici():
    """O anki çizimin çerez yöneticisi. oturum_tazele() onu hazırlar."""
    return st.session_state.get("_cerez_yoneticisi")


def kullanilabilir_mi():
    return _yonetici() is not None


def oturum_tazele():
    """Tarayıcıdaki çerezleri okur. Her çizimde TAM BİR KEZ çağrılmalı.

    CookieManager çerezleri yalnızca kurulurken okuyor. Nesne önbellekte
    tutulursa sayfa yenilendiğinde bileşen hiç çizilmez ve elde eski liste
    kalır; bu yüzden her çizimde yeniden kuruluyor. Aynı anahtar iki kez
    çizilemeyeceği için bu işlev app.py'nin başında bir kez çağrılır,
    diğer işlevler sonucu session_state'ten okur.
    """
    try:
        import extra_streamlit_components as stx
        cm = stx.CookieManager(key="nova_cerez")
    except Exception:  # noqa: BLE001
        st.session_state["_cerez_yoneticisi"] = None
        st.session_state["_cerezler"] = {}
        return {}
    cerezler = cm.cookies or {}
    st.session_state["_cerez_yoneticisi"] = cm
    st.session_state["_cerezler"] = cerezler

    # Bekleyen çerez işleri burada yapılır. Bunun sebebi önemli:
    # giriş anında st.rerun() çağrılıyor ve rerun betiği hemen kesiyor;
    # o çizimde yazılan çerez bileşeni tarayıcıya hiç ulaşmıyor. Bu yüzden
    # yazma ve silme bir sonraki çizime bırakılıyor.
    bekleyen = st.session_state.pop("_cerez_isi", None)
    if bekleyen:
        islem, deger = bekleyen
        if islem == "yaz":
            try:
                cm.set(CEREZ_ADI, deger,
                       expires_at=datetime.now() + timedelta(days=GUN),
                       key="nova_cerez_yaz")
                cerezler[CEREZ_ADI] = deger
            except Exception:  # noqa: BLE001
                pass
        elif islem == "sil":
            try:
                cm.delete(CEREZ_ADI, key="nova_cerez_sil")
                cerezler.pop(CEREZ_ADI, None)
            except Exception:  # noqa: BLE001
                pass
    return cerezler


def _belirtec():
    return (st.session_state.get("_cerezler") or {}).get(CEREZ_ADI)


# ----------------------------------------------------------------- Oturum aç
def oturum_baslat(db, kullanici):
    """Oturumu veritabanına kaydeder, çerez yazımını sıraya koyar.

    Çerez burada YAZILMAZ. Giriş akışı hemen st.rerun() çağırdığı için bu
    çizimde yazılan bileşen tarayıcıya ulaşmaz. Belirteç sıraya konur ve
    bir sonraki çizimde oturum_tazele() tarafından yazılır.
    """
    if db is None or not kullanilabilir_mi():
        return False
    belirtec = secrets.token_urlsafe(32)
    son = datetime.now(timezone.utc) + timedelta(days=GUN)
    try:
        db.table("oturumlar").insert({
            "belirtec_ozeti": _ozet(belirtec),
            "username": kullanici,
            "son_kullanma": son.isoformat(),
        }).execute()
    except Exception:  # noqa: BLE001
        return False
    st.session_state["_cerez_isi"] = ("yaz", belirtec)
    return True


# -------------------------------------------------------------- Oturum oku
def cerezden_giris(db):
    """Geçerli bir çerez varsa kullanıcı adını döndürür, yoksa None.

    Çerez bileşeni ilk çizimde boş dönebilir; o yüzden tek seferlik denenir ve
    sonsuz yenileme döngüsüne girilmez.
    """
    cm = _yonetici()
    if cm is None or db is None:
        return None
    if st.session_state.get("_oturum_denendi"):
        return None

    belirtec = _belirtec()

    if not belirtec:
        # Bileşen henüz cevap vermemiş olabilir; iki çizim hakkı tanınır
        sayac = st.session_state.get("_oturum_bekleme", 0) + 1
        st.session_state["_oturum_bekleme"] = sayac
        if sayac >= 3:
            st.session_state["_oturum_denendi"] = True
        return None

    st.session_state["_oturum_denendi"] = True
    try:
        res = (db.table("oturumlar").select("username, son_kullanma")
               .eq("belirtec_ozeti", _ozet(belirtec)).limit(1).execute())
    except Exception:  # noqa: BLE001
        return None
    if not res.data:
        _cerezi_sil(cm)
        return None

    satir = res.data[0]
    try:
        son = datetime.fromisoformat(str(satir["son_kullanma"]).replace("Z", "+00:00"))
        if son.tzinfo is None:
            son = son.replace(tzinfo=timezone.utc)
    except (ValueError, KeyError):
        return None
    if datetime.now(timezone.utc) > son:
        try:
            db.table("oturumlar").delete().eq("belirtec_ozeti", _ozet(belirtec)).execute()
        except Exception:  # noqa: BLE001
            pass
        _cerezi_sil(cm)
        return None

    return satir.get("username")


# ---------------------------------------------------------------- Oturum kapat
def _cerezi_sil(cm=None):
    """Çerez silmeyi sıraya koyar.

    Yazmada olduğu gibi burada da bileşen hemen çizilmez: çıkış akışı
    st.rerun() çağırıyor ve bu çizimdeki silme işlemi tarayıcıya ulaşmıyor.
    """
    st.session_state["_cerez_isi"] = ("sil", None)
    st.session_state.pop("_cerezler", None)


def oturum_bitir(db, kullanici=None):
    """Çerezi ve veritabanındaki kaydı siler."""
    cm = _yonetici()
    if cm is not None:
        belirtec = _belirtec()
        if belirtec and db is not None:
            try:
                db.table("oturumlar").delete().eq("belirtec_ozeti", _ozet(belirtec)).execute()
            except Exception:  # noqa: BLE001
                pass
        _cerezi_sil(cm)
    # Belirteç elde yoksa (ör. zaten girişliyken çıkış) kullanıcının tüm
    # oturumları silinir; böylece hiçbir kayıt arkada kalmaz.
    if db is not None and kullanici:
        try:
            db.table("oturumlar").delete().eq("username", kullanici).execute()
        except Exception:  # noqa: BLE001
            pass
    st.session_state["_cerezler"] = {}


def cikis_dugmesi(db, kullanici, anahtar="cikis"):
    """Çıkış yap düğmesi. Basılırsa oturumu tamamen kapatır."""
    if st.button("Çıkış yap", key=anahtar, use_container_width=True):
        oturum_bitir(db, kullanici)
        google_ile_mi = False
        try:
            google_ile_mi = st.user.is_logged_in
        except Exception:  # noqa: BLE001
            pass
        st.session_state.clear()
        # session_state temizlendikten SONRA sıraya konur, yoksa silinirdi
        st.session_state["_cerez_isi"] = ("sil", None)
        if google_ile_mi:
            try:
                st.logout()
                return True
            except Exception:  # noqa: BLE001
                pass
        st.rerun()
    return False
