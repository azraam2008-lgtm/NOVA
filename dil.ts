// dil.ts - Uygulamanın altı dili
// Anahtar Türkçe metnin kendisidir (sitedeki t() ile aynı düzen).
// Sıra: [en, de, es, fr, ar]. Eksik çeviri olursa Türkçe gösterilir.

export type Dil = "tr" | "en" | "de" | "es" | "fr" | "ar";

export const DILLER: { kod: Dil; ad: string }[] = [
  { kod: "tr", ad: "Türkçe" },
  { kod: "en", ad: "English" },
  { kod: "de", ad: "Deutsch" },
  { kod: "es", ad: "Español" },
  { kod: "fr", ad: "Français" },
  { kod: "ar", ad: "العربية" },
];

const SIRA: Dil[] = ["en", "de", "es", "fr", "ar"];

const C: Record<string, [string, string, string, string, string]> = {
  // ------------------------------------------------------------ genel
  "Devam": ["Continue", "Weiter", "Continuar", "Continuer", "متابعة"],
  "Geri": ["Back", "Zurück", "Atrás", "Retour", "رجوع"],
  "İleri": ["Next", "Weiter", "Siguiente", "Suivant", "التالي"],
  "Kapat": ["Close", "Schließen", "Cerrar", "Fermer", "إغلاق"],
  "Yükleniyor...": ["Loading...", "Wird geladen...", "Cargando...", "Chargement...", "جارٍ التحميل..."],
  "Bir sorun çıktı. Biraz sonra tekrar dene.": ["Something went wrong. Please try again shortly.", "Etwas ist schiefgelaufen. Bitte versuche es gleich noch einmal.", "Algo salió mal. Vuelve a intentarlo en un momento.", "Un problème est survenu. Réessaie dans un instant.", "حدث خطأ ما. حاول مرة أخرى بعد قليل."],
  "ZARAFET VE DENGE": ["GRACE AND BALANCE", "ANMUT UND BALANCE", "ELEGANCIA Y EQUILIBRIO", "GRÂCE ET ÉQUILIBRE", "أناقة وتوازن"],

  // ------------------------------------------------------------ dil
  "Hangi dili kullanmak istersin?": ["Which language would you like to use?", "Welche Sprache möchtest du verwenden?", "¿Qué idioma quieres usar?", "Quelle langue veux-tu utiliser ?", "ما اللغة التي تريد استخدامها؟"],
  "Nova'yı bu dilde kullanacaksın. Daha sonra ayarlardan değiştirebilirsin.": ["You will use Nova in this language. You can change it later in settings.", "Du nutzt Nova in dieser Sprache. Du kannst sie später in den Einstellungen ändern.", "Usarás Nova en este idioma. Puedes cambiarlo más tarde en los ajustes.", "Tu utiliseras Nova dans cette langue. Tu pourras la changer plus tard dans les réglages.", "ستستخدم Nova بهذه اللغة. يمكنك تغييرها لاحقًا من الإعدادات."],

  // ------------------------------------------------------------ giriş
  "Giriş Yap": ["Sign in", "Anmelden", "Iniciar sesión", "Se connecter", "تسجيل الدخول"],
  "Kayıt Ol": ["Sign up", "Registrieren", "Registrarse", "S'inscrire", "إنشاء حساب"],
  "Kullanıcı adı veya e-posta": ["Username or email", "Benutzername oder E-Mail", "Usuario o correo", "Nom d'utilisateur ou e-mail", "اسم المستخدم أو البريد الإلكتروني"],
  "Kullanıcı adı": ["Username", "Benutzername", "Nombre de usuario", "Nom d'utilisateur", "اسم المستخدم"],
  "E-posta (isteğe bağlı, şifreni unutursan gerekli)": ["Email (optional, needed if you forget your password)", "E-Mail (optional, nötig, falls du dein Passwort vergisst)", "Correo (opcional, necesario si olvidas tu contraseña)", "E-mail (facultatif, utile si tu oublies ton mot de passe)", "البريد الإلكتروني (اختياري، تحتاجه إذا نسيت كلمة المرور)"],
  "Şifre": ["Password", "Passwort", "Contraseña", "Mot de passe", "كلمة المرور"],
  "Şifre (en az 8 karakter, bir büyük harf ve bir rakam)": ["Password (at least 8 characters, one capital letter and one number)", "Passwort (mind. 8 Zeichen, ein Großbuchstabe und eine Zahl)", "Contraseña (mínimo 8 caracteres, una mayúscula y un número)", "Mot de passe (8 caractères min., une majuscule et un chiffre)", "كلمة المرور (8 أحرف على الأقل، حرف كبير ورقم)"],
  "Hatalı kullanıcı adı veya şifre.": ["Incorrect username or password.", "Benutzername oder Passwort falsch.", "Usuario o contraseña incorrectos.", "Nom d'utilisateur ou mot de passe incorrect.", "اسم المستخدم أو كلمة المرور غير صحيحة."],
  "Çok fazla yanlış deneme. Yarın tekrar dene ya da şifreni sıfırla.": ["Too many wrong attempts. Try again tomorrow or reset your password.", "Zu viele Fehlversuche. Versuche es morgen erneut oder setze dein Passwort zurück.", "Demasiados intentos fallidos. Inténtalo mañana o restablece tu contraseña.", "Trop de tentatives. Réessaie demain ou réinitialise ton mot de passe.", "محاولات خاطئة كثيرة. حاول غدًا أو أعد تعيين كلمة المرور."],
  "Bu kullanıcı adı zaten alınmış.": ["This username is already taken.", "Dieser Benutzername ist schon vergeben.", "Este nombre de usuario ya está en uso.", "Ce nom d'utilisateur est déjà pris.", "اسم المستخدم هذا مستخدم بالفعل."],
  "Bu e-posta ile kayıtlı bir hesap var.": ["An account with this email already exists.", "Mit dieser E-Mail gibt es bereits ein Konto.", "Ya existe una cuenta con este correo.", "Un compte existe déjà avec cet e-mail.", "يوجد حساب مسجّل بهذا البريد الإلكتروني."],
  "Kullanıcı adı 3-30 karakter olmalı; harf, rakam, nokta ve tire kullanabilirsin.": ["Username must be 3-30 characters; letters, numbers, dots and hyphens are allowed.", "Der Benutzername muss 3-30 Zeichen haben; Buchstaben, Zahlen, Punkte und Bindestriche sind erlaubt.", "El usuario debe tener 3-30 caracteres; letras, números, puntos y guiones.", "Le nom d'utilisateur doit faire 3 à 30 caractères : lettres, chiffres, points et tirets.", "يجب أن يكون اسم المستخدم من 3 إلى 30 حرفًا؛ أحرف وأرقام ونقاط وشرطات."],
  "E-posta adresi geçerli görünmüyor.": ["The email address doesn't look valid.", "Die E-Mail-Adresse scheint ungültig zu sein.", "El correo no parece válido.", "L'adresse e-mail ne semble pas valide.", "يبدو أن البريد الإلكتروني غير صالح."],
  "Şifre en az 8 karakter olmalıdır.": ["Password must be at least 8 characters.", "Das Passwort muss mindestens 8 Zeichen haben.", "La contraseña debe tener al menos 8 caracteres.", "Le mot de passe doit contenir au moins 8 caractères.", "يجب أن تتكون كلمة المرور من 8 أحرف على الأقل."],
  "Şifre en az bir büyük harf içermelidir.": ["Password must contain at least one capital letter.", "Das Passwort muss mindestens einen Großbuchstaben enthalten.", "La contraseña debe tener al menos una mayúscula.", "Le mot de passe doit contenir au moins une majuscule.", "يجب أن تحتوي كلمة المرور على حرف كبير واحد على الأقل."],
  "Şifre en az bir rakam içermelidir.": ["Password must contain at least one number.", "Das Passwort muss mindestens eine Zahl enthalten.", "La contraseña debe tener al menos un número.", "Le mot de passe doit contenir au moins un chiffre.", "يجب أن تحتوي كلمة المرور على رقم واحد على الأقل."],
  "Giriş servisine şu an ulaşılamadı. Biraz sonra tekrar dene.": ["The sign-in service is unreachable right now. Please try again shortly.", "Der Anmeldedienst ist gerade nicht erreichbar. Bitte versuche es gleich noch einmal.", "El servicio de inicio de sesión no está disponible ahora. Vuelve a intentarlo en un momento.", "Le service de connexion est momentanément indisponible. Réessaie dans un instant.", "خدمة تسجيل الدخول غير متاحة الآن. حاول مرة أخرى بعد قليل."],
  "Hesabın hazırlanamadı. Bir kez siteden giriş yapıp tekrar dene.": ["Your account couldn't be prepared. Sign in once on the website, then try again.", "Dein Konto konnte nicht vorbereitet werden. Melde dich einmal auf der Website an und versuche es erneut.", "No se pudo preparar tu cuenta. Inicia sesión una vez en la web y vuelve a intentarlo.", "Ton compte n'a pas pu être préparé. Connecte-toi une fois sur le site, puis réessaie.", "تعذّر تجهيز حسابك. سجّل الدخول مرة من الموقع ثم حاول مجددًا."],

  // ------------------------------------------------------------ kurulum
  "Merhaba! Adın nedir?": ["Hi! What's your name?", "Hallo! Wie heißt du?", "¡Hola! ¿Cómo te llamas?", "Salut ! Comment t'appelles-tu ?", "مرحبًا! ما اسمك؟"],
  "Adın": ["Your name", "Dein Name", "Tu nombre", "Ton prénom", "اسمك"],
  "Lütfen adını gir.": ["Please enter your name.", "Bitte gib deinen Namen ein.", "Escribe tu nombre.", "Indique ton prénom.", "يرجى إدخال اسمك."],
  "Nova'yı hangi amaçla kullanmak istiyorsun?": ["What would you like to use Nova for?", "Wofür möchtest du Nova nutzen?", "¿Para qué quieres usar Nova?", "Pour quoi veux-tu utiliser Nova ?", "لأي غرض تريد استخدام Nova؟"],
  "Birden fazla seçebilirsin.": ["You can choose more than one.", "Du kannst mehrere auswählen.", "Puedes elegir más de uno.", "Tu peux en choisir plusieurs.", "يمكنك اختيار أكثر من واحد."],
  "Kilo vermek istiyorum": ["Lose weight", "Abnehmen", "Perder peso", "Perdre du poids", "إنقاص الوزن"],
  "Kilomu korumak istiyorum": ["Maintain my weight", "Gewicht halten", "Mantener mi peso", "Maintenir mon poids", "الحفاظ على وزني"],
  "Kilo almak istiyorum": ["Gain weight", "Zunehmen", "Ganar peso", "Prendre du poids", "زيادة الوزن"],
  "Kas kazanmak istiyorum": ["Build muscle", "Muskeln aufbauen", "Ganar músculo", "Prendre du muscle", "بناء العضلات"],
  "Sağlıklı beslenmek istiyorum": ["Eat healthier", "Gesünder essen", "Comer más sano", "Manger plus sainement", "تناول طعام صحي"],
  "Cinsiyetin nedir?": ["What is your sex?", "Was ist dein Geschlecht?", "¿Cuál es tu sexo?", "Quel est ton sexe ?", "ما جنسك؟"],
  "Kadın": ["Female", "Weiblich", "Mujer", "Femme", "أنثى"],
  "Erkek": ["Male", "Männlich", "Hombre", "Homme", "ذكر"],
  "Cinsiyetin, günlük enerji ihtiyacını hesaplamamızı doğrudan etkiler.": ["Your sex directly affects how we calculate your daily energy needs.", "Dein Geschlecht beeinflusst direkt die Berechnung deines täglichen Energiebedarfs.", "Tu sexo influye directamente en el cálculo de tu energía diaria.", "Ton sexe influe directement sur le calcul de tes besoins énergétiques.", "يؤثر جنسك مباشرة في حساب احتياجك اليومي من الطاقة."],
  "Doğum yılın ne?": ["What year were you born?", "In welchem Jahr bist du geboren?", "¿En qué año naciste?", "En quelle année es-tu né(e) ?", "في أي سنة وُلدت؟"],
  "yaşındasın": ["years old", "Jahre alt", "años", "ans", "سنة"],
  "18 yaşından küçüksün. Büyüme çağında kalori kısıtlamak gelişimi etkileyebilir; kilo hedefi koymadan önce bir doktora ya da diyetisyene danışmanı öneririm.": ["You are under 18. Restricting calories while growing can affect development; please talk to a doctor or dietitian before setting a weight goal.", "Du bist unter 18. Kalorien im Wachstum einzuschränken kann die Entwicklung beeinträchtigen; sprich vor einem Gewichtsziel mit einer Ärztin oder Ernährungsberatung.", "Tienes menos de 18 años. Restringir calorías en la etapa de crecimiento puede afectar el desarrollo; consulta a un médico o dietista antes de fijar un objetivo de peso.", "Tu as moins de 18 ans. Restreindre les calories pendant la croissance peut nuire au développement ; parle à un médecin ou un diététicien avant de fixer un objectif de poids.", "عمرك أقل من 18 عامًا. تقليل السعرات في مرحلة النمو قد يؤثر على التطور؛ استشر طبيبًا أو أخصائي تغذية قبل تحديد هدف للوزن."],
  "Boyun kaç?": ["How tall are you?", "Wie groß bist du?", "¿Cuánto mides?", "Quelle est ta taille ?", "كم طولك؟"],
  "Boy (cm)": ["Height (cm)", "Größe (cm)", "Altura (cm)", "Taille (cm)", "الطول (سم)"],
  "Şu andaki kilon ne?": ["What is your current weight?", "Wie viel wiegst du aktuell?", "¿Cuál es tu peso actual?", "Quel est ton poids actuel ?", "ما وزنك الحالي؟"],
  "Kilo (kg)": ["Weight (kg)", "Gewicht (kg)", "Peso (kg)", "Poids (kg)", "الوزن (كغ)"],
  "Hedef kilon nedir?": ["What is your goal weight?", "Was ist dein Zielgewicht?", "¿Cuál es tu peso objetivo?", "Quel est ton poids cible ?", "ما وزنك المستهدف؟"],
  "Hedef kilo (kg)": ["Goal weight (kg)", "Zielgewicht (kg)", "Peso objetivo (kg)", "Poids cible (kg)", "الوزن المستهدف (كغ)"],
  "Kaç ayda?": ["In how many months?", "In wie vielen Monaten?", "¿En cuántos meses?", "En combien de mois ?", "خلال كم شهر؟"],
  "Günlük hareket düzeyin": ["Your daily activity level", "Dein tägliches Aktivitätsniveau", "Tu nivel de actividad diario", "Ton niveau d'activité quotidien", "مستوى نشاطك اليومي"],
  "Hareketsiz (masa başı, çok az yürüyüş)": ["Sedentary (desk job, very little walking)", "Inaktiv (Bürojob, kaum Gehen)", "Sedentario (trabajo de oficina, poco caminar)", "Sédentaire (travail de bureau, très peu de marche)", "قليل الحركة (عمل مكتبي، مشي قليل جدًا)"],
  "Az hareketli (haftada 1-3 gün egzersiz)": ["Lightly active (exercise 1-3 days a week)", "Leicht aktiv (1-3 Tage Sport pro Woche)", "Poco activo (ejercicio 1-3 días por semana)", "Peu actif (sport 1 à 3 jours par semaine)", "نشاط خفيف (تمرين 1-3 أيام أسبوعيًا)"],
  "Orta hareketli (haftada 3-5 gün egzersiz)": ["Moderately active (exercise 3-5 days a week)", "Mäßig aktiv (3-5 Tage Sport pro Woche)", "Moderadamente activo (ejercicio 3-5 días por semana)", "Modérément actif (sport 3 à 5 jours par semaine)", "نشاط متوسط (تمرين 3-5 أيام أسبوعيًا)"],
  "Çok hareketli (haftada 6-7 gün egzersiz)": ["Very active (exercise 6-7 days a week)", "Sehr aktiv (6-7 Tage Sport pro Woche)", "Muy activo (ejercicio 6-7 días por semana)", "Très actif (sport 6 à 7 jours par semaine)", "نشاط عالٍ (تمرين 6-7 أيام أسبوعيًا)"],
  "Bu tempo hızlı. Güvenli aralık genelde haftada 0,5-1 kilodur; süreyi uzatmanı öneririm.": ["This pace is fast. The safe range is usually 0.5-1 kg per week; consider giving yourself more time.", "Dieses Tempo ist hoch. Sicher sind meist 0,5-1 kg pro Woche; plane lieber mehr Zeit ein.", "Este ritmo es rápido. Lo seguro suele ser 0,5-1 kg por semana; te sugiero alargar el plazo.", "Ce rythme est rapide. La plage sûre est généralement de 0,5 à 1 kg par semaine ; allonge plutôt la durée.", "هذه الوتيرة سريعة. النطاق الآمن عادةً 0.5-1 كغ أسبوعيًا؛ أنصحك بإطالة المدة."],
  "Günlük hedefin": ["Your daily target", "Dein Tagesziel", "Tu objetivo diario", "Ton objectif quotidien", "هدفك اليومي"],
  "Dinlenik metabolizman": ["Resting metabolism", "Grundumsatz", "Metabolismo en reposo", "Métabolisme de base", "معدل الأيض في الراحة"],
  "Tahmini günlük harcaman": ["Estimated daily burn", "Geschätzter Tagesverbrauch", "Gasto diario estimado", "Dépense quotidienne estimée", "الحرق اليومي المقدّر"],
  "Nova bir sağlık uygulaması değildir ve tıbbi tavsiye vermez. Hesaplamalar genel formüllere dayanan tahminlerdir.": ["Nova is not a medical app and does not give medical advice. Calculations are estimates based on general formulas.", "Nova ist keine medizinische App und gibt keine medizinischen Ratschläge. Berechnungen sind Schätzungen auf Basis allgemeiner Formeln.", "Nova no es una app médica y no da consejo médico. Los cálculos son estimaciones basadas en fórmulas generales.", "Nova n'est pas une application médicale et ne donne pas d'avis médical. Les calculs sont des estimations fondées sur des formules générales.", "Nova ليست تطبيقًا طبيًا ولا تقدم نصائح طبية. الحسابات تقديرات مبنية على معادلات عامة."],
  "Uygulamaya başla": ["Start using Nova", "Los geht's", "Empezar", "Commencer", "ابدأ"],

  // ------------------------------------------------------------ ana ekran
  "Merhaba": ["Hi", "Hallo", "Hola", "Salut", "مرحبًا"],
  "kcal kaldı": ["kcal left", "kcal übrig", "kcal restantes", "kcal restantes", "سعرة متبقية"],
  "kcal fazla": ["kcal over", "kcal zu viel", "kcal de más", "kcal en trop", "سعرة زائدة"],
  "Alınan": ["Eaten", "Gegessen", "Consumido", "Consommé", "المتناول"],
  "Hedef": ["Target", "Ziel", "Objetivo", "Objectif", "الهدف"],
  "Protein": ["Protein", "Eiweiß", "Proteína", "Protéines", "بروتين"],
  "Karbonhidrat": ["Carbs", "Kohlenhydrate", "Carbohidratos", "Glucides", "كربوهيدرات"],
  "Yağ": ["Fat", "Fett", "Grasa", "Lipides", "دهون"],
  "Su": ["Water", "Wasser", "Agua", "Eau", "ماء"],
  "bardak": ["glasses", "Gläser", "vasos", "verres", "أكواب"],
  "Kahvaltı": ["Breakfast", "Frühstück", "Desayuno", "Petit-déjeuner", "الإفطار"],
  "Öğle Yemeği": ["Lunch", "Mittagessen", "Almuerzo", "Déjeuner", "الغداء"],
  "Akşam Yemeği": ["Dinner", "Abendessen", "Cena", "Dîner", "العشاء"],
  "Ara Öğün": ["Snack", "Snack", "Tentempié", "Collation", "وجبة خفيفة"],
  "Sahur": ["Suhoor", "Sahur", "Suhur", "Shour", "السحور"],
  "İftar": ["Iftar", "Iftar", "Iftar", "Iftar", "الإفطار"],
  "Gece Ara Öğünü": ["Late-night snack", "Spätsnack", "Tentempié nocturno", "Collation du soir", "وجبة ليلية"],
  "Henüz bir şey eklemedin.": ["Nothing added yet.", "Noch nichts hinzugefügt.", "Aún no has añadido nada.", "Rien d'ajouté pour l'instant.", "لم تضف شيئًا بعد."],
  "Ekle": ["Add", "Hinzufügen", "Añadir", "Ajouter", "إضافة"],
  "Çıkış yap": ["Sign out", "Abmelden", "Cerrar sesión", "Se déconnecter", "تسجيل الخروج"],
  "Sil": ["Delete", "Löschen", "Eliminar", "Supprimer", "حذف"],

  // ------------------------------------------------------------ ekle paneli
  "Ne eklemek istersin?": ["What would you like to add?", "Was möchtest du hinzufügen?", "¿Qué quieres añadir?", "Que veux-tu ajouter ?", "ماذا تريد أن تضيف؟"],
  "Ara": ["Search", "Suchen", "Buscar", "Rechercher", "بحث"],
  "Barkod": ["Barcode", "Barcode", "Código de barras", "Code-barres", "باركود"],
  "Fotoğraf": ["Photo", "Foto", "Foto", "Photo", "صورة"],
  "Yazarak anlat": ["Describe it", "Beschreiben", "Descríbelo", "Décris-le", "صِف ما أكلت"],
  "Tarif": ["Recipe", "Rezept", "Receta", "Recette", "وصفة"],
  "Yakında": ["Coming soon", "Bald verfügbar", "Próximamente", "Bientôt", "قريبًا"],
  "Yemek ara": ["Search food", "Lebensmittel suchen", "Buscar comida", "Rechercher un aliment", "ابحث عن طعام"],
  "Bulamadım. \"Yazarak anlat\" seçeneğini dene.": ["Not found. Try \"Describe it\".", "Nichts gefunden. Versuche \"Beschreiben\".", "No encontrado. Prueba \"Descríbelo\".", "Introuvable. Essaie \"Décris-le\".", "لم أجد شيئًا. جرّب \"صِف ما أكلت\"."],
  "gram": ["grams", "Gramm", "gramos", "grammes", "غرام"],
  "Hangi öğün?": ["Which meal?", "Welche Mahlzeit?", "¿Qué comida?", "Quel repas ?", "أي وجبة؟"],
  "Eklendi": ["Added", "Hinzugefügt", "Añadido", "Ajouté", "تمت الإضافة"],
  "Ne yediğini anlat": ["Tell Nova what you ate", "Erzähl, was du gegessen hast", "Cuenta qué comiste", "Raconte ce que tu as mangé", "أخبرني بما أكلت"],
  "Örnek: 2 yumurta, 1 dilim peynir ve bir bardak çay": ["Example: 2 eggs, a slice of cheese and a cup of tea", "Beispiel: 2 Eier, eine Scheibe Käse und eine Tasse Tee", "Ejemplo: 2 huevos, una loncha de queso y una taza de té", "Exemple : 2 œufs, une tranche de fromage et une tasse de thé", "مثال: بيضتان، شريحة جبن وكوب شاي"],
  "Hesapla": ["Calculate", "Berechnen", "Calcular", "Calculer", "احسب"],
  "Nova hesaplıyor...": ["Nova is calculating...", "Nova rechnet...", "Nova está calculando...", "Nova calcule...", "Nova تحسب..."],
  "Bunları ekle": ["Add these", "Diese hinzufügen", "Añadir estos", "Ajouter ceux-ci", "أضف هذه"],
  "Bu bir yiyecek gibi görünmüyor.": ["That doesn't look like food.", "Das scheint kein Essen zu sein.", "Eso no parece comida.", "Ça ne ressemble pas à de la nourriture.", "لا يبدو هذا طعامًا."],
  "Bugünkü hakkın doldu. Yarın tekrar dene.": ["You've used today's allowance. Try again tomorrow.", "Dein heutiges Kontingent ist aufgebraucht. Versuche es morgen erneut.", "Has agotado tu límite de hoy. Vuelve mañana.", "Ton quota du jour est épuisé. Réessaie demain.", "استنفدت حصتك اليوم. حاول غدًا."],
  "Tahmin": ["Estimate", "Schätzung", "Estimación", "Estimation", "تقدير"],

  // ------------------------------------------------------------ asistan
  "Nova'ya sor": ["Ask Nova", "Frag Nova", "Pregunta a Nova", "Demande à Nova", "اسأل Nova"],
  "Bir şey sor...": ["Ask something...", "Frag etwas...", "Pregunta algo...", "Pose une question...", "اسأل شيئًا..."],
  "Gönder": ["Send", "Senden", "Enviar", "Envoyer", "إرسال"],
  "Beslenme ve antrenman soruların için. Genel bilgi verir, tıbbi tavsiye değildir.": ["For your nutrition and training questions. General information, not medical advice.", "Für deine Fragen zu Ernährung und Training. Allgemeine Infos, keine medizinische Beratung.", "Para tus dudas de nutrición y entrenamiento. Información general, no consejo médico.", "Pour tes questions de nutrition et d'entraînement. Informations générales, pas un avis médical.", "لأسئلتك عن التغذية والتمارين. معلومات عامة وليست نصيحة طبية."],
  "Nova yazıyor...": ["Nova is typing...", "Nova schreibt...", "Nova está escribiendo...", "Nova écrit...", "Nova تكتب..."],
  "Asistanı aç": ["Open assistant", "Assistent öffnen", "Abrir asistente", "Ouvrir l'assistant", "افتح المساعد"],
};

let aktif: Dil = "tr";
export function dilAyarla(d: Dil) {
  aktif = d;
}
export function aktifDil(): Dil {
  return aktif;
}
export function sagdanSola(): boolean {
  return aktif === "ar";
}
export function t(metin: string): string {
  if (aktif === "tr") return metin;
  const satir = C[metin];
  return satir ? satir[SIRA.indexOf(aktif)] : metin;
}
// Sınama için: hangi anahtarın hangi dilde boş kaldığını bulur
export function eksikCeviriler(): string[] {
  return Object.entries(C).filter(([, v]) => v.length !== 5 || v.some((x) => !x)).map(([k]) => k);
}

/** Cihaz dilinden başlangıç dili (yalnızca ilk açılışta önerilir). */
export function cihazDili(kod: string | undefined | null): Dil {
  const k = (kod ?? "").slice(0, 2).toLowerCase();
  return (["tr", "en", "de", "es", "fr", "ar"] as Dil[]).includes(k as Dil) ? (k as Dil) : "en";
}
