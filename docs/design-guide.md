# KuyLab dizayn yo‘nalishi

11 oktabr 2026. Asosiy vizual referens — [Ivory](https://ivory-app.com/) va foydalanuvchi yuborgan umumiy shell hamda tushayotgan notalar playeri skrinshotlari. Uslub: yumshoq ranglar, kam border, qisqa matn va musiqaga yetarli joy.

Asosiy foydalanish muhiti — Yamaha YDP-145 yonidagi noutbuk yoki kompyuter. Katta player markazda; nazariya va dars mashqlari alohida ochiladi. Pianinoni kompyuterga ulash talab qilinmaydi.

## Rang, shrift va logo

| Qism | Amaldagi qaror |
| --- | --- |
| Umumiy fon | Light `#faf8f5`; dark `#18122b` |
| Yuzalar | Light `#fffdfa`; dark `#292043`, ko‘tarilgan yuza `#32284e` |
| Aksent | Light `#a47148`; dark `#eba165` |
| Matn | Light `#4b5563`; dark `#f5edc9` |
| Sarlavhalar | Lora, qisqa va katta; serif fallback |
| Boshqaruv va menyu | Alan Sans; kirill matn uchun Inter |
| Logo | Mustaqil pianino SVG, shared BrandMark va favicon |
| Chap/o‘ng qo‘l | Alohida sozlanadigan pushti/havorang ranglar |

Alan Sans Ivory’da kuzatilgan ochiq shrift oilasi; u Fontsource orqali alohida o‘rnatilgan. Lora — ochiq display-serif varianti. Ivory logosi, xususiy shrift fayllari va dastur kodi ko‘chirilmagan. Katta dekorativ gradient kartalari ishlatilmaydi; nota gradientlari musiqa ma’lumotini ko‘rsatadi.

## Shell va scroll

Chap menyu yuqori panel ostidan boshlanadi: bosh sahifa, kompozitsiyalar, umumiy mashqlar, nazariya, statistika va sozlamalar. Yuqorida UZ/RU/EN, light/dark va profil bor. Kichik ekranda menyu MUI Drawer’da ochiladi.

Header hamda sidebar joyida qoladi. Faqat asosiy kontent viewportning qolgan qismida scroll qiladi; document/body uchun ikkinchi scroll yo‘q. Scrollbar ingichka, temaga mos rangli, shaffof track bilan. Sidebar yoki sozlamalar o‘z balandligidan oshsa o‘zining ichki scroll’idan foydalanadi.

Dashboard oxirgi kompozitsiyani davom ettirish yoki playerni ochishni taklif qiladi. Darslar amali kompozitsiya materiallariga olib boradi. Haftalik saytda o‘tkazilgan vaqt va oxirgi faollik ixcham ko‘rinadi; batafsil statistika alohida sahifada. Sevimlilar, oxirgi ochilganlar, umumiy mashqlar va nazariyaga tez kirish bor.

## Tushayotgan notalar playeri

Katta player focused shell’da viewportni egallaydi; 88 klavish pastga yetadi. Umumiy app header/sidebar o‘rnini ixcham player paneli oladi. Dars playeri shu imkoniyatlarning kompakt ko‘rinishidan foydalanadi.

Yuqorida ijro/pauza, vaqt va timeline, tezlik, boshidan boshlash, sozlamalar, fullscreen va tema boshqaruvi bor. Click yoki drag vaqtga o‘tkazadi. Temp 20–200%, ko‘rinadigan kelajak 2–15 soniya; lookahead tempdan mustaqil. Space — ijro/pauza, strelkalar — 5 soniya, −/+ — tezlik, Home — boshiga; timeline fokusida End — oxiriga. Matn/dialog boshqaruvlari player shortcutlarini yutmaydi.

Avtomatik takrorlash, oraliq tanlash, repeat pause va L shortcut olib tashlangan. Ijro yakunda to‘xtaydi; foydalanuvchi xohlasa qayta boshlaydi.

Notalar yumaloq uchli vertikal barlar. MIDI velocity kuchliroq bo‘lsa yorqinlik/opacity shu qiymatga moslashadi; gradient sozlamasi uni o‘chirishga imkon beradi. Bu vizual tanlov MIDI timing, pitch yoki ovoz kuchini o‘zgartirmaydi. Nota/klavish nomlari alohida yashiriladi.

Klavish urilishidagi yengil zarrachalar qayta ishlatiladigan 144 elementli hovuz bilan cheklangan. Ular faqat ijro davomida chiqadi; pauza va seek eski effektlarni tozalaydi. Qurilmada reduced motion tanlangan bo‘lsa zarrachalar saqlangan sozlamadan qat’i nazar o‘chadi.

## Player sozlamalari va ovoz

Suzuvchi panel ikkita tabdan iborat:

- **Ko‘rinish:** nota va klavish nomlari, soyalar, velocity gradienti, zarrachalar, lookahead, qo‘l ranglari va ko‘rinishi.
- **Ovoz:** volume va reverb.

Tablar klaviatura va ekran o‘quvchi uchun belgilanadi. Panel ichki scroll’ga ega; tor ekranga moslashadi. MUI modal fokusni saqlaydi, Escape va yopish tugmasi bilan yopiladi. Shortcutlar panel oxirida ixcham ochiladigan ro‘yxatda.

Ko‘rinish, rang, effektlar, ovoz va tezlik qayta ochilganda saqlanadi. Kompozitsiyadagi ijro pozitsiyasi alohida saqlanadi. Qo‘llarni yashirish vizual tanlov; odatda butun kompozitsiya eshitiladi.

Ovoz mahalliy yozib olingan pianino sample’laridan keladi. Uch velocity qatlam orasida yumshoq o‘tish, yozuv darajasiga mos dinamika va stereo room reverb ustida audio adapter ishlaydi. Haqiqiy native brauzer renderida Still kirishi va zich forte akkordlari finite, clipping’siz audio berdi; aniq peak/RMS natijalari tekshiruv hujjatida. Vizual effektning o‘zi audio sifati dalili emas.

Player va uning sozlamalarida sample kredit matni yoki tashqi kredit havolasi yo‘q. Audio va font attribution’i `/licenses.html`da; Sozlamalar sahifasining pastidagi **Litsenziyalar / Лицензии / Licenses** havolasi orqali ochiladi. To‘liq litsenziyalar va sample metadata saqlangan.

## Kontent va yuklanish holatlari

Etalon — **Winter Sonata — Still**. Kontent oldindan tayyorlanadi; saytda kompozitsiya qo‘shish, variant tanlash va kontent tahriri yo‘q. Har bir Still darsida 60%/80%/100% source tezligidagi uchta alohida MIDI bosqichi, batafsil nazariya, amaliy ko‘rsatma va o‘zini tekshirish mezoni bor. Umumiy mashqlar kompozitsiyaga bog‘lanmaydi.

Kartalarda nom, yo‘nalish va kerakli metadata yetarli. Sevimlilar yurakcha bilan belgilanadi. Majburiy reja, o‘quvchining ijrosiga uydirma baho va motivatsion shior bloklari yo‘q.

Birinchi yuklanishda pianino logoli splash, sahifa/data almashganda mos skeletonlar ko‘rinadi. Skeleton kutilayotgan joylashuvni saqlaydi. Xatolik ixcham xabar va qayta urinish orqali tushuntiriladi. Sample’larning yuklanishi playerning o‘z holati; bu o‘quv progressi sifatida ko‘rsatilmaydi.

Oldindan keshlangan kontent offline ochiladi. “Offline tayyor” belgisi ko‘rsatilmaydi. Saytda o‘tkazilgan vaqt pianino ijrosiga qo‘yilgan baho sifatida talqin qilinmaydi.

## Qabul mezonlari

- Header joyida; asosiy kontent mustaqil scroll qiladi, tor ekranda keraksiz gorizontal scroll yo‘q.
- Player va 88 klavish asosiy o‘rinda; klaviatura ostida ortiqcha bo‘sh zona yo‘q.
- Sozlamalar Visual/Audio guruhlarida tushunarli, boshqaruvlar ishlaydi.
- Gradients/particles o‘chiriladi; reduced motion zarrachalarni majburan to‘xtatadi.
- Takrorlash UI’i va avtomatik qayta aylana yo‘q.
- UZ/RU/EN va dark/light’da matn, fokus va boshqaruvlar o‘qiladi.
- Loading/skeleton holatlari joylashuvni saqlaydi; offline tayyorlik belgisi va player krediti ko‘rsatilmaydi.

Joriy dalillar: [studio-verification.md](studio-verification.md). Qatlamlar: [frontend-architecture.md](frontend-architecture.md). MUI va boshqa manbalar: [THIRD_PARTY_NOTICES.md](../frontend/THIRD_PARTY_NOTICES.md).
