export const languages = ['uz', 'ru', 'en'];
export const origin = 'https://kuylab.uz';
export const reviewed = '2026-10-25';
export const paths = {
  home: { uz: '/', ru: '/ru/', en: '/en/' },
  piano: { uz: '/pianino-organish/', ru: '/ru/uchitsya-igrat-na-pianino/', en: '/en/learn-piano/' },
  theory: { uz: '/musiqa-nazariyasi/', ru: '/ru/teoriya-muzyki/', en: '/en/music-theory/' },
  exercises: {
    uz: '/pianino-mashqlari/',
    ru: '/ru/uprazhneniya-dlya-pianino/',
    en: '/en/piano-exercises/',
  },
  privacy: { uz: '/maxfiylik/', ru: '/ru/privacy/', en: '/en/privacy/' },
};

export const content = {
  uz: {
    title: 'Pianino chalishni o‘rganish va musiqa nazariyasi — KuyLab',
    description:
      'Sevgan kuyingizni pianinoda o‘rganing. KuyLab’da MIDI player, kompozitsiya darslari, qo‘l mashqlari va amaliy musiqa nazariyasi bir joyda.',
    home: 'Bosh sahifa',
    guidesLabel: 'Qo‘llanmalar',
    methodLabel: 'Qanday ishlaydi',
    open: 'Studiyani ochish',
    login: 'Studiyaga kirish',
    theme: 'Rang rejimini almashtirish',
    skip: 'Asosiy qismga o‘tish',
    headline: 'Sevgan kuyingizni pianinoda o‘rganing.',
    intro:
      'Tushayotgan MIDI notalari, kompozitsiya darslari va amaliy musiqa nazariyasi. Eshiting, tezlikni pasaytiring va o‘z pianinongizda mashq qiling.',
    preview: 'MIDI player ko‘rinishi',
    pauseMotion: 'Animatsiyani to‘xtatish',
    resumeMotion: 'Animatsiyani davom ettirish',
    previewAlt:
      'Chap va o‘ng qo‘l notalari pianino klavishlari tomon tushayotgan MIDI player tasviri',
    piece: 'Winter Sonata — Still',
    pieceMeta: '3:34 · 12 dars',
    methodTitle: 'Avval kuy. Keyin uning ichidagi bilim.',
    features: [
      [
        'Eshiting va kuzating',
        'Kompozitsiyani tushayotgan notalar bilan oching. Harfli nota nomlari va klavishlar qaysi tovush qachon chalinishini ko‘rsatadi. Tezlikni o‘zingizga moslang.',
      ],
      [
        'Darsni alohida o‘rganing',
        'Asarga oid nazariya va alohida MIDI mashqlari asosiy ijrodan ajratilgan. Chap qo‘l yoki soddaroq variantdan boshlab original ijroga yaqinlashing.',
      ],
      [
        'O‘z sur’atingizda mashq qiling',
        'Mustaqil qo‘l mashqlari va nazariya mavzularidan ham foydalaning. Bahosiz, majburiy rejasiz: qaysi ko‘nikma kerak bo‘lsa, shuni oching.',
      ],
    ],
    guidesTitle: 'Pianino oldida foydasi tegadigan bilim.',
    guidesIntro:
      'Klavishdan akkordgacha: qisqa tushuntirish, aniq misol va o‘zingiz sinab ko‘radigan mashq.',
    read: 'Qo‘llanmani o‘qish',
    faqTitle: 'Boshlashdan oldin',
    faqs: [
      [
        'KuyLab nima?',
        'KuyLab — pianino chalishni MIDI player, asarga oid darslar, mustaqil mashqlar va musiqa nazariyasi orqali o‘rganish uchun onlayn studiya. Har bir foydalanuvchining sozlamalari va shaxsiy faolligi alohida saqlanadi.',
      ],
      [
        'Pianinoni kompyuterga ulash kerakmi?',
        'Yo‘q. KuyLab’ni brauzerda ochib, playerga qarab o‘z pianinongizda mashq qilishingiz mumkin. USB yoki MIDI ulanish o‘rganishni boshlash sharti emas.',
      ],
      [
        'Oddiy nota yozuvini bilishim kerakmi?',
        'Boshlash uchun shart emas. Player C, D, E kabi harfli nomlar va klavishlarni ko‘rsatadi. Nazariyani alohida qo‘llanmalar va darslar orqali asta-sekin o‘rganish mumkin.',
      ],
      [
        'Kompozitsiya darslari va umumiy mashqlar nimasi bilan farq qiladi?',
        'Kompozitsiya darsi muayyan asarning ijrosiga tayyorlaydi. Mustaqil mashqlar esa qo‘llar koordinatsiyasi, ritm yoki akkord almashishi kabi ko‘nikmalarni bir asarga bog‘lamasdan rivojlantirish uchun.',
      ],
      [
        'Hozir qaysi asardan boshlash mumkin?',
        'Studiyada 38 ta kompozitsiya va 147 ta kompozitsiya darsi bor. Winter Sonata asarlari, Nino Rota, Yiruma, Chopin va Beethoven kompozitsiyalaridan boshlash mumkin. All in — Soundtrack uchun bitta playerda Easy va Hard variantlari, umumiy 9 ta dars mavjud. Asarga oid soddalashtirilgan mashqlar original ijroga bosqichma-bosqich tayyorlaydi.',
      ],
    ],
    about:
      'KuyLab mustaqil o‘rganuvchilar uchun yaratilgan. Maqsad — yoqtirgan kompozitsiyangiz ustida ishlashni nazariya va foydali mashqlar bilan bog‘lash. Bu avtomatik ijro bahosi yoki jonli ustoz darsi emas.',
    cta: 'Keyingi kuyingizni shu yerdan boshlang.',
    privacyLabel: 'Maxfiylik',
    sourceLabel: 'Ochiq kod',
    licensesLabel: 'Litsenziyalar',
    updated: 'Ko‘rib chiqilgan',
    back: 'Barcha qo‘llanmalar',
    guides: {
      piano: {
        title: 'Pianino chalishni o‘rganish: MIDI bilan qanday mashq qilish kerak?',
        description:
          'Tushayotgan MIDI notalaridan to‘g‘ri foydalanish: tinglash, tempni tanlash, qo‘llarni alohida o‘rganish va original ijroga o‘tish.',
        intro:
          'MIDI player qaysi klavish qachon va qancha vaqt chalinishini ko‘rsatadi. Unga shunchaki ergashish o‘rniga, kuyning ritmi va qo‘l harakatini tushunib mashq qilish foydaliroq.',
        sections: [
          [
            'Avval butun kompozitsiyani tinglang',
            'Ijroga qo‘shilmasdan bir marta eshiting. Melodiya qaytadigan joylarni, baland-past qismlarni va yakunni topishga harakat qiling. Keyingi mashqda eshitadigan narsangiz oldindan tanish bo‘ladi.',
          ],
          [
            'MIDI nimani ko‘rsatadi?',
            'MIDI audio yozuvning o‘zi emas: unda nota balandligi, boshlanishi, davomiyligi va velocity kabi ijro ma’lumotlari saqlanadi. Player bu ma’lumotlarni tovush va harakatga aylantiradi. Barmoqlash yoki musiqiy iborani qanday shakllantirish har bir MIDI faylda mavjud bo‘lavermaydi.',
          ],
          [
            'Shoshilmaydigan tempni tanlang',
            'Avval notalar orasida keyingi harakatni o‘ylashga vaqtingiz yetadigan tezlikda chaling. Masalan, original tezlikning 60 foizidan boshlash mumkin; bu majburiy raqam emas. Bir necha marta to‘xtamasdan chalganingizdan keyin tezlikni ozroq oshiring.',
          ],
          [
            'Qo‘llarning vazifasini ajrating',
            'Melodiya va jo‘r bo‘lishni alohida eshiting. Chap qo‘lning bas tovushlari qayerda almashishini, o‘ng qo‘ldagi ibora qayerda tugashini kuzating. Alohida MIDI mashqi soddalashtirilgan shaklni ko‘rsatishi mumkin; keyin shu ko‘nikmani to‘liq variantga olib o‘ting.',
          ],
          [
            'Klaviaturaga qaramasdan oldin yo‘nalishni biling',
            'Pianinodagi ikki qora klavish guruhining chapidagi oq klavish — C. Undan keyingi oq klavishlar D, E, F, G, A, B bo‘lib, yana C ga qaytadi. Nota nomini bilish ekrandagi rangni yodlashdan ko‘ra boshqa joylarda ham yo‘l topishga yordam beradi.',
          ],
          [
            'Ko‘rishdan eshitishga o‘ting',
            'Bir ibora tanish bo‘lgach, ekranga kamroq qarab ko‘ring. Keyingi tovushni ichingizda eshitib, shundan keyin chaling. So‘ng yozuvni yana tinglab, ritm va notalarning davomiyligini solishtiring. Maqsad faqat to‘g‘ri klavishni bosish bilan cheklanmaydi.',
          ],
        ],
        exercise: [
          'Hozir sinab ko‘ring',
          'C–D–E–F–G ni sekin, bir xil puls bilan chaling. Har bir notani bir xil vaqt ushlang. Keyin G–F–E–D–C qilib qayting. Bir maromni saqlay olsangiz, tovushlarni bir-biriga ravon ulashga e’tibor bering.',
        ],
      },
      theory: {
        title: 'Musiqa nazariyasi: pianino klavishlaridan boshlang',
        description:
          'Yarim ton va butun ton, intervallar, ritm, major va minor akkordlarni pianinoda tushunarli misollar orqali o‘rganing.',
        intro:
          'Musiqa nazariyasi — chalgan narsangizga nom berish va uning qanday ishlashini tushunish vositasi. Tushunchani o‘qigach, uni pianinoda eshitib ko‘rish ma’nosini aniqroq qiladi.',
        sections: [
          [
            'Yarim ton va butun ton',
            'Pianinoda yonma-yon ikki klavish orasidagi eng kichik masofa yarim ton deyiladi. C dan C♯ ga o‘tish — yarim ton. C dan D ga o‘tish ikkita yarim ton, ya’ni butun ton. E–F va B–C orasida qora klavish yo‘q: ular ham yarim ton masofada.',
          ],
          [
            'Interval — ikki tovush orasidagi masofa',
            'C–D sekunda, C–E tersiya, C–G kvinta deb ataladi. Nomdagi bosqich sonini harfli nota nomlari bilan, interval sifatini esa yarim tonlar soni bilan aniqlaymiz. C–E to‘rtta yarim tonli katta tersiya; C–E♭ uchta yarim tonli kichik tersiya.',
          ],
          [
            'Major va minor uch tovushlik',
            'C major akkordi C–E–G notalaridan tuziladi. Pastdan hisoblaganda katta tersiya va kichik tersiya keladi: 4 + 3 yarim ton. C minor esa C–E♭–G: 3 + 4 yarim ton. O‘rtadagi bitta nota o‘zgarishi rangni qanday almashtirishini tinglang.',
          ],
          [
            'Akkord aylanishi',
            'C–E–G notalarini E–G–C yoki G–C–E qilib joylashtirsangiz ham C major akkordi saqlanadi. Bu akkordning aylanishlari. Tovushlar tartibini o‘zgartirish qo‘lni keyingi akkordga yaqinlashtirishi va ovozlar harakatini ravonroq qilishi mumkin.',
          ],
          [
            'Puls va ritm bir narsa emas',
            'Puls — ichki bir marom, ritm esa shu marom ichidagi tovush va pauzalar naqshi. To‘rt zarb sanab, har zarbda bitta tovush chaling; keyin pulsni o‘zgartirmasdan bir zarbni ikkita teng tovushga bo‘ling. Davomiyliklar o‘zgarsa ham tayanch puls davom etadi.',
          ],
          [
            'Nazariyani kompozitsiyaga ulang',
            'O‘rganayotgan asaringizda bas qaysi tovushga o‘tishini va melodiya qaysi notada tinishini kuzating. Bir xil akkord yoki interval takrorlansa, uni alohida hodisa sifatida taniysiz. Barcha tovushlarga birdan nom topish shart emas: bitta tushunchani aniq eshitishdan boshlang.',
          ],
        ],
        exercise: [
          'Farqini eshiting',
          'C–E–G ni birga chaling. Keyin E ni yarim ton pasaytirib, C–E♭–G ni chaling. Pastki va yuqorigi tovushni o‘zgartirmang. Major va minor o‘rtasidagi farqni avval quloq bilan, keyin klavishlardagi masofa bilan tekshiring.',
        ],
      },
      exercises: {
        title: 'Pianino mashqlari: barmoqlar, ritm va qo‘llar koordinatsiyasi',
        description:
          'Besh barmoq, qo‘llar koordinatsiyasi va akkord almashishi uchun sodda pianino mashqlari. Qaysi ko‘nikmani qanday mashq qilishni biling.',
        intro:
          'Yaxshi mashqning aniq vazifasi bor. Tezlik, bir tekis tovush, ravon ulash va ikki qo‘lning moslashuvini bir vaqtda talab qilish o‘rniga, avval bittasiga e’tibor qarating.',
        sections: [
          [
            'Barmoqlar raqamini bilib oling',
            'Ikkala qo‘lda ham bosh barmoq 1, ko‘rsatkich 2, o‘rta 3, nomsiz 4 va jimjiloq 5 deb belgilanadi. C–D–E–F–G oq klavishlarida o‘ng qo‘l uchun 1–2–3–4–5, chap qo‘l uchun 5–4–3–2–1 sodda boshlang‘ich variant bo‘la oladi. Bu har bir asar uchun universal barmoqlash emas.',
          ],
          [
            'Besh barmoq bilan bir tekis tovush',
            'C dan G gacha yuqoriga, keyin orqaga chaling. Barcha tovushlar bir xil davomiylikda bo‘lsin. Tezlikni oshirishdan oldin notalar orasida tasodifiy uzilish yoki shoshilish yo‘qligini eshiting. Qaysi barmoq navbati kelishini oldindan biling.',
          ],
          [
            'Ikki qo‘lni birlashtirish',
            'Avval har bir qo‘l shu naqshni alohida bajarsin. Keyin ikkala qo‘l C–D–E–F–G ni bir xil yo‘nalishda chalsin. Bir xil nota nomiga mos barmoq raqamlari ikki qo‘lda turlicha bo‘lishini kuzating. Qo‘shganda ritm buzilsa, sekinroq tempga qayting.',
          ],
          [
            'Akkord almashish',
            'O‘ng qo‘lda C–E–G va C–F–A ni navbat bilan chaling. Har akkordni to‘rt zarb ushlang. Umumiy C notasi borligini va qolgan tovushlar qayerga siljishini kuzating. Keyin G–C–E kabi aylanishlarni sinab, qaysi joylashuv keyingi akkordga yaqinroq ekanini toping.',
          ],
          [
            'Ritmni klavishsiz ajrating',
            'Bir maromda to‘rtgacha sanang. Avval har sanoqda, keyin faqat birinchi va uchinchi sanoqda kaft bilan belgilang. Puls davom etsin. Ritmni ovoz chiqarib sanay olganingizdan keyin uni bitta klavishda, so‘ng nota naqshi bilan chaling.',
          ],
          [
            'Mashqni kuyga qaytaring',
            'Mustaqil mashq bir asarga bog‘lanmagan ko‘nikmani rivojlantiradi. Kompozitsiya darsi esa uning muayyan ijrosiga tayyorlaydi. Bir ko‘nikmani mashq qilgach, uni sevimli asaringizdagi mos joyda sinab ko‘ring. Natijani faqat tezlik bilan emas, boshqaruv va eshitiladigan farq bilan baholang.',
          ],
        ],
        exercise: [
          'Qisqa mashg‘ulot',
          'Bir daqiqa C–D–E–F–G ni bir tekis chaling. Keyingi daqiqada ikki qo‘lni qo‘shing. So‘ng ikkita akkordni sekin almashtiring. Har bosqichda bitta mezonni tanlang: ritm, tovushning tengligi yoki ravon harakat.',
        ],
      },
      privacy: {
        title: 'KuyLab’da maxfiylik va akkaunt ma’lumotlari',
        description:
          'KuyLab akkaunti, shaxsiy sozlamalar, faoliyat va brauzerda saqlanadigan fayllar haqida.',
        intro:
          'Ochiq qo‘llanmalarni akkauntsiz o‘qish mumkin. Shaxsiy studiya akkaunt orqali ishlaydi; bir foydalanuvchining profili, qaydlari va sozlamalari boshqasiga ko‘rsatilmaydi.',
        sections: [
          [
            'Akkaunt va shaxsiy holat',
            'Studiya login, parol xeshi va tanlagan ismingizni saqlaydi. Shaxsiy player sozlamalari, o‘rganish holati, sevimlilar va faoliyat ma’lumotlari akkauntingizga bog‘lanadi. Parol ochiq matn sifatida saqlanmaydi.',
          ],
          [
            'Cookie va mahalliy saqlash',
            'Akkauntga kirish va so‘rovlarni himoyalash uchun sessiya hamda CSRF cookie fayllari ishlatiladi. Til, rang rejimi va ayrim ijro sozlamalari brauzerda ham saqlanishi mumkin. Oflayn foydalanish uchun ilova fayllari va pianino namunalari keshlanadi.',
          ],
          [
            'Faoliyat statistikasi',
            'Statistika sayt ko‘rinib turgan yoki player ijro etgan vaqtga asoslanadi. Kamida besh daqiqalik faol tashriflar hisoblanadi. Bu pianinodagi haqiqiy ijroning avtomatik bahosi emas.',
          ],
          [
            'Hosting va ochiq sahifalar',
            'Sayt Cloudflare orqali yetkaziladi. Server xavfsizlik va nosozliklarni aniqlash uchun odatiy so‘rov jurnallarini yuritadi. Google Search Console ochiq sahifalarning qidiruvdagi ko‘rinishini o‘lchaydi; studiyadagi shaxsiy qaydlar sitemapga kiritilmaydi.',
          ],
          [
            'Savol va murojaatlar',
            'Texnik savol yoki ma’lumotlar bilan bog‘liq murojaat uchun sahifa oxiridagi ochiq kod havolasi orqali loyiha muammolari bo‘limidan foydalaning. Ochiq murojaatga parol yoki shaxsiy studiya ma’lumotlarini joylamang.',
          ],
        ],
      },
    },
  },
  ru: {
    title: 'Учиться играть на пианино и понимать музыку — KuyLab',
    description:
      'Учите любимые произведения на пианино с MIDI-плеером KuyLab: падающие ноты, уроки по композиции, упражнения и понятная теория музыки.',
    home: 'Главная',
    guidesLabel: 'Руководства',
    methodLabel: 'Как это работает',
    open: 'Открыть студию',
    login: 'Войти в студию',
    theme: 'Переключить тему',
    skip: 'Перейти к содержанию',
    headline: 'Учитесь играть то, что любите.',
    intro:
      'Падающие MIDI-ноты, уроки по произведениям и практическая теория музыки. Слушайте, снижайте темп и занимайтесь за своим пианино.',
    preview: 'Так выглядит MIDI-плеер',
    pauseMotion: 'Остановить анимацию',
    resumeMotion: 'Продолжить анимацию',
    previewAlt: 'Ноты левой и правой руки опускаются к клавиатуре пианино в MIDI-плеере',
    piece: 'Winter Sonata — Still',
    pieceMeta: '3:34 · 12 уроков',
    methodTitle: 'Начните с музыки. Разберитесь в том, как она устроена.',
    features: [
      [
        'Слушайте и наблюдайте',
        'Откройте произведение с падающими нотами. Буквенные обозначения и клавиши показывают высоту и момент звучания. Выберите удобный темп.',
      ],
      [
        'Изучайте уроки отдельно',
        'Теория по произведению и отдельные MIDI-упражнения не мешают основному плееру. Начните с одной руки или упрощённого варианта и переходите к оригиналу.',
      ],
      [
        'Занимайтесь в своём темпе',
        'Общие упражнения и теория доступны независимо от произведений. Без оценки исполнения и обязательного плана: выберите нужный навык.',
      ],
    ],
    guidesTitle: 'Знания, которые пригодятся за пианино.',
    guidesIntro:
      'От клавиш до аккордов: понятное объяснение, конкретный пример и небольшое задание.',
    read: 'Читать руководство',
    faqTitle: 'Перед первым занятием',
    faqs: [
      [
        'Что такое KuyLab?',
        'KuyLab — онлайн-студия для самостоятельного освоения пианино с MIDI-плеером, уроками по произведениям, отдельными упражнениями и теорией. Настройки и личная активность каждого пользователя хранятся отдельно.',
      ],
      [
        'Нужно ли подключать инструмент?',
        'Нет. Можно открыть KuyLab в браузере, смотреть на плеер и заниматься за своим инструментом. USB- или MIDI-подключение не является условием начала занятий.',
      ],
      [
        'Нужно ли уметь читать ноты?',
        'Для начала это не обязательно. Плеер показывает буквенные названия C, D, E и клавиши. Теорию можно осваивать постепенно в руководствах и уроках.',
      ],
      [
        'Чем отличаются уроки и общие упражнения?',
        'Урок по композиции готовит к конкретному произведению. Общие упражнения развивают координацию рук, ритм и смену аккордов независимо от репертуара.',
      ],
      [
        'Какое произведение уже доступно?',
        'В студии 38 произведений и 147 уроков по композициям. Можно начать с музыки Winter Sonata, Нино Роты, Yiruma, Шопена и Бетховена. У All in — Soundtrack два варианта Easy и Hard в одном плеере и 9 общих уроков. Отдельные упрощённые упражнения постепенно готовят к оригинальному исполнению.',
      ],
    ],
    about:
      'KuyLab создан для самостоятельных занятий. Его задача — связать работу над любимой композицией с теорией и полезными упражнениями. Это не автоматическая оценка исполнения и не живой урок с преподавателем.',
    cta: 'Начните работу над следующей мелодией.',
    privacyLabel: 'Конфиденциальность',
    sourceLabel: 'Исходный код',
    licensesLabel: 'Лицензии',
    updated: 'Проверено',
    back: 'Все руководства',
    guides: {
      piano: {
        title: 'Как учиться играть на пианино с MIDI-плеером',
        description:
          'Как использовать падающие MIDI-ноты: слушать, выбирать темп, разбирать партии рук и переходить к полному исполнению.',
        intro:
          'MIDI-плеер показывает, какую клавишу нажать, когда и как долго держать. Полезнее не просто повторять движение на экране, а понимать ритм и работу рук.',
        sections: [
          [
            'Сначала послушайте произведение целиком',
            'Не пытайтесь сразу играть вместе с записью. Найдите повторяющуюся мелодию, контрастные части и окончание. Знакомая на слух форма поможет ориентироваться при разборе.',
          ],
          [
            'Что хранится в MIDI',
            'MIDI — не сама аудиозапись. Он хранит высоту, начало, длительность и velocity нот, которые плеер превращает в звук и движение. Аппликатура и музыкальная фразировка присутствуют не в каждом MIDI-файле. Их не следует угадывать по цветам.',
          ],
          [
            'Выберите темп с запасом времени',
            'Начните со скорости, при которой успеваете подготовить следующее движение. Например, можно попробовать 60 процентов исходного темпа, но это не обязательное значение. После нескольких устойчивых исполнений немного увеличьте скорость.',
          ],
          [
            'Разделите задачи рук',
            'Отдельно прослушайте мелодию и сопровождение. Заметьте, где меняется бас левой руки и где заканчивается фраза правой. Упрощённое MIDI-упражнение помогает освоить движение; затем перенесите его в полную версию.',
          ],
          [
            'Научитесь находить клавиши',
            'Слева от группы из двух чёрных клавиш находится белая C. Следующие белые клавиши — D, E, F, G, A, B, затем снова C. Названия помогают ориентироваться в других регистрах, а не запоминать только цвет на экране.',
          ],
          [
            'Переходите от наблюдения к слуху',
            'Когда фраза знакома, попробуйте смотреть на экран реже. Представьте следующий звук и затем сыграйте. Снова сравните свою версию с записью: важны ритм, длительности и музыкальная связность, а не только правильные клавиши.',
          ],
        ],
        exercise: [
          'Попробуйте сейчас',
          'Медленно сыграйте C–D–E–F–G с одинаковой длительностью нот, затем G–F–E–D–C. Сохраняйте ровный пульс. Когда он устойчив, обратите внимание на плавность соединения звуков.',
        ],
      },
      theory: {
        title: 'Теория музыки на понятных примерах за пианино',
        description:
          'Полутон и тон, интервалы, ритм, мажорные и минорные аккорды: объяснения с примерами на клавиатуре.',
        intro:
          'Теория помогает назвать то, что вы уже играете, и понять его устройство. Прочитав определение, сразу проверьте его за инструментом и на слух.',
        sections: [
          [
            'Полутон и целый тон',
            'Расстояние между соседними клавишами, без промежуточной клавиши, — полутон. C–C♯ — полутон, C–D — два полутона, или целый тон. Между E–F и B–C нет чёрной клавиши: это тоже полутоны.',
          ],
          [
            'Интервал — расстояние между звуками',
            'C–D называется секундой, C–E — терцией, C–G — квинтой. Число ступеней определяют по названиям нот, а качество — по числу полутонов. C–E содержит четыре полутона и является большой терцией; C–E♭ — малой, из трёх полутонов.',
          ],
          [
            'Мажорное и минорное трезвучие',
            'C major состоит из C–E–G: большая терция и малая терция снизу вверх, 4 + 3 полутона. C minor — C–E♭–G: 3 + 4 полутона. Послушайте, как изменение одной средней ноты меняет окраску аккорда.',
          ],
          [
            'Обращения аккорда',
            'Расположите C–E–G как E–G–C или G–C–E: набор нот C major сохраняется. Это обращения. Другое расположение может приблизить руку к следующему аккорду и сделать движение отдельных голосов плавнее.',
          ],
          [
            'Пульс и ритм',
            'Пульс — равномерная основа, ритм — рисунок звуков и пауз внутри неё. Считайте четыре доли и играйте по одному звуку на долю. Затем разделите одну долю на два равных звука, сохраняя прежний пульс.',
          ],
          [
            'Найдите теорию в произведении',
            'Следите за сменой баса и за нотами, на которых мелодия приходит к покою. Повторяющийся интервал или аккорд становится узнаваемым. Не обязательно сразу подписывать каждый звук: начните с одного понятия, которое уверенно слышите.',
          ],
        ],
        exercise: [
          'Услышьте разницу',
          'Сыграйте C–E–G вместе. Затем опустите только E на полутон и сыграйте C–E♭–G. Сравните окраску мажора и минора, не меняя крайние ноты, а затем проверьте расстояния на клавиатуре.',
        ],
      },
      exercises: {
        title: 'Упражнения для пианино: пальцы, ритм и координация',
        description:
          'Простые упражнения на пять пальцев, координацию двух рук и смену аккордов с понятной целью каждого задания.',
        intro:
          'У полезного упражнения есть конкретная цель. Вместо одновременного требования скорости, ровности, связности и координации сначала выберите один критерий.',
        sections: [
          [
            'Нумерация пальцев',
            'На обеих руках большой палец обозначается 1, указательный 2, средний 3, безымянный 4, мизинец 5. Для C–D–E–F–G простой начальный вариант: правая 1–2–3–4–5, левая 5–4–3–2–1. Это не универсальная аппликатура для любого произведения.',
          ],
          [
            'Пять пальцев и ровный звук',
            'Играйте от C до G и обратно с одинаковой длительностью звуков. До ускорения убедитесь, что между нотами нет случайных остановок или спешки. Заранее представляйте, какой палец играет следующим.',
          ],
          [
            'Объединение рук',
            'Сначала выполните рисунок каждой рукой отдельно. Затем играйте C–D–E–F–G обеими руками в одном направлении. Одним и тем же названиям нот соответствуют разные номера пальцев. Если ритм нарушается, снизьте темп.',
          ],
          [
            'Смена аккордов',
            'Чередуйте правой рукой C–E–G и C–F–A, удерживая каждый аккорд четыре доли. Найдите общий C и проследите за перемещением остальных нот. Попробуйте обращения, например G–C–E, и сравните расстояния до следующего аккорда.',
          ],
          [
            'Отделите ритм от клавиш',
            'Ровно считайте до четырёх. Отмечайте хлопком сначала каждую долю, затем только первую и третью, не прекращая пульса. После этого перенесите рисунок на одну клавишу и лишь потом добавьте последовательность нот.',
          ],
          [
            'Верните навык в музыку',
            'Общие упражнения развивают навык вне одного произведения. Урок по композиции готовит к её конкретному исполнению. После упражнения найдите похожую задачу в любимой пьесе. Оценивайте не только скорость, но и управляемость и слышимый результат.',
          ],
        ],
        exercise: [
          'Небольшое занятие',
          'Минуту играйте C–D–E–F–G ровно, затем минуту соединяйте руки. После этого медленно чередуйте два аккорда. На каждом этапе выберите одну цель: ритм, ровность звука или плавность движения.',
        ],
      },
      privacy: {
        title: 'Конфиденциальность и данные аккаунта KuyLab',
        description:
          'Как KuyLab использует данные аккаунта, настройки, активность и хранилище браузера.',
        intro:
          'Открытые руководства доступны без аккаунта. Личная студия работает с авторизацией; профиль, заметки и настройки одного пользователя не показываются другому.',
        sections: [
          [
            'Аккаунт и личные данные',
            'Студия хранит логин, хеш пароля и выбранное имя. Настройки плеера, состояние обучения, избранное и активность привязаны к аккаунту. Пароль не хранится в открытом виде.',
          ],
          [
            'Cookie и хранилище браузера',
            'Для входа и защиты запросов используются cookie сессии и CSRF. Язык, тема и некоторые настройки также могут храниться в браузере. Файлы приложения и образцы пианино кешируются для офлайн-доступа.',
          ],
          [
            'Статистика активности',
            'Учитывается время, когда сайт виден или плеер воспроизводит музыку. В статистику входят активные посещения длительностью не менее пяти минут. Это не автоматическая оценка реальной игры на инструменте.',
          ],
          [
            'Хостинг и открытые страницы',
            'Сайт доставляется через Cloudflare. Сервер ведёт обычные журналы запросов для безопасности и диагностики. Google Search Console измеряет присутствие открытых страниц в поиске; личные записи студии не включаются в sitemap.',
          ],
          [
            'Обращения',
            'Для технических вопросов и обращений о данных используйте раздел задач проекта по ссылке на исходный код внизу страницы. Не публикуйте в открытом обращении пароль или личные данные студии.',
          ],
        ],
      },
    },
  },
  en: {
    title: 'Learn piano and understand music theory — KuyLab',
    description:
      'Learn the piano through music you love. KuyLab combines a falling-note MIDI player, composition lessons, independent exercises and practical music theory.',
    home: 'Home',
    guidesLabel: 'Guides',
    methodLabel: 'How it works',
    open: 'Open the studio',
    login: 'Sign in to the studio',
    theme: 'Switch colour theme',
    skip: 'Skip to content',
    headline: 'Learn to play the music you love.',
    intro:
      'Falling MIDI notes, composition lessons and practical music theory. Listen, slow the tempo and practise at your own piano.',
    preview: 'A look at the MIDI player',
    pauseMotion: 'Pause animation',
    resumeMotion: 'Resume animation',
    previewAlt: 'Left- and right-hand MIDI notes falling towards a piano keyboard',
    piece: 'Winter Sonata — Still',
    pieceMeta: '3:34 · 12 lessons',
    methodTitle: 'Start with the music. Understand what is inside it.',
    features: [
      [
        'Listen and follow',
        'Open a composition as falling notes. Letter names and piano keys show the pitch and timing. Choose a playback speed that suits you.',
      ],
      [
        'Learn the lesson separately',
        'Composition theory and dedicated MIDI exercises stay separate from the main player. Start with one hand or a simpler version and work towards the original.',
      ],
      [
        'Practise at your own pace',
        'Explore independent exercises and theory as well as your repertoire. No performance scores or compulsory schedule: choose the skill you want to work on.',
      ],
    ],
    guidesTitle: 'Ideas you can use at the piano.',
    guidesIntro:
      'From keys to chords: a clear explanation, a concrete example and something to try yourself.',
    read: 'Read the guide',
    faqTitle: 'Before you start',
    faqs: [
      [
        'What is KuyLab?',
        'KuyLab is an online studio for independent piano learning with a MIDI player, composition lessons, exercises and music theory. Each user has separate personal settings and activity.',
      ],
      [
        'Do I need to connect my piano?',
        'No. Open KuyLab in a browser, follow the player and practise on your own instrument. A USB or MIDI connection is not required to get started.',
      ],
      [
        'Do I need to read staff notation?',
        'Not to begin. The player shows letter names such as C, D and E and highlights piano keys. You can gradually explore theory through the guides and lessons.',
      ],
      [
        'How do composition lessons differ from independent exercises?',
        'A composition lesson prepares you for a particular piece. Independent exercises develop skills such as hand coordination, rhythm and chord changes without depending on one composition.',
      ],
      [
        'Which piece is available now?',
        'The studio includes 38 pieces and 147 composition lessons. Start with Winter Sonata, Nino Rota, Yiruma, Chopin or Beethoven. All in — Soundtrack has Easy and Hard versions in one player with 9 shared lessons. Separate simplified studies build towards the original performance.',
      ],
    ],
    about:
      'KuyLab is made for independent learners. It connects work on a favourite composition with theory and useful exercises. It does not automatically grade your playing or replace a live lesson with a teacher.',
    cta: 'Start working on your next piece.',
    privacyLabel: 'Privacy',
    sourceLabel: 'Source code',
    licensesLabel: 'Licences',
    updated: 'Reviewed',
    back: 'All guides',
    guides: {
      piano: {
        title: 'How to learn piano with a falling-note MIDI player',
        description:
          'Use a MIDI player thoughtfully: listen first, choose a manageable tempo, separate the hands and work towards a complete performance.',
        intro:
          'A MIDI player shows which key to press, when to press it and how long to hold it. Understanding the rhythm and movement is more useful than simply copying the screen.',
        sections: [
          [
            'Listen to the whole piece first',
            'Listen once without trying to play along. Notice returning melodies, contrasting sections and the ending. Knowing the shape by ear makes it easier to find your place when you begin practising.',
          ],
          [
            'Understand what MIDI contains',
            'MIDI is not the audio recording itself. It stores events such as pitch, onset, duration and velocity, which a player turns into sound and movement. Fingering and musical phrasing are not present in every MIDI file; note colours alone do not provide them.',
          ],
          [
            'Choose a tempo with thinking time',
            'Start slowly enough to prepare each next movement. You might try 60 percent of the original speed, but that number is not a rule. After several steady attempts, increase the speed a little. Keep listening for even timing as the tempo changes.',
          ],
          [
            'Separate the jobs of the hands',
            'Listen to the melody and accompaniment separately. Notice where the left-hand bass changes and where the right-hand phrase ends. A simplified MIDI exercise can make one movement clearer before you bring it back into the full version.',
          ],
          [
            'Learn your way around the keyboard',
            'The white key immediately left of a group of two black keys is C. The next white keys are D, E, F, G, A and B, followed by C again. Names help you find the same patterns in other registers instead of memorising a screen colour.',
          ],
          [
            'Move from watching to hearing',
            'Once a phrase is familiar, try looking at the screen less. Imagine the next sound before playing it. Listen to the recording again and compare the rhythm and note lengths. The goal includes musical continuity, not just pressing the correct keys.',
          ],
        ],
        exercise: [
          'Try this now',
          'Play C–D–E–F–G slowly with equal note lengths, then return G–F–E–D–C. Keep the pulse steady. When the timing feels reliable, focus on connecting the sounds smoothly.',
        ],
      },
      theory: {
        title: 'Music theory explained at the piano keyboard',
        description:
          'Understand semitones, intervals, rhythm, major and minor triads through concrete examples you can hear at the piano.',
        intro:
          'Theory gives names to things you play and helps explain how they work. After reading a definition, test it at the keyboard and listen to the result.',
        sections: [
          [
            'Semitones and whole tones',
            'The distance between adjacent piano keys, with no key in between, is a semitone. C to C♯ is one semitone; C to D is two semitones, or a whole tone. E–F and B–C have no black key between them and are also semitone steps.',
          ],
          [
            'An interval is a distance between notes',
            'C–D is a second, C–E a third and C–G a fifth. Letter names determine the interval number; semitone counts help determine its quality. C–E spans four semitones and is a major third. C–E♭ spans three and is a minor third.',
          ],
          [
            'Major and minor triads',
            'C major contains C–E–G: a major third followed by a minor third, or 4 + 3 semitones. C minor contains C–E♭–G, or 3 + 4 semitones. Listen to how changing just the middle note changes the colour of the chord.',
          ],
          [
            'Chord inversions',
            'Arrange C–E–G as E–G–C or G–C–E and the notes still form C major. These are inversions. A different arrangement can move your hand closer to the next chord and make the movement of individual voices smoother.',
          ],
          [
            'Pulse and rhythm are different',
            'Pulse is the steady underlying beat. Rhythm is the pattern of notes and silences within it. Count four beats and play one sound on each beat. Then divide one beat into two equal sounds while maintaining the same underlying pulse.',
          ],
          [
            'Find the idea in a composition',
            'Watch where the bass changes and which melody notes feel like points of rest. A repeated chord or interval becomes a recognisable idea rather than an isolated key press. Start by hearing one concept clearly instead of trying to label every note at once.',
          ],
        ],
        exercise: [
          'Hear the difference',
          'Play C–E–G together. Lower only E by a semitone and play C–E♭–G. Compare major and minor without changing the outside notes, then check the distances on the keyboard.',
        ],
      },
      exercises: {
        title: 'Piano exercises for fingers, rhythm and hand coordination',
        description:
          'Try five-finger patterns, two-hand coordination and chord changes with a clear purpose for each piano exercise.',
        intro:
          'A useful exercise has a specific job. Rather than demanding speed, evenness, smooth connection and coordination at once, choose one thing to pay attention to first.',
        sections: [
          [
            'Know the finger numbers',
            'On both hands the thumb is 1, index finger 2, middle finger 3, ring finger 4 and little finger 5. For C–D–E–F–G, a simple starting pattern is right hand 1–2–3–4–5 and left hand 5–4–3–2–1. This is not universal fingering for every piece.',
          ],
          [
            'Five fingers and an even sound',
            'Play from C to G and back using equal note lengths. Before increasing speed, listen for accidental gaps or rushing. Know which finger comes next rather than reacting at the last moment.',
          ],
          [
            'Bring the hands together',
            'Let each hand play the pattern alone first. Then play C–D–E–F–G with both hands travelling in the same direction. The same note names use different finger numbers in the two hands. If timing becomes uneven, choose a slower tempo.',
          ],
          [
            'Practise chord changes',
            'Alternate C–E–G and C–F–A in the right hand, holding each for four beats. Notice the common C and where the other notes move. Try inversions such as G–C–E and compare the distance to the next chord.',
          ],
          [
            'Separate rhythm from key finding',
            'Count evenly to four. Clap first on every count, then only on counts one and three, while keeping the pulse going. Move the pattern to one key before combining it with a changing sequence of notes.',
          ],
          [
            'Bring the skill back into music',
            'Independent exercises develop a skill beyond one piece. A composition lesson prepares you for a specific performance. After practising a skill, find a similar task in a piece you enjoy. Judge the result by control and the sound, as well as speed.',
          ],
        ],
        exercise: [
          'A short practice session',
          'Spend a minute playing C–D–E–F–G evenly, then a minute combining the hands. Slowly alternate two chords afterwards. Choose one goal at each stage: timing, an even sound or smooth movement.',
        ],
      },
      privacy: {
        title: 'Privacy and account data in KuyLab',
        description:
          'How KuyLab uses account information, personal settings, activity and browser storage.',
        intro:
          'Public guides can be read without an account. The personal studio requires sign-in; one user’s profile, notes and settings are not shown to another user.',
        sections: [
          [
            'Account and personal state',
            'The studio stores a username, password hash and chosen display name. Player preferences, learning state, favourites and activity are associated with your account. Passwords are not stored as plain text.',
          ],
          [
            'Cookies and browser storage',
            'Session and CSRF cookies support sign-in and request security. Language, theme and some playback preferences may also be stored in the browser. Application files and piano samples are cached for offline use.',
          ],
          [
            'Activity statistics',
            'Statistics count time while the site is visible or the player is playing. Active visits of at least five minutes are included. This is not an automatic assessment of your physical piano performance.',
          ],
          [
            'Hosting and public pages',
            'Cloudflare delivers the site. The server keeps standard request logs for security and troubleshooting. Google Search Console measures the visibility of public pages in search; private studio records are not included in the sitemap.',
          ],
          [
            'Questions and requests',
            'For technical questions or data-related requests, use the project issue tracker through the source-code link below. Do not post passwords or private studio information in a public issue.',
          ],
        ],
      },
    },
  },
};
