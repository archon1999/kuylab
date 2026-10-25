"""Compile reviewed lesson plans into deterministic source-note selections."""
from functools import lru_cache
from .repertoire import SOURCES, repertoire_source
from .repertoire_courses import COURSES, tr
from .repertoire_pedagogy import review_blocks


def landmarks(parsed, start, end, floor=0):
    hands = {
        hand: sorted((event for event in parsed["events"] if event["hand"] == hand
                      and start <= event["onset_seconds"] < end),
                     key=lambda event: event["onset_seconds"])
        for hand in ("right", "left")
    }
    groups = []
    for index, event in enumerate(hands["right"]):
        if event["pitch"]["midi"] < floor:
            continue
        if not groups or event["onset_seconds"] - hands["right"][groups[-1][0]]["onset_seconds"] > .045:
            groups.append([])
        groups[-1].append(index)
    upper = [max(group, key=lambda index: hands["right"][index]["pitch"]["midi"]) for group in groups]
    lower = {}
    for index, event in enumerate(hands["left"]):
        bucket = int((event["onset_seconds"] - start) / 2)
        previous = lower.get(bucket)
        if previous is None or event["pitch"]["midi"] < hands["left"][previous]["pitch"]["midi"]:
            lower[bucket] = index
    return upper, list(lower.values())


def stages(source, parsed, item_id, start, end, mode, floor=0, complete=False):
    upper, bass = landmarks(parsed, start, end, floor)
    if mode == "melody":
        selections = [{"right": upper, "left": []}, {"right": "all", "left": []}]
        titles = [tr("Kuy tayanchlari", "Опоры мелодии", "Melodic landmarks"),
                  tr("To‘liq yuqori qatlam", "Полный верхний слой", "Complete upper layer")]
        instructions = [
            tr("Ajratilgan yuqori tayanchlarni 60% asl tezlikda tinglang va chaling. Tushirilgan tovushlar o‘rnidagi vaqtni siqmang; darsdagi kuy yo‘nalishini kuzating.", "Слушайте и играйте выделенные верхние опоры на 60% исходной скорости. Не сжимайте промежутки удалённых нот; следуйте мелодической линии урока.", "Hear and play the selected upper landmarks at 60% source speed. Keep the time slots of omitted notes and follow the lesson's melodic line."),
            tr("Yuqori qatlamning barcha asl tovushlari 80% tezlikda qaytdi; pastki qatlam hali yo‘q. Kuy bilan ichki tovushlar balansi va qayta bosishlarni boshqaring.", "Все исходные верхние ноты возвращены на 80%; нижнего слоя пока нет. Управляйте балансом мелодии, внутренних тонов и повторных нажатий.", "All original upper-layer tones return at 80%, without the lower layer yet. Control the melody, inner-tone balance and repeated attacks."),
        ]
    elif mode == "bass":
        selections = [{"right": [], "left": bass}, {"right": [], "left": "all"}]
        titles = [tr("Pastki tayanchlar", "Нижние опоры", "Lower landmarks"),
                  tr("To‘liq pastki qatlam", "Полный нижний слой", "Complete lower layer")]
        instructions = [
            tr("Pastki qatlamning siyrak tayanchlari 60% asl tezlikda. Yangi pastki klavishni oldindan toping va tayanchlar orasida ichki vaqtni davom ettiring.", "Редкие нижние опоры на 60% исходной скорости. Заранее находите следующую клавишу и сохраняйте внутреннее время между вступлениями.", "Sparse lower landmarks at 60% source speed. Locate the next low key early and keep inner time between attacks."),
            tr("Pastki qatlamning barcha asl tovushlari 80% tezlikda qaytdi; yuqori qatlam hali yo‘q. Yangi bassga borish uchun oldingi tovushlarni shoshirmang.", "Все исходные нижние ноты возвращены на 80%, без верхнего слоя. Не торопите предыдущие звуки ради следующего баса.", "All original lower-layer tones return at 80%, without the upper layer yet. Do not rush earlier tones to reach the next bass."),
        ]
    else:
        selections = [{"right": upper, "left": bass}, {"right": "all", "left": bass}]
        titles = [tr("Ikki qatlam tayanchlari", "Опоры двух слоёв", "Landmarks in both layers"),
                  tr("Kuy va siyrak bass", "Мелодия и редкий бас", "Upper texture over sparse bass")]
        instructions = [
            tr("Ikki qatlamdan tanlangan tayanchlar 60% asl tezlikda. Birga keladigan va navbat bilan kiradigan tovushlarni ajrating; bo‘shliqlar asl vaqtini saqlaydi.", "Выбранные опоры обоих слоёв на 60%. Различайте совместные и последовательные вступления; промежутки сохраняют исходное время.", "Selected landmarks in both layers at 60%. Distinguish shared attacks from staggered entries; gaps preserve the source timing."),
            tr("Yuqori qatlam to‘liq, pastda siyrak asl tayanchlar: 80% tezlik. Band yuqori yo‘l yangi bassning vaqtini o‘zgartirmasin.", "Полный верх над редкими исходными нижними опорами на 80%. Активный верх не должен менять время нового баса.", "The complete upper layer over sparse source bass landmarks at 80%. A busier upper line should not change bass arrival times."),
        ]
    selections.extend({"right": "all", "left": "all"} for _ in range(3))
    titles.extend([
        tr("Ikki qo‘l · sekin", "Две руки · медленно", "Both hands · slow"),
        tr("Ikki qo‘l · ravon", "Две руки · плавно", "Both hands · flowing"),
    ])
    instructions.extend([
        tr("Ikkala qatlamning barcha asl notalari birinchi marta birga: tezlik yana 60% ga tushadi. Oldin ajratib o‘rgangan yo‘lni birlashtiring. Bir qo‘lning notasi tugaganda uni pedal dumi kabi cho‘zib ushlamang; ikkinchi qo‘l davom etishi mumkin. Uchta xotirjam urinishdan keyin keyingi bosqichga o‘ting.",
           "Все исходные ноты обоих слоёв впервые вместе, скорость снова снижена до 60%. Соедините изученные отдельно линии. Не продлевайте закончившуюся ноту как педальный хвост: другая рука может продолжать. После трёх спокойных попыток переходите дальше.",
           "Every original note in both layers is now present, with speed lowered back to 60%. Combine the lines you studied separately. Release each note at its own end rather than extending it like a pedal tail; the other hand may continue. Move on after three unhurried attempts."),
        tr("O‘sha to‘liq faktura 80% tezlikda. Yangi nota qo‘shilmaydi: e’tibor endi kirishlar, klavishni bo‘shatish va kuy–jo‘rlik balansida. Qayerda to‘xtasangiz, playerni qo‘lda shu joydan oldinroqqa qaytaring. Ravonlik yo‘qolsa, oldingi sekin bosqichga qayting.",
           "Та же полная фактура на 80%, без новых нот. Работайте над вступлениями, отпусканием клавиш и балансом мелодии с сопровождением. При остановке вручную вернитесь немного раньше этого места. Если плавность теряется, вернитесь к медленному этапу.",
           "The same complete texture at 80%, with no added notes. Focus on attacks, releases and melody/accompaniment balance. If you stop, manually seek to just before that point. Return to the slow stage if continuity breaks."),
    ])
    titles.append(tr("Original faktura", "Исходная фактура", "Original texture"))
    instructions.append(tr(
        "Ikkala qatlamning shu oraliqdagi barcha asl kirishlari 100% manba tezligida. Zarur bo‘lsa player tezligini pasaytiring; ravon ijro tezlikdan oldin keladi.",
        "Все исходные вступления обоих слоёв этого отрезка на 100% скорости источника. При необходимости снизьте скорость плеера; плавность важнее темпа.",
        "Every original attack in both layers of this passage at 100% source speed. Lower player speed if needed; fluency comes before speed."))
    result = []
    for index, selection in enumerate(selections):
        # Keep existing progress/deep links: the original remains :stage:3.
        suffix = ["1", "2", "combined-slow", "combined-flow", "3"][index]
        speed = [60, 80, 60, 80, 100][index]
        reuse = complete and index == 4
        result.append({
            "id": f"{item_id}:stage:{suffix}", "title": titles[index],
            "instruction": instructions[index], "source_speed_percent": speed,
            "_asset_key": source.asset_key if reuse else item_id if index == 0 else f"{item_id}:stage:{suffix}",
            "_reuse_original": reuse,
            "_generator": {"start": start, "end": end, "selection": selection,
                           "speed_percent": speed, "title": source.title.replace("—", "-") + " | " + titles[index]["en"]},
        })
    return result


def source_window(start, end):
    return {"start_seconds": start, "end_seconds": end,
            "transformation": tr("Tayanchlar → alohida qatlam → ikki qo‘l sekin → ravon → original",
                                 "Опоры → отдельный слой → две руки медленно → плавно → оригинал",
                                 "Landmarks → focused layer → both hands slowly → fluently → original")}


def time_range(start, end):
    def stamp(value):
        return f"{int(value) // 60}:{int(value) % 60:02d}"
    return stamp(start) + "–" + stamp(end)


@lru_cache(maxsize=1)
def repertoire_items():
    expected = {source.code for source in SOURCES if source.code != "still" and source.course_kind == "standard"}
    if set(COURSES) != expected:
        raise ValueError("Every registered source requires a reviewed course.")
    result = []
    for source in SOURCES[1:]:
        if source.course_kind != "standard":
            continue
        _, parsed = repertoire_source(source.code)
        duration = parsed["metadata"]["duration_seconds"]
        course = COURSES[source.code]
        for plan in course["lessons"]:
            start, end = plan["start"], plan["end"] or duration
            key = f"lesson:{source.code}:{plan['code']}"
            variants = stages(source, parsed, key, start, end, plan["mode"], plan["floor"])
            layer = {"melody": tr("Yuqori qatlam", "Верхний слой", "Upper layer"),
                     "bass": tr("Pastki qatlam", "Нижний слой", "Lower layer"),
                     "coordination": tr("Ikki qatlam", "Оба слоя", "Both layers")}[plan["mode"]]
            result.append({
                "id": key, "kind": "lesson", "_composition": source.code,
                "title": plan["title"], "subtitle": {language: time_range(start, end) + " · " + text for language, text in layer.items()}, "intro": plan["task"],
                "category": "harmony" if "triads" in plan["related"] else "expression" if plan["mode"] == "melody" else "coordination",
                "goals": ["accuracy", "understanding", "musicality"], "level": None, "minutes": 10,
                "explanation": review_blocks(source.code, plan, parsed),
                "steps": [{"title": stage["title"], "instruction": stage["instruction"]} for stage in variants],
                "stages": variants, "source": source_window(start, end), "ready_when": plan["ready"],
                "related_ids": ["theory:" + topic for topic in plan["related"]],
            })
        boundaries = course["boundaries"] + [duration]
        windows = [(f"part-{index + 1}", start, end,
                    tr(f"{index + 1}-qism: {course['parts'][index]['uz']}",
                       f"Часть {index + 1}: {course['parts'][index]['ru']}",
                       f"Part {index + 1}: {course['parts'][index]['en']}"), course["parts"][index])
                   for index, (start, end) in enumerate(zip(boundaries, boundaries[1:]))]
        windows += [(f"join-{index}", boundary - 4, boundary + 6,
                     tr(f"{index}–{index + 1} qismlarni bog‘lash", f"Соединить части {index}–{index + 1}", f"Connect parts {index}–{index + 1}"),
                     tr("Oldingi tayanch, ko‘chish va keyingi kirishni birga mashq qiling.",
                        "Соедините предыдущую опору, перенос и следующий вход.",
                        "Practise the preceding landmark, move and next entry together."))
                    for index, boundary in enumerate(boundaries[1:-1], 1)]
        windows.append(("complete", 0, duration,
                        tr(source.title + ": boshidan oxirigacha", source.title + ": от начала до конца", source.title + ": from beginning to end"),
                        tr("Butun fayl: siyrak tayanchlardan to‘liq originalga.", "Весь файл: от редких опор к полному оригиналу.", "The complete file, from sparse landmarks to the original.")))
        for code, start, end, title, focus in windows:
            key = f"journey:{source.code}:{code}"
            variants = stages(source, parsed, key, start, end, "coordination", complete=code == "complete")
            result.append({
                "id": key, "kind": "journey", "_composition": source.code,
                "title": title, "subtitle": time_range(start, end), "intro": focus,
                "category": "coordination", "goals": ["accuracy", "musicality"], "level": None, "minutes": 12,
                "source": source_window(start, end), "stages": variants,
                "explanation": [
                    {"title": tr("Asarning shu yo‘li", "Линия этого произведения", "This piece's path"), "text": focus},
                    {"title": tr("Qismlarni birlashtirish", "Соединение частей", "Connecting passages"),
                     "text": tr("Chegaralar mashq uchun tanlangan vaqt nuqtalari, taxminiy takt yoki rasmiy forma bo‘limlari emas. Har qism ravon bo‘lgach, uning chegarasidan oldin boshlanadigan bog‘lash mashqini oching. Keyingi kirishni kutib oldingi jumlani qisqartirmang.",
                                "Границы — временные точки для занятий, а не предполагаемые такты или формальные разделы. После освоения части откройте соединение, начинающееся до её границы. Не укорачивайте предыдущую фразу, ожидая следующего входа.",
                                "Boundaries are practice time points, not inferred bars or formal sections. After each part becomes fluent, use the joining study that starts before its boundary. Do not shorten the preceding phrase while preparing the next entry.")},
                    {"title": tr("To‘liq ijroga qaytish", "Возврат к полному исполнению", "Returning to the complete performance"),
                     "text": tr("Siyrak namuna kirishlar va registrlarni eslab qolishga yordam beradi. Ikkinchi bosqichda yuqori qatlam to‘liq qaytadi, so‘ng pastki ichki tovushlar ham qo‘shiladi. Butun asar yo‘lining oxirgi bosqichi siz yuborgan original faylning o‘zini ochadi.",
                                "Разреженный пример помогает запомнить входы и регистры. Затем возвращается полный верх, после него — внутренние нижние тоны. Последний этап полного пути открывает сам переданный оригинальный файл.",
                                "Sparse landmarks help you remember entries and registers. The full upper layer returns next, followed by the lower inner tones. The final stage of the complete-piece path opens the supplied original file itself.")},
                ],
                "steps": [{"title": stage["title"], "instruction": stage["instruction"]} for stage in variants],
                "ready_when": tr("Tanlagan qatlamni kirishlar orasida yoki qism chegarasida to‘xtamasdan, o‘zingizga qulay tezlikda chala olasiz.",
                                 "Вы играете выбранный слой на удобной скорости без остановки между входами или на границе частей.",
                                 "You can play the chosen texture at a comfortable speed without stopping between entries or at passage boundaries."),
                "related_ids": ["theory:practice", "theory:phrasing"],
            })
    return result
