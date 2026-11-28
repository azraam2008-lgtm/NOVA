// expo_hazirla.js - GitHub görevi içinde, "eas init"ten sonra çalışır.
// Expo Go yalnızca sürüm etiketi "exposdk:<SDK>.0.0" olan güncellemeleri açar.
// Bu betik app.json'a o etiketi ve güncelleme adresini yazar, telefonda açma
// bağlantılarını da görevin özet sayfasına koyar.
const fs = require("fs");
const yol = require("path").join(__dirname, "..", "app.json");
const app = JSON.parse(fs.readFileSync(yol, "utf8"));
const e = app.expo;
const projeId = e.extra && e.extra.eas && e.extra.eas.projectId;
if (!projeId) {
  console.error("Expo proje kimliği bulunamadı: 'eas init' çalışmamış ya da EXPO_TOKEN hatalı.");
  process.exit(1);
}
const sdk = require("expo/package.json").version.split(".")[0];
const surum = `exposdk:${sdk}.0.0`;
e.runtimeVersion = surum;
e.updates = { ...(e.updates || {}), url: `https://u.expo.dev/${projeId}` };
delete e.updates.enabled;
fs.writeFileSync(yol, JSON.stringify(app, null, 2));

const kanal = process.env.KANAL || "nova";
const exp = `exp://u.expo.dev/${projeId}?runtime-version=${encodeURIComponent(surum)}&channel-name=${kanal}`;
const qr = `https://qr.expo.dev/eas-update?projectId=${projeId}&runtimeVersion=${encodeURIComponent(surum)}&channel=${kanal}`;
console.log("Proje:", projeId, "| Sürüm etiketi:", surum);
if (process.env.GITHUB_OUTPUT) fs.appendFileSync(process.env.GITHUB_OUTPUT, `exp=${exp}\nqr=${qr}\n`);
