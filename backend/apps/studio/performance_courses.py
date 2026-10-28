"""Source-bound courses with reviewed sparse notes and complete final stages."""
from functools import lru_cache
import json
from pathlib import Path

from .content import tr
from .curated_lessons import note_name, midi_titles
from .ivory_repertoire import GROUP_BY_CODE
from .performance_course_plans import PLANS
from .repertoire import SOURCE_BY_CODE, repertoire_source
from .repertoire_studies import stages, source_window, time_range

NOTE_REVIEW = json.loads(Path(__file__).with_name("performance_course_notes.json").read_text(encoding="utf-8"))

READY = tr(
    "Kuy yoki bassning keyingi tayanchini oldindan eshitasiz, kirish va bo‘shatishlarni adashtirmaysiz, ikkinchi qatlam qo‘shilganda to‘xtamaysiz. Uchta xotirjam urinishda shu belgilar saqlansa, keyingi bosqichni sinang. Original tezlikka yetish shart emas: ravonlik birinchi o‘rinda.",
    "Вы заранее слышите следующую опору мелодии или баса, различаете атаку и отпускание и не останавливаетесь при добавлении второго слоя. Если это сохраняется в трёх спокойных попытках, пробуйте следующий этап. Достичь исходной скорости необязательно: плавность важнее.",
    "You can anticipate the next melodic or bass landmark, distinguish attacks from releases and continue when the second layer joins. Try the next stage after three unhurried attempts with those qualities. Reaching source speed is optional; fluency comes first.")

METHOD = tr(
    "Bosqichlar: tanlangan asl tayanchlar 60%; diqqat qilinayotgan qatlam to‘liq 80%; ikkala qatlam to‘liq 60%, keyin 80%, so‘ng original 100%. Yangi tovushlar qo‘shilganda tezlik ataylab pasayadi. Olib tashlangan notalar o‘rnidagi vaqt siqilmaydi; barcha qolgan kirishlar, ushlashlar va kuch bir xil nisbatda saqlanadi. Dars faqat ko‘rsatilgan oraliqni oladi, shuning uchun uning oxiridagi davom etayotgan tovush shu chegarada tugashi mumkin. Playerdagi umumiy tezlik bu tayyor bosqich tezligiga yana ta’sir qiladi: yozuvni aynan ko‘rsatilgan tezlikda eshitish uchun toolbarni 100% qiling.",
    "Этапы: выбранные исходные опоры на 60%; полный изучаемый слой на 80%; оба слоя полностью на 60%, затем 80% и исходные 100%. При добавлении нот скорость намеренно снижается. Время пропущенных нот не сжимается; все оставшиеся атаки, удержания и сила сохраняются в одном масштабе. Урок ограничен указанным отрезком, поэтому звучащая у его конца нота может закончиться на границе. Общая скорость плеера дополнительно масштабирует готовый этап: для обозначенной скорости установите в панели 100%.",
    "Stages: selected source landmarks at 60%; the complete focused layer at 80%; both complete layers at 60%, then 80%, then source 100%. Speed deliberately drops when notes are added. Omitted notes leave their time slots intact; remaining attacks, holds and velocities preserve their relationships. The lesson covers only its stated passage, so a note still sounding at the end can be clipped there. The player's global speed further scales the prepared stage: set the toolbar to 100% to hear the stated stage speed.")

LISTEN_CHECKS = {
    "melody": tr(
        "Namunani bir marta eshitib, pauza qiling va birinchi yo‘lni klavishsiz kuylang. Qaysi tovushga yetganda musiqa xotirjamroq yoki davom etishga intilayotgandek tuyuldi? Keyin to‘liq yuqori qatlamni ochib, aynan shu yo‘lni qo‘shimcha tovushlar orasidan toping. Farq eshitilmasa, birinchi bir necha kirishga qayting; butun parchani birdan yodlash shart emas.",
        "Прослушайте пример, поставьте паузу и напойте первую линию без клавиш. На каком звуке появилось ощущение покоя или продолжения? Затем откройте полный верхний слой и найдите ту же линию среди дополнительных тонов. Если различие не слышно, вернитесь к нескольким первым вступлениям; не нужно запоминать весь отрезок сразу.",
        "Listen once, pause and sing the opening line without touching the keys. Which arrival feels restful or seems to lead onward? Open the complete upper layer and find that same route among the added tones. If the distinction is unclear, return to the first few entries rather than memorising the entire passage at once."),
    "bass": tr(
        "Avval faqat pastki namunani tinglang va yangi bass kelganda bitta yengil urish bilan belgilang. Keyin ikkala qatlamli bosqichni ochib, aynan o‘sha joylarni yana belgilang. Yuqori kuy qo‘shilganda pastki kirishlar o‘zgardimi yoki faqat eshitishingiz qiyinlashdimi? Pauzada ikkala bosqichni solishtiring: tanlangan oraliq va vaqt nisbatlari bir xil qolgan.",
        "Послушайте только нижний пример, отмечая новый бас одним лёгким постукиванием. Затем откройте этап двух слоёв и отметьте те же места. Изменились ли нижние вступления после добавления мелодии или их стало труднее слышать? Сравните этапы на паузе: отрезок и временные пропорции сохранены.",
        "Hear the lower example alone, marking each new bass with a light tap. Open the two-layer stage and mark the same arrivals again. Did the lower entries change when the melody joined, or did they simply become harder to hear? Compare the stages while paused; the passage and its timing relationships are preserved."),
    "coordination": tr(
        "Bitta yangi bass kirishini tanlab, playerni undan oldin pauza qiling. Keyingi yuqori tovush bass bilan birgami, undan oldinmi yoki keyinmi? Avval taxmin qiling, keyin juda sekin ijroda tekshiring. Keyingi urinishda shu kichik voqeani ko‘rmasdan eshitishga harakat qiling. Bu ikki qo‘lni har tovushda majburan birga bosish odatini ajratadi.",
        "Выберите одно новое вступление баса и поставьте паузу перед ним. Следующий верхний звук совпадёт с басом, появится раньше или позже? Сначала предположите, затем проверьте на очень медленной скорости. В следующей попытке услышьте этот момент без зрительной подсказки. Так проще отказаться от привычки насильно совмещать каждую атаку рук.",
        "Choose one new bass entry and pause just before it. Will the next upper tone arrive with it, before it or after it? Predict first, then check with very slow playback. On another attempt, hear that small event without a visual cue. This helps separate the hands instead of forcing every attack to coincide."),
}


def reviewed_selection(parsed, plan, note_ids):
    selection = {}
    for hand in ("right", "left"):
        candidates = sorted((e for e in parsed["events"] if e["hand"] == hand
                             and plan["start"] <= e["onset_seconds"] < plan["end"]),
                            key=lambda e: e["onset_seconds"])
        by_id = {e["id"]: i for i, e in enumerate(candidates)}
        identifiers = note_ids[hand]
        if len(identifiers) != len(set(identifiers)) or any(key not in by_id for key in identifiers):
            raise ValueError("A reviewed course landmark is missing from its pinned source window.")
        selection[hand] = sorted(by_id[key] for key in identifiers)
    if not any(selection.values()):
        raise ValueError("A course needs audible reviewed landmarks.")
    return selection


def example(parsed, plan, selection):
    hand = "left" if plan["mode"] == "bass" else "right"
    events = sorted((e for e in parsed["events"] if e["hand"] == hand
                     and plan["start"] <= e["onset_seconds"] < plan["end"]), key=lambda e: e["onset_seconds"])
    selected = [events[i] for i in selection[hand]]
    first = selected[0]
    route = " → ".join(note_name(e["pitch"]["midi"]) for e in selected[:7])
    name = note_name(first["pitch"]["midi"])
    at, hold = first["onset_seconds"], first["duration_seconds"]
    return tr(
        f"Birinchi bosqichdagi aniq yo‘l: {route}. To‘liq yozuvdagi {name} {at:.3f}-soniyada boshlanadi, klavish {hold:.3f} soniya ushlanadi. Dars taymerining noli esa {plan['start']:.2f}-soniyadan boshlanadi; 60% bosqich vaqtlarni 100/60 marta cho‘zadi. C4 kabi raqam oktava registrini, ♯ yarim ton ko‘tarishni bildiradi. Rang yuqori/pastki qatlamni ajratadi; u majburiy barmoqlash emas.",
        f"Точный путь первого этапа: {route}. В полной записи {name} начинается на {at:.3f} с и удерживается {hold:.3f} с. Ноль таймера урока соответствует {plan['start']:.2f} с записи; этап 60% растягивает времена в 100/60 раза. Цифра в C4 обозначает октаву, ♯ — повышение на полутон. Цвет различает верхний/нижний слой, а не обязательную аппликатуру.",
        f"The first stage follows these exact notes: {route}. In the complete recording {name} starts at {at:.3f} s and is held for {hold:.3f} s. Lesson time zero corresponds to {plan['start']:.2f} s in the recording; the 60% stage scales times by 100/60. The number in C4 identifies the octave and ♯ raises a note one semitone. Colour separates upper/lower layers, not mandatory fingering.")


def binding(source):
    group = GROUP_BY_CODE[source.code]
    primary = group["variants"][0]
    value = {"playback_revision": source.sha256[:16]}
    if len(group["variants"]) > 1:
        value["composition_variant_id"] = primary["id"]
    return value


def related_ids(topics):
    exercises = {"leaps", "coordination", "balance", "articulation"}
    return [f"exercise:{topic}:easy" if topic in exercises else "theory:keyboard" if topic == "transposition" else f"theory:{topic}" for topic in topics]


@lru_cache(maxsize=1)
def performance_items():
    if set(PLANS) != set(NOTE_REVIEW):
        raise ValueError("Every performance course needs an exact note review.")
    result = []
    for code, plans in PLANS.items():
        source = SOURCE_BY_CODE[code]
        review = NOTE_REVIEW[code]
        if source.sha256 != review["source_sha256"] or {p["code"] for p in plans} != set(review["lessons"]):
            raise ValueError(f"{code}: review the course before changing its recording or lesson plan.")
        _, parsed = repertoire_source(code)
        duration = parsed["metadata"]["duration_seconds"]
        source_binding = binding(source)
        for plan in plans:
            key = f"lesson:{code}:{plan['code']}"
            start, end = plan["start"], plan["end"]
            if not 0 <= start < end <= duration:
                raise ValueError(f"{code}: the reviewed lesson lies outside its recording.")
            selection = reviewed_selection(parsed, plan, review["lessons"][plan["code"]])
            variants = midi_titles(source, stages(source, parsed, key, start, end, plan["mode"]))
            variants[0]["_generator"]["selection"] = selection
            # A coordination study adds the full upper texture over these exact
            # lower landmarks, rather than recomputing arbitrary bass buckets.
            if plan["mode"] == "coordination":
                variants[1]["_generator"]["selection"]["left"] = selection["left"]
            for stage in variants:
                if source_binding.get("composition_variant_id"):
                    stage["composition_variant_id"] = source_binding["composition_variant_id"]
            result.append({
                "id": key, "kind": "lesson", "_composition": code, "title": plan["title"],
                "subtitle": time_range(start, end), "intro": plan["practice"],
                "category": "expression" if plan["mode"] == "melody" else "coordination",
                "goals": ["accuracy", "understanding", "musicality"], "level": None, "minutes": 12,
                "explanation": [
                    {"title": tr("Tushuncha va shu asardagi ma’nosi", "Понятие и его смысл в этом произведении", "The concept in this piece"), "text": plan["concept"]},
                    {"title": tr("Shu MIDI’dan aniq misol", "Точный пример из этого MIDI", "An exact example from this MIDI"), "text": example(parsed, plan, selection)},
                    {"title": tr("Avval nimani tinglaymiz?", "Что слушаем сначала?", "What to listen for first"), "text": plan["practice"]},
                    {"title": tr("Oson variantdan originalga", "От простого варианта к оригиналу", "From a simpler version to the original"), "text": METHOD},
                    {"title": tr("Ko‘p uchraydigan xato", "Частая ошибка", "A common pitfall"), "text": plan["pitfall"]},
                    {"title": tr("Quloq bilan tekshiring", "Проверьте на слух", "Check it by ear"), "text": LISTEN_CHECKS[plan["mode"]]},
                ],
                "steps": [{"title": s["title"], "instruction": s["instruction"]} for s in variants],
                "stages": variants, "source": {**source_window(start, end), **source_binding},
                "ready_when": READY, "related_ids": related_ids(plan["related"]),
            })
        key = f"journey:{code}:complete"
        # A full performance should keep all notes even at the slowest speed;
        # sparse introductions belong to the short, focused lessons above.
        complete = midi_titles(source, stages(source, parsed, key, 0, duration, "coordination", complete=True))[2:]
        for stage in complete:
            if source_binding.get("composition_variant_id"):
                stage["composition_variant_id"] = source_binding["composition_variant_id"]
        result.append({
            "id": key, "kind": "journey", "_composition": code,
            "title": tr(source.title + ": to‘liq ijroga", source.title + ": к полному исполнению", source.title + ": toward the complete performance"),
            "subtitle": time_range(0, duration), "intro": tr("Alohida darslardan keyin asarni boshidan oxirigacha ulang.", "После отдельных уроков соедините произведение от начала до конца.", "After the focused lessons, join the work from beginning to end."),
            "category": "coordination", "goals": ["fluency", "musicality"], "level": None, "minutes": 15,
            "source": {**source_window(0, duration), **source_binding}, "stages": complete,
            "steps": [{"title": s["title"], "instruction": s["instruction"]} for s in complete],
            "explanation": [{"title": tr("Barcha notalar saqlangan", "Все ноты сохранены", "Every note is retained"),
                "text": tr("Uch bosqichning hammasida ikkala qatlam to‘liq: 60%, 80% va manbaning o‘zi. Sekin variantlarda butun vaqt bir xil nisbatda cho‘zilgan, oxirgi bosqich esa original MIDI’ni ochadi. Qiyin joyda to‘xtasangiz, unga mos qisqa darsga qayting; avtomatik takrorlash yo‘q. Har qatlamni eshitib, asarni uzluksiz davom ettirishni maqsad qiling.", "Во всех трёх этапах оба слоя полные: 60%, 80% и сам источник. Медленные варианты равномерно растягивают время, последний открывает оригинальный MIDI. При трудностях вернитесь к подходящему короткому уроку; автоматического повтора нет. Цель — слышать каждый слой и продолжать произведение без остановок.", "All three stages retain both complete layers: 60%, 80% and the source itself. Slow versions scale the entire timeline uniformly; the final stage opens the original MIDI. Return to a focused lesson for a difficult spot; playback does not loop automatically. Aim to hear both layers and continue through the work without stopping.") }],
            "ready_when": READY, "related_ids": [f"lesson:{code}:{p['code']}" for p in plans],
        })
    return result
