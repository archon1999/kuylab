"""Matched A/B examples: alter only the musical property being explained."""
from .midi_authoring import midi_bytes


def tr(uz, ru, en):
    return {"uz": uz, "ru": ru, "en": en}


COMPARISONS = {
    "voicing": [
        ("melody", tr("A · Faqat melodiya", "A · Только мелодия", "A · Melody alone"), tr("Yuqori yo‘lni kuylang. Keyin B da shu kuyga tayanch bo‘lgan tovushlarni eshiting.", "Напойте верхнюю линию, затем в B услышьте её опору.", "Sing the upper line, then hear its support in B.")),
        ("accompaniment", tr("B · Faqat jo‘rlik", "B · Только сопровождение", "B · Accompaniment alone"), tr("Melodiyani ichingizda davom ettiring. Asosiy namunada ikkala qatlam birga eshitiladi.", "Продолжайте мелодию мысленно. В основном примере оба слоя вместе.", "Continue the melody internally. The main example combines both layers.")),
    ],
    "meter": [
        ("even", tr("A · Bir xil kuch", "A · Ровная громкость", "A · Even volume"), tr("O‘n ikki teng pulsni eshiting. Aksent bo‘lmasa guruh chegarasi kamroq seziladi.", "Слушайте двенадцать равных долей. Без акцента граница группы менее заметна.", "Hear twelve equal pulses. Without accents, group boundaries are less apparent.")),
        ("accent", tr("B · Har guruhning birinchi urishi", "B · Первая доля каждой группы", "B · First beat of each group"), tr("1–2–3 deb sanang: 1 kuchliroq, 2 va 3 yumshoq. Tezlik va tovush balandligi A bilan bir xil; faqat bosish kuchi o‘zgardi.", "Считайте 1–2–3: 1 сильнее, 2 и 3 мягче. Темп и высота те же; меняется только сила нажатия.", "Count 1–2–3: emphasize 1, soften 2 and 3. Tempo and pitch match A; only velocity changes.")),
    ],
    "legato": [
        ("detached", tr("A · Ajratib", "A · Раздельно", "A · Detached"), tr("Klavishni keyingi tovushdan ancha oldin qo‘yib yuboring. Tovushlar orasidagi bo‘shliqni eshiting; akustik so‘nish sabab mutlaq sukut bo‘lmasligi mumkin.", "Отпускайте клавишу задолго до следующей. Услышьте промежутки; акустическое затухание может продолжаться.", "Release each key well before the next attack. Hear the gaps; the acoustic release may still ring.")),
        ("connected", tr("B · Bog‘lab", "B · Связно", "B · Connected"), tr("Yangi klavish bosilayotganda oldingisini bo‘shating. Nota boshlanishlari A bilan aynan bir xil; faqat ushlash vaqti uzaydi. Bu namunalarda pedal yo‘q.", "Отпускайте предыдущую при нажатии следующей. Начала нот те же; удлинено удержание. В примерах нет педали.", "Release the old key as the next goes down. Attacks match A; only key duration increases. Neither example uses pedal.")),
    ],
    "dynamics": [
        ("flat", tr("A · Tekis dinamika", "A · Ровная динамика", "A · Flat dynamics"), tr("Har tovush bir xil velocity bilan chalinadi. Tempni quloqda saqlang.", "Каждый звук имеет одинаковую velocity. Запомните темп.", "Every tone uses the same velocity. Keep the tempo in mind.")),
        ("shaped", tr("B · Kuchayib, so‘nib", "B · Нарастание и спад", "B · Grow and fade"), tr("A dagi ayni notalar ayni vaqtda boshlanadi. Faqat velocity o‘rtaga qadar ortadi, keyin pasayadi. Kuchayishda shoshilmang, so‘nishda sekinlashmang.", "Те же ноты начинаются в то же время. Velocity растёт к середине и затем падает. Не ускоряйтесь и не замедляйтесь вслед за громкостью.", "The same notes start at the same times. Velocity grows toward the middle, then fades. Do not speed up or slow down with the volume.")),
    ],
    "compound-meter": [
        ("three-beats", tr("A · 3/4: uch katta urish", "A · 3/4: три крупные доли", "A · 3/4: three large beats"), tr("Oltita sakkiztalikni 2+2+2 qilib sanang: BIR-va, IKKI-va, UCH-va. Keyingi namunada ham ayni tovushlar ayni vaqtda boshlanadi.", "Считайте шесть восьмых 2+2+2: РАЗ-и, ДВА-и, ТРИ-и. В следующем примере те же звуки вступают в то же время.", "Count six eighths as 2+2+2: ONE-and, TWO-and, THREE-and. The next example uses the same notes at the same times.")),
        ("two-beats", tr("B · 6/8: ikki katta urish", "B · 6/8: две крупные доли", "B · 6/8: two large beats"), tr("Endi 3+3: BIR-la-li, IKKI-la-li. Tezlikni emas, guruh chegarasini o‘zgartiring. Birinchi katta urish kuchliroq, ikkinchisi yengil tayanch.", "Теперь 3+3: РАЗ-та-та, ДВА-та-та. Меняется группировка, не скорость. Первая крупная доля яснее, вторая — лёгкая опора.", "Now 3+3: ONE-la-li, TWO-la-li. Change grouping rather than speed. The first large beat is stronger, the second a lighter reference.")),
    ],
}


def definitions(topic):
    return [{"id": f"theory:{topic}:{code}", "title": title, "instruction": instruction}
            for code, title, instruction in COMPARISONS.get(topic, [])]


def comparison_midi(topic, code):
    if code not in [entry[0] for entry in COMPARISONS.get(topic, [])]:
        raise ValueError(f"Unknown comparison: {topic}/{code}")
    notes = []
    if topic == "voicing":
        for i, pitch in enumerate([72, 74, 76, 74, 72, 71, 69, 72]):
            if code == "melody": notes.append((i, .9, pitch, "right", 78))
            else: notes.extend((i, .8, p, "left", 38) for p in [48, 55, 60])
    elif topic == "meter":
        notes = [(i, .4, 60, "right", (85 if i % 3 == 0 else 50) if code == "accent" else 65) for i in range(12)]
    elif topic == "legato":
        notes = [(i, .98 if code == "connected" else .2, p, "right", 70) for i, p in enumerate([60, 62, 64, 65, 67, 65, 64, 62])]
    elif topic == "dynamics":
        notes = [(i, .8, 60, "right", 65 if code == "flat" else 35 + round(50 * (1-abs(7.5-i)/7.5))) for i in range(16)]
    elif topic == "compound-meter":
        grouping = 2 if code == "three-beats" else 3
        notes = [(i*.5, .3, 60, "right", 88 if i % 6 == 0 else 72 if i % grouping == 0 else 48) for i in range(12)]
        return midi_bytes(notes, bpm=90, meter=(3,4) if grouping == 2 else (6,8), end_quarters=6)
    else: raise ValueError(topic)
    return midi_bytes(notes, bpm=76, meter=(3, 4) if topic == "meter" else (4, 4), end_quarters=12 if topic == "meter" else 16 if topic == "dynamics" else 8)
