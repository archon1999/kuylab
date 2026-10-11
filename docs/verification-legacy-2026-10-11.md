# KuyLab tekshiruvlari

11 oktabr 2026. Windows, Python 3.12, Django 5.2, React/MUI. Lokal API 127.0.0.1:8000, frontend 127.0.0.1:5173.

## Yakuniy avtomatik tekshiruv

- `manage.py test learning scores`: **91/91** test o‘tdi. MIDI parsing, manba va tarix, haqiqiy MIDI darslari, quiz, diagnostika, i18n, birinchi import, noto‘g‘ri payload va lokal origin himoyasi tekshirildi.
- Django system check xatosiz; `makemigrations --check --dry-run` farq topmadi.
- `npm test`: **75/75** test o‘tdi. Native tempo xaritasi, aniq sekundli clip, nota/pedal ovozi, seek/loop/yakun, 6/8 puls, MIDI adapter, parallel so‘rovlar, profil saqlash navbati, session taymeri, HTTP timeout va route transferi qamraldi.
- `npm run lint`: **67 source fayl, 217 import bog‘lanishi, 0 arxitektura buzilishi**. Alias, relative, dynamic va type importlar tekshirildi; format check ham o‘tdi.
- TypeScript va Vite production build o‘tdi. Yetti sahifa lazy chunklarga ajratilgan. Asosiy JS 328.21 kB, gzip 108.84 kB; React runtime alohida 223.68 kB, gzip 69.43 kB; MIDI workspace 43.89 kB, gzip 15.29 kB. 500 kB chunk ogohlantirishi yo‘q. Bu chunk taqsimoti; umumiy yuklash tezligi bo‘yicha benchmark emas.
- `npm audit` va production dependency auditi: tekshiruv vaqtida **0 vulnerability**.

## Takroriy review: tuzatilgan muammolar

- Temp almashishi ijro joyini endi boshiga qaytarmaydi. Ekran klavishlari ovoz beradi; strelkalar bilan nota tanlash, Enter/Space bilan chalish mumkin. Timeline vaqtni original MIDI davomiyligida ko‘rsatadi.
- Kech kelgan score, repertuar, dars yoki profil so‘rovi yangi tanlovni ustidan yozmaydi. Profil va preference yozuvlari navbat bilan bajariladi. Session tarixi parallel o‘qish/saqlashda takrorlanmaydi.
- MIDI yo‘q kompozitsiyada tayyor dars/reja ko‘rsatilmaydi. Birinchi MIDI importi kompozitsiya ID’si orqali yangi variant yaratishi mumkin. To‘liq manba belgisi tekshirilgan faol MIDI’gagina tegishli.
- Darslar haqiqiy MIDI nota juftlari, interval, metr va yakun hodisalaridan olinadi. Dars fragmentini o‘zgartirish butun manbani o‘zgartirmaydi.
- Mobil menyu fokusni ichida ushlab turadi; Escape va tanlov uni yopadi. Noto‘g‘ri kompozitsiya ID’si boshqa asarni yashirincha ochmaydi. Sahifa xatosida qayta yuklash yo‘li bor.
- GET/yozuv so‘rovlari cheksiz kutmaydi; yozuv timeout bo‘lsa natijani tekshirish so‘raladi, avtomatik qayta yozish yo‘q. Noto‘g‘ri JSON 400, import storage xatosi 503 qaytaradi; muvaffaqiyatsiz importning fayli va DB yozuvlari tozalanadi.
- Lokal API begona saytdan kelgan yozuvni rad etadi va shaxsiy javoblarni cache qilmaydi. Bu public hosting uchun login o‘rnini bosmaydi.
- Taymer fon tabidagi interval sekinlashganda vaqtni yo‘qotmaydi. Dark mode’dagi repertuar qidiruvi va qo‘shish kartasi, rang kontrasti, uzun profil ismlari, nazariya tablari tuzatildi.

Takroriy brauzer QA: 10% seek’dan keyin temp almashganda 10%/00:07 saqlandi; C♯4 ekran klavishi va ijro/pauza ishladi. Sound of Silence’da MIDI import dialogi ochildi, bo‘sh darslar yo‘q. Bo‘sh profil ismi saqlash tugmasini o‘chirdi. UZ/RU/EN server matnlari yangilandi; UZ/light/Pianinochi qaytarildi. 480 CSS px’da menyu va uchinchi nazariya tabi ishladi, document width 450 px. Kod tahriri paytidagi eski HMR loglaridan alohida, yakuniy toza reload’dan keyin **yangi konsol xatosi yo‘q**. Birinchi import test DB’da sinaldi; foydalanuvchi bazasiga test MIDI yoki o‘quv progressi yozilmadi.

## To‘liq MIDI dalili

Faol He’s a Pirate varianti: arrangement 8, Score 1, v1. Internetdan olingan original fayl **11,918 byte / 1,255 nota / 77.625 soniya**. SHA-256 `853c5d63d49fdfc685f4215092affa83794298347a52e328ee24fe2ee86da522`.

`/api/scores/1/file/` audio/midi qaytardi; API’dan olingan bytes original manba hashiga mos. Ikki piano trek manbada Right Hand va Left Hand deb nomlangan. Oxirgi notalar va Note Off/End of Track tekshirildi. [Batafsil audit](full-source-verification.md). Yangi oddiy import avtomatik “to‘liq manba” deb belgilanmaydi.

## Brauzerda tasdiqlangan oqimlar

- Sidebar header ostidan boshlanadi: birinchi guruh y=118 px. Katta bo‘shliq va sozlamalar ikonkasining siqilishi tuzatildi.
- Stylesheet import tartibi tuzatilib, sidebar va asosiy kontent ustma-ust tushishi bartaraf etildi; seek paytida bo‘lak badge ham sinxronlanadi.
- Butun He’s a Pirate tushayotgan tovushlar va 88 klavish bilan ochildi. Eshitish, pauza va seek ishladi; finalda ijro to‘xtadi.
- Asosiy playerda 100% / chorak=200 BPM va 1–87 MIDI vaqt oynasi ko‘rindi. Ular bosma takt raqami sifatida berilmaydi.
- “Darslar” alohida sahifani ochdi. Olti dars haqiqiy MIDI hodisalariga bog‘langan. Oktava darsi 3.600–7.200 s fragment va 12 yarim ton masofani ko‘rsatdi.
- Shu darsning mini-playeri 5–8 manba oynasini 50% / 100 BPM’da ochdi. “Tanlangan parchaga” source=1, aniq sekundlar, oynalar va tempni URL’da saqladi. Topilgan callback xatosi tuzatilib, uchta route regressiyasi qo‘shildi.
- Darsdan butun asarni boshlash eski score/clip/lesson/tempo parametrlarini tozaladi va butun MIDI’ni 100% tempda qayta ochdi.
- UZ/RU/EN menyular, ruscha dars tushuntirishi, quiz savoli va qadamlar ko‘rildi. Nazariy va foydalanuvchi qaydi alohida.
- Profil ismi sinov qiymatiga o‘zgartirilib saqlandi; reload’da saqlandi. Til va dark mode ham reload’dan keyin saqlandi. Sinov ismi Pianinochi’ga, til UZ va tema light holatiga qaytarildi.
- Dark mode’dagi kech yuklanadigan CSS ziddiyati tuzatildi: actual-score foni rgb(32,38,46), theme surface bilan mos. Oq kartalar qolmadi.
- Brauzer taqdim etgan **480 CSS px** mobil ko‘rinishda menyu ochilib/yopildi; yashirin menyu focus/AX oqimidan chiqarildi. Document scrollWidth 450 px bo‘lib, 480 px viewportdan oshmadi. Vaqtinchalik viewport qaytarildi.
- Yangi tekshiruv tabida player ishlaganda konsol xatosi topilmadi. Web MIDI uchun fizik pianino ruxsati olinmadi.

## Ishga tushirish va tarix

`run-local.ps1 -SkipInstall -Background` yangi MIDI-first seed bilan ishga tushdi. `stop-local.ps1` launcher qayd etgan workspace/PID/boshlanish vaqti mos processlarni to‘xtatadi. Qayta boshlanganda profil va mavjud tarix saqlandi. Eski variantlar arxiv sifatida qoladi, faol MIDI darslari ularning progressini avtomatik meros olmaydi.

Avtomatik testlar vaqtinchalik test DB’da ishladi. Brauzer QA’da yangi o‘quv progressi yoki soxta ijro sessiyasi yozilmadi. Profil sinov qiymati qaytarildi.

## Amaliy chegaralar

Yamaha YDP-145 bilan fizik USB/MIDI ulanishi va kalibratsiya hali sinalmagan. Adapter va ekran sinovlari fizik qurilma sinovi emas. Player ovozi Web Audio sintezi. Kutish rejimi nota balandligiga javob beradi; ritm, pedal, ifoda, barmoqlash yoki umumiy “perfect” bahosi chiqarilmaydi.

Sayt lokal bitta profilga mo‘ljallangan. Public hosting, multi-user login va foydalanuvchi o‘quv samarasi bo‘yicha uzoq pilot bu tekshiruvga kirmaydi.

## Tasvirlar

- [Review’dan keyingi MIDI player](../artifacts/review-player.jpg)
- [Dark mode repertuar](../artifacts/review-dark-library.jpg)
- [Mobil menyu](../artifacts/review-mobile-menu.jpg)
- [MIDI player va tuzatilgan sidebar](../artifacts/practice-room.jpg)
- [Alohida MIDI darsi](../artifacts/lesson.jpg)
- [Bugungi mashq](../artifacts/dashboard.jpg)
- [Mobil MIDI player](../artifacts/mobile-midi.jpg)

