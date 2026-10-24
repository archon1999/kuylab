"""Listening tasks and release evidence reviewed for every replacement lesson.

Anchors are (track, MIDI pitch, source onset seconds, key-hold seconds). They are
checked against the actual export before a course can be prepared or published.
"""
from .repertoire_courses import tr


def review(anchor, listen, pitfall):
    return dict(anchor=anchor, listen=listen, pitfall=pitfall)


YOUTH = {
    "octave-opening": review((0, 83, 0, .667),
        tr("B4 dan B5 gacha barcha oq-qora klavishlar orasidagi 12 qadamni sanang: nom bir xil, tovush balandligi boshqa. Avval B5–D6–C♯6–F♯5 ni kuylang. Pastki juft tovushlar qaytganda yuqori kuy tanishligicha qolsin. Juftlik ichidagi juda kichik kirish farqlari eksportda saqlangan; mashqda ularni ataylab katta ketma-ket zarbaga aylantirmang.",
           "От B4 до B5 — 12 соседних полутоновых шагов: имя то же, высота другая. Пропойте B5–D6–C♯6–F♯5. Когда вернутся нижние звуки пар, верхняя мелодия должна остаться узнаваемой. Небольшие расхождения атак сохранены в экспорте; не превращайте их в намеренно раздельные удары.",
           "Count twelve adjacent semitone steps from B4 to B5: the name repeats at a different height. Sing B5–D6–C♯6–F♯5 first. Keep that melody recognizable when the lower octave tones return. Tiny attack offsets remain in the export; do not exaggerate them into deliberately separate strikes."),
        tr("Oktava yetmasa qo‘lni kuch bilan cho‘zmang. Yuqori yo‘lni alohida chaling va qulay taqsimotni tanlang.", "Не растягивайте руку силой ради октавы. Играйте верх отдельно и выбирайте удобное распределение.", "Do not force an octave stretch. Study the upper line separately and choose a comfortable distribution.")),
    "broken-support": review((1, 45, 2.193, .510),
        tr("A2 bassidan keyin keladigan F♯3–A3–C♯4 ni eshiting: bu F♯ minor tarkibi, pastda A turibdi. Keyingi G2–D3–G3–D4 da faqat G va D nomlari bor; uchinchi tovush yetishmagani uchun uni avtomatik G major demang. Pastki qatlamning to‘liq namunasini ikki marta tinglab, bass almashishini ichingizda ayting.",
           "После баса A2 услышьте F♯3–A3–C♯4: состав F♯ minor с A внизу. В G2–D3–G3–D4 встречаются только G и D; без терции это не доказательство G major. Дважды послушайте полный нижний слой, мысленно называя смену баса.",
           "After bass A2, hear F♯3–A3–C♯4: an F♯ minor collection with A below. G2–D3–G3–D4 contains only G and D; without a third it does not establish G major. Listen to the complete lower layer twice and name each bass change internally."),
        tr("A2 ni butun arpejio tugaguncha majburan ushlamang: yangi eksportda uning o‘z tugash vaqti bor.", "Не держите A2 насильно до конца арпеджио: в новом экспорте у него собственный момент отпускания.", "Do not force A2 to last through the entire arpeggio: the new export gives it its own release.")),
    "paired-thirds": review((0, 78, 13.312, .229),
        tr("D5–F♯5 da D–D♯–E–F–F♯ bo‘ylab to‘rtta yarim tonli qadam bor. C♯5–E5 da esa uchta. Tersiya nomi harflar oralig‘idan, katta-kichikligi yarim tonlardan keladi. Avval yuqori F♯–E–D yo‘lini eshiting, so‘ng pastki tovush qaytganda ham kuyga quloq soling. Har juftlikni bir xil qattiq qo‘l shakliga tiqmang.",
           "D5–F♯5 содержит четыре полутона, C♯5–E5 — три. Название «терция» определяется буквами, большая или малая — числом полутонов. Сначала слушайте верхнюю F♯–E–D, затем следите за ней при возвращении нижних тонов. Не удерживайте все пары одной жёсткой формой руки.",
           "D5–F♯5 spans four semitones; C♯5–E5 spans three. Letter names determine that these are thirds, while semitones distinguish major from minor. Hear the upper F♯–E–D first and keep following it when lower tones return. Do not impose one rigid hand shape on every pair."),
        tr("Har juftlikni alohida aksent qilish kuy chizig‘ini bo‘lib yuboradi. Pastki tovushni yumshoqroq oling.", "Отдельный акцент на каждой паре дробит мелодию. Смягчайте нижний звук.", "Accenting every pair breaks the line. Give the lower tone less prominence.")),
    "dense-dialogue": review((0, 71, 64.031, .510),
        tr("1:04 atrofida yuqoridagi B4 va pastki E2 bir-biriga yaqin vaqtda kiradi; keyingi yuqori B4 ostida esa bass o‘zgaradi. Avval ikki qatlamni alohida eshiting, keyin qaysi kirishlar yaqin, qaysilari navbat bilan kelishini ayting. To‘liq 60% bosqichda yangi nota izlashdan ko‘ra shu tartibni saqlashni birinchi maqsad qiling.",
           "Около 1:04 верхний B4 и нижний E2 вступают близко по времени, но под следующим B4 бас уже меняется. Послушайте слои отдельно, затем назовите близкие и последовательные вступления. В полном этапе на 60% сначала сохраняйте их порядок, а не гонитесь за следующей клавишей.",
           "Around 1:04, upper B4 and lower E2 enter close together, but the bass changes beneath the next B4. Hear each layer separately and identify close versus staggered attacks. In the complete 60% stage, prioritize their order rather than chasing the next key."),
        tr("Har yuqori notada chapni kutdirish asl ritmni o‘zgartiradi. Ikkala yo‘lning kirishlari mustaqil.", "Если левая ждёт каждую верхнюю ноту, исходный ритм меняется. У каждого слоя свои вступления.", "Making the left wait for every upper note changes the rhythm. Each layer has its own entries.")),
    "wide-register-move": review((0, 95, 151.750, 7.870),
        tr("B4→B6 ikki oktava yuqoriga, B3→B0 uch oktava pastga. Bu bir joyda barmoqlarni ochish emas, qo‘lni boshqa hududga ko‘chirishdir. 2:31,75 dagi uzun B6 yangi eksportda ham saqlangan: barcha uzun notalar xato emas. Oldingi qisqa B3–F♯4 ni unga qo‘shib cho‘zmasdan, ko‘chish va uzun kelishni ikki alohida vazifa sifatida mashq qiling.",
           "B4→B6 — две октавы вверх, B3→B0 — три вниз. Это перенос в другой регистр, а не растяжение пальцев на месте. Долгий B6 в 2:31,75 сохранён и в новом экспорте: не все длинные ноты ошибочны. Не продлевайте предшествующие короткие B3–F♯4; отдельно отработайте перенос и удержание нового звука.",
           "B4→B6 moves two octaves up, while B3→B0 moves three down. Move to another register rather than stretching in place. The long B6 at 2:31.75 remains in the new export: not every long note is wrong. Keep the preceding short B3–F♯4 separate, then practise the move and the long arrival."),
        tr("Oldingi mayda tovushlarni uzun B bilan birga ushlab qolmang; har birining note-off’i alohida.", "Не удерживайте предыдущие короткие звуки вместе с долгим B: у каждого своё отпускание.", "Do not carry the preceding short tones into the long B; each has its own release.")),
    "opening-return": review((1, 33, 179.312, .062),
        tr("Qaytishda kuy nomlarini bilishning o‘zi yetmaydi: pastki A va G tayanchlarini, keyin yakunga chiqish yo‘lini ham taning. So‘nggi A1 juda qisqa; yozuv buni uzun tugallovchi akkordga aylantirmaydi. Butun namuna oxirigacha bir marta eshiting, so‘ng aynan fayl tugashini mashq qiling. Bu eksport tashqarisidagi ijro haqida xulosa bermaydi.",
           "В возвращении узнавайте не только мелодию, но и нижние опоры A/G и выход к концу. Последний A1 очень короткий: запись не превращает его в долгий заключительный аккорд. Прослушайте пример до конца и отработайте именно окончание файла. Это не утверждение о материале за пределами экспорта.",
           "Recognize the returning melody together with its A/G bass landmarks and the route to the end. The final A1 is very short; this export does not turn it into a long closing chord. Hear the example through once, then practise the actual file ending. This makes no claim about material outside the export."),
        tr("Qisqa yakun notalarini «chiroyli tugasin» deb o‘zboshimchalik bilan uzaytirmang.", "Не удлиняйте короткие финальные ноты лишь ради более привычного окончания.", "Do not lengthen the short ending notes merely to make a more familiar ending.")),
}

STAR = {
    "singing-opening": review((0, 76, 3.026, 2.479),
        tr("E5 0:03 atrofida kelgach, chapdagi E4 va A3 kabi yangi kirishlarni tinglang: o‘ngda yangi zarba bo‘lmasa ham jo‘rlik yuradi. Bitta uzun tovush ostidagi bir necha voqeani eshitish qo‘llar mustaqilligidir. Avval yuqorini kuylang, keyin pastkini qo‘shing. Yangi eksportda E5 taxminan 2,48 soniya; uni keyingi kuy notasigacha sun’iy cho‘zish talab qilinmaydi.",
           "После E5 около 0:03 слушайте новые нижние E4 и A3: сопровождение движется без новой атаки сверху. Умение слышать несколько событий под одним звуком развивает независимость рук. Пропойте верх, затем добавьте низ. В новом экспорте E5 длится около 2,48 секунды; искусственно тянуть его до следующей мелодической ноты не требуется.",
           "After E5 around 0:03, hear lower E4 and A3 entering without another upper attack. Following several events beneath one tone develops hand independence. Sing the upper line, then add the lower layer. E5 lasts about 2.48 seconds in the new export; it need not be artificially extended to the next melody note."),
        tr("Legato degani barcha bloklarni bir-biriga zo‘rlab tekkizish emas. Yozuvdagi bo‘shatish va jimliklarni ham saqlang.", "Legato не означает насильно соединять все блоки. Сохраняйте записанные отпускания и промежутки.", "Legato does not mean forcing every block to touch the next. Respect the recorded releases and gaps.")),
    "minor-and-major-shapes": review((1, 50, 0, 1.078),
        tr("D–F–A ni klavishlarda bir oktava ichida toping: D→F uch, F→A to‘rt yarim ton. A–C♯–E da tartib 4+3 bo‘ladi. Bu qo‘l ostida solishtirish uchun alohida tahlil; MIDI mashqda esa asl keng joylashuv va ketma-ket kirishlar saqlangan. C♯ bass bo‘lib kelishi A major tarkibining eng past tovushi har doim A bo‘lishi shart emasligini ko‘rsatadi.",
           "Найдите D–F–A в одной октаве: 3+4 полутона; у A–C♯–E — 4+3. Это отдельное сравнение на клавишах: MIDI сохраняет исходное широкое расположение и последовательные атаки. Бас C♯ показывает, что самый нижний звук состава A major не обязан быть A.",
           "Find D–F–A within one octave: 3+4 semitones, compared with 4+3 in A–C♯–E. This is a separate keyboard comparison; the MIDI retains its original wide spacing and attack order. Bass C♯ shows that A major's lowest tone need not be A."),
        tr("Uch tovushni taqqoslash mashqini originalning aynan bir vaqtdagi akkordi deb qabul qilmang.", "Не принимайте упражнение на сравнение трезвучий за точную одновременную атаку оригинала.", "Do not mistake the triad comparison exercise for a simultaneous chord attack in the original.")),
    "rising-and-falling-line": review((0, 76, 36.510, .516),
        tr("E–F orasida qora klavish yo‘q va bu yarim ton; F–G hamda G–A orasida bittadan qora klavish bor, ular butun ton. Avval ko‘tarilishdagi G ning boshqalardan uzunroq ekanini, keyin qaytishdagi D ning vaqtini eshiting. Nota nomlari o‘xshash qadamlardan iborat bo‘lsa ham, har birini teng davomiylikda chalish jumlani o‘zgartiradi.",
           "E–F — полутон без чёрной клавиши между ними; F–G и G–A — целые тоны. Услышьте более долгий G на подъёме, затем длительность D в конце спуска. Поступенное движение не означает равных длительностей: их выравнивание изменит фразу.",
           "E–F is a semitone with no intervening black key; F–G and G–A are whole tones. Hear the longer G on the rise and the D at the end of the descent. Stepwise movement does not imply equal durations: evening them out changes the phrase."),
        tr("A ga yetgach qaytuvchi G ni erta bosmang; burilishda ham ichki vaqt davom etadi.", "Не торопите G после вершины A: внутреннее время продолжается и на повороте.", "Do not rush G after the peak A; keep inner time through the change of direction.")),
    "high-register-entry": review((0, 89, 53.859, .214),
        tr("F4 hududidan keyin F6 ni oldindan ko‘ring. Bir xil harf ikki oktava uzoqda bo‘lishi mumkin: bu 24 yarim ton. Yuqori kirishdan keyin A5, D6 va yana F6 kelishini ham eshiting; faqat birinchi cho‘qqini yodlash yetarli emas. Pastki A3 yurishi ko‘chish vaqtida to‘xtamasligi uchun ikkala qo‘l sekin bosqichida yo‘llarni birlashtiring.",
           "После области F4 заранее найдите F6: одинаковая буква может находиться на две октавы, или 24 полутона, выше. Услышьте также A5, D6 и следующий F6; одного первого высокого звука мало. Соединяйте линии в медленном этапе, сохраняя движение нижнего A3 во время переноса.",
           "Locate F6 early after the F4 area: the same letter can be two octaves, or 24 semitones, apart. Also hear A5, D6 and the next F6 rather than memorizing only the first high arrival. Combine the lines slowly while keeping the lower A3 movement going through the shift."),
        tr("Yuqoriga chiqishni avtomatik kuchli urg‘uga aylantirmang; registr va ovoz kuchi ikki xil narsa.", "Подъём регистра не требует автоматического сильного акцента: высота и громкость различаются.", "A higher register does not automatically need a strong accent; height and loudness differ.")),
    "return-balance": review((0, 76, 123.208, .245),
        tr("Avval 0:36 dagi E–F–G–A yo‘lini eslang, keyin shu darsdagi qaytishni eshiting. Bu yerda qo‘shimcha E va G4 kirishlari bor: tanish kuy aynan bir xil nota-naqsh degani emas. Yuqori yo‘lni ichingizda kuylab, yangi bass kirganida ham davom ettiring. To‘liq 60% namunada jo‘rlikni yumshoqroq chalib ovozlar balansini tekshiring.",
           "Вспомните E–F–G–A около 0:36 и сравните с возвращением здесь. Добавлены вступления E и G4: знакомая мелодия не означает совершенно одинаковый рисунок. Мысленно пойте верх при смене баса. В полном примере на 60% смягчайте сопровождение, проверяя баланс голосов.",
           "Recall E–F–G–A around 0:36 and compare this return. Additional E and G4 attacks show that a familiar melody need not have an identical note pattern. Keep singing the upper line internally through bass changes. In the complete 60% example, soften the accompaniment and check the balance."),
        tr("Oldingi bo‘limdagi qo‘l harakatini ko‘r-ko‘rona ko‘chirmang; qaytishning kirishlari va bassi tekshiriladi.", "Не переносите движения из прежнего раздела вслепую: проверьте вступления и бас возвращения.", "Do not copy the earlier hand movement blindly; check this return's attacks and bass.")),
    "ending-space": review((1, 38, 198.771, .490),
        tr("D2 ning yangi ushlanishi taxminan 0,49 soniya: keyin A2–D3–F3–A3 ga yo‘l ochiladi. D–F–A tarkibi bir necha registrga yoyilsa ham tanish minor rangni saqlaydi. So‘nggi A3 taxminan 7,40, D6 esa 4,95 soniya ushlanadi: qisqa bass bilan haqiqiy uzun yakun tovushlarini alohida ajrating.",
           "Новый D2 удерживается около 0,49 секунды, затем идут A2–D3–F3–A3. Распределённый по регистрам состав D–F–A сохраняет узнаваемую минорную окраску. Последние A3 и D6 длятся примерно 7,40 и 4,95 секунды: различайте короткий бас и действительно долгие заключительные тоны.",
           "The new D2 hold is about 0.49 seconds, followed by A2–D3–F3–A3. D–F–A retains its minor colour across registers. The final A3 and D6 last about 7.40 and 4.95 seconds: distinguish the short bass from the genuinely long closing tones."),
        tr("D2 ni yakungacha ushlab qolish ham, so‘nggi A3/D6 ni erta uzish ham yangi eksportga mos emas.", "Ни удержание D2 до конца, ни раннее снятие последних A3/D6 не соответствуют новому экспорту.", "Neither holding D2 to the end nor cutting the final A3/D6 short matches the new export.")),
}

TEARS = {
    "opening-line": review((0, 72, .005, 1.370),
        tr("Birinchi C5 keyingi C5 dan taxminan uch baravar uzunroq. Bir xil klavish takrorlansa ham bu ikki mustaqil kirish: birinchisini tugatib, qayta bosishga imkon bering. D5→G4 pastga kvinta, undan B4 va E♭5 orqali yuqoriga qaytiladi. Avval nomlar bilan yo‘nalishni kuylang, keyin qisqa va uzun tovushlarni farqlab chaling.",
           "Первый C5 примерно втрое длиннее следующего C5. Это две самостоятельные атаки одной клавиши: завершите первую и подготовьте повторное нажатие. D5→G4 — квинта вниз, затем B4 и E♭5 ведут обратно вверх. Пропойте направление с названиями, затем сохраняйте различие коротких и долгих звуков.",
           "The first C5 is about three times as long as the next C5. They are separate attacks on one key: finish the first and allow the repeated press. D5→G4 moves down a fifth, then B4 and E♭5 lead upward again. Sing the direction with note names before playing the contrasting lengths."),
        tr("Takroriy C ni uzluksiz ushlab turish yangi kirishni yo‘qotadi; hammasini qisqa chalish esa jumla ritmini buzadi.", "Непрерывное удержание C скрывает повторную атаку; одинаково короткие ноты тоже меняют ритм фразы.", "Holding C continuously hides its repeated attack; making every note short also changes the phrase.")),
    "changing-third": review((1, 63, .943, .844),
        tr("C dan E♭ gacha C–C♯–D–E♭: uch yarim ton; E gacha yana bittasi qo‘shiladi. G ni o‘zgartirmasdan faqat shu o‘rta tovushni solishtiring. Player D♯ yozsa, bu darsdagi E♭ bilan ayni klavish. Bu enharmonik nomlash: yozilishi boshqacha, ushbu pianinoda balandligi bir xil. Pastki namunada aynan E♭4 va E4 paydo bo‘lishini tinglang.",
           "От C до E♭ — три полутона; до E добавляется ещё один. Не меняя G, сравните только средний тон. Надпись D♯ в плеере означает ту же клавишу, что E♭ в уроке: это энгармонические названия одной высоты на данном фортепиано. Услышьте конкретные появления E♭4 и E4 в нижнем примере.",
           "C to E♭ spans three semitones; reaching E adds one more. Keep G unchanged and compare just the middle tone. The player's D♯ is the same key as this lesson's E♭: enharmonic names for the same pitch on this piano. Listen for the actual E♭4 and E4 entries in the lower example."),
        tr("Bitta E kirishidan butun asarning tonalligi haqida xulosa chiqarmang; bu yerda mahalliy tovush tarkibi solishtiriladi.", "Не определяйте тональность всей пьесы по одному E: здесь сравнивается местный звуковой состав.", "Do not infer the whole piece's key from one E; this compares local pitch collections.")),
    "eight-note-theme": review((0, 83, 49.505, .411),
        tr("B–C–D–E♭ va E♭–D–C yo‘llarini alohida kuylang, keyin C6→A♭5→B♭5 bilan ulang. C6 dan A♭5 ga tushish katta tersiya — to‘rt yarim ton; uni yonma-yon qadam deb o‘ylamang. Birinchi bosqich juftliklarning yuqorisini ajratadi. Pastki juftlar qaytganda ham shu sakkiz tovushli yo‘lni eshitish asosiy vazifa.",
           "Пропойте B–C–D–E♭ и обратное E♭–D–C, затем соедините с C6→A♭5→B♭5. C6→A♭5 — большая терция вниз, четыре полутона, а не соседний шаг. Первый этап выделяет верх пар; при возвращении нижних тонов продолжайте слышать эту восьмизвучную линию.",
           "Sing B–C–D–E♭ and its E♭–D–C return, then connect C6→A♭5→B♭5. C6→A♭5 descends a major third, four semitones, rather than one adjacent step. The first stage exposes the tops of pairs; keep hearing that eight-note line when lower tones return."),
        tr("E♭ cho‘qqisini kutib oldingi D ni qisqartirmang, qaytishda esa C→A♭ masofasini oldindan ko‘ring.", "Не укорачивайте D в ожидании вершины E♭; заранее готовьте расстояние C→A♭ на спуске.", "Do not shorten D while anticipating the E♭ peak; prepare the C→A♭ distance on the descent.")),
    "middle-accompaniment": review((1, 60, 96.042, .479),
        tr("Pastki qatlamni eshitib C4–E4 dan F3–C4–F4 ga o‘tishni taning. Qo‘l pastga ko‘chganda tovushlar soni ko‘paysa ham umumiy vaqt tezlashishi shart emas. Avval siyrak basslar orasini eslab qoling, keyin to‘liq chap namunada ular orasiga kiradigan tovushlarni joylang. Ikki qo‘l 60% bosqichi aynan shu qo‘shimcha yukni sekinroq birlashtirish uchun.",
           "Узнайте переход C4–E4 к F3–C4–F4 в нижнем слое. Больше нот при переносе вниз не требует ускорять общее время. Запомните расстояния между редкими басами, затем расположите между ними остальные тоны полного левого примера. Полный этап на 60% помогает спокойно объединить эту дополнительную нагрузку.",
           "Hear the lower transition from C4–E4 to F3–C4–F4. More notes during a downward move do not require faster overall time. Learn the sparse bass spacing, then place the complete left-hand tones between those landmarks. The full 60% stage lets you combine that extra load slowly."),
        tr("Har jo‘rlik notasiga urg‘u berish yuqori kuyni yashiradi. Pastki qatlamni tekis va yumshoqroq olib boring.", "Акцент на каждом звуке сопровождения закрывает мелодию. Играйте низ ровнее и мягче.", "Accenting every accompaniment note obscures the melody. Keep the lower layer even and softer.")),
    "returning-theme-balance": review((0, 83, 135.703, .422),
        tr("Qaytuvchi B5–C6–D6–E♭6 yo‘lini ichingizda kuylab, pastdagi G3–D4–B3 tovushlarini eshiting. Ikki qatlam balandlikda yaqinlashsa, kuy chizig‘i ayniqsa muhim bo‘ladi. Avval pastkini jim tasavvur qilib yuqorini chaling, keyin to‘liq 60% namunada jo‘rlikni qo‘shing. Kuy sizga hali ham ravshan eshitilmasa, tezlikni oshirmang.",
           "Мысленно пойте возвращение B5–C6–D6–E♭6, слыша нижние G3–D4–B3. При сближении регистров мелодическая линия особенно важна. Сначала играйте верх, представляя низ, затем добавьте сопровождение в полном примере на 60%. Не повышайте скорость, пока мелодия теряется.",
           "Sing the returning B5–C6–D6–E♭6 internally while hearing lower G3–D4–B3. A clear melodic line matters especially when registers approach each other. Play the upper part while imagining the lower, then combine them at 60%. Do not speed up while the melody remains obscured."),
        tr("Tanish yuqori yo‘l pastki qatlamni avtomatik takrorlashga sabab bo‘lmasin; jo‘rlikning o‘zgarishini kuzating.", "Знакомый верх не повод автоматически повторять прежний низ: следите за изменившимся сопровождением.", "A familiar upper line is not a reason to replay the old bass automatically; follow the changed accompaniment.")),
    "last-semitone": review((0, 83, 188.568, 5.396),
        tr("B5 taxminan 3:08,57 da boshlanib 5,40 soniya davom etadi, keyingi C6 esa 3:14 atrofida keladi. Bu yerda uzun B haqiqatan yangi faylda bor. Yakunda yuqoridagi E♭5 va C6 pastki C3–G3–C4 bilan bir tarkibni turli registrlarga yoyadi. Avval B ning tugashi bilan yakuniy kirish orasini eshiting, keyin butun yakunni sekin chaling.",
           "B5 начинается примерно в 3:08,57 и длится 5,40 секунды, следующий C6 приходит около 3:14. Этот долгий B действительно есть в новом файле. Финальные E♭5/C6 и нижние C3–G3–C4 распределяют один состав по регистрам. Услышьте отпускание B и следующий вход, затем медленно соедините окончание.",
           "B5 begins around 3:08.57 and lasts 5.40 seconds; the next C6 arrives around 3:14. That long B is genuinely present in the new file. Final E♭5/C6 and lower C3–G3–C4 spread one collection across registers. Hear B's release and the following entry before combining the ending slowly."),
        tr("B ni qisqa notalar kabi erta qo‘yib yubormang; shu bilan birga uning vaqtini C6 dan keyinga uzaytirmang.", "Не снимайте B раньше как короткую ноту, но и не продлевайте его за вступление C6.", "Do not release B early as if it were short, or extend it beyond C6's arrival.")),
}

MY_MEMORY = {
    "staggered-entry": review((1, 67, 0, 1.182),
        tr("Uchta tayanchni ketma-ket ayting: pastki G4 → yuqori E5 → pastki C3. E5 ning kelishi G4 ni qayta bosish belgisi emas; C3 esa E5 bilan bir vaqtda boshlanmaydi. Birga yangrash bilan birga boshlanishni ajrating. To‘liq 60% bosqichda quloq bilan shu uch nuqtani tanish, keyin ularning orasidagi tovushlarni joylash muhim.",
           "Назовите три опоры по очереди: нижний G4 → верхний E5 → нижний C3. Приход E5 не требует повторять G4, а C3 не начинается одновременно с E5. Различайте совместное звучание и совместную атаку. В полном этапе на 60% узнавайте эти три точки и размещайте остальные тоны между ними.",
           "Name three landmarks in order: lower G4 → upper E5 → lower C3. E5's arrival does not require re-striking G4, and C3 does not begin with E5. Distinguish sounding together from attacking together. At the complete 60% stage, recognize these three points and fit the other tones between them."),
        tr("Ikkala qo‘l borligi uchun har boshlanishni bir vaqtdagi akkordga aylantirmang.", "Не превращайте все начала в одновременные аккорды лишь потому, что участвуют обе руки.", "Do not turn every entry into a simultaneous chord merely because both hands are involved.")),
    "flowing-left": review((1, 40, 16.276, .385),
        tr("C3–G3–C4 dan keyin E2 ga tushish chapning yangi yo‘lini ochadi. C3→G3 kvinta, G3→C4 kvarta; keyingi pastga ko‘chish bundan ancha keng. Avval bass nuqtalarini, keyin ular orasidagi yoylarni eshiting. E2 qisqa ushlanadi: klavishni bo‘shatish keyingi G3 hududiga erkin tayyorlanish imkonidir.",
           "После C3–G3–C4 перенос к E2 открывает новый нижний путь. C3→G3 — квинта, G3→C4 — кварта; следующий перенос вниз намного шире. Услышьте басовые точки, затем дуги между ними. Короткое удержание E2 позволяет свободно подготовиться к области G3.",
           "After C3–G3–C4, the drop to E2 opens a new lower route. C3→G3 is a fifth and G3→C4 a fourth; the next downward move is much wider. Hear bass points before their connecting arcs. E2's short hold frees you to prepare the G3 area."),
        tr("Arpejio tugaguncha eski bassni ushlab qo‘lni cho‘zib qotirmang. Yangi fayldagi release’ni kuzating.", "Не зажимайте растянутую руку, удерживая старый бас до конца арпеджио. Следуйте отпусканию нового файла.", "Do not lock a stretched hand by holding the old bass through the whole arpeggio. Follow the new release.")),
    "theme-return": review((0, 79, 134.240, .349),
        tr("Boshlanishdagi G5 takrorlari bilan shu joydagi G5 larni taqqoslang: birinchisi qisqaroq, keyingisi uzunroq bo‘lishi mumkin. Takroriy klavishni yetarlicha bo‘shatib yangi zarbani hosil qiling. So‘ng C5 takrorlaridan F5–E5 yo‘liga o‘tishni kuylang. Asosiy xotira tayanchi faqat harf nomi emas, kirish va ushlashlarning birgalikdagi naqshidir.",
           "Сравните повторения G5 в начале и здесь: короткий звук может сменяться более долгим. Достаточно отпускайте клавишу для новой атаки. Затем пропойте переход от повторных C5 к F5–E5. Опора памяти — не только названия, а совместный рисунок атак и удержаний.",
           "Compare repeated G5s here with the opening: a shorter tone can be followed by a longer one. Release the key sufficiently for a fresh attack. Then sing the move from repeated C5s to F5–E5. Memorize the combined pattern of attacks and holds rather than letter names alone."),
        tr("Har takrorni kuchliroq bosish shart emas. Qayta kirish aniq bo‘lsin, lekin jumla bo‘linmasin.", "Не нужно усиливать каждый повтор. Новая атака должна быть ясной, но не дробить фразу.", "Do not make every repeat louder. Make the new attack clear without fragmenting the phrase.")),
    "high-arc": review((0, 86, 161.349, 1.130),
        tr("D5 va D6 bir nomning bir oktava farqli jufti; keyingi C6/C5 ham shunday. Bu juftlarning yuqori yo‘lini alohida kuylang. G6 gacha kengayish notalarni bitta joyda cho‘zib olishni talab qilmaydi: yangi hududga ko‘chib, ichki tovushlarni yumshoqroq qo‘shing. To‘liq namuna sekinlashganda ham yuqori yo‘l ajralib eshitilishi kerak.",
           "D5/D6 — один звук в разных октавах, как следующие C6/C5. Пропойте верхнюю линию пар отдельно. Достижение G6 не требует растянуть всё из одной позиции: переноситесь в новый регистр и мягче добавляйте внутренние тоны. Верх должен оставаться различимым и в медленном полном примере.",
           "D5/D6 share a name one octave apart, as do the following C6/C5. Sing the tops of those pairs separately. Reaching G6 does not require stretching everything from one position: move to the new register and soften inner tones. The upper line should remain distinct in the slow complete example."),
        tr("Baland notani kuchliroq urish bilan kuy yo‘nalishini almashtirmang; registr o‘zgarishi aksent ko‘rsatmasi emas.", "Не заменяйте направление мелодии более сильными ударами по высоким нотам: регистр не задаёт акцент автоматически.", "Do not replace melodic direction with harder high-note strikes; a register change is not an automatic accent.")),
    "busy-final-section": review((1, 48, 207.984, .391),
        tr("3:27,98 dagi C3 dan G3–C4 yo‘liga quloq soling: keyin juft ichki tovushlar va qisqa qaytishlar ko‘payadi. Birinchi bosqich bass manzillarini yodlatadi, ikkinchisi ularning orasidagi barcha pastki kirishlarni qaytaradi. Ikkala qo‘lni qo‘shishda 60% ga qaytish ataylab qilingan: notalar ko‘payadi, shu sabab tezlikni vaqtincha pasaytirish foydali.",
           "От C3 в 3:27,98 следуйте к G3–C4: затем учащаются парные внутренние тоны и короткие возвраты. Первый этап знакомит с басовыми пунктами, второй возвращает все нижние вступления. Возврат к 60% при соединении рук намеренный: нот становится больше, поэтому полезно временно снизить скорость.",
           "Follow C3 at 3:27.98 into G3–C4, then the growing number of paired inner tones and short returns. The first stage establishes bass destinations; the second restores every lower attack. Returning to 60% when combining hands is deliberate: more notes justify a temporary speed reduction."),
        tr("Oldingi bir qo‘lli tezlikni ikki qo‘lga majburan ko‘chirmang. To‘liq sekin bosqichdan boshlang.", "Не переносите прежнюю одноручную скорость на две руки силой. Начните с полного медленного этапа.", "Do not force the previous one-hand speed onto both hands. Start with the complete slow stage.")),
    "independent-ending": review((0, 67, 268.422, 3.625),
        tr("Yuqoridagi E4/C5 ushlashlari taxminan 4:21,37 da tugaydi, yangi G4 esa 4:28,42 da keladi. Ularning orasida pastki qatlam harakat qiladi. Demak yuqori jimlik butun musiqa to‘xtadi degani emas. Avval faqat pastkini eshitib vaqtni saqlang, so‘ng yuqori tugash va qaytishni shu davomiy yo‘l ichiga joylang.",
           "Верхние E4/C5 заканчиваются примерно в 4:21,37, новый G4 появляется в 4:28,42. Между ними движется нижний слой: тишина сверху не означает остановку всей музыки. Сначала сохраняйте время, слушая низ, затем расположите отпускание и возвращение верха внутри этого непрерывного движения.",
           "Upper E4/C5 holds end around 4:21.37, while the new G4 arrives at 4:28.42. The lower layer moves between them: silence above does not stop the whole music. First keep time while hearing the lower part, then place the upper release and return within that continuing route."),
        tr("Yuqoridagi bo‘shliqni oldingi C5 ni yetti soniya ortiqcha ushlab berkitmang; yangi eksport uni tugatgan.", "Не закрывайте паузу сверху лишними семью секундами удержания C5: новый экспорт уже завершил его.", "Do not fill the upper gap with seven extra seconds of held C5; the new export has already released it.")),
}

PREMONITION = {
    "descending-bass": review((1, 45, 11.312, .156),
        tr("C3 dan B2, B♭2, A2, A♭2 va G2 ga tushganda har safar eng yaqin pastki klavish keladi. G2→F2 bundan farqli ravishda ikki yarim ton. A2 va A♭2 yangi faylda juda qisqa: ular keyingi bass kelguncha ushlanmaydi. Shuning uchun bass kirishi, uning tugashi va navbatdagi kirishni kutish uchta alohida vazifa bo‘ladi.",
           "C3→B2→B♭2→A2→A♭2→G2 каждый раз спускается к ближайшей клавише; G2→F2 отличается целым тоном. A2 и A♭2 в новом файле очень короткие, их не держат до следующего баса. Разделяйте начало баса, его отпускание и ожидание следующего вступления.",
           "C3→B2→B♭2→A2→A♭2→G2 descends to the nearest key each time; G2→F2 instead spans a whole tone. A2 and A♭2 are very short in the new file, not held until the next bass. Separate the bass attack, its release and the wait for the next entry."),
        tr("Basslar orasidagi bo‘shliqni har safar oldingi notani cho‘zib to‘ldirmang. Yuqori naqsh shu oraliqda davom etadi.", "Не заполняйте каждый промежуток продлением предыдущего баса. Верхний рисунок продолжает движение.", "Do not fill every gap by lengthening the previous bass. The upper pattern keeps moving through that space.")),
    "broken-triads": review((0, 75, 0, .474),
        tr("C–E♭–G ni tanish uchun ijro aynan C dan boshlanishi shart emas: bu yerda E♭–G–C–E♭ tartibi keladi. Keyingi D–G–B tarkibida G majorning G–B–D tovushlari bor. Uchlikning tarkibi, eng past tovushi va tovushlarning kirish tartibi uch xil savol. Avval uch nomni aniqlang, so‘ng aynan yozuvdagi tartibda chaling.",
           "Состав C–E♭–G узнаётся и без начала с C: здесь порядок E♭–G–C–E♭. Следующие D–G–B содержат звуки G major, G–B–D. Состав трезвучия, самый нижний тон и порядок вступлений — разные вопросы. Сначала назовите три звука, затем сыграйте их в порядке записи.",
           "C–E♭–G need not begin with C to be recognizable: here the order is E♭–G–C–E♭. The following D–G–B contains G major's G–B–D. A triad's collection, its lowest tone and its attack order are separate questions. Identify the three names, then play the recorded order."),
        tr("Bir rangdagi to‘rt kirishni avtomatik to‘rt tovushli yangi akkord deb atamang: ayrim nota nomlari takrorlangan.", "Не называйте четыре атаки одного цвета новым четырёхзвучным аккордом автоматически: некоторые имена повторяются.", "Do not call four same-colour attacks a new four-note chord automatically; some pitch names repeat.")),
    "expanding-lower-texture": review((1, 48, 30.516, .490),
        tr("Kirishdagi yakka C bassini bu darsdagi C3–G3–E♭4–G3–E♭4 bilan solishtiring. Birinchisi tayanch, ikkinchisi uning atrofida harakatli faktura. G3↔E♭4 yo‘lini tayyorlash yangi C3 kelishini kechiktirmasligi kerak. Avval pastkini to‘liq, so‘ng ikki qo‘lni 60% da eshitib, basslar orasidagi vaqtni bir xil saqlang.",
           "Сравните отдельный C вступления с C3–G3–E♭4–G3–E♭4 здесь. Первый — опора, второй создаёт движущуюся фактуру вокруг неё. Подготовка G3↔E♭4 не должна задерживать новый C3. Слушайте полный низ, затем обе руки на 60%, сохраняя расстояния между басами.",
           "Compare the opening's single C bass with C3–G3–E♭4–G3–E♭4 here. One is a landmark; the other creates a moving texture around it. Preparing G3↔E♭4 should not delay the next C3. Hear the complete lower layer, then both hands at 60%, preserving bass-to-bass spacing."),
        tr("Ichki tovushlar qo‘shilganda har biri alohida jumla bo‘lib qolmasin; butun yo‘lni bir nafasdek eshiting.", "Не превращайте каждый внутренний тон в отдельную фразу: слушайте весь путь одним движением.", "Do not turn every inner tone into a separate phrase; hear the whole route as one movement.")),
    "semitone-figure": review((0, 72, 39.865, .182),
        tr("C5 markaziga ikki tomondan keladigan B4 va C♯5 ni solishtiring. B→C oq-oq, C→C♯ oq-qora bo‘lsa ham ikkalasi bitta yarim tonli qadam. Avval C ni, so‘ng uning pastki va yuqori qo‘shnisini toping. Qisqa naqshdan keyingi uzun C larni eshiting: qo‘shni klavishlar orasidagi masofa bir xil bo‘lsa ham davomiylik har doim bir xil emas.",
           "Сравните B4 и C♯5 по обе стороны от C5. B→C — белая-белая, C→C♯ — белая-чёрная, но оба расстояния равны полутону. Найдите C, затем соседей снизу и сверху. Услышьте долгие C после короткого рисунка: одинаковое расстояние не означает одинаковую длительность.",
           "Compare B4 and C♯5 on either side of C5. B→C uses two white keys and C→C♯ a white/black pair, yet both span one semitone. Find C and its neighbours first. Hear the long Cs after the short figure: equal pitch distances do not imply equal durations."),
        tr("Qora klavish bor-yo‘qligiga qarab yarim tonni aniqlamang. B–C ham eng yaqin ikki klavishdir.", "Не определяйте полутон по наличию чёрной клавиши: B–C тоже ближайшие соседи.", "Do not identify a semitone by the presence of a black key: B–C are adjacent too.")),
    "restart-after-space": review((0, 67, 184.927, .818),
        tr("Yuqoridagi qisqa takrorlardan keyin D5 cho‘ziladi, so‘ng G4 qayta kiradi. Oldingi tovushning tugashi bilan yangi boshlanishni ikkita alohida nuqta sifatida belgilang. Pastda C3–B2–B♭2 yo‘li qaytishi kirish uchun ikkinchi tayanch bo‘ladi. 60% to‘liq namunada shu tayanchni eshitib G4 ga tayyor turing, ammo uni erta bosmang.",
           "После коротких повторов сверху тянется D5, затем возвращается G4. Отметьте окончание прежнего звука и новое вступление как разные точки. Возвращение нижней C3–B2–B♭2 даёт вторую опору. В полном примере на 60% услышите её и подготовьте G4, не нажимая раньше времени.",
           "Short upper repeats lead to a longer D5 and the return of G4. Treat the old tone's release and the new attack as separate points. Returning lower C3–B2–B♭2 provides another landmark. At 60% full texture, use that landmark to prepare G4 without pressing early."),
        tr("Qo‘l tayyor bo‘lgani tovushni darhol bosish kerak degani emas. Tayyorlanish va ijro vaqti ajratiladi.", "Готовая рука не означает немедленное нажатие: подготовка и момент исполнения различаются.", "A prepared hand is not a reason to press immediately; preparation and performance time are distinct.")),
    "closing-rise": review((1, 48, 220.125, 8.964),
        tr("Yakuniy C3 yangi faylda ham taxminan 8,96 soniya ushlanadi. Uning ustida C5–E♭5–G5/C6–E♭6–G6 yo‘li yoyiladi: bir minor uchlik tovushlari oktavalarda takrorlanmoqda. Har baland tovushni aloqasiz yangi akkord deb qabul qilish o‘rniga C, E♭ va G oilalarini taning. Shu haqiqiy uzun bassni oldingi qisqa basslar bilan adashtirmang.",
           "Финальный C3 и в новом файле удерживается около 8,96 секунды. Над ним разворачивается C5–E♭5–G5/C6–E♭6–G6: звуки одного минорного трезвучия повторяются по октавам. Узнавайте семейства C, E♭ и G, а не несвязанные аккорды. Отличайте этот действительно долгий бас от предыдущих коротких.",
           "The final C3 still lasts about 8.96 seconds in the new file. Above it, C5–E♭5–G5/C6–E♭6–G6 spreads one minor triad across octaves. Recognize the C, E♭ and G families rather than unrelated chords. Distinguish this genuinely long bass from the earlier short ones."),
        tr("Uzun blok ko‘rindi deb uni o‘zboshimchalik bilan kesmang. Bu yakundagi C3/G6 davomiyligi manbada bor.", "Не обрезайте длинный блок произвольно: длительности финальных C3/G6 присутствуют в источнике.", "Do not arbitrarily trim a long block: the closing C3/G6 holds are present in the source.")),
}

MEMORIES = {
    "sparse-opening": review((0, 72, 0, .521),
        tr("C5 ni, keyin pastroq E4 javobini tinglang; keyingi B4 dan so‘ng ham E4 keladi. Yuqori rangning o‘zi «faqat kuy» degani emas: bitta eksport qatlamida baland kuy va pastki javob almashishi mumkin. Harf bilan oktava raqamini birga o‘qing. C5 bilan E4 ni yangi bir akkordday bir paytda bosmasdan, navbatdagi ikki voqea sifatida chaling.",
           "Услышьте C5 и более низкий ответ E4; после следующего B4 снова приходит E4. Верхний цвет не всегда означает только мелодию: в одном экспортном слое чередуются высокая линия и низкий ответ. Читайте букву вместе с номером октавы. Играйте C5 и E4 по очереди, а не новым одновременным аккордом.",
           "Hear C5 and the lower E4 reply, then another E4 after B4. An upper colour need not mean melody alone: one export layer can alternate a high line and low replies. Read letter and octave together. Play C5 and E4 as successive events rather than a new simultaneous chord."),
        tr("Bo‘shliqni oldingi C yoki B ni cho‘zib yopmang; aks-sadoning o‘z boshlanish va tugashlari bor.", "Не закрывайте промежутки продлением прежнего C или B: у ответа свои начало и конец.", "Do not close the gaps by extending the earlier C or B; each reply has its own attack and release.")),
    "a-minor-support": review((1, 64, 12.104, .484),
        tr("E4–C4–A3 yo‘lini pastdan yuqoriga qayta nomlasangiz A–C–E hosil bo‘ladi. A→C uch, C→E to‘rt yarim ton, shu sabab minor uchligi. Qaysi tovush birinchi kelishi tarkib nomini o‘zgartirmaydi; qaysi biri bass bo‘lishi esa joylashuvga ta’sir qiladi. Keyin yuqoridagi uzun C5/E5 ostida shu uch ismning navbatini eshiting.",
           "Назовите E4–C4–A3 снизу вверх: получится A–C–E. A→C содержит три полутона, C→E — четыре, образуя минорное трезвучие. Первый вступивший тон не меняет состав, хотя бас влияет на расположение. Затем услышьте очередность этих имён под более долгими верхними C5/E5.",
           "Name E4–C4–A3 from low to high: A–C–E. A→C has three semitones and C→E four, forming a minor triad. The first attack does not change the collection, though the bass affects its arrangement. Then hear those names alternating beneath longer upper C5/E5 tones."),
        tr("Uchlikni tushunish uchun birga bosib ko‘rish mumkin, ammo MIDI mashqning ketma-ket ritmini saqlang.", "Для понимания можно сравнить трезвучие одновременно, но в MIDI-упражнении сохраняйте последовательный ритм.", "You may compare a simultaneous triad to understand it, but retain the MIDI exercise's successive rhythm.")),
    "low-register-arrival": review((1, 40, 77.964, 1.089),
        tr("C4 hududidan E2 ga tushishda oldin yangi klavishni ko‘z bilan toping. E2 juda past bo‘lgani uchun uni avtomatik qattiqroq bosish shart emas. Qo‘lni ko‘chirishdan oldin tugagan notani bo‘shating; boshqa qatlamdagi E4 shu payt davom etishi mumkin. Har ikki qatlamning alohida tugash vaqtini saqlash qo‘lni ortiqcha bog‘lab qo‘ymaslikka yordam beradi.",
           "До переноса из области C4 к E2 найдите новую клавишу взглядом. Низкий E2 не требует автоматически более сильного удара. Отпустите закончившуюся ноту перед переносом; E4 в другом слое может продолжаться. Собственные моменты отпускания каждого слоя помогают не связывать руки лишним удержанием.",
           "Locate E2 visually before moving down from the C4 area. Its low register does not automatically require a harder strike. Release the finished note before moving; E4 in the other layer may continue. Separate release times help avoid tying the hands together through unnecessary holding."),
        tr("Keyingi joyni topish uchun oldingi notani erta kesmang yoki yangi bassni kechiktirmang. Tempni pasaytiring.", "Не обрезайте прежний звук и не задерживайте новый бас ради поиска клавиши. Снизьте темп.", "Do not cut the old note or delay the bass while searching for the key. Reduce the tempo.")),
    "two-upper-voices": review((0, 81, 87.286, .354),
        tr("Birinchi namunada A4 olib tashlangan, shuning uchun A5–G5–F5–E5–D5 ochiq eshitiladi. Ikkinchisida A4 asl vaqtlariga qaytadi. Yuqori yo‘lni ichingizda kuylab, A4 larni undan yumshoqroq chaling. Bitta qo‘l ichida ovoz ajratish degani yangi notalarni uzaytirish emas; ikki balandlik yo‘lining kuchi va kirishlarini mustaqil boshqarishdir.",
           "В первом примере A4 убран, открывая A5–G5–F5–E5–D5. Во втором A4 возвращается в исходные моменты. Мысленно пойте верх и смягчайте повторные A4. Разделение голосов одной рукой не требует удлинять ноты: отдельно управляйте громкостью и вступлениями двух высотных линий.",
           "The first example removes A4, exposing A5–G5–F5–E5–D5. The second restores A4 at its original times. Sing the upper line internally and soften the repeated A4s. Voicing within one hand is not about lengthening notes; independently control the prominence and attacks of the two pitch lines."),
        tr("Har A4 ni urg‘u bilan bosish yuqori kuyni yashiradi; yuqori notani kutib A4 larni tezlashtirmang.", "Акценты на каждом A4 скрывают верх; не ускоряйте A4 в ожидании следующей мелодической ноты.", "Accenting every A4 hides the upper line; do not rush the A4s while waiting for its next note.")),
    "upper-peak": review((0, 88, 132.427, 1.005),
        tr("E5/E6 juftidan keyin E4 keladi. E6→E4 ikki oktava pastga: nom o‘zgarmaydi, lekin klavish joyi butunlay boshqa. Keyingi F4 davomni boshlaydi, demak baland cho‘qqi jumlaning oxiri emas. Avval E6 kelishi, tugashi va E4 ga o‘tishni alohida eshiting; keyin pastki C3 kirishlari bilan 60% tezlikda birlashtiring.",
           "После пары E5/E6 следует E4. E6→E4 — две октавы вниз: имя прежнее, клавиша в другом регистре. Следующий F4 продолжает фразу, поэтому высокая вершина не означает конец. Услышьте отдельно атаку E6, отпускание и переход к E4, затем соедините с нижними C3 на 60%.",
           "The E5/E6 pair is followed by E4. E6→E4 descends two octaves: the name stays but the key lies in another register. F4 continues the phrase, so the high peak is not its ending. Hear E6's attack, release and move to E4 before combining lower C3 entries at 60%."),
        tr("E6 ni E4 bosilgandan keyin ham ushlab qolib qo‘lni taranglashtirmang; yangi faylda uning tugashi ko‘rsatilgan.", "Не зажимайте E6 после нажатия E4: новый файл показывает его собственное окончание.", "Do not lock the hand by holding E6 after E4 arrives; the new file shows its own release.")),
    "descending-continuation": review((0, 74, 175.219, .583),
        tr("E–F–E–D–C–B yo‘lida yarim tonli E–F va C–B ni, butun tonli D–C ni ajrating. Avval harflarni ayting, keyin qaysi tovush qisqa, qaysisi uzunligini tinglang. Fayl oxirida yuqori D5 tugaganidan keyin ham pastki so‘nggi tovush ozroq davom etadi. Butun ijroni faqat yuqoridagi oxirgi notaga qarab to‘xtatmang.",
           "В E–F–E–D–C–B различайте полутоновые E–F/C–B и целотоновый D–C. Назовите звуки, затем услышьте различия длительностей. В конце последний нижний звук немного продолжается после отпускания верхнего D5. Не останавливайте полное исполнение, ориентируясь только на последнюю верхнюю ноту.",
           "In E–F–E–D–C–B, distinguish semitone E–F/C–B from whole-tone D–C. Name the tones, then hear their differing lengths. Near the end, the last lower tone briefly outlasts upper D5. Do not stop the complete performance merely because its final upper note has finished."),
        tr("Mavjud faylga qo‘shimcha yakuniy akkord qo‘shmang. Pastki so‘nggi kirish va uning tugashini ham eshiting.", "Не добавляйте к файлу выдуманный заключительный аккорд. Услышьте последнюю нижнюю атаку и её отпускание.", "Do not add an invented final chord to the file. Hear the last lower attack and its release too.")),
}

REVIEWS = {"youth": YOUTH, "star": STAR, "tears": TEARS,
           "my-memory": MY_MEMORY, "premonition": PREMONITION, "memories": MEMORIES}


def reviewed_anchor(code, plan, parsed):
    evidence = REVIEWS[code][plan["code"]]
    track, pitch, onset, hold = evidence["anchor"]
    matches = [event for event in parsed["events"]
               if event["track_index"] == track and event["pitch"]["midi"] == pitch
               and abs(event["onset_seconds"] - onset) < .002]
    if len(matches) != 1 or abs(matches[0]["duration_seconds"] - hold) > .002:
        raise ValueError(f"Review the release evidence for {code}/{plan['code']}.")
    if not plan["start"] <= matches[0]["onset_seconds"] < (plan["end"] or parsed["metadata"]["duration_seconds"]):
        raise ValueError(f"Release evidence outside lesson: {code}/{plan['code']}.")
    return matches[0]


def review_blocks(code, plan, parsed):
    evidence = REVIEWS[code][plan["code"]]
    event = reviewed_anchor(code, plan, parsed)
    names = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"]
    pitch = event["pitch"]["midi"]
    name = names[pitch % 12] + str(pitch // 12 - 1)
    def stamp(time):
        return f"{int(time) // 60}:{time % 60:05.2f}"
    start = stamp(event["onset_seconds"])
    duration = f"{event['duration_seconds']:.2f}"
    end = stamp(event["onset_seconds"] + event["duration_seconds"])
    release = tr(
        f"Masalan, {name} asl ijroda {start} da boshlanadi, {duration} soniya davom etib {end} da tugaydi. Bu to‘liq manbadagi vaqt; sekin misolda boshlanish va ushlash bir xil nisbatda cho‘ziladi. Yangi eksportdagi blok uzunligi shu notaning note-on va note-off oralig‘i, pedal bilan uzaytirilgan dum emas. Klavishni aynan shu tugashga mos bo‘shating; keyingi nota yoki boshqa qo‘lning tovushi davom etishi mumkin.",
        f"Например, {name} в источнике начинается в {start}, длится {duration} с и заканчивается в {end}. Это время полного источника; в медленном примере начала и удержания растягиваются одинаково. Длина блока нового экспорта — промежуток note-on/note-off, а не удлинённый педальный хвост. Отпускайте клавишу в её момент окончания, даже если следующий звук или другая рука продолжает.",
        f"For example, source {name} begins at {start}, lasts {duration} s and releases at {end}. These are full-source times; slower examples scale attacks and holds equally. The new export's block length is the interval between note-on and note-off, not a pedal-extended tail. Release the key at its own ending even if the next note or the other hand continues.")
    return [
        {"title": tr("Shu ijrodagi joy", "Место в этом исполнении", "In this performance"), "text": plan["observation"]},
        {"title": tr("Nazariy ma’nosi", "Музыкальный смысл", "The musical idea"), "text": plan["theory"]},
        {"title": tr("Eshitib va klavishda tekshiring", "Проверьте слухом и на клавишах", "Listen and check on the keys"), "text": evidence["listen"]},
        {"title": tr("Nota qachon tugaydi?", "Когда заканчивается нота?", "When does this note release?"), "text": release},
        {"title": tr("Mashq usuli", "Как заниматься", "How to practise"), "text": plan["task"]},
        {"title": tr("Ko‘p uchraydigan xato", "Частая ошибка", "A common pitfall"), "text": evidence["pitfall"]},
    ]
