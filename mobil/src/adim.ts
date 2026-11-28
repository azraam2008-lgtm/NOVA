// adim.ts - iPhone'un hareket sensöründen adım sayısı (expo-sensors Pedometer)
// Apple Health bağlantısı değil: sensörün kendi kaydı. iPhone son 7 günü saklar,
// bu yüzden uygulama birkaç gün açılmasa da o günler sonradan doldurulur.
// Yalnızca iOS'ta çalışır; Android ve web'de "yok" döner, adım elle girilmeye devam eder.
import { useEffect, useRef, useState } from "react";
import { AppState, Platform } from "react-native";
import { Pedometer } from "expo-sensors";
import { bugunMetni, type Veri } from "./hesap";

export type AdimDurumu = "var" | "yok" | "izin_yok";

const GUN = 7;
const UST = 100000; // Antrenman ekranındaki elle girişle aynı üst sınır

/** Sensör kullanılabilir mi, izin verildi mi. İzin hiç sorulmadıysa bir kez sorar. */
export async function adimIzni(): Promise<AdimDurumu> {
  if (Platform.OS !== "ios") return "yok";
  try {
    if (!(await Pedometer.isAvailableAsync())) return "yok";
    let izin = await Pedometer.getPermissionsAsync();
    if (!izin.granted && izin.canAskAgain) izin = await Pedometer.requestPermissionsAsync();
    return izin.granted ? "var" : "izin_yok";
  } catch {
    return "yok";
  }
}

/** Son 7 günün (bugün dahil) sensör adımları: { "2026-11-28": 6420, ... } */
export async function sonGunlerinAdimi(simdi = new Date()): Promise<Record<string, number>> {
  const sonuc: Record<string, number> = {};
  for (let i = 0; i < GUN; i++) {
    const bas = new Date(simdi.getFullYear(), simdi.getMonth(), simdi.getDate() - i);
    const son = i === 0 ? simdi : new Date(bas.getFullYear(), bas.getMonth(), bas.getDate() + 1);
    try {
      const { steps } = await Pedometer.getStepCountAsync(bas, son);
      if (steps > 0) sonuc[bugunMetni(bas)] = Math.min(UST, Math.round(steps));
    } catch {
      // O gün için veri yoksa atla; sıfır yazma
    }
  }
  return sonuc;
}

/**
 * Sensör değerlerini kayıtlara işler. Kayıtlı sayı sensörden yüksekse (elle girilmişse) dokunmaz.
 * Değişen gün yoksa null döner; böylece veritabanına boş yere yazılmaz.
 */
export function adimlariIsle(v: Veri, sensor: Record<string, number>): Veri | null {
  const loglar = { ...(v.aktivite_loglari ?? {}) };
  let degisti = false;
  for (const [tarih, adim] of Object.entries(sensor)) {
    const g = loglar[tarih] ?? {};
    if (adim > Number(g.adim ?? 0)) {
      loglar[tarih] = { su: 0, egzersiz_kalori: 0, ...g, adim };
      degisti = true;
    }
  }
  return degisti ? { ...v, aktivite_loglari: loglar } : null;
}

const ARALIK_MS = 3 * 60 * 1000; // uygulama açıkken 3 dakikada bir tazele

/** Açılışta, uygulama öne geldiğinde ve açıkken birkaç dakikada bir sensörü okuyup kaydeder. */
export function useAdimSayar(veri: Veri, guncelle: (f: (v: Veri) => Veri) => Promise<void>): AdimDurumu | null {
  const [durum, setDurum] = useState<AdimDurumu | null>(null);
  const son = useRef(veri);
  son.current = veri;
  const yaz = useRef(guncelle);
  yaz.current = guncelle;
  const calisiyor = useRef(false);

  useEffect(() => {
    let iptal = false;
    const tazele = async () => {
      if (calisiyor.current) return;
      calisiyor.current = true;
      try {
        const d = await adimIzni();
        if (iptal) return;
        setDurum(d);
        if (d !== "var") return;
        const sensor = await sonGunlerinAdimi();
        if (!iptal && adimlariIsle(son.current, sensor)) await yaz.current((v) => adimlariIsle(v, sensor) ?? v);
      } catch {
        // Kayıt olmazsa bir sonraki tazelemede yeniden denenir
      } finally {
        calisiyor.current = false;
      }
    };
    tazele();
    const dinle = AppState.addEventListener("change", (h) => { if (h === "active") tazele(); });
    const sayac = setInterval(() => { if (AppState.currentState === "active") tazele(); }, ARALIK_MS);
    return () => { iptal = true; dinle.remove(); clearInterval(sayac); };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return durum;
}
