"""
gelisim.py - Nova'nin Gelisim sekmesi

7 / 30 / 90 gunluk kalori, kilo, makro, ogun ve egzersiz raporlari.
Grafikler Altair ile cizilir; Altair Streamlit ile birlikte geldigi icin ek kurulum gerekmez.

app.py icinde kullanim:

    from gelisim import gelisim_sayfasi
    gelisim_sayfasi(st.session_state.gunluk_kayitlar, st.session_state.aktivite_loglari,
                    p, hedef_kalori_alim, bmr, tema)
"""

import datetime

import altair as alt
import pandas as pd
import streamlit as st

DONEMLER = {"Son 7 gün": 7, "Son 30 gün": 30, "Son 90 gün": 90}
OGUNLER = ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği", "Ara Öğün"]

MAVI, KIRMIZI, YESIL, SARI, GRI = "#4a9eff", "#ff5a52", "#32c75f", "#ffc93c", "#6b6b6b"
YAZI = "Plus Jakarta Sans, Helvetica Neue, Helvetica, Arial, sans-serif"


# ------------------------------------------------------------------ Yardımcılar
def _gun_listesi(gun_sayisi):
    bugun = datetime.date.today()
    return [bugun - datetime.timedelta(days=i) for i in range(gun_sayisi - 1, -1, -1)]


def _gunluk_tablo(gunluk_kayitlar, aktivite_loglari, gunler, bmr):
    """Her gün için alınan kalori, makrolar, adım, su ve harcanan enerji."""
    kayit_gun = {}
    for k in gunluk_kayitlar or []:
        kayit_gun.setdefault(k.get("Tarih"), []).append(k)

    satirlar = []
    for g in gunler:
        anahtar = str(g)
        ogunler = kayit_gun.get(anahtar, [])
        akt = (aktivite_loglari or {}).get(anahtar, {}) or {}
        adim = int(akt.get("adim", 0) or 0)
        egzersiz = float(akt.get("egzersiz_kalori", 0) or 0)
        satirlar.append({
            "tarih": g,
            "alinan": sum(float(k.get("Kalori", 0) or 0) for k in ogunler),
            "protein": sum(float(k.get("Protein", 0) or 0) for k in ogunler),
            "karb": sum(float(k.get("Karbonhidrat", 0) or 0) for k in ogunler),
            "yag": sum(float(k.get("Yağ", 0) or 0) for k in ogunler),
            "adim": adim,
            "su": float(akt.get("su", 0) or 0),
            "egzersiz": egzersiz,
            "harcanan": bmr + adim * 0.04 + egzersiz,
            "kayit_var": len(ogunler) > 0,
            "kalem": len(ogunler),
        })
    return pd.DataFrame(satirlar)


def _tema(grafik, renk):
    """Grafiği kartın koyu arka planına ve yazı rengine uydurur.

    Altair varsayılan olarak beyaz zemin çizer; koyu temada okunmaz hale gelir.
    Zemin saydam yapılır, bütün yazılar tema rengine çekilir.
    """
    return (grafik
            .configure(background="transparent")
            .configure_view(strokeWidth=0, fill="transparent")
            .configure_axis(labelColor=renk, titleColor=renk, domainColor=renk,
                            gridColor=renk, gridOpacity=0.15, tickColor=renk,
                            labelFontSize=11, titleFontSize=11, labelFont=YAZI, titleFont=YAZI)
            .configure_legend(labelColor=renk, titleColor=renk, labelFontSize=11,
                              labelFont=YAZI, symbolType="square")
            .configure_title(color=renk))


def _tarih_ekseni(satir_sayisi):
    adim = 1 if satir_sayisi <= 10 else (5 if satir_sayisi <= 35 else 14)
    return alt.X("tarih:T", title=None,
                 axis=alt.Axis(format="%d %b", labelAngle=0, labelOverlap="greedy",
                               tickCount=min(satir_sayisi, max(2, satir_sayisi // adim))))


# --------------------------------------------------------------- Kalori raporu
def _kalori_bolumu(df, hedef_kalori, gun_sayisi, renk):
    st.markdown("#### Kalori")
    kayitli = df[df["kayit_var"]]
    if kayitli.empty:
        st.caption("Bu dönemde öğün kaydın yok.")
        return

    ortalama = kayitli["alinan"].mean()
    fark = ortalama - hedef_kalori
    c1, c2, c3 = st.columns(3)
    c1.metric("Günlük ortalaman", f"{round(ortalama)} kcal",
              f"{fark:+.0f} kcal", delta_color="inverse")
    c2.metric("Hedefin", f"{round(hedef_kalori)} kcal")
    c3.metric("Kayıt tuttuğun gün", f"{len(kayitli)} / {len(df)}",
              f"%{len(kayitli) / len(df) * 100:.0f}")

    if gun_sayisi <= 30:
        veri = df.copy()
        veri["durum"] = veri.apply(
            lambda r: "Kayıt yok" if not r["kayit_var"]
            else ("Hedefin üstünde" if r["alinan"] > hedef_kalori else "Hedefin altında"), axis=1)
        alan = alt.Scale(domain=["Hedefin altında", "Hedefin üstünde", "Kayıt yok"],
                         range=[YESIL, KIRMIZI, "#4a4a4a"])
        y_basligi = "kcal"
        ipucu = [alt.Tooltip("tarih:T", title="Tarih", format="%d %B"),
                 alt.Tooltip("alinan:Q", title="Alınan kcal", format=".0f"),
                 alt.Tooltip("kalem:Q", title="Kalem")]
        kalinlik = max(5, int(230 / max(len(veri), 1)))
    else:
        veri = df[df["kayit_var"]].copy()
        veri["tarih"] = pd.to_datetime(veri["tarih"]).dt.to_period("W").dt.start_time
        veri = veri.groupby("tarih", as_index=False)["alinan"].mean()
        veri["durum"] = veri["alinan"].apply(
            lambda v: "Hedefin üstünde" if v > hedef_kalori else "Hedefin altında")
        alan = alt.Scale(domain=["Hedefin altında", "Hedefin üstünde"], range=[YESIL, KIRMIZI])
        y_basligi = "kcal (haftalık ortalama)"
        ipucu = [alt.Tooltip("tarih:T", title="Hafta başı", format="%d %B"),
                 alt.Tooltip("alinan:Q", title="Ortalama kcal", format=".0f")]
        kalinlik = 14
        st.caption("90 günlük görünümde her çubuk bir haftanın ortalamasıdır.")

    cubuklar = alt.Chart(veri).mark_bar(
        cornerRadiusTopLeft=3, cornerRadiusTopRight=3, size=kalinlik).encode(
        x=_tarih_ekseni(len(veri)),
        y=alt.Y("alinan:Q", title=y_basligi),
        color=alt.Color("durum:N", scale=alan, legend=alt.Legend(title=None, orient="top")),
        tooltip=ipucu,
    )
    hedef_cizgi = alt.Chart(pd.DataFrame({"h": [hedef_kalori]})).mark_rule(
        color=MAVI, strokeDash=[6, 4], size=2).encode(y="h:Q")

    st.altair_chart(_tema((cubuklar + hedef_cizgi).properties(height=240), renk),
                    use_container_width=True)
    st.caption("Mavi kesikli çizgi günlük hedefin.")


# ----------------------------------------------------------------- Kilo raporu
def _kilo_bolumu(profil, gun_sayisi, renk):
    st.markdown("#### Kilo")
    gecmis = sorted(profil.get("kilo_gecmisi", []), key=lambda x: x.get("tarih", ""))
    if len(gecmis) < 2:
        st.caption("Kilo grafiğin ikinci tartından sonra görünecek. "
                   "Her Pazar tartılman ya da Günlük Özet'ten kilo girmen yeterli.")
        return

    baslangic = datetime.date.today() - datetime.timedelta(days=gun_sayisi)
    try:
        veri = pd.DataFrame([
            {"tarih": pd.to_datetime(k["tarih"]), "kilo": float(k["kilo"])}
            for k in gecmis if datetime.date.fromisoformat(k["tarih"]) >= baslangic
        ])
    except (ValueError, KeyError):
        st.caption("Kilo kayıtlarında okunamayan bir tarih var.")
        return

    if len(veri) < 2:
        st.caption(f"Son {gun_sayisi} günde en az iki tartı yok. Daha geniş bir dönem seç.")
        return

    hedef = float(profil.get("hedef_kilo", veri["kilo"].iloc[-1]))
    ilk, son = float(veri["kilo"].iloc[0]), float(veri["kilo"].iloc[-1])
    gun_araligi = max((veri["tarih"].iloc[-1] - veri["tarih"].iloc[0]).days, 1)
    haftalik = (son - ilk) / gun_araligi * 7

    c1, c2, c3 = st.columns(3)
    c1.metric("Şu anki kilon", f"{son:.1f} kg", f"{son - ilk:+.1f} kg")
    c2.metric("Haftalık değişim", f"{haftalik:+.2f} kg")
    c3.metric("Hedefe kalan", f"{abs(son - hedef):.1f} kg")

    olcek = alt.Scale(zero=False, nice=True)
    tarih_ekseni = alt.X("tarih:T", title=None,
                         axis=alt.Axis(format="%d %b", labelAngle=0,
                                       tickCount=min(len(veri), 7), labelOverlap="greedy"))
    cizgi = alt.Chart(veri).mark_line(color=MAVI, size=2, interpolate="monotone").encode(
        x=tarih_ekseni, y=alt.Y("kilo:Q", title="kg", scale=olcek))
    nokta = alt.Chart(veri).mark_circle(size=55, color=MAVI).encode(
        x="tarih:T", y=alt.Y("kilo:Q", scale=olcek),
        tooltip=[alt.Tooltip("tarih:T", title="Tarih", format="%d %B"),
                 alt.Tooltip("kilo:Q", title="Kilo", format=".1f")])
    hedef_cizgi = alt.Chart(pd.DataFrame({"h": [hedef]})).mark_rule(
        color=YESIL, strokeDash=[6, 4], size=2).encode(y=alt.Y("h:Q", scale=olcek))

    st.altair_chart(_tema((cizgi + nokta + hedef_cizgi).properties(height=240), renk),
                    use_container_width=True)
    st.caption("Yeşil kesikli çizgi hedef kilon. Günlük dalgalanma normaldir, eğilime bak.")

    if abs(haftalik) > 0.05 and abs(son - hedef) > 0.3:
        dogru_yon = (hedef < son and haftalik < 0) or (hedef > son and haftalik > 0)
        if dogru_yon:
            kalan_hafta = abs(son - hedef) / abs(haftalik)
            if kalan_hafta < 260:
                varis = datetime.date.today() + datetime.timedelta(weeks=kalan_hafta)
                st.success(f"Bu hızla gidersen hedefine yaklaşık {varis.strftime('%d.%m.%Y')} "
                           "tarihinde ulaşırsın.")
        else:
            st.info("Son tartıların hedefinin ters yönünde ilerliyor. "
                    "Birkaç hafta daha veriye bakmak gerek.")


# ---------------------------------------------------------------- Makro raporu
def _makro_bolumu(df, hedef_kalori, renk):
    st.markdown("#### Makro dağılımın")
    kayitli = df[df["kayit_var"]]
    if kayitli.empty:
        st.caption("Bu dönemde öğün kaydın yok.")
        return

    gercek = {"Protein": kayitli["protein"].mean(),
              "Karbonhidrat": kayitli["karb"].mean(),
              "Yağ": kayitli["yag"].mean()}
    hedefler = {"Protein": hedef_kalori * 0.30 / 4,
                "Karbonhidrat": hedef_kalori * 0.40 / 4,
                "Yağ": hedef_kalori * 0.30 / 9}

    veri = pd.DataFrame(
        [{"makro": a, "tur": "Ortalaman", "gram": gercek[a]} for a in gercek]
        + [{"makro": a, "tur": "Hedefin", "gram": hedefler[a]} for a in hedefler])

    grafik = alt.Chart(veri).mark_bar(cornerRadiusEnd=3).encode(
        y=alt.Y("makro:N", title=None, sort=["Protein", "Karbonhidrat", "Yağ"],
                axis=alt.Axis(labelOverlap=False, labelLimit=140, labelPadding=8)),
        x=alt.X("gram:Q", title="gram (günlük ortalama)", axis=alt.Axis(tickCount=6)),
        yOffset="tur:N",
        color=alt.Color("tur:N", scale=alt.Scale(domain=["Ortalaman", "Hedefin"],
                                                 range=[MAVI, GRI]),
                        legend=alt.Legend(title=None, orient="top")),
        tooltip=[alt.Tooltip("makro:N", title="Makro"), alt.Tooltip("tur:N", title=""),
                 alt.Tooltip("gram:Q", title="gram", format=".0f")],
    ).properties(height=230)
    st.altair_chart(_tema(grafik, renk), use_container_width=True)

    toplam = gercek["Protein"] * 4 + gercek["Karbonhidrat"] * 4 + gercek["Yağ"] * 9
    if toplam > 0:
        st.caption(f"Kalorinin dağılımı: protein %{gercek['Protein'] * 4 / toplam * 100:.0f}, "
                   f"karbonhidrat %{gercek['Karbonhidrat'] * 4 / toplam * 100:.0f}, "
                   f"yağ %{gercek['Yağ'] * 9 / toplam * 100:.0f}")


# ------------------------------------------------------------- Öğün dağılımı
def _ogun_bolumu(gunluk_kayitlar, gunler, renk):
    st.markdown("#### Öğünlere göre dağılım")
    aralik = {str(g) for g in gunler}
    sayac = {o: 0.0 for o in OGUNLER}
    gun_sayisi = len({k.get("Tarih") for k in (gunluk_kayitlar or []) if k.get("Tarih") in aralik})
    for k in gunluk_kayitlar or []:
        if k.get("Tarih") in aralik and k.get("Öğün") in sayac:
            sayac[k["Öğün"]] += float(k.get("Kalori", 0) or 0)

    if gun_sayisi == 0 or sum(sayac.values()) == 0:
        st.caption("Bu dönemde öğün kaydın yok.")
        return

    veri = pd.DataFrame([{"ogun": o, "kcal": sayac[o] / gun_sayisi} for o in OGUNLER])
    grafik = alt.Chart(veri).mark_bar(cornerRadiusEnd=3, color=SARI).encode(
        y=alt.Y("ogun:N", title=None, sort=OGUNLER,
                axis=alt.Axis(labelOverlap=False, labelLimit=140, labelPadding=8)),
        x=alt.X("kcal:Q", title="günlük ortalama kcal", axis=alt.Axis(tickCount=6)),
        tooltip=[alt.Tooltip("ogun:N", title="Öğün"),
                 alt.Tooltip("kcal:Q", title="Ortalama kcal", format=".0f")],
    ).properties(height=200)
    st.altair_chart(_tema(grafik, renk), use_container_width=True)


# -------------------------------------------------------- Egzersiz ve aktivite
def _egzersiz_bolumu(df, aktivite_loglari, gunler, renk):
    st.markdown("#### Egzersiz ve aktivite")
    hareketli = df[df["adim"] > 0]
    antrenmanli = df[df["egzersiz"] > 0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Günlük ortalama adım",
              f"{round(hareketli['adim'].mean()) if not hareketli.empty else 0}")
    c2.metric("Antrenman yaptığın gün", f"{len(antrenmanli)} / {len(df)}")
    c3.metric("Günlük ortalama su", f"{df['su'].mean():.2f} L")

    if not hareketli.empty:
        cubuk = alt.Chart(df).mark_bar(
            color=YESIL, cornerRadiusTopLeft=2, cornerRadiusTopRight=2,
            size=max(5, int(230 / max(len(df), 1)))).encode(
            x=_tarih_ekseni(len(df)),
            y=alt.Y("adim:Q", title="adım"),
            tooltip=[alt.Tooltip("tarih:T", title="Tarih", format="%d %B"),
                     alt.Tooltip("adim:Q", title="Adım")])
        hedef_cizgi = alt.Chart(pd.DataFrame({"h": [10000]})).mark_rule(
            color=MAVI, strokeDash=[6, 4], size=2).encode(y="h:Q")
        st.altair_chart(_tema((cubuk + hedef_cizgi).properties(height=180), renk),
                        use_container_width=True)
        st.caption("Mavi kesikli çizgi günde 10.000 adım hedefi.")

    kayitlar = []
    for g in gunler:
        for a in ((aktivite_loglari or {}).get(str(g), {}) or {}).get("antrenmanlar", []) or []:
            kayitlar.append((g, a))

    if kayitlar:
        with st.expander(f"Antrenman günlüğün ({len(kayitlar)} kayıt)"):
            for g, a in reversed(kayitlar):
                hareketler = a.get("hareketler", [])
                toplam_set = sum(int(h.get("sets_done", 0) or 0) for h in hareketler)
                st.markdown(f"**{g.strftime('%d.%m.%Y')}** - {a.get('gun', 'Antrenman')}, "
                            f"{toplam_set} set")
                for h in hareketler:
                    tekrar = f" ({h['reps']})" if h.get("reps") else ""
                    st.caption(f"{h.get('name', h.get('id', ''))} - "
                               f"{h.get('sets_done', 0)} set{tekrar}")
    else:
        st.caption("Bu dönemde kaydedilmiş antrenman yok. Antrenman Koçu sekmesinden plan "
                   "yapıp tamamladığın setleri girebilirsin.")


# -------------------------------------------------------------------- Giriş
def gelisim_sayfasi(gunluk_kayitlar, aktivite_loglari, profil, hedef_kalori, bmr, tema):
    """Gelişim sekmesini çizer."""
    renk = (tema or {}).get("text_color", "#ffffff")

    secim = st.radio("Dönem", list(DONEMLER), horizontal=True,
                     key="gelisim_donem", label_visibility="collapsed")
    gun_sayisi = DONEMLER[secim]
    gunler = _gun_listesi(gun_sayisi)
    df = _gunluk_tablo(gunluk_kayitlar, aktivite_loglari, gunler, bmr)

    _kalori_bolumu(df, hedef_kalori, gun_sayisi, renk)
    st.divider()
    _kilo_bolumu(profil or {}, gun_sayisi, renk)
    st.divider()
    _makro_bolumu(df, hedef_kalori, renk)
    st.divider()
    _ogun_bolumu(gunluk_kayitlar, gunler, renk)
    st.divider()
    _egzersiz_bolumu(df, aktivite_loglari, gunler, renk)

    st.divider()
    disa = df.drop(columns=["kayit_var", "kalem"]).rename(columns={
        "tarih": "Tarih", "alinan": "Alınan kcal", "protein": "Protein (g)",
        "karb": "Karbonhidrat (g)", "yag": "Yağ (g)", "adim": "Adım",
        "su": "Su (L)", "egzersiz": "Egzersiz kcal", "harcanan": "Harcanan kcal"})
    st.download_button(
        f"Son {gun_sayisi} günü CSV olarak indir",
        disa.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"nova_{gun_sayisi}gun_{datetime.date.today()}.csv",
        mime="text/csv", use_container_width=True)
    st.caption("Bu dosyayı diyetisyenine gönderebilirsin.")
