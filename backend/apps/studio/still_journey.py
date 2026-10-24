"""Source-derived continuity studies. The original MIDI is never rewritten.

Foundation retains the upper note of attacks grouped within 45ms and every
left-track attack at or below C3. Bridge restores the complete upper track.
These are explicit register/texture reductions, not inferred chords or meter.
"""
from functools import lru_cache
from .midi_authoring import source_data


def tr(uz, ru, en):
    return {"uz": uz, "ru": ru, "en": en}


WINDOWS = [
    ("part-one", 0, 48, tr("1-qism: boshlanishdan yuqori registrgacha", "Часть 1: от вступления к верхнему регистру", "Part 1: opening to the upper register")),
    ("part-two", 48, 112, tr("2-qism: uzun yo‘lni davom ettirish", "Часть 2: сохранить длинную линию", "Part 2: sustain the longer line")),
    ("part-three", 112, 196, tr("3-qism: keyingi katta yo‘l", "Часть 3: следующая большая линия", "Part 3: the next extended passage")),
    ("ending", 196, None, tr("4-qism: yakunni ravon tugatish", "Часть 4: плавно завершить", "Part 4: a continuous ending")),
    ("join-one", 40, 56, tr("1–2 qismlarni bog‘lash", "Соединить части 1–2", "Connect parts 1–2")),
    ("join-two", 104, 120, tr("2–3 qismlarni bog‘lash", "Соединить части 2–3", "Connect parts 2–3")),
    ("join-three", 188, 204, tr("3-qismdan yakunga o‘tish", "От части 3 к завершению", "Connect part 3 to the ending")),
    ("complete", 0, None, tr("Still: boshidan oxirigacha", "Still: от начала до конца", "Still: from beginning to end")),
]
TITLES = [tr("Siyrak tayanchlar", "Разреженная опора", "Sparse landmarks"), tr("Yuqori qatlam to‘liq", "Полный верхний голос", "Complete upper texture"), tr("Original ijro", "Исходное исполнение", "Original performance")]
SUBTITLES = [
    tr("0:00–0:48 · bas tayanchlari va yuqori yo‘l", "0:00–0:48 · басовые опоры и верхняя линия", "0:00–0:48 · bass landmarks and the upper line"),
    tr("0:48–1:52 · registr ko‘chishlarida ravonlik", "0:48–1:52 · плавность при смене регистра", "0:48–1:52 · continuity through register changes"),
    tr("1:52–3:16 · oldindan tayyorgarlik va muvozanat", "1:52–3:16 · подготовка и баланс", "1:52–3:16 · preparation and balance"),
    tr("3:16–3:34 · so‘nggi ibora va jarang", "3:16–3:34 · последняя фраза и звучание", "3:16–3:34 · the last phrase and its resonance"),
    tr("0:40–0:56 · yuqori registrga uzluksiz kirish", "0:40–0:56 · непрерывный вход в верхний регистр", "0:40–0:56 · a continuous entry into the upper register"),
    tr("1:44–2:00 · ikki qo‘l joylashuvini bog‘lash", "1:44–2:00 · соединить позиции обеих рук", "1:44–2:00 · connect the hand positions"),
    tr("3:08–3:24 · yakuniy iboraga tayyorlanish", "3:08–3:24 · подготовить последнюю фразу", "3:08–3:24 · prepare for the ending phrase"),
    tr("3:34 · butun asar, uch bosqich", "3:34 · всё произведение, три этапа", "3:34 · the complete piece in three stages"),
]
TASKS = [
    tr("Yuqori qatlamning yaqin kirishlarida eng yuqori nota qoldirilgan. Chapda C3 va undan past asl bas kirishlari bor. Tushirib qoldirilgan notalarni o‘zingiz to‘ldirmang; sukut ichida ichki vaqtni davom ettiring. Namuna original tezlikning 60% ida.", "В близких вступлениях верхнего голоса оставлена верхняя нота, слева — исходные басовые вступления C3 и ниже. Не заполняйте пропуски; сохраняйте внутреннее время. Темп — 60% исходного.", "Near-simultaneous upper-track attacks retain the highest note; the left hand retains original C3-and-lower bass attacks. Do not fill omitted notes. Keep inner time through silence at 60% source speed."),
    tr("O‘ng qatlamdagi barcha asl notalar qaytdi; chapda oldingi bas tayanchlari qoladi. Juft notalar orasida yuqori yo‘lni eshitib boring. Bu namuna original tezlikning 80% ida.", "Все исходные ноты верхнего голоса восстановлены; слева остаются прежние басовые опоры. Слушайте верхнюю линию внутри пар. Темп — 80% исходного.", "All original upper-track notes return over the same bass landmarks. Hear the upper line within the pairs at 80% source speed."),
    tr("Ikkala qatlamning barcha asl notalari va tezligi. Bo‘laklar chegarasida to‘xtamasdan, keyingi qo‘l joyini oldindan tayyorlang. Zarur bo‘lsa player tezligini o‘zingiz pasaytiring.", "Все исходные ноты обоих голосов в исходном темпе. Готовьте следующую позицию заранее и проходите границы без остановки. При необходимости снизьте скорость плеера.", "All original attacks in both tracks at source speed. Prepare the next hand position before each boundary and keep moving through it. Lower player speed when useful."),
]


def reduction_selection(parsed, start, end):
    right = sorted((event for event in parsed["events"] if event["hand"] == "right" and start <= event["onset_seconds"] < end), key=lambda event: event["onset_seconds"])
    left = sorted((event for event in parsed["events"] if event["hand"] == "left" and start <= event["onset_seconds"] < end), key=lambda event: event["onset_seconds"])
    groups = []
    for index, event in enumerate(right):
        if not groups or event["onset_seconds"] - right[groups[-1][0]]["onset_seconds"] > .045:
            groups.append([])
        groups[-1].append(index)
    upper = [max(group, key=lambda index: right[index]["pitch"]["midi"]) for group in groups]
    bass = [index for index, event in enumerate(left) if event["pitch"]["midi"] <= 48]
    return {"right": upper, "left": bass}, {"right": "all", "left": bass}


@lru_cache(maxsize=1)
def journey_items():
    _, parsed = source_data()
    end_of_file = parsed["metadata"]["duration_seconds"]
    result = []
    for number, (code, start, end, title) in enumerate(WINDOWS):
        end = end if end is not None else end_of_file
        key = "journey:still:" + code
        easy, bridge = reduction_selection(parsed, start, end)
        stages = []
        for index, selection in enumerate([easy, bridge, {"right": "all", "left": "all"}]):
            reuse_original = code == "complete" and index == 2
            asset = ("composition:still:original" if reuse_original else key if (index == 2 or code == "complete" and index == 0) else f"{key}:stage:{index+1}")
            stages.append({"id": f"{key}:stage:{index+1}", "title": TITLES[index], "instruction": TASKS[index], "source_speed_percent": [60,80,100][index], "_asset_key": asset,
                "_reuse_original": reuse_original,
                "_generator": {"start": start, "end": end, "selection": selection, "speed_percent": [60,80,100][index]}})
        intro = tr("Asl ijrodan olingan uzun qism. Uch bosqich bilan siyrak tayanchlardan to‘liq fakturaga o‘ting; bo‘limlarni istalgan tartibda ochishingiz mumkin.", "Длинный отрезок исходного исполнения. Три этапа ведут от разреженной опоры к полной фактуре; любой этап доступен сразу.", "An extended passage from the source performance. Three stages move from sparse landmarks to the full texture; every stage is freely available.")
        result.append({"id": key, "kind": "journey", "title": title, "subtitle": SUBTITLES[number], "intro": intro, "category": "coordination", "goals": ["accuracy", "musicality"], "level": None, "minutes": 12, "stages": stages,
            "source": {"start_seconds": start, "end_seconds": end, "transformation": tr("Tanlangan notalar → to‘liq yuqori qatlam → original", "Выбранные ноты → полный верх → оригинал", "Selected attacks → full upper track → original")},
            "explanation": [{"title": tr("Qismdan butun ijroga", "От фрагмента к целому", "From passage to complete performance"), "text": tr("Bu vaqt chegaralari mashq uchun tanlangan, partituradagi formal bo‘limlar emas. Qismlarni qulay chalgach, ularni kesib o‘tadigan bog‘lash mashqini oching. So‘ng to‘liq asarda o‘sha o‘tishni eshiting.", "Границы выбраны для занятий, это не формальные разделы партитуры. Освоив части, откройте упражнение, пересекающее границу, затем услышите переход в полном произведении.", "These time boundaries are practice selections, not claims about formal score sections. Once each part feels comfortable, use the study spanning the boundary, then hear the transition in the complete piece.")},
                {"title": tr("Oldindan tayyorlaning", "Подготовьтесь заранее", "Prepare before the change"), "text": tr("Qiyin o‘tishdan oldingi oxirgi ikki tovushda keyingi bas va qo‘l shaklini ko‘z bilan toping. Oxirgi notani qisqartirmasdan keyingi joyga o‘ting. Qo‘lni uzoqqa tez tashlashdan ko‘ra, vaqtida tayyorlashga e’tibor bering.", "На последних двух звуках перед переходом заранее найдите следующий бас и форму руки. Не укорачивайте окончание ради переноса; важна своевременная подготовка.", "During the final two notes before a transition, locate the next bass and hand shape. Keep the ending intact while preparing the move; focus on timely preparation rather than a fast jump.")}],
            "steps": [{"title": TITLES[index], "instruction": TASKS[index]} for index in range(3)],
            "ready_when": tr("Tanlagan bosqichni bo‘limlar chegarasida to‘xtamasdan va pulsni yo‘qotmasdan chala olsangiz, keyingi fakturani sinab ko‘ring.", "Попробуйте следующий этап, когда проходите границы без остановки и потери пульса.", "Try the next texture when you can cross the boundaries without stopping or losing pulse."),
            "related_ids": ["theory:practice", "theory:phrasing"]})
    return result
