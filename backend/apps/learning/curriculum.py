"""Authored lessons: metadata links explain relevance; drills are original.

No bar number, melody, or fingering is inferred from an unavailable song score.
The scheduling constants are product choices, not clinical/pedagogical guarantees.
"""
from copy import deepcopy
import hashlib
import json
from urllib.parse import urlencode
from django.apps import apps
from .models import LearningLesson

SKILLS = {
    "rhythm": "Ritm va puls", "reading": "Klavish va registr", "harmony": "Akkord va tonallik",
    "intervals": "Intervallar", "coordination": "Qo'llar muvofiqligi", "practice": "Mustaqil mashq",
}
PIRATE_SOURCE_ID = "MN0224234"
SOURCES = {
    "meter": {"title": "Open Music Theory · Compound meter", "url": "https://viva.pressbooks.pub/openmusictheory/chapter/compound-meters-and-time-signatures/"},
    "minor": {"title": "Open Music Theory · Minor scales", "url": "https://viva.pressbooks.pub/openmusictheory/chapter/minor-scales/"},
    "triads": {"title": "Open Music Theory · Triads", "url": "https://viva.pressbooks.pub/openmusictheory/chapter/triads/"},
    "clefs": {"title": "Open Music Theory · Reading clefs", "url": "https://viva.pressbooks.pub/openmusictheory/chapter/clefs/"},
    "intervals": {"title": "Open Music Theory · Intervals", "url": "https://viva.pressbooks.pub/openmusictheory/chapter/intervals/"},
    "practice": {"title": "UT Austin · Tips for Effective Practice", "url": "https://cml.music.utexas.edu/online-resources/intelligent-music-practice/10-tips-for-effective-practice"},
}


def choices(*labels):
    return [{"id": str(index), "label": label} for index, label in enumerate(labels)]


def question(code, prompt, labels, correct, explanation):
    return {"id": code, "prompt": prompt, "choices": choices(*labels), "correct_choice": str(correct), "explanation": explanation}


DIAGNOSTIC_QUESTIONS = [
    {**question("pulse", "Odatiy 6/8 metrida nechta katta urish bor?", ["6 ta", "2 ta, har biri uchga bo'linadi", "3 ta, har biri ikkiga bo'linadi", "Hali bilmayman"], 1, "6/8 odatda ikkita nuqtali chorak pulsidan iborat; har puls uchta sakkizlik."), "skill": "rhythm", "kind": "knowledge"},
    {**question("dot", "Nuqtali chorak nechta sakkizlik davom etadi?", ["2", "3", "4", "Hali bilmayman"], 1, "Nuqta chorakka uning yarmi — bir sakkizlikni — qo'shadi: 2 + 1 = 3."), "skill": "rhythm", "kind": "knowledge"},
    {**question("minor", "D minor uch tovushli akkordi qaysi?", ["D–F♯–A", "D–F–A", "D–G–A", "Hali bilmayman"], 1, "D dan F gacha kichik tersiya; D dan A gacha sof kvinta."), "skill": "harmony", "kind": "knowledge"},
    {**question("clef", "Sol kalitida pastki chiziqdagi nota qaysi?", ["G", "F", "E", "Hali bilmayman"], 2, "Sol kaliti ikkinchi chiziqni G deb belgilaydi; pastki chiziq E4."), "skill": "reading", "kind": "knowledge"},
    {**question("interval", "D–F oralig'i qaysi interval?", ["Sekunda", "Kichik tersiya", "Sof kvinta", "Hali bilmayman"], 1, "D–E–F uchta harf nomi va uch yarim ton: kichik tersiya."), "skill": "intervals", "kind": "knowledge"},
    {**question("strategy", "Bir o'tishda doim to'xtaysiz. Avval nima qilasiz?", ["Har safar butun asarni boshidan chalaman", "Tempni darhol oshiraman", "O'tishning oldi va keyinini kichik bo'lakda ajratib tekshiraman", "Hali bilmayman"], 2, "Muammo joyini ajratish sababni tekshirish va aniq natijani kuzatishga yordam beradi."), "skill": "practice", "kind": "knowledge"},
    {"id": "coordination", "title": "Qulay sekin tempda ikkala qo'l bilan bir xil kichik mashqni uch marta to'xtamay chala olasizmi?", "skill": "coordination", "kind": "self_report", "choices": choices("Hali sinamaganman", "Hozircha yo'q", "Ba'zan", "Ko'pincha", "Ha, uchala urinishda")},
    {"id": "reading_self", "title": "Yangi, oson notani videodagi klavishlarga qaramay o'qish qanchalik qulay?", "skill": "reading", "kind": "self_report", "choices": choices("Hali sinamaganman", "Juda qiyin", "Sekin, yordam bilan", "Asosan mustaqil", "Qulay va mustaqil")},
    {"id": "rhythm_self", "title": "Chalayotganda ovoz bilan ichki bo'linmalarni sanab, pulsni ushlash qanchalik qulay?", "skill": "rhythm", "kind": "self_report", "choices": choices("Hali sinamaganman", "Juda qiyin", "Ba'zan", "Asosan qulay", "Qulay va barqaror")},
]


def diagnostic_definitions(arrangement=None):
    score = active_score(arrangement) if arrangement is not None else None
    if not score or score.file_format != "midi":
        return DIAGNOSTIC_QUESTIONS
    return [
        {**question("midi-pulse-basis", "Barqaror puls bilan nota soni o'rtasidagi farq nima?", ["Har bir nota albatta bitta puls", "Bitta puls ichida bir nechta nota yoki sukut bo'lishi mumkin", "Puls faqat chap qo'lda bo'ladi", "Hali bilmayman"], 1, "Puls — vaqt tayanchi; nota hujumlari unga nisbatan turli bo'linmalarda boshlanishi mumkin."), "skill": "rhythm", "kind": "knowledge"},
        {**question("midi-held-key", "Pedal bilan tovush cho'zilganda klavish qachon qo'yib yuborilganini bilish mumkinmi?", ["Tovush tugaganida, albatta", "Nota qo'yib yuborilishi va pedal uzaytirgan tovush alohida vaqtlar", "MIDI da nota davomiyligi yo'q", "Hali bilmayman"], 1, "note_off klavish qo'yib yuborilishini, CC64 pedal esa undan keyingi tovush uzayishini ajratadi."), "skill": "rhythm", "kind": "knowledge"},
        {**question("midi-triad-structure", "Minor uch tovushli akkordda asosiy tovushdan qolgan ikki tovushgacha masofa qaysi?", ["4 va 7 yarim ton", "3 va 7 yarim ton", "2 va 5 yarim ton", "Hali bilmayman"], 1, "Minor uch tovushli akkord kichik tersiya (3) va sof kvintadan (7) tuziladi."), "skill": "harmony", "kind": "knowledge"},
        {**question("midi-keyboard", "Ikki qora klavish guruhining darhol chapidagi oq klavish qaysi?", ["G", "D", "C", "Hali bilmayman"], 2, "Ikki qora klavish guruhining chapidagi oq klavish C. Shu tayanch turli registrda takrorlanadi."), "skill": "reading", "kind": "knowledge"},
        {**question("midi-distance", "Ikki klavish MIDI raqamlari 57 va 60 bo'lsa, masofa qancha?", ["2 yarim ton", "3 yarim ton", "7 yarim ton", "Hali bilmayman"], 1, "MIDI raqami bir yarim tonda bittaga o'zgaradi: 60 − 57 = 3."), "skill": "intervals", "kind": "knowledge"},
        *[item for item in DIAGNOSTIC_QUESTIONS if item["id"] in ["strategy", "coordination"]],
        {"id": "midi-reading-self", "title": "Player yordamini kamaytirganda ko'rsatilgan klavish va registrni o'zingiz topish qanchalik qulay?", "skill": "reading", "kind": "self_report", "choices": choices("Hali sinamaganman", "Juda qiyin", "Sekin, yordam bilan", "Asosan mustaqil", "Qulay va mustaqil")},
        next(item for item in DIAGNOSTIC_QUESTIONS if item["id"] == "rhythm_self"),
    ]


def diagnostic_questions(definitions=None):
    # The answer key and explanation are only returned after submission.
    definitions = definitions if definitions is not None else DIAGNOSTIC_QUESTIONS
    return [{"id": item["id"], "skill": item["skill"], "kind": item["kind"],
             "title": item.get("title", item.get("prompt")), "choices": item["choices"]} for item in definitions]


def lesson(code, title, skill, minutes, summary, context, explanation, steps, exercise, success, quiz, sources):
    return {"code": code, "title": title, "skill": skill, "minutes": minutes, "summary": summary,
            "context": context, "success_criterion": success, "kind": "preparation",
            "content": {"explanation": explanation, "steps": steps, "exercise": {"label": "KuyLab original tayyorlov mashqi", "original": True, **exercise},
                        "transfer": "O'zingizdagi aynan tanlangan nota yoki ijroga qayting. Shu tushunchani topgan joyingizni yozing; to'liq nota tekshirilmaguncha sayt takt yoki barmoqlash belgilamaydi.",
                        "sources": [SOURCES[key] for key in sources]}, "quiz": {"questions": quiz}}


PIRATE_LESSONS = [
    lesson("compound-pulse", "6/8: ikkita katta urish", "rhythm", 7,
           "Sanashni oltita alohida zarbdan ikki katta pulsga o'tkazing.",
           "Chrissy Ricker MN0224234 varianti 6/8 metrida. Bu dars uning pulsini tushunishga tayyorlaydi; mashq asarning ritmi emas.",
           [{"title": "3 + 3", "text": "1–2–3 / 4–5–6: oltita sakkizlik teng. Odatiy 6/8 da ular ikkita guruhga yig'iladi. Katta urish uch sakkizlik davom etadi; sanash: BIR-la-li IKKI-la-li."},
            {"title": "Nuqta va temp", "text": "Chorak = ikki sakkizlik. Nuqtali chorak = uch sakkizlik. Mashq uchun nuqtali chorak 50/min tanlasangiz, sakkizlik bo'linma 150/min bo'ladi. Manbaning nuqtali chorak 120/min belgisi mashqni hozir 120 da bajarish talabi emas."}],
           [{"title": "Klavishsiz", "instruction": "BIR-la-li IKKI-la-li ni to'rt marta ayting. Stolga faqat BIR va IKKI paytida yengil uring."},
            {"title": "Bitta nota", "instruction": "D4 ni olti teng sakkizlik bilan chaling; 1 va 4 da yengil urg'u. Qulay tempda to'rt aylana, pedal kerak emas."},
            {"title": "Klikni kamaytiring", "instruction": "Avval har sakkizlikda klik, keyin faqat katta urishda klik. Sanash va teng bo'linish saqlanganini tinglang."}],
           {"notes": ["D4", "D4", "D4", "D4", "D4", "D4"], "counting": ["BIR", "la", "li", "IKKI", "la", "li"], "bpm": 50, "beat_unit": "dotted_quarter", "time_signature": "6/8", "duration_eighths": [1, 1, 1, 1, 1, 1]},
           "Olti teng bo'linmani ikki katta urishga birlashtirib uch marta sanab va chalib bera oldim.",
           [question("group", "6/8 ning odatiy guruhlanishi qaysi?", ["2+2+2", "3+3", "4+2"], 1, "Compound duple meter: ikkita katta urish, har biri uchga bo'linadi."),
            question("tempo", "Katta urish 50/min bo'lsa, sakkizliklar soni minutiga qancha?", ["50", "100", "150"], 2, "Har katta urishda uch sakkizlik: 50 × 3 = 150.")], ["meter"]),
    lesson("d-minor-map", "D minor: tovushdan akkordga", "harmony", 7,
           "Qo'lingiz bilgan shaklni tovush nomi va akkord bilan bog'lang.",
           "Tanlangan nashr D minor deb ko'rsatilgan. Bu original mashq tonallikni tushunishga xizmat qiladi; nashrning akkordlar ketma-ketligi hali tahlil qilinmagan.",
           [{"title": "Tabiiy minor", "text": "D tabiiy minor: D–E–F–G–A–B♭–C–D. B♭ B dan yarim ton past. Tonallikdagi bitta bemol barcha notalar aynan shu gamma bilan cheklanishini anglatmaydi."},
            {"title": "Uch tovush", "text": "D–F–A: asosiy tovush, kichik tersiya, sof kvinta. D–F♯–A esa D major; bittagina tovush almashishi akkord sifatini o'zgartiradi. F–A–D ham D minor tovushlari, ammo pastda F bo'lgani uchun birinchi aylanish."},
            {"title": "C va C♯", "text": "D tabiiy minor gammasida C bor. D garmonik minor gammasida yettinchi pog'ona C♯ ga ko'tariladi. Bu farqni eshitish mumkin, ammo C♯ aynan asarning qayerida kelishini to'liq notasiz aytmaymiz."}],
           [{"title": "Toping va ayting", "instruction": "D4, F4, A4 ni alohida toping va nomini ayting. Keyin qulay qo'l holatida birga yoki navbat bilan chaling."},
            {"title": "Taqqoslang", "instruction": "D–F–A va D–F♯–A ni sekin eshiting. O'zgaradigan yagona tovushni ayting; minor va major nomini tovush bilan bog'lang."},
            {"title": "Aylanish", "instruction": "D4–F4–A4 dan F4–A4–D5 ga o'ting. Qo'lga noqulay bo'lsa notalarni navbat bilan chaling. Uch tovush nomi o'zgarmaganini tekshiring."}],
           {"notes": ["D4", "F4", "A4", "F4", "A4", "D5"], "bpm": 50, "beat_unit": "quarter", "chords": [["D4", "F4", "A4"], ["F4", "A4", "D5"]]},
           "D minor tovushlarini nomsiz yordamga qaramay topdim, major bilan farqini va birinchi aylanishni uch marta tushuntirib/chalib berdim.",
           [question("triad", "D minor tarkibi qaysi?", ["D–F–A", "D–F♯–A", "D–G–B"], 0, "D–F kichik tersiya va D–A sof kvinta minor uch tovushli akkordni hosil qiladi."),
            question("scale", "D tabiiy minor tarkibidagi tovush qaysi?", ["B", "B♭", "F♯"], 1, "D tabiiy minorning oltinchi pog'onasi B♭."),
            question("inversion", "F–A–D qanday akkord?", ["F major", "D minor, birinchi aylanish", "Yangi tonallik"], 1, "Tovushlar D–F–A o'shaligicha, lekin pastda tersiya F turibdi.")], ["minor", "triads"]),
    lesson("interval-navigation", "Interval bilan yo'l topish", "intervals", 6,
           "Har notani yodlash o'rniga tovushlar orasidagi masofani ko'ring.",
           "D minor tayyorlovidagi D–F–A shakli intervalni eshitish va topish uchun qulay. Aynan nashrdagi sakrash yoki fingering haqida taxmin qilinmaydi.",
           [{"title": "Harf va yarim ton", "text": "Interval o'lchamida boshlang'ich va oxirgi harf ham sanaladi: D–E–F = tersiya. D dan F gacha uch yarim ton bo'lgani uchun kichik tersiya. D dan A gacha besh harf va yetti yarim ton — sof kvinta."},
            {"title": "Masofa va yo'nalish", "text": "D–F–A–F–D da yuqoriga va pastga yo'nalishni ayting. Klavishdagi masofani ko'rish bilan eshitilgan masofani bog'lang; faqat barmoq raqamiga suyanmang."}],
           [{"title": "Masofani ayting", "instruction": "D4–F4, D4–A4 juftlarini chaling. Har safar interval nomini ayting. Ko'zni yumish yoki katta masofaga cho'zish shart emas."},
            {"title": "Yo'nalish", "instruction": "D4–F4–A4–F4–D4 ni sekin chaling. Har keyingi tovushdan oldin yuqori/past va intervalni ayting."},
            {"title": "Boshqa registr", "instruction": "Xuddi shu ketma-ketlikni D3 dan toping. Nota nomlari bir xil, registr boshqa ekanini eshiting."}],
           {"notes": ["D4", "F4", "A4", "F4", "D4"], "bpm": 50, "beat_unit": "quarter"},
           "D–F va D–A ni nomlay oldim; ketma-ketlikni ikki registrda uch marta mustaqil topdim.",
           [question("third", "D–F qanday interval?", ["Katta tersiya", "Kichik tersiya", "Sof kvarta"], 1, "Uch harf nomi, uch yarim ton — kichik tersiya."),
            question("fifth", "D–A intervali nechta yarim ton?", ["5", "7", "9"], 1, "Sof kvinta yetti yarim ton; harf bo'yicha D–E–F–G–A.")], ["intervals"]),
    lesson("staff-landmarks", "Klavishdan nota chizig'iga", "reading", 7,
           "Yoddagi tovushlarni ikki kalitdagi tayanchlar bilan bog'lang.",
           "Pianino solo nashri bilan ishlash uchun ikki kalitni o'qish foydali. Quyidagi D minor notalari original misol; asarning notasi emas.",
           [{"title": "Ikki tayanch", "text": "Sol kalitining ikkinchi chizig'i G4; uning pastki chizig'i E4. Fa kalitining yuqoridan ikkinchi (pastdan to'rtinchi) chizig'i F3. O'rta C — C4 — ikki sistemaning orasidagi qo'shimcha chiziqda yoziladi."},
            {"title": "Yonma-yon o'qish", "text": "Chiziqdan keyingi bo'shliq yoki bo'shliqdan keyingi chiziq — harf nomida bir pog'ona. Chiziqdan keyingi chiziq — bir harfni tashlab o'tish. Oktava raqami registrni ajratadi: D3 va D4 bir nom, boshqa balandlik."}],
           [{"title": "Tayanch", "instruction": "Pianinoda C4 va G4 ni toping. Sol kalitidagi G4 tayanchidan D4–F4–A4 original misolini qog'ozga joylashtiring yoki nota ko'rsatgich bilan tekshiring."},
            {"title": "Bas", "instruction": "Fa kalitidagi F3 dan D3 va A3 ga harf pog'onalarini sanang. D3–F3–A3 ni klavishda toping."},
            {"title": "Yordamni kamaytirish", "instruction": "D4–F4–A4 va D3–F3–A3 ni navbat bilan o'qing. Avval nomlab keyin chaling; uch urinishda tayanchni o'zingiz toping."}],
           {"notes": ["D4", "F4", "A4", "D3", "F3", "A3"], "bpm": 40, "beat_unit": "quarter", "notation": "original_landmarks"},
           "Sol va fa kaliti tayanchini nomladim; original uch tovushni ikki registrda mustaqil o'qib uch marta topdim.",
           [question("treble", "Sol kalitida ikkinchi chiziq qaysi nota?", ["E4", "G4", "F3"], 1, "Sol (G) kaliti ikkinchi chiziqni G4 deb belgilaydi."),
            question("bass", "Fa kalitidagi pastdan to'rtinchi chiziq qaysi?", ["F3", "C4", "G4"], 0, "Fa (F) kalitining ikki nuqtasi F3 chizig'ini o'rab turadi.")], ["clefs"]),
    lesson("hands-meeting", "Ikki qo'l: uchrashuv nuqtalari", "coordination", 8,
           "Qo'llar qayerda birga va qayerda alohida tushishini tushuning.",
           "6/8 tayyorlovida ikki katta urish qo'llarning uchrashuvini rejalash uchun ishlatiladi. Bu tanlangan nashrning chap yoki o'ng qo'l partiyasi emas.",
           [{"title": "Bir vaqt xaritasi", "text": "Original mashqda chap qo'l D3 ni 1 va 4 da bosadi; o'ng qo'l D4–F4–A4 / D4–F4–A4 ni oltita teng sakkizlikda chaladi. Ikkala qo'l 1 va 4 da birga boshlaydi. Avval shu uchrashuvlarni tushuning."},
            {"title": "Kichik vazifa", "text": "Bir qo'l qulay, birga esa qiyin bo'lsa, faqat 1–2–3 ni oling. Muammo koordinatsiya bo'lishi mumkin; bu avtomatik jismoniy tashxis emas. Qo'l erkinligini tekshiring, noqulaylik bo'lsa tanaffus qiling."}],
           [{"title": "Stolda", "instruction": "O'ng qo'l bilan olti teng urish, chap qo'l bilan faqat 1 va 4. To'rt aylana ovoz bilan sanang."},
            {"title": "Uch tovush", "instruction": "O'ng qo'l D4–F4–A4 ni qulay tempda chalsin. Chap qo'l D3 ni guruh boshida chalib, uch sakkizlik davomida ushlab tursin."},
            {"title": "Ulang", "instruction": "Ikkita guruhni birlashtiring. Uchta ravon urinishda faqat tovush/puls va qulaylikni tekshiring. Tezlikni oshirish shart emas."}],
           {"notes": ["D4", "F4", "A4", "D4", "F4", "A4"], "left_hand": [{"note": "D3", "start_eighth": 0, "duration_eighths": 3}, {"note": "D3", "start_eighth": 3, "duration_eighths": 3}], "duration_eighths": [1, 1, 1, 1, 1, 1], "counting": ["BIR", "la", "li", "IKKI", "la", "li"], "bpm": 40, "beat_unit": "dotted_quarter", "time_signature": "6/8"},
           "Ikki qo'lni 1 va 4 da birga tushirib, olti bo'linmani qulay tempda uch marta to'xtamay chaldim.",
           [question("meeting", "Original mashqda ikkala qo'l qayerda birga boshlaydi?", ["1 va 4", "2 va 5", "Har sakkizlikda"], 0, "Chap qo'l guruh boshida: 1 va 4. O'ng qo'l har sakkizlikda."),
            question("next", "Birga chalish buzilsa, qanday tekshirasiz?", ["Darhol tezlashtiraman", "Faqat 1–2–3 guruhini sekin tekshiraman", "Butun asarni boshidan takrorlayman"], 1, "Kichik guruh vaqt va harakatning aynan qayerda buzilishini aniqlashga yordam beradi.")], ["meter", "practice"]),
    lesson("repair-and-recall", "Xatoni tuzatish va ertaga tekshirish", "practice", 6,
           "Mashq natijasini vaqt bilan emas, aniq o'zgarish bilan yozing.",
           "Siz asarni chala olasiz, lekin barqarorlikni oshirmoqchisiz. Shu dars tanish He’s a Pirate ijroingizdagi bitta to'xtashni kuzatishga yordam beradi; tizim notalarni bilmagani uchun xatoni siz belgilaysiz.",
           [{"title": "Aniq savol", "text": "'Yaxshiroq chalish' o'rniga kuzatiladigan bitta maqsad: masalan, 'belgilagan o'tishimda to'xtamaslik'. Xato tovushmi, pulsmi, qo'llar uchrashuvimi yoki boshlash joyini eslay olmaslikmi — bittasini tanlang."},
            {"title": "Kontekst", "text": "Qiyin nuqtaning oldidan boshlang, undan keyingacha ulang. Qulay tempda to'g'ri chiqqan kichik bo'lakni boshqa tanish bo'lak bilan almashib qayta tekshiring. Ertasi kuni tayyorlovsiz birinchi urinishni qayd eting."},
            {"title": "Dalil", "text": "Savolga javob — nazariy dalil. 'Uch marta ravon chaldim' — sizning amaliy kuzatuvingiz. Keyingi kuni saqlanish — boshqa dalil. Sayt bularni bir xil 'perfect' foizga aylantirmaydi."}],
           [{"title": "Boshlang'ich urinish", "instruction": "O'zingiz biladigan tanlangan ijroda bitta qisqa qiyin joyni sinang. Joyni o'z so'zingiz bilan yozing; takt raqamini faqat o'zingizdagi nota bilan bilsangiz kiriting."},
            {"title": "Tuzatish", "instruction": "Faqat bitta sababni tekshiring. Qulay temp, oldi-keyini ulangan kichik bo'lak va uchta barqaror urinish. Bu mezon mahsulot sozlamasi, natija kafolati emas."},
            {"title": "Qayta chaqirish", "instruction": "Bugun nima o'zgarganini va ertaga birinchi urinishda nimani tekshirishingizni yozing. Keyingi darsda avval shu yozuvsiz urinib ko'ring."}],
           {"notes": ["D4", "F4", "A4", "D5", "A4", "F4", "E4", "D4"], "mode": "original_recall_fragment", "bpm": 50, "beat_unit": "quarter", "original": True, "label": "KuyLab original qayta chaqirish mashqi; so'ng siz tanlagan asar joyiga qayting"},
           "Bitta xato sababini, qulay tempni va uchta urinish natijasini yozdim; keyingi tekshiruv uchun aniq maqsad belgiladim.",
           [question("evidence", "Nazariya quizidan 100% olish nimani isbotlaydi?", ["Asarni perfect chalishni", "Shu savollarga to'g'ri javob berganimni", "Barmoqlashim avtomatik to'g'riligini"], 1, "Quiz tushunchaga dalil; amaliy ijro va saqlanish alohida tekshiriladi."),
            question("reflection", "Qaysi qayd foydaliroq?", ["Bugun yaxshi", "30 daqiqa chaldim", "Tanlagan o'tishim 60 katta urish/min da uch urinishning ikkitasida to'xtamadi; ertaga shu joyni tekshiraman"], 2, "Aniq joy, urish birligi, natija va keyingi maqsad keyingi mashqni tanlashga yordam beradi.")], ["practice"]),
]

SOURCE_LESSON = {
    "code": "choose-exact-version", "title": "Aynan qaysi ijroni o'rganamiz?", "skill": "practice", "minutes": 5,
    "summary": "Trek va aranjirovkani belgilang; keyin nota asosida dars bog'lanadi.",
    "context": "Asar/to'plam nomining o'zi tonallik, ritm, murakkablik yoki barmoqlashni aniqlamaydi.",
    "success_criterion": "Aniq trek/ijro manbasi va men yaxshilamoqchi bo'lgan bitta joy qayd etildi.", "kind": "source",
    "content": {"explanation": [{"title": "Variant", "text": "Bir xil asarning pianino aranjirovkalari turlicha. OST bo'lsa avval trek nomini, keyin aynan yoqqan ijroni tanlang. Havola to'liq nota yoki huquqni tasdiqlamaydi."}],
                "steps": [{"title": "Tanlang", "instruction": "Bitta trek va yoqqan bitta ijro/nota havolasini kompozitsiya manbasiga yozing."},
                          {"title": "Kuzating", "instruction": "Ijroda sizni qiziqtirgan yoki to'xtatgan bitta joyni o'z so'zingiz bilan yozing. Tasdiqlanmagan takt yoki tonallikni aniq deb belgilamang."}],
                "exercise": {"label": "Manba va maqsadni tanlash", "original": False, "notes": []},
                "transfer": "To'liq nota kelgach shu variantga nazariya va qo'l mashqi bog'lanadi.", "sources": []},
    "quiz": {"questions": []},
}


def supports_pirate_preparation(arrangement):
    return (PIRATE_SOURCE_ID in arrangement.source_url or arrangement.seed_key == "hes-a-pirate-unpianiste-full" and arrangement.full_score_verified_at) and arrangement.key_signature == "D minor" and arrangement.time_signature == "6/8"


def pdf_definitions(arrangement):
    definitions = deepcopy(PIRATE_LESSONS)
    pdf_url = f"/api/arrangements/{arrangement.id}/full-score/"
    practical = lesson("pdf-full-piece", "To'liq asar: to'rt sahifada mashq", "practice", 12,
                       "103 taktli aranjirovkaning aniq joylariga nazariya va qo'l mashqini bog'lang.",
                       "Alexis Quoniamning to'liq 4 sahifali pianino notasi: 1–103 takt, D minor, 6/8. Manbada temp belgisi yozilmagan; mashq tempi qulaylikka qarab tanlanadi.",
                       [{"title": "Puls", "text": "1-sahifa, 18–23 taktlar: chap qo'ldagi D minor bas tayanchida ikki katta urishni sanang. Har biri uchta sakkizlikka bo'linadi. Bitta kichik guruhni o'qib, keyin oldi va keyiniga ulang."},
                        {"title": "A → Dm", "text": "2-sahifa, 38–40 taktlar: 38–39 dagi A akkordi/C♯ va 40-taktda Dm ga qaytishni ko'ring. D tabiiy minorda C bor; C♯ yettinchi pog'onani ko'tarib D ga tortilishni kuchaytiradi. Akkord belgisi va haqiqiy notalarni birga tekshiring."},
                        {"title": "Chap qo'l va yakun", "text": "3-sahifa, 72–83 taktlar: uzluksiz chap qo'l sakkizliklarini bir guruhdan ajrating. 4-sahifa, 97–103 taktlar: yakunni oldingi o'tish bilan ulang; final Dm va yakuniy chiziqqacha to'liq nota mavjud."}],
                       [{"title": "1-sahifa · 18–23", "instruction": "PDFda 18–23 taktlarni toping. Ikki katta urishni ovoz bilan sanang; avval basni, keyin ikkala qo'lni qulay sekin tempda tekshiring.", "pdf_page": 1, "bar_start": 18, "bar_end": 23},
                        {"title": "2-sahifa · 38–40", "instruction": "38–39 dagi A akkordi/C♯ va 40-taktdagi Dm qaytishini topib chaling. Ikki akkordni alohida tinglang, so'ng qo'shni taktlar bilan ulang.", "pdf_page": 2, "bar_start": 38, "bar_end": 40},
                        {"title": "3-sahifa · 72–83", "instruction": "Chap qo'l sakkizliklaridan bitta kichik guruhni tanlang. Chap qo'lni alohida, keyin o'ng bilan birga chaling; puls saqlanishini tinglang.", "pdf_page": 3, "bar_start": 72, "bar_end": 83},
                        {"title": "4-sahifa · 97–103", "instruction": "Yakuniy bo'lakni oldingi takt bilan ulang. Uchta qulay urinishni yozing va keyingi kuni birinchi urinishda qayta tekshiring.", "pdf_page": 4, "bar_start": 97, "bar_end": 103}],
                       {"original": False, "type": "pdf_source_excerpt", "label": "To'liq 4 sahifali kompozitsiya notasi", "pdf_url": pdf_url, "pdf_page": 1, "bar_start": 18, "bar_end": 23, "bpm": 40, "beat_unit": "dotted_quarter", "tempo_choice": {"bpm": 40, "beat_unit": "dotted_quarter"}},
                       "Tanlagan PDF bo'lagini qulay tempda uch marta ravon chaldim; aniq joy va keyingi maqsadni yozdim.",
                       [question("pdf-pulse", "Shu nashrning 6/8 metrida odatda nechta katta urish?", ["6", "2", "3"], 1, "Ikkita nuqtali chorak; har biri uch sakkizlikka bo'linadi."),
                        question("pdf-leading-tone", "38–40 taktlardagi A → Dm bilan bog'liq ko'tarilgan tovush qaysi?", ["C♯", "C", "B♭"], 0, "38–39 taktlardagi A akkordi C♯ bilan yozilgan; 40-taktda Dm ga qaytadi. D minorning ko'tarilgan yettinchi pog'onasi C♯.")], [])
    practical["kind"] = "source_excerpt"
    practical["content"]["sources"] = [{"title": "Alexis Quoniam · to'liq pianino notasi", "url": arrangement.full_score_url}, {"title": "Unpianiste · CC BY-NC-SA 3.0 France", "url": "https://unpianiste.com/informations-legales"}]
    query = {"page": "practice", "composition": arrangement.composition_id, "pdf": arrangement.id, "pdf_page": 1, "bar_start": 18, "bar_end": 23, "bpm": 40, "beat_unit": "dotted_quarter"}
    practical["content"]["practice_link"] = "/?" + urlencode(query)
    practical["content"]["exercise"]["practice_link"] = practical["content"]["practice_link"]
    practical["content"]["transfer"] = "To'liq PDFdagi tanlagan joyingizga qayting; sahifa va taktni yozib, uchta qulay urinishni tekshiring."
    for definition in definitions:
        definition["context"] = f"Alexis Quoniamning to'liq 4 sahifali D minor / 6/8 aranjirovkasiga original tayyorlov. Mashqdan so'ng PDFdagi haqiqiy notaga qayting."
        definition["content"]["transfer"] = "To'liq PDFdagi 1-sahifa, 18–23 taktga qayting; darsdagi fikrni notada topib, qulay tempda qo'llang."
        definition["content"]["practice_link"] = "/?" + urlencode(query)
        if definition["code"] == "compound-pulse":
            definition["content"]["explanation"][1]["text"] = "Chorak = ikki sakkizlik; nuqtali chorak = uch sakkizlik. Original mashqda nuqtali chorak 50/min bo'lsa, sakkizlik 150/min. To'liq nashrda temp belgisi yo'q; mashq tezligi sizga qulay tanlanadi."
        if definition["code"] == "d-minor-map":
            definition["content"]["explanation"][2]["text"] = "D tabiiy minor gammasida C bor. D garmonik minor gammasida yettinchi pog'ona C♯ ga ko'tariladi. To'liq PDFning 2-sahifasida, 38–39 taktlardagi A akkordi/C♯ va 40-taktda Dm qaytishini tekshiring."
    return [practical, *definitions]


def active_score(arrangement):
    try:
        Score = apps.get_model("scores", "Score")
    except LookupError:
        return None
    return Score.objects.filter(arrangement=arrangement).order_by("-created_at", "-id").first()


def score_binding(arrangement, score=None):
    score = score or active_score(arrangement)
    if score is None:
        return None
    section = (score.sections or [None])[0]
    measures = score.parsed.get("measures", [])
    focus = measures[section["start_index"]] if section and 0 <= section["start_index"] < len(measures) else None
    metadata = score.parsed.get("metadata", {})
    return {"score_id": score.id, "version": score.version, "title": score.title,
            "exact_version_confirmed": score.exact_version_confirmed,
            "metadata": metadata, "focus_section": section,
            "focus_key": (focus.get("key") or metadata.get("key")) if focus else metadata.get("key"),
            "focus_time": (focus.get("time") or metadata.get("time")) if focus else metadata.get("time"),
            "measure_count": metadata.get("measure_count", len(measures))}


def pitch_name(letter, accidental):
    return letter + ("♭" * -accidental if accidental < 0 else "♯" * accidental)


def tonal_material(key):
    """Use explicit MusicXML key mode; fifths alone cannot prove tonality."""
    if not key or key.get("mode") not in ["major", "minor"] or not isinstance(key.get("fifths"), int) or not -7 <= key["fifths"] <= 7:
        return None
    major = ["C♭", "G♭", "D♭", "A♭", "E♭", "B♭", "F", "C", "G", "D", "A", "E", "B", "F♯", "C♯"]
    minor = ["A♭", "E♭", "B♭", "F", "C", "G", "D", "A", "E", "B", "F♯", "C♯", "G♯", "D♯", "A♯"]
    tonic = (major if key["mode"] == "major" else minor)[key["fifths"] + 7]
    accidental_by_letter = {letter: 0 for letter in "CDEFGAB"}
    order = "FCGDAEB" if key["fifths"] >= 0 else "BEADGCF"
    for letter in order[:abs(key["fifths"])]:
        accidental_by_letter[letter] = 1 if key["fifths"] > 0 else -1
    letters = "CDEFGAB"
    start = letters.index(tonic[0])
    sequence = [letters[(start + offset) % 7] for offset in range(7)]
    scale = [pitch_name(letter, accidental_by_letter[letter]) for letter in sequence]
    notes = []
    octave = 4
    for index, name in enumerate(scale + [tonic]):
        if index and name[0] == "C":
            octave += 1
        notes.append(name + str(octave))
    return {"tonic": tonic, "mode": key["mode"], "scale": scale + [tonic], "notes": notes,
            "triad": [scale[index] for index in [0, 2, 4]], "triad_notes": [notes[index] for index in [0, 2, 4]]}


def imported_definitions(arrangement, score):
    binding = score_binding(arrangement, score)
    section = binding["focus_section"]
    context = f"Import qilingan «{score.title}», {score.version}-versiya. "
    if section:
        context += f"Siz belgilagan «{section['title']}» qismi boshlanishidagi metadata asosida. "
    else:
        context += "Notaning boshlanish metadata belgilariga tayyorlov. "
    context += "Original mashq qo'shiq notalaridan ajratilgan; texnik qiyinchilik yoki barmoqlash avtomatik taxmin qilinmaydi."
    if not score.exact_version_confirmed:
        context += " Bu fayl yoqqan aynan ijroga mosligi hali siz tomonidan tasdiqlanmagan."
    definitions = []
    # Factual source events make the actual composition the first teaching task.
    # This is a passage observation, not an inferred fingering/difficulty grade.
    from apps.scores.analysis import analyze_passage
    start_index = section["start_index"] if section else 0
    end_index = section["end_index"] if section else min(1, len(score.parsed.get("measures", [])) - 1)
    analysis = analyze_passage(score.parsed, start_index=start_index, end_index=end_index, hand_overrides=score.hand_overrides, tempo_bpm=40, beat_unit="quarter")
    facts = analysis["facts"]
    measure_numbers = analysis["range"]["measure_numbers"]
    count = facts["pitched_note_count"]
    rests = facts["rest_count"]
    short_names = facts.get("short_pitch_names") or []
    passage_name = section["title"] if section else "Boshlanishdagi nota parchasi"
    source_context = f"Import qilingan «{score.title}», {score.version}-versiya: {', '.join(str(number) for number in measure_numbers)} raqamli o'lchovlardagi haqiqiy nota parchasi. "
    if section:
        source_context += f"Siz belgilagan «{section['title']}» oraliq. "
    source_context += "Nota kuzatuvlari shu importdan; barmoqlash va ijro mahorati alohida tekshiriladi."
    if not score.exact_version_confirmed:
        source_context += " Bu fayl yoqqan aynan ijroga mosligi hali siz tomonidan tasdiqlanmagan."
    explanations = [{"title": "Notadagi naqsh", "text": f"{', '.join(str(number) for number in measure_numbers)} raqamli o'lchovlar: {count} ta nota yozuvi, {rests} ta pauza, {facts['chord_group_count']} ta akkord guruhi, {facts['tie_count']} ta bog'langan nota yozuvi."}]
    if short_names:
        explanations.append({"title": "Ko'rib, so'ng chaling", "text": "Dastlabki tovushlar: " + ", ".join(short_names) + ". Ritm va pauzani sanang, keyin qo'llar joylashuvini tekshiring."})
    for caution in analysis.get("cautions", []):
        explanations.append({"title": "Dalil chegarasi", "text": caution})
    source_questions = [question("source-rests", "Shu import parchasida nechta yozilgan pauza hodisasi bor?", [str(rests + 1), str(rests), str(rests + 2)], 1, f"MusicXML hodisalarida {rests} ta rest belgisi bor; ikki qo'lda bir vaqtga to'g'ri kelishi ham mumkin."),
                        question("source-claim", "Bu parcha tahlili nimani aniqlaydi?", ["Yozilgan nota hodisalari va siz belgilagan oraliqni", "Sizning barmoqlashingiz to'g'riligini", "Asarni perfect chalishingizni"], 0, "Tahlil import faylining yozilgan hodisalari haqida; texnika va ijro sifati alohida tekshiriladi.")]
    definitions.append(lesson("source-passage", passage_name, "practice", 10,
                              "Siz tanlagan kompozitsiya parchasini uning haqiqiy notasi bilan o'rganing.", source_context,
                              explanations, [{"title": step["title"], "instruction": step["instruction"], "kind": step["kind"], "basis": step.get("basis"), "range": step.get("range"), "hand": step.get("hand"), "tempo": step.get("tempo")} for step in analysis["steps"]],
                              {"original": False, "label": "Siz import qilgan kompozitsiyaning haqiqiy parchasi", "type": "source_excerpt", "score_id": score.id, "score_url": f"/api/scores/{score.id}/", "musicxml_url": f"/api/scores/{score.id}/musicxml/", "start_index": start_index, "end_index": end_index, "bpm": 40, "beat_unit": "quarter", "tempo_choice": {"bpm": 40, "beat_unit": "quarter"}},
                              "Parchani qulay tempda uch marta to'xtamay chaldim; qiyin joy va keyingi maqsadni yozdim.", source_questions, ["practice"]))
    definitions[0]["kind"] = "source_excerpt"
    definitions[0]["content"]["source_analysis"] = analysis
    time = binding["focus_time"] or {}
    try:
        beats = int(time.get("beats", "0"))
        denominator = int(time.get("beat_type", 0))
    except (ValueError, TypeError):
        beats, denominator = 0, 0
    if denominator == 8 and beats in [6, 9, 12]:
        definition = deepcopy(PIRATE_LESSONS[0])
        pulse = beats // 3
        definition["title"] = f"{beats}/8: {pulse} ta katta urish"
        definition["summary"] = f"Har katta urishni uch teng sakkizlikka bo'ling; original {beats}/8 mashqi."
        definition["content"]["explanation"] = [{"title": f"{pulse} × 3", "text": f"Import o'lchovi {beats}/8. Odatiy compound talqinda {pulse} ta nuqtali chorak puls bor; har biri uch sakkizlik. Bu asosiy sanash; aksent va guruhlashni aniq notadan tekshiring."}, {"title": "Temp birligi", "text": "Original mashqda nuqtali chorak 50/min; sakkizlik klik 150/min. Nashrdagi temp belgisi bundan mustaqil, uni bir xil BPM deb almashtirmang."}]
        counting = [word for index in range(pulse) for word in [str(index + 1), "la", "li"]]
        definition["content"]["exercise"] = {"label": "KuyLab original compound metr mashqi", "original": True, "notes": ["C4"] * beats, "counting": counting, "duration_eighths": [1] * beats, "bpm": 50, "beat_unit": "dotted_quarter", "time_signature": f"{beats}/8"}
        definition["content"]["steps"] = [{"title": "Sanang", "instruction": " / ".join("-".join(counting[index:index+3]) for index in range(0, beats, 3)) + " deb ovoz bilan sanang; katta urish boshida yengil qarsak."}, {"title": "Chaling", "instruction": "C4 da har sakkizlikni teng chaling. Har uchlik boshiga yengil urg'u. Qulay tempda uchta ravon takror."}]
        definition["quiz"]["questions"] = [question("group", f"Odatiy {beats}/8 metrida nechta katta urish?", [str(pulse), str(beats), "1"], 0, f"{beats} sakkizlik uchlikka yig'iladi: {pulse} ta katta urish."), PIRATE_LESSONS[0]["quiz"]["questions"][1]]
        definitions.append(definition)
    elif beats in [2, 3, 4] and denominator in [2, 4, 8]:
        definition = lesson("simple-pulse", f"{beats}/{denominator}: puls va bo'linma", "rhythm", 6,
                            "Import metrini aniq urish birligi bilan sanang.", context,
                            [{"title": "Oddiy bo'linish", "text": f"Boshlang'ich talqinda {beats}/{denominator} metrida {beats} ta {denominator}lik urish bor. Har urishni ikkiga bo'lib sanash mumkin. Bu {beats}/8 bo'lsa ham odatda compound 6/8 kabi uchga bo'linmaydi."}, {"title": "Nuqta", "text": "Nuqta nota davomiyligining yarmini qo'shadi. Chorak ikki sakkizlik, nuqtali chorak uch sakkizlik. Tempda qaysi nota birligi ko'rsatilganiga qarang."}],
                            [{"title": "Sanang", "instruction": f"1 dan {beats} gacha pulsni ayting. Har urish orasiga 'va' qo'shing: 1-va, 2-va ..."}, {"title": "Chaling", "instruction": "C4 da pulsni, keyin ikkiga bo'linmalarni chaling. Klikga qaytishda vaqt bir xil qolganini tinglang."}],
                            {"notes": ["C4"] * (beats * 2), "counting": [value for index in range(beats) for value in [str(index + 1), "va"]], "duration_eighths": [4 / denominator] * (beats * 2), "bpm": 50, "beat_unit": {2: "half", 4: "quarter", 8: "eighth"}[denominator], "time_signature": f"{beats}/{denominator}"},
                            "Import metrini ovoz bilan sanadim; original mashqni pulsni o'zgartirmay uch marta chaldim.",
                            [question("beats", f"Boshlang'ich talqinda {beats}/{denominator} bir o'lchovida nechta {denominator}lik urish bor?", [str(beats), "6", "8"], 0, "Yuqoridagi son ko'rsatilgan nota birliklari sonini bildiradi."), question("dot", "Nuqtali chorak nechta sakkizlik?", ["2", "3", "4"], 1, "Chorakning ikkita sakkizligiga yana bitta sakkizlik qo'shiladi.")], ["meter"])
        definitions.append(definition)
    elif time:
        definitions.append(lesson("meter-inspection", "Metrni notadan tekshirish", "rhythm", 6,
                                  "Murakkab yoki qo'shiluvchi o'lchovda aksentni taxmin qilmang.", context,
                                  [{"title": "Nota belgilari", "text": f"Import boshlanishida {time.get('beats', '?')}/{time.get('beat_type', '?')} ko'rsatilgan. Katta urish guruhlanishi faqat sonlardan to'liq aniqlanmaydi; beaming, aksent va ijrodan tekshiring."}],
                                  [{"title": "Ko'ring", "instruction": "Tanlangan notadagi o'lchov belgisi va guruhlangan notalarni ko'ring. O'zingiz ko'rgan guruhni sanab, kuzatuvga yozing."}],
                                  {"notes": [], "label": "Import metrini kuzatish; tayyor qo'shiq ritmi berilmaydi"}, "O'lchov belgisini va notada ko'rgan guruhlanishni alohida qayd etdim.",
                                  [question("grouping", "O'lchov sonlari doim barcha aksentlarni aniqlaydimi?", ["Ha", "Yo'q, notadagi guruhlash va aksent ham tekshiriladi"], 1, "Notadagi beaming, aksent va ijro konteksti kerak.")], ["meter"]))
    tonal = tonal_material(binding["focus_key"])
    if tonal:
        name = f"{tonal['tonic']} {tonal['mode']}"
        triad = "–".join(tonal["triad"])
        scale = "–".join(tonal["scale"])
        definition = lesson("tonal-map", f"{name}: tovush va akkord", "harmony", 7,
                            "Importdagi aniq mode belgisi asosida original tovush xaritasini toping.", context,
                            [{"title": "Manba belgisi", "text": f"MusicXML key belgisi: {binding['focus_key']['fifths']} fifths, {tonal['mode']} mode. Bu nota faylidagi belgidir; butun asar bo'ylab tonallik o'zgarmaydi degan da'vo emas."}, {"title": "Original xarita", "text": f"{'Tabiiy minor' if tonal['mode'] == 'minor' else 'Major'} gamma: {scale}. Asosiy uch tovush: {triad}. Asarning akkordlar ketma-ketligi bundan taxmin qilinmaydi."}],
                            [{"title": "Toping", "instruction": f"{triad} tovushlarini alohida aytib klavishda toping; keyin qulay holda birga yoki navbat bilan chaling."}, {"title": "Gamma", "instruction": f"{scale} tovushlarini sekin toping. Bemol/diezlarni ayting; fingeringni sayt taxmin qilmaydi."}],
                            {"notes": tonal["notes"], "chords": [tonal["triad_notes"]], "bpm": 40, "beat_unit": "quarter", "key": name},
                            "Nota key belgisini tushuntirdim; original gamma va asosiy uch tovushni uch marta mustaqil topdim.",
                            [question("triad", f"{name} asosiy uch tovushi qaysi?", [triad, "Tovushlar nota importisiz taxmin qilinadi", "Faqat bir tovush"], 0, "Gamma 1, 3, 5 pog'onalaridan uch tovush tuziladi."), question("certainty", "Bu key belgisi nimani isbotlaydi?", ["Butun ijroning barcha akkordlarini", "Import qilingan joydagi yozilgan key va mode belgisini", "Mening amaliy mahoratimni"], 1, "Key metama'lumot; akkordlar ketma-ketligi va ijro mahorati alohida dalil.")], ["minor" if tonal["mode"] == "minor" else "triads", "triads"])
        definitions.append(definition)
    for index in [2, 3, 4, 5]:
        definition = deepcopy(PIRATE_LESSONS[index])
        triad = tonal["triad_notes"] if tonal else ["C4", "E4", "G4"]
        lower = [name[:-1] + str(int(name[-1]) - 1) for name in triad]
        third_name = "Kichik tersiya" if tonal and tonal["mode"] == "minor" else "Katta tersiya"
        semitones = 3 if tonal and tonal["mode"] == "minor" else 4
        if index == 2:
            pair = "–".join([triad[0][:-1], triad[1][:-1]])
            definition["content"]["explanation"] = [{"title": "Harf va yarim ton", "text": f"Original {pair} juftligi — {third_name.lower()}, {semitones} yarim ton. Harf nomida boshlang'ich va oxirgi tovush ham sanaladi. Asosiy va beshinchi pog'ona orasida sof kvinta bor."}, {"title": "Yo'nalish", "text": "Uch tovush bo'ylab yuqori-past harakatni nomlang va keyingi tovushni oldindan toping. Bu original mashqning yo'nalishi; asardagi sakrash tahlili emas."}]
            definition["content"]["steps"] = [{"title": "Ayting", "instruction": f"{pair} va {triad[0][:-1]}–{triad[2][:-1]} juftlarini toping; intervalni nomlab chaling."}, {"title": "Yo'nalish", "instruction": "Original uch tovush bo'ylab yuqoriga va pastga chaling; keyingi tovushni oldindan ayting."}]
            definition["content"]["exercise"] = {"label": "KuyLab original interval mashqi", "original": True, "notes": [triad[0], triad[1], triad[2], triad[1], triad[0]], "bpm": 50, "beat_unit": "quarter"}
            definition["quiz"]["questions"] = [question("third", f"Original {pair} qanday interval?", [third_name, "Sof kvarta", "Sekunda"], 0, f"{semitones} yarim tonli tersiya."), question("fifth", f"{triad[0][:-1]}–{triad[2][:-1]} sof kvintasi nechta yarim ton?", ["5", "7", "9"], 1, "Sof kvinta yetti yarim ton.")]
            definition["success_criterion"] = "Original tersiya va kvintani nomladim; ikki registrda uch marta mustaqil topdim."
        elif index == 3:
            definition["content"]["exercise"] = {"label": "KuyLab original ikki kalit mashqi", "original": True, "notes": triad + lower, "note_hands": ["right"] * 3 + ["left"] * 3, "bpm": 40, "beat_unit": "quarter", "notation": "original_landmarks"}
            definition["content"]["steps"] = [{"title": "Tayanch", "instruction": "Sol kalitidagi G4 va fa kalitidagi F3 tayanchini ko'ring. Original ko'rsatilgan tovushlarga harf pog'onasi bo'yicha sanang."}, {"title": "O'qing", "instruction": "Ko'rsatilgan original notalarni avval nomlab, keyin klavishda chaling. Ikki registrni ajrating."}]
            definition["content"]["explanation"][1]["text"] = f"Chiziqdan keyingi bo'shliq yoki bo'shliqdan keyingi chiziq — harf nomida bir pog'ona. {triad[0]} va {lower[0]} bir nota nomi, lekin boshqa registr. Mashqda yuqori uch tovush sol kalitida, pastki uch tovush fa kalitida ko'rsatiladi."
            definition["success_criterion"] = "Sol va fa kaliti tayanchini nomladim; " + ("import tonalligiga mos " if tonal else "mustaqil ") + "original tovushlarni ikki kalitda uch marta mustaqil o'qidim."
        elif index == 4:
            compound = denominator == 8 and beats in [6, 9, 12]
            group_size = 3 if compound else 2
            pulse_count = beats // 3 if compound else beats if beats in [2, 3, 4] and denominator in [2, 4, 8] else 2
            subdivision_quarters = 0.5 if compound else 2 / denominator if denominator in [2, 4, 8] else 0.5
            count = pulse_count * group_size
            original_meter = f"{beats}/{denominator}" if compound or beats in [2, 3, 4] and denominator in [2, 4, 8] else "4/4"
            right_notes = [triad[position % 3] for position in range(count)]
            definition["content"]["explanation"] = [{"title": "Uchrashuv", "text": f"Original {original_meter} mashqida chap qo'l katta urish boshida, o'ng qo'l har ichki bo'linmada chaladi. Har katta urish {group_size} teng bo'linmadan iborat. Bu asarning qo'l partiyasi emas."}]
            definition["content"]["steps"] = [{"title": "Klavishsiz", "instruction": f"O'ng qo'l bilan har bo'linma, chap qo'l bilan har {group_size} bo'linma boshida yengil uring."}, {"title": "Kichik guruh", "instruction": "Bitta katta urishni ikkala qo'lda qulay tempda chaling, keyin guruhlarni ulang. Uchta ravon urinishni kuzating."}]
            definition["content"]["exercise"] = {"label": "KuyLab original ikki qo'l mashqi", "original": True, "notes": right_notes, "duration_quarters": [subdivision_quarters] * count,
                                                    "left_hand": [{"note": lower[0], "start_quarters": position * subdivision_quarters * group_size, "duration_quarters": subdivision_quarters * group_size} for position in range(pulse_count)],
                                                    "bpm": 40, "beat_unit": "dotted_quarter" if compound else {2: "half", 4: "quarter", 8: "eighth"}.get(denominator, "quarter"), "time_signature": original_meter}
            definition["quiz"]["questions"] = [question("meeting", "Original mashqda qo'llar qayerda birga boshlaydi?", ["Har katta urish boshida", "Tasodifiy joylarda", "Faqat yakunda"], 0, "Chap qo'l katta puls boshida; o'ng qo'l ichki bo'linmalar bilan davom etadi."), PIRATE_LESSONS[4]["quiz"]["questions"][1]]
            definition["success_criterion"] = "Ikki qo'lni katta urish boshida birga tushirdim; original mashqni qulay tempda uch marta to'xtamay chaldim."
        elif index == 5:
            definition["content"]["exercise"] = {"label": "KuyLab original qayta chaqirish mashqi", "original": True, "notes": triad + [triad[0][:-1] + str(int(triad[0][-1]) + 1)] + list(reversed(triad)) + [triad[0]], "bpm": 50, "beat_unit": "quarter", "mode": "original_recall_fragment"}
        if index == 4 and not (beats == 6 and denominator == 8):
            definition["context"] = context
        else:
            definition["context"] = context
        definitions.append(definition)
    query = {"page": "practice", "composition": arrangement.composition_id, "score": score.id,
             "start_index": start_index, "end_index": end_index}
    if section:
        query["section"] = section["id"]
    for definition in definitions:
        scope = {"key": binding["focus_key"], "time": binding["focus_time"], "section": {field: section[field] for field in ["id", "start_index", "end_index"]} if section else None}
        fingerprint = hashlib.sha256(json.dumps(scope, sort_keys=True).encode()).hexdigest()[:8]
        definition["code"] = f"score-{score.id}-{fingerprint}-{definition['code']}"
        definition["score_version_id"] = score.id
        if definition["kind"] != "source_excerpt":
            definition["context"] = context
        definition["content"]["score_binding"] = binding
        if definition["kind"] == "preparation" and definition.get("skill") != "rhythm" and not tonal:
            definition["context"] += " Key mode belgisi tasdiqlanmagani uchun bu klavish mashqi mustaqil C major misolida; importning tonalligi deb ko'rsatilmaydi."
        item_query = dict(query)
        if definition["kind"] == "source_excerpt":
            item_query.update(definition["content"]["exercise"]["tempo_choice"])
        definition["content"]["practice_link"] = "/?" + urlencode(item_query)
        if definition["kind"] == "source_excerpt":
            definition["content"]["exercise"]["practice_link"] = definition["content"]["practice_link"]
        definition["content"]["transfer"] = f"Import qilingan shu {score.version}-versiyaga qayting" + (f", siz belgilagan «{section['title']}» qismini tanlang" if section else "; o'zingiz qiyin joyni belgilang") + ". Dars fikrini notada toping va bir aniq kuzatuv yozing." + ("" if definition["kind"] == "source_excerpt" else " Bu joy texnik jihatdan avtomatik tahlil qilingan emas.")
    return definitions


def ensure_curriculum(arrangement):
    """Only fill missing authored modules, preserving progress and user content."""
    score = active_score(arrangement)
    if score and score.file_format == "midi":
        from .midi_curriculum import midi_definitions
        definitions = midi_definitions(arrangement, score)
    else:
        definitions = imported_definitions(arrangement, score) if score else pdf_definitions(arrangement) if arrangement.full_score_verified_at and arrangement.seed_key == "hes-a-pirate-unpianiste-full" else PIRATE_LESSONS if supports_pirate_preparation(arrangement) else [SOURCE_LESSON]
    for position, definition in enumerate(definitions, 1):
        item, created = LearningLesson.objects.get_or_create(arrangement=arrangement, code=definition["code"], defaults={"order": position, **definition})
        # User hotspot edits update navigation/evidence, never transfer mastery
        # from one score version to a different score version.
        needs_source_refresh = item.kind == "source_excerpt" and (item.content != definition["content"] or item.context != definition["context"] or item.title != definition["title"])
        # Editorial corrections to the same authored quiz keep learner evidence;
        # a different score or passage still gets its own lesson identity above.
        needs_authored_text_refresh = not score and supports_pirate_preparation(arrangement) and item.quiz == definition["quiz"] and item.content != definition["content"]
        if not created and (needs_authored_text_refresh or needs_source_refresh or score and item.content.get("score_binding") != definition["content"].get("score_binding")):
            item.context = definition["context"]
            item.content = definition["content"]
            if item.kind == "source_excerpt":
                item.title = definition["title"]
            before_key = [(question["id"], question.get("correct_choice"), [choice["id"] for choice in question["choices"]]) for question in item.quiz.get("questions", [])]
            after_key = [(question["id"], question.get("correct_choice"), [choice["id"] for choice in question["choices"]]) for question in definition["quiz"].get("questions", [])]
            if before_key == after_key:
                item.quiz = definition["quiz"]
            item.save(update_fields=["context", "content", "title", "quiz"])
    # Source selection may advance; hide the obsolete onboarding module in API,
    # but retain its records as historical evidence.
    return arrangement.lessons.filter(code__in=[item["code"] for item in definitions])
