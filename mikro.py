"""
mikro.py - Mikro besinler ve günlük referans değerler

Kaynak: Avrupa Birliği 1169/2011 sayılı tüzüğün XIII. ekindeki besin referans
değerleri (NRV). Bunlar paket etiketlerinde "günlük referans alımın yüzde kaçı"
hesabında kullanılan resmi sayılardır. Lif için AB'nin bir NRV'si yok; EFSA'nın
yeterli alım değeri olan 25 gram kullanılıyor.

ÖNEMLİ: Nova mikro besin değeri uydurmaz. Bir yemeğin değeri yalnızca gerçek
bir kaynaktan geliyorsa gösterilir:
  - Open Food Facts'ten gelen paketli ürünler
  - Etiket fotoğrafından okunan değerler
Kendi yemek veritabanımızdaki ev yemeklerinde bu veriler yok; orada "veri yok"
yazar. Tahmini bir sayı göstermek, yanlış sayı göstermekten iyi değildir.
"""

from diller import t

# ad -> (kayıttaki alan adı, birim, günlük referans, sınır mı)
# "sınır mı" True ise az olması iyidir (tuz, şeker, doymuş yağ)
BESINLER = [
    ("Lif",          "Lif (g)",          "g",  25.0,  False),
    ("Şeker",        "Şeker (g)",        "g",  90.0,  True),
    ("Doymuş yağ",   "Doymuş yağ (g)",   "g",  20.0,  True),
    ("Tuz",          "Tuz (g)",          "g",   6.0,  True),
    ("Demir",        "Demir (mg)",       "mg", 14.0,  False),
    ("Kalsiyum",     "Kalsiyum (mg)",    "mg", 800.0, False),
    ("Magnezyum",    "Magnezyum (mg)",   "mg", 375.0, False),
    ("Çinko",        "Çinko (mg)",       "mg", 10.0,  False),
    ("Potasyum",     "Potasyum (mg)",    "mg", 2000.0, False),
    ("C vitamini",   "C vitamini (mg)",  "mg", 80.0,  False),
    ("D vitamini",   "D vitamini (µg)",  "µg",  5.0,  False),
    ("B12 vitamini", "B12 vitamini (µg)", "µg", 2.5,  False),
]

ALANLAR = [b[1] for b in BESINLER]


def topla(kayitlar):
    """Verilen öğün kayıtlarındaki mikro besinleri toplar.

    Dönen sözlükte yalnızca en az bir kayıtta gerçekten veri bulunan besinler
    olur. Hiç veri yoksa o besin sözlükte hiç görünmez; sıfır yazmak yanıltıcı
    olurdu, çünkü "yok" ile "sıfır" aynı şey değil.
    """
    toplam = {}
    for kayit in kayitlar or []:
        for _ad, alan, _birim, _ref, _sinir in BESINLER:
            deger = kayit.get(alan)
            if deger is None:
                continue
            try:
                toplam[alan] = toplam.get(alan, 0.0) + float(deger)
            except (TypeError, ValueError):
                continue
    return toplam


def kapsama(kayitlar):
    """Kaç kayıtta mikro besin verisi var, kaçında yok. (var, toplam) döner."""
    kayitlar = kayitlar or []
    var = sum(1 for k in kayitlar if any(k.get(a) is not None for a in ALANLAR))
    return var, len(kayitlar)


def _renk(yuzde, sinir_mi):
    """Yüzdeye göre çubuk rengi. Emoji yerine renk kullanılıyor."""
    if sinir_mi:
        if yuzde > 100:
            return "#ff3b30"      # kırmızı: sınırı aştı
        if yuzde > 75:
            return "#ffcc00"      # sarı: sınıra yaklaştı
        return "#34c759"          # yeşil: rahat
    if yuzde >= 100:
        return "#34c759"          # yeşil: ihtiyacı karşıladı
    if yuzde >= 50:
        return "#ffcc00"
    return "#ff9500"              # turuncu: epey geride


def cubuklar_html(toplam, metin_rengi="#ffffff"):
    """Mikro besin çubuklarını HTML olarak üretir. Veri yoksa boş döner."""
    if not toplam:
        return ""
    satirlar = []
    for ad, alan, birim, referans, sinir_mi in BESINLER:
        if alan not in toplam:
            continue
        deger = toplam[alan]
        yuzde = (deger / referans) * 100 if referans else 0
        genislik = min(yuzde, 100)
        renk = _renk(yuzde, sinir_mi)
        gosterim = f"{deger:.1f}".rstrip("0").rstrip(".")
        satirlar.append(f"""
        <div style="margin-bottom: 12px;">
          <div style="display:flex; justify-content:space-between; font-size:0.9rem;
                      margin-bottom:4px; color:{metin_rengi};">
            <span>{t(ad)}</span>
            <span>{gosterim} {birim} · %{round(yuzde)}</span>
          </div>
          <div style="width:100%; background-color:rgba(255,255,255,0.15);
                      border-radius:4px; height:6px;">
            <div style="width:{genislik}%; background-color:{renk}; height:100%;
                        border-radius:4px;"></div>
          </div>
        </div>""")
    return "".join(satirlar)


def eksikler(toplam, esik=50):
    """Günlük referansın belirtilen yüzdesinin altında kalan besinlerin adları."""
    cikti = []
    for ad, alan, _birim, referans, sinir_mi in BESINLER:
        if sinir_mi or alan not in toplam or not referans:
            continue
        if (toplam[alan] / referans) * 100 < esik:
            cikti.append(ad)
    return cikti


def asilanlar(toplam):
    """Sınırı aşılan besinlerin adları (tuz, şeker, doymuş yağ)."""
    cikti = []
    for ad, alan, _birim, referans, sinir_mi in BESINLER:
        if not sinir_mi or alan not in toplam or not referans:
            continue
        if toplam[alan] > referans:
            cikti.append(ad)
    return cikti
