"""Translations keep the exact MIDI fragment, event IDs and numeric facts."""
from copy import deepcopy


def midi_question(question, lesson, lang):
    result = deepcopy(question)
    facts = lesson.content["midi_facts"]
    english = lang == "en"
    prompts = {"midi-first-note": "What is the first note in this exact passage?" if english else "Какая первая нота в этом точном фрагменте?",
               "midi-pulse-group": "How are the actual opening attack intervals grouped in eighth-note units?" if english else "Как сгруппированы фактические интервалы атак начала в единицах восьмых?",
               "midi-span": "How many semitones span the selected source note group?" if english else "Сколько полутонов между крайними звуками выбранной группы источника?",
               "midi-interval": "How many semitones separate the two source notes?" if english else "Сколько полутонов между двумя звуками источника?",
               "midi-chord": "Which structure fits this actual source note group?" if english else "Какая структура соответствует этой фактической группе звуков?",
               "midi-fingering": "What does a MIDI track name establish?" if english else "Что подтверждает название MIDI-трека?",
               "midi-recall": "How do you check retention next day?" if english else "Как проверить сохранение на следующий день?"}
    explanations = {"midi-first-note": "The answer comes from the first note_on in this selected passage." if english else "Ответ взят из первого note_on выбранного фрагмента.",
                    "midi-pulse-group": "Source gaps of 1, 0.5, 1, 0.5 quarters equal 2, 1, 2, 1 eighth notes. Each main pulse spans three eighth notes." if english else "Интервалы источника 1, 0.5, 1, 0.5 четверти равны 2, 1, 2, 1 восьмой. В каждой основной доле три восьмых.",
                    "midi-span": f"The source key numbers differ by {facts['span_semitones']} semitones." if english else f"Номера клавиш источника различаются на {facts['span_semitones']} полутонов.",
                    "midi-interval": f"The absolute difference between the two MIDI key numbers is {facts['interval_semitones']}." if english else f"Разность двух номеров MIDI-клавиш по модулю — {facts['interval_semitones']}.",
                    "midi-chord": "Check the intervals among the actual simultaneous source notes; do not infer the entire key from one chord." if english else "Проверьте интервалы фактических одновременных звуков; один аккорд не определяет тональность целиком.",
                    "midi-fingering": "A track name is a hand-part hint, separate from fingering and playing quality." if english else "Название трека — указание на партию руки, отдельно от аппликатуры и качества игры.",
                    "midi-recall": "The first independent attempt checks recall of this exact passage." if english else "Первая самостоятельная попытка проверяет припоминание именно этого фрагмента."}
    labels = {"minor": "Minor" if english else "Минорное трезвучие", "major": "Major" if english else "Мажорное трезвучие", "interval": "Two-note interval" if english else "Двухзвучный интервал", "faqat bitta tovush": "Only one note" if english else "Только один звук",
              "Har bir barmoq raqamini": "Every finger number" if english else "Номер каждого пальца", "Qo'l partiyasi uchun manba ko'rsatkichi, keyin tekshirish mumkin": "A source hand-part hint that can be checked" if english else "Указание партии руки, которое можно проверить", "Ijro mukammalligi bahosini": "A perfect-performance grade" if english else "Оценку идеального исполнения",
              "Darhol eng tez tempga o'taman": "Immediately use the fastest tempo" if english else "Сразу перейти к максимальному темпу", "Avval shu bo'lakni yordam kamaytirilgan holda bir marta sinayman": "First try this passage once with less help" if english else "Сначала один раз сыграть фрагмент с меньшей помощью", "Faqat qancha daqiqa ishlaganimni ko'raman": "Only check time spent" if english else "Проверить только потраченное время"}
    result["prompt"] = prompts[question["id"]]
    result["explanation"] = explanations[question["id"]]
    result["choices"] = [{**choice, "label": labels.get(choice["label"], choice["label"])} for choice in result["choices"]]
    return result


def midi_lesson(data, lesson, lang):
    result = deepcopy(data)
    facts, exercise = lesson.content["midi_facts"], result["exercise"]
    topic = lesson.content["midi_topic"]
    start, end = exercise["start_seconds"], exercise["end_seconds"]
    english = lang == "en"
    texts = {
        "midi-pulse": ("Opening: the actual rhythm" if english else "Начало: фактический ритм", "Hear and count the spacing of attacks in the exact MIDI opening." if english else "Послушайте и посчитайте интервалы между атаками точного MIDI-начала.",
                       [("Notes and time" if english else "Ноты и время", f"The first tone is {facts['first_note']}. Tempo is expressed in quarter notes. Key-hold duration can differ from the interval until the next attack." if english else f"Первый звук — {facts['first_note']}. Темп выражен четвертями. Длительность удержания клавиши может отличаться от времени до следующей атаки."),
                        ("A small group" if english else "Небольшая группа", "Listen slowly to this exact source fragment. Clap its real attack pattern, then play it on the piano." if english else "Медленно послушайте точный фрагмент источника. Прохлопайте его реальный рисунок атак, затем сыграйте на пианино.")]),
        "midi-register": ("Left-hand entrance: key distance" if english else "Вход левой руки: расстояние клавиш", "Find the actual simultaneous left-hand notes." if english else "Найдите фактические одновременные ноты левой руки.",
                          [("Source distance" if english else "Расстояние в источнике", f"The group's lowest and highest keys are {facts['span_semitones']} semitones apart. Twelve semitones form an octave: the same note name in another register." if english else f"Между нижней и верхней клавишами группы {facts['span_semitones']} полутонов. Двенадцать полутонов — октава: то же название звука в другом регистре."),
                           ("Comfortable movement" if english else "Удобное движение", "Find the notes separately, then play them together at the source timing. Avoid forcing a stretch; try a comfortable hand movement." if english else "Найдите звуки по отдельности, затем сыграйте вместе в момент источника. Не растягивайте руку силой; попробуйте удобное перемещение.")]),
        "midi-interval": ("Melody: the path between two tones" if english else "Мелодия: путь между звуками", "Understand an actual melodic change as a key distance." if english else "Рассмотрите фактическое изменение мелодии как расстояние клавиш.",
                          [("The exact pair" if english else "Точная пара", f"{facts['interval_from']} → {facts['interval_to']}: {facts['interval_semitones']} semitones. Say the direction and distance before playing. MIDI does not store enharmonic spelling; displayed names identify keyboard pitches." if english else f"{facts['interval_from']} → {facts['interval_to']}: {facts['interval_semitones']} полутонов. Назовите направление и расстояние до игры. MIDI не хранит энгармоническое написание; названия обозначают высоту клавиш."),
                           ("Return to the piece" if english else "Вернитесь к произведению", "Play the two source tones at their actual attack times, then join the notes before and after them." if english else "Сыграйте два звука источника в их фактические моменты, затем соедините с нотами до и после.")]),
        "midi-chord": ("A chord shape in the composition" if english else "Аккордная форма в произведении", "Name and hear the actual tones starting together." if english else "Назовите и послушайте фактические одновременно начинающиеся звуки.",
                       [("Actual tones" if english else "Фактические звуки", f"The selected source group is {facts['chord_notes']}; its pitch structure is {facts['chord_mode']}. A minor third spans three semitones, a major third four, and a perfect fifth seven." if english else f"Выбранная группа источника — {facts['chord_notes']}; структура высот — {facts['chord_mode']}. Малая терция содержит три полутона, большая — четыре, чистая квинта — семь."),
                        ("Harmony and metadata" if english else "Гармония и метаданные", "One chord does not prove the whole composition's key. Preserve the literal MIDI key metadata; this question concerns only the actual source group." if english else "Один аккорд не доказывает тональность всего произведения. Буквальные MIDI-метаданные тональности сохраняются; вопрос относится только к фактической группе источника.")]),
        "midi-coordination": ("Join both hands in the actual passage" if english else "Соедините руки в точном фрагменте", "Check the entrances and shared starts in the real source timeline." if english else "Проверьте входы и совместные начала по реальной временной линии.",
                              [("Hand evidence" if english else "Данные рук", "Right Hand and Left Hand come from source track names or your explicit overrides. MIDI does not determine fingering." if english else "Right Hand и Left Hand взяты из названий треков или ваших явных назначений. MIDI не определяет аппликатуру."),
                               ("Meeting points" if english else "Точки встречи", "Listen and play one hand in this exact fragment, then add the other. Check actual simultaneous source starts." if english else "Послушайте и сыграйте одну руку в точном фрагменте, затем добавьте вторую. Проверяйте фактические одновременные начала источника.")]),
        "midi-recall": ("The ending and next-day check" if english else "Финал и проверка на следующий день", "Restart from the MIDI file's ending and check recall." if english else "Начните с финала MIDI-файла и проверьте припоминание.",
                        [("Actual ending" if english else "Фактический финал", f"The file timeline ends at {facts['duration_seconds']:.3f} seconds. This passage includes its final source note attacks; sustain tails are represented separately." if english else f"Временная линия файла заканчивается на {facts['duration_seconds']:.3f} секунды. Фрагмент содержит финальные атаки источника; хвосты педали учитываются отдельно."),
                         ("Recall" if english else "Припоминание", "Play the ending comfortably three times. Next day, first try once with less help. Immediate fluency and delayed retention are separate evidence." if english else "Трижды удобно сыграйте финал. На следующий день сначала попробуйте один раз с меньшей помощью. Немедленная беглость и отложенное сохранение — разные доказательства.")]),
    }
    title, summary, blocks = texts[topic]
    if not facts.get("left_available", True) and topic in ["midi-register", "midi-coordination"]:
        title = "Key distance: assign a hand" if english and topic == "midi-register" else "Check the hand map" if english else "Расстояние клавиш: назначьте руку" if topic == "midi-register" else "Проверьте карту рук"
        summary = "This file has no left-hand track hint. Find the actual keys and assign hands in the player." if english else "В файле нет указания трека левой руки. Найдите фактические клавиши и назначьте руки в плеере."
        if topic == "midi-coordination":
            blocks[0] = ("Hand evidence" if english else "Данные рук", "No left-hand track hint was found. Hands are not guessed from pitch; assign them explicitly before practising this passage." if english else "Указание трека левой руки не найдено. Руки не угадываются по высоте; назначьте их явно перед упражнением.")
    if topic == "midi-pulse":
        if facts.get("compound_long_short"):
            blocks.append(("Source grouping: 3 + 3" if english else "Группировка источника: 3 + 3",
                f"The first track attacks at quarter positions 0, 1, 1.5, 2.5, 3. Its gaps 1, 0.5, 1, 0.5 become (2 + 1) / (2 + 1) eighth notes. Attacks fall on subdivisions 1, 3, 4, 6; main pulses on 1 and 4. Count ONE-two-THREE / TWO-two-THREE, playing only the source attacks. The first key is held for {facts['first_key_duration_quarters']:g} quarters, while the next attack is 1 quarter later: key hold and rhythmic spacing differ." if english else
                f"Атаки первого трека стоят на позициях 0, 1, 1.5, 2.5, 3 четверти. Интервалы 1, 0.5, 1, 0.5 дают (2 + 1) / (2 + 1) восьмой. Атаки приходятся на деления 1, 3, 4, 6; основные доли — на 1 и 4. Считайте РАЗ-два-ТРИ / ДВА-два-ТРИ, играя только атаки источника. Первая клавиша удерживается {facts['first_key_duration_quarters']:g} четверти, следующая атака через 1 четверть: удержание клавиши и ритмический промежуток различаются."))
        else:
            attacks = ", ".join(f"{value:g}" for value in facts.get("opening_attacks_quarters", []))
            gaps = ", ".join(f"{value:g}" for value in facts.get("opening_gaps_quarters", []))
            blocks.append(("Actual attack intervals" if english else "Фактические интервалы атак",
                           f"The first track attacks at quarter positions {attacks}; consecutive gaps are {gaps or 'no pair'}. A 3 + 3 pattern is not assumed for this file." if english else f"Атаки первого трека в единицах четвертей: {attacks}; последовательные интервалы: {gaps or 'нет пары'}. Схема 3 + 3 этому файлу не приписывается."))
    result.update({"language": lang, "title": title, "summary": summary,
                   "context": f"{lesson.arrangement.composition.title} · exact source fragment {start:.3f}–{end:.3f} s; " + ("verified complete source" if facts.get("source_completeness_verified") else "uploaded file") + f" {facts['duration_seconds']:.3f} s." if english else f"{lesson.arrangement.composition.title} · точный фрагмент источника {start:.3f}–{end:.3f} с; " + ("проверенный полный источник" if facts.get("source_completeness_verified") else "загруженный файл") + f" {facts['duration_seconds']:.3f} с.",
                   "explanation": [{"title": title, "text": text} for title, text in blocks],
                   "success_criterion": "I played this exact source passage comfortably three times and recorded the next check." if english else "Я трижды удобно сыграл точный фрагмент источника и записал следующую проверку.",
                   "transfer": "Join this exact composition transition with its neighbouring notes. The source player opens separately from the lesson." if english else "Соедините точный переход произведения с соседними нотами. Плеер источника открывается отдельно от урока."})
    result["steps"] = [{"title": "Listen to the exact passage" if english else "Послушайте точный фрагмент", "instruction": f"Listen slowly to {start:.3f}–{end:.3f} s and find its actual source tones." if english else f"Медленно послушайте {start:.3f}–{end:.3f} с и найдите фактические звуки источника."},
                       {"title": "Isolate and join" if english else "Выделите и соедините", "instruction": "Check one lesson idea in this passage. Select one hand if useful, then join both." if english else "Проверьте одну идею урока в этом фрагменте. При необходимости выберите одну руку, затем соедините обе."},
                       {"title": "Independent attempt" if english else "Самостоятельная попытка", "instruction": "Reduce the help and check three comfortable attempts. Record pulse, tones and comfort." if english else "Уменьшите подсказки и проверьте три удобные попытки. Запишите пульс, звуки и удобство."}]
    result["exercise"]["label"] = "Exact composition MIDI fragment" if english else "Точный MIDI-фрагмент произведения"
    result["quiz"] = {"questions": [{key: item[key] for key in ["id", "prompt", "choices"]} for item in [midi_question(question, lesson, lang) for question in lesson.quiz["questions"]]]}
    result["sources"] = [{**source, "title": "MIDI source" if english else "MIDI-источник"} for source in result.get("sources", [])]
    return result
