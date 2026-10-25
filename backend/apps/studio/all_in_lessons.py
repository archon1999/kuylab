"""Shared All in course, reviewed against all thirteen supplied MIDI files.

The PDF's nine drills are retained as nine lessons, with separate study copies
and explicit links back to Easy/Hard source passages. A main-player variant is
an arrangement choice, never a second course or duplicated learning progress.
"""
from functools import lru_cache
from .content import tr
from .all_in_package import package_source

VERSE = (15.713544, 29.458336)
MOTIF = (15.713544, 19.255212)
PRECHORUS = (42.218756, 67.040048)
CHORUS = (67.040048, 91.850174)

PLANS = [
    {
        "code": "chord-shapes", "file": "01_Akkord_shakllari_60bpm.mid", "bpm": 60, "window": VERSE,
        "title": tr("Akkordni tanish: Dm, B♭ va A", "Узнать аккорд: Dm, B♭ и A", "Recognise the chord: Dm, B♭ and A"),
        "concept": tr(
            "Akkord — bir-biriga tegishli tovushlar guruhi. Uch tovushli akkordda asos, tersiya va kvinta bor. Asosdan uchta harf nomini sanab tersiyani topamiz: D–E–F, demak D dan tersiya F. Kvinta beshinchi harf: D–E–F–G–A. Minor tersiya 3 yarim ton, major tersiya 4 yarim ton. Dm = D–F–A; A major = A–C♯–E.",
            "Аккорд — группа связанных звуков. В трезвучии есть основной тон, терция и квинта. Терция охватывает три буквенных имени: D–E–F, значит терция от D — F. Квинта — пятое имя D–E–F–G–A. Малая терция содержит 3 полутона, большая — 4. Dm = D–F–A; A major = A–C♯–E.",
            "A chord is a group of related tones. A triad contains a root, third and fifth. Count three letter names for the third: D–E–F, so F is the third above D. The fifth is the fifth letter, D–E–F–G–A. A minor third spans 3 semitones; a major third spans 4. Dm is D–F–A; A major is A–C♯–E."),
        "example": tr(
            "01-mashq olti shaklni beradi: Dm = D–F–A, B♭ = B♭–D–F, A = A–C♯–E, Gm = G–B♭–D, C = C–E–G, F = F–A–C. Har shakl oldin bir vaqtda, keyin asos–kvinta–tersiya–kvinta tartibida chalinadi. Dm uchun bu D3–A3–F3–A3. Raqamli darajalar barmoq raqamlari emas.",
            "Упражнение 01 даёт шесть форм: Dm = D–F–A, B♭ = B♭–D–F, A = A–C♯–E, Gm = G–B♭–D, C = C–E–G, F = F–A–C. Сначала звуки вместе, затем основной тон–квинта–терция–квинта. Для Dm это D3–A3–F3–A3. Ступени аккорда не являются номерами пальцев.",
            "Drill 01 contains six shapes: Dm = D–F–A, B♭ = B♭–D–F, A = A–C♯–E, Gm = G–B♭–D, C = C–E–G, F = F–A–C. Each is first blocked, then broken as root–fifth–third–fifth. Dm becomes D3–A3–F3–A3. Chord degrees are not finger numbers."),
        "listen": tr("Birga bosilgan akkord va tarqatilgan naqshda bir xil tovushlar qolishini eshiting. A akkordidagi C♯ ni C bilan almashtirib bo‘lmaydi: bu boshqa akkord bo‘ladi.", "Услышьте одинаковый набор звуков в аккорде и разложенной фигуре. Не заменяйте C♯ в аккорде A на C: получится другой аккорд.", "Hear the same pitch collection in the blocked and broken shapes. Replacing C♯ with C changes the A chord."),
        "method": tr("Avval uch klavishani tovushsiz toping, keyin birga chaling. Qo‘lni shu shakl atrofida saqlab, to‘rt notali naqshga o‘ting. Dm, B♭ va A ni alohida aytib, yangi asosni oldindan ko‘ring; keyingi bosqichda shu shakllarni asarning oson kupletida eshitasiz.", "Сначала найдите три клавиши без звука, затем возьмите их вместе. Сохраняя форму, перейдите к четырём звукам. Назовите Dm, B♭ и A и заранее найдите новый основной тон; следующий этап переносит формы в облегчённый куплет.", "Locate the three keys silently, then play them together. Keep the shape as you unfold four notes. Name Dm, B♭ and A and locate each new root early; the next stage places these shapes in the Easy verse."),
        "pitfall": tr("B♭ — si bemol, C♯ — do diyez. Player B♭ ni A♯ deb ko‘rsatishi mumkin: pianinoda ayni klavisha. Bu kurs D minor tonalligida; A major ichidagi C♯ uning D ga yo‘nalishini kuchaytiradi.", "B♭ — си-бемоль, C♯ — до-диез. Плеер может показать B♭ как A♯: на пианино это та же клавиша. Курс в ре миноре; C♯ в A major усиливает тяготение к D.", "B♭ means B flat and C♯ means C sharp. The player may spell B♭ as A♯: they share a piano key. This arrangement is in D minor; C♯ in A major strengthens the pull towards D."),
        "ready": tr("Olti shaklning tovushlarini aytib, birga va ketma-ket chalishni farqlay olaman.", "Могу назвать звуки шести форм и отличить аккорд от разложенной фигуры.", "I can name the six shapes and distinguish blocked from broken chords."),
        "fingering": tr("Chap qo‘lning oddiy to‘rt notali naqshlari: 5–1–3–1 ni sinang. 1 — bosh barmoq, 5 — jimjiloq. Bu qo‘lga moslashtiriladigan tavsiya.", "Для простого рисунка левой попробуйте 5–1–3–1. 1 — большой палец, 5 — мизинец. Подстройте рекомендацию под руку.", "For the simple LH patterns try 5–1–3–1. 1 is the thumb and 5 the little finger; adapt the suggestion to your hand."),
        "related": ["triads", "intervals"], "path": "easy",
    },
    {
        "code": "easy-verse", "file": "02_Kuplet_oson_60bpm.mid", "bpm": 60, "window": VERSE,
        "title": tr("Oson kuplet: Dm–Dm–B♭–A", "Простой куплет: Dm–Dm–B♭–A", "Easy verse: Dm–Dm–B♭–A"),
        "concept": tr("Jo‘rlik melodiyaga tayanch bo‘ladi. Bitta takt — shu mashqda 1–2–3–4 deb sanaladigan to‘rt urish. Har urishda bitta chap qo‘l notasi bor. Dm ikki takt davom etadi, so‘ng bir takt B♭ va bir takt A keladi: akkordlar soni bilan taktlar sonini aralashtirmang.", "Сопровождение поддерживает мелодию. В этом упражнении такт содержит четыре доли: 1–2–3–4. На долю приходится одна нота левой. Dm длится два такта, затем по такту B♭ и A: число аккордов не равно числу тактов.", "Accompaniment supports the melody. Here a bar contains four beats counted 1–2–3–4, with one LH note per beat. Dm lasts two bars, followed by one bar each of B♭ and A; chord count is not bar count."),
        "example": tr("02-mashqda D3–A3–F3–A3 ikki marta; keyin B♭2–F3–D3–F3; A2–E3–C♯3–E3 keladi. Bir aylanish 16 urish. 60 BPM da har urish bir soniya; to‘rt urishlik kirishdan keyin naqsh boshlanadi. To‘liq Easy faylida shu qism 0:15.71 da boshlanadi va ijro tempi erkinroq.", "В упражнении 02 дважды звучит D3–A3–F3–A3, затем B♭2–F3–D3–F3 и A2–E3–C♯3–E3. Цикл — 16 долей. При 60 BPM доля равна секунде; перед вступлением четыре подготовительные доли. В полном Easy куплет начинается на 0:15.71, с более свободным темпом.", "Drill 02 plays D3–A3–F3–A3 twice, then B♭2–F3–D3–F3 and A2–E3–C♯3–E3. One cycle is 16 beats. At 60 BPM each beat lasts a second, after four preparation beats. In the complete Easy file the verse begins at 0:15.71 with freer timing."),
        "listen": tr("Ikkinchi Dm yangi akkord emas, o‘sha shaklning yana bir takti. A ning C♯ tovushi kelganda rang o‘zgarishini eshiting. Asosiy kuyni qo‘shganda chap qo‘l undan yumshoqroq qolsin.", "Второй Dm — ещё один такт той же формы. Услышьте смену окраски на C♯ аккорда A. С мелодией левая должна оставаться мягче.", "The second Dm is another bar of the same shape. Hear the colour change at the A chord's C♯. With the melody added, keep the LH softer."),
        "method": tr("Akkord nomlarini urish ustida ayting. Avval bitta aylanishni xotirjam chaling, keyin qo‘lda boshiga qaytib yana tekshiring. Dm dan B♭ ga o‘tishda qo‘lni pastroqqa tayyorlang. Easy kontekst bosqichida yangi kuy kirsa ham chapdagi to‘rtlikni shoshirmang.", "Произносите названия аккордов на долях. Спокойно сыграйте цикл, вручную вернитесь и проверьте ещё раз. Перед B♭ подготовьте руку ниже. В контексте Easy мелодия не должна ускорять левую четвёрку.", "Say the chord names over the pulse. Play one calm cycle, seek back manually and check it again. Prepare the lower position before B♭. In the Easy context, do not let the arriving melody hurry the four-note accompaniment."),
        "pitfall": tr("Faqat birinchi notani bilish yetmaydi: keyingi uch nota ham akkord shakliga tegishli. A da C♯ o‘rniga C bosish yoki ikkinchi Dm taktini tashlab ketish aylanishni o‘zgartiradi.", "Недостаточно знать первый бас: следующие три звука тоже принадлежат форме. C вместо C♯ в A или пропуск второго такта Dm меняет цикл.", "Knowing only the first bass is insufficient: the next three notes belong to the shape too. Playing C instead of C♯ in A, or skipping the second Dm bar, changes the cycle."),
        "ready": tr("16 urishlik aylanishda akkord va tempni yo‘qotmayman; o‘ng qo‘l qo‘shilganda jo‘rlik yumshoq qoladi.", "Сохраняю аккорды и пульс все 16 долей; с правой рукой сопровождение остаётся мягким.", "I keep the chords and pulse for all 16 beats, with soft accompaniment when the RH joins."),
        "related": ["pulse", "arpeggio"], "path": "easy",
    },
    {
        "code": "open-arpeggio", "file": "03_Dm_ochiq_arpej_50bpm.mid", "bpm": 50, "window": MOTIF,
        "title": tr("Keng arpej: cho‘zilish emas, ko‘chish", "Широкое арпеджио: перенос руки", "Open arpeggio: move the hand"),
        "concept": tr("Arpejio — akkord tovushlarining ketma-ket kelishi. Ochiq arpejda tovushlar bir kaft pozitsiyasidan kengroq yoyiladi. D3–A3 bir guruh, D4–F4 esa keyingi guruh: bularni bir vaqtning o‘zida kaft bilan qamrash shart emas.", "Арпеджио — последовательность звуков аккорда. В открытом расположении они выходят за одну позицию кисти. D3–A3 — одна группа, D4–F4 — следующая; не нужно охватывать обе группы одновременно.", "An arpeggio unfolds chord tones. An open voicing spreads them beyond one hand position. D3–A3 forms one group and D4–F4 the next; you do not need to span both groups at once."),
        "example": tr("03-mashq: D3 → A3 → D4 → F4, har notaga bir urish, 50 BPM. C4 — o‘rta do, shuning uchun D3 undan pastda, D4 yuqoriroq. Hard kupletining dastlabki to‘rtta chap qo‘l notasi ham shu balandliklarda, lekin 0:15.72 dan tezroq va erkin vaqtda kiradi.", "Упражнение 03: D3 → A3 → D4 → F4, по ноте на долю при 50 BPM. C4 — среднее до: D3 ниже, D4 выше. Первые четыре ноты левой в Hard имеют те же высоты, но с 0:15.72 вступают быстрее и свободнее.", "Drill 03 is D3 → A3 → D4 → F4, one note per beat at 50 BPM. C4 is middle C, placing D3 below it and D4 above. The first four Hard verse LH notes have these same pitches but enter faster and more freely from 0:15.72."),
        "listen": tr("Yuqoridagi F4 ga yetish uchun past D ni kuchaytirish kerak emas. Guruh almashganda ovoz birdan qattiqlashmasin. Mashqdagi bir urishli qadamni manbadagi tez figura bilan bir xil ritm deb qabul qilmang.", "Не усиливайте нижнее D ради достижения F4. При смене группы не должно возникать резкого акцента. Шаги по долям в упражнении не являются ритмом быстрой исходной фигуры.", "Do not strike low D harder to reach F4. Avoid a sudden accent at the group change. The drill's one-beat steps are not the rhythm of the fast source figure."),
        "method": tr("D3–A3 ni alohida, so‘ng D4–F4 ni alohida toping. Oldingi tovushni bo‘shatib, butun kaftni ikkinchi guruhga olib boring. Keyin ikkalasini ulang. Asl chap qo‘l bosqichida E4 va G4 qo‘shimcha tovushlar ham qaytadi; ularni keyingi dars izohlaydi.", "Отдельно найдите D3–A3 и D4–F4. Освободив предыдущий звук, перенесите кисть во вторую группу, затем соедините их. В исходном левом слое вернутся E4 и G4; следующий урок объясняет эти дополнительные тоны.", "Locate D3–A3 and D4–F4 separately. Release the earlier tone, move the hand to the second group, then connect them. The source LH stage brings back E4 and G4; the next lesson explains these additional tones."),
        "pitfall": tr("MIDIdagi uzun nota barmoqni shu klavishada qoldirish bo‘yicha rasmiy ko‘rsatma emas. Avval pedalsiz yo‘lni tekshiring; pedal qo‘lning noqulay cho‘zilishini oqlamaydi.", "Длинная нота MIDI не является официальным указанием удерживать её пальцем. Сначала проверьте перенос без педали; педаль не оправдывает неудобное растяжение.", "A long MIDI note is not an official instruction to keep a finger fixed on that key. Check the travel without pedal first; pedal does not justify an awkward stretch."),
        "ready": tr("D3–A3 dan D4–F4 ga qo‘lni qotirmasdan va keskin aksentsiz ko‘cha olaman.", "Перехожу от D3–A3 к D4–F4 без зажима и резкого акцента.", "I can move from D3–A3 to D4–F4 without stiffness or an abrupt accent."),
        "fingering": tr("Guruhlash uchun chap 5–2 | 5–3 ni sinang. D4 oldidan kaft ko‘chadi. Bu tez final ijro uchun majburiy applikatura emas.", "Для группировки попробуйте левой 5–2 | 5–3. Перед D4 кисть переносится; это не обязательная аппликатура финального темпа.", "For grouping, try LH 5–2 | 5–3, moving before D4. This is not mandatory fingering for the final tempo."),
        "related": ["arpeggio", "legato"], "path": "hard",
    },
    {
        "code": "original-motif", "file": "04_Dm_asl_motiv_40bpm.mid", "bpm": 40, "window": MOTIF,
        "title": tr("Asl sakkiz notali Dm motivi", "Исходный мотив Dm из восьми нот", "The original eight-note Dm figure"),
        "concept": tr("Akkord tovushi bilan melodik bezak boshqa vazifalar bajaradi. Dm uchligi D–F–A bo‘lsa ham, figura E va G orqali yurishi mumkin. Bu tovushlarni xato deb olib tashlamang: arpej shakli ustida kichik melodik javob hosil bo‘ladi.", "Аккордовые тоны и мелодическое украшение выполняют разные функции. Трезвучие Dm — D–F–A, но фигура может проходить через E и G. Это не ошибки: над арпеджио возникает небольшой мелодический ответ.", "Chord tones and melodic decoration serve different roles. Dm contains D–F–A, yet its figure can travel through E and G. These are not errors: a small melodic response grows out of the arpeggio."),
        "example": tr("Aniq tartib: D3–A3 | D4–F4–E4–D4–F4–G4. 04-mashqda sakkiz nota teng o‘n oltitalikka yozilgan: har urishda to‘rtta nota, 40 BPM. Figura ikki urishda tugaydi; qolgan ikki urish dam. Hard faylida shu balandlik va tartib bor, ammo kirishlar tenglashtirilmagan.", "Точный порядок: D3–A3 | D4–F4–E4–D4–F4–G4. В упражнении 04 восемь ровных шестнадцатых: четыре на долю при 40 BPM. Фигура занимает две доли, ещё две — отдых. В Hard те же высоты и порядок, но вступления не выровнены.", "The exact order is D3–A3 | D4–F4–E4–D4–F4–G4. Drill 04 uses eight even sixteenths: four per beat at 40 BPM. The figure fills two beats, followed by two beats of rest. Hard has these pitches in this order, with unquantised attacks."),
        "listen": tr("Sanoqni 1-e-&-a | 2-e-&-a | 3 | 4 deb ajrating. Dam vaqtida ham ichki urish davom etadi. F4–E4–D4 pasayishidan keyin F4–G4 ko‘tarilishini alohida eshiting.", "Разделите счёт: 1-e-&-a | 2-e-&-a | 3 | 4. Во время паузы пульс продолжается. Услышьте спуск F4–E4–D4, затем подъём F4–G4.", "Count 1-e-&-a | 2-e-&-a | 3 | 4. Keep the inner pulse through the rest. Hear F4–E4–D4 descend before F4–G4 rises."),
        "method": tr("Avval 03-darsdagi to‘rtta tayanchni eslang. F4 dan keyin E4–D4 javobini, so‘ng F4–G4 ni qo‘shing. Tovush nomlari aniq bo‘lgach guruhlarni ulang. Hard chap qo‘lini 60% da tinglab, tekis mashq va erkin ijro farqini eshiting; keyin ikki qo‘lni qo‘shing.", "Вспомните четыре опоры урока 03. После F4 добавьте E4–D4, затем F4–G4. Соедините группы, когда названия ясны. Сравните ровное упражнение с левой Hard на 60%, затем добавьте обе руки.", "Recall lesson 03's four landmarks. After F4 add E4–D4, then F4–G4. Connect the groups once the names are clear. Compare the even drill with the Hard LH at 60%, then add both hands."),
        "pitfall": tr("40 BPM sekin ko‘rinsa ham, bir urishga to‘rtta nota sabab sekundiga taxminan 2.67 nota keladi. Har notani bitta urish deb sanamang va ikki urishlik damni qisqartirmang.", "Хотя 40 BPM кажется медленным, четыре ноты на долю дают около 2,67 нот в секунду. Не считайте каждую ноту долей и не сокращайте две доли отдыха.", "Although 40 BPM sounds slow, four notes per beat means about 2.67 notes per second. Do not count each note as a beat or shorten the two-beat rest."),
        "ready": tr("Sakkiz notaning tartibini va ikki urishlik damni bilaman; asl erkin vaqtga o‘tganda ortiqcha aksent bermayman.", "Знаю восемь нот и две доли отдыха; при переходе к свободному времени не добавляю акцентов.", "I know all eight notes and the two-beat rest, without adding accents when returning to freer source timing."),
        "fingering": tr("Guruhlash tavsiyasi: 5–2 | 5–3–4–5–3–2. Pozitsiyalar orasida kaft ko‘chadi; raqamlar qo‘lga qarab moslanadi.", "Для группировки: 5–2 | 5–3–4–5–3–2. Между позициями переносится кисть; подстройте пальцы под руку.", "Grouping suggestion: 5–2 | 5–3–4–5–3–2. Move between positions and adapt the fingers to your hand."),
        "related": ["durations", "rests", "arpeggio"], "path": "hard",
    },
    {
        "code": "prechorus", "file": "05_Prechorus_60bpm.mid", "bpm": 60, "window": PRECHORUS,
        "title": tr("Naqarot oldi: Em7♭5 dan A ga", "Перед припевом: от Em7♭5 к A", "Before the chorus: Em7♭5 to A"),
        "concept": tr("Septakkord to‘rtta turli tovushdan tuziladi. Em7♭5 = E–G–B♭–D: asos E, kichik tersiya G, pasaytirilgan kvinta B♭ va kichik septima D. Bu oddiy E minor uchligi E–G–B emas. Keyingi A = A–C♯–E akkordi D minorning asosiy D tovushiga qaytishga tayyorlaydi.", "Септаккорд содержит четыре разных звука. Em7♭5 = E–G–B♭–D: основной E, малая терция G, уменьшённая квинта B♭ и малая септима D. Это не трезвучие E minor E–G–B. Следующий A = A–C♯–E готовит возвращение к основному D ре минора.", "A seventh chord has four distinct tones. Em7♭5 is E–G–B♭–D: root E, minor third G, diminished fifth B♭ and minor seventh D. It is not the E minor triad E–G–B. The following A = A–C♯–E prepares the return to D minor's tonic D."),
        "example": tr("05-mashq xaritasi: Gm | C | F | B♭ | Gm | Em7♭5 | A | A. Em7♭5 naqshi E3–B♭3–G3–D4. So‘ng A2–E3–C♯3–E3 ga tushasiz. Asarda tayyorlov 0:42.22 dan 1:07.04 gacha; to‘liq ijroda qo‘shimcha tovushlar va vaqt erkinligi bor.", "Карта упражнения 05: Gm | C | F | B♭ | Gm | Em7♭5 | A | A. Рисунок Em7♭5: E3–B♭3–G3–D4, затем A2–E3–C♯3–E3. В пьесе подготовка длится с 0:42.22 до 1:07.04; полная фактура содержит дополнительные звуки и свободное время.", "Drill 05 follows Gm | C | F | B♭ | Gm | Em7♭5 | A | A. Em7♭5 unfolds E3–B♭3–G3–D4, then moves down to A2–E3–C♯3–E3. The source passage runs from 0:42.22 to 1:07.04, with additional tones and freer timing in the full texture."),
        "listen": tr("B♭ dan keyingi C♯ ning boshqa klavisha ekanini eshiting va ko‘ring. Oxirgi ikki A takti shoshilmay, naqarotning D ga kirishini tayyorlasin.", "Услышьте и увидьте, что после B♭ приходит другая клавиша C♯. Два последних такта A не торопятся, а готовят D припева.", "Hear and see B♭ give way to the different key C♯. Let the final two A bars prepare the chorus's D without rushing."),
        "method": tr("Avval Em7♭5 va A ning barcha klavishalarini alohida toping. E3 dan A2 ga kaft ko‘chishini tovushsiz mashq qiling. Keyin Gm dan boshlab butun sakkiz taktni ulang. Easy chap qo‘ldan Hard chap qo‘lga o‘tganda akkord xaritasi saqlanadi, nota soni ko‘payadi.", "Найдите клавиши Em7♭5 и A отдельно. Без звука подготовьте перенос с E3 к A2, затем соедините все восемь тактов от Gm. При переходе от Easy к Hard карта аккордов сохраняется, нот становится больше.", "Locate Em7♭5 and A separately. Rehearse the move from E3 to A2 silently, then connect all eight bars from Gm. Moving from Easy to Hard retains the harmonic map while increasing the note count."),
        "pitfall": tr("Em7♭5 ichidagi B♭ ni B ga yoki A ichidagi C♯ ni C ga almashtirmang. Bir xil barmoqlashni har akkordga majburan qo‘llash o‘rniga registr va kenglikni oldindan tekshiring.", "Не меняйте B♭ на B в Em7♭5 и C♯ на C в A. Вместо одной обязательной аппликатуры проверьте регистр и расстояния каждого аккорда.", "Do not replace B♭ with B in Em7♭5, or C♯ with C in A. Check each chord's register and spacing instead of forcing one fingering onto every shape."),
        "ready": tr("Em7♭5 va A tovushlarini tushuntirib, sakkiz takt xaritasini tempni yo‘qotmasdan kuzata olaman.", "Могу назвать звуки Em7♭5 и A и пройти карту восьми тактов без потери пульса.", "I can explain Em7♭5 and A and follow the eight-bar map without losing the pulse."),
        "related": ["seventh-chords", "tonic-dominant"], "path": "both",
    },
    {
        "code": "octave-landings", "file": "06_Naqarot_faqat_oktavalar_60bpm.mid", "bpm": 60, "window": CHORUS,
        "title": tr("Naqarot: past oktava tayanchlari", "Припев: опоры низких октав", "Chorus: low octave landings"),
        "concept": tr("Oktava — bir xil harfli tovushning boshqa registrdagi jufti, masalan D2+D3. Ular orasida 12 yarim ton bor. “+” ikkala tovush bir vaqtda chalinishini bildiradi. Bu mashqda yuqori javoblar olib tashlangan: maqsad faqat past tayanchdan keyingisiga erkin ko‘chish.", "Октава — пара одноимённых звуков в разных регистрах, например D2+D3, на расстоянии 12 полутонов. Знак «+» означает одновременное нажатие. Верхние ответы здесь убраны: задача — свободно переходить между нижними опорами.", "An octave pairs the same letter name in different registers, such as D2+D3, twelve semitones apart. The plus sign means play both together. Upper responses are omitted here so you can practise travelling between low landmarks."),
        "example": tr("Birinchi taktning 1-urishida D2+D3, 3-urishida A1+A2. Keyingi B♭ taktida B♭1+B♭2. 06-mashqda zarbalar aniq bir vaqtda va qisqaroq yozilgan. Asosiy Easy va Hard fayllaridagi 42 past oktava jufti esa asl mayda vaqt farqi, davomiyligi va kuchini bir xil saqlaydi.", "В первом такте на доле 1 — D2+D3, на доле 3 — A1+A2; в следующем — B♭1+B♭2. В упражнении 06 атаки ровно вместе и короче. В основных Easy и Hard все 42 низкие октавные пары сохраняют одинаковые исходные микросдвиги, длительности и силу.", "The first bar places D2+D3 on beat 1 and A1+A2 on beat 3, followed by B♭1+B♭2 in the next bar. Drill 06 aligns and shortens these attacks. Both main variants retain the same 42 original low octave pairs, including small timing offsets, holds and velocities."),
        "listen": tr("Past oktava urg‘u beradi, lekin uni maksimal kuch bilan urish shart emas. Zarbalar orasidagi bo‘shliq vaqtni yo‘qotish emas: ichingizda 1–2–3–4 davom etsin.", "Низкая октава даёт опору, но не требует максимального удара. Промежуток — не потерянное время: продолжайте внутренний счёт 1–2–3–4.", "A low octave provides weight without needing maximum force. The gap is not lost time: keep counting 1–2–3–4 internally."),
        "method": tr("Avval har oktavaning faqat pastki notasini topib chiqing. Keyin qulay bo‘lsa yuqori juftni qo‘shing. Zarbadan so‘ng qo‘lni bo‘shatib, keyingi joyni ko‘z bilan toping. Easy kontekstida yuqori javoblar qaytadi; bu yangi vazifa keyingi darsda alohida ishlanadi.", "Сначала найдите только нижние ноты, затем добавьте верхние, если расстояние удобно. После атаки освободите кисть и глазами найдите следующее место. В контексте Easy вернутся верхние ответы; следующий урок изучает их отдельно.", "First locate only the lower notes, adding the upper partner if the span is comfortable. Release the hand after each attack and look ahead to the next landing. Upper responses return in the Easy context and are studied separately next."),
        "pitfall": tr("Oktavaga yetish uchun kaftni kuch bilan cho‘zmang. Oson variantda ham bu sakrashlar qolgan; “Easy” butun asar boshlang‘ich darajada degani emas. Tayyor bo‘lmasangiz, avval pastki notaning o‘zini mashq qiling.", "Не растягивайте кисть через усилие. Эти скачки остаются и в Easy: это не начальная сложность всей пьесы. Если пока неудобно, изучите только нижний тон.", "Do not force the octave span. These jumps remain in Easy, which does not make the entire piece beginner-level. If needed, first practise the lower note alone."),
        "ready": tr("Keyingi past tayanchni oldindan topaman, oktavadan keyin qo‘l bo‘sh va sanoq davom etadi.", "Заранее нахожу следующую опору, освобождаю руку после октавы и сохраняю счёт.", "I locate the next low landmark early, release after the octave and keep counting."),
        "fingering": tr("Oktava uchun chap 5+1 odatiy boshlang‘ich variant. Oraliq qulay bo‘lmasa uni majburan cho‘zmang; avval pastki tovush bilan yo‘lni o‘rganing.", "Для октавы левой обычно начинают с 5+1. Не тянитесь через усилие; сначала изучите путь по нижним звукам.", "LH 5+1 is a common starting point for octaves. Do not force the span; learn the route with lower tones first."),
        "related": ["intervals", "practice"], "path": "easy",
    },
    {
        "code": "chorus-responses", "file": "07_Naqarot_oson_LH_60bpm.mid", "bpm": 60, "window": CHORUS,
        "title": tr("Oktavadan keyin: oson chap qo‘l javobi", "После октавы: простой ответ левой", "After the octave: the Easy LH response"),
        "concept": tr("Jo‘rlik past tayanch va yuqoriroq javob o‘rtasida almashadi. Birinchi takt o‘rtasida uyg‘unlik Dm dan A7 ga o‘zgaradi. A7 — A–C♯–E–G; javobdagi C♯ va G uning tersiyasi va septimasi. Demak butun takt davomida bitta akkord turmaydi.", "Сопровождение чередует нижнюю опору и верхний ответ. В середине первого такта Dm меняется на A7. A7 — A–C♯–E–G; C♯ и G в ответе — его терция и септима. Один аккорд не обязательно длится весь такт.", "The accompaniment alternates a low landmark with an upper response. Halfway through the first bar Dm changes to A7. A7 contains A–C♯–E–G; the response's C♯ and G are its third and seventh. One chord need not last the entire bar."),
        "example": tr("07-mashqning birinchi takti: 1 — D2+D3; 2 — F3+A3; 3 — A1+A2; 4 — C♯3+G3. Keyingi takt: B♭1+B♭2 → F3 → D3 → F3. Bu Easy variantidagi naqsh; Hard shu joyda kengroq va zichroq yuradi.", "Первый такт упражнения 07: 1 — D2+D3; 2 — F3+A3; 3 — A1+A2; 4 — C♯3+G3. Следующий: B♭1+B♭2 → F3 → D3 → F3. Это рисунок Easy; Hard движется здесь шире и плотнее.", "Drill 07's first bar is 1: D2+D3; 2: F3+A3; 3: A1+A2; 4: C♯3+G3. Next comes B♭1+B♭2 → F3 → D3 → F3. This is the Easy pattern; Hard uses wider and denser travel here."),
        "listen": tr("Yuqori javobni oktavadan yengilroq chaling: past tayanch eshitilsin, lekin javob ham yo‘qolmasin. 2 va 4-urishlarni shoshirsangiz, oktavalar orasidagi masofa notekis eshitiladi.", "Верхний ответ играйте легче октавы: бас слышен, ответ не теряется. Если торопить доли 2 и 4, расстояние между октавами станет неровным.", "Play the upper response lighter than the octave, without losing it. Rushing beats 2 and 4 makes the spacing between octave landmarks uneven."),
        "method": tr("06-darsdagi oktavalarni eslang. Faqat 1→2 ko‘chishni, keyin 3→4 ni tayyorlang. Ikkisini birlashtirib, keyingi B♭ ga chiqishni qo‘shing. Easy kontekstdan keyin Hard ning sekin ikki qo‘l bosqichida qo‘shimcha notalarni alohida kuzating.", "Вспомните октавы урока 06. Подготовьте отдельно переносы 1→2 и 3→4, соедините их и добавьте выход к B♭. После Easy следите за добавленными нотами в медленном этапе обеих рук Hard.", "Recall lesson 06's octaves. Prepare moves 1→2 and 3→4 separately, join them, then add the exit to B♭. After the Easy context, identify added notes in the slow both-hands Hard stage."),
        "pitfall": tr("Naqshni bitta uzluksiz pedal bilan xiralashtirmang. Dm dan A7 ga o‘tishda uyg‘unlik yangilanadi. Paketning asosiy fayllarida CC64 pedal yoqilmagan; eshitilayotgan uzun notalar avtomatik pedal ko‘rsatmasi emas.", "Не размывайте рисунок одной непрерывной педалью: при Dm→A7 гармония меняется. В основных файлах CC64 только выключает педаль; длинные ноты не являются автоматической инструкцией педализации.", "Do not blur the pattern under one continuous pedal: Dm→A7 changes the harmony. The main files contain only sustain-off CC64 messages; long notes are not automatic pedal instructions."),
        "ready": tr("To‘rt urishdagi oktava–javob almashishini va Dm→A7 o‘zgarishini tushuntirib, tekis chala olaman.", "Могу объяснить и ровно сыграть чередование октава–ответ и смену Dm→A7.", "I can explain and evenly play the octave–response alternation and Dm→A7 change."),
        "related": ["seventh-chords", "pedal", "voicing"], "path": "both",
    },
    {
        "code": "chorus-together", "file": "08_Naqarot_ikki_qol_60bpm.mid", "bpm": 60, "window": CHORUS,
        "title": tr("Naqarotni ikki qo‘lda birlashtirish", "Соединить припев двумя руками", "Join both hands in the chorus"),
        "concept": tr("Ikki qo‘l mustaqilligi — har qo‘l o‘z ritmini saqlab, umumiy urishni yo‘qotmasligi. O‘ng qo‘lning zich notalari chap qo‘ldagi oktava va javobni tezlashtirmasligi kerak. Easy ham o‘ng qo‘lni soddalashtirmaydi: bu bosqichning murakkabligi qoladi.", "Независимость рук означает сохранение собственного ритма в общем пульсе. Плотные ноты правой не должны ускорять октавы и ответы левой. Easy не упрощает правую руку: эта сложность остаётся.", "Hand independence means retaining each hand's rhythm within a shared pulse. Dense RH notes must not hurry LH octaves and responses. Easy does not simplify the RH, so that challenge remains."),
        "example": tr("08-mashqda o‘ng qo‘l reference’i bilan 07-mashqning 100 ta chap qo‘l notasi birlashtirilgan. 60 BPM va tekis o‘quv ritmi ishlatilgan. Asosiy ikki variantning o‘ng qo‘li esa aynan bir xil 1049 ta nota: tovush balandligi, boshlanishi, davomiyligi va velocity qiymatlari mos.", "Упражнение 08 соединяет правый reference со 100 нотами левой из упражнения 07, при 60 BPM и ровном учебном ритме. В двух основных вариантах правая полностью одинакова: 1049 нот с одинаковой высотой, началом, длительностью и velocity.", "Drill 08 combines the RH reference with all 100 LH notes from drill 07 at 60 BPM and even study timing. The two main variants share exactly 1049 RH notes, matching pitch, onset, duration and velocity."),
        "listen": tr("Avval o‘ng qo‘l kuyining yuqori yo‘lini kuylang. Keyin birga keladigan tayanchlarni tinglang; ular orasida o‘ng qo‘l davom etishi mumkin. Jo‘rlikni pasaytirib, melodiya ravshanligini solishtiring.", "Сначала напойте верхнюю линию правой. Затем услышьте общие опоры; между ними правая может продолжаться. Смягчите сопровождение и сравните ясность мелодии.", "Sing the upper RH line first. Then hear the shared landmarks; the RH may continue between them. Soften the accompaniment and compare the melody's clarity."),
        "method": tr("Player tezligini zarur bo‘lsa pasaytiring. Avval bitta taktni eshitib, chap qo‘lni sanang. Keyin ikki taktni qo‘shing. Easy ning asl vaqtli sekin bosqichidan Hard ning sekin bosqichiga o‘tganda o‘ng qo‘l bir xil qoladi; faqat yangi chap qo‘l yo‘liga diqqat bering.", "При необходимости снизьте скорость. Сначала прослушайте такт, считая левую, затем соедините два. При переходе от медленного Easy к медленному Hard правая остаётся прежней: внимание направьте на новый путь левой.", "Lower player speed if needed. Hear one bar while counting the LH, then join two. Moving from slow Easy source timing to slow Hard leaves the RH unchanged; focus on the new LH route."),
        "pitfall": tr("Bir qo‘l adashsa, ikkinchisini tezlashtirib yetib olishga urinmang. Ikki qo‘ldagi barcha notalarni bir xil kuchda bosish kuy va jo‘rlik farqini yo‘qotadi. 08-mashqdagi tekis ritm final rubatoning nusxasi emas.", "Не пытайтесь догнать ошибку ускорением другой руки. Одинаковая сила всех нот стирает разницу мелодии и сопровождения. Ровный ритм упражнения 08 не копирует финальное rubato.", "Do not catch up with an error by speeding the other hand. Equal force on every note erases melody/accompaniment balance. Drill 08's even rhythm does not copy the final rubato."),
        "ready": tr("Ikki qo‘l bilan kirish va chiqishlarni bilaman; Hard ga o‘tganda o‘ng qo‘lni boshqatdan o‘rganmay, chapdagi farqni ajrata olaman.", "Знаю вступления обеих рук и при переходе к Hard выделяю изменения левой, не переучивая правую.", "I know both hands' entries and can isolate the LH changes in Hard without relearning the RH."),
        "related": ["voicing", "syncopation", "practice"], "path": "together",
    },
    {
        "code": "full-verse", "file": "09_Kuplet_asl_LH_45bpm.mid", "bpm": 45, "window": VERSE,
        "title": tr("To‘liq kuplet: mashqdan asl ijroga", "Полный куплет: от упражнения к исполнению", "Full verse: from drill to performance"),
        "concept": tr("Rubato — jumla ichidagi vaqtning ifodali erkinligi. Uni tasodifiy tezlashish bilan aralashtirmang: jumla yo‘nalishi saqlanadi. 09-mashq nota yo‘lini teng o‘n oltitalikda ochib beradi; keyingi bosqichlar Hard faylining barcha asl kirish va davomiyliklariga qaytadi.", "Rubato — выразительная свобода времени внутри фразы, а не случайное ускорение: направление фразы сохраняется. Упражнение 09 раскрывает путь нот ровными шестнадцатыми; следующие этапы возвращают все исходные атаки и длительности Hard.", "Rubato is expressive flexibility within a phrase, not random speeding: the phrase retains direction. Drill 09 exposes the route in even sixteenths; the following stages restore Hard's complete original attacks and holds."),
        "example": tr("09-mashq Dm | Dm | B♭ | A kupletining asl chap qo‘l tovushlarini 45 BPM da beradi, sakkiz taktli o‘quv ko‘rinishida. Birinchi guruh D3–A3–D4–F4–E4–D4–F4–G4. Keyingi kontekst 0:15.71–0:29.46 dagi to‘rt manba taktini oladi: vaqtlar 60%, 80%, so‘ng 100% nisbatda qaytadi.", "Упражнение 09 даёт исходные звуки левой Dm | Dm | B♭ | A при 45 BPM в восьмитактовой учебной форме. Первая группа D3–A3–D4–F4–E4–D4–F4–G4. Контекст берёт четыре исходных такта 0:15.71–0:29.46: сначала 60%, затем 80% и 100% времени исполнения.", "Drill 09 presents the original LH pitches of Dm | Dm | B♭ | A at 45 BPM in an eight-bar study form. Its first group is D3–A3–D4–F4–E4–D4–F4–G4. Context stages use the four source bars at 0:15.71–0:29.46, returning through 60%, 80% and 100% performance speed."),
        "listen": tr("Dm dan B♭ va A ga o‘tishda shakl o‘zgaradi, lekin past tayanch va yuqori javob mantiqi qoladi. Asl vaqtga qaytganda barcha tenglashtirilgan notalarni metronomdek bir xil bosishga urinmang; jumla oqimini eshiting.", "При Dm→B♭→A форма меняется, но логика нижней опоры и верхнего ответа остаётся. Вернувшись к исходному времени, не выравнивайте всё как метроном: слушайте поток фразы.", "Dm→B♭→A changes the shape but retains the low-landmark/upper-response logic. When returning to source timing, do not force every attack into metronomic equality; hear the phrase flow."),
        "method": tr("Avval 09-ni chap qo‘lda ko‘rib, yangi akkord oldidan yo‘lni ayting. Hard chap qo‘lni 60% da, keyin ikkala qo‘lni 60% da ulang. Ravon bo‘lgach 80% va 100% ni solishtiring. Butun kuy yo‘nalishida 2-part, o‘tish va yakunni alohida tekshirish davom etadi.", "В упражнении 09 проговорите путь перед новым аккордом. Соедините левую Hard на 60%, затем обе руки на 60%. При плавности сравните 80% и 100%. Путь всей пьесы отдельно проверяет вторую часть, переходы и окончание.", "In drill 09, name the route before each new chord. Connect Hard LH at 60%, then both hands at 60%. Once fluent, compare 80% and 100%. The whole-piece paths separately review part two, transitions and the ending."),
        "pitfall": tr("Asosiy paketda CC64 faqat pedalni o‘chiradi, ba’zi klavishalar MIDI bo‘yicha uzun ushlangan. Hammasini fizik barmoq bilan ushlab qolish shart emas. Pedalni qo‘shsangiz yangi bass yoki uyg‘unlikda eski jarangni tozalang; bu qo‘llanma tavsiyasi, fayldan tiklangan pedal emas.", "В основных файлах CC64 только выключает педаль, а некоторые MIDI-клавиши удерживаются долго. Не обязательно физически держать всё пальцами. Добавляя педаль, очищайте старое звучание при новом басе или гармонии; это рекомендация, а не восстановленная из файла педаль.", "The main files contain only sustain-off CC64 messages, though some MIDI keys are held for a long time. You need not physically retain every tone with a finger. If adding pedal, clear the previous resonance at a new bass or harmony; that is guidance, not a pedal curve recovered from the file."),
        "ready": tr("To‘liq kupletni sekin ikkala qo‘lda ravon ulayman; tekis mashq va asl rubato farqini tushunaman.", "Плавно соединяю полный куплет медленно двумя руками и понимаю разницу упражнения и исходного rubato.", "I can connect the full verse slowly with both hands and explain the difference between drill timing and source rubato."),
        "related": ["phrasing", "pedal", "practice"], "path": "full",
    },
]


def excerpt_stage(key, suffix, variant, hand, start, end, speed):
    variant_name = "Easy" if variant == "easy" else "Hard"
    hand_label = tr("Chap qo‘l", "Левая рука", "Left hand") if hand == "left" else tr("Ikki qo‘l", "Две руки", "Both hands")
    return {
        "id": f"{key}:stage:{suffix}", "_asset_key": f"{key}:stage:{suffix}",
        "title": {lang: f"{variant_name} · {label} · {speed}%" for lang, label in hand_label.items()},
        "instruction": tr(
            f"{variant_name} manbaning shu bo‘lagi {speed}% tezlikda. " + ("Faqat chap qatlamni kuzating; keyin ikki qo‘l bosqichiga o‘ting." if hand == "left" else "Ikkala qo‘l birga. Tayanchlarni va kuy–jo‘rlik balansini saqlang."),
            f"Этот отрывок {variant_name} на {speed}% скорости. " + ("Следите только за левой, затем переходите к обеим рукам." if hand == "left" else "Обе руки вместе. Сохраняйте опоры и баланс мелодии с сопровождением."),
            f"This {variant_name} source passage at {speed}% speed. " + ("Follow the left layer, then move to the both-hands stage." if hand == "left" else "Both hands together. Retain landmarks and melody/accompaniment balance.")),
        "source_speed_percent": speed, "composition_variant_id": variant, "_source_variant": variant,
        "_generator": {"start": start, "end": end, "selection": {"left": "all", "right": [] if hand == "left" else "all"},
                       "speed_percent": speed, "title": f"All in | {variant_name} | {suffix}"},
    }


def source_window(start, end):
    return {"start_seconds": start, "end_seconds": end,
            "transformation": tr("Alohida o‘quv MIDI → Easy kontekst → Hard ijro", "Отдельный учебный MIDI → контекст Easy → исполнение Hard", "Separate study MIDI → Easy context → Hard performance")}


@lru_cache(maxsize=1)
def all_in_items():
    result = []
    for plan in PLANS:
        key = "lesson:all-in:" + plan["code"]
        start, end = plan["window"]
        stages = [{
            "id": key + ":stage:drill", "_asset_key": key,
            "_package_file": "Mashqlar/" + plan["file"], "tempo_bpm": plan["bpm"],
            "composition_variant_id": "hard" if plan["path"] in {"hard", "full"} else "easy",
            "title": tr(f"O‘quv mashqi · {plan['bpm']} BPM", f"Учебный пример · {plan['bpm']} BPM", f"Study drill · {plan['bpm']} BPM"),
            "instruction": tr(
                "To‘rt tayyorlov urishini ichingizda sanang, keyin notalar kiradi. Bu alohida o‘quv MIDI: ritm tekis va ushlashlar qisqaroq. Playerdagi 100% ko‘rsatilgan BPM ga teng; zarur bo‘lsa sekinlating.",
                "Внутренне отсчитайте четыре подготовительные доли, затем вступают ноты. Это отдельный учебный MIDI с ровным ритмом и короткими удержаниями. 100% плеера соответствует указанному BPM; при необходимости замедлите.",
                "Count four preparation beats internally before the notes enter. This separate study MIDI uses even rhythm and shorter holds. The player's 100% equals the stated BPM; slow it if needed."),
        }]
        if plan["path"] in {"easy", "both"}:
            stages.append(excerpt_stage(key, "easy-left", "easy", "left", start, end, 100))
        if plan["path"] in {"easy", "together"}:
            stages.append(excerpt_stage(key, "easy-together", "easy", "both", start, end, 80 if plan["path"] == "easy" else 60))
        if plan["path"] in {"hard", "both", "full"}:
            stages.append(excerpt_stage(key, "hard-left", "hard", "left", start, end, 60))
        if plan["path"] != "easy":
            stages.append(excerpt_stage(key, "hard-slow", "hard", "both", start, end, 60))
            if plan["path"] in {"together", "full"}:
                stages.append(excerpt_stage(key, "hard-flow", "hard", "both", start, end, 80))
            stages.append(excerpt_stage(key, "hard-original", "hard", "both", start, end, 100))
        labels = [tr("Avval tushunib oling", "Сначала разберитесь", "Understand first"),
                  tr("Aniq nota misoli", "Точный нотный пример", "Exact note example"),
                  tr("Nimani eshitasiz?", "Что услышать?", "What to listen for"),
                  tr("Qanday mashq qilamiz?", "Как заниматься?", "How to practise"),
                  tr("Adashmaslik uchun", "Как избежать ошибки", "Avoid this mistake")]
        result.append({
            "id": key, "kind": "lesson", "_composition": "all-in", "title": plan["title"],
            "subtitle": tr(f"{plan['bpm']} BPM · alohida MIDI mashqi", f"{plan['bpm']} BPM · отдельный MIDI", f"{plan['bpm']} BPM · separate MIDI drill"),
            "intro": plan["concept"], "category": "harmony" if plan["code"] in {"chord-shapes", "prechorus"} else "coordination",
            "goals": ["understanding", "accuracy", "fluency"], "level": None, "minutes": 12,
            "explanation": [{"title": label, "text": plan[field]} for label, field in zip(labels, ["concept", "example", "listen", "method", "pitfall"])],
            "steps": [{"title": s["title"], "instruction": s["instruction"]} for s in stages],
            "stages": stages, "source": source_window(start, end), "ready_when": plan["ready"],
            "related_ids": ["theory:" + topic for topic in plan["related"]],
            **({"fingering": plan["fingering"]} if plan.get("fingering") else {}),
        })
    _, parsed = package_source("All_In_Plus5_Full.mid")
    duration = parsed["metadata"]["duration_seconds"]
    windows = [
        ("first-part", 0, 127.9243, tr("Birinchi part va o‘tish", "Первая часть и переход", "First part and transition")),
        ("second-part", 127.9243, 239.924744, tr("Ikkinchi part va o‘tish", "Вторая часть и переход", "Second part and transition")),
        ("outro", 239.924744, duration, tr("Yakuniy instrumental", "Заключительный инструментал", "Final instrumental")),
        ("chorus-join", 60.876048, 94.871006, tr("Tayyorlovdan naqarotga", "Из подготовки в припев", "From preparation to the chorus")),
        ("complete", 0, duration, tr("Butun asar: Easy dan Hard ga", "Вся пьеса: от Easy к Hard", "Complete piece: Easy to Hard")),
    ]
    for code, start, end, title in windows:
        key = "journey:all-in:" + code
        stages = [excerpt_stage(key, "easy-left", "easy", "left", start, end, 80),
                  excerpt_stage(key, "easy-together", "easy", "both", start, end, 80),
                  excerpt_stage(key, "hard-left", "hard", "left", start, end, 60),
                  excerpt_stage(key, "hard-slow", "hard", "both", start, end, 60),
                  excerpt_stage(key, "hard-flow", "hard", "both", start, end, 80),
                  excerpt_stage(key, "hard-original", "hard", "both", start, end, 100)]
        stages[0]["_asset_key"] = key
        if code == "complete":
            for i, asset, filename in [
                (0, "composition:all-in:lh-easy", "All_In_Plus5_LH_Only_Easy.mid"),
                (1, "composition:all-in:easy", "All_In_Plus5_Easy_LH.mid"),
                (2, "composition:all-in:lh-hard", "All_In_Plus5_LH_Only_Full.mid"),
                (5, "composition:all-in:original", "All_In_Plus5_Full.mid"),
            ]:
                # The first key still supplies the stable journey identity; only
                # its stage points to the pinned, unchanged full-length file.
                stages[i]["_asset_key"] = asset
                stages[i]["_reuse_original"] = True
                stages[i]["source_speed_percent"] = 100
                hand = tr("Chap qo‘l", "Левая рука", "Left hand") if i in {0, 2} else tr("Ikki qo‘l", "Две руки", "Both hands")
                variant = "Easy" if i < 2 else "Hard"
                stages[i]["title"] = {lang: f"{variant} · {label}" for lang, label in hand.items()}
                stages[i]["instruction"] = tr(
                    "Butun fayl asl holida, manbaning 100% tezligida. Player tezligini pasaytirishingiz mumkin. Chap qo‘l yakka fayllarida kirishning dastlabki 15.7 soniyasi sukut; bu joy o‘ng qo‘lga tegishli.",
                    "Полный неизменённый файл на 100% скорости источника. Можно замедлить плеер. В файлах только левой первые 15,7 секунды тихие: вступление принадлежит правой.",
                    "The complete unchanged file at 100% source speed. You can lower player speed. LH-only files are silent for the first 15.7 seconds because the introduction belongs to the RH.")
        intro = tr("Bir xil kuy va tempo xaritasida avval Easy jo‘rlikni, so‘ng Hard ning to‘liq chap qo‘lini ulang. Darslarda o‘rgangan akkord xaritasi ikkala variantga ham tegishli.", "На одной мелодии и карте темпа соедините сначала Easy, затем полную левую Hard. Изученная карта аккордов общая для обоих вариантов.", "With the same melody and tempo map, connect Easy first and then Hard's full LH. The harmonic map learned in the lessons applies to both variants.")
        result.append({
            "id": key, "kind": "journey", "_composition": "all-in", "title": title,
            "subtitle": tr(f"{int(start)//60}:{int(start)%60:02d}–{int(end)//60}:{int(end)%60:02d} · Easy → Hard", f"{int(start)//60}:{int(start)%60:02d}–{int(end)//60}:{int(end)%60:02d} · Easy → Hard", f"{int(start)//60}:{int(start)%60:02d}–{int(end)//60}:{int(end)%60:02d} · Easy → Hard"),
            "intro": intro, "category": "coordination", "goals": ["fluency", "musicality"], "level": None, "minutes": 15,
            "explanation": [
                {"title": tr("Umumiy xarita", "Общая карта", "Shared map"), "text": intro},
                {"title": tr("Qismlar va vaqt", "Части и время", "Sections and timing"), "text": tr(
                    "0:15.71 — kuplet; 0:42.22 — tayyorlov; 1:07.04 va 1:31.85 — naqarotlar; 2:07.92 — ikkinchi part; 3:59.92 — yakuniy instrumental. Kuplet Dm–Dm–B♭–A xaritasiga qaytadi. Naqarotdagi bir takt ichida ham uyg‘unlik almashishi mumkin. Boshlanishdagi 1/8, qisqa 2/4 va yakun yaqinidagi 9/8 sabab hamma joyni 4/4 deb sanamang.",
                    "0:15.71 — куплет; 0:42.22 — подготовка; 1:07.04 и 1:31.85 — припевы; 2:07.92 — вторая часть; 3:59.92 — инструментальное окончание. Куплет возвращает Dm–Dm–B♭–A; в припеве гармония меняется и внутри такта. В файле есть начальные 1/8, короткие 2/4 и 9/8 ближе к концу: не считайте всё как 4/4.",
                    "0:15.71: verse; 0:42.22: preparation; 1:07.04 and 1:31.85: choruses; 2:07.92: part two; 3:59.92: instrumental ending. The verse returns to Dm–Dm–B♭–A; chorus harmony can change inside a bar. The file includes opening 1/8, short 2/4 and later 9/8, so do not count everything as 4/4.")},
                {"title": tr("Ravonlikni tekshirish", "Проверка плавности", "Check continuity"), "text": tr(
                    "Qayerda adashsangiz, playerni shu joydan biroz oldinroqqa qo‘lda qaytaring. O‘tishdan oldingi va keyingi tayanchni birga o‘rganing. Easy dan Hard ga o‘tganda o‘ng qo‘l o‘zgarmaydi; chapdagi yangi notalarni ajrating. Tezlikdan oldin erkin harakat va kuy ravshanligini tekshiring.",
                    "При ошибке вручную вернитесь немного раньше. Изучайте опоры до и после перехода вместе. При Easy→Hard правая не меняется: выделите новые ноты левой. До ускорения проверьте свободное движение и ясность мелодии.",
                    "When you stumble, manually seek slightly earlier. Learn the landmarks before and after a transition together. Easy→Hard leaves the RH unchanged: isolate the added LH notes. Check free movement and melodic clarity before increasing speed.")},
            ],
            "steps": [{"title": s["title"], "instruction": s["instruction"]} for s in stages],
            "stages": stages, "source": source_window(start, end),
            "ready_when": tr("Kirish, o‘tish va yakunda yo‘nalishni yo‘qotmayman; Hard da ham kuy jo‘rlikdan ravshan.", "Не теряю направление на вступлении, переходах и окончании; мелодия ясна и в Hard.", "I retain direction through entries, joins and ending, with a clear melody in Hard too."),
            "related_ids": ["lesson:all-in:easy-verse", "lesson:all-in:chorus-together", "lesson:all-in:full-verse"],
        })
    return result
