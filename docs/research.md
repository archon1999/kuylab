# Kompozitsiyalar orqali pianino va musiqa nazariyasini o‘rganish platformasi

> **Tarixiy tadqiqot — joriy talablar emas.** Quyidagi mahsulot takliflari avvalgi Pirate/import/quiz/reja prototipi uchun yozilgan. Keyingi suhbatda ular Still asosidagi curated studiya bilan almashtirildi. Nom variantlari va manbali kuzatishlar tadqiqot sifatida saqlanadi; versiya, narx va xizmat holatlari qayta tekshirilgan deb olinmasin. Amaldagi talablar va API: [studio-contract.md](studio-contract.md). Joriy mahsulot va ishga tushirish: [README](../README.md).

Tadqiqot sanasi: 11 oktabr 2026. Ishchi nom: **KuyLab**. Asosiy foydalanuvchi: Yamaha YDP-145 bilan chaladigan, amaliy ko‘nikmasi shakllangan, nazariyasi va ijro barqarorligini rivojlantirmoqchi bo‘lgan katta yoshli mustaqil pianinochi.

Tavsiya: platformaning markaziga **kompozitsiya → aynan tanlangan aranjirovka → qiyin parcha → nazariya → maqsadli mashq → yana kompozitsiya → tekshirish** siklini qo‘yish. O‘quv yo‘li sevgan repertuaringizdan chiqadi. Boshlang‘ich foydalanuvchiga mo‘ljallangan umumiy kurs sizning qo‘lingizdagi tajribani to‘liq aks ettirmaydi; ritm, nota o‘qish, armoniya, eshitish va texnikani alohida diagnostika qilish kerak.

Bu hujjat mahsulot, nom, raqobatchilar, dizayn, kontent, xarajat va bosqichlarni belgilaydi. Batafsil [ta’lim tadqiqoti](learning-research.md) va [texnik tadqiqot](technical-research.md) shu qarorlarni ochib beradi. Lokal ishga tushirish [README](../README.md)da. So‘nggi mahsulot talabi: to‘liq internet MIDI, Synthesia kabi player, aynan shu fayldan olingan alohida kompozitsiya darslari, Ivory kabi chap navigatsiya va `cp_uz`ga o‘xshash frontend arxitekturasi. Amaldagi tekshiruv dalillari [verification](verification.md)da. Fizik YDP-145 bilan ijroning ritm, ifoda yoki barmoqlashi avtomatik baholanmaydi.

## Sizga mos boshlang‘ich profil

Siz kompozitsiyalarni chalishga o‘rganganingizni aytdingiz. Buning o‘zi nota o‘qish, eshitib topish, mustaqil chap qo‘l, pedal yoki ritmda bir xil darajani kafolatlamaydi. He’s a Pirate’ni chalish asosida imtihon grade’i berilmaydi: har xil aranjirovkalar juda farq qiladi.

Dastlabki diagnostika 20–30 daqiqalik taklif: tanish asarni odatiy tempda ijro qilish; qiyin parchani sekinroq chalish; ikki qo‘lni alohida tekshirish; qisqa yangi ritmni sanash; bir necha nota va intervalni tanish; akkordni tuzish; qisqa audio bo‘yicha eshitish; qo‘l qulayligi haqida o‘z bahongiz. MIDI bo‘lmasa yozma javob va yozuv orqali boshlash mumkin. Bu vaqt klinik yoki standartlashtirilgan baholash emas, mahsulot uchun taxmin.

Natija bitta “intermediate” yorlig‘i o‘rniga ko‘nikmalar xaritasi bo‘ladi. Masalan, yaxshi yodlangan ijro bilan sust nota o‘qish birga mavjud bo‘lishi mumkin. Darslar kuchli tomonlaringizni ishlatib, kerakli bo‘shliqni yopadi.

## Repertuar va birinchi aranjirovka

Siz bergan yo‘nalish bo‘yicha boshlang‘ich ro‘yxat:

| Repertuar | Hozirgi holat | O‘quv imkoniyati, nota tasdiqlangandan keyin |
| --- | --- | --- |
| He’s a Pirate | Boshlang‘ich aniq variant tanlandi | Murakkab metr, puls va bo‘linmalar, qo‘llar koordinatsiyasi, temp barqarorligi |
| The Sound of Silence — Simon & Garfunkel | Istak ro‘yxati; aranjirovka tanlanadi | Akkordlar, melodiya va jo‘rlik muvozanati, frazalash |
| What Is a Youth — Nino Rota | Istak ro‘yxati; aranjirovka tanlanadi | Kuy yo‘nalishi, legato, ovozlar muvozanati va pedal |
| All In dorama OST | To‘plam; alohida treklar kerak | Trek va variantga qarab maqsad belgilanadi |
| Winter Sonata OST | To‘plam; alohida treklar kerak | Trek va variantga qarab maqsad belgilanadi |
| Naruto OST | To‘plam; alohida treklar kerak | Trek va variantga qarab maqsad belgilanadi |

Ushbu ko‘nikma bog‘lanishlari o‘quv rejasining takliflari; ko‘rilmagan aranjirovkaning aniq tahlili sifatida qabul qilinmasin. OST to‘plami bitta asar emas. Har bir trek uchun kompozitsiya, har bir ijro varianti uchun alohida aranjirovka saqlanadi.

Birinchi variant: **He’s a Pirate — to‘liq ikki qo‘lli piano MIDI**. [BitMidi (3)](https://bitmidi.com/pirates-of-the-caribbean-hes-a-pirate-3-mid) faylida Cerullean Pictures aranjirovka krediti, 77.625 soniya va 1,255 nota bor. Qo‘l treklarining nomlari va final tekshirildi. Asosiy oqim Synthesia kabi tushayotgan tovushlar: nota varaqlarini ochish shart emas. [To‘liq tekshiruv](full-source-verification.md). Preview yoki qisqartirilgan manba asosiy variant sifatida tanlanmaydi.

Kompozitsiya darslari shu MIDI’dagi aniq hodisa va vaqt parchasidan olinadi va alohida “Darslar” sahifasida beriladi. Playerning butun asar ko‘rinishi dars matni bilan band qilinmaydi. Barmoqlash va “eng qiyin joy” faylning o‘zi bilan ishonchli aniqlangan deb da’vo qilinmaydi.

## Dars qanday ishlaydi

Bir darsning maqsadi “videoni ko‘rish” emas, kompozitsiyadagi aniq muammoni tushunish va yaxshilash bo‘ladi.

1. Siz qiyin parchani belgilaysiz yoki MIDI tahlilidan keyin tizim uni taklif qiladi.
2. “Nima qiyin?” tanlanadi: nota, ritm, qo‘llarni qo‘shish, sakrash, akkord almashish, ovoz muvozanati, xotira yoki pedal.
3. Shu muammoni tushuntiradigan 2–4 daqiqalik nazariya mikro-darsi chiqadi.
4. Asarning aynan shu MIDI fragmenti qo‘l/ritm/interval bo‘yicha ajratib mashq qilinadi. Qo‘shimcha umumiy original mashqlar alohida bo‘limda qoladi.
5. Mashq yana asarning o‘ziga qaytariladi.
6. Temp va urinish natijasi qayd etiladi; keyingi sessiyada parchani oldindan qayta mashq qilmasdan, bir xil nota va yordam sharoitida qayta tekshirish rejalashtiriladi. Yoddan chalish tanlansa, u alohida ko‘nikma sifatida tekshiriladi.

Misol: tanlangan 6/8 MIDI boshlanishidagi real D4 takrorlari ritm darsiga misol bo‘ladi; chap qo‘l 3.6-soniyadagi D1/D2 kirishi oktava darsiga olinadi. O‘quvchi shu hodisalarni qisqa loopda chalib, keyin butun asarga qaytadi. Alohida umumiy nazariya mashqlari kompozitsiya parchasining o‘rnini egallamaydi.

Taklif qilinayotgan 30 daqiqalik seans: 3 daqiqa qulay boshlash va oldingi qiyin joyni tekshirish; 5 daqiqa bog‘liq nazariya; 7 daqiqa maqsadli mashq; 2 daqiqa tanaffus; 10 daqiqa kompozitsiya; 3 daqiqa yozuvni tinglash va qayd. Nazariya ulushi qat’iy foiz emas: ritm muammosi ko‘payganda mavzu uchun vaqt ortadi. Siz kunlik vaqtingizni hali belgilamagansiz, shuning uchun 30 daqiqa maket taxmini. Jismoniy qulaylik uchun muntazam tanaffus va og‘riq sezilsa mashqni to‘xtatish ko‘zda tutiladi. [BAPAM sog‘lom mashq tavsiyalari](https://www.bapam.org.uk/dont-cramp-your-style/).

Tadqiqot sifatli xato tuzatish, tempni moslash va to‘g‘ri urinishni barqarorlashtirish foydasini ko‘rsatadi; birgina ko‘p vaqt yoki ko‘p takror natijani anglatmaydi. Duke, Simmons va Cash tadqiqoti 17 ilg‘or pianinochining ma’lum vazifasiga tegishli, shuning uchun uning natijasidan barcha darajalar uchun “X marta tezroq” va’dasi chiqarmaymiz. [Tadqiqot](https://journals.sagepub.com/doi/10.1177/0022429408328851).

## Progress va individual moslashuv

“Perfect”ni bir nechta kuzatiladigan maqsadga ajratamiz: to‘g‘ri nota; kerakli ritm; qulay va barqaror temp; to‘xtamasdan davom etish; qo‘llar va ovoz muvozanati; frazalash, dinamika va pedal; keyingi kun qayta ijro qila olish.

Boshlang‘ich qoidalar tushunarli bo‘ladi: muammoli joyni qulay tempda ajratish; ishonchli urinishlardan keyin tempni kichik qadam bilan oshirish; xato qaytsa uni aniqlab tezlikni moslash; keyingi kuni qayta tekshirish. “Uch toza urinish” kabi mezonlar mahsulot tajribasi uchun sozlanadigan qoida, universal ilmiy chegaralar emas.

MIDI kelajakda notalar va vaqt bo‘yicha dalil beradi. U qaysi barmoq ishlatilganini, qo‘l tarangligini yoki talqinning musiqiy sifatini bevosita ko‘rmaydi. “Foydalanuvchi bahosi”, “MIDI o‘lchovi” va “o‘qituvchi tekshiruvi” turli kelib chiqishga ega natijalar sifatida saqlanadi.

## Mavjud platformalardan nimani olamiz

Quyidagi taqqoslash rasmiy ochiq sahifalardagi funksiyalar asosida. Pulli akkaunt ichidagi barcha funksiyalar audit qilinmadi. “Biz uchun yetarli emas” degan ustun xizmatda bu funksiya umuman mavjud emas degan da’vo emas.

| Platforma | Tasdiqlangan kuchli tomon | Biz oladigan fikr | Sizning vazifangiz uchun tekshirish kerak bo‘lgan narsa |
| --- | --- | --- | --- |
| [flowkey](https://www.flowkey.com/en) | Asarlar, video va nota bir ekranda, wait mode, loop, sekin ijro, qo‘l tanlash | Repertuardan boshlash, sodda mashq boshqaruvi | O‘zingiz tanlagan tashqi variant uchun individual nazariya va xato asosidagi reja |
| [Soundslice](https://www.soundslice.com/) | MusicXML importi, nota bilan audio/video sinxronlash, loop va qismlarni boshqarish | Mashq xonasining markaziy joylashuvi; kontent muallifi uchun muharrir yo‘li | Ko‘nikmalar xaritasi, o‘zbekcha darslar va pedagogik adaptatsiya |
| [Piano Marvel](https://pianomarvel.com/en/article/what-is-practice-mode) | Asarni kichik qismlarga ajratib o‘rganish yo‘li | Parcha, qo‘l, keyin butun ijro ketma-ketligi | Ifoda va texnik holatga inson mulohazasi; aniq shaxsiy repertuar mosligi |
| [Skoove](https://www.skoove.com/) | Qisqa darslar, real vaqt nota fikr-mulohazasi, nazariya va texnika | Mikro-dars formati va mashq bilan bog‘lash | Tanlangan aranjirovka bo‘yicha kontentni qanchalik erkin tuzish mumkinligi |
| [Pianote](https://www.pianote.com/) | O‘qituvchi video-darslari va qo‘shiqlar | Inson tushuntirishi, musiqiy ifodaga urg‘u | Notaga sinxron interaktiv baholash va sizning variantingiz uchun shaxsiy yo‘l |
| [Tomplay](https://tomplay.com/how-it-works) | Interaktiv nota, temp, jo‘rlik, annotatsiyalar | Nota ustidagi boshqaruv va versiyalarni ajratish | Kundalik individual dars va qo‘l mashqini birlashtirish |
| [Ivory](https://ivory-app.com/) | Audio’dan nota/MIDI, MusicXML eksporti, muharrir va piano roll haqida rasmiy tavsif | Siz tanlagan asosiy vizual uslub; kelajakda transkripsiya ish joyini baholash | Transkripsiya, barmoqlash va kontent sifati haqiqiy namunada alohida tekshiriladi; individual pedagogika o‘z qatlamimiz |
| [musictheory.net](https://www.musictheory.net/exercises) | Nota, interval, akkord va eshitish mashqlari | Diagnostika va umumiy nazariya bo‘limining boshlang‘ich manbasi | O‘zbekcha kontekst va aynan kompozitsiyaga qaytish |

Eng yaqin mahsulot fikri: flowkey’ning repertuar motivatsiyasi + Soundslice’ning parcha markazidagi ish joyi + Piano Marvel’dagi bosqichli mashq + sizga mos nazariya va kuzatiladigan individual reja. Bu o‘xshashliklar dizayn va ish jarayoni yo‘nalishidir, ularning natija va’dalarini ko‘chirmaymiz.

## Dizaynni qayerdan olamiz

Siz tanlagan asosiy vizual referens — **Ivory**. Uning iliq och foni, jigarrang aksenti, serif sarlavhalari, yumaloq boshqaruvlari va keng bo‘shlig‘i KuyLab’ga moslashtiriladi. Kam matn, yumshoq zamonaviy ko‘rinish va kam border sizning aniq talabingiz. Mashg‘ulot sahifasi shu vizual til bilan, kompozitsiya asosidagi o‘quv ishiga mos tuziladi. [Ivory](https://ivory-app.com/).

**MUI rasmiy bepul dashboard andozasi** kod tuzilmasi, navigatsiya va tayyor komponentlar uchun qayta ishlatiladi. Music platformalaridan katalog, mashq boshqaruvi va nota/video joylashuvi g‘oyalarini olamiz. [MUI andozalari](https://mui.com/material-ui/getting-started/templates/), [MUI manbasi va MIT litsenziyasi](https://github.com/mui/material-ui).

Prototipdagi navigatsiya haqiqiy MUI Dashboard MenuContent andozasidan moslashtirilgan. Manba va litsenziya frontend/THIRD_PARTY_NOTICES.md hamda frontend/MUI-LICENSE.txtda saqlanadi. Butun flowkey yoki Soundslice ekranining nusxasi olinmagan; ularning logotipi, albom muqovasi, videolari va nota fayllari ko‘chirilmagan.

| Ekran | Tayyor asos yoki namuna | O‘zgartirish |
| --- | --- | --- |
| Bugungi mashq | MUI shell; bosqichli practice modeli | Keyingi aniq vazifa, kunlik vaqt va oxirgi o‘z bahosi |
| Kompozitsiyalar | flowkey’dagi repertuar katalogi g‘oyasi | Shaxsiy istak ro‘yxati, aniq variant va manba holati |
| Kompozitsiya loyihasi | Asar tafsiloti va dars rejalari | Parcha → ko‘nikma → nazariya → mashq bog‘lanishi |
| Mashq xonasi | Soundslice/flowkey practice g‘oyasi | Nota/video uchun markaz, temp/qo‘l/loop boshqaruvi, yozuv |
| Nazariya va mashqlar | MUI kartalari; qisqa nazariya mashqlari | Har bir mavzuda qaysi asarga tegishli ekani |
| Profil va qurilma | MUI forma komponentlari | YDP-145, kundalik vaqt, MIDI holati |

Vizual yo‘nalish: Ivory’dan ilhomlangan iliq oq fon, jigarrang aksent, kulrang matn, serif sarlavha, keng asosiy mashq maydoni va ixcham gorizontal navigatsiya. Motivatsion shiorlar va takroriy tushuntirishlar olib tashlanadi. Kartalar chegarasi asosan yuzalar farqi va bo‘shliq orqali beriladi. Uzun nazariy izoh faqat ochilgan darsda; boshqaruvlar qisqa nomlangan. Desktop va pianino yonidagi planshet birinchi o‘rinda; telefon katalog va reja uchun qulay. Nota ekranida to‘liq 88 klavishli mayda klaviatura o‘rniga kerakli diapazon ko‘rsatiladi. Mobile’da murakkab pianino ish joyi qatorlarga joylashadi.

Ivory o‘zini pianino audio transkripsiyasi va interaktiv nota/MIDI ish joyi sifatida ta’riflaydi. KuyLab’ning vazifasi esa sizning repertuaringiz orqali nazariya va texnikani o‘rgatish. Ivory’ning transkripsiya va aplikatura haqidagi da’volari KuyLab’ning mavjud imkoniyati sifatida ko‘rsatilmaydi. Rangi va ekran tartibi dizayn uchun referens; uning xususiy kodi, logotipi va shrift fayllari ishlatilmaydi. Batafsil [dizayn qarorlari](design-guide.md).

Bu poydevor Figma’da ham xuddi shu MUI tokenlari bilan aks ettirilishi mumkin. Hozir Figma fayli yaratilmagan; ishlaydigan React maket dizaynni tekshirish uchun yetarli. MUI komponentlari, umumiy pattern va litsenziyalangan andoza qayta ishlatilgani boshlang‘ich dizayn ishini qisqartiradi.

musictheory.net o‘z FAQ’ida dars va mashqlarni iframe orqali ulashga ruxsat beradi, kamida 600×600 maydon talab qiladi. Bu umumiy mashqlarni erta ulash variantidir; cross-origin iframe’dagi natijalarni avtomatik o‘qib backend progressiga aylantirib bo‘lmaydi. Til va mobil moslashuv uchun keyin original o‘zbekcha mashqlar ma’qul. [Embedding shartlari](https://www.musictheory.net/faq).

## Nom variantlari

| Nom | Mazmun va kuchli tomoni | E’tibor beriladigan jihat |
| --- | --- | --- |
| **KuyLab** | Kuy + laboratoriya; sevgan asarni tahlil qilib o‘rganish | Ishchi tavsiya; domen va tovar belgisi tekshiriladi |
| **NotaYo‘l** | Nota orqali individual o‘quv yo‘li | O‘zbekcha aniq; domen yozilishi notayol bo‘lishi mumkin |
| **Reperto88** | Repertuar va 88 klavish | Mahsulot g‘oyasini aniq anglatadi; kelajakda boshqa asboblar uchun torroq |
| **Kuydan** | Bilim kuydan keladi | Qisqa va shaxsiy; xalqaro auditoriyaga izoh kerak |
| **AkorYo‘l** | Akkordlar va rivojlanish yo‘li | Armoniya urg‘usi kuchliroq |
| **IjroLab** | Ijroni yaxshilash laboratoriyasi | Nazariyadan ko‘ra practice g‘oyasi oldinda |
| **NotaKo‘prik** | Nazariya bilan qo‘l tajribasini bog‘lash | Ma’noli, lekin uzunroq |
| **Phrase88** | Parchalar va pianino | Xalqaro, lekin inglizcha talaffuz kerak |

Birinchi uchlik: **KuyLab**, **NotaYo‘l**, **Reperto88**. Maketda KuyLab ishlatilgan. Dastlab ko‘rib chiqilgan NotaLab nomi boshqa musiqa akademiyasida ishlatilayotgani aniqlandi, shu sabab asosiy tavsiyadan chiqarildi. [Mavjud NotaLab](https://notalab.com.tr/). Nom bo‘yicha oddiy veb qidiruv domen yoki tovar belgisi mavjudligi tekshiruvi o‘rnini bosmaydi; hozir hech biri “bo‘sh” deb tasdiqlanmaydi.

## Yamaha YDP-145 bilan ulanish

YDP-145 sizga mos texnik imkoniyat beradi: USB TO HOST orqali performance/MIDI ma’lumoti va USB audio almashinuvi. Yamaha qo‘llanmasi 3 metrdan qisqa AB turidagi USB kabelni ko‘rsatadi; USB 3.0 kabelidan foydalanmaslikni va simli ulanishni aytadi. Kompyuteringizdagi port USB-C bo‘lsa mos data kabel yoki adapter zarur. Alohida MIDI-interface xaridi USB ulanish ishlaganda talab etilmaydi. [Yamaha qo‘llanmasi, 30-bet](https://data.yamaha.com/files/download/other_assets/6/1538796/ydp165_en_om_single_b0.pdf), [MIDI reference](https://usa.yamaha.com/files/download/other_assets/6/1545676/ydp165_145_s55_s35_en_mr_b0.pdf).

Windows’da Yamaha USB audio ishlatish uchun Yamaha Steinberg USB Driver kerakligi qo‘llanmada yozilgan. MIDI input’ning tizimda paydo bo‘lishi alohida tekshiriladi; audio uchun drayver kerakligini barcha MIDI holatlariga umumlashtirmaymiz. Drayver o‘rnatish va fizik ulanish hozir bajarilmadi. [Rasmiy drayverlar](https://usa.yamaha.com/products/musical_instruments/pianos/arius/ydp-145/downloads.html).

Birinchi real qurilma bosqichi: pianinoni kabel bilan ulash → operatsion tizim qurilmani ko‘rishini tekshirish → qo‘llab-quvvatlangan brauzerda foydalanuvchi harakatidan keyin Web MIDI ruxsati → nota/pedal test → timestamp va kechikish kalibratsiyasi. Brauzer qo‘llamasa qo‘lda mashq rejimi qoladi. Web MIDI va USB audio ikki alohida yo‘l: USB audio yozuv uchun, MIDI nota/vaqt hodisalari uchun. [Web MIDI](https://developer.mozilla.org/en-US/docs/Web/API/Web_MIDI_API).

## Texnik mahsulot qarori

Siz so‘ragan stack saqlanadi: **Python + Django + Django REST Framework**, **React + TypeScript + MUI**. Lokal prototip SQLite bilan; haqiqiy host uchun PostgreSQL. Boshlanishda Django admin kontent muharriri bo‘ladi. Audio/MIDI oqimi real vaqt frontendda ishlanadi; har bir nota uchun Django serveriga HTTP so‘rovi yuborilmaydi.

Model: Composition → Arrangement → o‘zgarmas MIDI versiyasi → aniq fragment → ko‘nikma va dars. Progress, quiz, diagnostika va sessiyalar manba versiyasidan ajratilmaydi. Asosiy o‘rganish MIDI voqealari bilan ishlaydi; notation formati yoki PDF majburiy emas.

Nota importi va audio tahlili zarur bo‘lganda Celery/Redis worker qo‘shiladi. AI o‘qituvchi tekshirgan ma’lumot asosida izoh va reja taklif qiladi; nota yoki aplikaturani asos yo‘q joyda taxmin qilishga tayanilmaydi. Faqat URL kiritish hali to‘liq MusicXML, avtomatik dars yoki nota huquqini bermaydi. Batafsil arxitektura va API [texnik tadqiqot](technical-research.md)da.

## Kontent ishlab chiqarish

Birinchi dars paketi uchun ketma-ketlik: to‘liq MIDI va aniq variantni tekshirish; manba/provenance saqlash; haqiqiy hujum, davomiylik va qo‘l treklaridan parcha ajratish; shu tovushlarga nazariya va amaliy qadamni bog‘lash; alohida darsdan player fragmentini ochish; foydalanuvchi sinovi va reja qayta ko‘rigi. Ustoz barmoqlash, harakat va ifoda tavsiyasini qo‘shimcha tekshiradi.

Xarajatning muhim qismi dars sifatidir. Video URL’dan bir bosishda xatosiz nota, to‘g‘ri aplikatura va yaxshi pedagogika chiqishi MVP uchun ishonchli asos emas. Professional notali manba tanlanganida ham avtomatik import va aranjirovka tahlili tekshirishni talab qiladi.

Aranjirovka va audio yozuv huquqlari alohida hisobga olinadi. Musiqa do‘konidan nota sotib olish uni umumiy sayt katalogida tarqatishga avtomatik ruxsat degani emas. Kontent yozuvida manba, muallif/arranger, litsenziya, ruxsat etilgan saqlash va ko‘rsatish doirasi bo‘ladi. AQSH Copyright Office aranjirovkalarni hosila asar misoli sifatida sanaydi; bu O‘zbekiston uchun individual huquqiy xulosa emas, kontent modelida versiya va huquqni ajratish sababidir. [Rasmiy tushuntirish](https://www.copyright.gov/eco/help-limitation.html).

Video uchun ruxsat berilgan original player yoki tashqi havola qo‘llanadi. YouTube faylini yuklab olib o‘z serverimizda qayta tarqatish poydevorga kiritilmaydi. [YouTube embedding yo‘li](https://support.google.com/youtube/answer/171780).

## Qurilish bosqichlari va qabul mezonlari

Quyidagi muddatlar bir tajribali dasturchi va kontent bo‘yicha musiqachi hamkor bilan taxmin; buyurtma narxi yoki kafolatlangan sana emas.

| Bosqich | Taxminiy mehnat | Chiqariladigan natija | Qabul mezoni |
| --- | --- | --- | --- |
| Hozirgi lokal sayt va tadqiqot | Amalga oshirildi | Manbali tadqiqot, nomlar, Ivory yo‘nalishidagi React/MUI, Django, diagnostika, dars, import/player va reja | Texnik tekshiruvlar [verification](verification.md)da; haqiqiy o‘quv natijasi sizning amaliy sinovingizda baholanadi |
| Musiqachi bilan kontent piloti | 2–4 hafta taxmin | Bitta litsenziyalangan aranjirovka, tekshirilgan aplikatura va texnik annotatsiya | Siz bitta qiyin parchani keyingi kun qayta tekshirasiz; ustoz nota va harakat tavsiyasini tekshiradi |
| MIDI practice | Qo‘shimcha 2–4 hafta | Qurilma ulash, kalibratsiya, pitch/timing tahlili, hisobot | Haqiqiy YDP-145 bilan noto‘g‘ri nota/vaqt va qurilma uzilishi sinovdan o‘tadi |
| Ko‘p repertuar va kontent ish joyi | Qo‘shimcha 2–4 hafta | Bir necha asar, qayta foydalaniladigan ko‘nikma darslari, muharrir | Turli aranjirovkalarning progressi ajratilgan; darslar musiqachi tekshirgan |
| Hosting va ishonchli foydalanish | Alohida rejalash | Login, foydalanuvchi ma’lumotini ajratish, backup, media saqlash, monitoring | Boshqa foydalanuvchi yozuviga kira olmaydi; backup qayta tiklanadi |

AI bilan audio’dan avtomatik polifonik transkripsiya, kameradan barmoq va holatni baholash, katta litsenziyalangan katalog, to‘lov va ijtimoiy funksiyalar birinchi individual MVP’ga kiritilmaydi. Ular vaqt va tekshirish talabini keskin oshiradi.

## Xarajat modeli

Shaxsiy lokal versiya uchun hosting xarajati yo‘q; mavjud kompyuter va pianino ishlatiladi. Kabel/adapter, tanlangan nota va o‘qituvchi tekshiruvi alohida xarajat. Audio yozuv lokal saqlansa hajm va backup sizning kompyuteringizga bog‘liq. AI API majburiy emas: qoida asosidagi reja va tekshirilgan dars bilan boshlash mumkin.

Onlayn Django uchun hisob: web service + PostgreSQL + backup/media + domen + kerak bo‘lsa worker/Redis + AI sarfi + kontent mehnati. Birgina “server $X” umumiy xarajatni ifodalamaydi. Render misolida statik frontend, web service va PostgreSQL alohida xizmatlar; ayrim bepul xizmatlarning cheklovlari bor va bepul PostgreSQL 30 kunda tugaydi. Doimiy foydalanuvchi ma’lumotini shu vaqtinchalik DB’ga bog‘lamaslik kerak. [Xizmat turlari](https://render.com/docs/service-types), [bepul tarif cheklovlari](https://render.com/docs/free), [rasmiy narxlar](https://render.com/pricing).

Hosting sotib olish qarori hozir talab qilinmaydi. Avval bitta asar uchun darslar ishlashini va siz qayta-qayta foydalanishingizni tekshiramiz. So‘ng kerakli RAM, media hajmi, backup va domen asosida aniq hisob chiqariladi.

## Eng muhim ochiq qarorlar

1. KuyLab nomi vaqtincha; yakuniy nom va domen tanlanadi.
2. Kunlik mashq vaqti hali aytilmadi; hozir 30 daqiqa.
3. BitMidi (3) to‘liq ikki qo‘lli piano MIDI boshlang‘ich tanlov. Boshqa variantga o‘tishda ham butun fayl va final tekshiriladi.
4. All In, Winter Sonata va Naruto’dan aniq treklar ro‘yxati tanlanadi; bir collection uchun bitta soxta dars yaratilmaydi.
5. Birinchi oltita kompozitsiya darsi haqiqiy MIDI fragmentlariga bog‘langan. Sizning amaliy sinovingizga qarab parcha va murakkablik moslashtiriladi.
6. YDP-145 bilan Web MIDI va audio ulanishi haqiqiy qurilmada tekshiriladi.

Mahsulot muvaffaqiyatining birinchi mezoni: siz sevgan aniq variantning oldin beqaror bo‘lgan parchasini keyingi kuni tushunib, qulay va barqaror ijro qila olishingiz. Mashg‘ulot daqiqalari va tugallangan kartalar shu natijani tushuntiruvchi yordamchi ma’lumot bo‘ladi.
