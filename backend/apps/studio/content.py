"""Authored practical curriculum. All examples are produced by midi_authoring.

UZ teaching intentionally includes Russian terminology; translations are authored,
not a claim that the MIDI contains words, theory, fingerings or formal sections.
"""
from .practice_reviews import EXTRA_FAMILIES, exercise_review
from .theory_reviews import EXTRA_THEORY, theory_review

REVISION = "piano-courses-2026-10-v17"


def tr(uz, ru, en):
    return {"uz": uz, "ru": ru, "en": en}


def localize(value, language):
    if isinstance(value, dict):
        if set(value) == {"uz", "ru", "en"}:
            return value[language]
        return {key: localize(item, language) for key, item in value.items()}
    if isinstance(value, list):
        return [localize(item, language) for item in value]
    return value


CATEGORIES = [
    ("coordination", tr("Qo‘llar koordinatsiyasi", "Координация рук", "Hand coordination")),
    ("technique", tr("Texnika va aniqlik", "Техника и точность", "Technique and accuracy")),
    ("rhythm", tr("Ritm va barqarorlik", "Ритм и устойчивость", "Rhythm and consistency")),
    ("expression", tr("Ifodali chalish", "Выразительность", "Expression")),
    ("pedal", tr("Pedal", "Педаль", "Pedal")),
    ("harmony", tr("Akkord va garmoniya", "Аккорды и гармония", "Chords and harmony")),
    ("foundations", tr("Amaliy asoslar", "Практические основы", "Practical foundations")),
]
GOALS = [
    ("independence", tr("Ikki qo‘lni erkin boshqarish", "Независимость рук", "Independent hands")),
    ("accuracy", tr("Toza va aniq chalish", "Чистота и точность", "Play accurately")),
    ("fluency", tr("Ravon va uzluksiz chalish", "Беглость и непрерывность", "Play fluently")),
    ("pulse", tr("Tempni barqaror saqlash", "Устойчивый темп", "Keep a steady pulse")),
    ("musicality", tr("Ifodali eshitilish", "Музыкальная выразительность", "Shape the sound")),
    ("understanding", tr("Chalayotganimni tushunish", "Понимать исполняемое", "Understand what you play")),
]

FAMILIES = [
    ("five-finger", "coordination", ["independence", "accuracy"],
     tr("Besh barmoq", "Пять пальцев", "Five fingers"),
     tr("Barmoqlar mustaqilligi — независимость пальцев. Besh tovushli pozitsiyada har bir bosish bir xil ravshan bo‘lsin; ishlamayotgan barmoqlarni yuqoriga tortmang.", "Независимость пальцев в пятипальцевой позиции. Добивайтесь одинаковой ясности звука, не поднимая свободные пальцы высоко.", "Keep five fingers over a five-note position. Aim for equally clear attacks without lifting the unused fingers high."),
     [tr("Ikki qo‘l bir yo‘nalishda, har urishda bitta tovush.", "Руки движутся одинаково, по звуку на долю.", "Both hands follow the same pattern, one note per beat."),
      tr("Qo‘shni bo‘lmagan barmoqlar almashadi; bilakni buramang.", "Чередуйте несоседние пальцы без поворота запястья.", "Alternate nonadjacent fingers without twisting the wrist."),
      tr("Qo‘llar turlicha tartibda yuradi; avval alohida, keyin birga.", "Разные последовательности в руках: сначала отдельно, затем вместе.", "The hands use different sequences: separate first, then together.")],
     tr("C–D–E–F–G: o‘ng 1–2–3–4–5, chap 5–4–3–2–1. Bu mashq uchun tavsiya.", "C–D–E–F–G: правая 1–2–3–4–5, левая 5–4–3–2–1. Рекомендация для этого упражнения.", "C–D–E–F–G: RH 1–2–3–4–5, LH 5–4–3–2–1; suggested for this study.")),
    ("scales", "technique", ["accuracy", "fluency"],
     tr("Do major gammasi", "Гамма до мажор", "C major scale"),
     tr("Gamma — гамма. Bosh barmoqni kaft ostiga zo‘rlab tiqmang: qo‘l yon tomonga yengil siljib, keyingi pozitsiyaga o‘tadi. O‘tishda tovush balandlashmasin.", "При смене позиции не зажимайте большой палец под ладонью: слегка перемещайте всю руку. Переход не должен создавать акцент.", "Move the hand gently sideways through each thumb transition. Avoid forcing the thumb under a fixed palm or accenting the change."),
     [tr("O‘ng qo‘lda bir oktava; barmoq almashadigan joyni sekinlang.", "Одна октава правой рукой; замедлите смену пальцев.", "One octave in the right hand; slow the fingering transition."),
      tr("Ikki oktava, ikki qo‘l parallel; oktava chegarasida to‘xtamang.", "Две октавы параллельно обеими руками без остановки на границе октавы.", "Two octaves in parallel motion; do not stop at the octave boundary."),
      tr("Ikki oktava qarama-qarshi harakat; har bir qo‘l yo‘lini oldindan ko‘ring.", "Две октавы в противоположном движении; заранее видьте путь каждой руки.", "Two octaves in contrary motion; anticipate each hand's path.")],
     tr("O‘ng yuqoriga: 1–2–3–1–2–3–4–5. Ikki oktavada oraliq C ga 1. Chap yuqoriga: 5–4–3–2–1–3–2–1; pastga teskari.", "Правая вверх: 1–2–3–1–2–3–4–5; промежуточное C в двух октавах — 1. Левая вверх: 5–4–3–2–1–3–2–1; вниз наоборот.", "RH ascending: 1–2–3–1–2–3–4–5; use 1 on the intermediate C over two octaves. LH ascending: 5–4–3–2–1–3–2–1; reverse descending.")),
    ("arpeggios", "technique", ["fluency", "accuracy"],
     tr("Do major arpejiosi", "Арпеджио до мажор", "C major arpeggio"),
     tr("Arpejio — арпеджио: akkord tovushlari ketma-ket chalinadi. Keyingi tovushga barmoqni cho‘zib yetish o‘rniga butun qo‘lni siljiting.", "Арпеджио — последовательные звуки аккорда. Перемещайте всю руку вместо чрезмерного растяжения пальцев к следующему звуку.", "An arpeggio unfolds a chord one note at a time. Move the hand to the next position instead of stretching fingers excessively."),
     [tr("C–E–G–E–C: bir pozitsiyadan boshlang‘ich C ga ravon qaytish.", "C–E–G–E–C: ровное возвращение к начальному C в одной позиции.", "C–E–G–E–C: return evenly to the starting C within one position."),
      tr("C–E–G–C yo‘li, ikki qo‘l; yuqoridagi C ga aksent bermang.", "C–E–G–C обеими руками; без акцента на верхнем C.", "C–E–G–C with both hands; avoid accenting the top C."),
      tr("Ikki oktava; qo‘l harakati va bosh barmoq o‘tishini uzluksiz ulang.", "Две октавы: соединяйте перенос руки и смену большого пальца.", "Two octaves; connect hand travel and thumb changes smoothly.")],
     tr("C–E–G: o‘ng 1–2–3, chap 5–3–2. Bir oktava C–E–G–C: o‘ng 1–2–3–5, chap 5–3–2–1. Kenglik qo‘lga mos bo‘lmasa arpejioni sekin siljib chaling.", "C–E–G: правая 1–2–3, левая 5–3–2. Октава C–E–G–C: правая 1–2–3–5, левая 5–3–2–1. Не растягивайте руку через усилие.", "C–E–G: RH 1–2–3, LH 5–3–2. One octave C–E–G–C: RH 1–2–3–5, LH 5–3–2–1. Move slowly rather than forcing a stretch.")),
    ("chords", "harmony", ["fluency", "understanding"],
     tr("Akkord almashish", "Смена аккордов", "Chord changes"),
     tr("Akkord — аккорд. Tovushlar bir vaqtda boshlansin. Umumiy tovushlarni topib, keyingi shaklga eng qisqa harakat bilan o‘ting.", "Начинайте звуки аккорда одновременно. Находите общие звуки и переходите к следующей форме кратчайшим движением.", "Start chord notes together. Find shared tones and take the shortest comfortable path to the next shape."),
     [tr("C major shaklini ko‘taring va qayta yumshoq tushiring.", "Мягко снимайте и вновь берите трезвучие C major.", "Release and gently reset a C major triad."),
      tr("C–F–G–C aylanishlari; umumiy C yoki G joyini yodda tuting.", "Обращения C–F–G–C: сохраняйте ориентиры C и G.", "C–F–G–C inversions: keep C and G as landmarks."),
      tr("To‘rt tovushli shakllar; ichki ovozlarni bir tekis, yuqorini ravshan chaling.", "Четырёхзвучные формы: ровные внутренние голоса и ясный верх.", "Four-note shapes: keep inner voices even and the top clear.")],
     tr("Uch tovushli yaqin shaklda o‘ng 1–3–5 yoki 1–2–5 ni solishtiring; eng erkin variantni tanlang. Bu yagona universal barmoqlash emas.", "Для тесного трезвучия сравните 1–3–5 и 1–2–5 правой рукой; выбирайте свободный вариант. Универсальной схемы нет.", "For a close triad compare RH 1–3–5 and 1–2–5; choose a relaxed option. This is not a universal fingering.")),
    ("coordination", "coordination", ["independence", "pulse"],
     tr("Turli ritmli qo‘llar", "Разный ритм в руках", "Independent hand rhythms"),
     tr("Koordinatsiya — координация. Qaysi zarbalar birga tushishini ajrating; qo‘llarni faqat tezlik hisobiga birlashtirmang.", "Отмечайте совпадающие атаки. Соединяйте руки через понятную ритмическую опору, а не за счёт скорости.", "Identify the attacks that coincide. Coordinate through a clear rhythmic reference rather than relying on speed."),
     [tr("O‘ng har urishda, chap har ikki urishda. Birga tushadigan zarbalarni sanang.", "Правая каждую долю, левая через долю. Считайте совпадения.", "RH every beat, LH every two beats; count the shared attacks."),
      tr("O‘ngda ikkita, chapda bitta tovush — 2:1.", "Два звука справа на один слева — 2:1.", "Two RH notes for every LH note: 2:1."),
      tr("O‘ng har 0.5, chap har 0.75 urishda: 3:2. Avval 1.5 urishli bitta siklni ajrating.", "Правая через 0.5, левая через 0.75 доли: 3:2. Начните с цикла в 1.5 доли.", "RH every 0.5 beats and LH every 0.75: 3:2. Isolate one 1.5-beat cycle first.")], None),
    ("rhythm", "rhythm", ["pulse", "accuracy"],
     tr("Ritmni ajratish", "Ритмические деления", "Rhythmic subdivisions"),
     tr("Puls — пульс — o‘zgarmas tayanch. Qisqa tovushlar ko‘payganda pulsni tezlashtirmang; avval o‘ng ritmni chap puls ustida qarsak bilan sinang.", "Пульс остаётся опорой при любом количестве звуков. Сначала прохлопайте правый ритм поверх ровных долей левой.", "Keep the pulse stable when the number of notes changes. First clap the right-hand rhythm over the steady left-hand beats."),
     [tr("Chorak va yarim davomiylik; uzun tovush ichida sanash davom etadi.", "Четверти и половины; продолжайте счёт внутри длинного звука.", "Quarter and half durations; keep counting through long notes."),
      tr("Nuqtali ritm: 3:1 uzun-qisqa nisbatini eshiting.", "Пунктир: слушайте соотношение длинного и короткого 3:1.", "Dotted rhythm: hear the long-short ratio of 3:1."),
      tr("Ikkilik va uchlik bo‘linish navbatlashadi; umumiy puls saqlansin.", "Чередуйте двоичные и троичные деления при общем пульсе.", "Alternate binary and triplet subdivisions while keeping the pulse.")], None),
    ("leaps", "technique", ["accuracy", "fluency"],
     tr("Chap qo‘l sakrashlari", "Скачки левой руки", "Left-hand leaps"),
     tr("Sakrash — скачок. Keyingi klavishni ko‘z bilan oldindan toping. Qo‘lni yuqoriga ortiqcha ko‘tarmasdan yon tomonga olib boring.", "Заранее находите следующую клавишу взглядом. Переносите руку в сторону без лишнего вертикального движения.", "Look ahead to the destination key. Travel sideways without unnecessary lifting."),
     [tr("Kvinta oralig‘i: avval jim qo‘nishni, keyin tovushni mashq qiling.", "Квинта: сначала беззвучное попадание, затем звук.", "A fifth: rehearse a silent landing before sounding the key."),
      tr("Oktava sakrashi ustida o‘ng qo‘l melodiyasi davom etadi.", "Правая мелодия продолжается над октавными скачками.", "Keep the RH melody moving over octave leaps."),
      tr("Oktava va kvinta masofasi; masofani qo‘lni tarang cho‘zish bilan bosmang.", "Октава плюс квинта: переносите руку, не растягивайте её через напряжение.", "An octave plus a fifth: move the arm instead of forcing a stretch.")], None),
    ("octaves", "technique", ["accuracy", "fluency"],
     tr("Yengil oktavalar", "Свободные октавы", "Relaxed octaves"),
     tr("Oktava — октава. Har bosishdan so‘ng taranglikni bo‘shating. Qo‘lga kenglik noqulay bo‘lsa tovushlarni navbat bilan chaling; zo‘rlamang.", "После каждой атаки освобождайте напряжение. Если размах неудобен, играйте звуки последовательно, без усилия.", "Release tension after each attack. If the span is uncomfortable, play the tones successively rather than forcing it."),
     [tr("Bitta oktava shakli, bosishlar orasida bo‘shashish.", "Одна октавная позиция с расслаблением между атаками.", "One octave position, relaxing between attacks."),
      tr("Oktavalar besh tovushli yo‘lda siljiydi.", "Октавы движутся по пятипальцевому звукоряду.", "Move octaves along a five-note contour."),
      tr("Ikki qo‘lda parallel oktavalar; past ovoz yuqorini bosmasin.", "Параллельные октавы обеими руками; низ не перекрывает верх.", "Parallel octaves in both hands; keep the bass below the upper voice.")],
     tr("Oktavalar uchun 1–5 odatiy tavsiya; qulaylik va qo‘l o‘lchami ustuvor.", "Обычно 1–5; комфорт и размер руки важнее схемы.", "1–5 is a common octave fingering; comfort and hand size take priority.")),
    ("articulation", "expression", ["independence", "musicality"],
     tr("Legato va stakkato", "Легато и стаккато", "Legato and staccato"),
     tr("Legato — легато — tovushlarni ulash; stakkato — стаккато — qisqa ajratish. Farqni faqat ovoz balandligida emas, klavishni ushlash vaqtida yarating.", "Легато соединяет звуки, стаккато отделяет. Создавайте контраст длительностью удержания, а не только громкостью.", "Legato connects tones; staccato separates them. Create the contrast through key duration, not merely volume."),
     [tr("Avval sakkizta ulangan, keyin sakkizta qisqa tovush.", "Восемь связанных звуков, затем восемь коротких.", "Eight connected tones followed by eight short tones."),
      tr("O‘ngda uzun-qisqa almashadi, chapda qisqa tayanch.", "Справа длинный-короткий, слева короткая опора.", "RH alternates long and short over a short LH accompaniment."),
      tr("Qo‘llarda qarama-qarshi artikulyatsiya; chap uzun bo‘lsa o‘ng qisqa.", "Противоположная артикуляция: длинный слева — короткий справа.", "Opposite articulations: a long LH tone against a short RH tone.")], None),
    ("balance", "expression", ["musicality", "independence"],
     tr("Melodiyani ajratish", "Баланс мелодии и сопровождения", "Melody and accompaniment"),
     tr("Ovozlar balansi — баланс голосов. Yuqori melodiyani kuylayotgandek tasavvur qiling. Pastdagi tovushlar aniq eshitilsin, ammo melodiyadan yumshoqroq.", "Представляйте верхнюю мелодию как пение. Нижние звуки должны быть ясными, но мягче мелодии.", "Imagine singing the top line. Keep lower tones clear but softer than the melody."),
     [tr("O‘ng ravshan, chap doim yumshoq.", "Правая ясная, левая стабильно мягкая.", "A clear RH melody over a consistently soft LH."),
      tr("Melodiya kuchayib-so‘nadi, jo‘rlik darajasi o‘zgarmaydi.", "Мелодия растёт и затихает, сопровождение остаётся ровным.", "Let the melody rise and fall while accompaniment stays even."),
      tr("Ikkala qo‘lning dinamikasi mustaqil; har to‘rtlikni bitta jumla deb eshiting.", "Независимая динамика рук; слушайте каждую четвёрку как фразу.", "Independent dynamics in both hands; hear each group of four as a phrase.")], None),
    ("pedal", "pedal", ["musicality", "accuracy"],
     tr("Pedalni toza almashtirish", "Чистая смена педали", "Clean pedal changes"),
     tr("Kechiktirilgan pedal — запаздывающая педаль. Yangi akkord bosilganda eski pedalni ko‘tarib, keyin qayta bosing. Namuna MIDI’sida bu CC64 bilan ko‘rsatilgan.", "При новом аккорде снимите старую педаль и затем нажмите снова. В примере это показано сообщениями CC64.", "At a new chord release the old pedal, then press again. The example encodes this with CC64 sustain messages."),
     [tr("To‘rt akkord, har biri uchun bitta pedal almashtirish.", "Четыре аккорда, одна смена педали на каждый.", "Four chords, one pedal change per chord."),
      tr("Akkord ustida melodiya: pedal melodiyaning ravshanligini buzmasin.", "Мелодия над аккордами: педаль не размывает её ясность.", "A melody over chords: keep the pedal from blurring it."),
      tr("Akkord ichida ham qo‘shimcha tozalash; quloq bilan farqni eshiting.", "Дополнительная смена внутри аккорда: услышите, как очищается звучание.", "Refresh the pedal inside each chord and hear the clearer texture.")], None),
    ("continuity", "rhythm", ["fluency", "pulse"],
     tr("To‘xtamasdan jumla chalish", "Непрерывное исполнение фразы", "Continuous phrasing"),
     tr("Barqarorlik — устойчивость. Xato bo‘lsa har safar boshidan boshlamang: pulsni saqlab keyingi tayanchga yeting, keyin qiyin joyni alohida ajrating.", "При ошибке не начинайте каждый раз сначала. Сохраните пульс до следующей опоры, затем отдельно разберите трудность.", "Do not restart from the beginning after every error. Keep the pulse to the next landmark, then isolate the difficult spot."),
     [tr("Bir qo‘lda 16 urishli jumla; oxirigacha barqaror chaling.", "Фраза в 16 долей одной рукой до конца без остановок.", "A 16-beat phrase in one hand, steady to the end."),
      tr("Jo‘rlik qo‘shiladi; melodiyani ichingizda kuylang.", "Добавляется сопровождение; мысленно пойте мелодию.", "Add accompaniment while singing the melody internally."),
      tr("O‘ng har to‘rtinchi urishda jim, chap puls davom etadi.", "Правая молчит на каждой четвёртой доле, левая продолжает пульс.", "RH rests on every fourth beat while LH keeps the pulse.")], None),
]
FAMILIES += EXTRA_FAMILIES

LEVELS = ["easy", "intermediate", "advanced"]
LEVEL_LABELS = [tr("Oson", "Легко", "Easy"), tr("O‘rta", "Средне", "Intermediate"), tr("Murakkab", "Сложно", "Advanced")]


def exercise_items():
    items = []
    for family, category, goals, title, explanation, variants, fingering in FAMILIES:
        for index, level in enumerate(LEVELS):
            item = {"id": f"exercise:{family}:{level}", "kind": "exercise", "title": title,
                    "subtitle": variants[index], "category": category, "goals": goals, "level": level,
                    "minutes": [4, 6, 8][index], "intro": variants[index],
                    "explanation": [{"title": tr("Nimaga e’tibor beramiz", "На что обратить внимание", "What to listen for"), "text": explanation}],
                    "steps": [
                        {"title": tr("Tinglang", "Послушайте", "Listen"), "instruction": variants[index]},
                        {"title": tr("Sekin sinang", "Попробуйте медленно", "Try slowly"), "instruction": tr("Avval 50–70% tezlikda bitta siklni chaling. Kerak bo‘lsa timeline orqali uning boshiga qayting; tovushlar va harakat ravshanlashgach davom eting.", "Начните с одного цикла на 50–70% скорости. При необходимости вернитесь по шкале к его началу; продолжайте, когда звук и движение ясны.", "Begin with one cycle at 50–70% speed. If needed, seek back to its start on the timeline; continue when the sound and movement are clear.")},
                        {"title": tr("Eshiting va solishtiring", "Слушайте и сравнивайте", "Listen and compare"), "instruction": explanation},
                    ], "related_ids": [f"exercise:{family}:{other}" for other in LEVELS if other != level],
                    "_generator": {"family": family, "level": index}}
            if fingering: item["fingering"] = fingering
            review = exercise_review(family, index)
            item["explanation"].extend(review.pop("explanation"))
            item["related_ids"].extend(review.pop("related_ids"))
            item.update(review)
            items.append(item)
    return items


THEORY = [
    ("keyboard", "foundations", tr("Klavishlar va yarim ton", "Клавиши и полутон", "Keys and semitones"),
     tr("Yarim ton — полутон — klaviaturadagi eng yaqin qo‘shni tovush. E–F va B–C orasida qora klavish yo‘q, lekin masofa baribir yarim ton. ♯ tovushni yarim ton ko‘taradi, ♭ esa tushiradi. Pianinoda bitta qora klavish ikki nomga ega bo‘lishi mumkin: C♯=D♭, D♯=E♭, G♯=A♭ va A♯=B♭. Player qora klavishlarni ♯ nomlari bilan ko‘rsatadi.", "Полутон — расстояние между соседними клавишами. Между E–F и B–C нет чёрной клавиши, но расстояние также полутон. ♯ повышает звук на полутон, ♭ понижает. Одна чёрная клавиша может иметь два имени: C♯=D♭, D♯=E♭, G♯=A♭, A♯=B♭. Плеер подписывает чёрные клавиши через ♯.", "A semitone is the distance between adjacent keys. E–F and B–C have no black key between them, but are still a semitone apart. A sharp raises a tone by one semitone; a flat lowers it. One piano key can have two names: C♯=D♭, D♯=E♭, G♯=A♭ and A♯=B♭. The player uses sharp names for black keys."),
     tr("C dan G gacha oq-qora klavishlarni ketma-ket tinglang. E–F o‘tishini toping.", "Прослушайте все клавиши от C до G. Найдите переход E–F.", "Hear every key from C to G, then locate the E–F transition.")),
    ("pulse", "rhythm", tr("Puls va ritm", "Пульс и ритм", "Pulse and rhythm"),
     tr("Puls — пульс — muntazam tayanch; ritm — ритм — tovush va sukutning shu tayanch ustidagi tartibi. Har nota alohida puls bo‘lishi shart emas.", "Пульс — регулярная опора; ритм — порядок звуков и пауз поверх неё. Не каждой ноте соответствует отдельная доля.", "Pulse is the regular reference; rhythm arranges sounds and silences over it. A note does not always equal a beat."),
     tr("Chapning tekis zarbalarini sanang, o‘ngdagi tovushlar soni o‘zgarsa ham sanashni saqlang.", "Считайте ровные доли левой, даже когда количество звуков справа меняется.", "Count the steady LH beats even when the RH note count changes.")),
    ("durations", "rhythm", tr("Tovush davomiyligi", "Длительности", "Note durations"),
     tr("Davomiylik — длительность — tovushni qancha ushlash. Namunada 4, 2, 1 va yarim urishli tovushlar bor; tezlik o‘zgarsa nisbatlar saqlanadi.", "Длительность определяет время удержания. В примере 4, 2, 1 и половина доли; при смене темпа отношения сохраняются.", "Duration is how long a note lasts. The example uses 4, 2, 1 and half beats; their ratios remain when tempo changes."),
     tr("Uzun tovush davomida ham ichingizda teng urishlarni sanang.", "Продолжайте считать равные доли внутри длинного звука.", "Keep counting equal beats throughout the longer notes.")),
    ("rests", "rhythm", tr("Sukutda ham ritm bor", "Пауза сохраняет ритм", "Rests keep the rhythm"),
     tr("Pauza — пауза — vaqtning yo‘qolishi emas, belgilangan sukut. Qo‘lni bo‘shating, lekin ichki pulsni ushlang.", "Пауза — отмеренная тишина, а не исчезновение времени. Освободите руку, сохранив внутренний пульс.", "A rest is measured silence, not missing time. Relax your hand while keeping an internal pulse."),
     tr("Namunadagi bo‘sh urishlarni ovoz chiqarmasdan sanang va keyingi tovushga o‘z vaqtida kiring.", "Молча считайте пустые доли и вовремя вступайте следующим звуком.", "Count the silent beats and re-enter on time.")),
    ("intervals", "harmony", tr("Intervalni eshitish", "Слышать интервалы", "Hear intervals"),
     tr("Interval — интервал — ikki tovush orasidagi masofa. Namuna C dan turli yuqori tovushlarga yuradi; kichik qadam va keng sakrashni farqlang.", "Интервал — расстояние между двумя звуками. Пример идёт от C к разным верхним звукам: различайте шаг и скачок.", "An interval is the distance between two tones. Listen from C to different upper tones and distinguish steps from leaps."),
     tr("Har juftlikdan keyin keyingi tovushni kuylab ko‘ring; keyin klaviaturadagi masofani ko‘ring.", "После пары попробуйте пропеть верхний звук, затем посмотрите расстояние на клавиатуре.", "Sing the upper note after each pair, then look at its keyboard distance.")),
    ("major-minor", "harmony", tr("Major va minor farqi", "Мажор и минор", "Major and minor"),
     tr("C–E–G major, C–E♭–G minor uch tovushligidir. Tersiya — терция — bitta yarim ton o‘zgarib, akkord tusini o‘zgartiradi; kayfiyat faqat shu bilan belgilanmaydi.", "C–E–G — мажорное, C–E♭–G — минорное трезвучие. Изменение терции на полутон меняет окраску; настроение зависит не только от лада.", "C–E–G is major; C–E♭–G is minor. Moving the third by a semitone changes its color; mood depends on more than the mode."),
     tr("Pastki va yuqori tovushni saqlab, faqat o‘rtadagini almashtiring.", "Сохраните нижний и верхний звуки, меняя только средний.", "Keep the outer tones and change only the middle tone.")),
    ("triads", "harmony", tr("Uch tovushli akkord", "Трезвучие", "Triads"),
     tr("Uch tovushlik — трезвучие — asosiy holatda tersiyalar bilan tuzilgan akkord. C–E–G ni avval ketma-ket, keyin birga eshiting.", "Трезвучие в основном положении строится по терциям. Прослушайте C–E–G последовательно и одновременно.", "A root-position triad stacks thirds. Hear C–E–G successively, then together."),
     tr("Uch klavishga oldindan qo‘nib, bir vaqtda bosishga harakat qiling.", "Заранее расположите пальцы на трёх клавишах и нажмите вместе.", "Place the fingers over all three keys before pressing together.")),
    ("inversions", "harmony", tr("Akkord aylanishi", "Обращение аккорда", "Chord inversions"),
     tr("Aylanish — обращение — akkord tovushlari saqlanib, eng past tovushning o‘zgarishi. C–E–G, E–G–C, G–C–E: uchalasi ham C major.", "В обращении звуки аккорда сохраняются, а нижний меняется. C–E–G, E–G–C, G–C–E — всё C major.", "An inversion keeps the chord tones but changes the lowest one. C–E–G, E–G–C and G–C–E are all C major."),
     tr("Uch shaklni solishtiring. Qaysi tovush pastdan yuqoriga ko‘chganini toping.", "Сравните три формы: какой звук перенесён снизу вверх?", "Compare the three shapes and identify the tone moved from bottom to top.")),
    ("tonic-dominant", "harmony", tr("Tayanch va qaytish", "Тоника и доминанта", "Tonic and dominant"),
     tr("Do majorda C akkordi tonika — тоника, G akkordi dominanta — доминанта. C–G–C misolida uzoqlashish va qaytish tuyg‘usini tinglang.", "В до мажоре C — тоника, G — доминанта. Слушайте ощущение ухода и возвращения в C–G–C.", "In C major, C is tonic and G is dominant. Hear the departure and return in C–G–C."),
     tr("Oxirgi C ni chalishdan oldin uning kelishini ichingizda tasavvur qiling.", "Перед последним C мысленно представьте его разрешение.", "Anticipate the final C chord before it arrives.")),
    ("arpeggio", "harmony", tr("Akkorddan arpejioga", "От аккорда к арпеджио", "From chord to arpeggio"),
     tr("Bir xil C–E–G tovushlarini birga bossak akkord, ketma-ket chalsak arpejio — арпеджио. Jo‘rlikning ko‘p shakllari shu usulda quriladi.", "Одни и те же C–E–G вместе образуют аккорд, последовательно — арпеджио. Так устроены многие фактуры сопровождения.", "The same C–E–G tones form a chord together and an arpeggio in sequence. Many accompaniment textures use this idea."),
     tr("Ketma-ket eshitilayotgan tovushlardan qaysilari avvalgi akkordda bo‘lganini toping.", "Найдите в последовательности звуки предыдущего аккорда.", "Find the original chord tones in the broken pattern.")),
    ("meter", "rhythm", tr("Uchlik guruhlash", "Группировка по три", "Grouping in three"),
     tr("O‘lchov — размер — urishlarni guruhlash. Bu original misol 3/4: har uch urishdan birinchisi tayanch. Bu Still faylining o‘lchovi haqidagi da’vo emas.", "Размер группирует доли. Этот оригинальный пример в 3/4: опора каждые три доли. Это не утверждение о размере файла Still.", "Meter groups beats. This original 3/4 example places a reference every three beats; it does not assert the meter of the Still file."),
     tr("Bir–ikki–uch deb sanang; birinchi urishni kuchli urish emas, yengil tayanch deb his qiling.", "Считайте раз–два–три; первая доля — опора, а не удар.", "Count one–two–three; feel the first beat as support rather than a thump.")),
    ("syncopation", "rhythm", tr("Urish oralig‘ida boshlash", "Синкопа", "Offbeat entries"),
     tr("Sinkopa — синкопа — urg‘uning kutilgan kuchli joydan siljishi. Namunada yuqori tovushlar chap pulsning orasida boshlanadi va keyingi urishgacha cho‘ziladi.", "Синкопа смещает ожидаемый акцент. Верхние звуки начинаются между долями левой и продолжаются через следующую долю.", "Syncopation shifts the expected emphasis. Upper tones begin between LH beats and last across the next beat."),
     tr("Chap bilan 1–2–3–4, o‘ng bilan ularning ‘va’ qismida kiring.", "Слева 1–2–3–4, справа вступайте на ‘и’ между ними.", "Count 1–2–3–4 in the left and enter on the 'and' with the right.")),
    ("legato", "expression", tr("Tovushlarni ulash va ajratish", "Связно и отрывисто", "Connect and separate"),
     tr("Legato — легато — keyingi tovush bosilganda oldingisini bo‘shatish bilan ulash. Stakkato — стаккато — qisqa, ammo tarang bo‘lmagan ajratish.", "Легато связывает отпускание старой клавиши с нажатием новой. Стаккато отделяет коротко, но без напряжения.", "Legato connects the release of one key with the next attack. Staccato separates briefly without tension."),
     tr("Birinchi to‘rt va keyingi to‘rt tovush orasidagi ushlash vaqti farqini kuzating.", "Сравните время удержания первых и следующих четырёх звуков.", "Compare key durations in the first and last four tones.")),
    ("dynamics", "expression", tr("Kuchayish va so‘nish", "Крещендо и диминуэндо", "Crescendo and diminuendo"),
     tr("Kreshchendo — крещендо — asta kuchayish; diminuendo — диминуэндо — asta so‘nish. Tempni o‘zgartirmasdan ovozni shakllantiring.", "Крещендо постепенно усиливает звук, диминуэндо ослабляет. Формируйте громкость без изменения темпа.", "Crescendo gradually grows; diminuendo fades. Shape volume without changing tempo."),
     tr("Bir tovushni takrorlab, o‘rtaga qadar kuchaytiring va keyin yumshating.", "Повторяя один звук, усиливайте к середине и затем смягчайте.", "Repeat one pitch, grow toward the middle, then soften.")),
    ("voicing", "expression", tr("Melodiya va jo‘rlik", "Мелодия и сопровождение", "Melody and accompaniment"),
     tr("Ovoz ajratish — выделение голоса — asosiy melodiyani boshqa tovushlardan ravshanroq chiqarish. Hammasini kuchli chalish bilan melodiya ajralmaydi.", "Выделение голоса делает главную мелодию яснее остальных звуков. Общая громкость не заменяет баланс.", "Voicing makes the principal melody clearer than other notes. Overall loudness cannot replace balance."),
     tr("Yuqori yo‘lni kuylang; keyin chapni shunchalik yumshoq chalingki, melodiya erkin eshitilsin.", "Напойте верхнюю линию и смягчите левую настолько, чтобы мелодия звучала свободно.", "Sing the upper line and soften the LH until the melody speaks freely.")),
    ("pedal", "pedal", tr("Klavish va pedal davomiyligi", "Клавиша и педаль", "Key hold and pedal sustain"),
     tr("Klavishni bo‘shatish tovush tugashi bilan bir xil emas: pedal — педаль — uni davom ettiradi. Yangi uyg‘unlikda eski tovushlarni tozalash kerak.", "Отпускание клавиши не всегда завершает звук: педаль его продолжает. При новой гармонии очищайте старое звучание.", "Releasing a key need not end its sound: the pedal sustains it. Clear the previous harmony when a new one arrives."),
     tr("Namunada qisqa klavish ushlashidan keyin ham tovush davom etishini eshiting.", "Услышьте продолжение звука после короткого удержания клавиш.", "Hear the sound continue after the short key hold.")),
    ("phrasing", "expression", tr("Musiqiy jumla", "Музыкальная фраза", "Musical phrasing"),
     tr("Fraza — фраза — bir fikr kabi eshitiladigan tovushlar yo‘li. Har notaga bir xil aksent berish o‘rniga boshlanish, yo‘nalish va yumshoq yakunni eshiting.", "Фраза звучит как единая мысль. Вместо одинакового акцента на каждой ноте услышите начало, направление и мягкое завершение.", "A phrase sounds like one thought. Hear its opening, direction and gentle ending rather than accenting every note alike."),
     tr("Namunaning ikki to‘rtlik qismini kuylang; ularning orasida yengil nafas oling.", "Пропойте две группы по четыре звука с лёгким дыханием между ними.", "Sing the two four-note groups with a small breath between them.")),
    ("practice", "foundations", tr("Qiyin joyni kichraytirish", "Как выделить трудное место", "Isolate a difficult spot"),
     tr("Parcha mashqi — работа фрагментами. Xatodan oldingi va keyingi tayanchni qo‘shing; faqat xato notani takrorlash kirish-chiqishni o‘rgatmaydi.", "Включайте опору до и после ошибки. Повторение одной ошибочной ноты не учит входу и выходу из фрагмента.", "Include a landmark before and after the problem. Repeating one wrong note alone does not teach the entry and exit."),
     tr("Timeline orqali to‘rt tovushli guruhning boshiga qayting. Qayta ijrodan oldin qo‘lni xotirjam joylashtiring.", "Вернитесь по timeline к началу группы из четырёх звуков. Перед новым проигрыванием спокойно подготовьте руку.", "Seek to the start of one four-note group on the timeline. Reset your hand calmly before playing it again.")),
]


THEORY += EXTRA_THEORY


def theory_items():
    items = [{"id": f"theory:{key}", "kind": "theory", "title": title, "subtitle": task,
             "category": category, "goals": ["understanding"], "level": None, "minutes": 4,
             "intro": task, "explanation": [{"title": title, "text": text}],
             "steps": [{"title": tr("Ko‘ring va eshiting", "Посмотрите и послушайте", "Watch and listen"), "instruction": task},
                       {"title": tr("Pianinoda sinang", "Попробуйте на пианино", "Try at the piano"), "instruction": text}],
             "related_ids": [], "_generator": {"topic": key}} for key, category, title, text, task in THEORY]
    for item in items:
        review = theory_review(item["_generator"]["topic"])
        item["explanation"].extend(review.pop("explanation"))
        item.update(review)
    return items


from .still_lessons import LESSONS, lesson_items


def all_items():
    from .still_journey import journey_items
    from .repertoire_studies import repertoire_items
    from .all_in_lessons import all_in_items
    from .curated_lessons import curated_items
    from .performance_courses import performance_items
    return lesson_items()+exercise_items()+theory_items()+journey_items()+repertoire_items()+all_in_items()+curated_items()+performance_items()
