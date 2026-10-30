"""
nova_core.py - Nova'nın ortak yapay zeka motoru

Tek Gemini bağlantısı, birden çok mod (öğün, antrenman koçu, soru-cevap), kullanıcı başı
günlük limit, önbellek ve destek/sponsor alanı burada. Sayfalar sadece run_mode() çağırır.

Yeni mod eklemek için: bir şema (isteğe bağlı) + bir Mode kaydı + DAILY_LIMITS satırı yeterli.

Streamlit Secrets:
    GEMINI_API_KEY = "..."
    GEMINI_MODEL   = "gemini-2.5-flash-lite"      # isteğe bağlı
    SUPPORT_URL    = "https://..."                # isteğe bağlı (bağış/destek bağlantısı)
    SPONSOR_TEXT   = "..."  SPONSOR_URL = "..."   # isteğe bağlı (doğrudan sponsor yazısı)
"""

import io
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Type
from uuid import uuid4
from zoneinfo import ZoneInfo

import streamlit as st
from google import genai
from google.genai import types
from PIL import Image, ImageOps
from pydantic import BaseModel

# ------------------------------------------------------------------ Ayarlar
DEFAULT_MODEL = "gemini-2.5-flash-lite"
MAX_SIDE = 1024                                   # fotoğraf bu boyuta küçültülür
DAILY_LIMITS = {"meal": 5, "coach": 3, "ask": 15}  # kullanıcı başına günlük hak
GLOBAL_DAILY_LIMIT = 800                          # tüm kullanıcılar, tüm modlar (API çağrısı)


def cfg(name, default=None):
    """Streamlit Secrets'tan oku; yoksa varsayılanı döndür."""
    try:
        return st.secrets[name]
    except Exception:
        return default


# ------------------------------------------------------------ Yanıt şemaları
class FoodItem(BaseModel):
    name: str
    grams: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    confidence: float


class MealAnalysis(BaseModel):
    is_food: bool
    items: list[FoodItem]
    assumptions: str


class PlanExercise(BaseModel):
    exercise_id: str
    sets: int
    reps: str          # "8-12" ya da "30 sn"
    rest_sec: int
    note: str


class PlanDay(BaseModel):
    title: str
    focus: str
    exercises: list[PlanExercise]


class WorkoutPlan(BaseModel):
    summary: str
    days: list[PlanDay]
    safety_note: str


# ------------------------------------------------------------------ Talimatlar
SAFETY = """Genel kurallar:
- Tıbbi tanı koyma, ilaç veya doz önerme.
- Aşırı düşük kalori, uzun oruç, kusma ya da müshil gibi sağlıksız yöntemler önerme.
- Kullanıcı yeme bozukluğu belirtisi gösterirse (öğün atlama takıntısı, kusma, aşırı kısıtlama gibi) kalori, gram veya diyet sayısı verme; destekleyici ol ve bir sağlık uzmanına başvurmasını öner.
- Kullanıcı sakatlık, ağrı, hamilelik ya da kronik hastalık belirtirse genel bilgi ver ve bir uzmana danışmasını öner.
- Türkçe, sade ve kısa yaz."""

MEAL_SYSTEM = SAFETY + """

Görev: Sen deneyimli bir diyetisyensin. Fotoğraftaki öğünü analiz et.
- Her yemeği veya içeceği ayrı kalem olarak yaz (en fazla 8 kalem). Adlar Türkçe olsun.
- Gramajı tabak, çatal, kaşık, bardak gibi referans nesnelere bakarak tahmin et. Servis edilen (pişmiş) haliyle gram ver.
- Görünmeyen ama büyük olasılıkla kullanılmış yağ, sos, şeker gibi şeyleri (ör. zeytinyağı, tereyağı) ayrı kalem yap ve 'assumptions' alanında açıkla.
- Protein, karbonhidrat ve yağ değerlerini 100 gram için ver. Türk mutfağı için gerçekçi değerler kullan.
- confidence: 0 ile 1 arası, tahminden ne kadar emin olduğun.
- Fotoğrafta yiyecek yoksa is_food=false yap ve items'ı boş bırak.
- Emin değilsen uç değerlerden kaçın, makul orta bir tahmin ver."""

COACH_SYSTEM = SAFETY + """

Görev: Sen Nova'nın antrenman koçusun. Kullanıcı bilgilerine göre haftalık antrenman planı hazırla.
- SADECE aşağıda verilen egzersiz kütüphanesindeki exercise_id değerlerini kullan. Kütüphanede olmayan hareket uydurma.
- Gün sayısı kullanıcının istediği kadar olsun. Her gün 4 ile 7 hareket seç ve süreyi aşma.
- Başlangıç seviyesinde hacmi düşük tut: set sayısı 2 ile 4 arası, reps için aralık ("8-12") ya da süre ("30 sn") yaz.
- Aynı kas grubunu ardışık günlerde ağır çalıştırma.
- Kullanıcı sakatlık veya ağrı belirttiyse o bölgeyi zorlayan hareketlerden kaçın.
- note alanı: o hareket için kullanıcıya özel en fazla bir kısa cümle.
- safety_note: ısınma, ağrıda durma ve gerekirse uzmana danışma hakkında tek cümle."""

ASK_SYSTEM = SAFETY + """

Görev: Sen Nova'nın beslenme ve spor asistanısın. Sorulara en fazla yaklaşık 150 kelimeyle cevap ver.
Emin olmadığın şeyi uydurma, bilmediğini söyle."""


@dataclass(frozen=True)
class Mode:
    key: str
    label: str
    system: str
    schema: Optional[Type[BaseModel]] = None
    needs_image: bool = False
    temperature: float = 0.3


MODES = {
    "meal": Mode("meal", "Öğün taraması", MEAL_SYSTEM, MealAnalysis, needs_image=True, temperature=0.2),
    "coach": Mode("coach", "Antrenman koçu", COACH_SYSTEM, WorkoutPlan, temperature=0.4),
    "ask": Mode("ask", "Beslenme ve spor asistanı", ASK_SYSTEM, None, temperature=0.4),
}


# ----------------------------------------------------------- Kullanım sayacı
class QuotaError(Exception):
    """Günlük hak ya da genel kapasite doldu."""


@st.cache_resource
def _store():
    # Sunucu yeniden başlayınca sıfırlanır. Kalıcı sayaç için bu sözlüğü bir veritabanıyla değiştir.
    return {"lock": threading.Lock(), "day": None, "global": 0, "users": {}}


def _fresh():
    """Gemini kotası Pasifik saatiyle gece yarısı sıfırlandığı için günü ona göre say."""
    store = _store()
    today = datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
    with store["lock"]:
        if store["day"] != today:
            store["day"], store["global"], store["users"] = today, 0, {}
    return store


def user_key() -> str:
    """Önce uygulamanın kendi girişindeki kullanıcı adı, sonra Streamlit girişi (e-posta), yoksa oturum kimliği.
    Giriş varsa sayaç sayfa yenilemeyle sıfırlanamaz."""
    name = st.session_state.get("aktif_kullanici")
    if name:
        return f"user:{name}"
    try:
        if st.user.is_logged_in:
            email = getattr(st.user, "email", None)
            if email:
                return f"user:{email}"
    except Exception:
        pass
    return "sess:" + st.session_state.setdefault("_nova_sid", uuid4().hex)


def remaining(mode_key: str) -> int:
    used = _fresh()["users"].get((user_key(), mode_key), 0)
    return max(0, DAILY_LIMITS[mode_key] - used)


def _charge(mode_key: str):
    store = _fresh()
    with store["lock"]:
        k = (user_key(), mode_key)
        store["users"][k] = store["users"].get(k, 0) + 1


def _check_quota(mode_key: str):
    if remaining(mode_key) <= 0:
        raise QuotaError("Bu özellik için bugünkü hakkın doldu. Yarın tekrar dene.")
    if _fresh()["global"] >= GLOBAL_DAILY_LIMIT:
        raise QuotaError("Nova'nın bugünkü yapay zeka kapasitesi doldu. Yarın tekrar dene.")


# ------------------------------------------------------------- Gemini çağrısı
@st.cache_resource
def _client():
    key = cfg("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY bulunamadı. Streamlit Secrets'a ekle.")
    return genai.Client(api_key=key)


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def _call(mode_key: str, user_text: str, context: str, image_bytes: Optional[bytes], model: str) -> dict:
    """Aynı girdi için sonuç önbellekten gelir. Gövde sadece önbellek ıskalandığında çalışır."""
    mode = MODES[mode_key]
    store = _fresh()
    with store["lock"]:
        store["global"] += 1

    system = mode.system + ("\n\n" + context if context else "")
    kwargs = {"system_instruction": system, "temperature": mode.temperature}
    if mode.schema is not None:
        kwargs.update(response_mime_type="application/json", response_schema=mode.schema)

    contents = []
    if image_bytes:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))
    contents.append(user_text or "Analiz et.")

    response = _client().models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(**kwargs),
    )
    if mode.schema is not None:
        if response.parsed is None:
            raise RuntimeError("Yanıt okunamadı.")
        return response.parsed.model_dump()
    return {"text": (response.text or "").strip()}


def run_mode(mode_key: str, user_text: str = "", image_bytes: Optional[bytes] = None,
             context: str = "") -> dict:
    """Bir modu çalıştırır. Hak kontrolü yapar, başarılı olursa kullanıcının hakkından düşer."""
    mode = MODES[mode_key]
    if mode.needs_image and not image_bytes:
        raise ValueError("Bu mod için fotoğraf gerekli.")
    _check_quota(mode_key)
    result = _call(mode_key, user_text.strip(), context, image_bytes, cfg("GEMINI_MODEL", DEFAULT_MODEL))
    _charge(mode_key)
    return result


def friendly_error(e: Exception) -> str:
    text = str(e)
    if isinstance(e, QuotaError):
        return text
    if "429" in text or "RESOURCE_EXHAUSTED" in text:
        return "API kotası doldu. Biraz sonra tekrar dene."
    if "GEMINI_API_KEY" in text or "API key" in text or "401" in text or "403" in text:
        return "API anahtarı sorunu var. Anahtarı ve Secrets ayarını kontrol et."
    return f"İşlem yapılamadı: {text}"


# ---------------------------------------------------------------- Yardımcılar
def prepare_image(file) -> bytes:
    """Fotoğrafın dönüklüğünü düzeltir, küçültür, JPEG'e çevirir."""
    img = Image.open(file)
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


# ----------------------------------------------------------- Arayüz parçaları
def quota_caption(mode_key: str):
    st.caption(f"Bugünkü kalan hakkın: {remaining(mode_key)} / {DAILY_LIMITS[mode_key]}")


def support_slot():
    """Destek bağlantısı ve sponsor yazısı. Secrets'ta tanımlı değilse hiçbir şey çizmez."""
    sponsor_text, sponsor_url = cfg("SPONSOR_TEXT"), cfg("SPONSOR_URL")
    support_url = cfg("SUPPORT_URL")
    has_sponsor = bool(sponsor_text and sponsor_url)
    if not has_sponsor and not support_url:
        return
    with st.container(border=True):
        if has_sponsor:
            st.caption("Sponsor")
            st.markdown(f"[{sponsor_text}]({sponsor_url})")
        if support_url:
            st.link_button("Nova'yı destekle", support_url)


def show_limit_reached(message: str):
    st.warning(message)
    support_slot()
