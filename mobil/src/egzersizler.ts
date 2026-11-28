// egzersizler.ts - Hareket kütüphanesi (sitedeki exercises.json ile aynı 35 hareket)
// Adlar ve kas grupları altı dilde. Sıra: [tr, en, de, es, fr, ar].
import { aktifDil, type Dil } from "./dil";

type Alti = [string, string, string, string, string, string];
export type Egzersiz = { id: string; ad: Alti; kas: string[]; ekipman: string[]; seviye: "başlangıç" | "orta" | "ileri"; set: number; tekrar: string };

const DILSIRA: Dil[] = ["tr", "en", "de", "es", "fr", "ar"];
const sec = (x: Alti) => x[DILSIRA.indexOf(aktifDil())] || x[0];

export const EGZERSIZLER: Egzersiz[] = [
  { id: "squat", ad: ["Çömelme (Squat)", "Squat", "Kniebeuge", "Sentadilla", "Squat", "القرفصاء"], kas: ["bacak", "kalça"], ekipman: [], seviye: "başlangıç", set: 3, tekrar: "10-15" },
  { id: "pushup", ad: ["Şınav", "Push-up", "Liegestütz", "Flexión", "Pompe", "تمرين الضغط"], kas: ["göğüs", "omuz", "arka kol"], ekipman: [], seviye: "başlangıç", set: 3, tekrar: "8-12" },
  { id: "incline_pushup", ad: ["Yüksek zeminde şınav", "Incline push-up", "Erhöhter Liegestütz", "Flexión inclinada", "Pompe inclinée", "ضغط مائل"], kas: ["göğüs", "omuz", "arka kol"], ekipman: [], seviye: "başlangıç", set: 3, tekrar: "10-15" },
  { id: "plank", ad: ["Plank", "Plank", "Unterarmstütz", "Plancha", "Gainage", "البلانك"], kas: ["karın", "omuz", "core"], ekipman: [], seviye: "başlangıç", set: 3, tekrar: "20-40 sn" },
  { id: "side_plank", ad: ["Yan plank", "Side plank", "Seitstütz", "Plancha lateral", "Gainage latéral", "البلانك الجانبي"], kas: ["yan karın", "core"], ekipman: [], seviye: "orta", set: 3, tekrar: "15-30 sn (her taraf)" },
  { id: "dead_bug", ad: ["Ölü böcek (Dead bug)", "Dead bug", "Dead Bug", "Dead bug", "Dead bug", "تمرين الحشرة الميتة"], kas: ["karın", "core"], ekipman: [], seviye: "başlangıç", set: 3, tekrar: "8-12 (her taraf)" },
  { id: "bird_dog", ad: ["Kuş-köpek (Bird dog)", "Bird dog", "Vierfüßlerstand diagonal", "Bird dog", "Bird dog", "تمرين الطائر والكلب"], kas: ["karın", "bel", "kalça"], ekipman: [], seviye: "başlangıç", set: 3, tekrar: "8-10 (her taraf)" },
  { id: "superman", ad: ["Superman", "Superman", "Superman", "Superman", "Superman", "تمرين سوبرمان"], kas: ["bel", "sırt", "kalça"], ekipman: [], seviye: "başlangıç", set: 3, tekrar: "10-15" },
  { id: "glute_bridge", ad: ["Kalça köprüsü", "Glute bridge", "Beckenheben", "Puente de glúteos", "Pont fessier", "جسر الأرداف"], kas: ["kalça", "arka bacak"], ekipman: [], seviye: "başlangıç", set: 3, tekrar: "12-15" },
  { id: "single_leg_bridge", ad: ["Tek bacak kalça köprüsü", "Single-leg glute bridge", "Einbeiniges Beckenheben", "Puente a una pierna", "Pont fessier sur une jambe", "جسر الأرداف بساق واحدة"], kas: ["kalça", "arka bacak"], ekipman: [], seviye: "orta", set: 3, tekrar: "8-12 (her bacak)" },
  { id: "lunge", ad: ["Hamle (Lunge)", "Lunge", "Ausfallschritt", "Zancada", "Fente", "الطعن"], kas: ["bacak", "kalça"], ekipman: [], seviye: "başlangıç", set: 3, tekrar: "8-12 (her bacak)" },
  { id: "reverse_lunge", ad: ["Geriye hamle", "Reverse lunge", "Ausfallschritt rückwärts", "Zancada inversa", "Fente arrière", "الطعن الخلفي"], kas: ["bacak", "kalça"], ekipman: [], seviye: "başlangıç", set: 3, tekrar: "8-12 (her bacak)" },
  { id: "step_up", ad: ["Basamak çıkma", "Step-up", "Step-up", "Subida al escalón", "Montée sur marche", "الصعود على الدرجة"], kas: ["bacak", "kalça"], ekipman: [], seviye: "başlangıç", set: 3, tekrar: "10-12 (her bacak)" },
  { id: "wall_sit", ad: ["Duvar oturuşu", "Wall sit", "Wandsitzen", "Sentadilla isométrica en pared", "Chaise au mur", "الجلوس على الحائط"], kas: ["ön bacak"], ekipman: [], seviye: "başlangıç", set: 3, tekrar: "20-45 sn" },
  { id: "calf_raise", ad: ["Baldır kaldırma", "Calf raise", "Wadenheben", "Elevación de talones", "Extension des mollets", "رفع السمانة"], kas: ["baldır"], ekipman: [], seviye: "başlangıç", set: 3, tekrar: "15-20" },
  { id: "chair_dip", ad: ["Sandalyede dip", "Chair dip", "Dips am Stuhl", "Fondos en silla", "Dips sur chaise", "الغطس على الكرسي"], kas: ["arka kol", "omuz"], ekipman: [], seviye: "orta", set: 3, tekrar: "8-12" },
  { id: "pike_pushup", ad: ["Pike şınav", "Pike push-up", "Pike-Liegestütz", "Flexión en pica", "Pompe en pike", "ضغط بايك"], kas: ["omuz", "arka kol"], ekipman: [], seviye: "orta", set: 3, tekrar: "6-10" },
  { id: "mountain_climber", ad: ["Dağcı (Mountain climber)", "Mountain climber", "Bergsteiger", "Escalador", "Mountain climber", "متسلق الجبال"], kas: ["karın", "omuz", "kardiyo"], ekipman: [], seviye: "orta", set: 3, tekrar: "30 sn" },
  { id: "jumping_jack", ad: ["Jumping jack", "Jumping jack", "Hampelmann", "Saltos de tijera", "Jumping jack", "القفز المفتوح"], kas: ["tüm vücut", "kardiyo"], ekipman: [], seviye: "başlangıç", set: 3, tekrar: "30-45 sn" },
  { id: "high_knees", ad: ["Yüksek diz koşusu", "High knees", "Kniehebelauf", "Rodillas al pecho", "Montées de genoux", "رفع الركبتين"], kas: ["bacak", "kardiyo"], ekipman: [], seviye: "başlangıç", set: 3, tekrar: "30 sn" },
  { id: "squat_jump", ad: ["Sıçrama squat", "Jump squat", "Sprungkniebeuge", "Sentadilla con salto", "Squat sauté", "القرفصاء مع القفز"], kas: ["bacak", "kalça", "kardiyo"], ekipman: [], seviye: "ileri", set: 3, tekrar: "8-12" },
  { id: "burpee", ad: ["Burpee", "Burpee", "Burpee", "Burpee", "Burpee", "بيربي"], kas: ["tüm vücut", "kardiyo"], ekipman: [], seviye: "ileri", set: 3, tekrar: "6-10" },
  { id: "russian_twist", ad: ["Rus twisti", "Russian twist", "Russian Twist", "Giro ruso", "Rotation russe", "الالتواء الروسي"], kas: ["yan karın"], ekipman: [], seviye: "orta", set: 3, tekrar: "12-16 (toplam)" },
  { id: "leg_raise", ad: ["Yatarak bacak kaldırma", "Lying leg raise", "Beinheben im Liegen", "Elevación de piernas tumbado", "Relevé de jambes allongé", "رفع الساقين مستلقيًا"], kas: ["alt karın"], ekipman: [], seviye: "orta", set: 3, tekrar: "10-15" },
  { id: "glute_kickback", ad: ["Dört ayak kalça itme", "Glute kickback", "Kickback im Vierfüßlerstand", "Patada de glúteo", "Kickback fessier", "ركلة الأرداف"], kas: ["kalça"], ekipman: [], seviye: "başlangıç", set: 3, tekrar: "12-15 (her bacak)" },
  { id: "db_goblet_squat", ad: ["Goblet squat", "Goblet squat", "Goblet Squat", "Sentadilla goblet", "Goblet squat", "قرفصاء الكأس"], kas: ["bacak", "kalça", "core"], ekipman: ["dambıl"], seviye: "başlangıç", set: 3, tekrar: "10-12" },
  { id: "db_row", ad: ["Tek kol dambıl kürek", "Single-arm dumbbell row", "Einarmiges Kurzhantelrudern", "Remo a una mano con mancuerna", "Rowing unilatéral haltère", "تجديف بالدمبل بذراع واحدة"], kas: ["sırt", "arka omuz", "pazu"], ekipman: ["dambıl", "bank"], seviye: "başlangıç", set: 3, tekrar: "10-12 (her kol)" },
  { id: "db_curl", ad: ["Dambıl biceps curl", "Dumbbell biceps curl", "Kurzhantel-Bizepscurl", "Curl de bíceps con mancuerna", "Curl biceps haltère", "تمرين البايسبس بالدمبل"], kas: ["ön kol", "pazu"], ekipman: ["dambıl"], seviye: "başlangıç", set: 3, tekrar: "10-12" },
  { id: "db_lateral_raise", ad: ["Dambıl yan kaldırış", "Dumbbell lateral raise", "Seitheben mit Kurzhanteln", "Elevación lateral con mancuernas", "Élévation latérale haltères", "الرفع الجانبي بالدمبل"], kas: ["omuz"], ekipman: ["dambıl"], seviye: "başlangıç", set: 3, tekrar: "12-15" },
  { id: "db_shoulder_press", ad: ["Dambıl omuz press", "Dumbbell shoulder press", "Kurzhantel-Schulterdrücken", "Press de hombros con mancuernas", "Développé épaules haltères", "ضغط الكتف بالدمبل"], kas: ["omuz", "arka kol"], ekipman: ["dambıl"], seviye: "orta", set: 3, tekrar: "8-12" },
  { id: "db_chest_press", ad: ["Dambıl göğüs press", "Dumbbell chest press", "Kurzhantel-Brustdrücken", "Press de pecho con mancuernas", "Développé couché haltères", "ضغط الصدر بالدمبل"], kas: ["göğüs", "omuz", "arka kol"], ekipman: ["dambıl"], seviye: "başlangıç", set: 3, tekrar: "10-12" },
  { id: "db_rdl", ad: ["Dambıl Romen deadlift", "Dumbbell Romanian deadlift", "Rumänisches Kreuzheben mit Kurzhanteln", "Peso muerto rumano con mancuernas", "Soulevé de terre roumain haltères", "الرفعة الرومانية بالدمبل"], kas: ["arka bacak", "kalça", "bel"], ekipman: ["dambıl"], seviye: "orta", set: 3, tekrar: "8-12" },
  { id: "db_lunge", ad: ["Dambıllı hamle", "Dumbbell lunge", "Ausfallschritt mit Kurzhanteln", "Zancada con mancuernas", "Fente avec haltères", "الطعن بالدمبل"], kas: ["bacak", "kalça"], ekipman: ["dambıl"], seviye: "orta", set: 3, tekrar: "8-10 (her bacak)" },
  { id: "pullup", ad: ["Barfiks", "Pull-up", "Klimmzug", "Dominada", "Traction", "العقلة"], kas: ["sırt", "pazu"], ekipman: ["barfiks"], seviye: "ileri", set: 3, tekrar: "3-8" },
  { id: "hanging_knee_raise", ad: ["Barda diz çekme", "Hanging knee raise", "Knieheben im Hang", "Elevación de rodillas colgado", "Relevé de genoux suspendu", "رفع الركبتين معلقًا"], kas: ["alt karın"], ekipman: ["barfiks"], seviye: "orta", set: 3, tekrar: "8-12" },
];

const KAS: Record<string, Alti> = {
  "alt karın": ["alt karın", "lower abs", "untere Bauchmuskeln", "abdomen inferior", "bas des abdos", "أسفل البطن"],
  "arka bacak": ["arka bacak", "hamstrings", "Beinbeuger", "isquiotibiales", "ischio-jambiers", "أوتار الركبة"],
  "arka kol": ["arka kol", "triceps", "Trizeps", "tríceps", "triceps", "العضلة ثلاثية الرؤوس"],
  "arka omuz": ["arka omuz", "rear delts", "hintere Schulter", "deltoides posterior", "deltoïde postérieur", "الكتف الخلفي"],
  "bacak": ["bacak", "legs", "Beine", "piernas", "jambes", "الساقان"],
  "baldır": ["baldır", "calves", "Waden", "gemelos", "mollets", "السمانة"],
  "bel": ["bel", "lower back", "unterer Rücken", "zona lumbar", "bas du dos", "أسفل الظهر"],
  "core": ["core", "core", "Rumpf", "core", "gainage", "الجذع"],
  "göğüs": ["göğüs", "chest", "Brust", "pecho", "pectoraux", "الصدر"],
  "kalça": ["kalça", "glutes", "Gesäß", "glúteos", "fessiers", "الأرداف"],
  "kardiyo": ["kardiyo", "cardio", "Ausdauer", "cardio", "cardio", "كارديو"],
  "karın": ["karın", "abs", "Bauch", "abdomen", "abdos", "البطن"],
  "omuz": ["omuz", "shoulders", "Schultern", "hombros", "épaules", "الكتفان"],
  "pazu": ["pazu", "biceps", "Bizeps", "bíceps", "biceps", "العضلة ذات الرأسين"],
  "sırt": ["sırt", "back", "Rücken", "espalda", "dos", "الظهر"],
  "tüm vücut": ["tüm vücut", "full body", "Ganzkörper", "cuerpo completo", "corps entier", "الجسم كله"],
  "yan karın": ["yan karın", "obliques", "seitliche Bauchmuskeln", "oblicuos", "obliques", "الخواصر"],
  "ön bacak": ["ön bacak", "quads", "Oberschenkel vorne", "cuádriceps", "quadriceps", "العضلة الرباعية"],
  "ön kol": ["ön kol", "forearms", "Unterarme", "antebrazos", "avant-bras", "الساعد"],
};

const TEKRAR_EK: [string, Alti][] = [
  [" (her taraf)", [" (her taraf)", " (each side)", " (pro Seite)", " (cada lado)", " (chaque côté)", " (لكل جانب)"]],
  [" (her bacak)", [" (her bacak)", " (each leg)", " (pro Bein)", " (cada pierna)", " (chaque jambe)", " (لكل ساق)"]],
  [" (her kol)", [" (her kol)", " (each arm)", " (pro Arm)", " (cada brazo)", " (chaque bras)", " (لكل ذراع)"]],
  [" (toplam)", [" (toplam)", " (total)", " (gesamt)", " (en total)", " (au total)", " (المجموع)"]],
  [" sn", [" sn", " s", " Sek.", " s", " s", " ث"]],
];

export const egzersizAdi = (e: Egzersiz) => sec(e.ad);
export const kasAdi = (k: string) => (KAS[k] ? sec(KAS[k]) : k);
export function tekrarMetni(e: Egzersiz): string {
  let m = e.tekrar;
  for (const [tr, x] of TEKRAR_EK) m = m.replace(tr, sec(x));
  return m;
}
