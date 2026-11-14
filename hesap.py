"""
hesap.py - Hesap ayarları: verilerini indir ve hesabını sil

app.py içinde kullanım:

    from hesap import hesap_bolumu
    hesap_bolumu(supabase, aktif_user, st.session_state.gunluk_kayitlar,
                 st.session_state.aktivite_loglari, p)

Hesap silme KVKK açısından da gerekli: kullanıcı verisinin kendisinde kalan bir kopyasını
alabilmeli ve istediğinde hesabını tamamen sildirebilmeli.
"""

import datetime
import json

import streamlit as st


def _tum_veri(kullanici, gunluk_kayitlar, aktivite_loglari, profil, db=None):
    """Kullanıcının Nova'daki her şeyi, tek bir JSON yapısında."""
    veri = {
        "nova_veri_disa_aktarma": {
            "kullanici": kullanici,
            "tarih": datetime.datetime.now().isoformat(timespec="seconds"),
            "aciklama": "Nova hesabındaki tüm veriler. Bu dosyayı saklayabilir ya da "
                        "diyetisyenine gönderebilirsin.",
        },
        "profil": profil or {},
        "ogun_kayitlari": gunluk_kayitlar or [],
        "gunluk_aktivite": aktivite_loglari or {},
    }
    # Kendi eklediği yemekler ve favorileri de dahil et
    if db is not None:
        try:
            res = db.table("kullanici_yemekleri").select("tur, ad, veri").eq("kullanici", kullanici).execute()
            veri["kendi_yemeklerim_ve_favorilerim"] = res.data or []
        except Exception:  # noqa: BLE001
            pass
    return veri


def _hesabi_sil(db, kullanici):
    """Kullanıcının bütün satırlarını siler. Hata olursa False döner."""
    tablolar = [
        ("kullanici_verileri", "username"),
        ("kullanici_yemekleri", "kullanici"),
        ("oturumlar", "username"),
        ("sifre_sifirlama", "username"),
        ("kullanicilar", "username"),   # en sona, çünkü hesabın kendisi
    ]
    hatalar = []
    for tablo, sutun in tablolar:
        try:
            db.table(tablo).delete().eq(sutun, kullanici).execute()
        except Exception as e:  # noqa: BLE001
            # Tablo henüz oluşturulmadıysa sorun değil, diğerlerine devam
            if "does not exist" not in str(e).lower():
                hatalar.append(f"{tablo}: {e}")
    # Yapay zeka sayacı kullanıcı anahtarını "user:" ön ekiyle tutuyor
    try:
        db.table("ai_kullanim").delete().eq("kullanici", f"user:{kullanici}").execute()
    except Exception:  # noqa: BLE001
        pass
    return hatalar


def hesap_bolumu(db, kullanici, gunluk_kayitlar, aktivite_loglari, profil,
                 sifre_dogrula=None, sifre_ozeti=None):
    """Verilerini indir ve hesabını sil bölümünü çizer."""
    st.markdown("#### Verilerin")
    st.caption("Nova'daki bütün verilerin senin. İstediğin zaman indirebilir ya da sildirebilirsin.")

    veri = _tum_veri(kullanici, gunluk_kayitlar, aktivite_loglari, profil, db)
    kalem = len(veri["ogun_kayitlari"])
    gun = len(veri["gunluk_aktivite"])
    st.caption(f"Hesabında {kalem} öğün kaydı ve {gun} günlük aktivite kaydı var.")

    st.download_button(
        "Verilerimi indir (JSON)",
        json.dumps(veri, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name=f"nova_verilerim_{kullanici}_{datetime.date.today()}.json",
        mime="application/json",
        use_container_width=True,
    )

    st.divider()
    st.markdown("#### Hesabını sil")
    st.caption("Hesabın ve bütün kayıtların kalıcı olarak silinir. Bu işlem geri alınamaz.")

    with st.expander("Hesabımı silmek istiyorum"):
        st.warning("Silmeden önce verilerini indirmeni öneririm. Silinen veriler geri getirilemez.")

        onay = st.text_input(
            f"Onaylamak için kullanıcı adını yaz: {kullanici}",
            key="hesap_sil_onay", placeholder=kullanici)

        sifre = ""
        if sifre_dogrula is not None and sifre_ozeti:
            sifre = st.text_input("Şifreni gir", type="password", key="hesap_sil_sifre")

        if st.button("Hesabımı kalıcı olarak sil", key="hesap_sil_btn"):
            if onay.strip() != kullanici:
                st.error("Kullanıcı adını tam olarak yazman gerekiyor.")
            elif sifre_dogrula is not None and sifre_ozeti and not sifre_dogrula(sifre, sifre_ozeti):
                st.error("Şifre yanlış.")
            elif db is None:
                st.error("Veritabanına bağlanılamadı, silme yapılamadı.")
            else:
                hatalar = _hesabi_sil(db, kullanici)
                if hatalar:
                    st.error("Bazı kayıtlar silinemedi: " + "; ".join(hatalar))
                else:
                    st.session_state.clear()
                    st.success("Hesabın silindi. Nova'yı kullandığın için teşekkürler.")
                    st.rerun()
