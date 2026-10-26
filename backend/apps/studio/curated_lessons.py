"""Source-matched introductions to the newly selected performances.

Each passage has a listening goal, a concrete example from its actual MIDI and
five independently playable reductions. The complete path ends at the same
source score as the composition player, never a separately invented finale.
"""
from functools import lru_cache

from .curated_repertoire import ENTRY_BY_CODE
from .repertoire import SOURCES, repertoire_source
from .repertoire_courses import tr
from .repertoire_studies import stages, source_window, time_range


LABELS = {
    "melody": tr("Kuy chizig‘ini eshitish", "Услышать мелодическую линию", "Hear the melodic line"),
    "bass": tr("Bass va jo‘rlikni tushunish", "Разобраться в басе и сопровождении", "Understand bass and accompaniment"),
    "coordination": tr("Ikki qatlamni birlashtirish", "Соединить два слоя", "Bring the two layers together"),
}

MEANINGS = {
    "melody": tr(
        "Melodiya — kuylab davom ettirish mumkin bo‘lgan asosiy tovush yo‘li. Jo‘rlik esa shu yo‘lni qo‘llab turadi. Yuqori registrdagi har bir tovushni alohida urg‘ulash kuy jumlasini bo‘lib yuboradi. Avval tayanchlarni eshiting, ularning orasidagi yo‘nalishni ichingizda kuylang. To‘liq yuqori qatlam qaytganda asosiy yo‘lni ichki tovushlardan ajratib tinglang. Qisqa nota keyingisiga o‘tish uchun xizmat qilishi, uzun nota esa jumlaga tayanch berishi mumkin; ularni bir xil davomiylikka keltirmang.",
        "Мелодия — основная линия, которую можно продолжить голосом; сопровождение её поддерживает. Отдельный акцент на каждой верхней ноте дробит фразу. Сначала услышьте опоры и мысленно пропойте направление между ними. Когда вернётся весь верхний слой, отличайте главную линию от внутренних звуков. Короткая нота может вести к следующей, а длинная давать опору: не уравнивайте их длительности.",
        "The melody is the main line you can continue with your voice; accompaniment supports it. Accenting every upper note separately breaks the phrase. First hear the landmarks and sing the direction between them internally. When the complete upper layer returns, distinguish the main line from inner tones. A short note may lead onward while a long note provides a resting point; do not make their durations identical."),
    "bass": tr(
        "Bass — pastki registrdagi tayanch yo‘l. Akkord birga eshitiladigan tovushlar guruhidir; arpejioda shu guruhning tovushlari navbat bilan keladi. Bass har notada almashishi shart emas: uning ustida bir nechta jo‘rlik tovushi yurishi mumkin. Avval pastki tayanchlarni ajrating, keyin ular orasidagi to‘liq harakatni tinglang. Keyingi bassni qidirish uchun oldingi tovushlarni tezlashtirmang. Katta masofada qo‘lni cho‘zib qotirish o‘rniga, oldingi klavishni vaqtida bo‘shatib qo‘lni yangi joyga ko‘chiring.",
        "Бас — опорная линия в нижнем регистре. Аккорд объединяет звучащие вместе тоны; в арпеджио они идут последовательно. Бас не обязан меняться с каждой нотой: над ним может двигаться несколько звуков сопровождения. Сначала выделите нижние опоры, затем послушайте движение между ними. Не ускоряйте предыдущие звуки ради следующего баса. При большом расстоянии вовремя отпускайте клавишу и переносите руку, не удерживая растянутую жёсткую форму.",
        "The bass is the supporting line in the lower register. A chord groups tones sounding together; an arpeggio places those tones in sequence. The bass need not change at every note: several accompaniment tones may move above it. Hear the low landmarks first, then the complete motion between them. Do not rush earlier notes to reach the next bass. For a large move, release the preceding key at its ending and carry the hand to its new position instead of holding a rigid stretch."),
    "coordination": tr(
        "Koordinatsiya ikkala qatlamning har notasini bir paytda boshlash degani emas. Birga keladigan kirishlar tayanch bo‘ladi; ularning orasida qatlamlar o‘z tartibida davom etadi. Bir qo‘l tovushni ushlab turganda ikkinchisi bir necha marta yangi nota boshlashi mumkin. Avval siyrak ikki qatlamni eshiting, keyin jo‘rlikning to‘liq notalarini qaytaring. To‘liq sekin bosqichda notalar soni original bilan teng, faqat vaqt bir xil nisbatda kengaygan. Shuning uchun tezlikni ko‘tarishdan oldin kirishlar tartibi va bo‘shatishlarni saqlang.",
        "Координация не требует начинать каждую ноту обоих слоёв одновременно. Совместные вступления дают опоры, а между ними линии движутся самостоятельно. Пока одна рука держит звук, другая может начать несколько новых нот. Сначала послушайте редкие опоры двух слоёв, затем верните полное сопровождение. В медленном полном этапе нот столько же, сколько в источнике; всё время растянуто в одном отношении. До повышения скорости сохраните порядок вступлений и отпусканий.",
        "Coordination does not mean starting every note of both layers together. Shared attacks provide landmarks while each line moves independently between them. One hand may hold a tone while the other starts several new notes. Hear the sparse two-layer outline first, then restore the complete accompaniment. The slow complete stage contains the source's full note set, with all time scaled equally. Preserve attack order and releases before increasing speed."),
}


def note_name(pitch):
    return ("C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B")[pitch % 12] + str(pitch // 12 - 1)


def audible_example(parsed, start, end, hand):
    events = sorted((event for event in parsed["events"]
                     if event.get("pitch") and event.get("hand") == hand and not event.get("percussion")
                     and start <= event["onset_seconds"] < end),
                    key=lambda event: (event["onset_seconds"], -event["pitch"]["midi"] if hand == "right" else event["pitch"]["midi"]))
    grouped = []
    for event in events:
        if not grouped or event["onset_seconds"] - grouped[-1]["onset_seconds"] > .045:
            grouped.append(event)
    if len(grouped) < 3:
        raise ValueError("Review the lesson window: it needs three audible entries in its selected layer.")
    return grouped[:4]


def example_text(parsed, start, end, mode):
    hand = "left" if mode == "bass" else "right"
    selected = audible_example(parsed, start, end, hand)
    names = " – ".join(note_name(event["pitch"]["midi"]) for event in selected)
    first = selected[0]
    onset, hold = first["onset_seconds"], first["duration_seconds"]
    name = note_name(first["pitch"]["midi"])
    return tr(
        f"Shu oraliqdagi tanlangan tayanchlar: {names}. Avval playerda ularning tartibini eshiting, keyin pauzada klavishlarini toping. Masalan, {name} to‘liq MIDIda {onset:.2f}-soniyada boshlanib {hold:.2f} soniya ushlanadi. Sekin dars shu vaqtlarni bir xil nisbatda cho‘zadi; notaning tugashini keyingi qatlam kirishi bilan adashtirmang. Harf yonidagi raqam oktava registrini bildiradi: C4 va C5 nomi bir xil, klavishi boshqa.",
        f"Выбранные опоры этого отрезка: {names}. Сначала услышьте их порядок в плеере, затем найдите клавиши на паузе. Например, {name} начинается в полном MIDI на {onset:.2f} с и держится {hold:.2f} с. Медленный урок растягивает эти времена одинаково; не путайте отпускание с новым вступлением другого слоя. Цифра после буквы обозначает октаву: C4 и C5 имеют одинаковое имя, но это разные клавиши.",
        f"Selected landmarks in this passage: {names}. Hear their order in the player, then locate their keys while paused. For example, {name} begins at {onset:.2f} s in the complete MIDI and is held for {hold:.2f} s. The slower lesson scales these times equally; do not confuse its release with another layer's next entry. The number after a letter identifies the octave: C4 and C5 share a name but are different keys.")


def midi_titles(source, variants):
    # SMF text has no mandatory Unicode encoding. Keep the file's track title
    # interoperable; the complete localized display title remains in the catalog.
    for stage in variants:
        stage["_generator"]["title"] = source.code + " | " + stage["title"]["en"].replace("·", "-")
    return variants


@lru_cache(maxsize=1)
def curated_items():
    result = []
    for source in SOURCES:
        if source.course_kind != "curated":
            continue
        entry = ENTRY_BY_CODE[source.code]
        _, parsed = repertoire_source(source.code)
        duration = parsed["metadata"]["duration_seconds"]
        for window in entry["lesson_windows"]:
            mode, start, end = window["mode"], window["start"], window["end"]
            key = f"lesson:{source.code}:{mode}"
            variants = midi_titles(source, stages(source, parsed, key, start, end, mode))
            task = tr(
                "Avval namunani bir marta to‘liq tinglang. Keyin birinchi siyrak bosqichdan boshlang: notalar orasidagi vaqtni ichingizda davom ettiring. Alohida qatlam ravon bo‘lgach, ikki qatlamli 60% bosqichga o‘ting. Bir necha tinch urinishdan keyin 80%, so‘ng manba tempini tanlang. Qiyinlashsa oldingi bosqichga qaytish mumkin; keyingi darslar qulflanmaydi.",
                "Сначала один раз прослушайте весь пример. Затем начните с редкого первого этапа, сохраняя внутреннее время между звуками. После плавного отдельного слоя переходите к двум слоям на 60%. После нескольких спокойных попыток выберите 80%, затем темп источника. При трудностях вернитесь назад; следующие уроки не блокируются.",
                "Listen to the complete example once. Begin with the sparse first stage and maintain inner time between notes. Once the separate layer flows, move to both layers at 60%. After several unhurried attempts choose 80%, then source speed. Return to an earlier stage when needed; later lessons remain available.")
            ready = tr(
                "Tanlangan yo‘lni eshitib davom ettira olasiz, tayanchlarda to‘xtamaysiz va yangi qatlam qo‘shilganda puls buzilmaydi. Tezlikdan oldin shu uch belgini tekshiring.",
                "Вы можете продолжить выбранную линию на слух, не останавливаетесь на опорах и сохраняете пульс при добавлении второго слоя. Проверьте эти три признака до увеличения скорости.",
                "You can continue the selected line by ear, move through its landmarks without stops and keep the pulse when the second layer joins. Check these three signs before increasing speed.")
            result.append({
                "id": key, "kind": "lesson", "_composition": source.code,
                "title": LABELS[mode], "subtitle": time_range(start, end), "intro": entry["learning_focus"],
                "category": "expression" if mode == "melody" else "coordination",
                "goals": ["accuracy", "understanding", "musicality"], "level": None, "minutes": 10,
                "explanation": [
                    {"title": tr("Shu asarda nimani eshitamiz?", "Что услышать в этом произведении?", "What to hear in this piece"), "text": entry["learning_focus"]},
                    {"title": LABELS[mode], "text": MEANINGS[mode]},
                    {"title": tr("Aynan shu MIDI misoli", "Пример из этого MIDI", "An example from this MIDI"), "text": example_text(parsed, start, end, mode)},
                    {"title": tr("Mashq tartibi", "Порядок занятий", "Practice method"), "text": task},
                    {"title": tr("Tayyor bo‘lganda", "Когда можно идти дальше", "Ready to move on"), "text": ready},
                ],
                "steps": [{"title": stage["title"], "instruction": stage["instruction"]} for stage in variants],
                "stages": variants, "source": source_window(start, end), "ready_when": ready,
                "related_ids": ["theory:intervals", "theory:voicing", "theory:arpeggio"],
            })
        key = f"journey:{source.code}:complete"
        variants = midi_titles(source, stages(source, parsed, key, 0, duration, "coordination", complete=True))
        result.append({
            "id": key, "kind": "journey", "_composition": source.code,
            "title": tr(source.title + ": boshidan oxirigacha", source.title + ": от начала до конца", source.title + ": from beginning to end"),
            "subtitle": time_range(0, duration), "intro": entry["learning_focus"],
            "category": "coordination", "goals": ["accuracy", "musicality"], "level": None, "minutes": 15,
            "source": source_window(0, duration), "stages": variants,
            "steps": [{"title": stage["title"], "instruction": stage["instruction"]} for stage in variants],
            "related_ids": [f"lesson:{source.code}:{mode}" for mode in LABELS],
            "explanation": [
                {"title": tr("Butun asarni bir yo‘lga yig‘ish", "Собрать произведение в одну линию", "Connect the complete piece"),
                 "text": tr("Alohida darslarda o‘rgangan tayanchlarni butun faylda kuzating. Dastlab siyrak qatlamlar, keyin yuqori yo‘l va bass, so‘ng ikki qatlamning barcha asl notalari keladi. Tezlik 60% va 80% bosqichlardan manba tempiga olib boradi. Oxirgi bosqich kompozitsiya playeridagi aynan o‘sha to‘liq MIDI; qo‘shimcha yakun yoki boshqa aranjirovka qo‘shilmagan.",
                            "Проследите опоры отдельных уроков во всём файле. Сначала идут редкие слои, затем верхняя линия с басом, после — все исходные ноты обоих слоёв. Этапы на 60% и 80% ведут к темпу источника. Последний этап — тот же полный MIDI, что в плеере произведения; другого окончания или аранжировки нет.",
                            "Follow the landmarks from the separate lessons throughout the file. Sparse layers lead to the upper texture over bass, then to every original note of both layers. The 60% and 80% stages lead to source speed. The last stage is the same complete MIDI used by the composition player, with no substituted ending or arrangement.")},
                {"title": tr("Asarning asosiy vazifasi", "Главная задача произведения", "The piece's main task"), "text": entry["learning_focus"]},
            ],
            "ready_when": tr("Butun fayl davomida kuy yo‘li va puls saqlanadi; bir joydagi xato keyingi jumlani ham to‘xtatib qo‘ymaydi.",
                             "Мелодическая линия и пульс сохраняются до конца файла; ошибка в одном месте не останавливает следующую фразу.",
                             "The melodic line and pulse continue to the end; a local mistake does not stop the next phrase."),
        })
    return result
