"""Authored Uzbek/Russian/English teaching; IDs and answer keys stay unchanged."""
from copy import deepcopy
from rest_framework.exceptions import ValidationError
from .midi_localization import midi_question as localized_midi_question, midi_lesson as localized_midi_lesson

LANGUAGES = {"uz", "ru", "en"}


def request_language(request, profile):
    explicit = request.query_params.get("lang")
    if explicit is not None:
        if explicit not in LANGUAGES:
            raise ValidationError({"lang": "Supported languages: uz, ru, en."})
        return explicit
    weighted = []
    for order, token in enumerate(request.headers.get("Accept-Language", "").split(",")):
        pieces = token.strip().split(";")
        code = pieces[0].strip().lower().split("-")[0]
        quality = 1.0
        for piece in pieces[1:]:
            if piece.strip().startswith("q="):
                try:
                    quality = float(piece.strip()[2:])
                except ValueError:
                    quality = 0
        if code in LANGUAGES and 0 < quality <= 1:
            weighted.append((-quality, order, code))
    return min(weighted)[2] if weighted else profile.language


SKILL_LABELS = {
    "en": {"rhythm": "Rhythm and pulse", "reading": "Keyboard and register", "harmony": "Chords and key", "intervals": "Intervals", "coordination": "Hand coordination", "practice": "Independent practice"},
    "ru": {"rhythm": "Ритм и пульс", "reading": "Клавиши и регистр", "harmony": "Аккорды и тональность", "intervals": "Интервалы", "coordination": "Координация рук", "practice": "Самостоятельные занятия"},
}


DIAGNOSTIC = {
    "en": {
        "midi-pulse-basis": ("How does a steady pulse differ from the number of notes?", ["Every note must be one beat", "One beat may contain several notes or a rest", "Only the left hand has a pulse", "I do not know yet"], "The pulse is a timing reference; attacks can fall at different subdivisions within it."),
        "midi-held-key": ("When the pedal sustains a sound, when was the key released?", ["Always when the sound ends", "Key release and the pedal-extended sound have separate times", "MIDI contains no note durations", "I do not know yet"], "note_off marks key release; CC64 can extend the sounding tail after that release."),
        "midi-triad-structure": ("How far are the other two tones of a minor triad from its root?", ["4 and 7 semitones", "3 and 7 semitones", "2 and 5 semitones", "I do not know yet"], "A minor triad contains a minor third (3 semitones) and a perfect fifth (7)."),
        "midi-keyboard": ("Which white key is immediately left of a group of two black keys?", ["G", "D", "C", "I do not know yet"], "C lies immediately left of the two-black-key group. This landmark repeats in each register."),
        "midi-distance": ("How far apart are MIDI keys 57 and 60?", ["2 semitones", "3 semitones", "7 semitones", "I do not know yet"], "Each MIDI key number steps by one semitone: 60 − 57 = 3."),
        "midi-reading-self": ("How comfortable is finding the indicated key and register with less player guidance?", ["Not tested", "Very difficult", "Slow, with help", "Mostly independent", "Comfortable and independent"], ""),
        "pulse": ("How many main beats does a typical 6/8 bar have?", ["Six", "Two, each divided into three", "Three, each divided into two", "I do not know yet"], "A typical 6/8 bar has two dotted-quarter beats; each contains three eighth notes."),
        "dot": ("How many eighth notes equal a dotted quarter?", ["2", "3", "4", "I do not know yet"], "A dot adds half the original value: two eighth notes plus one equals three."),
        "minor": ("Which notes form a D minor triad?", ["D–F♯–A", "D–F–A", "D–G–A", "I do not know yet"], "D–F is a minor third and D–A a perfect fifth."),
        "clef": ("Which note is on the lowest line of the treble staff?", ["G", "F", "E", "I do not know yet"], "The treble clef marks G on the second line; the lowest line is E4."),
        "interval": ("What interval is D–F?", ["Second", "Minor third", "Perfect fifth", "I do not know yet"], "Three letter names and three semitones make a minor third."),
        "strategy": ("You keep stopping at one transition. What do you try first?", ["Restart the entire piece every time", "Immediately increase the tempo", "Isolate a short section including both sides of the transition", "I do not know yet"], "A small section helps locate the cause and check a specific change."),
        "coordination": ("At a comfortable slow tempo, can you play the same short two-hand exercise three times without stopping?", ["Not tested", "Not yet", "Sometimes", "Usually", "Yes, in all three attempts"], ""),
        "reading_self": ("How comfortable is reading an easy unfamiliar score without following a keyboard video?", ["Not tested", "Very difficult", "Slow, with help", "Mostly independent", "Comfortable and independent"], ""),
        "rhythm_self": ("How comfortable is counting subdivisions aloud while keeping the pulse?", ["Not tested", "Very difficult", "Sometimes", "Mostly comfortable", "Comfortable and steady"], ""),
    },
    "ru": {
        "midi-pulse-basis": ("Чем устойчивый пульс отличается от количества нот?", ["Каждая нота обязательно равна одной доле", "В одной доле может быть несколько нот или пауза", "Пульс есть только у левой руки", "Пока не знаю"], "Пульс — опора времени; атаки могут начинаться на разных делениях внутри него."),
        "midi-held-key": ("Когда отпущена клавиша, если педаль продлевает звук?", ["Всегда в момент окончания звука", "Отпускание клавиши и продлённый педалью звук имеют разное время", "MIDI не содержит длительностей нот", "Пока не знаю"], "note_off обозначает отпускание клавиши; CC64 может продлевать звук после него."),
        "midi-triad-structure": ("На каком расстоянии от основного тона находятся два других звука минорного трезвучия?", ["4 и 7 полутонов", "3 и 7 полутонов", "2 и 5 полутонов", "Пока не знаю"], "Минорное трезвучие содержит малую терцию (3 полутона) и чистую квинту (7)."),
        "midi-keyboard": ("Какая белая клавиша находится сразу слева от группы из двух чёрных?", ["G", "D", "C", "Пока не знаю"], "Слева от группы двух чёрных клавиш находится C. Этот ориентир повторяется в разных регистрах."),
        "midi-distance": ("Каково расстояние между MIDI-клавишами 57 и 60?", ["2 полутона", "3 полутона", "7 полутонов", "Пока не знаю"], "Номер MIDI-клавиши меняется на единицу за полутон: 60 − 57 = 3."),
        "midi-reading-self": ("Насколько удобно находить указанную клавишу и регистр с меньшей помощью плеера?", ["Не проверял", "Очень трудно", "Медленно, с помощью", "В основном самостоятельно", "Удобно и самостоятельно"], ""),
        "pulse": ("Сколько основных долей обычно в такте 6/8?", ["Шесть", "Две, каждая делится на три", "Три, каждая делится на две", "Пока не знаю"], "Обычно в 6/8 две доли по четверти с точкой; в каждой три восьмые."),
        "dot": ("Сколько восьмых длится четверть с точкой?", ["2", "3", "4", "Пока не знаю"], "Точка добавляет половину исходной длительности: две восьмые плюс одна — три."),
        "minor": ("Какие звуки образуют трезвучие ре минор?", ["D–F♯–A", "D–F–A", "D–G–A", "Пока не знаю"], "D–F — малая терция, D–A — чистая квинта."),
        "clef": ("Какая нота на нижней линейке в скрипичном ключе?", ["G", "F", "E", "Пока не знаю"], "Скрипичный ключ отмечает G на второй линейке; нижняя линейка — E4."),
        "interval": ("Какой интервал между D и F?", ["Секунда", "Малая терция", "Чистая квинта", "Пока не знаю"], "Три буквенных названия и три полутона образуют малую терцию."),
        "strategy": ("Вы постоянно останавливаетесь на одном переходе. Что попробовать сначала?", ["Каждый раз играть всё произведение сначала", "Сразу повысить темп", "Выделить короткий фрагмент до и после перехода", "Пока не знаю"], "Небольшой фрагмент помогает найти причину и проверить конкретное изменение."),
        "coordination": ("Можете ли вы в удобном медленном темпе трижды сыграть короткое упражнение двумя руками без остановки?", ["Не проверял", "Пока нет", "Иногда", "Чаще всего", "Да, все три раза"], ""),
        "reading_self": ("Насколько удобно читать простые новые ноты без видео с клавишами?", ["Не проверял", "Очень трудно", "Медленно, с помощью", "В основном самостоятельно", "Удобно и самостоятельно"], ""),
        "rhythm_self": ("Насколько удобно считать мелкие деления вслух, сохраняя пульс?", ["Не проверял", "Очень трудно", "Иногда", "В основном удобно", "Удобно и устойчиво"], ""),
    },
}


def localized_diagnostic(questions, lang):
    if lang == "uz":
        return questions
    result = deepcopy(questions)
    for item in result:
        title, labels, _ = DIAGNOSTIC[lang][item["id"]]
        item["title"] = title
        item["choices"] = [{"id": choice["id"], "label": label} for choice, label in zip(item["choices"], labels)]
    return result


def localized_skills(skills, lang):
    if lang == "uz":
        return skills
    return [{**item, "label": SKILL_LABELS[lang][item["id"]]} for item in skills]


def localized_diagnostic_feedback(feedback, lang):
    if lang == "uz":
        return feedback
    return [{**item, "explanation": DIAGNOSTIC[lang][item["id"]][2]} for item in feedback]


NOTICES = {
    "en": {
        "imported": "These lessons use the imported score version. Original drills and the actual piece are assessed separately; fingering has not been teacher reviewed.",
        "metadata": "Preparation based on published key and meter metadata. The full score is unavailable; measures and fingering are not inferred.",
        "pending": "Choose the exact track, arrangement and complete score before starting composition lessons.",
    },
    "ru": {
        "imported": "Уроки связаны с этой версией импортированных нот. Оригинальные упражнения и само произведение оцениваются отдельно; аппликатура не проверена преподавателем.",
        "metadata": "Подготовка по опубликованной тональности и размеру. Полных нот пока нет; такты и аппликатура не предполагаются.",
        "pending": "Выберите точный трек, аранжировку и полные ноты перед уроками по произведению.",
    },
}


def localized_notice(kind, original, lang):
    return original if lang == "uz" else NOTICES[lang][kind]


LESSON_TEXT = {
    "en": {
        "compound-pulse": {"title": "{meter}: {pulses} main beats", "summary": "Group equal eighth notes into three-note pulses.",
            "explanation": [("Three subdivisions", "In a typical {meter} bar, {beats} equal eighth notes form {pulses} main beats. Each main beat lasts a dotted quarter. Count three equal syllables per beat; written accents can differ from the basic pulse."), ("Tempo unit", "At dotted quarter = 50/min, the eighth-note subdivision is 150/min. This is a comfortable starting exercise tempo, independent of the piece's printed tempo.")],
            "steps": [("Count first", "Count each group aloud: ONE-and-a, TWO-and-a. Tap only at the beginning of each group."), ("One key", "Play the displayed repeated note with equal subdivisions. Lightly emphasize each group beginning; repeat comfortably three times."), ("Reduce the clicks", "First listen to every subdivision, then only the main beats. Keep the spacing equal when the smaller clicks disappear.")],
            "success": "I counted the main beats and equal subdivisions and played the original drill three times without stopping."},
        "simple-pulse": {"title": "{meter}: beats and subdivisions", "summary": "Count the imported meter with its stated note unit.",
            "explanation": [("Two subdivisions", "The basic reading of {meter} has {beats} beats in the written note unit. Divide each beat into two equal parts: ONE-and, TWO-and. Check the score for accents and grouping."), ("Dotted values", "A dot adds half the original note value. A quarter equals two eighth notes; a dotted quarter equals three. Keep the metronome's stated unit clear.")],
            "steps": [("Count", "Count the beats, then add an 'and' between consecutive beats."), ("Play", "Play the displayed repeated note first on beats, then on subdivisions. Return to the beat without changing the elapsed time.")], "success": "I counted the written meter and played the original drill three times with a steady pulse."},
        "meter-inspection": {"title": "Read the meter from the score", "summary": "Check written grouping before choosing accents.",
            "explanation": [("Written grouping", "The selected passage is marked {meter}. The numbers alone do not establish every main accent. Check beams, accent marks and the reference performance.")],
            "steps": [("Inspect", "Find the time signature and beamed groups in the actual score. Count a grouping you can verify and record what you observed.")], "success": "I recorded the written time signature and the grouping I could verify in the score."},
        "harmony": {"title": "{key}: notes and triad", "summary": "Connect familiar key shapes to named notes and chords.",
            "explanation": [("Scale map", "The {mode} scale used in this original preparation is {scale}. The tonic triad is {triad}. A key signature does not determine every chord or accidental in the composition."), ("Triad and inversion", "A triad uses scale degrees 1, 3 and 5. The same three note names remain the same chord when reordered; the lowest chord tone determines its inversion. Play the tones separately if a simultaneous grip is uncomfortable.")],
            "steps": [("Name and find", "Find {triad} on the keyboard and name each note. Then play the displayed original drill slowly."), ("Listen", "Compare the original triad shapes and notice which tone changes or moves to a different register."), ("Return to the score", "Find the same note names in the selected score. Describe the actual written figure rather than assuming an entire chord progression.")],
            "success": "I named the original scale and triad, found their notes independently and repeated the drill comfortably three times."},
        "interval-navigation": {"title": "Navigate by intervals", "summary": "Read and hear the distance between consecutive tones.",
            "explanation": [("Letters and semitones", "An interval counts both starting and ending letter names. The first and third notes of this original triad form a {third}; the tonic and fifth form a perfect fifth of seven semitones."), ("Direction", "Say whether the next displayed note goes up or down, then find it before playing. Connect the visual distance to its sound rather than relying only on a remembered finger number.")],
            "steps": [("Name the distance", "Play the original note pairs and name the third and fifth."), ("Plan the next tone", "Play the displayed pattern up and down. Say the direction before each new note."), ("Another register", "Find the same original pattern one octave lower and compare the sound.")],
            "success": "I named the third and fifth and independently found the original pattern in two registers three times."},
        "staff-landmarks": {"title": "From keys to the staff", "summary": "Use landmarks to connect note names and two clefs.",
            "explanation": [("Two landmarks", "The second line of the treble staff is G4. The fourth line from the bottom of the bass staff is F3. Middle C, C4, sits on a ledger line between the two staves."), ("Read by steps", "Moving from a line to the next space changes one letter name; line to next line skips a letter. An octave number identifies the register. Read the displayed original upper and lower notes using these landmarks.")],
            "steps": [("Landmarks", "Find G4 in the treble clef and F3 in the bass clef, then count letter steps to the displayed notes."), ("Two registers", "Name each displayed original note before playing. Keep the upper and lower registers distinct."), ("Less help", "Try the same short exercise three times, finding each landmark independently.")],
            "success": "I named the treble and bass landmarks and read the original notes independently in both registers three times."},
        "hands-meeting": {"title": "Two hands: meeting points", "summary": "Plan where the hands begin together and where they move independently.",
            "explanation": [("A shared timeline", "In the original {exercise_meter} drill, the left hand begins at each main beat while the right plays the smaller divisions. The displayed notation determines their meeting points; this is preparation, not a transcription of the composition's hand parts."), ("One small task", "If each hand is comfortable but combining them is difficult, isolate one beat or group. Check timing and comfort, then join the groups. Increasing speed is optional.")],
            "steps": [("Tap first", "Tap every subdivision with the right hand and only the group beginnings with the left."), ("One group", "Play one displayed group slowly with both hands, sustaining the left note for its written value."), ("Join", "Connect the groups and check pulse, note starts and comfort in three attempts.")],
            "success": "I started the hands together at the written meeting points and played the original drill comfortably three times without stopping."},
        "repair-and-recall": {"title": "Repair an error and check tomorrow", "summary": "Record a specific change and test whether it lasts.",
            "explanation": [("One observable goal", "Choose one issue: a wrong note, uneven pulse, hand meeting or forgotten starting point. Replace 'play better' with an observable result such as 'continue through my chosen transition without stopping'."), ("Context and recall", "Include a little before and after the difficult point. Work at a comfortable tempo, alternate with another familiar section, and check the first attempt again next day."), ("Separate evidence", "A quiz checks the answers you gave. Reported repetitions describe your practice. A later attempt checks retention. These do not establish whole-piece perfection.")],
            "steps": [("First attempt", "Play the original recall drill or your chosen familiar passage and describe one point that interrupted the flow."), ("Repair", "Check one cause in a short section, including both sides of the transition. Record the results of three comfortable attempts."), ("Recall", "Write what changed and what you will test on the first attempt next time. Try that attempt before reviewing your notes.")],
            "success": "I recorded one cause, a comfortable tempo and three attempts, then set a clear goal for the next check."},
    },
    "ru": {
        "compound-pulse": {"title": "{meter}: {pulses} основных долей", "summary": "Объединяйте равные восьмые в группы по три.",
            "explanation": [("Три деления", "Обычно в такте {meter} {beats} равных восьмых образуют {pulses} основных долей. Каждая доля длится четверть с точкой. Считайте три равных слога на долю; записанные акценты могут отличаться от основного пульса."), ("Единица темпа", "При четверти с точкой = 50/мин восьмые идут со скоростью 150/мин. Это удобный начальный темп упражнения, независимый от темпа произведения.")],
            "steps": [("Сначала счёт", "Считайте группы вслух: РАЗ-и-а, ДВА-и-а. Постукивайте только в начале каждой группы."), ("Одна клавиша", "Играйте показанную повторяющуюся ноту равными делениями. Слегка выделяйте начало группы; удобно повторите три раза."), ("Меньше щелчков", "Сначала слушайте каждое деление, затем только основные доли. Сохраняйте равные интервалы между нотами, когда мелкие щелчки исчезнут.")],
            "success": "Я посчитал основные доли и равные деления и трижды сыграл оригинальное упражнение без остановки."},
        "simple-pulse": {"title": "{meter}: пульс и деления", "summary": "Считайте размер с указанной единицей длительности.",
            "explanation": [("Два деления", "В базовом чтении размера {meter} {beats} долей указанной длительности. Каждую долю можно разделить пополам: РАЗ-и, ДВА-и. Проверьте акценты и группировку в нотах."), ("Точка", "Точка добавляет половину исходной длительности. Четверть равна двум восьмым, четверть с точкой — трём. Учитывайте единицу метронома.")],
            "steps": [("Счёт", "Посчитайте доли, затем добавьте 'и' между соседними долями."), ("Игра", "Играйте показанную ноту сначала по долям, затем по делениям. Вернитесь к долям, сохранив тот же ход времени.")], "success": "Я посчитал записанный размер и трижды сыграл оригинальное упражнение с устойчивым пульсом."},
        "meter-inspection": {"title": "Проверьте размер по нотам", "summary": "Посмотрите записанную группировку перед выбором акцентов.",
            "explanation": [("Записанная группировка", "В выбранном фрагменте указан размер {meter}. Одни числа не определяют все основные акценты. Проверьте рёбра, знаки акцента и образец исполнения.")],
            "steps": [("Посмотрите", "Найдите размер и группы нот под рёбрами. Посчитайте группировку, которую можете подтвердить, и запишите наблюдение.")], "success": "Я записал обозначение размера и группировку, подтверждённую нотами."},
        "harmony": {"title": "{key}: звуки и трезвучие", "summary": "Свяжите знакомую форму руки с названиями нот и аккорда.",
            "explanation": [("Карта гаммы", "В этом оригинальном упражнении используется {mode} гамма: {scale}. Тоническое трезвучие — {triad}. Тональность не определяет все аккорды и случайные знаки в произведении."), ("Трезвучие и обращение", "Трезвучие строится из ступеней 1, 3 и 5. Перестановка тех же трёх звуков сохраняет аккорд; нижний звук определяет обращение. Если совместное взятие неудобно, играйте звуки по очереди.")],
            "steps": [("Назовите и найдите", "Найдите {triad} на клавиатуре и назовите каждый звук. Затем медленно сыграйте показанное оригинальное упражнение."), ("Послушайте", "Сравните формы оригинального трезвучия: какой звук изменился или переместился в другой регистр?"), ("Вернитесь к нотам", "Найдите те же названия звуков в выбранных нотах. Опишите записанную фигуру, не предполагая всю последовательность аккордов.")],
            "success": "Я назвал оригинальную гамму и трезвучие, самостоятельно нашёл звуки и трижды удобно повторил упражнение."},
        "interval-navigation": {"title": "Ориентируйтесь по интервалам", "summary": "Читайте и слышьте расстояния между звуками.",
            "explanation": [("Буквы и полутоны", "При подсчёте интервала учитываются оба крайних буквенных названия. Первая и третья ступени оригинального трезвучия образуют {third}; тоника и пятая — чистую квинту из семи полутонов."), ("Направление", "Перед игрой назовите, идёт ли следующая нота вверх или вниз. Свяжите видимое расстояние со звучанием, а не только с привычным номером пальца.")],
            "steps": [("Назовите расстояние", "Сыграйте оригинальные пары звуков и назовите терцию и квинту."), ("Следующий звук", "Играйте показанный рисунок вверх и вниз. Перед новой нотой называйте направление."), ("Другой регистр", "Найдите тот же оригинальный рисунок октавой ниже и сравните звучание.")],
            "success": "Я назвал терцию и квинту и трижды самостоятельно нашёл оригинальный рисунок в двух регистрах."},
        "staff-landmarks": {"title": "От клавиш к нотному стану", "summary": "Свяжите звуки с опорными нотами двух ключей.",
            "explanation": [("Две опоры", "Вторая линейка в скрипичном ключе — G4. Четвёртая снизу в басовом — F3. Среднее до, C4, записывается на добавочной линейке между станами."), ("Чтение по ступеням", "Переход с линейки на соседний промежуток меняет название на одну ступень; с линейки на следующую линейку — через ступень. Номер октавы указывает регистр. Читайте показанные верхние и нижние ноты от этих опор.")],
            "steps": [("Опорные ноты", "Найдите G4 в скрипичном ключе и F3 в басовом, затем посчитайте буквенные ступени до показанных нот."), ("Два регистра", "Назовите каждую оригинальную ноту перед игрой. Различайте верхний и нижний регистры."), ("Меньше подсказок", "Трижды попробуйте короткое упражнение, самостоятельно находя опоры.")],
            "success": "Я назвал опорные ноты двух ключей и трижды самостоятельно прочитал оригинальные ноты в двух регистрах."},
        "hands-meeting": {"title": "Две руки: точки встречи", "summary": "Определите совместные и отдельные движения рук.",
            "explanation": [("Общая временная линия", "В оригинальном упражнении {exercise_meter} левая рука начинает на основной доле, правая играет мелкие деления. Точки встречи определяются показанными нотами; это подготовка, а не копия партий произведения."), ("Одна небольшая задача", "Если отдельно руки играют удобно, но соединение трудно, выделите одну долю или группу. Проверьте время и удобство, затем соедините группы. Повышать скорость необязательно.")],
            "steps": [("Сначала постукивание", "Правой рукой отмечайте все деления, левой — только начало групп."), ("Одна группа", "Медленно сыграйте одну показанную группу двумя руками; держите левую ноту её записанную длительность."), ("Соединение", "Соедините группы и проверьте пульс, начало нот и удобство в трёх попытках.")],
            "success": "Я одновременно начал обеими руками в точках встречи и трижды удобно сыграл оригинальное упражнение без остановки."},
        "repair-and-recall": {"title": "Исправьте ошибку и проверьте завтра", "summary": "Запишите конкретное изменение и проверьте его сохранение.",
            "explanation": [("Наблюдаемая цель", "Выберите одну проблему: неверная нота, неровный пульс, встреча рук или забытая точка начала. Вместо 'играть лучше' задайте результат, например 'пройти выбранный переход без остановки'."), ("Контекст и припоминание", "Включите немного музыки до и после трудного места. Работайте в удобном темпе, чередуйте со знакомым фрагментом и проверьте первую попытку на следующий день."), ("Разные доказательства", "Quiz проверяет данные вами ответы. Отмеченные повторы описывают вашу практику. Поздняя попытка проверяет сохранение навыка. Это не означает идеальное исполнение всего произведения.")],
            "steps": [("Первая попытка", "Сыграйте оригинальное упражнение на припоминание или знакомый выбранный фрагмент и опишите одно место, нарушившее движение."), ("Исправление", "Проверьте одну причину в коротком фрагменте с обеими сторонами перехода. Запишите результат трёх удобных попыток."), ("Припоминание", "Запишите, что изменилось и что проверить в первой попытке в следующий раз. Попробуйте до чтения своих записей.")],
            "success": "Я записал одну причину, удобный темп и три попытки, затем задал ясную цель следующей проверки."},
    },
}


CHOICE_LABELS = {
    "en": {"Katta tersiya": "Major third", "Kichik tersiya": "Minor third", "Sof kvarta": "Perfect fourth", "Sekunda": "Second", "D minor, birinchi aylanish": "D minor, first inversion", "F major": "F major", "Yangi tonallik": "A new key", "1 va 4": "1 and 4", "2 va 5": "2 and 5", "Har sakkizlikda": "On every eighth note", "Darhol tezlashtiraman": "Immediately increase the tempo", "Faqat 1–2–3 guruhini sekin tekshiraman": "Check only the 1–2–3 group slowly", "Butun asarni boshidan takrorlayman": "Restart the entire piece", "Asarni perfect chalishni": "Perfect performance of the piece", "Shu savollarga to'g'ri javob berganimni": "Correct answers to these questions", "Barmoqlashim avtomatik to'g'riligini": "Automatically correct fingering", "Bugun yaxshi": "Good today", "30 daqiqa chaldim": "I played for 30 minutes", "Tanlagan o'tishim 60 katta urish/min da uch urinishning ikkitasida to'xtamadi; ertaga shu joyni tekshiraman": "My transition continued in two of three attempts at 60 main beats/min; I will check it tomorrow", "Har katta urish boshida": "At the start of each main beat", "Tasodifiy joylarda": "At random places", "Faqat yakunda": "Only at the end", "Tovushlar nota importisiz taxmin qilinadi": "Guess the notes without the score", "Faqat bir tovush": "Only one note", "Butun ijroning barcha akkordlarini": "Every chord in the entire performance", "Import qilingan joydagi yozilgan key va mode belgisini": "The key and mode written at this imported location", "Mening amaliy mahoratimni": "My performance skill", "Ha": "Yes", "Yo'q, notadagi guruhlash va aksent ham tekshiriladi": "No; check written grouping and accents too", "Yozilgan nota hodisalari va siz belgilagan oraliqni": "Written note events in your selected range", "Sizning barmoqlashingiz to'g'riligini": "Whether your fingering is correct", "Asarni perfect chalishingizni": "Whether you play the piece perfectly"},
    "ru": {"Katta tersiya": "Большая терция", "Kichik tersiya": "Малая терция", "Sof kvarta": "Чистая кварта", "Sekunda": "Секунда", "D minor, birinchi aylanish": "Ре минор, первое обращение", "F major": "Фа мажор", "Yangi tonallik": "Новая тональность", "1 va 4": "1 и 4", "2 va 5": "2 и 5", "Har sakkizlikda": "На каждой восьмой", "Darhol tezlashtiraman": "Сразу увеличить темп", "Faqat 1–2–3 guruhini sekin tekshiraman": "Медленно проверить только группу 1–2–3", "Butun asarni boshidan takrorlayman": "Играть всё произведение сначала", "Asarni perfect chalishni": "Идеальное исполнение произведения", "Shu savollarga to'g'ri javob berganimni": "Верные ответы на эти вопросы", "Barmoqlashim avtomatik to'g'riligini": "Автоматически верную аппликатуру", "Bugun yaxshi": "Сегодня хорошо", "30 daqiqa chaldim": "Играл 30 минут", "Tanlagan o'tishim 60 katta urish/min da uch urinishning ikkitasida to'xtamadi; ertaga shu joyni tekshiraman": "Переход прошёл в двух из трёх попыток при 60 основных долях/мин; завтра проверю снова", "Har katta urish boshida": "В начале каждой основной доли", "Tasodifiy joylarda": "В случайных местах", "Faqat yakunda": "Только в конце", "Tovushlar nota importisiz taxmin qilinadi": "Предположить звуки без нот", "Faqat bir tovush": "Только один звук", "Butun ijroning barcha akkordlarini": "Все аккорды исполнения", "Import qilingan joydagi yozilgan key va mode belgisini": "Записанное обозначение тональности и лада в этом месте импорта", "Mening amaliy mahoratimni": "Моё исполнительское умение", "Ha": "Да", "Yo'q, notadagi guruhlash va aksent ham tekshiriladi": "Нет, проверяются также группировка и акценты", "Yozilgan nota hodisalari va siz belgilagan oraliqni": "Записанные ноты в выбранном диапазоне", "Sizning barmoqlashingiz to'g'riligini": "Правильность вашей аппликатуры", "Asarni perfect chalishingizni": "Идеальное исполнение произведения"},
}


def base_code(lesson):
    import re
    return re.sub(r"^(?:score|midi)-\d+-[0-9a-f]+-", "", lesson.code)


def lesson_parameters(lesson):
    from .curriculum import tonal_material
    exercise = lesson.content.get("exercise", {})
    binding = lesson.content.get("score_binding", {})
    tonal = tonal_material(binding.get("focus_key")) or tonal_material({"fifths": 0, "mode": "major"}) if lesson.score_version_id else tonal_material({"fifths": -1, "mode": "minor"})
    meter = exercise.get("time_signature") or (str((binding.get("focus_time") or {}).get("beats", "6")) + "/" + str((binding.get("focus_time") or {}).get("beat_type", 8)))
    try:
        beats = int(meter.split("/")[0])
    except ValueError:
        beats = 0
    return {"meter": meter, "exercise_meter": exercise.get("time_signature", "6/8"), "beats": beats,
            "pulses": beats // 3, "key": tonal["tonic"] + " " + tonal["mode"], "mode": tonal["mode"],
            "scale": "–".join(tonal["scale"]), "triad": "–".join(tonal["triad"]), "third": "minor third" if tonal["mode"] == "minor" else "major third"}


def localized_question(question, lesson, lang):
    if lang == "uz":
        return question
    result = deepcopy(question)
    if lesson.content.get("exercise", {}).get("type") == "midi_source_fragment":
        return localized_midi_question(question, lesson, lang)
    code = base_code(lesson)
    params = lesson_parameters(lesson)
    rhythm = code in ["compound-pulse", "simple-pulse", "meter-inspection"]
    harmony = code in ["d-minor-map", "tonal-map"]
    qid = question["id"]
    if lang == "en":
        prompts = {"tempo": "At 50 main beats/min with three subdivisions per beat, how many eighth notes occur per minute?", "scale": "Which note belongs to D natural minor?", "inversion": "What is F–A–D?", "treble": "Which note is on the second line of the treble staff?", "bass": "Which note is on the fourth line from the bottom of the bass staff?", "meeting": "Where do the hands begin together in this original drill?", "next": "How do you check a disrupted two-hand group?", "evidence": "What does a 100% theory quiz prove?", "reflection": "Which practice record is most useful?", "certainty": "What does the imported key marking establish?", "dot": "How many eighth notes equal a dotted quarter?", "grouping": "Do meter numbers alone establish every accent?", "source-rests": "How many written rest events are in this imported passage?", "source-claim": "What does this passage analysis establish?", "pdf-pulse": "How many main beats are typical in this edition's 6/8 meter?", "pdf-leading-tone": "Which raised note connects A to Dm in measures 38–40?"}
        prompt = f"How many main beats does a typical {params['meter']} bar have?" if qid == "group" else f"How many beats in the written note unit does {params['meter']} contain?" if qid == "beats" else f"Which notes form the {params['key']} tonic triad?" if qid == "triad" else "What is the third interval in this original note pair?" if qid == "third" else "How many semitones form this perfect fifth?" if qid == "fifth" else prompts.get(qid, question["prompt"])
        explanations = {"tempo": "Three eighth notes per beat: 50 × 3 = 150.", "scale": "B♭ is the sixth degree of D natural minor.", "inversion": "The tones are still D–F–A, with the third F as the lowest note.", "treble": "The treble clef marks G4 on its second line.", "bass": "The bass clef marks F3 on the fourth line from the bottom.", "meeting": "Use the meeting points shown by the original written left and right parts.", "next": "A smaller group helps locate the timing or movement that interrupts the flow.", "evidence": "A quiz checks understanding; playing and delayed retention are separate evidence.", "reflection": "Location, tempo unit, attempt result and next goal make the record actionable.", "certainty": "A key marking is written metadata, separate from chord analysis and playing skill.", "dot": "Two eighth notes plus half that value equals three.", "grouping": "Written beams, accents and the performance context also matter.", "source-rests": "Count the rest events actually written in the selected imported range.", "source-claim": "The facts describe written events, not performance skill or fingering.", "group": "In compound meter, each main beat divides into three equal eighth notes.", "beats": "The upper number gives the quantity of the written note unit.", "triad": "Scale degrees 1, 3 and 5 form the tonic triad.", "third": "Count the letter names and semitones in the original pair.", "fifth": "A perfect fifth spans seven semitones.", "pdf-pulse": "Two dotted-quarter beats, each divided into three eighth notes.", "pdf-leading-tone": "The A chord in measures 38–39 contains C♯; measure 40 returns to Dm. C♯ is the raised seventh degree of D minor."}
    else:
        prompts = {"tempo": "При 50 основных долях/мин и трёх делениях на долю сколько восьмых в минуту?", "scale": "Какой звук входит в ре натуральный минор?", "inversion": "Какой аккорд F–A–D?", "treble": "Какая нота на второй линейке в скрипичном ключе?", "bass": "Какая нота на четвёртой снизу линейке в басовом ключе?", "meeting": "Где руки начинают вместе в этом оригинальном упражнении?", "next": "Как проверить нарушенную группу двумя руками?", "evidence": "Что доказывает результат 100% в тесте по теории?", "reflection": "Какая запись о занятии полезнее?", "certainty": "Что подтверждает обозначение тональности в импортированных нотах?", "dot": "Сколько восьмых длится четверть с точкой?", "grouping": "Определяют ли числа размера все акценты?", "source-rests": "Сколько записанных пауз в этом импортированном фрагменте?", "source-claim": "Что определяет анализ этого фрагмента?", "pdf-pulse": "Сколько основных долей обычно в размере 6/8 этого издания?", "pdf-leading-tone": "Какая повышенная нота связана с переходом A → Dm в тактах 38–40?"}
        prompt = f"Сколько основных долей обычно в такте {params['meter']}?" if qid == "group" else f"Сколько долей указанной длительности в размере {params['meter']}?" if qid == "beats" else f"Какие звуки образуют тоническое трезвучие {params['key']}?" if qid == "triad" else "Какая терция между звуками этой оригинальной пары?" if qid == "third" else "Сколько полутонов в этой чистой квинте?" if qid == "fifth" else prompts.get(qid, question["prompt"])
        explanations = {"tempo": "Три восьмые на долю: 50 × 3 = 150.", "scale": "B♭ — шестая ступень ре натурального минора.", "inversion": "Звуки D–F–A остаются теми же; нижний звук — терция F.", "treble": "Скрипичный ключ отмечает G4 на второй линейке.", "bass": "Басовый ключ отмечает F3 на четвёртой снизу линейке.", "meeting": "Пользуйтесь точками встречи, записанными в оригинальных партиях двух рук.", "next": "Небольшая группа помогает найти нарушенное время или движение.", "evidence": "Тест проверяет понимание; игра и отложенное сохранение — отдельные доказательства.", "reflection": "Место, единица темпа, результат попыток и следующая цель делают запись полезной.", "certainty": "Обозначение тональности — данные нот, отдельно от анализа аккордов и исполнительского навыка.", "dot": "Две восьмые плюс половина этой длительности дают три.", "grouping": "Также важны рёбра, акценты и контекст исполнения.", "source-rests": "Посчитайте паузы, записанные в выбранном диапазоне импортированных нот.", "source-claim": "Факты описывают записанные ноты, а не исполнительское умение и аппликатуру.", "group": "В составном размере каждая основная доля делится на три равные восьмые.", "beats": "Верхнее число показывает количество указанной длительности.", "triad": "Тоническое трезвучие строится из ступеней 1, 3 и 5.", "third": "Посчитайте буквенные названия и полутоны оригинальной пары.", "fifth": "Чистая квинта содержит семь полутонов.", "pdf-pulse": "Две четверти с точкой, каждая делится на три восьмые.", "pdf-leading-tone": "Аккорд A в тактах 38–39 содержит C♯; в такте 40 возвращается Dm. C♯ — повышенная седьмая ступень ре минора."}
    result["prompt"] = prompt
    result["explanation"] = explanations.get(qid, question.get("explanation", ""))
    for choice in result["choices"]:
        choice["label"] = CHOICE_LABELS[lang].get(choice["label"], choice["label"])
    return result


def localized_lesson(data, lesson, lang):
    if lang == "uz":
        return data
    result = deepcopy(data)
    if lesson.content.get("exercise", {}).get("type") == "midi_source_fragment":
        return localized_midi_lesson(result, lesson, lang)
    result["language"] = lang
    code = base_code(lesson)
    params = lesson_parameters(lesson)
    if lang == "ru":
        params["mode"] = "натуральная минорная" if params["mode"] == "minor" else "мажорная"
        params["third"] = "малую терцию" if params["third"] == "minor third" else "большую терцию"
        params["key"] = params["key"].replace("minor", "минор").replace("major", "мажор")
    else:
        params["mode"] = "natural minor" if params["mode"] == "minor" else "major"
    text_code = "harmony" if code in ["d-minor-map", "tonal-map"] else code
    if text_code in LESSON_TEXT[lang]:
        text = LESSON_TEXT[lang][text_code]
        result["title"] = text["title"].format(**params)
        result["summary"] = text["summary"]
        result["explanation"] = [{"title": title.format(**params), "text": paragraph.format(**params)} for title, paragraph in text["explanation"]]
        result["steps"] = [{"title": title.format(**params), "instruction": instruction.format(**params)} for title, instruction in text["steps"]]
        result["success_criterion"] = text["success"].format(**params)
        if code == "d-minor-map":
            result["explanation"].append({"title": "C and C♯" if lang == "en" else "C и C♯", "text": "D natural minor contains C. In D harmonic minor, the seventh degree is raised to C♯. In the complete PDF, compare the A chord in measures 38–39 with the return to Dm in measure 40." if lang == "en" and lesson.arrangement.full_score_verified_at else "D natural minor contains C; D harmonic minor raises the seventh degree to C♯. Compare their sound in the original drill." if lang == "en" else "В ре натуральном миноре есть C. В ре гармоническом миноре седьмая ступень повышается до C♯. В полных нотах сравните аккорд A в тактах 38–39 с возвращением Dm в такте 40." if lesson.arrangement.full_score_verified_at else "В ре натуральном миноре есть C; в гармоническом седьмая ступень повышается до C♯. Сравните их звучание в оригинальном упражнении."})
    if code == "choose-exact-version":
        result.update({"title": "Choose the complete arrangement" if lang == "en" else "Выберите полную аранжировку", "summary": "Choose an exact track and a complete score before composition lessons." if lang == "en" else "Выберите точный трек и полные ноты перед уроками по произведению.", "context": "A title alone does not determine the piano arrangement, key, meter or fingering." if lang == "en" else "Название само по себе не определяет фортепианную аранжировку, тональность, размер и аппликатуру.", "success_criterion": "I selected an exact track, complete score and one place I want to improve." if lang == "en" else "Я выбрал точный трек, полные ноты и одно место, которое хочу улучшить."})
        result["explanation"] = [{"title": "Complete source" if lang == "en" else "Полный источник", "text": "Choose the exact arrangement with all score pages. For an OST collection, choose the track first. Verify that the score and reference performance match." if lang == "en" else "Выберите точную аранжировку со всеми страницами нот. В сборнике OST сначала выберите трек. Проверьте соответствие нот и образца исполнения."}]
        result["steps"] = [{"title": "Select" if lang == "en" else "Выберите", "instruction": "Save the exact track and complete score source." if lang == "en" else "Сохраните точный трек и источник полных нот."}, {"title": "Observe" if lang == "en" else "Посмотрите", "instruction": "Describe one place you want to learn. Use only page or measure numbers you can verify." if lang == "en" else "Опишите одно место для изучения. Указывайте только подтверждённые номера страниц и тактов."}]
    elif code == "pdf-full-piece":
        if lang == "en":
            result.update({"title": "The complete piece: four-page practice", "summary": "Connect theory and hand exercises to exact locations in the 103-measure arrangement.", "context": "Alexis Quoniam's complete four-page piano score: measures 1–103, D minor, 6/8. No tempo mark is printed; choose a comfortable practice tempo.", "success_criterion": "I played my selected PDF section comfortably three times and recorded the exact location and next goal."})
            result["explanation"] = [{"title": "Pulse", "text": "Page 1, measures 18–23: count two main beats over the D minor bass support. Each divides into three eighth notes. Read a small group, then connect both sides."}, {"title": "A → Dm", "text": "Page 2: the A chord and C♯ are in measures 38–39; Dm returns in measure 40. D natural minor contains C; raising it to C♯ creates the leading seventh degree. Check both chord symbols and written notes."}, {"title": "Left hand and ending", "text": "Page 3, measures 72–83: isolate a small group of the continuous left-hand eighth notes. Page 4, measures 97–103: join the ending to its preceding transition. The full score includes the final Dm and closing barline."}]
            steps = [("Page 1 · 18–23", "Find measures 18–23. Count two main beats aloud; check the bass first, then both hands at a comfortable slow tempo."), ("Page 2 · 38–40", "Find A/C♯ in measures 38–39 and Dm in 40. Listen to the chords separately, then join the surrounding measures."), ("Page 3 · 72–83", "Choose a small group of the left-hand eighth notes. Play the left hand separately, then combine it with the right while keeping the pulse."), ("Page 4 · 97–103", "Join the ending with the preceding measure. Record three comfortable attempts; check the first attempt again next day.")]
        else:
            result.update({"title": "Всё произведение: четыре страницы", "summary": "Свяжите теорию и упражнения с точными местами аранжировки из 103 тактов.", "context": "Полные фортепианные ноты Alexis Quoniam: четыре страницы, такты 1–103, ре минор, 6/8. Обозначения темпа нет; выберите удобный темп занятий.", "success_criterion": "Я трижды удобно сыграл выбранный фрагмент PDF и записал точное место и следующую цель."})
            result["explanation"] = [{"title": "Пульс", "text": "Страница 1, такты 18–23: считайте две основные доли над басовой опорой ре минора. Каждая делится на три восьмые. Прочитайте небольшую группу, затем соедините её с обеих сторон."}, {"title": "A → Dm", "text": "Страница 2: аккорд A и C♯ записаны в тактах 38–39, Dm возвращается в такте 40. В ре натуральном миноре есть C; повышение до C♯ даёт вводную седьмую ступень. Проверьте обозначения аккордов и записанные звуки."}, {"title": "Левая рука и финал", "text": "Страница 3, такты 72–83: выделите небольшую группу непрерывных восьмых левой руки. Страница 4, такты 97–103: соедините финал с предшествующим переходом. Полные ноты включают последний Dm и заключительную тактовую черту."}]
            steps = [("Страница 1 · 18–23", "Найдите такты 18–23. Считайте две основные доли вслух; сначала проверьте бас, затем две руки в удобном медленном темпе."), ("Страница 2 · 38–40", "Найдите A/C♯ в тактах 38–39 и Dm в 40. Послушайте аккорды отдельно, затем соедините с соседними тактами."), ("Страница 3 · 72–83", "Выберите небольшую группу восьмых левой руки. Играйте отдельно левой, затем вместе с правой, сохраняя пульс."), ("Страница 4 · 97–103", "Соедините финал с предыдущим тактом. Запишите три удобные попытки; проверьте первую попытку на следующий день.")]
        result["steps"] = [{**original, "title": title, "instruction": instruction} for original, (title, instruction) in zip(result["steps"], steps)]
    elif code == "source-passage":
        analysis = result.get("source_analysis") or {}
        facts = analysis.get("facts", {})
        numbers = ", ".join(analysis.get("range", {}).get("measure_numbers", []))
        english = lang == "en"
        result["title"] = result.get("score_binding", {}).get("focus_section", {}).get("title") if result.get("score_binding", {}).get("focus_section") else "Selected score passage" if english else "Выбранный нотный фрагмент"
        result["summary"] = "Study the actual written passage in your imported score." if english else "Изучите фактический фрагмент импортированных нот."
        result["explanation"] = [{"title": "Written pattern" if english else "Записанный рисунок", "text": f"Measures {numbers}: {facts.get('pitched_note_count', 0)} written notes, {facts.get('rest_count', 0)} rests, {facts.get('chord_group_count', 0)} chord groups and {facts.get('tie_count', 0)} tied note events." if english else f"Такты {numbers}: {facts.get('pitched_note_count', 0)} записанных нот, {facts.get('rest_count', 0)} пауз, {facts.get('chord_group_count', 0)} аккордных групп и {facts.get('tie_count', 0)} связанных нот."}]
        if facts.get("short_pitch_names"):
            result["explanation"].append({"title": "Read, then play" if english else "Прочитайте и сыграйте", "text": ("Written tones: " if english else "Записанные звуки: ") + ", ".join(facts["short_pitch_names"])})
        step_text = [("Inspect the actual passage", f"Find measures {numbers}. Count the written rhythm and rests, then name the notes."), ("Separate the hands", "Check each labelled hand in the selected range. Confirm any uncertain hand assignments from the score."), ("Combine slowly", "Start at quarter = 40/min, an adjustable practice choice. Join the parts while checking written chord starts and sustained ties."), ("Connect the transition", "Use the step's stated range to include a neighbouring measure. Record where the transition stayed fluent or stopped.")] if english else [("Посмотрите точный фрагмент", f"Найдите такты {numbers}. Посчитайте записанный ритм и паузы, затем назовите звуки."), ("Разделите руки", "Проверьте каждую обозначенную руку в выбранном диапазоне. Уточните спорное распределение рук по нотам."), ("Соедините медленно", "Начните с четверти = 40/мин; это изменяемый темп занятия. Соедините партии, проверяя начало аккордов и связанные ноты."), ("Переход в контексте", "Используйте указанный диапазон шага, включающий соседний такт. Запишите, где переход прошёл плавно или остановился.")]
        result["steps"] = [{**step, "title": title, "instruction": instruction} for step, (title, instruction) in zip(result["steps"], step_text)]
        result["success_criterion"] = "I played the selected written passage comfortably three times and recorded its difficult point and next goal." if english else "Я трижды удобно сыграл выбранный нотный фрагмент и записал трудное место и следующую цель."
        if analysis:
            analysis["steps"] = deepcopy(result["steps"])
            analysis["cautions"] = []
            if facts.get("hand_counts", {}).get("unknown"):
                analysis["cautions"].append("Some hand assignments are unknown; confirm them from the score." if english else "Руки для некоторых нот не определены; уточните их по нотам.")
            if facts.get("playable_pitch_count", 0) < facts.get("pitched_note_count", 0):
                analysis["cautions"].append("Some pitches lie outside the 88-key range or are microtonal." if english else "Некоторые звуки вне диапазона 88 клавиш или микротональные.")
            result["source_analysis"] = analysis
    arrangement = lesson.arrangement
    if code not in ["choose-exact-version", "pdf-full-piece"]:
        if lesson.score_version_id:
            binding = result.get("score_binding") or {}
            result["context"] = f"Imported score «{binding.get('title', '')}», version {binding.get('version', '')}. " if lang == "en" else f"Импортированные ноты «{binding.get('title', '')}», версия {binding.get('version', '')}. "
            result["context"] += "Written observations and playing skill are checked separately." if lang == "en" else "Записанные данные и исполнительское умение проверяются отдельно."
        elif arrangement.full_score_verified_at:
            result["context"] = "Original preparation for Alexis Quoniam's complete four-page D minor / 6/8 piano arrangement. Return to the actual PDF after the drill." if lang == "en" else "Оригинальная подготовка к полной четырёхстраничной аранжировке Alexis Quoniam: ре минор, 6/8. После упражнения вернитесь к фактическим нотам PDF."
        else:
            result["context"] = "Original preparation linked to the selected arrangement's verified metadata." if lang == "en" else "Оригинальная подготовка по подтверждённым данным выбранной аранжировки."
    result["exercise"]["label"] = "Complete four-page piano score" if code == "pdf-full-piece" and lang == "en" else "Полные фортепианные ноты: четыре страницы" if code == "pdf-full-piece" else "Imported score passage" if lesson.kind == "source_excerpt" and lang == "en" else "Фрагмент импортированных нот" if lesson.kind == "source_excerpt" else "Choose the complete score" if lesson.kind == "source" and lang == "en" else "Выберите полные ноты" if lesson.kind == "source" else "KuyLab original preparation drill" if lang == "en" else "Оригинальное подготовительное упражнение KuyLab"
    count_words = {"BIR": "ONE" if lang == "en" else "РАЗ", "IKKI": "TWO" if lang == "en" else "ДВА", "la": "and" if lang == "en" else "и", "li": "a" if lang == "en" else "а", "va": "and" if lang == "en" else "и"}
    if "counting" in result["exercise"]:
        result["exercise"]["counting"] = [count_words.get(word, word) for word in result["exercise"]["counting"]]
    result["transfer"] = "Return to the actual complete score, apply this lesson to your selected passage and record one observation." if lang == "en" else "Вернитесь к фактическим полным нотам, примените урок в выбранном фрагменте и запишите одно наблюдение."
    if code == "choose-exact-version":
        result["transfer"] = "Begin composition lessons after selecting the complete source." if lang == "en" else "Начните уроки по произведению после выбора полного источника."
    questions = [localized_question(question, lesson, lang) for question in lesson.quiz.get("questions", [])]
    result["quiz"] = {"questions": [{key: question[key] for key in ["id", "prompt", "choices"]} for question in questions]}
    result["sources"] = [{**source, "title": source["title"].replace("to'liq pianino notasi", "complete piano score" if lang == "en" else "полные фортепианные ноты")} for source in result.get("sources", [])]
    return result


def localized_plan(plan, lessons, lang):
    if lang == "uz":
        return plan
    import re
    result = deepcopy(plan)
    lesson_map = {item.id: item for item in lessons}
    midi_course = any(item.content.get("exercise", {}).get("type") == "midi_source_fragment" for item in lessons)
    title_map = {item.id: localized_lesson({"title": item.title, "summary": item.summary, "context": item.context, "explanation": item.content.get("explanation", []), "steps": item.content.get("steps", []), "exercise": item.content.get("exercise", {}), "success_criterion": item.success_criterion, "quiz": item.quiz, "score_binding": item.content.get("score_binding"), "source_analysis": item.content.get("source_analysis")}, item, lang)["title"] for item in lessons}
    labels = {"break": ("Short break", "Короткий перерыв"), "reflect": ("Result and next check", "Результат и следующая проверка"), "transfer": ("Return to the piece", "Вернитесь к произведению")}
    for item in result["items"]:
        lesson = lesson_map.get(item.get("lesson_id"))
        item["title"] = labels[item["kind"]][0 if lang == "en" else 1] if item["kind"] in labels else title_map.get(item.get("lesson_id"), item["title"])
        if item["kind"] == "review":
            item["reason"] = "The delayed check is due: repeat the quiz and practical attempt." if lang == "en" else "Пришло время отложенной проверки: повторите тест и практическую попытку."
        elif item["kind"] == "break":
            item["reason"] = "Rest briefly and check comfort before continuing." if lang == "en" else "Немного отдохните и проверьте удобство перед продолжением."
        elif item["kind"] == "reflect":
            item["reason"] = "Record the exact location, tempo unit, attempt result and next goal." if lang == "en" else "Запишите точное место, единицу темпа, результат попытки и следующую цель."
        elif item["kind"] == "transfer":
            item["reason"] = "Apply the lesson in this exact MIDI passage and join the neighbouring notes." if lang == "en" and midi_course else "Примените урок в точном MIDI-фрагменте и соедините соседние звуки." if midi_course else "Apply the lesson in the actual selected score and check a small transition." if lang == "en" else "Примените урок в выбранных фактических нотах и проверьте небольшой переход."
        elif lesson and lesson.kind == "source_excerpt":
            item["reason"] = "Your chosen composition is the priority: use its exact MIDI fragment." if lang == "en" and midi_course else "В приоритете выбранное произведение: используйте его точный MIDI-фрагмент." if midi_course else "Your chosen composition is the priority: work from its actual complete score." if lang == "en" else "В приоритете выбранное произведение: работайте по его фактическим полным нотам."
        elif lesson and lesson.kind == "source":
            item["reason"] = "Select a complete, exact arrangement before composition teaching." if lang == "en" else "Выберите полную точную аранжировку перед уроками по произведению."
        else:
            label = SKILL_LABELS[lang].get(lesson.skill, "") if lesson else ""
            item["reason"] = label + (": selected from your latest answers and reported practice; theory and playing remain separate." if lang == "en" else ": выбрано по последним ответам и отмеченной практике; теория и игра учитываются отдельно.")
            original_item = next(original for original in plan["items"] if original.get("lesson_id") == item.get("lesson_id") and original["kind"] == item["kind"])
            score = re.search(r"(\d+)/100", original_item.get("reason", ""))
            item["reason"] += (f" Latest estimate: {score.group(1)}/100." if lang == "en" else f" Последняя оценка: {score.group(1)}/100.") if score else (" Not assessed yet." if lang == "en" else " Пока не проверено.")
    result["language"] = lang
    result["source_notice"] = NOTICES[lang]["pending"] if plan.get("basis") == "source_pending" else "The MIDI player is separate; each lesson uses exact source notes and timestamps." if lang == "en" and midi_course else "MIDI-плеер открыт отдельно; уроки используют точные звуки и время источника." if midi_course else "Work with the complete selected score; return to the composition after original preparation." if lang == "en" else "Работайте с полными выбранными нотами; после оригинальной подготовки возвращайтесь к произведению."
    return result


def localized_legacy_plan(data, lang):
    if lang == "uz":
        return data
    result = deepcopy(data)
    if (data.get("arrangement") or {}).get("workflow_status") != "full_score_ready":
        return result
    english = lang == "en"
    result["title"] = "He's a Pirate: complete score practice" if english else "He's a Pirate: занятия по полным нотам"
    result["summary"] = "Alexis Quoniam's complete four-page, 103-measure piano arrangement: D minor, 6/8. No tempo is printed. Connect theory and original preparation to actual PDF locations." if english else "Полная фортепианная аранжировка Alexis Quoniam: четыре страницы, 103 такта, ре минор, 6/8. Темп не указан. Свяжите теорию и оригинальную подготовку с точными местами PDF."
    tasks = [("Complete score and performance", "Open all four score pages and locate the opening and ending, measures 1–103. Listen to the reference arrangement.", "Form", "I located the complete score and selected arrangement."), ("Two main beats in 6/8", "Page 1, measures 18–23: count two main beats. Play the original 6/8 preparation, then return to the PDF.", "6/8", "Two main beats and their three subdivisions remained steady."), ("Left-hand eighth notes", "Page 3, measures 72–83: check a small group of continuous left-hand eighth notes at a comfortable tempo. Read first, then combine the hands.", "Coordination", "The selected small group was comfortable in three attempts."), ("Harmony and ending", "Page 2: A/C♯ in measures 38–39 returns to Dm in 40. Page 4, measures 97–103: join the ending at a comfortable tempo.", "D minor and expression", "I played my chosen transition without stopping."), ("Next attempt", "Record one difficult place, tempo unit and three attempt results. Test the same place first next day.", "Delayed check", "I saved a specific next goal.")] if english else [("Полные ноты и исполнение", "Откройте все четыре страницы, найдите начало и конец, такты 1–103. Послушайте выбранную аранжировку.", "Форма", "Я нашёл полные ноты и выбранную аранжировку."), ("Две основные доли в 6/8", "Страница 1, такты 18–23: считайте две основные доли. Сыграйте оригинальную подготовку в 6/8 и вернитесь к PDF.", "6/8", "Две основные доли и тройные деления остались ровными."), ("Восьмые левой руки", "Страница 3, такты 72–83: проверьте небольшую группу непрерывных восьмых левой руки в удобном темпе. Сначала прочитайте, затем соедините руки.", "Координация", "Выбранная группа была удобной в трёх попытках."), ("Гармония и финал", "Страница 2: A/C♯ в тактах 38–39 возвращается к Dm в 40. Страница 4, такты 97–103: соедините финал в удобном темпе.", "Ре минор и выразительность", "Я сыграл выбранный переход без остановки."), ("Следующая попытка", "Запишите одно трудное место, единицу темпа и результат трёх попыток. На следующий день сначала проверьте то же место.", "Отложенная проверка", "Я сохранил конкретную следующую цель.")]
    for item in result.get("tasks", []):
        if 1 <= item["order"] <= len(tasks):
            item["title"], item["instructions"], item["concept"], item["success_criterion"] = tasks[item["order"] - 1]
    result["language"] = lang
    return result
