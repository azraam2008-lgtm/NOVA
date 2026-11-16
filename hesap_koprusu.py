"""
hesap_koprusu.py - Eski hesaplardan Supabase Auth'a köprü

Neden: Telefon uygulaması gizli service_role anahtarını taşıyamaz (uygulamadan
çıkarılabilir ve bütün veritabanı okunur). Uygulama kullanıcıyı Supabase'in kendi
giriş sistemiyle (Auth) tanır, veritabanı kuralları da (RLS) herkese yalnızca kendi
satırlarını gösterir. Bunun için her Nova hesabının bir Auth karşılığı olmalı.

Kural: bir hesabın Auth karşılığı (auth_id) oluştuğu anda şifrenin TEK doğrusu
Auth'tur. kullanicilar.password_hash ondan sonra kullanılmaz. Şifre iki yerde
tutulursa biri değiştiğinde öteki eskir ve kullanıcı bir yerden giremez.

Taşıma sessiz ve kayıpsız:
  - Siteye giren kullanıcının Auth hesabı o anda, girdiği şifreyle açılır.
  - Siteye hiç girmeyen kullanıcı uygulamadan ilk girdiğinde sunucu fonksiyonu
    aynı işi yapar (supabase/functions/giris).
  - Google ile girenlerin şifresi yok; Auth onları ilk Google girişinde e-postayla
    kendisi eşler.

E-postası olmayan hesaplar için Auth'a kullanıcı adından türetilen bir adres
yazılır (kullanici@hesap.nova.invalid). ".invalid" uzantısı internette asla
gerçek bir adres olamayacak şekilde ayrılmıştır; oraya e-posta gitmez.
"""

import re

SAHTE_ALAN = "hesap.nova.invalid"


def giris_epostasi(kullanici, eposta=None):
    """Auth'a yazılacak e-posta. Gerçek e-posta yoksa kullanıcı adından türetilir."""
    eposta = (eposta or "").strip().lower()
    if eposta and "@" in eposta:
        return eposta
    temiz = re.sub(r"[^a-z0-9._-]", "", (kullanici or "").lower()) or "kullanici"
    return f"{temiz}@{SAHTE_ALAN}"


def sahte_mi(eposta):
    return (eposta or "").endswith("@" + SAHTE_ALAN)


def _admin(db):
    return db.auth.admin


def _id(yanit):
    """create_user yanıtından kullanıcı kimliğini çıkarır (sürümler arasında biçim değişebiliyor)."""
    kullanici = getattr(yanit, "user", None) or yanit
    return str(getattr(kullanici, "id", "") or (kullanici.get("id") if isinstance(kullanici, dict) else ""))


def auth_id_al(db, kullanici):
    try:
        res = db.table("kullanicilar").select("auth_id").eq("username", kullanici).limit(1).execute()
        return (res.data[0].get("auth_id") or None) if res.data else None
    except Exception:  # noqa: BLE001  (sütun henüz yoksa da buraya düşer)
        return None


def auth_olustur(db, kullanici, eposta, sifre=None, sifre_ozeti=None):
    """Hesap için Auth kullanıcısı açar, kimliğini kullanicilar.auth_id'ye yazar.

    sifre        : düz şifre (girişte elimizde olan)
    sifre_ozeti  : bcrypt özeti ($2...). Düz şifre yoksa, toplu taşımada kullanılır.
    Başarılıysa auth_id döner, olmazsa None. Hata giriş akışını asla durdurmaz.
    """
    if not sifre and not (sifre_ozeti or "").startswith("$2"):
        return None   # eski SHA-256 özeti Auth'a aktarılamaz; ilk girişte taşınır
    nitelik = {
        "email": giris_epostasi(kullanici, eposta),
        "email_confirm": True,               # adres zaten bizim kaydımızda; onay e-postası gönderme
        "user_metadata": {"username": kullanici},
    }
    if sifre:
        nitelik["password"] = sifre
    else:
        nitelik["password_hash"] = sifre_ozeti
    try:
        yeni = _id(_admin(db).create_user(nitelik))
    except Exception:  # noqa: BLE001
        return None
    if not yeni:
        return None
    try:
        db.table("kullanicilar").update({"auth_id": yeni}).eq("username", kullanici).execute()
    except Exception:  # noqa: BLE001
        # Auth hesabı açıldı ama bağlanamadı: yarım kalmasın diye geri al
        try:
            _admin(db).delete_user(yeni)
        except Exception:  # noqa: BLE001
            pass
        return None
    return yeni


def auth_ile_dogrula(url, anahtar, kullanici, eposta, sifre, istemci_fabrikasi=None):
    """Şifreyi Auth'a sorarak doğrular.

    Paylaşılan veritabanı istemcisiyle giriş YAPILMAZ: giriş yapınca o istemci
    kullanıcının yetkisiyle çalışmaya başlar ve uygulamanın geri kalanı bozulur.
    Bu yüzden her doğrulama için geçici bir istemci açılır.

    Döner: True doğru, False yanlış şifre, None servise ulaşılamadı.
    """
    if not sifre:
        return False
    if istemci_fabrikasi is None:
        from supabase import create_client as istemci_fabrikasi
    try:
        gecici = istemci_fabrikasi(url, anahtar)
        yanit = gecici.auth.sign_in_with_password(
            {"email": giris_epostasi(kullanici, eposta), "password": sifre})
    except Exception as e:  # noqa: BLE001
        metin = str(e).lower()
        if "invalid" in metin or "credentials" in metin or "400" in metin:
            return False
        return None
    try:
        gecici.auth.sign_out()
    except Exception:  # noqa: BLE001
        pass
    return bool(getattr(yanit, "user", None))


def sifre_guncelle(db, kullanici, yeni_sifre):
    """Şifre sıfırlama: Auth karşılığı varsa şifreyi orada değiştirir."""
    auth_id = auth_id_al(db, kullanici)
    if not auth_id:
        return False
    try:
        _admin(db).update_user_by_id(auth_id, {"password": yeni_sifre})
        return True
    except Exception:  # noqa: BLE001
        return False


def eposta_guncelle(db, kullanici, yeni_eposta):
    auth_id = auth_id_al(db, kullanici)
    if not auth_id:
        return False
    try:
        _admin(db).update_user_by_id(
            auth_id, {"email": giris_epostasi(kullanici, yeni_eposta), "email_confirm": True})
        return True
    except Exception:  # noqa: BLE001
        return False


def auth_sil(db, kullanici):
    """Hesap silinirken Auth karşılığı da silinir."""
    auth_id = auth_id_al(db, kullanici)
    if not auth_id:
        return True
    try:
        _admin(db).delete_user(auth_id)
        return True
    except Exception:  # noqa: BLE001
        return False


def toplu_tasi(db, sinir=500):
    """bcrypt özeti olan ama Auth karşılığı olmayan hesapları tek seferde taşır.

    Şart değil: girişlerde zaten taşınıyorlar. Uygulama çıkmadan önce bir kez
    çalıştırılırsa siteye uzun süre girmemiş kullanıcılar da hazır olur.
    Döner: (taşınan, atlanan)
    """
    try:
        satirlar = (db.table("kullanicilar").select("username, email, password_hash, auth_id")
                    .is_("auth_id", "null").limit(sinir).execute().data or [])
    except Exception:  # noqa: BLE001
        return 0, 0
    tasinan = atlanan = 0
    for s in satirlar:
        if auth_olustur(db, s["username"], s.get("email"), sifre_ozeti=s.get("password_hash")):
            tasinan += 1
        else:
            atlanan += 1
    return tasinan, atlanan
