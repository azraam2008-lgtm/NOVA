"""
ceviriler_ek.py - Gelişim, yemek arama, asistan, hesap, öğün tarama ve
şifre sıfırlama bölümlerinin çevirileri.

diller.py bu dosyayı kendiliğinden yükler. Ayrı tutulmasının sebebi
diller.py'nin tek dosyada okunamayacak kadar büyümesi.
"""

EK = {
"en": {
 "#### Oturum": "#### Session",
 # Gelişim
 "#### Kalori": "#### Calories",
 "#### Kilo": "#### Weight",
 "#### Makro dağılımın": "#### Your macro split",
 "#### Öğünlere göre dağılım": "#### Split by meal",
 "#### Egzersiz ve aktivite": "#### Exercise and activity",
 "Dönem": "Period",
 "Son 7 gün": "Last 7 days",
 "Son 30 gün": "Last 30 days",
 "Son 90 gün": "Last 90 days",
 "90 günlük görünümde her çubuk bir haftanın ortalamasıdır.":
   "In the 90-day view each bar is a weekly average.",
 "Mavi kesikli çizgi günlük hedefin.": "The dashed blue line is your daily target.",
 "Mavi kesikli çizgi günde 10.000 adım hedefi.": "The dashed blue line is the 10,000 step goal.",
 "Bu dönemde öğün kaydın yok.": "You have no meals logged in this period.",
 "Kilo kayıtlarında okunamayan bir tarih var.": "One of your weight entries has an unreadable date.",
 "Bu dosyayı diyetisyenine gönderebilirsin.": "You can send this file to your dietitian.",
 # Yemek arama
 "Yemek ara": "Search for a food",
 "Aramak için en az iki harf yaz.": "Type at least two letters to search.",
 "Sonuçlar": "Results",
 "Marka ürünlerinde de ara (Open Food Facts)": "Also search branded products (Open Food Facts)",
 "Marka ürünlerine şu an ulaşılamadı. Kendi veritabanındaki sonuçlar aşağıda.":
   "Branded products are unreachable right now. Results from your own database are below.",
 "Ürün veritabanına şu an ulaşılamadı. Biraz sonra tekrar dene.":
   "The product database is unreachable right now. Please try again shortly.",
 "Bulamadım. \"Kendi yemeğim\" sekmesinden kendin ekleyebilirsin.":
   "No match. You can add it yourself from the \"My own food\" tab.",
 "Yediğin miktar (gram)": "Amount you ate (grams)",
 "Günlüğe ekle": "Add to diary",
 "Favorilere ekle": "Add to favourites",
 "Hangi öğün": "Which meal",
 "Hangi gün": "Which day",
 "Ekle": "Add",
 "Çıkar": "Remove",
 "Tekrar ekle": "Add again",
 "Nasıl?": "How?",
 # Barkod
 "Barkod numarası": "Barcode number",
 "Barkodu ortala ve çek": "Centre the barcode and take the photo",
 "Kamerayı aç": "Open camera",
 "Kamerayı kapat": "Close camera",
 "Kamera yalnızca bu düğmeye bastığında açılır.": "The camera only opens when you press this button.",
 "Paketin arkasındaki barkodu okut. Bulunamazsa besin değerleri tablosunun fotoğrafından okuyabilirim.":
   "Scan the barcode on the back of the pack. If it is not found, I can read the nutrition table from a photo.",
 "Barkodu okuyamadım. Daha yakın, net ve düz çekmeyi dene ya da numarayı elle yaz.":
   "I could not read the barcode. Try closer, sharper and straight on, or type the number in.",
 "Bu numara geçerli bir barkod gibi görünmüyor. Rakamları kontrol et.":
   "That does not look like a valid barcode. Check the digits.",
 "Bu barkod veritabanında yok. Paketin besin değerleri tablosunu çekersen okuyabilirim.":
   "That barcode is not in the database. Photograph the nutrition table and I can read it.",
 "Barkod okuyucu kurulu değil. requirements.txt dosyasına zxing-cpp ekle.":
   "The barcode reader is not installed. Add zxing-cpp to requirements.txt.",
 "Bunun yerine besin değerleri tablosunu oku": "Read the nutrition table instead",
 "Etiketi oku": "Read the label",
 "Besin değerleri tablosunun fotoğrafı": "Photo of the nutrition table",
 "Etiketteki protein, karbonhidrat ve yağ değerlerinin hepsi okunamadı. Daha net bir fotoğraf dene.":
   "I could not read all of the protein, carbs and fat from the label. Try a sharper photo.",
 "Okunan değerleri kontrol et, yanlışsa aşağıdan düzelt.":
   "Check the values I read and correct them below if needed.",
 "ya da galerinden bir fotoğraf seç": "or pick a photo from your gallery",
 # Favoriler ve kopyalama
 "#### Favorilerin": "#### Your favourites",
 "#### Kaydettiklerin": "#### Your saved foods",
 "#### Son yedikleri": "#### Recently eaten",
 "#### Önceki bir öğünü kopyala": "#### Copy an earlier meal",
 "Henüz favorin yok. Bir yemek eklerken \"Favorilere ekle\" düğmesini kullan.":
   "No favourites yet. Use the \"Add to favourites\" button when you log a food.",
 "Henüz kayıt yok.": "Nothing logged yet.",
 "Kopyalanacak başka gün yok.": "There is no other day to copy from.",
 "O gün o öğünde kayıt yok.": "Nothing was logged for that meal on that day.",
 # Kendi yemeğim
 "Yemeğin adı": "Name of the food",
 "Yemeğin adını yaz.": "Enter a name for the food.",
 "Bir porsiyon kaç gram?": "How many grams is one portion?",
 "Protein (porsiyon başına, g)": "Protein (per portion, g)",
 "Karbonhidrat (porsiyon başına, g)": "Carbs (per portion, g)",
 "Yağ (porsiyon başına, g)": "Fat (per portion, g)",
 "En az bir besin değeri gir.": "Enter at least one nutrition value.",
 "Veritabanına bağlanılamadı, kaydedilemedi.": "Could not reach the database, nothing was saved.",
 # Antrenman koçu ve asistan
 "Antrenman koçu": "Training coach",
 "Seviyen": "Your level",
 "Elindeki ekipman (boşsa ekipmansız)": "Equipment you have (leave empty for none)",
 "Ağrı ya da sınırlaman var mı? (isteğe bağlı)": "Any pain or limitation? (optional)",
 "Bu seçimlerle yeterli hareket yok. exercises.json dosyasına hareket ekle.":
   "Not enough exercises match these choices. Add more to exercises.json.",
 "exercises.json bulunamadı ya da boş.": "exercises.json is missing or empty.",
 "Plan oluşturulamadı. Tekrar dene.": "Could not build a plan. Please try again.",
 "Video yakında eklenecek.": "A video will be added soon.",
 "#### Antrenmanı kaydet": "#### Log your workout",
 "Antrenmanı kaydet": "Log workout",
 "Antrenman kaydedildi.": "Workout logged.",
 "Tamamlanan set": "Sets completed",
 "Tekrarlar (örn. 12-10-8)": "Reps (e.g. 12-10-8)",
 "Hangi günü yaptın?": "Which day did you train?",
 "Önce tamamladığın setleri gir.": "Enter the sets you completed first.",
 "Hazır sorular": "Suggested questions",
 "Bir şey sor...": "Ask me something...",
 "Sohbeti temizle": "Clear the chat",
 "Beslenme ve antrenman soruların için. Genel bilgi verir, tıbbi tavsiye değildir.":
   "For your nutrition and training questions. General information, not medical advice.",
 # Öğün tarama
 "Öğün taraması": "Meal scan",
 "Yemeğin fotoğrafını çek": "Take a photo of your meal",
 "Yemeğin fotoğrafını seç": "Choose a photo of your meal",
 "Analiz et": "Analyse",
 "Not (isteğe bağlı)": "Note (optional)",
 "Örn: \"Kahvaltıda iki yumurta, bir dilim tam buğday ekmeği, yarım avuç ceviz ve şekersiz çay\"":
   "e.g. \"Two eggs, a slice of wholemeal bread, a small handful of walnuts and unsweetened tea\"",
 "#### Değerleri düzenle": "#### Adjust the values",
 "Gramajı kaydırarak değiştir. Bir kalemi çıkarmak için 0'a çek.":
   "Drag to change the grams. Set an item to 0 to remove it.",
 "Tüm kalemler 0 gram. En az birini artır.": "Every item is 0 g. Increase at least one.",
 "Bu kalemden emin değilim. Gramajı kontrol et.": "I am not confident about this item. Check the grams.",
 "Değerler yapay zekanın tahminidir ve gerçek değerden sapabilir.":
   "These values are the AI's estimate and can differ from the real ones.",
 "Referans değerlerle doğrula": "Check against reference values",
 "Fotoğraf ya da ses kaydı analiz için Google Gemini'ye gönderilir.":
   "The photo or voice recording is sent to Google Gemini for analysis.",
 "Kaynak": "Source",
 # Hesap
 "#### Hatırlatmalar": "#### Reminders",
 "#### Verilerin": "#### Your data",
 "#### Hesabını sil": "#### Delete your account",
 "Her akşam hatırlatma gönder": "Send me a reminder every evening",
 "Hatırlatma gönderimi henüz ayarlanmamış.": "Reminders are not set up yet.",
 "Telegram sohbet numaran": "Your Telegram chat ID",
 "Deneme mesajı gönder": "Send a test message",
 "Gönderildi, telefonuna bak.": "Sent, check your phone.",
 "Verilerimi indir (JSON)": "Download my data (JSON)",
 "Nova'daki bütün verilerin senin. İstediğin zaman indirebilir ya da sildirebilirsin.":
   "All your data in Nova belongs to you. You can download or delete it at any time.",
 "Hesabın ve bütün kayıtların kalıcı olarak silinir. Bu işlem geri alınamaz.":
   "Your account and all your records are permanently deleted. This cannot be undone.",
 "Silmeden önce verilerini indirmeni öneririm. Silinen veriler geri getirilemez.":
   "I recommend downloading your data first. Deleted data cannot be recovered.",
 "Hesabımı kalıcı olarak sil": "Permanently delete my account",
 "Kullanıcı adını tam olarak yazman gerekiyor.": "You need to type your username exactly.",
 "Şifreni gir": "Enter your password",
 "Şifre yanlış.": "Wrong password.",
 "Veritabanına bağlanılamadı, silme yapılamadı.": "Could not reach the database, nothing was deleted.",
 "Hesabın silindi. Nova'yı kullandığın için teşekkürler.":
   "Your account has been deleted. Thank you for using Nova.",
 # Şifre sıfırlama
 "Kullanıcı adın ya da e-postan": "Your username or email",
 "Kod gönder": "Send code",
 "E-postana gelen 6 haneli kod": "The 6-digit code sent to your email",
 "Kodu gir.": "Enter the code.",
 "Yeni şifren (en az 8 karakter, bir büyük harf ve bir rakam)":
   "Your new password (at least 8 characters, one capital letter and one digit)",
 "Yeni şifren (tekrar)": "Your new password (again)",
 "İki şifre birbirini tutmuyor.": "The two passwords do not match.",
 "Şifremi değiştir": "Change my password",
 "Şifren değişti. Artık yeni şifrenle giriş yapabilirsin.":
   "Your password has been changed. You can now sign in with it.",
 "Vazgeç": "Cancel",
},

"de": {
 "#### Oturum": "#### Sitzung",
 "#### Kalori": "#### Kalorien", "#### Kilo": "#### Gewicht",
 "#### Makro dağılımın": "#### Deine Makroverteilung",
 "#### Öğünlere göre dağılım": "#### Verteilung nach Mahlzeit",
 "#### Egzersiz ve aktivite": "#### Training und Aktivität",
 "Dönem": "Zeitraum", "Son 7 gün": "Letzte 7 Tage", "Son 30 gün": "Letzte 30 Tage",
 "Son 90 gün": "Letzte 90 Tage",
 "90 günlük görünümde her çubuk bir haftanın ortalamasıdır.":
   "In der 90-Tage-Ansicht ist jeder Balken ein Wochendurchschnitt.",
 "Mavi kesikli çizgi günlük hedefin.": "Die blaue gestrichelte Linie ist dein Tagesziel.",
 "Mavi kesikli çizgi günde 10.000 adım hedefi.": "Die blaue gestrichelte Linie ist das Ziel von 10.000 Schritten.",
 "Bu dönemde öğün kaydın yok.": "In diesem Zeitraum hast du nichts erfasst.",
 "Kilo kayıtlarında okunamayan bir tarih var.": "Eine deiner Gewichtsangaben hat ein unlesbares Datum.",
 "Bu dosyayı diyetisyenine gönderebilirsin.": "Diese Datei kannst du deiner Ernährungsberatung schicken.",
 "Yemek ara": "Lebensmittel suchen",
 "Aramak için en az iki harf yaz.": "Gib mindestens zwei Buchstaben ein.",
 "Sonuçlar": "Ergebnisse",
 "Marka ürünlerinde de ara (Open Food Facts)": "Auch Markenprodukte durchsuchen (Open Food Facts)",
 "Marka ürünlerine şu an ulaşılamadı. Kendi veritabanındaki sonuçlar aşağıda.":
   "Markenprodukte sind gerade nicht erreichbar. Unten die Treffer aus deiner eigenen Datenbank.",
 "Ürün veritabanına şu an ulaşılamadı. Biraz sonra tekrar dene.":
   "Die Produktdatenbank ist gerade nicht erreichbar. Versuch es gleich noch einmal.",
 "Bulamadım. \"Kendi yemeğim\" sekmesinden kendin ekleyebilirsin.":
   "Nichts gefunden. Du kannst es im Tab \"Mein eigenes Essen\" selbst anlegen.",
 "Yediğin miktar (gram)": "Gegessene Menge (Gramm)",
 "Günlüğe ekle": "Zum Tagebuch hinzufügen", "Favorilere ekle": "Zu Favoriten hinzufügen",
 "Hangi öğün": "Welche Mahlzeit", "Hangi gün": "Welcher Tag",
 "Ekle": "Hinzufügen", "Çıkar": "Entfernen", "Tekrar ekle": "Erneut hinzufügen", "Nasıl?": "Wie?",
 "Barkod numarası": "Barcode-Nummer",
 "Barkodu ortala ve çek": "Barcode mittig halten und fotografieren",
 "Kamerayı aç": "Kamera öffnen", "Kamerayı kapat": "Kamera schließen",
 "Kamera yalnızca bu düğmeye bastığında açılır.":
   "Die Kamera öffnet sich nur, wenn du diese Taste drückst.",
 "Paketin arkasındaki barkodu okut. Bulunamazsa besin değerleri tablosunun fotoğrafından okuyabilirim.":
   "Scanne den Barcode auf der Rückseite. Wird er nicht gefunden, lese ich die Nährwerttabelle vom Foto.",
 "Barkodu okuyamadım. Daha yakın, net ve düz çekmeyi dene ya da numarayı elle yaz.":
   "Ich konnte den Barcode nicht lesen. Versuch es näher, schärfer und gerade, oder tippe die Nummer ein.",
 "Bu numara geçerli bir barkod gibi görünmüyor. Rakamları kontrol et.":
   "Das sieht nicht nach einem gültigen Barcode aus. Prüfe die Ziffern.",
 "Bu barkod veritabanında yok. Paketin besin değerleri tablosunu çekersen okuyabilirim.":
   "Dieser Barcode ist nicht in der Datenbank. Fotografiere die Nährwerttabelle, dann lese ich sie.",
 "Barkod okuyucu kurulu değil. requirements.txt dosyasına zxing-cpp ekle.":
   "Der Barcode-Leser ist nicht installiert. Füge zxing-cpp zur requirements.txt hinzu.",
 "Bunun yerine besin değerleri tablosunu oku": "Stattdessen die Nährwerttabelle lesen",
 "Etiketi oku": "Etikett lesen",
 "Besin değerleri tablosunun fotoğrafı": "Foto der Nährwerttabelle",
 "Etiketteki protein, karbonhidrat ve yağ değerlerinin hepsi okunamadı. Daha net bir fotoğraf dene.":
   "Ich konnte Eiweiß, Kohlenhydrate und Fett nicht vollständig lesen. Versuch ein schärferes Foto.",
 "Okunan değerleri kontrol et, yanlışsa aşağıdan düzelt.":
   "Prüfe die gelesenen Werte und korrigiere sie unten, falls nötig.",
 "ya da galerinden bir fotoğraf seç": "oder wähle ein Foto aus deiner Galerie",
 "#### Favorilerin": "#### Deine Favoriten", "#### Kaydettiklerin": "#### Deine gespeicherten Lebensmittel",
 "#### Son yedikleri": "#### Zuletzt gegessen", "#### Önceki bir öğünü kopyala": "#### Frühere Mahlzeit kopieren",
 "Henüz favorin yok. Bir yemek eklerken \"Favorilere ekle\" düğmesini kullan.":
   "Noch keine Favoriten. Nutze beim Erfassen die Taste \"Zu Favoriten hinzufügen\".",
 "Henüz kayıt yok.": "Noch nichts erfasst.",
 "Kopyalanacak başka gün yok.": "Es gibt keinen anderen Tag zum Kopieren.",
 "O gün o öğünde kayıt yok.": "Für diese Mahlzeit wurde an dem Tag nichts erfasst.",
 "Yemeğin adı": "Name des Lebensmittels", "Yemeğin adını yaz.": "Gib einen Namen ein.",
 "Bir porsiyon kaç gram?": "Wie viel Gramm ist eine Portion?",
 "Protein (porsiyon başına, g)": "Eiweiß (pro Portion, g)",
 "Karbonhidrat (porsiyon başına, g)": "Kohlenhydrate (pro Portion, g)",
 "Yağ (porsiyon başına, g)": "Fett (pro Portion, g)",
 "En az bir besin değeri gir.": "Gib mindestens einen Nährwert ein.",
 "Veritabanına bağlanılamadı, kaydedilemedi.": "Datenbank nicht erreichbar, nichts gespeichert.",
 "Antrenman koçu": "Trainingscoach", "Seviyen": "Dein Niveau",
 "Elindeki ekipman (boşsa ekipmansız)": "Verfügbare Ausrüstung (leer = ohne Geräte)",
 "Ağrı ya da sınırlaman var mı? (isteğe bağlı)": "Schmerzen oder Einschränkungen? (optional)",
 "Bu seçimlerle yeterli hareket yok. exercises.json dosyasına hareket ekle.":
   "Zu wenige Übungen passen dazu. Ergänze exercises.json.",
 "exercises.json bulunamadı ya da boş.": "exercises.json fehlt oder ist leer.",
 "Plan oluşturulamadı. Tekrar dene.": "Plan konnte nicht erstellt werden. Versuch es erneut.",
 "Video yakında eklenecek.": "Ein Video folgt bald.",
 "#### Antrenmanı kaydet": "#### Training erfassen", "Antrenmanı kaydet": "Training erfassen",
 "Antrenman kaydedildi.": "Training erfasst.", "Tamamlanan set": "Absolvierte Sätze",
 "Tekrarlar (örn. 12-10-8)": "Wiederholungen (z. B. 12-10-8)",
 "Hangi günü yaptın?": "An welchem Tag war das?",
 "Önce tamamladığın setleri gir.": "Trage zuerst deine Sätze ein.",
 "Hazır sorular": "Vorgeschlagene Fragen", "Bir şey sor...": "Frag mich etwas...",
 "Sohbeti temizle": "Chat leeren",
 "Beslenme ve antrenman soruların için. Genel bilgi verir, tıbbi tavsiye değildir.":
   "Für Fragen zu Ernährung und Training. Allgemeine Infos, keine medizinische Beratung.",
 "Öğün taraması": "Mahlzeit scannen",
 "Yemeğin fotoğrafını çek": "Foto deiner Mahlzeit aufnehmen",
 "Yemeğin fotoğrafını seç": "Foto deiner Mahlzeit auswählen",
 "Analiz et": "Analysieren", "Not (isteğe bağlı)": "Notiz (optional)",
 "Örn: \"Kahvaltıda iki yumurta, bir dilim tam buğday ekmeği, yarım avuç ceviz ve şekersiz çay\"":
   "z. B. \"Zwei Eier, eine Scheibe Vollkornbrot, eine kleine Handvoll Walnüsse und ungesüßter Tee\"",
 "#### Değerleri düzenle": "#### Werte anpassen",
 "Gramajı kaydırarak değiştir. Bir kalemi çıkarmak için 0'a çek.":
   "Zieh den Regler, um das Gewicht zu ändern. Auf 0 ziehen entfernt den Posten.",
 "Tüm kalemler 0 gram. En az birini artır.": "Alle Posten stehen auf 0 g. Erhöhe mindestens einen.",
 "Bu kalemden emin değilim. Gramajı kontrol et.": "Bei diesem Posten bin ich unsicher. Prüfe das Gewicht.",
 "Değerler yapay zekanın tahminidir ve gerçek değerden sapabilir.":
   "Die Werte sind Schätzungen der KI und können abweichen.",
 "Referans değerlerle doğrula": "Mit Referenzwerten abgleichen",
 "Fotoğraf ya da ses kaydı analiz için Google Gemini'ye gönderilir.":
   "Foto oder Sprachaufnahme wird zur Analyse an Google Gemini gesendet.",
 "Kaynak": "Quelle",
 "#### Hatırlatmalar": "#### Erinnerungen", "#### Verilerin": "#### Deine Daten",
 "#### Hesabını sil": "#### Konto löschen",
 "Her akşam hatırlatma gönder": "Jeden Abend eine Erinnerung senden",
 "Hatırlatma gönderimi henüz ayarlanmamış.": "Erinnerungen sind noch nicht eingerichtet.",
 "Telegram sohbet numaran": "Deine Telegram-Chat-ID",
 "Deneme mesajı gönder": "Testnachricht senden", "Gönderildi, telefonuna bak.": "Gesendet, schau auf dein Handy.",
 "Verilerimi indir (JSON)": "Meine Daten herunterladen (JSON)",
 "Nova'daki bütün verilerin senin. İstediğin zaman indirebilir ya da sildirebilirsin.":
   "Alle deine Daten in Nova gehören dir. Du kannst sie jederzeit herunterladen oder löschen.",
 "Hesabın ve bütün kayıtların kalıcı olarak silinir. Bu işlem geri alınamaz.":
   "Dein Konto und alle Einträge werden dauerhaft gelöscht. Das lässt sich nicht rückgängig machen.",
 "Silmeden önce verilerini indirmeni öneririm. Silinen veriler geri getirilemez.":
   "Lade deine Daten vorher herunter. Gelöschte Daten sind nicht wiederherstellbar.",
 "Hesabımı kalıcı olarak sil": "Mein Konto dauerhaft löschen",
 "Kullanıcı adını tam olarak yazman gerekiyor.": "Du musst deinen Benutzernamen exakt eingeben.",
 "Şifreni gir": "Gib dein Passwort ein", "Şifre yanlış.": "Falsches Passwort.",
 "Veritabanına bağlanılamadı, silme yapılamadı.": "Datenbank nicht erreichbar, nichts gelöscht.",
 "Hesabın silindi. Nova'yı kullandığın için teşekkürler.":
   "Dein Konto wurde gelöscht. Danke, dass du Nova genutzt hast.",
 "Kullanıcı adın ya da e-postan": "Dein Benutzername oder deine E-Mail",
 "Kod gönder": "Code senden", "E-postana gelen 6 haneli kod": "Der 6-stellige Code aus deiner E-Mail",
 "Kodu gir.": "Gib den Code ein.",
 "Yeni şifren (en az 8 karakter, bir büyük harf ve bir rakam)":
   "Dein neues Passwort (mindestens 8 Zeichen, ein Großbuchstabe und eine Ziffer)",
 "Yeni şifren (tekrar)": "Neues Passwort (wiederholen)",
 "İki şifre birbirini tutmuyor.": "Die beiden Passwörter stimmen nicht überein.",
 "Şifremi değiştir": "Passwort ändern",
 "Şifren değişti. Artık yeni şifrenle giriş yapabilirsin.":
   "Dein Passwort wurde geändert. Du kannst dich jetzt damit anmelden.",
 "Vazgeç": "Abbrechen",
},

"es": {
 "#### Oturum": "#### Sesión",
 "#### Kalori": "#### Calorías", "#### Kilo": "#### Peso",
 "#### Makro dağılımın": "#### Tu reparto de macros",
 "#### Öğünlere göre dağılım": "#### Reparto por comida",
 "#### Egzersiz ve aktivite": "#### Ejercicio y actividad",
 "Dönem": "Periodo", "Son 7 gün": "Últimos 7 días", "Son 30 gün": "Últimos 30 días",
 "Son 90 gün": "Últimos 90 días",
 "90 günlük görünümde her çubuk bir haftanın ortalamasıdır.":
   "En la vista de 90 días cada barra es la media de una semana.",
 "Mavi kesikli çizgi günlük hedefin.": "La línea azul discontinua es tu objetivo diario.",
 "Mavi kesikli çizgi günde 10.000 adım hedefi.": "La línea azul discontinua es el objetivo de 10.000 pasos.",
 "Bu dönemde öğün kaydın yok.": "No tienes comidas registradas en este periodo.",
 "Kilo kayıtlarında okunamayan bir tarih var.": "Uno de tus registros de peso tiene una fecha ilegible.",
 "Bu dosyayı diyetisyenine gönderebilirsin.": "Puedes enviar este archivo a tu dietista.",
 "Yemek ara": "Buscar un alimento",
 "Aramak için en az iki harf yaz.": "Escribe al menos dos letras para buscar.",
 "Sonuçlar": "Resultados",
 "Marka ürünlerinde de ara (Open Food Facts)": "Buscar también productos de marca (Open Food Facts)",
 "Marka ürünlerine şu an ulaşılamadı. Kendi veritabanındaki sonuçlar aşağıda.":
   "Los productos de marca no están disponibles ahora. Abajo están los de tu propia base de datos.",
 "Ürün veritabanına şu an ulaşılamadı. Biraz sonra tekrar dene.":
   "La base de datos de productos no responde. Inténtalo dentro de un momento.",
 "Bulamadım. \"Kendi yemeğim\" sekmesinden kendin ekleyebilirsin.":
   "No lo encuentro. Puedes añadirlo tú desde la pestaña \"Mi propio alimento\".",
 "Yediğin miktar (gram)": "Cantidad que comiste (gramos)",
 "Günlüğe ekle": "Añadir al diario", "Favorilere ekle": "Añadir a favoritos",
 "Hangi öğün": "Qué comida", "Hangi gün": "Qué día",
 "Ekle": "Añadir", "Çıkar": "Quitar", "Tekrar ekle": "Añadir otra vez", "Nasıl?": "¿Cómo?",
 "Barkod numarası": "Número de código de barras",
 "Barkodu ortala ve çek": "Centra el código y haz la foto",
 "Kamerayı aç": "Abrir cámara", "Kamerayı kapat": "Cerrar cámara",
 "Kamera yalnızca bu düğmeye bastığında açılır.": "La cámara solo se abre al pulsar este botón.",
 "Paketin arkasındaki barkodu okut. Bulunamazsa besin değerleri tablosunun fotoğrafından okuyabilirim.":
   "Escanea el código del reverso. Si no aparece, puedo leer la tabla nutricional de una foto.",
 "Barkodu okuyamadım. Daha yakın, net ve düz çekmeyi dene ya da numarayı elle yaz.":
   "No pude leer el código. Prueba más cerca, más nítido y recto, o escribe el número.",
 "Bu numara geçerli bir barkod gibi görünmüyor. Rakamları kontrol et.":
   "Ese número no parece un código válido. Revisa los dígitos.",
 "Bu barkod veritabanında yok. Paketin besin değerleri tablosunu çekersen okuyabilirim.":
   "Ese código no está en la base de datos. Fotografía la tabla nutricional y la leo.",
 "Barkod okuyucu kurulu değil. requirements.txt dosyasına zxing-cpp ekle.":
   "El lector de códigos no está instalado. Añade zxing-cpp a requirements.txt.",
 "Bunun yerine besin değerleri tablosunu oku": "Leer la tabla nutricional en su lugar",
 "Etiketi oku": "Leer la etiqueta",
 "Besin değerleri tablosunun fotoğrafı": "Foto de la tabla nutricional",
 "Etiketteki protein, karbonhidrat ve yağ değerlerinin hepsi okunamadı. Daha net bir fotoğraf dene.":
   "No pude leer todas las proteínas, carbohidratos y grasas. Prueba una foto más nítida.",
 "Okunan değerleri kontrol et, yanlışsa aşağıdan düzelt.":
   "Revisa los valores leídos y corrígelos abajo si hace falta.",
 "ya da galerinden bir fotoğraf seç": "o elige una foto de tu galería",
 "#### Favorilerin": "#### Tus favoritos", "#### Kaydettiklerin": "#### Tus alimentos guardados",
 "#### Son yedikleri": "#### Comido recientemente", "#### Önceki bir öğünü kopyala": "#### Copiar una comida anterior",
 "Henüz favorin yok. Bir yemek eklerken \"Favorilere ekle\" düğmesini kullan.":
   "Aún no tienes favoritos. Usa el botón \"Añadir a favoritos\" al registrar un alimento.",
 "Henüz kayıt yok.": "Todavía no hay registros.",
 "Kopyalanacak başka gün yok.": "No hay otro día para copiar.",
 "O gün o öğünde kayıt yok.": "No hay nada registrado en esa comida ese día.",
 "Yemeğin adı": "Nombre del alimento", "Yemeğin adını yaz.": "Escribe un nombre.",
 "Bir porsiyon kaç gram?": "¿Cuántos gramos tiene una ración?",
 "Protein (porsiyon başına, g)": "Proteína (por ración, g)",
 "Karbonhidrat (porsiyon başına, g)": "Carbohidratos (por ración, g)",
 "Yağ (porsiyon başına, g)": "Grasa (por ración, g)",
 "En az bir besin değeri gir.": "Introduce al menos un valor nutricional.",
 "Veritabanına bağlanılamadı, kaydedilemedi.": "No se pudo conectar con la base de datos; no se guardó nada.",
 "Antrenman koçu": "Entrenador", "Seviyen": "Tu nivel",
 "Elindeki ekipman (boşsa ekipmansız)": "Equipamiento disponible (vacío = sin equipo)",
 "Ağrı ya da sınırlaman var mı? (isteğe bağlı)": "¿Algún dolor o limitación? (opcional)",
 "Bu seçimlerle yeterli hareket yok. exercises.json dosyasına hareket ekle.":
   "No hay suficientes ejercicios para esas opciones. Añade más a exercises.json.",
 "exercises.json bulunamadı ya da boş.": "No se encuentra exercises.json o está vacío.",
 "Plan oluşturulamadı. Tekrar dene.": "No se pudo crear el plan. Inténtalo de nuevo.",
 "Video yakında eklenecek.": "Pronto habrá un vídeo.",
 "#### Antrenmanı kaydet": "#### Registrar el entrenamiento", "Antrenmanı kaydet": "Registrar entrenamiento",
 "Antrenman kaydedildi.": "Entrenamiento registrado.", "Tamamlanan set": "Series completadas",
 "Tekrarlar (örn. 12-10-8)": "Repeticiones (p. ej. 12-10-8)",
 "Hangi günü yaptın?": "¿Qué día entrenaste?",
 "Önce tamamladığın setleri gir.": "Introduce primero las series que hiciste.",
 "Hazır sorular": "Preguntas sugeridas", "Bir şey sor...": "Pregúntame algo...",
 "Sohbeti temizle": "Borrar la conversación",
 "Beslenme ve antrenman soruların için. Genel bilgi verir, tıbbi tavsiye değildir.":
   "Para tus dudas de nutrición y entrenamiento. Información general, no consejo médico.",
 "Öğün taraması": "Escaneo de comida",
 "Yemeğin fotoğrafını çek": "Haz una foto de tu comida",
 "Yemeğin fotoğrafını seç": "Elige una foto de tu comida",
 "Analiz et": "Analizar", "Not (isteğe bağlı)": "Nota (opcional)",
 "Örn: \"Kahvaltıda iki yumurta, bir dilim tam buğday ekmeği, yarım avuç ceviz ve şekersiz çay\"":
   "P. ej.: \"Dos huevos, una rebanada de pan integral, un puñado pequeño de nueces y té sin azúcar\"",
 "#### Değerleri düzenle": "#### Ajustar los valores",
 "Gramajı kaydırarak değiştir. Bir kalemi çıkarmak için 0'a çek.":
   "Desliza para cambiar los gramos. Ponlo a 0 para quitar un elemento.",
 "Tüm kalemler 0 gram. En az birini artır.": "Todos los elementos están a 0 g. Sube al menos uno.",
 "Bu kalemden emin değilim. Gramajı kontrol et.": "No estoy seguro de este elemento. Revisa los gramos.",
 "Değerler yapay zekanın tahminidir ve gerçek değerden sapabilir.":
   "Son estimaciones de la IA y pueden diferir de los valores reales.",
 "Referans değerlerle doğrula": "Comprobar con valores de referencia",
 "Fotoğraf ya da ses kaydı analiz için Google Gemini'ye gönderilir.":
   "La foto o la grabación se envía a Google Gemini para su análisis.",
 "Kaynak": "Fuente",
 "#### Hatırlatmalar": "#### Recordatorios", "#### Verilerin": "#### Tus datos",
 "#### Hesabını sil": "#### Eliminar tu cuenta",
 "Her akşam hatırlatma gönder": "Enviarme un recordatorio cada tarde",
 "Hatırlatma gönderimi henüz ayarlanmamış.": "Los recordatorios aún no están configurados.",
 "Telegram sohbet numaran": "Tu ID de chat de Telegram",
 "Deneme mesajı gönder": "Enviar mensaje de prueba", "Gönderildi, telefonuna bak.": "Enviado, mira tu teléfono.",
 "Verilerimi indir (JSON)": "Descargar mis datos (JSON)",
 "Nova'daki bütün verilerin senin. İstediğin zaman indirebilir ya da sildirebilirsin.":
   "Todos tus datos en Nova son tuyos. Puedes descargarlos o borrarlos cuando quieras.",
 "Hesabın ve bütün kayıtların kalıcı olarak silinir. Bu işlem geri alınamaz.":
   "Tu cuenta y todos tus registros se eliminan permanentemente. No se puede deshacer.",
 "Silmeden önce verilerini indirmeni öneririm. Silinen veriler geri getirilemez.":
   "Te recomiendo descargar tus datos antes. Los datos borrados no se recuperan.",
 "Hesabımı kalıcı olarak sil": "Eliminar mi cuenta permanentemente",
 "Kullanıcı adını tam olarak yazman gerekiyor.": "Tienes que escribir tu nombre de usuario exactamente.",
 "Şifreni gir": "Introduce tu contraseña", "Şifre yanlış.": "Contraseña incorrecta.",
 "Veritabanına bağlanılamadı, silme yapılamadı.": "No se pudo conectar con la base de datos; no se borró nada.",
 "Hesabın silindi. Nova'yı kullandığın için teşekkürler.":
   "Tu cuenta ha sido eliminada. Gracias por usar Nova.",
 "Kullanıcı adın ya da e-postan": "Tu usuario o tu correo",
 "Kod gönder": "Enviar código", "E-postana gelen 6 haneli kod": "El código de 6 dígitos de tu correo",
 "Kodu gir.": "Introduce el código.",
 "Yeni şifren (en az 8 karakter, bir büyük harf ve bir rakam)":
   "Tu nueva contraseña (mínimo 8 caracteres, una mayúscula y un número)",
 "Yeni şifren (tekrar)": "Nueva contraseña (otra vez)",
 "İki şifre birbirini tutmuyor.": "Las dos contraseñas no coinciden.",
 "Şifremi değiştir": "Cambiar mi contraseña",
 "Şifren değişti. Artık yeni şifrenle giriş yapabilirsin.":
   "Tu contraseña ha cambiado. Ya puedes entrar con ella.",
 "Vazgeç": "Cancelar",
},

"fr": {
 "#### Oturum": "#### Session",
 "#### Kalori": "#### Calories", "#### Kilo": "#### Poids",
 "#### Makro dağılımın": "#### Ta répartition de macros",
 "#### Öğünlere göre dağılım": "#### Répartition par repas",
 "#### Egzersiz ve aktivite": "#### Activité et entraînement",
 "Dönem": "Période", "Son 7 gün": "7 derniers jours", "Son 30 gün": "30 derniers jours",
 "Son 90 gün": "90 derniers jours",
 "90 günlük görünümde her çubuk bir haftanın ortalamasıdır.":
   "Dans la vue 90 jours, chaque barre est une moyenne hebdomadaire.",
 "Mavi kesikli çizgi günlük hedefin.": "La ligne bleue en pointillés est ton objectif quotidien.",
 "Mavi kesikli çizgi günde 10.000 adım hedefi.": "La ligne bleue en pointillés correspond à 10 000 pas.",
 "Bu dönemde öğün kaydın yok.": "Aucun repas enregistré sur cette période.",
 "Kilo kayıtlarında okunamayan bir tarih var.": "Une de tes pesées a une date illisible.",
 "Bu dosyayı diyetisyenine gönderebilirsin.": "Tu peux envoyer ce fichier à ton diététicien.",
 "Yemek ara": "Rechercher un aliment",
 "Aramak için en az iki harf yaz.": "Saisis au moins deux lettres pour chercher.",
 "Sonuçlar": "Résultats",
 "Marka ürünlerinde de ara (Open Food Facts)": "Chercher aussi les produits de marque (Open Food Facts)",
 "Marka ürünlerine şu an ulaşılamadı. Kendi veritabanındaki sonuçlar aşağıda.":
   "Les produits de marque sont indisponibles. Voici les résultats de ta propre base.",
 "Ürün veritabanına şu an ulaşılamadı. Biraz sonra tekrar dene.":
   "La base de produits est indisponible. Réessaie dans un instant.",
 "Bulamadım. \"Kendi yemeğim\" sekmesinden kendin ekleyebilirsin.":
   "Rien trouvé. Tu peux l'ajouter depuis l'onglet \"Mon propre aliment\".",
 "Yediğin miktar (gram)": "Quantité mangée (grammes)",
 "Günlüğe ekle": "Ajouter au journal", "Favorilere ekle": "Ajouter aux favoris",
 "Hangi öğün": "Quel repas", "Hangi gün": "Quel jour",
 "Ekle": "Ajouter", "Çıkar": "Retirer", "Tekrar ekle": "Ajouter à nouveau", "Nasıl?": "Comment ?",
 "Barkod numarası": "Numéro du code-barres",
 "Barkodu ortala ve çek": "Centre le code-barres et prends la photo",
 "Kamerayı aç": "Ouvrir la caméra", "Kamerayı kapat": "Fermer la caméra",
 "Kamera yalnızca bu düğmeye bastığında açılır.": "La caméra ne s'ouvre qu'en appuyant sur ce bouton.",
 "Paketin arkasındaki barkodu okut. Bulunamazsa besin değerleri tablosunun fotoğrafından okuyabilirim.":
   "Scanne le code au dos. S'il est introuvable, je peux lire le tableau nutritionnel sur une photo.",
 "Barkodu okuyamadım. Daha yakın, net ve düz çekmeyi dene ya da numarayı elle yaz.":
   "Je n'ai pas pu lire le code. Essaie plus près, plus net et bien droit, ou saisis le numéro.",
 "Bu numara geçerli bir barkod gibi görünmüyor. Rakamları kontrol et.":
   "Ce numéro ne ressemble pas à un code-barres valide. Vérifie les chiffres.",
 "Bu barkod veritabanında yok. Paketin besin değerleri tablosunu çekersen okuyabilirim.":
   "Ce code n'est pas dans la base. Photographie le tableau nutritionnel et je le lirai.",
 "Barkod okuyucu kurulu değil. requirements.txt dosyasına zxing-cpp ekle.":
   "Le lecteur de codes-barres n'est pas installé. Ajoute zxing-cpp à requirements.txt.",
 "Bunun yerine besin değerleri tablosunu oku": "Lire plutôt le tableau nutritionnel",
 "Etiketi oku": "Lire l'étiquette",
 "Besin değerleri tablosunun fotoğrafı": "Photo du tableau nutritionnel",
 "Etiketteki protein, karbonhidrat ve yağ değerlerinin hepsi okunamadı. Daha net bir fotoğraf dene.":
   "Je n'ai pas pu lire protéines, glucides et lipides en entier. Essaie une photo plus nette.",
 "Okunan değerleri kontrol et, yanlışsa aşağıdan düzelt.":
   "Vérifie les valeurs lues et corrige-les ci-dessous si besoin.",
 "ya da galerinden bir fotoğraf seç": "ou choisis une photo dans ta galerie",
 "#### Favorilerin": "#### Tes favoris", "#### Kaydettiklerin": "#### Tes aliments enregistrés",
 "#### Son yedikleri": "#### Mangé récemment", "#### Önceki bir öğünü kopyala": "#### Copier un repas précédent",
 "Henüz favorin yok. Bir yemek eklerken \"Favorilere ekle\" düğmesini kullan.":
   "Pas encore de favoris. Utilise le bouton \"Ajouter aux favoris\" en enregistrant un aliment.",
 "Henüz kayıt yok.": "Rien d'enregistré pour l'instant.",
 "Kopyalanacak başka gün yok.": "Il n'y a pas d'autre jour à copier.",
 "O gün o öğünde kayıt yok.": "Rien n'a été enregistré pour ce repas ce jour-là.",
 "Yemeğin adı": "Nom de l'aliment", "Yemeğin adını yaz.": "Saisis un nom.",
 "Bir porsiyon kaç gram?": "Combien de grammes pour une portion ?",
 "Protein (porsiyon başına, g)": "Protéines (par portion, g)",
 "Karbonhidrat (porsiyon başına, g)": "Glucides (par portion, g)",
 "Yağ (porsiyon başına, g)": "Lipides (par portion, g)",
 "En az bir besin değeri gir.": "Saisis au moins une valeur nutritionnelle.",
 "Veritabanına bağlanılamadı, kaydedilemedi.": "Base de données injoignable, rien n'a été enregistré.",
 "Antrenman koçu": "Coach d'entraînement", "Seviyen": "Ton niveau",
 "Elindeki ekipman (boşsa ekipmansız)": "Matériel disponible (vide = sans matériel)",
 "Ağrı ya da sınırlaman var mı? (isteğe bağlı)": "Une douleur ou une limitation ? (facultatif)",
 "Bu seçimlerle yeterli hareket yok. exercises.json dosyasına hareket ekle.":
   "Pas assez d'exercices pour ces choix. Ajoutes-en dans exercises.json.",
 "exercises.json bulunamadı ya da boş.": "exercises.json est introuvable ou vide.",
 "Plan oluşturulamadı. Tekrar dene.": "Impossible de créer le plan. Réessaie.",
 "Video yakında eklenecek.": "Une vidéo arrive bientôt.",
 "#### Antrenmanı kaydet": "#### Enregistrer la séance", "Antrenmanı kaydet": "Enregistrer la séance",
 "Antrenman kaydedildi.": "Séance enregistrée.", "Tamamlanan set": "Séries réalisées",
 "Tekrarlar (örn. 12-10-8)": "Répétitions (ex. 12-10-8)",
 "Hangi günü yaptın?": "Quel jour as-tu fait la séance ?",
 "Önce tamamladığın setleri gir.": "Saisis d'abord les séries réalisées.",
 "Hazır sorular": "Questions suggérées", "Bir şey sor...": "Pose-moi une question...",
 "Sohbeti temizle": "Effacer la conversation",
 "Beslenme ve antrenman soruların için. Genel bilgi verir, tıbbi tavsiye değildir.":
   "Pour tes questions de nutrition et d'entraînement. Informations générales, pas un avis médical.",
 "Öğün taraması": "Scan de repas",
 "Yemeğin fotoğrafını çek": "Prends une photo de ton repas",
 "Yemeğin fotoğrafını seç": "Choisis une photo de ton repas",
 "Analiz et": "Analyser", "Not (isteğe bağlı)": "Note (facultatif)",
 "Örn: \"Kahvaltıda iki yumurta, bir dilim tam buğday ekmeği, yarım avuç ceviz ve şekersiz çay\"":
   "Ex. : \"Deux œufs, une tranche de pain complet, une petite poignée de noix et un thé sans sucre\"",
 "#### Değerleri düzenle": "#### Ajuster les valeurs",
 "Gramajı kaydırarak değiştir. Bir kalemi çıkarmak için 0'a çek.":
   "Fais glisser pour changer les grammes. Mets à 0 pour retirer un élément.",
 "Tüm kalemler 0 gram. En az birini artır.": "Tous les éléments sont à 0 g. Augmentes-en au moins un.",
 "Bu kalemden emin değilim. Gramajı kontrol et.": "Je ne suis pas sûr de cet élément. Vérifie les grammes.",
 "Değerler yapay zekanın tahminidir ve gerçek değerden sapabilir.":
   "Ces valeurs sont des estimations de l'IA et peuvent différer du réel.",
 "Referans değerlerle doğrula": "Vérifier avec les valeurs de référence",
 "Fotoğraf ya da ses kaydı analiz için Google Gemini'ye gönderilir.":
   "La photo ou l'enregistrement est envoyé à Google Gemini pour analyse.",
 "Kaynak": "Source",
 "#### Hatırlatmalar": "#### Rappels", "#### Verilerin": "#### Tes données",
 "#### Hesabını sil": "#### Supprimer ton compte",
 "Her akşam hatırlatma gönder": "M'envoyer un rappel chaque soir",
 "Hatırlatma gönderimi henüz ayarlanmamış.": "Les rappels ne sont pas encore configurés.",
 "Telegram sohbet numaran": "Ton identifiant de discussion Telegram",
 "Deneme mesajı gönder": "Envoyer un message test", "Gönderildi, telefonuna bak.": "Envoyé, regarde ton téléphone.",
 "Verilerimi indir (JSON)": "Télécharger mes données (JSON)",
 "Nova'daki bütün verilerin senin. İstediğin zaman indirebilir ya da sildirebilirsin.":
   "Toutes tes données dans Nova t'appartiennent. Tu peux les télécharger ou les supprimer quand tu veux.",
 "Hesabın ve bütün kayıtların kalıcı olarak silinir. Bu işlem geri alınamaz.":
   "Ton compte et tous tes enregistrements sont supprimés définitivement. C'est irréversible.",
 "Silmeden önce verilerini indirmeni öneririm. Silinen veriler geri getirilemez.":
   "Télécharge tes données avant. Les données supprimées sont irrécupérables.",
 "Hesabımı kalıcı olarak sil": "Supprimer définitivement mon compte",
 "Kullanıcı adını tam olarak yazman gerekiyor.": "Tu dois saisir ton nom d'utilisateur exactement.",
 "Şifreni gir": "Saisis ton mot de passe", "Şifre yanlış.": "Mot de passe incorrect.",
 "Veritabanına bağlanılamadı, silme yapılamadı.": "Base de données injoignable, rien n'a été supprimé.",
 "Hesabın silindi. Nova'yı kullandığın için teşekkürler.":
   "Ton compte a été supprimé. Merci d'avoir utilisé Nova.",
 "Kullanıcı adın ya da e-postan": "Ton nom d'utilisateur ou ton e-mail",
 "Kod gönder": "Envoyer le code", "E-postana gelen 6 haneli kod": "Le code à 6 chiffres reçu par e-mail",
 "Kodu gir.": "Saisis le code.",
 "Yeni şifren (en az 8 karakter, bir büyük harf ve bir rakam)":
   "Ton nouveau mot de passe (au moins 8 caractères, une majuscule et un chiffre)",
 "Yeni şifren (tekrar)": "Nouveau mot de passe (à nouveau)",
 "İki şifre birbirini tutmuyor.": "Les deux mots de passe ne correspondent pas.",
 "Şifremi değiştir": "Changer mon mot de passe",
 "Şifren değişti. Artık yeni şifrenle giriş yapabilirsin.":
   "Ton mot de passe a été changé. Tu peux maintenant t'en servir pour te connecter.",
 "Vazgeç": "Annuler",
},

"ar": {
 "#### Oturum": "#### الجلسة",
 "#### Kalori": "#### السعرات", "#### Kilo": "#### الوزن",
 "#### Makro dağılımın": "#### توزيع العناصر الكبرى",
 "#### Öğünlere göre dağılım": "#### التوزيع حسب الوجبة",
 "#### Egzersiz ve aktivite": "#### التمارين والنشاط",
 "Dönem": "الفترة", "Son 7 gün": "آخر ٧ أيام", "Son 30 gün": "آخر ٣٠ يومًا",
 "Son 90 gün": "آخر ٩٠ يومًا",
 "90 günlük görünümde her çubuk bir haftanın ortalamasıdır.":
   "في عرض ٩٠ يومًا، كل عمود هو متوسط أسبوع.",
 "Mavi kesikli çizgi günlük hedefin.": "الخط الأزرق المتقطع هو هدفك اليومي.",
 "Mavi kesikli çizgi günde 10.000 adım hedefi.": "الخط الأزرق المتقطع هو هدف ١٠٬٠٠٠ خطوة.",
 "Bu dönemde öğün kaydın yok.": "لا توجد وجبات مسجلة في هذه الفترة.",
 "Kilo kayıtlarında okunamayan bir tarih var.": "أحد سجلات وزنك يحمل تاريخًا غير مقروء.",
 "Bu dosyayı diyetisyenine gönderebilirsin.": "يمكنك إرسال هذا الملف إلى أخصائي التغذية.",
 "Yemek ara": "ابحث عن طعام",
 "Aramak için en az iki harf yaz.": "اكتب حرفين على الأقل للبحث.",
 "Sonuçlar": "النتائج",
 "Marka ürünlerinde de ara (Open Food Facts)": "ابحث أيضًا في المنتجات التجارية (Open Food Facts)",
 "Marka ürünlerine şu an ulaşılamadı. Kendi veritabanındaki sonuçlar aşağıda.":
   "المنتجات التجارية غير متاحة الآن. النتائج من قاعدة بياناتك في الأسفل.",
 "Ürün veritabanına şu an ulaşılamadı. Biraz sonra tekrar dene.":
   "قاعدة بيانات المنتجات غير متاحة الآن. حاول بعد قليل.",
 "Bulamadım. \"Kendi yemeğim\" sekmesinden kendin ekleyebilirsin.":
   "لم أجده. يمكنك إضافته من تبويب \"طعامي الخاص\".",
 "Yediğin miktar (gram)": "الكمية التي أكلتها (غرام)",
 "Günlüğe ekle": "أضف إلى اليوميات", "Favorilere ekle": "أضف إلى المفضلة",
 "Hangi öğün": "أي وجبة", "Hangi gün": "أي يوم",
 "Ekle": "إضافة", "Çıkar": "إزالة", "Tekrar ekle": "أضف مرة أخرى", "Nasıl?": "كيف؟",
 "Barkod numarası": "رقم الباركود",
 "Barkodu ortala ve çek": "ضع الباركود في المنتصف والتقط الصورة",
 "Kamerayı aç": "فتح الكاميرا", "Kamerayı kapat": "إغلاق الكاميرا",
 "Kamera yalnızca bu düğmeye bastığında açılır.": "لا تُفتح الكاميرا إلا عند الضغط على هذا الزر.",
 "Paketin arkasındaki barkodu okut. Bulunamazsa besin değerleri tablosunun fotoğrafından okuyabilirim.":
   "امسح الباركود خلف العبوة. إن لم يُعثر عليه، يمكنني قراءة جدول القيم الغذائية من صورة.",
 "Barkodu okuyamadım. Daha yakın, net ve düz çekmeyi dene ya da numarayı elle yaz.":
   "لم أتمكن من قراءة الباركود. جرّب من مسافة أقرب وأوضح ومستقيمة، أو اكتب الرقم يدويًا.",
 "Bu numara geçerli bir barkod gibi görünmüyor. Rakamları kontrol et.":
   "هذا الرقم لا يبدو باركودًا صالحًا. تحقق من الأرقام.",
 "Bu barkod veritabanında yok. Paketin besin değerleri tablosunu çekersen okuyabilirim.":
   "هذا الباركود غير موجود في قاعدة البيانات. صوّر جدول القيم الغذائية وسأقرؤه.",
 "Barkod okuyucu kurulu değil. requirements.txt dosyasına zxing-cpp ekle.":
   "قارئ الباركود غير مثبّت. أضف zxing-cpp إلى ملف requirements.txt.",
 "Bunun yerine besin değerleri tablosunu oku": "اقرأ جدول القيم الغذائية بدلًا من ذلك",
 "Etiketi oku": "اقرأ الملصق",
 "Besin değerleri tablosunun fotoğrafı": "صورة جدول القيم الغذائية",
 "Etiketteki protein, karbonhidrat ve yağ değerlerinin hepsi okunamadı. Daha net bir fotoğraf dene.":
   "لم أتمكن من قراءة البروتين والكربوهيدرات والدهون كاملة. جرّب صورة أوضح.",
 "Okunan değerleri kontrol et, yanlışsa aşağıdan düzelt.":
   "تحقق من القيم المقروءة وصححها في الأسفل إن لزم.",
 "ya da galerinden bir fotoğraf seç": "أو اختر صورة من معرضك",
 "#### Favorilerin": "#### مفضلاتك", "#### Kaydettiklerin": "#### أطعمتك المحفوظة",
 "#### Son yedikleri": "#### أُكل مؤخرًا", "#### Önceki bir öğünü kopyala": "#### انسخ وجبة سابقة",
 "Henüz favorin yok. Bir yemek eklerken \"Favorilere ekle\" düğmesini kullan.":
   "لا توجد مفضلات بعد. استخدم زر \"أضف إلى المفضلة\" عند تسجيل طعام.",
 "Henüz kayıt yok.": "لا توجد سجلات بعد.",
 "Kopyalanacak başka gün yok.": "لا يوجد يوم آخر للنسخ منه.",
 "O gün o öğünde kayıt yok.": "لم يُسجَّل شيء لتلك الوجبة في ذلك اليوم.",
 "Yemeğin adı": "اسم الطعام", "Yemeğin adını yaz.": "اكتب اسمًا للطعام.",
 "Bir porsiyon kaç gram?": "كم غرامًا في الحصة الواحدة؟",
 "Protein (porsiyon başına, g)": "البروتين (لكل حصة، غ)",
 "Karbonhidrat (porsiyon başına, g)": "الكربوهيدرات (لكل حصة، غ)",
 "Yağ (porsiyon başına, g)": "الدهون (لكل حصة، غ)",
 "En az bir besin değeri gir.": "أدخل قيمة غذائية واحدة على الأقل.",
 "Veritabanına bağlanılamadı, kaydedilemedi.": "تعذّر الاتصال بقاعدة البيانات، لم يُحفظ شيء.",
 "Antrenman koçu": "مدرب التمارين", "Seviyen": "مستواك",
 "Elindeki ekipman (boşsa ekipmansız)": "المعدات المتوفرة (اتركها فارغة إن لم توجد)",
 "Ağrı ya da sınırlaman var mı? (isteğe bağlı)": "هل لديك ألم أو قيد؟ (اختياري)",
 "Bu seçimlerle yeterli hareket yok. exercises.json dosyasına hareket ekle.":
   "لا توجد تمارين كافية لهذه الخيارات. أضف المزيد إلى ملف exercises.json.",
 "exercises.json bulunamadı ya da boş.": "ملف exercises.json غير موجود أو فارغ.",
 "Plan oluşturulamadı. Tekrar dene.": "تعذّر إنشاء الخطة. حاول مرة أخرى.",
 "Video yakında eklenecek.": "سيُضاف فيديو قريبًا.",
 "#### Antrenmanı kaydet": "#### سجّل تمرينك", "Antrenmanı kaydet": "سجّل التمرين",
 "Antrenman kaydedildi.": "تم تسجيل التمرين.", "Tamamlanan set": "المجموعات المكتملة",
 "Tekrarlar (örn. 12-10-8)": "التكرارات (مثال ١٢-١٠-٨)",
 "Hangi günü yaptın?": "في أي يوم تمرّنت؟",
 "Önce tamamladığın setleri gir.": "أدخل أولًا المجموعات التي أكملتها.",
 "Hazır sorular": "أسئلة مقترحة", "Bir şey sor...": "اسألني شيئًا...",
 "Sohbeti temizle": "مسح المحادثة",
 "Beslenme ve antrenman soruların için. Genel bilgi verir, tıbbi tavsiye değildir.":
   "لأسئلتك عن التغذية والتمارين. معلومات عامة وليست نصيحة طبية.",
 "Öğün taraması": "مسح الوجبة",
 "Yemeğin fotoğrafını çek": "التقط صورة لوجبتك",
 "Yemeğin fotoğrafını seç": "اختر صورة لوجبتك",
 "Analiz et": "حلّل", "Not (isteğe bağlı)": "ملاحظة (اختياري)",
 "Örn: \"Kahvaltıda iki yumurta, bir dilim tam buğday ekmeği, yarım avuç ceviz ve şekersiz çay\"":
   "مثال: \"بيضتان وشريحة خبز قمح كامل وحفنة صغيرة من الجوز وشاي بلا سكر\"",
 "#### Değerleri düzenle": "#### عدّل القيم",
 "Gramajı kaydırarak değiştir. Bir kalemi çıkarmak için 0'a çek.":
   "اسحب لتغيير الغرامات. اجعلها صفرًا لإزالة عنصر.",
 "Tüm kalemler 0 gram. En az birini artır.": "كل العناصر صفر غرام. ارفع واحدًا على الأقل.",
 "Bu kalemden emin değilim. Gramajı kontrol et.": "لست واثقًا من هذا العنصر. تحقق من الغرامات.",
 "Değerler yapay zekanın tahminidir ve gerçek değerden sapabilir.":
   "هذه القيم تقديرات من الذكاء الاصطناعي وقد تختلف عن الواقع.",
 "Referans değerlerle doğrula": "قارن بالقيم المرجعية",
 "Fotoğraf ya da ses kaydı analiz için Google Gemini'ye gönderilir.":
   "تُرسل الصورة أو التسجيل الصوتي إلى Google Gemini للتحليل.",
 "Kaynak": "المصدر",
 "#### Hatırlatmalar": "#### التذكيرات", "#### Verilerin": "#### بياناتك",
 "#### Hesabını sil": "#### حذف حسابك",
 "Her akşam hatırlatma gönder": "أرسل لي تذكيرًا كل مساء",
 "Hatırlatma gönderimi henüz ayarlanmamış.": "لم تُضبط التذكيرات بعد.",
 "Telegram sohbet numaran": "رقم محادثتك في تيليجرام",
 "Deneme mesajı gönder": "إرسال رسالة تجريبية", "Gönderildi, telefonuna bak.": "أُرسلت، تفقّد هاتفك.",
 "Verilerimi indir (JSON)": "تنزيل بياناتي (JSON)",
 "Nova'daki bütün verilerin senin. İstediğin zaman indirebilir ya da sildirebilirsin.":
   "كل بياناتك في Nova ملك لك. يمكنك تنزيلها أو حذفها متى شئت.",
 "Hesabın ve bütün kayıtların kalıcı olarak silinir. Bu işlem geri alınamaz.":
   "سيُحذف حسابك وكل سجلاتك نهائيًا. لا يمكن التراجع عن ذلك.",
 "Silmeden önce verilerini indirmeni öneririm. Silinen veriler geri getirilemez.":
   "أنصحك بتنزيل بياناتك أولًا. البيانات المحذوفة لا تُستعاد.",
 "Hesabımı kalıcı olarak sil": "احذف حسابي نهائيًا",
 "Kullanıcı adını tam olarak yazman gerekiyor.": "عليك كتابة اسم المستخدم بالضبط.",
 "Şifreni gir": "أدخل كلمة المرور", "Şifre yanlış.": "كلمة المرور خاطئة.",
 "Veritabanına bağlanılamadı, silme yapılamadı.": "تعذّر الاتصال بقاعدة البيانات، لم يُحذف شيء.",
 "Hesabın silindi. Nova'yı kullandığın için teşekkürler.":
   "حُذف حسابك. شكرًا لاستخدامك Nova.",
 "Kullanıcı adın ya da e-postan": "اسم المستخدم أو بريدك الإلكتروني",
 "Kod gönder": "إرسال الرمز", "E-postana gelen 6 haneli kod": "الرمز المكوّن من ٦ أرقام المرسل إلى بريدك",
 "Kodu gir.": "أدخل الرمز.",
 "Yeni şifren (en az 8 karakter, bir büyük harf ve bir rakam)":
   "كلمة المرور الجديدة (٨ أحرف على الأقل، حرف كبير ورقم)",
 "Yeni şifren (tekrar)": "كلمة المرور الجديدة (مرة أخرى)",
 "İki şifre birbirini tutmuyor.": "كلمتا المرور غير متطابقتين.",
 "Şifremi değiştir": "تغيير كلمة المرور",
 "Şifren değişti. Artık yeni şifrenle giriş yapabilirsin.":
   "تم تغيير كلمة المرور. يمكنك الآن الدخول بها.",
 "Vazgeç": "إلغاء",
},
}

# Mikro besinler
EK_MIKRO = {'en': {'#### Vitamin ve mineraller': '#### Vitamins and minerals', 'Vitamin ve Mineraller': 'Vitamins and minerals', 'Lif': 'Fibre', 'Şeker': 'Sugar', 'Doymuş yağ': 'Saturated fat', 'Tuz': 'Salt', 'Demir': 'Iron', 'Kalsiyum': 'Calcium', 'Magnezyum': 'Magnesium', 'Çinko': 'Zinc', 'Potasyum': 'Potassium', 'C vitamini': 'Vitamin C', 'D vitamini': 'Vitamin D', 'B12 vitamini': 'Vitamin B12', 'Veri bulunan': 'Average over the', 'günün ortalaması.': 'days that have data.', 'Sürekli geride kaldıkların:': 'Consistently below target:', 'günlük sınırını aştın.': 'is over its daily limit.', 'kalemden': 'items,', 'tanesinde vitamin ve mineral verisi var. Bu veriler barkodlu ürünlerde ve etiket okumada geliyor, ev yemeklerinde gelmiyor.': 'have vitamin and mineral data. This data comes from barcoded products and label scans, not from home-cooked dishes.', 'Bu dönemde vitamin ve mineral verisi olan kayıt yok. Bu veriler barkodlu ürünlerde ve etiket okumada geliyor.': 'No entries with vitamin and mineral data in this period. That data comes from barcoded products and label scans.'}, 'de': {'#### Vitamin ve mineraller': '#### Vitamine und Mineralstoffe', 'Vitamin ve Mineraller': 'Vitamine und Mineralstoffe', 'Lif': 'Ballaststoffe', 'Şeker': 'Zucker', 'Doymuş yağ': 'Gesättigte Fettsäuren', 'Tuz': 'Salz', 'Demir': 'Eisen', 'Kalsiyum': 'Kalzium', 'Magnezyum': 'Magnesium', 'Çinko': 'Zink', 'Potasyum': 'Kalium', 'C vitamini': 'Vitamin C', 'D vitamini': 'Vitamin D', 'B12 vitamini': 'Vitamin B12', 'Veri bulunan': 'Durchschnitt über die', 'günün ortalaması.': 'Tage mit Daten.', 'Sürekli geride kaldıkların:': 'Dauerhaft unter dem Ziel:', 'günlük sınırını aştın.': 'liegt über dem Tageslimit.', 'kalemden': 'Posten haben', 'tanesinde vitamin ve mineral verisi var. Bu veriler barkodlu ürünlerde ve etiket okumada geliyor, ev yemeklerinde gelmiyor.': 'Vitamin- und Mineralstoffdaten. Diese Daten stammen aus Barcode-Produkten und Etiketten, nicht aus selbst gekochten Gerichten.', 'Bu dönemde vitamin ve mineral verisi olan kayıt yok. Bu veriler barkodlu ürünlerde ve etiket okumada geliyor.': 'In diesem Zeitraum gibt es keine Einträge mit Vitamin- und Mineralstoffdaten. Diese stammen aus Barcode-Produkten und Etiketten.'}, 'es': {'#### Vitamin ve mineraller': '#### Vitaminas y minerales', 'Vitamin ve Mineraller': 'Vitaminas y minerales', 'Lif': 'Fibra', 'Şeker': 'Azúcar', 'Doymuş yağ': 'Grasas saturadas', 'Tuz': 'Sal', 'Demir': 'Hierro', 'Kalsiyum': 'Calcio', 'Magnezyum': 'Magnesio', 'Çinko': 'Zinc', 'Potasyum': 'Potasio', 'C vitamini': 'Vitamina C', 'D vitamini': 'Vitamina D', 'B12 vitamini': 'Vitamina B12', 'Veri bulunan': 'Media de los', 'günün ortalaması.': 'días con datos.', 'Sürekli geride kaldıkların:': 'Siempre por debajo del objetivo:', 'günlük sınırını aştın.': 'supera su límite diario.', 'kalemden': 'elementos,', 'tanesinde vitamin ve mineral verisi var. Bu veriler barkodlu ürünlerde ve etiket okumada geliyor, ev yemeklerinde gelmiyor.': 'tienen datos de vitaminas y minerales. Estos datos vienen de productos con código de barras y de etiquetas, no de platos caseros.', 'Bu dönemde vitamin ve mineral verisi olan kayıt yok. Bu veriler barkodlu ürünlerde ve etiket okumada geliyor.': 'No hay registros con datos de vitaminas y minerales en este periodo. Esos datos vienen de productos con código de barras y de etiquetas.'}, 'fr': {'#### Vitamin ve mineraller': '#### Vitamines et minéraux', 'Vitamin ve Mineraller': 'Vitamines et minéraux', 'Lif': 'Fibres', 'Şeker': 'Sucres', 'Doymuş yağ': 'Acides gras saturés', 'Tuz': 'Sel', 'Demir': 'Fer', 'Kalsiyum': 'Calcium', 'Magnezyum': 'Magnésium', 'Çinko': 'Zinc', 'Potasyum': 'Potassium', 'C vitamini': 'Vitamine C', 'D vitamini': 'Vitamine D', 'B12 vitamini': 'Vitamine B12', 'Veri bulunan': 'Moyenne sur les', 'günün ortalaması.': 'jours avec données.', 'Sürekli geride kaldıkların:': "Toujours en dessous de l'objectif :", 'günlük sınırını aştın.': 'dépasse sa limite quotidienne.', 'kalemden': 'éléments,', 'tanesinde vitamin ve mineral verisi var. Bu veriler barkodlu ürünlerde ve etiket okumada geliyor, ev yemeklerinde gelmiyor.': 'ont des données de vitamines et minéraux. Ces données viennent des produits à code-barres et des étiquettes, pas des plats maison.', 'Bu dönemde vitamin ve mineral verisi olan kayıt yok. Bu veriler barkodlu ürünlerde ve etiket okumada geliyor.': 'Aucune entrée avec des données de vitamines et minéraux sur cette période. Ces données viennent des produits à code-barres et des étiquettes.'}, 'ar': {'#### Vitamin ve mineraller': '#### الفيتامينات والمعادن', 'Vitamin ve Mineraller': 'الفيتامينات والمعادن', 'Lif': 'الألياف', 'Şeker': 'السكر', 'Doymuş yağ': 'الدهون المشبعة', 'Tuz': 'الملح', 'Demir': 'الحديد', 'Kalsiyum': 'الكالسيوم', 'Magnezyum': 'المغنيسيوم', 'Çinko': 'الزنك', 'Potasyum': 'البوتاسيوم', 'C vitamini': 'فيتامين C', 'D vitamini': 'فيتامين D', 'B12 vitamini': 'فيتامين B12', 'Veri bulunan': 'متوسط', 'günün ortalaması.': 'يومًا تحتوي على بيانات.', 'Sürekli geride kaldıkların:': 'أقل من الهدف باستمرار:', 'günlük sınırını aştın.': 'تجاوز حدّه اليومي.', 'kalemden': 'عنصرًا،', 'tanesinde vitamin ve mineral verisi var. Bu veriler barkodlu ürünlerde ve etiket okumada geliyor, ev yemeklerinde gelmiyor.': 'منها يحتوي على بيانات الفيتامينات والمعادن. تأتي هذه البيانات من المنتجات ذات الباركود ومن الملصقات، لا من الأطباق المنزلية.', 'Bu dönemde vitamin ve mineral verisi olan kayıt yok. Bu veriler barkodlu ürünlerde ve etiket okumada geliyor.': 'لا توجد سجلات بها بيانات فيتامينات ومعادن في هذه الفترة. تأتي هذه البيانات من المنتجات ذات الباركود ومن الملصقات.'}}
for _k, _v in EK_MIKRO.items():
    EK.setdefault(_k, {}).update(_v)

# Grafik eksen ve ipucu etiketleri
EK_GRAFIK = {'en': {'Tarih': 'Date', 'Alınan kcal': 'kcal eaten', 'Kalem': 'Items', 'Hafta başı': 'Week of', 'Ortalama kcal': 'Average kcal', 'kg': 'kg', '7 günlük ortalama': '7-day average', 'gram (günlük ortalama)': 'grams (daily average)', 'günlük ortalama kcal': 'daily average kcal'}, 'de': {'Tarih': 'Datum', 'Alınan kcal': 'Aufgenommene kcal', 'Kalem': 'Posten', 'Hafta başı': 'Woche ab', 'Ortalama kcal': 'Durchschnitt kcal', 'kg': 'kg', '7 günlük ortalama': '7-Tage-Durchschnitt', 'gram (günlük ortalama)': 'Gramm (Tagesdurchschnitt)', 'günlük ortalama kcal': 'kcal im Tagesdurchschnitt'}, 'es': {'Tarih': 'Fecha', 'Alınan kcal': 'kcal consumidas', 'Kalem': 'Elementos', 'Hafta başı': 'Semana del', 'Ortalama kcal': 'kcal media', 'kg': 'kg', '7 günlük ortalama': 'media de 7 días', 'gram (günlük ortalama)': 'gramos (media diaria)', 'günlük ortalama kcal': 'kcal media diaria'}, 'fr': {'Tarih': 'Date', 'Alınan kcal': 'kcal consommées', 'Kalem': 'Éléments', 'Hafta başı': 'Semaine du', 'Ortalama kcal': 'kcal moyennes', 'kg': 'kg', '7 günlük ortalama': 'moyenne sur 7 jours', 'gram (günlük ortalama)': 'grammes (moyenne par jour)', 'günlük ortalama kcal': 'kcal moyennes par jour'}, 'ar': {'Tarih': 'التاريخ', 'Alınan kcal': 'السعرات المتناولة', 'Kalem': 'العناصر', 'Hafta başı': 'أسبوع', 'Ortalama kcal': 'متوسط السعرات', 'kg': 'كغ', '7 günlük ortalama': 'متوسط ٧ أيام', 'gram (günlük ortalama)': 'غرام (المتوسط اليومي)', 'günlük ortalama kcal': 'متوسط السعرات اليومي'}}
for _k, _v in EK_GRAFIK.items():
    EK.setdefault(_k, {}).update(_v)

# Tarif olusturucu
EK_TARIF = {'en': {'Ara': 'Search', 'Barkod': 'Barcode', 'Tarif': 'Recipe', 'Favoriler': 'Favourites', 'Kendi yemeğim': 'My own food', 'Malzeme ara': 'Search for an ingredient', 'Tarifin': 'Your recipe', 'Tarifin adı': 'Recipe name', 'Tarifin adını yaz.': 'Enter a name for the recipe.', 'Tarifi kaydet': 'Save recipe', 'Tarifi temizle': 'Clear recipe', 'Bugüne ekle': 'Add to today', 'Bu tarif kaç porsiyon?': 'How many portions does this make?', 'Bir porsiyon': 'One portion', 'Toplam': 'Total', 'gram': 'grams', 'Henüz malzeme eklemedin. Yukarıdan arayıp ekle.': 'No ingredients yet. Search above and add some.', 'Marka ürünlerine şu an ulaşılamadı.': 'Branded products are unreachable right now.', 'kaydedildi. Artık aramada çıkacak.': 'saved. It will now show up in search.', 'Örn: Hamburger menü': 'e.g. Burger meal', 'Örn: hamburger ekmeği, dana köfte, patates kızartması': 'e.g. burger bun, beef patty, fries', 'Birden çok parçadan oluşan bir öğünü tek seferde kur. Örnek: hamburger menü için ekmek, köfte, peynir, patates ve içecek ekle; sonra tarifi kaydet, bir daha tek tek eklemen gerekmesin.': 'Build a meal that has several parts in one go. For a burger meal, add the bun, patty, cheese, fries and drink, then save the recipe so you never have to add them one by one again.', 'Bulamadım. "Kendi yemeğim" sekmesinden ekleyip buraya malzeme olarak koyabilirsin.': 'No match. Add it from the "My own food" tab and then use it here as an ingredient.', 'Tek kişilik bir menü için 1 bırak. Dört kişilik bir tencere yemeği pişirdiysen 4 yaz; Nova porsiyon başı değeri kendi hesaplar.': 'Leave it at 1 for a single meal. If you cooked a pot for four, enter 4 and Nova works out the per-portion values.'}, 'de': {'Ara': 'Suchen', 'Barkod': 'Barcode', 'Tarif': 'Rezept', 'Favoriler': 'Favoriten', 'Kendi yemeğim': 'Mein eigenes Essen', 'Malzeme ara': 'Zutat suchen', 'Tarifin': 'Dein Rezept', 'Tarifin adı': 'Name des Rezepts', 'Tarifin adını yaz.': 'Gib dem Rezept einen Namen.', 'Tarifi kaydet': 'Rezept speichern', 'Tarifi temizle': 'Rezept leeren', 'Bugüne ekle': 'Zu heute hinzufügen', 'Bu tarif kaç porsiyon?': 'Wie viele Portionen ergibt das?', 'Bir porsiyon': 'Eine Portion', 'Toplam': 'Gesamt', 'gram': 'Gramm', 'Henüz malzeme eklemedin. Yukarıdan arayıp ekle.': 'Noch keine Zutaten. Such oben und füge welche hinzu.', 'Marka ürünlerine şu an ulaşılamadı.': 'Markenprodukte sind gerade nicht erreichbar.', 'kaydedildi. Artık aramada çıkacak.': 'gespeichert. Es erscheint jetzt in der Suche.', 'Örn: Hamburger menü': 'z. B. Burger-Menü', 'Örn: hamburger ekmeği, dana köfte, patates kızartması': 'z. B. Burgerbrötchen, Rinderpatty, Pommes', 'Birden çok parçadan oluşan bir öğünü tek seferde kur. Örnek: hamburger menü için ekmek, köfte, peynir, patates ve içecek ekle; sonra tarifi kaydet, bir daha tek tek eklemen gerekmesin.': 'Stell eine mehrteilige Mahlzeit auf einmal zusammen. Für ein Burger-Menü: Brötchen, Patty, Käse, Pommes und Getränk hinzufügen, dann das Rezept speichern und nie wieder einzeln erfassen.', 'Bulamadım. "Kendi yemeğim" sekmesinden ekleyip buraya malzeme olarak koyabilirsin.': 'Nichts gefunden. Lege es im Tab "Mein eigenes Essen" an und nutze es hier als Zutat.', 'Tek kişilik bir menü için 1 bırak. Dört kişilik bir tencere yemeği pişirdiysen 4 yaz; Nova porsiyon başı değeri kendi hesaplar.': 'Für eine einzelne Mahlzeit 1 lassen. Hast du für vier gekocht, trag 4 ein; Nova rechnet die Werte pro Portion aus.'}, 'es': {'Ara': 'Buscar', 'Barkod': 'Código de barras', 'Tarif': 'Receta', 'Favoriler': 'Favoritos', 'Kendi yemeğim': 'Mi propio alimento', 'Malzeme ara': 'Buscar un ingrediente', 'Tarifin': 'Tu receta', 'Tarifin adı': 'Nombre de la receta', 'Tarifin adını yaz.': 'Escribe un nombre para la receta.', 'Tarifi kaydet': 'Guardar receta', 'Tarifi temizle': 'Vaciar receta', 'Bugüne ekle': 'Añadir a hoy', 'Bu tarif kaç porsiyon?': '¿Cuántas raciones salen?', 'Bir porsiyon': 'Una ración', 'Toplam': 'Total', 'gram': 'gramos', 'Henüz malzeme eklemedin. Yukarıdan arayıp ekle.': 'Aún no hay ingredientes. Búscalos arriba y añádelos.', 'Marka ürünlerine şu an ulaşılamadı.': 'Los productos de marca no están disponibles ahora.', 'kaydedildi. Artık aramada çıkacak.': 'guardada. Ya aparecerá en la búsqueda.', 'Örn: Hamburger menü': 'P. ej.: menú de hamburguesa', 'Örn: hamburger ekmeği, dana köfte, patates kızartması': 'P. ej.: pan de hamburguesa, carne de ternera, patatas fritas', 'Birden çok parçadan oluşan bir öğünü tek seferde kur. Örnek: hamburger menü için ekmek, köfte, peynir, patates ve içecek ekle; sonra tarifi kaydet, bir daha tek tek eklemen gerekmesin.': 'Monta de una vez una comida con varias partes. Para un menú de hamburguesa añade el pan, la carne, el queso, las patatas y la bebida; guarda la receta y no tendrás que añadirlos uno a uno nunca más.', 'Bulamadım. "Kendi yemeğim" sekmesinden ekleyip buraya malzeme olarak koyabilirsin.': 'No lo encuentro. Añádelo en la pestaña "Mi propio alimento" y úsalo aquí como ingrediente.', 'Tek kişilik bir menü için 1 bırak. Dört kişilik bir tencere yemeği pişirdiysen 4 yaz; Nova porsiyon başı değeri kendi hesaplar.': 'Deja 1 para una comida individual. Si cocinaste para cuatro, pon 4 y Nova calcula los valores por ración.'}, 'fr': {'Ara': 'Rechercher', 'Barkod': 'Code-barres', 'Tarif': 'Recette', 'Favoriler': 'Favoris', 'Kendi yemeğim': 'Mon propre aliment', 'Malzeme ara': 'Rechercher un ingrédient', 'Tarifin': 'Ta recette', 'Tarifin adı': 'Nom de la recette', 'Tarifin adını yaz.': 'Donne un nom à la recette.', 'Tarifi kaydet': 'Enregistrer la recette', 'Tarifi temizle': 'Vider la recette', 'Bugüne ekle': "Ajouter à aujourd'hui", 'Bu tarif kaç porsiyon?': 'Combien de portions ?', 'Bir porsiyon': 'Une portion', 'Toplam': 'Total', 'gram': 'grammes', 'Henüz malzeme eklemedin. Yukarıdan arayıp ekle.': "Pas encore d'ingrédients. Cherche ci-dessus et ajoute-les.", 'Marka ürünlerine şu an ulaşılamadı.': 'Les produits de marque sont indisponibles.', 'kaydedildi. Artık aramada çıkacak.': 'enregistrée. Elle apparaîtra désormais dans la recherche.', 'Örn: Hamburger menü': 'Ex. : menu burger', 'Örn: hamburger ekmeği, dana köfte, patates kızartması': 'Ex. : pain à burger, steak haché, frites', 'Birden çok parçadan oluşan bir öğünü tek seferde kur. Örnek: hamburger menü için ekmek, köfte, peynir, patates ve içecek ekle; sonra tarifi kaydet, bir daha tek tek eklemen gerekmesin.': 'Compose en une fois un repas en plusieurs parties. Pour un menu burger, ajoute le pain, le steak, le fromage, les frites et la boisson, puis enregistre la recette : plus besoin de tout ressaisir.', 'Bulamadım. "Kendi yemeğim" sekmesinden ekleyip buraya malzeme olarak koyabilirsin.': "Rien trouvé. Ajoute-le depuis l'onglet « Mon propre aliment » puis utilise-le ici comme ingrédient.", 'Tek kişilik bir menü için 1 bırak. Dört kişilik bir tencere yemeği pişirdiysen 4 yaz; Nova porsiyon başı değeri kendi hesaplar.': 'Laisse 1 pour un repas individuel. Si tu as cuisiné pour quatre, mets 4 : Nova calcule les valeurs par portion.'}, 'ar': {'Ara': 'بحث', 'Barkod': 'الباركود', 'Tarif': 'وصفة', 'Favoriler': 'المفضلة', 'Kendi yemeğim': 'طعامي الخاص', 'Malzeme ara': 'ابحث عن مكوّن', 'Tarifin': 'وصفتك', 'Tarifin adı': 'اسم الوصفة', 'Tarifin adını yaz.': 'اكتب اسمًا للوصفة.', 'Tarifi kaydet': 'حفظ الوصفة', 'Tarifi temizle': 'إفراغ الوصفة', 'Bugüne ekle': 'أضف إلى اليوم', 'Bu tarif kaç porsiyon?': 'كم حصة تعطي هذه الوصفة؟', 'Bir porsiyon': 'حصة واحدة', 'Toplam': 'الإجمالي', 'gram': 'غرام', 'Henüz malzeme eklemedin. Yukarıdan arayıp ekle.': 'لم تضف مكوّنات بعد. ابحث في الأعلى وأضفها.', 'Marka ürünlerine şu an ulaşılamadı.': 'المنتجات التجارية غير متاحة الآن.', 'kaydedildi. Artık aramada çıkacak.': 'حُفظت. ستظهر الآن في البحث.', 'Örn: Hamburger menü': 'مثال: وجبة برجر', 'Örn: hamburger ekmeği, dana köfte, patates kızartması': 'مثال: خبز البرجر، قطعة لحم بقري، بطاطس مقلية', 'Birden çok parçadan oluşan bir öğünü tek seferde kur. Örnek: hamburger menü için ekmek, köfte, peynir, patates ve içecek ekle; sonra tarifi kaydet, bir daha tek tek eklemen gerekmesin.': 'كوّن وجبة متعددة الأجزاء دفعة واحدة. لوجبة البرجر أضف الخبز وقطعة اللحم والجبن والبطاطس والمشروب، ثم احفظ الوصفة حتى لا تضطر لإضافتها واحدة واحدة مرة أخرى.', 'Bulamadım. "Kendi yemeğim" sekmesinden ekleyip buraya malzeme olarak koyabilirsin.': 'لم أجده. أضفه من تبويب "طعامي الخاص" ثم استخدمه هنا كمكوّن.', 'Tek kişilik bir menü için 1 bırak. Dört kişilik bir tencere yemeği pişirdiysen 4 yaz; Nova porsiyon başı değeri kendi hesaplar.': 'اتركها ١ للوجبة الفردية. إذا طبخت لأربعة فاكتب ٤، وسيحسب Nova قيم الحصة الواحدة.'}}
for _k, _v in EK_TARIF.items():
    EK.setdefault(_k, {}).update(_v)
