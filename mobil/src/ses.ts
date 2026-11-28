// ses.ts - Öğünü sesle anlatmak için kısa ses kaydı (expo-audio)
// Ses yazıya telefonda çevrilmez: kayıt doğrudan yapay zeka sunucu fonksiyonuna gider
// (yapay-zeka "voice" modu, sitedeki meal_scan.py ile aynı yol). Gemini anahtarı telefonda yok.
// iPhone'da 16 kHz tek kanallı WAV kaydedilir: site de audio/wav gönderiyor; dakikası yaklaşık 2 MB.
import { useEffect, useRef, useState } from "react";
import { Platform } from "react-native";
import {
  AudioQuality, IOSOutputFormat, requestRecordingPermissionsAsync, setAudioModeAsync,
  useAudioRecorder, useAudioRecorderState, type RecordingOptions,
} from "expo-audio";
import { File } from "expo-file-system";

export const EN_UZUN_SN = 60;

const AYAR: RecordingOptions = {
  extension: ".wav",
  sampleRate: 16000,
  numberOfChannels: 1,
  bitRate: 256000,
  ios: {
    extension: ".wav", outputFormat: IOSOutputFormat.LINEARPCM, audioQuality: AudioQuality.HIGH, sampleRate: 16000,
    linearPCMBitDepth: 16, linearPCMIsBigEndian: false, linearPCMIsFloat: false,
  },
  android: { extension: ".m4a", outputFormat: "mpeg4", audioEncoder: "aac", sampleRate: 16000 },
  web: { mimeType: "audio/webm" },
};
const TUR = Platform.OS === "ios" ? "audio/wav" : Platform.OS === "android" ? "audio/mp4" : "audio/webm";

/** Dosyayı base64 okur: önce expo-file-system, olmazsa fetch + FileReader (web ve yedek yol) */
async function base64Oku(uri: string): Promise<string> {
  try {
    return await new File(uri).base64();
  } catch {
    const blob = await (await fetch(uri)).blob();
    return await new Promise<string>((coz, red) => {
      const r = new FileReader();
      r.onload = () => coz(String(r.result).split(",")[1] ?? "");
      r.onerror = () => red(r.error);
      r.readAsDataURL(blob);
    });
  }
}

export type SesSonucu = { ses_b64: string; ses_tur: string };

export function useSesKaydi() {
  const kaydedici = useAudioRecorder(AYAR);
  const durum = useAudioRecorderState(kaydedici, 250);
  const [hazirlaniyor, setHazirlaniyor] = useState(false);
  const bitince = useRef<(() => void) | null>(null);
  const sure = Math.floor((durum.durationMillis ?? 0) / 1000);

  // Süre dolunca kendiliğinden bitir
  useEffect(() => { if (durum.isRecording && sure >= EN_UZUN_SN) bitince.current?.(); }, [sure, durum.isRecording]);

  /** Kaydı başlatır. İzin yoksa "izin", başlayamazsa "hata" döner. */
  const baslat = async (otomatikBitir: () => void): Promise<"tamam" | "izin" | "hata"> => {
    setHazirlaniyor(true);
    try {
      const izin = await requestRecordingPermissionsAsync();
      if (!izin.granted) return "izin";
      await setAudioModeAsync({ allowsRecording: true, playsInSilentMode: true });
      await kaydedici.prepareToRecordAsync();
      kaydedici.record();
      bitince.current = otomatikBitir;
      return "tamam";
    } catch {
      return "hata";
    } finally {
      setHazirlaniyor(false);
    }
  };

  /** Kaydı durdurur ve dosyayı base64 olarak verir. Çok kısa ya da boşsa null. */
  const bitir = async (): Promise<SesSonucu | null> => {
    bitince.current = null;
    try {
      await kaydedici.stop();
      await setAudioModeAsync({ allowsRecording: false });
      const uri = kaydedici.uri;
      if (!uri) return null;
      const b64 = await base64Oku(uri);
      return b64.length > 2000 ? { ses_b64: b64, ses_tur: TUR } : null;
    } catch {
      return null;
    }
  };

  /** Kaydı gönderMEden bırakır */
  const vazgec = async () => {
    bitince.current = null;
    try { await kaydedici.stop(); await setAudioModeAsync({ allowsRecording: false }); } catch { /* boş */ }
  };

  return { kaydediyor: durum.isRecording, sure, hazirlaniyor, baslat, bitir, vazgec };
}
