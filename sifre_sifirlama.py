"""
sifre_sifirlama.py - Şifremi unuttum akışı

Kullanıcı adını ya da e-postasını yazar, e-postasına 6 haneli bir kod gider,
kodu ve yeni şifresini girer. Kodun kendisi veritabanında saklanmaz, yalnızca özeti.

app.py içinde, giriş ekranında:

    from sifre_sifirlama import sifre_sifirlama_bolumu
    sifre_sifirlama_bolumu(supabase, sifre_olustur, sifre_kontrol)

Gerekli tablo: sifre_sifirlama (supabase_kurulum.sql içinde)
Gerekli ayar: bildirim.py'deki e-posta ayarlarından biri
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import streamlit as st

from bildirim import eposta_ayarli_mi, eposta_gonder

GECERLILIK_DK = 15
EN_FAZLA_DENEME = 5


def _ozet(kod):
    return hashlib.sha256(str(kod).strip().encode("utf-8")).hexdigest()


def _kullaniciyi_bul(db, girdi):
    """Kullanıcı adı ya da e-posta ile arar. (kullanici_adi, eposta) ya da (None, None)."""
    girdi = (girdi or "").strip().lower()
    if not girdi or db is None:
        return None, None
    try:
        sutun = "email" if "@" in girdi else "username"
        res = db.table("kullanicilar").select("username, email").eq(sutun, girdi).limit(1).execute()
        if res.data:
            return res.data[0]["username"], (res.data[0].get("email") or "")
    except Exception:  # noqa: BLE001
        pass
    return None, None


def _kod_olustur_ve_gonder(db, kullanici, eposta):
    kod = f"{secrets.randbelow(900000) + 100000}"
    son = datetime.now(timezone.utc) + timedelta(minutes=GECERLILIK_DK)
    try:
        db.table("sifre_sifirlama").upsert({
            "username": kullanici, "kod_ozeti": _ozet(kod),
            "son_kullanma": son.isoformat(), "deneme": 0,
        }, on_conflict="username").execute()
    except Exception as e:  # noqa: BLE001
        return False, f"Kod kaydedilemedi: {e}"

    metin = (f"Merhaba,\n\nNova şifreni sıfırlamak için kodun: {kod}\n\n"
             f"Bu kod {GECERLILIK_DK} dakika geçerli.\n"
             "Bu isteği sen yapmadıysan bu e-postayı yok sayabilirsin, şifren değişmez.")
    return eposta_gonder(eposta, "Nova şifre sıfırlama kodun", metin)


def _kodu_dogrula(db, kullanici, kod):
    """(gecerli_mi, mesaj) döner."""
    try:
        res = db.table("sifre_sifirlama").select("*").eq("username", kullanici).limit(1).execute()
    except Exception as e:  # noqa: BLE001
        return False, f"Doğrulama yapılamadı: {e}"
    if not res.data:
        return False, "Bu hesap için bekleyen bir kod yok. Yeniden kod iste."

    satir = res.data[0]
    if int(satir.get("deneme", 0)) >= EN_FAZLA_DENEME:
        return False, "Çok fazla yanlış deneme yapıldı. Yeniden kod iste."

    try:
        son = datetime.fromisoformat(str(satir["son_kullanma"]).replace("Z", "+00:00"))
        if son.tzinfo is None:
            son = son.replace(tzinfo=timezone.utc)
    except (ValueError, KeyError):
        return False, "Kodun süresi okunamadı. Yeniden kod iste."
    if datetime.now(timezone.utc) > son:
        return False, "Kodun süresi dolmuş. Yeniden kod iste."

    if not secrets.compare_digest(str(satir.get("kod_ozeti", "")), _ozet(kod)):
        try:
            db.table("sifre_sifirlama").update(
                {"deneme": int(satir.get("deneme", 0)) + 1}).eq("username", kullanici).execute()
        except Exception:  # noqa: BLE001
            pass
        kalan = EN_FAZLA_DENEME - int(satir.get("deneme", 0)) - 1
        return False, f"Kod yanlış. {max(kalan, 0)} deneme hakkın kaldı."
    return True, ""


def sifre_sifirlama_bolumu(db, sifre_olustur, sifre_kontrol):
    """Giriş ekranındaki 'Şifremi unuttum' bölümü."""
    with st.expander("Şifremi unuttum"):
        if not eposta_ayarli_mi():
            st.info("Şifre sıfırlama için e-posta gönderimi henüz ayarlanmamış. "
                    "Uygulama sahibi Secrets'a RESEND_API_KEY eklemeli.")
            return

        asama = st.session_state.get("sifirlama_asama", "kod_iste")

        if asama == "kod_iste":
            girdi = st.text_input("Kullanıcı adın ya da e-postan", key="sifirlama_girdi")
            if st.button("Kod gönder", key="sifirlama_gonder", use_container_width=True):
                kullanici, eposta = _kullaniciyi_bul(db, girdi)
                # Hesabın olup olmadığını dışarıya söyleme
                if kullanici and eposta:
                    basarili, mesaj = _kod_olustur_ve_gonder(db, kullanici, eposta)
                    if basarili:
                        st.session_state["sifirlama_asama"] = "kod_gir"
                        st.session_state["sifirlama_kullanici"] = kullanici
                        st.rerun()
                    else:
                        st.error(f"Kod gönderilemedi. {mesaj}")
                elif kullanici and not eposta:
                    st.warning("Bu hesapta kayıtlı e-posta yok, bu yüzden kod gönderilemiyor. "
                               "Hesabı Google ile açtıysan Google ile giriş yapabilirsin.")
                else:
                    st.success("Böyle bir hesap varsa e-posta adresine bir kod gönderildi. "
                               "Gelen kutunu ve istenmeyen klasörünü kontrol et.")

        else:
            kullanici = st.session_state.get("sifirlama_kullanici", "")
            st.success(f"**{kullanici}** hesabının e-postasına {GECERLILIK_DK} dakika geçerli "
                       "bir kod gönderildi.")
            kod = st.text_input("E-postana gelen 6 haneli kod", max_chars=6, key="sifirlama_kod")
            yeni = st.text_input("Yeni şifren (en az 8 karakter, bir büyük harf ve bir rakam)",
                                 type="password", key="sifirlama_yeni")
            yeni2 = st.text_input("Yeni şifren (tekrar)", type="password", key="sifirlama_yeni2")

            c1, c2 = st.columns([3, 1])
            if c1.button("Şifremi değiştir", key="sifirlama_bitir",
                         type="primary", use_container_width=True):
                hata = sifre_kontrol(yeni)
                if not kod.strip():
                    st.error("Kodu gir.")
                elif hata:
                    st.error(hata)
                elif yeni != yeni2:
                    st.error("İki şifre birbirini tutmuyor.")
                else:
                    gecerli, mesaj = _kodu_dogrula(db, kullanici, kod)
                    if not gecerli:
                        st.error(mesaj)
                    else:
                        try:
                            db.table("kullanicilar").update(
                                {"password_hash": sifre_olustur(yeni)}
                            ).eq("username", kullanici).execute()
                            db.table("sifre_sifirlama").delete().eq("username", kullanici).execute()
                            # Eski "beni hatırla" oturumları da düşsün
                            db.table("oturumlar").delete().eq("username", kullanici).execute()
                        except Exception as e:  # noqa: BLE001
                            st.error(f"Şifre değiştirilemedi: {e}")
                        else:
                            for anahtar in ("sifirlama_asama", "sifirlama_kullanici"):
                                st.session_state.pop(anahtar, None)
                            st.success("Şifren değişti. Artık yeni şifrenle giriş yapabilirsin.")

            if c2.button("Vazgeç", key="sifirlama_iptal", use_container_width=True):
                for anahtar in ("sifirlama_asama", "sifirlama_kullanici"):
                    st.session_state.pop(anahtar, None)
                st.rerun()
