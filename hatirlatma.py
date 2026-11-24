"""
hatirlatma.py - Günlük hatırlatma gönderen betik

Bu dosya uygulamanın içinde değil, GitHub Actions'ta günde bir kez çalışır
(.github/workflows/hatirlatma.yml). Streamlit bir siteye telefon bildirimi
gönderemediği için hatırlatmalar e-posta ve (açıksa) Telegram ile gider.

Elle denemek için:
    SUPABASE_URL=... SUPABASE_KEY=... RESEND_API_KEY=... python hatirlatma.py --deneme

Seçenekler:
    --deneme       Hiçbir şey göndermez, kime ne gideceğini yazar
    --kullanici X  Sadece o kullanıcıya gönderir (test için)
"""

import argparse
import datetime
import os
import sys

from bildirim import ayar, eposta_ayarli_mi, kullaniciya_gonder
import tarti

_GUN_ADLARI = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

# Bir kullanıcıya günde en fazla bir hatırlatma
GUNLUK_SU_HEDEFI = 2.5
GUNLUK_ADIM_HEDEFI = 10000


def _baglan():
    from supabase import create_client
    url, anahtar = ayar("SUPABASE_URL"), ayar("SUPABASE_KEY")
    if not url or not anahtar:
        print("HATA: SUPABASE_URL ve SUPABASE_KEY tanımlı değil.", file=sys.stderr)
        sys.exit(1)
    return create_client(url, anahtar)


def _kullanicilari_al(db):
    """E-postası olan kullanıcıları ve verilerini getirir."""
    try:
        hesaplar = db.table("kullanicilar").select("username, email").execute().data or []
    except Exception as e:  # noqa: BLE001
        print(f"HATA: kullanıcılar okunamadı: {e}", file=sys.stderr)
        return []
    try:
        veriler = {r["username"]: r.get("data") or {}
                   for r in (db.table("kullanici_verileri").select("username, data").execute().data or [])}
    except Exception as e:  # noqa: BLE001
        print(f"HATA: kullanıcı verileri okunamadı: {e}", file=sys.stderr)
        return []

    cikti = []
    for h in hesaplar:
        ad = h.get("username")
        if not ad:
            continue
        veri = veriler.get(ad, {})
        cikti.append({
            "kullanici": ad,
            "eposta": (h.get("email") or "").strip(),
            "profil": veri.get("profil") or {},
            "kayitlar": veri.get("gunluk_kayitlar") or [],
            "aktivite": veri.get("aktivite_loglari") or {},
        })
    return cikti


def mesaj_olustur(k, bugun):
    """Kullanıcının bugününe bakıp hatırlatma metni üretir. Gerek yoksa None."""
    gun = str(bugun)
    profil = k["profil"]
    ad = (profil.get("ad") or k["kullanici"]).strip().capitalize()

    ogunler = [r for r in k["kayitlar"] if r.get("Tarih") == gun]
    akt = (k["aktivite"] or {}).get(gun, {}) or {}
    su = float(akt.get("su", 0) or 0)
    adim = int(akt.get("adim", 0) or 0)

    satirlar = []
    if not ogunler:
        satirlar.append("Bugün hiç öğün kaydetmemişsin. Akşam kapanmadan birkaç dakikanı ayırırsan "
                        "haftalık tablon eksik kalmaz.")
    else:
        kalori = sum(float(r.get("Kalori", 0) or 0) for r in ogunler)
        satirlar.append(f"Bugün {len(ogunler)} kalem kaydettin, toplam {round(kalori)} kcal.")

    if su < GUNLUK_SU_HEDEFI * 0.6:
        satirlar.append(f"Su: {su:.2f} litre. Hedefin {GUNLUK_SU_HEDEFI} litre, biraz geriden geliyorsun.")
    if adim and adim < GUNLUK_ADIM_HEDEFI * 0.5:
        satirlar.append(f"Adım: {adim}. Kısa bir yürüyüş hedefe yaklaştırır.")

    # Oruç modundaysa mesaj oruç düzenine göre yazılır
    if profil.get("oruc_modu"):
        satirlar = _oruc_satirlari(k, ogunler, su, satirlar)

    # Tartı günü hatırlatması (Pazartesi, Cuma, Pazar; tarti.TARTI_GUNLERI)
    if tarti.tarti_gunu_mu(bugun) and not tarti.tartildi_mi(profil, bugun):
        satirlar.append(f"Bugün {_GUN_ADLARI[bugun.weekday()]}, tartı günü. "
                        "Tartılıp kilonu girersen gelişim grafiğin güncellenir.")

    # Söylenecek olumsuz bir şey yoksa rahatsız etme
    if len(satirlar) == 1 and ogunler and su >= GUNLUK_SU_HEDEFI * 0.6:
        return None
    if not satirlar:
        return None

    return f"Merhaba {ad},\n\n" + "\n".join(satirlar) + "\n\nNova"


def _oruc_satirlari(k, ogunler, su, satirlar):
    """Oruç tutan kullanıcı için mesajı yeniden yazar.

    Oruçluyken "bugün hiç öğün kaydetmemişsin" demek anlamsız; gündüz zaten
    yemiyor. Bunun yerine sahur ve iftarın kaydedilip kaydedilmediğine bakılır.
    """
    adlar = {(r.get("Öğün") or "").strip() for r in ogunler}
    yeni = []
    if "Sahur" not in adlar and "İftar" not in adlar:
        yeni.append("Bugün sahur ve iftar kaydın görünmüyor. İftardan sonra birkaç dakikanı "
                    "ayırıp girersen haftalık tablon eksik kalmaz.")
    elif "İftar" not in adlar:
        yeni.append("Sahurunu kaydetmişsin, iftarın eksik görünüyor.")
    elif "Sahur" not in adlar:
        yeni.append("İftarını kaydetmişsin, sahurun eksik görünüyor.")
    else:
        yeni.append(f"Bugün {len(ogunler)} kalem kaydettin.")

    if su < GUNLUK_SU_HEDEFI * 0.6:
        yeni.append(f"Su: {su:.2f} litre. İftar ile sahur arasında {GUNLUK_SU_HEDEFI} litreye "
                    "ulaşmaya çalış; tek seferde değil, yayarak.")
    # Adım uyarısı oruçluyken çıkarılıyor: gündüz hareket zaten kısıtlı
    return yeni


def main():
    ayrıstirici = argparse.ArgumentParser(description="Nova günlük hatırlatmaları")
    ayrıstirici.add_argument("--deneme", action="store_true", help="gönderme, sadece yaz")
    ayrıstirici.add_argument("--kullanici", default=None, help="sadece bu kullanıcıya")
    args = ayrıstirici.parse_args()

    if not eposta_ayarli_mi() and not args.deneme:
        print("HATA: e-posta gönderimi ayarlanmamış (RESEND_API_KEY / BREVO_API_KEY / SMTP_HOST).",
              file=sys.stderr)
        sys.exit(1)

    bugun = datetime.date.today()
    db = _baglan()
    kullanicilar = _kullanicilari_al(db)

    gonderildi = atlandi = hata = 0
    for k in kullanicilar:
        if args.kullanici and k["kullanici"] != args.kullanici:
            continue
        profil = k["profil"]

        # Kullanıcı hatırlatmaları kapatmışsa dokunma
        if not profil.get("hatirlatma_acik"):
            atlandi += 1
            continue
        if not k["eposta"] and not profil.get("telegram_id"):
            atlandi += 1
            continue

        metin = mesaj_olustur(k, bugun)
        if metin is None:
            atlandi += 1
            continue

        if args.deneme:
            print(f"--- {k['kullanici']} ({k['eposta'] or 'telegram'}) ---\n{metin}\n")
            gonderildi += 1
            continue

        sonuclar = kullaniciya_gonder(profil, k["eposta"], "Nova günlük hatırlatman", metin)
        if any(s[1] for s in sonuclar):
            gonderildi += 1
        else:
            hata += 1
            for kanal, basarili, mesaj in sonuclar:
                if not basarili:
                    print(f"  {k['kullanici']} {kanal}: {mesaj}", file=sys.stderr)

    print(f"Toplam {len(kullanicilar)} kullanıcı · gönderildi {gonderildi} · "
          f"atlandı {atlandi} · hata {hata}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
