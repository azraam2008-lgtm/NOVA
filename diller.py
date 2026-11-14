"""
diller.py - Nova'nın dil altyapısı

Kullanım:
    from diller import t, dil_ayarla, aktif_dil, DIL_LISTESI
    st.button(t("Giriş Yap"))

Anahtar olarak Türkçe metnin kendisi kullanılıyor. Böylece bir metin
çevrilmemişse boş kutu değil, Türkçesi görünür. Yeni dil eklemek için
CEVIRILER'e yeni bir sözlük eklemek yeterli.

Diller: Türkçe, English, Deutsch, Español, Français, العربية
Arapça sağdan sola yazılır; yon() bunu söyler, app.py CSS'i ona göre kurar.
"""

import re

import streamlit as st

DIL_LISTESI = {
    "tr": "Türkçe",
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
    "fr": "Français",
    "ar": "العربية",
}

VARSAYILAN = "tr"

# Sağdan sola yazılan diller
SAGDAN_SOLA = {"ar"}


def aktif_dil():
    d = st.session_state.get("dil")
    if d in DIL_LISTESI:
        return d
    try:
        d = (st.session_state.get("profil") or {}).get("dil")
    except Exception:  # noqa: BLE001
        d = None
    return d if d in DIL_LISTESI else VARSAYILAN


def dil_ayarla(kod):
    if kod in DIL_LISTESI:
        st.session_state["dil"] = kod


def yon(dil=None):
    return "rtl" if (dil or aktif_dil()) in SAGDAN_SOLA else "ltr"


def h(parca, dil=None):
    """HTML parçasının içindeki Türkçe ifadeleri çevirir.

    st.markdown ile yazılan başlıklar, bilgi kutuları ve tablolar HTML olduğu
    için tek tek t() ile sarılamıyor. Bu işlev hazır metnin içinde geçen bilinen
    ifadeleri bulup çevirir; sayılar, etiketler ve biçimlendirme olduğu gibi kalır.
    Uzun ifadeler önce denenir ki kısa bir parça uzununun içinden kesmesin.
    """
    d = dil or aktif_dil()
    if d == "tr" or not parca:
        return parca
    sozluk = CEVIRILER.get(d)
    if not sozluk:
        return parca
    # Stil bloklarına asla dokunulmaz; orada bir kelime değiştirmek sayfayı bozar
    if "<style>" in parca or "@import" in parca:
        return parca
    for anahtar, kalip in _KALIPLAR.get(d, ()):
        if anahtar in parca:
            parca = kalip.sub(lambda _m, _k=anahtar: sozluk[_k], parca)
    return parca


def t(metin, dil=None):
    """Metni aktif dile çevirir. Çeviri yoksa Türkçesini döndürür."""
    d = dil or aktif_dil()
    if d == "tr":
        return metin
    sozluk = CEVIRILER.get(d, {})
    if metin in sozluk:
        return sozluk[metin]
    # Koddaki metinlerin bir kısmında sonda fazladan boşluk var; onlar da bulunsun
    kirpik = metin.strip()
    if kirpik in sozluk:
        return sozluk[kirpik]
    # Satır sonlarından kaynaklanan çoklu boşluklar
    sade = " ".join(metin.split())
    return sozluk.get(sade, metin)


# --------------------------------------------------------------------------
# ÇEVİRİLER
# --------------------------------------------------------------------------
_EN = {
    # Giriş ve kayıt
    "ZARAFET VE DENGE": "ELEGANCE AND BALANCE",
    "Kullanıcı Adı": "Username",
    "Şifre": "Password",
    "Beni hatırla": "Remember me",
    "Giriş Yap": "Sign in",
    "Kayıt Ol": "Sign up",
    "Hatalı kullanıcı adı veya şifre.": "Incorrect username or password.",
    "Yeni Kullanıcı Adı": "Choose a username",
    "E-posta (şifreni unutursan gerekli)": "Email (needed if you forget your password)",
    "Şifre (en az 8 karakter, bir büyük harf ve bir rakam)":
        "Password (at least 8 characters, one capital letter and one digit)",
    "Hesap Oluştur": "Create account",
    "Kullanıcı adı boş olamaz.": "Username cannot be empty.",
    "Bu kullanıcı adı zaten alınmış.": "That username is already taken.",
    "E-posta adresi geçerli görünmüyor.": "That email address does not look valid.",
    "Google ile devam et": "Continue with Google",
    "ya da": "or",
    "Bu tarayıcıda 30 gün açık kalırsın, sayfayı yenileyince çıkış yapmazsın. "
    "Ortak bir bilgisayardaysan işaretleme.":
        "You stay signed in on this browser for 30 days and refreshing the page will not log you out. "
        "Leave it unchecked on a shared computer.",

    # Kurulum
    "Hangi dili kullanmak istersin?": "Which language would you like to use?",
    "Dil": "Language",
    "Nova'yı bu dilde kullanacaksın. Daha sonra ayarlardan değiştirebilirsin.":
        "You will use Nova in this language. You can change it later in settings.",
    "Devam": "Continue",
    "Başla": "Start",
    "İleri": "Next",
    "Geri": "Back",
    "Tanıştığımıza memnun oldum,": "Lovely to meet you,",
    "Nova'ya Hoş Geldin!": "Welcome to Nova!",
    "Hedeflerine ulaşmanda sana yardımcı olmak için buradayız.":
        "We are here to help you reach your goals.",
    "Başlamak için birkaç kısa sorumuz olacak.":
        "We have a few short questions to get started.",
    "Cevapların, hedeflerini anlamamıza ve uygulamayı senin için kişiselleştirmemize yardımcı olacak.":
        "Your answers help us understand your goals and tailor Nova to you.",
    "Merhaba! Adın nedir?": "Hello! What is your name?",
    "Adını Gir": "Enter your name",
    "Lütfen adını gir.": "Please enter your name.",
    "Nova uygulamasını sana özel hale getirmek ve sana hitap edebilmek için adını kullanacağız.":
        "We use your name to personalise Nova and to address you properly.",
    "Nova'yı Hangi Amaçla Kullanmak İstiyorsun": "What would you like to use Nova for",
    "Hedeflerin (Birden fazla seçebilirsin)": "Your goals (you can pick more than one)",
    "Kilo vermek istiyorum": "I want to lose weight",
    "Kilomu korumak istiyorum": "I want to maintain my weight",
    "Kilo almak istiyorum": "I want to gain weight",
    "Kas kazanmak istiyorum": "I want to build muscle",
    "Sağlıklı beslenmek istiyorum": "I want to eat healthily",
    "Cinsiyetin nedir?": "What is your sex?",
    "Seçimini yap:": "Make your choice:",
    "Kadın": "Female",
    "Erkek": "Male",
    "Cinsiyetin, vücudunun günlük enerji ihtiyacını hesaplamamızı doğrudan etkiler.":
        "Your sex directly affects how we calculate your daily energy needs.",
    "Doğum yılın ne?": "What year were you born?",
    "Yıl": "Year",
    "yaşındasın.": "years old.",
    "Yaşın, vücudunun her gün ne kadar enerjiye (BMR) ihtiyaç duyduğunu etkiler.":
        "Your age affects how much energy (BMR) your body needs each day.",
    "18 yaşından küçüksün. Büyüme çağında kalori kısıtlamak gelişimi etkileyebilir.":
        "You are under 18. Restricting calories while still growing can affect your development.",
    "Boyun kaç?": "How tall are you?",
    "Boy (cm)": "Height (cm)",
    "Boyun, vücudunun her gün ne kadar enerji harcadığını etkiler.":
        "Your height affects how much energy your body uses each day.",
    "Şu andaki kilon ne?": "What do you weigh right now?",
    "Kilo (kg)": "Weight (kg)",
    "Bu bilgi, bulunduğun noktaya göre kalori hedefini hesaplamamıza yardımcı olur. "
    "Şu anki kilonu tam bilmiyorsan en iyi tahminini gir, daha sonra uygulamada "
    "Pazar günleri güncelleyebilirsin.":
        "This helps us calculate your calorie target from where you are now. If you are not sure, "
        "enter your best guess; you can update it on Sundays inside the app.",
    "Hedef kilon nedir?": "What is your goal weight?",
    "Hedef Kilo (kg)": "Goal weight (kg)",
    "Hedefe Ulaşma Süresi (Ay)": "Time to reach it (months)",
    "Günlük hareket düzeyin": "Your daily activity level",
    "Hareket düzeyin, günde ne kadar enerji harcadığını belirleyen en önemli etken. "
    "Adım ve egzersiz kayıtların bunun üzerine eklenir.":
        "Your activity level is the biggest factor in how much energy you burn daily. "
        "Your steps and workouts are added on top of it.",
    "Nova Deneyimin İçin Bir Tema Seç": "Pick a theme for Nova",
    "Kalori Hedefimi Hesapla": "Calculate my calorie target",
    "Bu tempo hızlı. Güvenli aralık genelde haftada 0,5-1 kilodur; süreyi uzatmanı öneririm.":
        "That pace is fast. A safe range is usually 0.5-1 kg per week; consider allowing more time.",
    "Paylaştığın için teşekkürler": "Thank you for sharing",
    "Bize söylediklerin, seni nasıl destekleyeceğimizi şekillendirmemize yardımcı olacak.":
        "What you told us shapes how we will support you.",
    "İşte Kişisel Kalori Hedefin": "Here is your personal calorie target",
    "Amacın:": "Your goal:",
    "Dinlenik Metabolizman (BMR):": "Resting metabolism (BMR):",
    "Tahmini Günlük Harcaman:": "Estimated daily burn:",
    "Günlük Hedefin": "Your daily target",
    "Nova Kalori Hedefin, amacına ulaşmak için her gün kaç kalori tüketmen gerektiğini gösterir. "
    "Her gün bu hedefe yakın miktarda tüketirsen başarıya ulaşırsın.":
        "Your Nova calorie target shows how much to eat each day to reach your goal. "
        "Stay close to it daily and you will get there.",
    "Harika, Uygulamaya Başla!": "Great, let's begin",
    "Nova bir sağlık uygulaması değildir ve tıbbi tavsiye vermez.":
        "Nova is not a medical app and does not give medical advice.",
    "Hesaplamalar genel formüllere dayanan tahminlerdir.":
        "The calculations are estimates based on general formulas.",

    # Ana ekran
    "Geçmiş Tarih İnceleme": "View another date",
    "Ayarlar": "Settings",
    "Kalori ve Denge Tablosu": "Calories and balance",
    "Günlük Hedef Kalori Bütçen": "Your daily calorie budget",
    "Bugüne Kadar Yediklerin": "Eaten so far",
    "Hareket ve Egzersizle Kazandıkların": "Earned through activity",
    "Geriye Kalan Yeme Hakkın": "Remaining",
    "Günlük Makro İhtiyaçları": "Daily macro targets",
    "Protein": "Protein",
    "Karbonhidrat": "Carbs",
    "Yağ": "Fat",
    "Yemek Ekle": "Add food",
    "Bugünkü Öğünlerin": "Today's meals",
    "Bugünkü Egzersizin": "Today's exercise",
    "Günlük Aktivite ve Su Halkaları": "Activity and water rings",
    "Hesap ve Verilerin": "Account and data",
    "Gelişimin": "Your progress",
    "Hangi öğüne eklenecek?": "Which meal?",
    "Kahvaltı": "Breakfast",
    "Öğle Yemeği": "Lunch",
    "Akşam Yemeği": "Dinner",
    "Ara Öğün": "Snack",
    "Bugün kaydedilmiş antrenman yok. Antrenman Koçu sekmesinden plan yapıp "
    "tamamladığın setleri girebilirsin.":
        "No workout logged today. Plan one in the Training Coach tab and enter the sets you finish.",
    "Başka bir egzersiz yaptıysan yaktığın tahmini kalori":
        "If you did another activity, the calories you estimate you burned",
    "Egzersiz kalorisini kaydet": "Save exercise calories",
    "Bugünkü toplam adımın": "Your total steps today",
    "Adımı Kaydet": "Save steps",
    "Eklenecek su (litre)": "Water to add (litres)",
    "Suyu Ekle": "Add water",
    "Sıfırla": "Reset",
    "Adım": "Steps",
    "Su": "Water",
    "Pazar Günü Tartı ve Durum Güncellemesi!": "Sunday weigh-in",
    "Harika bir hafta geçirdik! Haftayı kapatmadan önce bugün sabah tartıldığın güncel kilonu "
    "girerek hedeflerini ve kalori planını yeni kilosuna göre güncelleyebilirsin.":
        "Good week. Before it closes, enter this morning's weight and your targets and calorie "
        "plan will be recalculated.",
    "Bugünkü Güncel Kilon (kg)": "Today's weight (kg)",
    "Kilomu Güncelle ve Hedeflerimi Yenile": "Update my weight and refresh my targets",
    "Harika! Kilon güncellendi ve haftalık kalori/makro planın yeni hedeflerine göre "
    "yeniden hesaplandı!":
        "Done. Your weight is updated and your calorie and macro plan has been recalculated.",

    # Sekmeler
    "Günlük Özet": "Daily summary",
    "Gelişim": "Progress",
    "Öğün Tarama": "Scan a meal",
    "Antrenman Koçu": "Training coach",
    "Asistan": "Assistant",
    "Hangi Öğün İçin Tarama Yapıyorsun?": "Which meal are you scanning?",

    # Oturum
    "Oturum": "Session",
    "Çıkış yap": "Sign out",
    "Çıkış yaparsan bu tarayıcıdaki kayıtlı oturum da silinir.":
        "Signing out also clears the saved session on this browser.",

    # Ayarlar paneli
    "Bilgilerin": "Your details",
    "Görünüm": "Appearance",
    "Hedefin": "Your goal",
    "Kaydet": "Save",
    "Ayarlardan çık": "Close settings",
    "Değişikliklerin kaydedildi.": "Your changes have been saved.",
    "Kurulum sorularını baştan cevapla": "Answer the setup questions again",
    "Adın": "Your name",
}

_DE = {
    "ZARAFET VE DENGE": "ELEGANZ UND BALANCE",
    "Kullanıcı Adı": "Benutzername",
    "Şifre": "Passwort",
    "Beni hatırla": "Angemeldet bleiben",
    "Giriş Yap": "Anmelden",
    "Kayıt Ol": "Registrieren",
    "Hatalı kullanıcı adı veya şifre.": "Benutzername oder Passwort ist falsch.",
    "Yeni Kullanıcı Adı": "Benutzernamen wählen",
    "E-posta (şifreni unutursan gerekli)": "E-Mail (nötig, falls du dein Passwort vergisst)",
    "Şifre (en az 8 karakter, bir büyük harf ve bir rakam)":
        "Passwort (mindestens 8 Zeichen, ein Großbuchstabe und eine Ziffer)",
    "Hesap Oluştur": "Konto erstellen",
    "Kullanıcı adı boş olamaz.": "Der Benutzername darf nicht leer sein.",
    "Bu kullanıcı adı zaten alınmış.": "Dieser Benutzername ist bereits vergeben.",
    "E-posta adresi geçerli görünmüyor.": "Diese E-Mail-Adresse sieht nicht gültig aus.",
    "Google ile devam et": "Mit Google fortfahren",
    "ya da": "oder",
    "Hangi dili kullanmak istersin?": "Welche Sprache möchtest du verwenden?",
    "Dil": "Sprache",
    "Nova'yı bu dilde kullanacaksın. Daha sonra ayarlardan değiştirebilirsin.":
        "Du wirst Nova in dieser Sprache verwenden. Du kannst sie später in den Einstellungen ändern.",
    "Devam": "Weiter",
    "Başla": "Los geht's",
    "İleri": "Weiter",
    "Geri": "Zurück",
    "Tanıştığımıza memnun oldum,": "Schön, dich kennenzulernen,",
    "Nova'ya Hoş Geldin!": "Willkommen bei Nova!",
    "Hedeflerine ulaşmanda sana yardımcı olmak için buradayız.":
        "Wir sind hier, um dir beim Erreichen deiner Ziele zu helfen.",
    "Başlamak için birkaç kısa sorumuz olacak.":
        "Wir haben ein paar kurze Fragen zum Start.",
    "Merhaba! Adın nedir?": "Hallo! Wie heißt du?",
    "Adını Gir": "Gib deinen Namen ein",
    "Lütfen adını gir.": "Bitte gib deinen Namen ein.",
    "Hedeflerin (Birden fazla seçebilirsin)": "Deine Ziele (Mehrfachauswahl möglich)",
    "Kilo vermek istiyorum": "Ich möchte abnehmen",
    "Kilomu korumak istiyorum": "Ich möchte mein Gewicht halten",
    "Kilo almak istiyorum": "Ich möchte zunehmen",
    "Kas kazanmak istiyorum": "Ich möchte Muskeln aufbauen",
    "Sağlıklı beslenmek istiyorum": "Ich möchte mich gesund ernähren",
    "Cinsiyetin nedir?": "Was ist dein Geschlecht?",
    "Seçimini yap:": "Triff deine Wahl:",
    "Kadın": "Weiblich",
    "Erkek": "Männlich",
    "Doğum yılın ne?": "In welchem Jahr bist du geboren?",
    "Yıl": "Jahr",
    "yaşındasın.": "Jahre alt.",
    "18 yaşından küçüksün. Büyüme çağında kalori kısıtlamak gelişimi etkileyebilir.":
        "Du bist unter 18. Kalorien zu beschränken kann die Entwicklung im Wachstum beeinträchtigen.",
    "Boyun kaç?": "Wie groß bist du?",
    "Boy (cm)": "Größe (cm)",
    "Şu andaki kilon ne?": "Was wiegst du derzeit?",
    "Kilo (kg)": "Gewicht (kg)",
    "Hedef kilon nedir?": "Was ist dein Zielgewicht?",
    "Hedef Kilo (kg)": "Zielgewicht (kg)",
    "Hedefe Ulaşma Süresi (Ay)": "Zeitraum bis zum Ziel (Monate)",
    "Günlük hareket düzeyin": "Dein tägliches Aktivitätsniveau",
    "Nova Deneyimin İçin Bir Tema Seç": "Wähle ein Design für Nova",
    "Kalori Hedefimi Hesapla": "Mein Kalorienziel berechnen",
    "Bu tempo hızlı. Güvenli aralık genelde haftada 0,5-1 kilodur; süreyi uzatmanı öneririm.":
        "Das Tempo ist hoch. Sicher sind meist 0,5-1 kg pro Woche; nimm dir lieber mehr Zeit.",
    "Paylaştığın için teşekkürler": "Danke für deine Angaben",
    "İşte Kişisel Kalori Hedefin": "Hier ist dein persönliches Kalorienziel",
    "Amacın:": "Dein Ziel:",
    "Dinlenik Metabolizman (BMR):": "Grundumsatz (BMR):",
    "Tahmini Günlük Harcaman:": "Geschätzter Tagesverbrauch:",
    "Günlük Hedefin": "Dein Tagesziel",
    "Harika, Uygulamaya Başla!": "Super, los geht's",
    "Nova bir sağlık uygulaması değildir ve tıbbi tavsiye vermez.":
        "Nova ist keine medizinische App und gibt keine medizinischen Ratschläge.",
    "Hesaplamalar genel formüllere dayanan tahminlerdir.":
        "Die Berechnungen sind Schätzungen auf Basis allgemeiner Formeln.",
    "Geçmiş Tarih İnceleme": "Anderes Datum ansehen",
    "Ayarlar": "Einstellungen",
    "Kalori ve Denge Tablosu": "Kalorien und Bilanz",
    "Günlük Hedef Kalori Bütçen": "Dein tägliches Kalorienbudget",
    "Bugüne Kadar Yediklerin": "Bisher gegessen",
    "Hareket ve Egzersizle Kazandıkların": "Durch Bewegung verdient",
    "Geriye Kalan Yeme Hakkın": "Verbleibend",
    "Günlük Makro İhtiyaçları": "Tägliche Makroziele",
    "Protein": "Eiweiß",
    "Karbonhidrat": "Kohlenhydrate",
    "Yağ": "Fett",
    "Yemek Ekle": "Essen hinzufügen",
    "Bugünkü Öğünlerin": "Deine Mahlzeiten heute",
    "Bugünkü Egzersizin": "Dein Training heute",
    "Günlük Aktivite ve Su Halkaları": "Aktivitäts- und Wasserringe",
    "Hesap ve Verilerin": "Konto und Daten",
    "Gelişimin": "Dein Fortschritt",
    "Hangi öğüne eklenecek?": "Zu welcher Mahlzeit?",
    "Kahvaltı": "Frühstück",
    "Öğle Yemeği": "Mittagessen",
    "Akşam Yemeği": "Abendessen",
    "Ara Öğün": "Snack",
    "Egzersiz kalorisini kaydet": "Trainingskalorien speichern",
    "Bugünkü toplam adımın": "Deine Schritte heute",
    "Adımı Kaydet": "Schritte speichern",
    "Eklenecek su (litre)": "Wasser hinzufügen (Liter)",
    "Suyu Ekle": "Wasser hinzufügen",
    "Sıfırla": "Zurücksetzen",
    "Adım": "Schritte",
    "Su": "Wasser",
    "Bugünkü Güncel Kilon (kg)": "Heutiges Gewicht (kg)",
    "Günlük Özet": "Tagesübersicht",
    "Gelişim": "Fortschritt",
    "Öğün Tarama": "Mahlzeit scannen",
    "Antrenman Koçu": "Trainingscoach",
    "Asistan": "Assistent",
    "Oturum": "Sitzung",
    "Çıkış yap": "Abmelden",
    "Bilgilerin": "Deine Angaben",
    "Görünüm": "Darstellung",
    "Hedefin": "Dein Ziel",
    "Kaydet": "Speichern",
    "Ayarlardan çık": "Einstellungen schließen",
    "Değişikliklerin kaydedildi.": "Deine Änderungen wurden gespeichert.",
    "Kurulum sorularını baştan cevapla": "Einrichtungsfragen erneut beantworten",
    "Adın": "Dein Name",
}

_ES = {
    "ZARAFET VE DENGE": "ELEGANCIA Y EQUILIBRIO",
    "Kullanıcı Adı": "Nombre de usuario",
    "Şifre": "Contraseña",
    "Beni hatırla": "Recordarme",
    "Giriş Yap": "Iniciar sesión",
    "Kayıt Ol": "Crear cuenta",
    "Hatalı kullanıcı adı veya şifre.": "Usuario o contraseña incorrectos.",
    "Yeni Kullanıcı Adı": "Elige un nombre de usuario",
    "E-posta (şifreni unutursan gerekli)": "Correo (necesario si olvidas la contraseña)",
    "Şifre (en az 8 karakter, bir büyük harf ve bir rakam)":
        "Contraseña (mínimo 8 caracteres, una mayúscula y un número)",
    "Hesap Oluştur": "Crear cuenta",
    "Kullanıcı adı boş olamaz.": "El nombre de usuario no puede estar vacío.",
    "Bu kullanıcı adı zaten alınmış.": "Ese nombre de usuario ya está en uso.",
    "E-posta adresi geçerli görünmüyor.": "Ese correo no parece válido.",
    "Google ile devam et": "Continuar con Google",
    "ya da": "o",
    "Hangi dili kullanmak istersin?": "¿Qué idioma quieres usar?",
    "Dil": "Idioma",
    "Nova'yı bu dilde kullanacaksın. Daha sonra ayarlardan değiştirebilirsin.":
        "Usarás Nova en este idioma. Puedes cambiarlo después en ajustes.",
    "Devam": "Continuar",
    "Başla": "Empezar",
    "İleri": "Siguiente",
    "Geri": "Atrás",
    "Tanıştığımıza memnun oldum,": "Encantado de conocerte,",
    "Nova'ya Hoş Geldin!": "¡Bienvenido a Nova!",
    "Hedeflerine ulaşmanda sana yardımcı olmak için buradayız.":
        "Estamos aquí para ayudarte a alcanzar tus objetivos.",
    "Başlamak için birkaç kısa sorumuz olacak.":
        "Tenemos unas preguntas breves para empezar.",
    "Merhaba! Adın nedir?": "¡Hola! ¿Cómo te llamas?",
    "Adını Gir": "Escribe tu nombre",
    "Lütfen adını gir.": "Por favor, escribe tu nombre.",
    "Hedeflerin (Birden fazla seçebilirsin)": "Tus objetivos (puedes elegir varios)",
    "Kilo vermek istiyorum": "Quiero perder peso",
    "Kilomu korumak istiyorum": "Quiero mantener mi peso",
    "Kilo almak istiyorum": "Quiero ganar peso",
    "Kas kazanmak istiyorum": "Quiero ganar músculo",
    "Sağlıklı beslenmek istiyorum": "Quiero comer sano",
    "Cinsiyetin nedir?": "¿Cuál es tu sexo?",
    "Seçimini yap:": "Elige:",
    "Kadın": "Mujer",
    "Erkek": "Hombre",
    "Doğum yılın ne?": "¿En qué año naciste?",
    "Yıl": "Año",
    "yaşındasın.": "años.",
    "18 yaşından küçüksün. Büyüme çağında kalori kısıtlamak gelişimi etkileyebilir.":
        "Tienes menos de 18 años. Restringir calorías durante el crecimiento puede afectar tu desarrollo.",
    "Boyun kaç?": "¿Cuánto mides?",
    "Boy (cm)": "Altura (cm)",
    "Şu andaki kilon ne?": "¿Cuánto pesas ahora?",
    "Kilo (kg)": "Peso (kg)",
    "Hedef kilon nedir?": "¿Cuál es tu peso objetivo?",
    "Hedef Kilo (kg)": "Peso objetivo (kg)",
    "Hedefe Ulaşma Süresi (Ay)": "Tiempo para lograrlo (meses)",
    "Günlük hareket düzeyin": "Tu nivel de actividad diaria",
    "Nova Deneyimin İçin Bir Tema Seç": "Elige un tema para Nova",
    "Kalori Hedefimi Hesapla": "Calcular mi objetivo de calorías",
    "Bu tempo hızlı. Güvenli aralık genelde haftada 0,5-1 kilodur; süreyi uzatmanı öneririm.":
        "Ese ritmo es rápido. Lo seguro suele ser 0,5-1 kg por semana; mejor date más tiempo.",
    "Paylaştığın için teşekkürler": "Gracias por compartirlo",
    "İşte Kişisel Kalori Hedefin": "Este es tu objetivo personal de calorías",
    "Amacın:": "Tu objetivo:",
    "Dinlenik Metabolizman (BMR):": "Metabolismo basal (BMR):",
    "Tahmini Günlük Harcaman:": "Gasto diario estimado:",
    "Günlük Hedefin": "Tu objetivo diario",
    "Harika, Uygulamaya Başla!": "Genial, empecemos",
    "Nova bir sağlık uygulaması değildir ve tıbbi tavsiye vermez.":
        "Nova no es una app médica y no da consejos médicos.",
    "Hesaplamalar genel formüllere dayanan tahminlerdir.":
        "Los cálculos son estimaciones basadas en fórmulas generales.",
    "Geçmiş Tarih İnceleme": "Ver otra fecha",
    "Ayarlar": "Ajustes",
    "Kalori ve Denge Tablosu": "Calorías y balance",
    "Günlük Hedef Kalori Bütçen": "Tu presupuesto diario de calorías",
    "Bugüne Kadar Yediklerin": "Consumido hasta ahora",
    "Hareket ve Egzersizle Kazandıkların": "Ganado con actividad",
    "Geriye Kalan Yeme Hakkın": "Restante",
    "Günlük Makro İhtiyaçları": "Objetivos diarios de macros",
    "Protein": "Proteína",
    "Karbonhidrat": "Carbohidratos",
    "Yağ": "Grasa",
    "Yemek Ekle": "Añadir comida",
    "Bugünkü Öğünlerin": "Tus comidas de hoy",
    "Bugünkü Egzersizin": "Tu ejercicio de hoy",
    "Günlük Aktivite ve Su Halkaları": "Anillos de actividad y agua",
    "Hesap ve Verilerin": "Cuenta y datos",
    "Gelişimin": "Tu progreso",
    "Hangi öğüne eklenecek?": "¿A qué comida?",
    "Kahvaltı": "Desayuno",
    "Öğle Yemeği": "Almuerzo",
    "Akşam Yemeği": "Cena",
    "Ara Öğün": "Tentempié",
    "Egzersiz kalorisini kaydet": "Guardar calorías del ejercicio",
    "Bugünkü toplam adımın": "Tus pasos de hoy",
    "Adımı Kaydet": "Guardar pasos",
    "Eklenecek su (litre)": "Agua a añadir (litros)",
    "Suyu Ekle": "Añadir agua",
    "Sıfırla": "Reiniciar",
    "Adım": "Pasos",
    "Su": "Agua",
    "Bugünkü Güncel Kilon (kg)": "Tu peso de hoy (kg)",
    "Günlük Özet": "Resumen diario",
    "Gelişim": "Progreso",
    "Öğün Tarama": "Escanear comida",
    "Antrenman Koçu": "Entrenador",
    "Asistan": "Asistente",
    "Oturum": "Sesión",
    "Çıkış yap": "Cerrar sesión",
    "Bilgilerin": "Tus datos",
    "Görünüm": "Apariencia",
    "Hedefin": "Tu objetivo",
    "Kaydet": "Guardar",
    "Ayarlardan çık": "Cerrar ajustes",
    "Değişikliklerin kaydedildi.": "Se han guardado tus cambios.",
    "Kurulum sorularını baştan cevapla": "Responder de nuevo las preguntas iniciales",
    "Adın": "Tu nombre",
}

_FR = {
    "ZARAFET VE DENGE": "ÉLÉGANCE ET ÉQUILIBRE",
    "Kullanıcı Adı": "Nom d'utilisateur",
    "Şifre": "Mot de passe",
    "Beni hatırla": "Se souvenir de moi",
    "Giriş Yap": "Se connecter",
    "Kayıt Ol": "S'inscrire",
    "Hatalı kullanıcı adı veya şifre.": "Nom d'utilisateur ou mot de passe incorrect.",
    "Yeni Kullanıcı Adı": "Choisis un nom d'utilisateur",
    "E-posta (şifreni unutursan gerekli)": "E-mail (nécessaire en cas d'oubli du mot de passe)",
    "Şifre (en az 8 karakter, bir büyük harf ve bir rakam)":
        "Mot de passe (au moins 8 caractères, une majuscule et un chiffre)",
    "Hesap Oluştur": "Créer un compte",
    "Kullanıcı adı boş olamaz.": "Le nom d'utilisateur ne peut pas être vide.",
    "Bu kullanıcı adı zaten alınmış.": "Ce nom d'utilisateur est déjà pris.",
    "E-posta adresi geçerli görünmüyor.": "Cette adresse e-mail ne semble pas valide.",
    "Google ile devam et": "Continuer avec Google",
    "ya da": "ou",
    "Hangi dili kullanmak istersin?": "Quelle langue veux-tu utiliser ?",
    "Dil": "Langue",
    "Nova'yı bu dilde kullanacaksın. Daha sonra ayarlardan değiştirebilirsin.":
        "Tu utiliseras Nova dans cette langue. Tu pourras la changer plus tard dans les réglages.",
    "Devam": "Continuer",
    "Başla": "Commencer",
    "İleri": "Suivant",
    "Geri": "Retour",
    "Tanıştığımıza memnun oldum,": "Ravi de te rencontrer,",
    "Nova'ya Hoş Geldin!": "Bienvenue sur Nova !",
    "Hedeflerine ulaşmanda sana yardımcı olmak için buradayız.":
        "Nous sommes là pour t'aider à atteindre tes objectifs.",
    "Başlamak için birkaç kısa sorumuz olacak.":
        "Quelques questions rapides pour commencer.",
    "Merhaba! Adın nedir?": "Bonjour ! Comment t'appelles-tu ?",
    "Adını Gir": "Saisis ton prénom",
    "Lütfen adını gir.": "Merci de saisir ton prénom.",
    "Hedeflerin (Birden fazla seçebilirsin)": "Tes objectifs (plusieurs choix possibles)",
    "Kilo vermek istiyorum": "Je veux perdre du poids",
    "Kilomu korumak istiyorum": "Je veux stabiliser mon poids",
    "Kilo almak istiyorum": "Je veux prendre du poids",
    "Kas kazanmak istiyorum": "Je veux prendre du muscle",
    "Sağlıklı beslenmek istiyorum": "Je veux manger sainement",
    "Cinsiyetin nedir?": "Quel est ton sexe ?",
    "Seçimini yap:": "Fais ton choix :",
    "Kadın": "Femme",
    "Erkek": "Homme",
    "Doğum yılın ne?": "En quelle année es-tu né ?",
    "Yıl": "Année",
    "yaşındasın.": "ans.",
    "18 yaşından küçüksün. Büyüme çağında kalori kısıtlamak gelişimi etkileyebilir.":
        "Tu as moins de 18 ans. Restreindre les calories pendant la croissance peut nuire au développement.",
    "Boyun kaç?": "Combien mesures-tu ?",
    "Boy (cm)": "Taille (cm)",
    "Şu andaki kilon ne?": "Combien pèses-tu actuellement ?",
    "Kilo (kg)": "Poids (kg)",
    "Hedef kilon nedir?": "Quel est ton poids cible ?",
    "Hedef Kilo (kg)": "Poids cible (kg)",
    "Hedefe Ulaşma Süresi (Ay)": "Délai pour l'atteindre (mois)",
    "Günlük hareket düzeyin": "Ton niveau d'activité quotidien",
    "Nova Deneyimin İçin Bir Tema Seç": "Choisis un thème pour Nova",
    "Kalori Hedefimi Hesapla": "Calculer mon objectif calorique",
    "Bu tempo hızlı. Güvenli aralık genelde haftada 0,5-1 kilodur; süreyi uzatmanı öneririm.":
        "Ce rythme est rapide. On conseille 0,5 à 1 kg par semaine ; prends plus de temps.",
    "Paylaştığın için teşekkürler": "Merci pour ces informations",
    "İşte Kişisel Kalori Hedefin": "Voici ton objectif calorique personnel",
    "Amacın:": "Ton objectif :",
    "Dinlenik Metabolizman (BMR):": "Métabolisme de base (BMR) :",
    "Tahmini Günlük Harcaman:": "Dépense quotidienne estimée :",
    "Günlük Hedefin": "Ton objectif quotidien",
    "Harika, Uygulamaya Başla!": "Parfait, commençons",
    "Nova bir sağlık uygulaması değildir ve tıbbi tavsiye vermez.":
        "Nova n'est pas une application médicale et ne donne pas de conseils médicaux.",
    "Hesaplamalar genel formüllere dayanan tahminlerdir.":
        "Les calculs sont des estimations basées sur des formules générales.",
    "Geçmiş Tarih İnceleme": "Voir une autre date",
    "Ayarlar": "Réglages",
    "Kalori ve Denge Tablosu": "Calories et bilan",
    "Günlük Hedef Kalori Bütçen": "Ton budget calorique quotidien",
    "Bugüne Kadar Yediklerin": "Consommé jusqu'ici",
    "Hareket ve Egzersizle Kazandıkların": "Gagné par l'activité",
    "Geriye Kalan Yeme Hakkın": "Restant",
    "Günlük Makro İhtiyaçları": "Objectifs de macros quotidiens",
    "Protein": "Protéines",
    "Karbonhidrat": "Glucides",
    "Yağ": "Lipides",
    "Yemek Ekle": "Ajouter un aliment",
    "Bugünkü Öğünlerin": "Tes repas d'aujourd'hui",
    "Bugünkü Egzersizin": "Ton activité d'aujourd'hui",
    "Günlük Aktivite ve Su Halkaları": "Anneaux d'activité et d'eau",
    "Hesap ve Verilerin": "Compte et données",
    "Gelişimin": "Ta progression",
    "Hangi öğüne eklenecek?": "À quel repas ?",
    "Kahvaltı": "Petit-déjeuner",
    "Öğle Yemeği": "Déjeuner",
    "Akşam Yemeği": "Dîner",
    "Ara Öğün": "Collation",
    "Egzersiz kalorisini kaydet": "Enregistrer les calories",
    "Bugünkü toplam adımın": "Tes pas aujourd'hui",
    "Adımı Kaydet": "Enregistrer les pas",
    "Eklenecek su (litre)": "Eau à ajouter (litres)",
    "Suyu Ekle": "Ajouter de l'eau",
    "Sıfırla": "Réinitialiser",
    "Adım": "Pas",
    "Su": "Eau",
    "Bugünkü Güncel Kilon (kg)": "Ton poids aujourd'hui (kg)",
    "Günlük Özet": "Résumé du jour",
    "Gelişim": "Progression",
    "Öğün Tarama": "Scanner un repas",
    "Antrenman Koçu": "Coach d'entraînement",
    "Asistan": "Assistant",
    "Oturum": "Session",
    "Çıkış yap": "Se déconnecter",
    "Bilgilerin": "Tes informations",
    "Görünüm": "Apparence",
    "Hedefin": "Ton objectif",
    "Kaydet": "Enregistrer",
    "Ayarlardan çık": "Fermer les réglages",
    "Değişikliklerin kaydedildi.": "Tes modifications ont été enregistrées.",
    "Kurulum sorularını baştan cevapla": "Répondre à nouveau aux questions de configuration",
    "Adın": "Ton prénom",
}

_AR = {
    "ZARAFET VE DENGE": "أناقة وتوازن",
    "Kullanıcı Adı": "اسم المستخدم",
    "Şifre": "كلمة المرور",
    "Beni hatırla": "تذكرني",
    "Giriş Yap": "تسجيل الدخول",
    "Kayıt Ol": "إنشاء حساب",
    "Hatalı kullanıcı adı veya şifre.": "اسم المستخدم أو كلمة المرور غير صحيحة.",
    "Yeni Kullanıcı Adı": "اختر اسم مستخدم",
    "E-posta (şifreni unutursan gerekli)": "البريد الإلكتروني (مطلوب إذا نسيت كلمة المرور)",
    "Şifre (en az 8 karakter, bir büyük harf ve bir rakam)":
        "كلمة المرور (٨ أحرف على الأقل، حرف كبير ورقم)",
    "Hesap Oluştur": "إنشاء حساب",
    "Kullanıcı adı boş olamaz.": "لا يمكن ترك اسم المستخدم فارغًا.",
    "Bu kullanıcı adı zaten alınmış.": "اسم المستخدم هذا مستخدم بالفعل.",
    "E-posta adresi geçerli görünmüyor.": "عنوان البريد الإلكتروني لا يبدو صحيحًا.",
    "Google ile devam et": "المتابعة باستخدام Google",
    "ya da": "أو",
    "Hangi dili kullanmak istersin?": "ما اللغة التي تريد استخدامها؟",
    "Dil": "اللغة",
    "Nova'yı bu dilde kullanacaksın. Daha sonra ayarlardan değiştirebilirsin.":
        "ستستخدم Nova بهذه اللغة. يمكنك تغييرها لاحقًا من الإعدادات.",
    "Devam": "متابعة",
    "Başla": "ابدأ",
    "İleri": "التالي",
    "Geri": "رجوع",
    "Tanıştığımıza memnun oldum,": "سعدنا بلقائك،",
    "Nova'ya Hoş Geldin!": "أهلًا بك في Nova!",
    "Hedeflerine ulaşmanda sana yardımcı olmak için buradayız.":
        "نحن هنا لمساعدتك على تحقيق أهدافك.",
    "Başlamak için birkaç kısa sorumuz olacak.": "لدينا بعض الأسئلة القصيرة للبدء.",
    "Merhaba! Adın nedir?": "مرحبًا! ما اسمك؟",
    "Adını Gir": "اكتب اسمك",
    "Lütfen adını gir.": "من فضلك اكتب اسمك.",
    "Hedeflerin (Birden fazla seçebilirsin)": "أهدافك (يمكنك اختيار أكثر من هدف)",
    "Kilo vermek istiyorum": "أريد إنقاص وزني",
    "Kilomu korumak istiyorum": "أريد الحفاظ على وزني",
    "Kilo almak istiyorum": "أريد زيادة وزني",
    "Kas kazanmak istiyorum": "أريد بناء العضلات",
    "Sağlıklı beslenmek istiyorum": "أريد أن آكل بشكل صحي",
    "Cinsiyetin nedir?": "ما جنسك؟",
    "Seçimini yap:": "اختر:",
    "Kadın": "أنثى",
    "Erkek": "ذكر",
    "Doğum yılın ne?": "في أي سنة وُلدت؟",
    "Yıl": "السنة",
    "yaşındasın.": "سنة.",
    "18 yaşından küçüksün. Büyüme çağında kalori kısıtlamak gelişimi etkileyebilir.":
        "عمرك أقل من ١٨ عامًا. تقييد السعرات أثناء النمو قد يؤثر على تطورك.",
    "Boyun kaç?": "كم طولك؟",
    "Boy (cm)": "الطول (سم)",
    "Şu andaki kilon ne?": "كم وزنك حاليًا؟",
    "Kilo (kg)": "الوزن (كغ)",
    "Hedef kilon nedir?": "ما وزنك المستهدف؟",
    "Hedef Kilo (kg)": "الوزن المستهدف (كغ)",
    "Hedefe Ulaşma Süresi (Ay)": "المدة للوصول إليه (أشهر)",
    "Günlük hareket düzeyin": "مستوى نشاطك اليومي",
    "Nova Deneyimin İçin Bir Tema Seç": "اختر مظهرًا لـ Nova",
    "Kalori Hedefimi Hesapla": "احسب هدفي من السعرات",
    "Bu tempo hızlı. Güvenli aralık genelde haftada 0,5-1 kilodur; süreyi uzatmanı öneririm.":
        "هذه الوتيرة سريعة. المعدل الآمن عادة ٠٫٥ إلى ١ كغ أسبوعيًا؛ يُفضل تمديد المدة.",
    "Paylaştığın için teşekkürler": "شكرًا لمشاركتك",
    "İşte Kişisel Kalori Hedefin": "هذا هدفك الشخصي من السعرات",
    "Amacın:": "هدفك:",
    "Dinlenik Metabolizman (BMR):": "معدل الأيض الأساسي (BMR):",
    "Tahmini Günlük Harcaman:": "الحرق اليومي التقديري:",
    "Günlük Hedefin": "هدفك اليومي",
    "Harika, Uygulamaya Başla!": "رائع، لنبدأ",
    "Nova bir sağlık uygulaması değildir ve tıbbi tavsiye vermez.":
        "Nova ليست تطبيقًا طبيًا ولا تقدم نصائح طبية.",
    "Hesaplamalar genel formüllere dayanan tahminlerdir.":
        "الحسابات تقديرات مبنية على معادلات عامة.",
    "Geçmiş Tarih İnceleme": "عرض تاريخ آخر",
    "Ayarlar": "الإعدادات",
    "Kalori ve Denge Tablosu": "السعرات والتوازن",
    "Günlük Hedef Kalori Bütçen": "ميزانيتك اليومية من السعرات",
    "Bugüne Kadar Yediklerin": "ما تناولته حتى الآن",
    "Hareket ve Egzersizle Kazandıkların": "ما كسبته بالنشاط",
    "Geriye Kalan Yeme Hakkın": "المتبقي",
    "Günlük Makro İhtiyaçları": "أهداف العناصر الكبرى اليومية",
    "Protein": "البروتين",
    "Karbonhidrat": "الكربوهيدرات",
    "Yağ": "الدهون",
    "Yemek Ekle": "إضافة طعام",
    "Bugünkü Öğünlerin": "وجباتك اليوم",
    "Bugünkü Egzersizin": "تمرينك اليوم",
    "Günlük Aktivite ve Su Halkaları": "حلقات النشاط والماء",
    "Hesap ve Verilerin": "الحساب والبيانات",
    "Gelişimin": "تقدمك",
    "Hangi öğüne eklenecek?": "إلى أي وجبة؟",
    "Kahvaltı": "الفطور",
    "Öğle Yemeği": "الغداء",
    "Akşam Yemeği": "العشاء",
    "Ara Öğün": "وجبة خفيفة",
    "Egzersiz kalorisini kaydet": "حفظ سعرات التمرين",
    "Bugünkü toplam adımın": "خطواتك اليوم",
    "Adımı Kaydet": "حفظ الخطوات",
    "Eklenecek su (litre)": "الماء المضاف (لتر)",
    "Suyu Ekle": "إضافة ماء",
    "Sıfırla": "تصفير",
    "Adım": "الخطوات",
    "Su": "الماء",
    "Bugünkü Güncel Kilon (kg)": "وزنك اليوم (كغ)",
    "Günlük Özet": "الملخص اليومي",
    "Gelişim": "التقدم",
    "Öğün Tarama": "مسح وجبة",
    "Antrenman Koçu": "مدرب التمارين",
    "Asistan": "المساعد",
    "Oturum": "الجلسة",
    "Çıkış yap": "تسجيل الخروج",
    "Bilgilerin": "بياناتك",
    "Görünüm": "المظهر",
    "Hedefin": "هدفك",
    "Kaydet": "حفظ",
    "Ayarlardan çık": "إغلاق الإعدادات",
    "Değişikliklerin kaydedildi.": "تم حفظ تغييراتك.",
    "Kurulum sorularını baştan cevapla": "أجب عن أسئلة الإعداد من جديد",
    "Adın": "اسمك",
}

CEVIRILER = {"en": _EN, "de": _DE, "es": _ES, "fr": _FR, "ar": _AR}

# --------------------------------------------------------------------------
# Uzun açıklama cümleleri (sonradan tamamlandı)
# --------------------------------------------------------------------------
_EK = {
"de": {
 "Başka bir egzersiz yaptıysan yaktığın tahmini kalori":
   "Wenn du etwas anderes gemacht hast, die geschätzt verbrannten Kalorien",
 "Bize söylediklerin, seni nasıl destekleyeceğimizi şekillendirmemize yardımcı olacak.":
   "Deine Angaben helfen uns zu bestimmen, wie wir dich unterstützen.",
 "Boyun, vücudunun her gün ne kadar enerji harcadığını etkiler.":
   "Deine Größe beeinflusst, wie viel Energie dein Körper täglich verbraucht.",
 "Bu bilgi, bulunduğun noktaya göre kalori hedefini hesaplamamıza yardımcı olur. Şu anki kilonu tam bilmiyorsan en iyi tahminini gir, daha sonra uygulamada Pazar günleri güncelleyebilirsin.":
   "Das hilft uns, dein Kalorienziel von deinem jetzigen Stand aus zu berechnen. Wenn du unsicher bist, gib deine beste Schätzung ein; sonntags kannst du sie in der App aktualisieren.",
 "Bu tarayıcıda 30 gün açık kalırsın, sayfayı yenileyince çıkış yapmazsın. Ortak bir bilgisayardaysan işaretleme.":
   "Du bleibst 30 Tage in diesem Browser angemeldet und wirst beim Neuladen nicht abgemeldet. An einem gemeinsam genutzten Rechner besser nicht aktivieren.",
 "Bugün kaydedilmiş antrenman yok. Antrenman Koçu sekmesinden plan yapıp tamamladığın setleri girebilirsin.":
   "Heute ist kein Training erfasst. Plane eines im Tab Trainingscoach und trage deine Sätze ein.",
 "Cevapların, hedeflerini anlamamıza ve uygulamayı senin için kişiselleştirmemize yardımcı olacak.":
   "Deine Antworten helfen uns, deine Ziele zu verstehen und Nova für dich anzupassen.",
 "Cinsiyetin, vücudunun günlük enerji ihtiyacını hesaplamamızı doğrudan etkiler.":
   "Dein Geschlecht beeinflusst direkt die Berechnung deines täglichen Energiebedarfs.",
 "Hangi Öğün İçin Tarama Yapıyorsun?": "Welche Mahlzeit scannst du?",
 "Hareket düzeyin, günde ne kadar enerji harcadığını belirleyen en önemli etken. Adım ve egzersiz kayıtların bunun üzerine eklenir.":
   "Dein Aktivitätsniveau bestimmt maßgeblich deinen Energieverbrauch. Schritte und Training kommen obendrauf.",
 "Harika bir hafta geçirdik! Haftayı kapatmadan önce bugün sabah tartıldığın güncel kilonu girerek hedeflerini ve kalori planını yeni kilosuna göre güncelleyebilirsin.":
   "Gute Woche. Trage vor dem Wochenabschluss dein Gewicht von heute Morgen ein, dann werden Ziele und Kalorienplan neu berechnet.",
 "Harika! Kilon güncellendi ve haftalık kalori/makro planın yeni hedeflerine göre yeniden hesaplandı!":
   "Fertig. Dein Gewicht ist aktualisiert und dein Kalorien- und Makroplan wurde neu berechnet.",
 "Kilomu Güncelle ve Hedeflerimi Yenile": "Gewicht aktualisieren und Ziele neu berechnen",
 "Nova Kalori Hedefin, amacına ulaşmak için her gün kaç kalori tüketmen gerektiğini gösterir. Her gün bu hedefe yakın miktarda tüketirsen başarıya ulaşırsın.":
   "Dein Nova-Kalorienziel zeigt, wie viel du täglich essen solltest. Bleib nah dran, dann erreichst du dein Ziel.",
 "Nova uygulamasını sana özel hale getirmek ve sana hitap edebilmek için adını kullanacağız.":
   "Wir verwenden deinen Namen, um Nova persönlicher zu machen und dich anzusprechen.",
 "Nova'yı Hangi Amaçla Kullanmak İstiyorsun": "Wofür möchtest du Nova nutzen",
 "Pazar Günü Tartı ve Durum Güncellemesi!": "Sonntags-Wiegen",
 "Yaşın, vücudunun her gün ne kadar enerjiye (BMR) ihtiyaç duyduğunu etkiler.":
   "Dein Alter beeinflusst, wie viel Energie (BMR) dein Körper täglich braucht.",
 "Çıkış yaparsan bu tarayıcıdaki kayıtlı oturum da silinir.":
   "Beim Abmelden wird auch die gespeicherte Sitzung in diesem Browser gelöscht.",
},
"es": {
 "Başka bir egzersiz yaptıysan yaktığın tahmini kalori":
   "Si hiciste otra actividad, las calorías que calculas haber quemado",
 "Bize söylediklerin, seni nasıl destekleyeceğimizi şekillendirmemize yardımcı olacak.":
   "Lo que nos cuentas da forma a cómo vamos a apoyarte.",
 "Boyun, vücudunun her gün ne kadar enerji harcadığını etkiler.":
   "Tu altura influye en la energía que gasta tu cuerpo cada día.",
 "Bu bilgi, bulunduğun noktaya göre kalori hedefini hesaplamamıza yardımcı olur. Şu anki kilonu tam bilmiyorsan en iyi tahminini gir, daha sonra uygulamada Pazar günleri güncelleyebilirsin.":
   "Esto nos ayuda a calcular tu objetivo desde tu punto actual. Si no estás seguro, pon tu mejor estimación; podrás actualizarla los domingos en la app.",
 "Bu tarayıcıda 30 gün açık kalırsın, sayfayı yenileyince çıkış yapmazsın. Ortak bir bilgisayardaysan işaretleme.":
   "Permanecerás conectado 30 días en este navegador y recargar la página no cerrará tu sesión. No lo marques en un ordenador compartido.",
 "Bugün kaydedilmiş antrenman yok. Antrenman Koçu sekmesinden plan yapıp tamamladığın setleri girebilirsin.":
   "Hoy no hay entrenamiento registrado. Planifica uno en la pestaña Entrenador e introduce las series que completes.",
 "Cevapların, hedeflerini anlamamıza ve uygulamayı senin için kişiselleştirmemize yardımcı olacak.":
   "Tus respuestas nos ayudan a entender tus objetivos y adaptar Nova a ti.",
 "Cinsiyetin, vücudunun günlük enerji ihtiyacını hesaplamamızı doğrudan etkiler.":
   "Tu sexo influye directamente en el cálculo de tu necesidad diaria de energía.",
 "Hangi Öğün İçin Tarama Yapıyorsun?": "¿Qué comida estás escaneando?",
 "Hareket düzeyin, günde ne kadar enerji harcadığını belirleyen en önemli etken. Adım ve egzersiz kayıtların bunun üzerine eklenir.":
   "Tu nivel de actividad es el factor que más determina tu gasto diario. Los pasos y el ejercicio se suman encima.",
 "Harika bir hafta geçirdik! Haftayı kapatmadan önce bugün sabah tartıldığın güncel kilonu girerek hedeflerini ve kalori planını yeni kilosuna göre güncelleyebilirsin.":
   "Buena semana. Antes de cerrarla, introduce tu peso de esta mañana y recalcularemos tus objetivos y tu plan de calorías.",
 "Harika! Kilon güncellendi ve haftalık kalori/makro planın yeni hedeflerine göre yeniden hesaplandı!":
   "Listo. Tu peso se ha actualizado y tu plan de calorías y macros se ha recalculado.",
 "Kilomu Güncelle ve Hedeflerimi Yenile": "Actualizar mi peso y recalcular objetivos",
 "Nova Kalori Hedefin, amacına ulaşmak için her gün kaç kalori tüketmen gerektiğini gösterir. Her gün bu hedefe yakın miktarda tüketirsen başarıya ulaşırsın.":
   "Tu objetivo de calorías indica cuánto comer cada día para lograr tu meta. Mantente cerca de él y lo conseguirás.",
 "Nova uygulamasını sana özel hale getirmek ve sana hitap edebilmek için adını kullanacağız.":
   "Usamos tu nombre para personalizar Nova y poder dirigirnos a ti.",
 "Nova'yı Hangi Amaçla Kullanmak İstiyorsun": "¿Para qué quieres usar Nova",
 "Pazar Günü Tartı ve Durum Güncellemesi!": "Pesaje del domingo",
 "Yaşın, vücudunun her gün ne kadar enerjiye (BMR) ihtiyaç duyduğunu etkiler.":
   "Tu edad influye en la energía (BMR) que tu cuerpo necesita cada día.",
 "Çıkış yaparsan bu tarayıcıdaki kayıtlı oturum da silinir.":
   "Al cerrar sesión también se borra la sesión guardada en este navegador.",
},
"fr": {
 "Başka bir egzersiz yaptıysan yaktığın tahmini kalori":
   "Si tu as fait autre chose, les calories que tu estimes avoir brûlées",
 "Bize söylediklerin, seni nasıl destekleyeceğimizi şekillendirmemize yardımcı olacak.":
   "Ce que tu nous dis façonne la manière dont nous allons t'accompagner.",
 "Boyun, vücudunun her gün ne kadar enerji harcadığını etkiler.":
   "Ta taille influence l'énergie que ton corps dépense chaque jour.",
 "Bu bilgi, bulunduğun noktaya göre kalori hedefini hesaplamamıza yardımcı olur. Şu anki kilonu tam bilmiyorsan en iyi tahminini gir, daha sonra uygulamada Pazar günleri güncelleyebilirsin.":
   "Cela nous aide à calculer ton objectif à partir de ta situation actuelle. Si tu hésites, donne ta meilleure estimation ; tu pourras la mettre à jour le dimanche.",
 "Bu tarayıcıda 30 gün açık kalırsın, sayfayı yenileyince çıkış yapmazsın. Ortak bir bilgisayardaysan işaretleme.":
   "Tu resteras connecté 30 jours sur ce navigateur et recharger la page ne te déconnectera pas. À éviter sur un ordinateur partagé.",
 "Bugün kaydedilmiş antrenman yok. Antrenman Koçu sekmesinden plan yapıp tamamladığın setleri girebilirsin.":
   "Aucune séance enregistrée aujourd'hui. Planifie-en une dans l'onglet Coach et saisis tes séries.",
 "Cevapların, hedeflerini anlamamıza ve uygulamayı senin için kişiselleştirmemize yardımcı olacak.":
   "Tes réponses nous aident à comprendre tes objectifs et à adapter Nova.",
 "Cinsiyetin, vücudunun günlük enerji ihtiyacını hesaplamamızı doğrudan etkiler.":
   "Ton sexe influence directement le calcul de tes besoins énergétiques quotidiens.",
 "Hangi Öğün İçin Tarama Yapıyorsun?": "Quel repas scannes-tu ?",
 "Hareket düzeyin, günde ne kadar enerji harcadığını belirleyen en önemli etken. Adım ve egzersiz kayıtların bunun üzerine eklenir.":
   "Ton niveau d'activité est le facteur principal de ta dépense quotidienne. Les pas et les séances s'y ajoutent.",
 "Harika bir hafta geçirdik! Haftayı kapatmadan önce bugün sabah tartıldığın güncel kilonu girerek hedeflerini ve kalori planını yeni kilosuna göre güncelleyebilirsin.":
   "Bonne semaine. Avant de la clore, saisis ton poids de ce matin : tes objectifs et ton plan calorique seront recalculés.",
 "Harika! Kilon güncellendi ve haftalık kalori/makro planın yeni hedeflerine göre yeniden hesaplandı!":
   "C'est fait. Ton poids est à jour et ton plan calories et macros a été recalculé.",
 "Kilomu Güncelle ve Hedeflerimi Yenile": "Mettre à jour mon poids et recalculer mes objectifs",
 "Nova Kalori Hedefin, amacına ulaşmak için her gün kaç kalori tüketmen gerektiğini gösterir. Her gün bu hedefe yakın miktarda tüketirsen başarıya ulaşırsın.":
   "Ton objectif calorique indique combien manger chaque jour pour atteindre ton but. Reste proche et tu y arriveras.",
 "Nova uygulamasını sana özel hale getirmek ve sana hitap edebilmek için adını kullanacağız.":
   "Nous utilisons ton prénom pour personnaliser Nova et t'adresser la parole.",
 "Nova'yı Hangi Amaçla Kullanmak İstiyorsun": "Pourquoi veux-tu utiliser Nova",
 "Pazar Günü Tartı ve Durum Güncellemesi!": "Pesée du dimanche",
 "Yaşın, vücudunun her gün ne kadar enerjiye (BMR) ihtiyaç duyduğunu etkiler.":
   "Ton âge influence l'énergie (BMR) dont ton corps a besoin chaque jour.",
 "Çıkış yaparsan bu tarayıcıdaki kayıtlı oturum da silinir.":
   "La déconnexion efface aussi la session enregistrée sur ce navigateur.",
},
"ar": {
 "Başka bir egzersiz yaptıysan yaktığın tahmini kalori":
   "إذا مارست نشاطًا آخر، السعرات التي تقدر أنك أحرقتها",
 "Bize söylediklerin, seni nasıl destekleyeceğimizi şekillendirmemize yardımcı olacak.":
   "ما أخبرتنا به يحدد كيف سندعمك.",
 "Boyun, vücudunun her gün ne kadar enerji harcadığını etkiler.":
   "طولك يؤثر على كمية الطاقة التي يحرقها جسمك يوميًا.",
 "Bu bilgi, bulunduğun noktaya göre kalori hedefini hesaplamamıza yardımcı olur. Şu anki kilonu tam bilmiyorsan en iyi tahminini gir, daha sonra uygulamada Pazar günleri güncelleyebilirsin.":
   "هذا يساعدنا على حساب هدفك انطلاقًا من وضعك الحالي. إن لم تكن متأكدًا فاكتب أفضل تقدير، ويمكنك تحديثه أيام الأحد داخل التطبيق.",
 "Bu tarayıcıda 30 gün açık kalırsın, sayfayı yenileyince çıkış yapmazsın. Ortak bir bilgisayardaysan işaretleme.":
   "ستبقى مسجلًا ٣٠ يومًا في هذا المتصفح ولن يؤدي تحديث الصفحة إلى خروجك. لا تفعّله على جهاز مشترك.",
 "Bugün kaydedilmiş antrenman yok. Antrenman Koçu sekmesinden plan yapıp tamamladığın setleri girebilirsin.":
   "لا يوجد تمرين مسجل اليوم. خطط له من تبويب مدرب التمارين وأدخل المجموعات التي أكملتها.",
 "Cevapların, hedeflerini anlamamıza ve uygulamayı senin için kişiselleştirmemize yardımcı olacak.":
   "إجاباتك تساعدنا على فهم أهدافك وتخصيص Nova لك.",
 "Cinsiyetin, vücudunun günlük enerji ihtiyacını hesaplamamızı doğrudan etkiler.":
   "جنسك يؤثر مباشرة على حساب احتياجك اليومي من الطاقة.",
 "Hangi Öğün İçin Tarama Yapıyorsun?": "أي وجبة تقوم بمسحها؟",
 "Hareket düzeyin, günde ne kadar enerji harcadığını belirleyen en önemli etken. Adım ve egzersiz kayıtların bunun üzerine eklenir.":
   "مستوى نشاطك هو أهم عامل في تحديد حرقك اليومي، وتُضاف إليه خطواتك وتمارينك.",
 "Harika bir hafta geçirdik! Haftayı kapatmadan önce bugün sabah tartıldığın güncel kilonu girerek hedeflerini ve kalori planını yeni kilosuna göre güncelleyebilirsin.":
   "أسبوع جيد. قبل إغلاقه أدخل وزنك هذا الصباح وسيُعاد حساب أهدافك وخطة السعرات.",
 "Harika! Kilon güncellendi ve haftalık kalori/makro planın yeni hedeflerine göre yeniden hesaplandı!":
   "تم. حُدِّث وزنك وأُعيد حساب خطة السعرات والعناصر الكبرى.",
 "Kilomu Güncelle ve Hedeflerimi Yenile": "حدّث وزني وأعد حساب أهدافي",
 "Nova Kalori Hedefin, amacına ulaşmak için her gün kaç kalori tüketmen gerektiğini gösterir. Her gün bu hedefe yakın miktarda tüketirsen başarıya ulaşırsın.":
   "هدف السعرات يوضح كم تأكل يوميًا للوصول إلى غايتك. ابقَ قريبًا منه وستصل.",
 "Nova uygulamasını sana özel hale getirmek ve sana hitap edebilmek için adını kullanacağız.":
   "نستخدم اسمك لجعل Nova أكثر تخصيصًا ولمخاطبتك.",
 "Nova'yı Hangi Amaçla Kullanmak İstiyorsun": "لماذا تريد استخدام Nova",
 "Pazar Günü Tartı ve Durum Güncellemesi!": "وزن يوم الأحد",
 "Yaşın, vücudunun her gün ne kadar enerjiye (BMR) ihtiyaç duyduğunu etkiler.":
   "عمرك يؤثر على كمية الطاقة (BMR) التي يحتاجها جسمك يوميًا.",
 "Çıkış yaparsan bu tarayıcıdaki kayıtlı oturum da silinir.":
   "تسجيل الخروج يحذف أيضًا الجلسة المحفوظة في هذا المتصفح.",
},
}

for _kod, _sozluk in _EK.items():
    CEVIRILER[_kod].update(_sozluk)

# Uzun yaş uyarısı ve kalan tekil metinler
_EK2 = {'en': {'18 yaşından küçüksün. Büyüme çağında kalori kısıtlamak gelişimi etkileyebilir. Nova senin için günlük hedefi dinlenik metabolizmanın altına indirmeyecek, ama kilo hedefi koymadan önce bir doktora ya da diyetisyene danışmanı öneririm.': 'You are under 18. Restricting calories while you are still growing can affect your development. Nova will not set your daily target below your resting metabolism, but please talk to a doctor or dietitian before setting a weight goal.', 'Sil': 'Delete'}, 'de': {'18 yaşından küçüksün. Büyüme çağında kalori kısıtlamak gelişimi etkileyebilir. Nova senin için günlük hedefi dinlenik metabolizmanın altına indirmeyecek, ama kilo hedefi koymadan önce bir doktora ya da diyetisyene danışmanı öneririm.': 'Du bist unter 18. Kalorien zu beschränken, während du noch wächst, kann die Entwicklung beeinträchtigen. Nova setzt dein Tagesziel nicht unter deinen Grundumsatz, sprich aber bitte mit einem Arzt oder einer Ernährungsberatung, bevor du ein Gewichtsziel setzt.', 'Sil': 'Löschen'}, 'es': {'18 yaşından küçüksün. Büyüme çağında kalori kısıtlamak gelişimi etkileyebilir. Nova senin için günlük hedefi dinlenik metabolizmanın altına indirmeyecek, ama kilo hedefi koymadan önce bir doktora ya da diyetisyene danışmanı öneririm.': 'Tienes menos de 18 años. Restringir calorías mientras creces puede afectar tu desarrollo. Nova no pondrá tu objetivo diario por debajo de tu metabolismo basal, pero habla con un médico o dietista antes de fijar un objetivo de peso.', 'Sil': 'Eliminar'}, 'fr': {'18 yaşından küçüksün. Büyüme çağında kalori kısıtlamak gelişimi etkileyebilir. Nova senin için günlük hedefi dinlenik metabolizmanın altına indirmeyecek, ama kilo hedefi koymadan önce bir doktora ya da diyetisyene danışmanı öneririm.': 'Tu as moins de 18 ans. Restreindre les calories pendant la croissance peut nuire à ton développement. Nova ne placera pas ton objectif quotidien sous ton métabolisme de base, mais parles-en à un médecin ou un diététicien avant de fixer un objectif de poids.', 'Sil': 'Supprimer'}, 'ar': {'18 yaşından küçüksün. Büyüme çağında kalori kısıtlamak gelişimi etkileyebilir. Nova senin için günlük hedefi dinlenik metabolizmanın altına indirmeyecek, ama kilo hedefi koymadan önce bir doktora ya da diyetisyene danışmanı öneririm.': 'عمرك أقل من ١٨ عامًا. تقييد السعرات أثناء النمو قد يؤثر على تطورك. لن يضع Nova هدفك اليومي تحت معدل الأيض الأساسي، لكن استشر طبيبًا أو أخصائي تغذية قبل تحديد هدف للوزن.', 'Sil': 'حذف'}}
_EN.update(_EK2["en"])
for _k, _v in _EK2.items():
    CEVIRILER[_k].update(_v)

# h() için anahtarlar uzundan kısaya sıralanır: böylece "Protein" ifadesi
# "Protein İhtiyacı" gibi daha uzun bir anahtarın içinden kesmez.
# Her anahtar icin kelime sinirli bir kalip hazirlanir: "Su" ifadesi
# "Sunum" kelimesinin icinden kesemesin diye. Uzun anahtarlar once denenir.
_HARF = r"0-9A-Za-zÇĞİÖŞÜçğıöşüÂÎÛâîû"
_KALIPLAR = {
    _kod: tuple(
        (_a, re.compile(rf"(?<![{_HARF}]){re.escape(_a)}(?![{_HARF}])"))
        for _a in sorted(_sz, key=len, reverse=True)
    )
    for _kod, _sz in CEVIRILER.items()
}

# --------------------------------------------------------------------------
# TARİH
# --------------------------------------------------------------------------
_AYLAR = {
 "tr": ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"],
 "en": ["January","February","March","April","May","June","July","August","September","October","November","December"],
 "de": ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"],
 "es": ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"],
 "fr": ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"],
 "ar": ["يناير","فبراير","مارس","أبريل","مايو","يونيو","يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"],
}
_GUNLER = {
 "tr": ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"],
 "en": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
 "de": ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"],
 "es": ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"],
 "fr": ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"],
 "ar": ["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"],
}


def tarih_yaz(gun, dil=None):
    """Tarihi aktif dilin yazım düzenine göre yazar."""
    d = dil or aktif_dil()
    ay = _AYLAR.get(d, _AYLAR["tr"])[gun.month - 1]
    gun_adi = _GUNLER.get(d, _GUNLER["tr"])[gun.weekday()]
    if d == "en":
        return f"{gun_adi}, {ay} {gun.day}, {gun.year}"
    if d == "ar":
        return f"{gun_adi} {gun.day} {ay} {gun.year}"
    if d == "de":
        return f"{gun_adi}, {gun.day}. {ay} {gun.year}"
    if d == "es":
        return f"{gun_adi}, {gun.day} de {ay} de {gun.year}"
    if d == "fr":
        return f"{gun_adi} {gun.day} {ay} {gun.year}"
    return f"{gun.day} {ay} {gun.year} {gun_adi}"

# Dinamik cümle parçaları ve tablo başlıkları
_EK3 = {'en': {'Şu an': 'You are', 'yaşındasın.': 'years old.', 'Harika gidiyorsun! Günün geri kalanı için': 'Going well. For the rest of today you still have', 'yeme hakkın duruyor.': 'left to eat.', 'Limitini': 'You went', 'aştın. Hedefe dönmek için biraz egzersiz yapmalısın!': 'over your limit. Some activity would bring you back on track.', 'Metrik': 'Metric', 'Değer': 'Value', 'Yemek Adı': 'Food', 'Kalori (kcal)': 'Calories (kcal)', 'Protein (g)': 'Protein (g)', 'Karbonhidrat (g)': 'Carbs (g)', 'Yağ (g)': 'Fat (g)'}, 'de': {'Şu an': 'Du bist', 'yaşındasın.': 'Jahre alt.', 'Harika gidiyorsun! Günün geri kalanı için': 'Läuft gut. Für den Rest des Tages hast du noch', 'yeme hakkın duruyor.': 'übrig.', 'Limitini': 'Du liegst', 'aştın. Hedefe dönmek için biraz egzersiz yapmalısın!': 'über deinem Limit. Etwas Bewegung bringt dich zurück auf Kurs.', 'Metrik': 'Kennzahl', 'Değer': 'Wert', 'Yemek Adı': 'Lebensmittel', 'Kalori (kcal)': 'Kalorien (kcal)', 'Protein (g)': 'Eiweiß (g)', 'Karbonhidrat (g)': 'Kohlenhydrate (g)', 'Yağ (g)': 'Fett (g)'}, 'es': {'Şu an': 'Tienes', 'yaşındasın.': 'años.', 'Harika gidiyorsun! Günün geri kalanı için': 'Vas bien. Para el resto del día te quedan', 'yeme hakkın duruyor.': 'por comer.', 'Limitini': 'Te has pasado', 'aştın. Hedefe dönmek için biraz egzersiz yapmalısın!': 'de tu límite. Un poco de actividad te devolverá al plan.', 'Metrik': 'Métrica', 'Değer': 'Valor', 'Yemek Adı': 'Alimento', 'Kalori (kcal)': 'Calorías (kcal)', 'Protein (g)': 'Proteína (g)', 'Karbonhidrat (g)': 'Carbohidratos (g)', 'Yağ (g)': 'Grasa (g)'}, 'fr': {'Şu an': 'Tu as', 'yaşındasın.': 'ans.', 'Harika gidiyorsun! Günün geri kalanı için': 'Ça avance bien. Pour le reste de la journée, il te reste', 'yeme hakkın duruyor.': 'à manger.', 'Limitini': 'Tu as dépassé', 'aştın. Hedefe dönmek için biraz egzersiz yapmalısın!': "ta limite. Un peu d'activité te remettra sur la bonne voie.", 'Metrik': 'Indicateur', 'Değer': 'Valeur', 'Yemek Adı': 'Aliment', 'Kalori (kcal)': 'Calories (kcal)', 'Protein (g)': 'Protéines (g)', 'Karbonhidrat (g)': 'Glucides (g)', 'Yağ (g)': 'Lipides (g)'}, 'ar': {'Şu an': 'عمرك', 'yaşındasın.': 'سنة.', 'Harika gidiyorsun! Günün geri kalanı için': 'تسير بشكل جيد. لبقية اليوم ما زال لديك', 'yeme hakkın duruyor.': 'للأكل.', 'Limitini': 'تجاوزت', 'aştın. Hedefe dönmek için biraz egzersiz yapmalısın!': 'حدّك. بعض النشاط سيعيدك إلى المسار.', 'Metrik': 'المؤشر', 'Değer': 'القيمة', 'Yemek Adı': 'الطعام', 'Kalori (kcal)': 'السعرات (kcal)', 'Protein (g)': 'البروتين (غ)', 'Karbonhidrat (g)': 'الكربوهيدرات (غ)', 'Yağ (g)': 'الدهون (غ)'}}
_EN.update(_EK3["en"])
for _k, _v in _EK3.items():
    CEVIRILER[_k].update(_v)
_KALIPLAR = {
    _kod: tuple(
        (_a, re.compile(rf"(?<![{_HARF}]){re.escape(_a)}(?![{_HARF}])"))
        for _a in sorted(_sz, key=len, reverse=True)
    )
    for _kod, _sz in CEVIRILER.items()
}

# --------------------------------------------------------------------------
# Diğer bölümlerin çevirileri ayrı dosyada tutulur
# --------------------------------------------------------------------------
try:
    from ceviriler_ek import EK as _EK_DIGER
    _EN.update(_EK_DIGER.get("en", {}))
    for _kod, _sozluk in _EK_DIGER.items():
        CEVIRILER.setdefault(_kod, {}).update(_sozluk)
    _KALIPLAR = {
        _kod: tuple(
            (_a, re.compile(rf"(?<![{_HARF}]){re.escape(_a)}(?![{_HARF}])"))
            for _a in sorted(_sz, key=len, reverse=True)
        )
        for _kod, _sz in CEVIRILER.items()
    }
except ImportError:  # dosya yoksa Türkçe ile devam
    pass
