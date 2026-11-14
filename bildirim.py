"""
bildirim.py - Nova'nın e-posta ve Telegram gönderimi

İki yerden kullanılır:
    - Uygulamanın içinden (şifre sıfırlama kodu)
    - GitHub Actions'ın her gün çalıştırdığı hatirlatma.py (günlük hatırlatmalar)

O yüzden ayarları önce ortam değişkeninden, bulamazsa Streamlit Secrets'tan okur.

AYARLAR (en az bir e-posta yolu gerekli)

  Resend ile (en kolay, ücretsiz başlangıç):
      RESEND_API_KEY = "re_..."
      GONDEREN = "Nova <onboarding@resend.dev>"

  ya da Brevo ile:
      BREVO_API_KEY = "xkeysib-..."
      GONDEREN = "Nova <senin@adresin.com>"

  ya da kendi e-posta hesabınla (Gmail'de "uygulama şifresi" gerekir):
      SMTP_HOST = "smtp.gmail.com"
      SMTP_PORT = "587"
      SMTP_USER = "senin@gmail.com"
      SMTP_PASS = "uygulama-sifresi"
      GONDEREN = "Nova <senin@gmail.com>"

  Telefona anlık bildirim istersen (isteğe bağlı):
      TELEGRAM_BOT_TOKEN = "123456:ABC..."
"""

import os
import re
import smtplib
from email.message import EmailMessage

import requests

ZAMAN_ASIMI = 15


def ayar(ad, varsayilan=None):
    """Önce ortam değişkeni, sonra Streamlit Secrets."""
    deger = os.environ.get(ad)
    if deger:
        return deger
    try:
        import streamlit as st
        return st.secrets.get(ad, varsayilan)
    except Exception:  # noqa: BLE001
        return varsayilan


def eposta_gecerli_mi(adres):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}", (adres or "").strip()))


def eposta_ayarli_mi():
    return bool(ayar("RESEND_API_KEY") or ayar("BREVO_API_KEY") or ayar("SMTP_HOST"))


# ------------------------------------------------------------------ E-posta
def _resend(alici, konu, metin, html, gonderen):
    cevap = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {ayar('RESEND_API_KEY')}",
                 "Content-Type": "application/json"},
        json={"from": gonderen, "to": [alici], "subject": konu,
              "text": metin, "html": html or _html_sar(konu, metin)},
        timeout=ZAMAN_ASIMI,
    )
    if cevap.status_code in (200, 201):
        return True, "gönderildi"
    return False, f"Resend {cevap.status_code}: {cevap.text[:200]}"


def _brevo(alici, konu, metin, html, gonderen):
    ad, adres = _gonderen_parcala(gonderen)
    cevap = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={"api-key": ayar("BREVO_API_KEY"), "Content-Type": "application/json"},
        json={"sender": {"name": ad, "email": adres}, "to": [{"email": alici}],
              "subject": konu, "textContent": metin,
              "htmlContent": html or _html_sar(konu, metin)},
        timeout=ZAMAN_ASIMI,
    )
    if cevap.status_code in (200, 201):
        return True, "gönderildi"
    return False, f"Brevo {cevap.status_code}: {cevap.text[:200]}"


def _smtp(alici, konu, metin, html, gonderen):
    mesaj = EmailMessage()
    mesaj["Subject"], mesaj["From"], mesaj["To"] = konu, gonderen, alici
    mesaj.set_content(metin)
    mesaj.add_alternative(html or _html_sar(konu, metin), subtype="html")
    try:
        port = int(ayar("SMTP_PORT", "587"))
        with smtplib.SMTP(ayar("SMTP_HOST"), port, timeout=ZAMAN_ASIMI) as sunucu:
            sunucu.starttls()
            kullanici, sifre = ayar("SMTP_USER"), ayar("SMTP_PASS")
            if kullanici and sifre:
                sunucu.login(kullanici, sifre)
            sunucu.send_message(mesaj)
        return True, "gönderildi"
    except Exception as e:  # noqa: BLE001
        return False, f"SMTP: {e}"


def _gonderen_parcala(gonderen):
    m = re.match(r"\s*(.*?)\s*<([^>]+)>\s*$", gonderen or "")
    return (m.group(1) or "Nova", m.group(2)) if m else ("Nova", (gonderen or "").strip())


def _html_sar(baslik, metin):
    govde = "".join(f"<p style='margin:0 0 14px'>{satir}</p>"
                    for satir in metin.strip().split("\n") if satir.strip())
    return f"""<!doctype html><html><body style="margin:0;background:#f4f5f7;padding:28px 14px;">
<div style="max-width:520px;margin:0 auto;background:#ffffff;border-radius:18px;padding:32px;
     font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1a1a1a;line-height:1.6;">
  <div style="font-family:Georgia,serif;font-size:26px;letter-spacing:9px;text-align:center;
       margin-bottom:6px;">N O V A</div>
  <div style="text-align:center;color:#8a8a8a;font-size:11px;letter-spacing:3px;
       margin-bottom:26px;">ZARAFET VE DENGE</div>
  <h2 style="font-size:17px;margin:0 0 14px;">{baslik}</h2>
  {govde}
  <p style="color:#9a9a9a;font-size:12px;margin-top:26px;border-top:1px solid #eee;padding-top:14px;">
    Bu e-posta Nova uygulamasından gönderildi. Hatırlatmaları uygulamadaki
    Hesap ve Verilerin bölümünden kapatabilirsin.</p>
</div></body></html>"""


def eposta_gonder(alici, konu, metin, html=None):
    """E-posta gönderir. (başarili, mesaj) döner."""
    if not eposta_gecerli_mi(alici):
        return False, "E-posta adresi geçersiz."
    gonderen = ayar("GONDEREN", "Nova <onboarding@resend.dev>")
    try:
        if ayar("RESEND_API_KEY"):
            return _resend(alici, konu, metin, html, gonderen)
        if ayar("BREVO_API_KEY"):
            return _brevo(alici, konu, metin, html, gonderen)
        if ayar("SMTP_HOST"):
            return _smtp(alici, konu, metin, html, gonderen)
    except requests.RequestException as e:
        return False, f"Bağlantı hatası: {e}"
    except Exception as e:  # noqa: BLE001
        return False, f"Beklenmeyen hata: {e}"
    return False, "E-posta gönderimi ayarlanmamış. Secrets'a RESEND_API_KEY ekle."


# ------------------------------------------------------------------ Telegram
def telegram_ayarli_mi():
    return bool(ayar("TELEGRAM_BOT_TOKEN"))


def telegram_gonder(sohbet_id, metin):
    """Telefona anlık bildirim. (başarili, mesaj) döner."""
    jeton = ayar("TELEGRAM_BOT_TOKEN")
    if not jeton:
        return False, "Telegram botu ayarlanmamış."
    if not str(sohbet_id or "").strip():
        return False, "Telegram sohbet kimliği yok."
    try:
        cevap = requests.post(
            f"https://api.telegram.org/bot{jeton}/sendMessage",
            json={"chat_id": str(sohbet_id).strip(), "text": metin,
                  "disable_web_page_preview": True},
            timeout=ZAMAN_ASIMI,
        )
        if cevap.status_code == 200 and (cevap.json() or {}).get("ok"):
            return True, "gönderildi"
        return False, f"Telegram {cevap.status_code}: {cevap.text[:200]}"
    except requests.RequestException as e:
        return False, f"Bağlantı hatası: {e}"
    except Exception as e:  # noqa: BLE001
        return False, f"Beklenmeyen hata: {e}"


# --------------------------------------------------------- Kullanıcıya gönder
def kullaniciya_gonder(profil, eposta, konu, metin):
    """Kullanıcının açık olan kanallarına gönderir. Sonuç listesi döner."""
    profil = profil or {}
    sonuclar = []
    if profil.get("bildirim_eposta", True) and eposta:
        sonuclar.append(("e-posta",) + eposta_gonder(eposta, konu, metin))
    sohbet = profil.get("telegram_id", "")
    if profil.get("bildirim_telegram") and sohbet:
        sonuclar.append(("telegram",) + telegram_gonder(sohbet, f"{konu}\n\n{metin}"))
    return sonuclar
