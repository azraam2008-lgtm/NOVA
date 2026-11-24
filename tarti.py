"""
tarti.py - Tartı günleri ve kilo geçmişi kuralları

Hem uygulama (app.py) hem de GitHub Actions'ta çalışan hatırlatma betiği
(hatirlatma.py) tartı günlerini buradan alır. Bu yüzden dosya Streamlit'e
ya da Supabase'e bağlı değildir.
"""

import datetime

# datetime.weekday(): Pazartesi=0 ... Pazar=6
TARTI_GUNLERI = frozenset({0, 4, 6})  # Pazartesi, Cuma, Pazar


def tarti_gunu_mu(gun):
    return gun.weekday() in TARTI_GUNLERI


def tartildi_mi(profil, gun):
    """O tarihte kilo geçmişinde kayıt var mı."""
    hedef = str(gun)
    return any(k.get("tarih") == hedef for k in profil.get("kilo_gecmisi", []) or [])


def kilo_gecmisine_yaz(profil, tarih, kilo, bugun=None):
    """Kilo kaydını profile işler (kaydetmez).

    - Gelecek tarih kabul edilmez (ValueError).
    - Aynı tarihte kayıt varsa yenisi eklenmez, eskisi güncellenir.
    - Geçmiş tarihe göre sıralanır.
    - mevcut_kilo ve son_tarti_tarihi yalnızca bu kayıt en yeni tartıysa değişir;
      eski bir tarihi girmek güncel kiloyu ezmez.
    """
    bugun = bugun or datetime.date.today()
    if isinstance(tarih, str):
        tarih = datetime.date.fromisoformat(tarih)
    if tarih > bugun:
        raise ValueError("Gelecek bir tarihe kilo girilemez.")

    tarih_str = str(tarih)
    kilo = round(float(kilo), 1)
    gecmis = [dict(k) for k in (profil.get("kilo_gecmisi") or []) if k.get("tarih") != tarih_str]
    gecmis.append({"tarih": tarih_str, "kilo": kilo})
    gecmis.sort(key=lambda k: k.get("tarih", ""))
    profil["kilo_gecmisi"] = gecmis

    if gecmis[-1]["tarih"] == tarih_str:
        profil["mevcut_kilo"] = kilo
        profil["son_tarti_tarihi"] = tarih_str
    return profil
