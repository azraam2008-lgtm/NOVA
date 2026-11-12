"""
nova_pages.py - Antrenman koçu ve beslenme/spor asistanı sayfaları

    from nova_pages import coach_page, ask_page

    log = coach_page()      # kullanıcı "Antrenmanı kaydet"e basarsa sözlük döner
    if log:
        kaydet(log)         # {"day", "exercises": [{"id","name","sets_planned","sets_done","reps"}]}

    ask_page()

Koç, planı SADECE exercises.json içindeki hareketlerden kurar. Böylece her harekette senin
çektiğin video, ipuçları ve sık yapılan hatalar gösterilebilir. Kendi videonu bağlamak için
exercises.json'da ilgili hareketin "video" alanına bir bağlantı (YouTube, R2, Supabase vb.)
ya da repodaki göreli dosya yolu (örn. "videos/squat.mp4") yaz.
"""

import hashlib
import json
import re
from pathlib import Path
from typing import List, Optional

import streamlit as st

from nova_core import (
    QuotaError,
    friendly_error,
    quota_caption,
    run_mode,
    show_limit_reached,
    support_slot,
)

LIB_PATH = Path(__file__).parent / "exercises.json"
LEVELS = {"başlangıç": 0, "orta": 1, "ileri": 2}
EQUIPMENT_OPTIONS = {"Dambıl": "dambıl", "Bank": "bank", "Bar": "bar"}
GOALS = ["Kas kazanmak", "Genel kondisyon", "Güçlenmek"]


# ------------------------------------------------------- Saf yardımcı fonksiyonlar
def usable_exercises(library: List[dict], have: set, level: str) -> List[dict]:
    """Kullanıcının ekipmanıyla yapabileceği ve seviyesini aşmayan hareketler."""
    max_level = LEVELS.get(level, 0)
    return [
        ex for ex in library
        if set(ex.get("equipment", [])) <= have and LEVELS.get(ex.get("level", "başlangıç"), 0) <= max_level
    ]


def library_context(exercises: List[dict]) -> str:
    lines = ["Egzersiz kütüphanesi (id | ad | kas | seviye):"]
    lines += [f'- {e["id"]} | {e["name"]} | {e["muscle"]} | {e.get("level", "başlangıç")}' for e in exercises]
    return "\n".join(lines)


def filter_plan(plan: dict, valid_ids: set) -> dict:
    """Modelin uydurduğu (kütüphanede olmayan) hareketleri ve boş günleri ayıklar."""
    days = []
    for day in plan.get("days", []):
        exercises = [x for x in day.get("exercises", []) if x.get("exercise_id") in valid_ids]
        if exercises:
            days.append({**day, "exercises": exercises})
    return {**plan, "days": days}


def video_src(value: str) -> Optional[str]:
    """Bağlantıysa olduğu gibi, dosya yoluysa dosya varsa döndürür."""
    if not value:
        return None
    if value.startswith(("http://", "https://")):
        return value
    path = Path(__file__).parent / value
    return str(path) if path.exists() else None


@st.cache_data
def load_exercises() -> List[dict]:
    try:
        return json.loads(LIB_PATH.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []


# ------------------------------------------------------------------ Antrenman koçu
def _plan_form(library: List[dict]):
    with st.form("coach_form"):
        goal = st.selectbox("Hedefin", GOALS)
        level = st.selectbox("Seviyen", list(LEVELS))
        equipment = st.multiselect("Elindeki ekipman (boşsa ekipmansız)", list(EQUIPMENT_OPTIONS))
        c1, c2 = st.columns(2)
        days = c1.slider("Haftada kaç gün", 2, 6, 3)
        minutes = c2.slider("Antrenman süresi (dk)", 20, 90, 45, step=5)
        limits = st.text_input("Ağrı ya da sınırlaman var mı? (isteğe bağlı)", max_chars=200,
                               placeholder="Örn: sol dizimde ağrı var")
        submitted = st.form_submit_button("Planımı hazırla", type="primary")
    if not submitted:
        return None

    have = {EQUIPMENT_OPTIONS[e] for e in equipment}
    pool = usable_exercises(library, have, level)
    if len(pool) < 4:
        st.error("Bu seçimlerle yeterli hareket yok. exercises.json dosyasına hareket ekle.")
        return None

    request = (
        f"Hedef: {goal}\nSeviye: {level}\nHaftada {days} gün\nAntrenman süresi: {minutes} dakika\n"
        f"Ekipman: {', '.join(equipment) if equipment else 'ekipmansız'}\n"
        f"Ağrı veya sınırlama: {limits.strip() or 'yok'}"
    )
    with st.spinner("Plan hazırlanıyor..."):
        raw = run_mode("coach", request, context=library_context(pool))

    plan = filter_plan(raw, {e["id"] for e in pool})
    if not plan["days"]:
        st.error("Plan oluşturulamadı. Tekrar dene.")
        return None
    return plan


def _render_plan(plan: dict, by_id: dict, plan_id: str):
    st.info(plan["summary"])
    for di, day in enumerate(plan["days"]):
        # "1. Gün" gibi başlıklar markdown'da listeye dönüşmesin diye nokta kaçışlanır
        baslik = re.sub(r"^(\d+)\.", r"\1\\.", str(day["title"]))
        with st.expander(f'{baslik} · {day["focus"]}', expanded=(di == 0)):
            for ei, item in enumerate(day["exercises"]):
                ex = by_id[item["exercise_id"]]
                st.markdown(f'**{ex["name"]}**  \n{item["sets"]} set x {item["reps"]}, dinlenme {item["rest_sec"]} sn')
                src = video_src(ex.get("video", ""))
                if src:
                    st.video(src)
                else:
                    st.caption("Video yakında eklenecek.")
                if item.get("note"):
                    st.caption(item["note"])
                st.markdown("\n".join(f"- {t}" for t in ex.get("tips", [])))
                if ex.get("mistakes"):
                    st.caption("Sık yapılan hatalar: " + "; ".join(ex["mistakes"]))

                sets_max = max(1, min(int(item["sets"]), 10))
                c1, c2 = st.columns(2)
                c1.number_input("Tamamlanan set", 0, sets_max, 0, 1, key=f"done_{plan_id}_{di}_{ei}")
                c2.text_input("Tekrarlar (örn. 12-10-8)", key=f"reps_{plan_id}_{di}_{ei}", max_chars=40)
                st.divider()
    st.caption(plan["safety_note"])


def _save_log(plan: dict, by_id: dict, plan_id: str):
    st.markdown("#### Antrenmanı kaydet")
    di = st.selectbox("Hangi günü yaptın?", range(len(plan["days"])),
                      format_func=lambda i: plan["days"][i]["title"], key=f"day_{plan_id}")
    if not st.button("Antrenmanı kaydet", type="primary", key=f"savelog_{plan_id}"):
        return None

    done = []
    for ei, item in enumerate(plan["days"][di]["exercises"]):
        sets_done = st.session_state.get(f"done_{plan_id}_{di}_{ei}", 0)
        if sets_done > 0:
            done.append({
                "id": item["exercise_id"],
                "name": by_id[item["exercise_id"]]["name"],
                "sets_planned": item["sets"],
                "sets_done": sets_done,
                "reps": st.session_state.get(f"reps_{plan_id}_{di}_{ei}", "").strip(),
            })
    if not done:
        st.info("Önce tamamladığın setleri gir.")
        return None
    st.success("Antrenman kaydedildi.")
    return {"day": plan["days"][di]["title"], "exercises": done}


def coach_page():
    """Plan oluşturur, videolu hareketleri gösterir. Kaydedilirse antrenman günlüğü sözlüğü döner."""
    st.subheader("Antrenman koçu")
    library = load_exercises()
    if not library:
        st.error("exercises.json bulunamadı ya da boş.")
        return None
    by_id = {e["id"]: e for e in library}

    quota_slot = st.empty()
    try:
        try:
            new_plan = _plan_form(library)
        except QuotaError as e:
            show_limit_reached(str(e))
            new_plan = None
        except Exception as e:  # noqa: BLE001
            st.error(friendly_error(e))
            new_plan = None
        if new_plan:
            st.session_state["nova_plan"] = new_plan

        plan = st.session_state.get("nova_plan")
        if not plan:
            return None
        plan_id = hashlib.md5(json.dumps(plan, sort_keys=True).encode()).hexdigest()[:8]
        _render_plan(plan, by_id, plan_id)
        log = _save_log(plan, by_id, plan_id)
        support_slot()
        return log
    finally:
        with quota_slot.container():
            quota_caption("coach")


# ------------------------------------------------------------ Beslenme / spor asistanı
ONERILER = [
    "🥗 Antrenmandan sonra ne yemeliyim?",
    "🥩 Günde ne kadar protein almalıyım?",
    "🌙 Akşam acıkınca ne atıştırabilirim?",
    "💧 Daha çok su içmeyi nasıl alışkanlık yaparım?",
]
ASISTAN_AVATAR = "🦢"


def _oneri_sec(metin: str):
    st.session_state["ask_pending"] = metin.split(" ", 1)[1] if " " in metin else metin


def ask_page():
    """Sohbet görünümlü soru-cevap. Son birkaç mesajı bağlam olarak gönderir."""
    st.markdown(
        """<div class="nova-sohbet-baslik"><div class="nova-sohbet-logo">🦢</div>
        <div><b>Nova Asistan</b><small>Beslenme ve spor sorularını yanıtlar · tıbbi tavsiye değildir</small></div></div>""",
        unsafe_allow_html=True,
    )
    quota_slot = st.empty()
    history = st.session_state.setdefault("ask_history", [])

    try:
        sohbet = st.container(key="nova_sohbet", height=440) if history else st.container(key="nova_sohbet")
        with sohbet:
            if not history:
                with st.chat_message("assistant", avatar=ASISTAN_AVATAR):
                    st.markdown("Merhaba! 👋 Beslenme, antrenman ya da günlük alışkanlıklar hakkında merak ettiğin her şeyi sorabilirsin. Aşağıdaki örneklerden birine dokunarak da başlayabilirsin.")
            for question, answer in history[-10:]:
                with st.chat_message("user"):
                    st.markdown(question)
                with st.chat_message("assistant", avatar=ASISTAN_AVATAR):
                    st.markdown(answer)

        if not history:
            with st.container(key="nova_oneriler"):
                cols = st.columns(2)
                for i, oneri in enumerate(ONERILER):
                    cols[i % 2].button(oneri, key=f"oneri_{i}", width="stretch", on_click=_oneri_sec, args=(oneri,))

        yazilan = st.chat_input("Nova'ya bir soru sor...", max_chars=500, key="ask_input")
        question = (yazilan or st.session_state.pop("ask_pending", None) or "").strip()

        if question:
            recent = "\n".join(f"Kullanıcı: {q}\nNova: {a}" for q, a in history[-3:])
            text = (f"Önceki konuşma:\n{recent}\n\n" if recent else "") + f"Yeni soru: {question}"
            with sohbet:
                with st.chat_message("user"):
                    st.markdown(question)
                with st.chat_message("assistant", avatar=ASISTAN_AVATAR):
                    try:
                        with st.spinner("Nova yazıyor..."):
                            answer = run_mode("ask", text)["text"]
                    except QuotaError as e:
                        show_limit_reached(str(e))
                        answer = None
                    except Exception as e:  # noqa: BLE001
                        st.error(friendly_error(e))
                        answer = None
            if answer is not None:
                history.append((question, answer or "Cevap üretilemedi, tekrar dene."))
                st.rerun()

        if history and st.button("🧹 Sohbeti temizle", key="sohbet_temizle"):
            history.clear()
            st.rerun()
    finally:
        with quota_slot.container():
            quota_caption("ask")
