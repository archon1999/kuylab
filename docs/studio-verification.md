# KuyLab tekshiruvlari

11 oktabr 2026. Joriy ish: loyihani `C:\Users\Asus\Documents\KuyLab.uz`ga ko‘chirish, Deenly asosidagi arxitektura, Ivory tipografiya/ranglari, yangi logo/yuklanish holatlari va avtomatik takrorlashni olib tashlash.

## Joriy tekshiruv holati

**Yakuniy lint, format, test va production build o‘tdi.** Quyidagi natijalar ko‘chirilgan workspace va yangilangan frontend/backendga tegishli.

- Frontend to‘liq **139/139 test**, TypeScript va Vite production build o‘tdi. Arxitektura tekshiruvi: **189 source fayl, 506 import, 0 buzilish**; Prettier format tekshiruvi toza.
- Backend app/test/settings ko‘chirilishi va matn-only seed regressiyasidan keyin to‘liq **112/112 test** o‘tdi; Poetry check/install, `manage.py check` va `makemigrations --check --dry-run` toza. Buyruq quyida.
- Backend dars matnlaridan endi mavjud bo‘lmagan timeline loop va repeat pause ko‘rsatmalari UZ/RU/EN bo‘yicha olib tashlandi. Musiqiy takroriy notalar va qo‘lda mashq qilish izohlari saqlangan. Katalog reviziyasi `still-studio-2026-10-v3`; qayta seed barcha 91 asset Score ID’si, 103 Score versiyasi, profil, shaxsiy kutubxona va tashriflarni saqlagan.

## Qayta bajariladigan buyruqlar

Backend katalogida:

```powershell
poetry run python manage.py check
poetry run python manage.py makemigrations --check --dry-run
poetry run python manage.py test tests --settings=config.settings.test --noinput
```

Frontend katalogida:

```powershell
npm.cmd run lint
npm.cmd test
npm.cmd run build
```

Loyiha ildizida:

```powershell
python ops/verify_workspace.py
```

Backendning barcha 112 testi alohida test DB’da ishlaydi. Joriy studiya regressiyalarining 35 tasi: studio 15, activity 6, lokal API/profile 5, MIDI parser 9. Legacy authoring testlari faqat test ichida read-only cheklovni aniq o‘chiradi; studio testlari uni yoqilgan holatda tekshiradi. Bu legacy API’larning ishlayotgan ilovada ochilganini anglatmaydi.

## Yangilangan player uchun tekshirish mezonlari

- Hech bir playerda takrorlash tugmasi, `L` shortcut, avtomatik aylana, parcha tanlash yoki takror tanaffusi bo‘lmaydi.
- Timeline click/drag — oddiy vaqtga o‘tish. Klaviatura orqali 5 soniya surish, Home/End, temp va pauza ishlaydi.
- Ijro oxirgi source release’da to‘xtaydi; uzoq vaqt yashirin qolgan tab ham keyingi aylana yaratmaydi. Qo‘lda qayta boshlash ishlaydi.
- Eski brauzer sozlamasidagi `loopDelay` va range yangi sozlamaga ko‘chmaydi. Ovoz, tezlik, label va lookahead saqlanadi.
- Oddiy sahifa hamda playerda light/dark ranglar, logo, yuklanish skeletonlari, tor ekran va xatolik/retry holatlari tekshiriladi.
- Header/sidebar joyida turadi; faqat kontent scroll qiladi. Ingichka scrollbar light/dark’da ko‘rinadi, body’da ikkinchi scrollbar paydo bo‘lmaydi.
- Player sozlamasida Ko‘rinish/Ovoz tablari, velocity gradienti va zarrachalar tanlovi tekshiriladi. Zarrachalar 144 bilan cheklangan; reduced motion saqlangan tanlovdan ustun, seek/pauzada eski zarrachalar qolmaydi.
- Player va sozlamalarida sample kredit matni bo‘lmaydi. Profil Sozlamalaridagi Litsenziyalar havolasi `/licenses.html`ni yangi tabda ochadi; audio/font manbalari va to‘liq litsenziya havolalari saqlangan.
- Offline readiness belgisi ko‘rinmaydi. Oldindan saqlangan app/katalog/Score/sample keshi saqlanadi.

Litsenziya sahifasi va uning to‘rtta lokal to‘liq-litsenziya havolasi HTTP 200 bilan tekshirilgan. Audio engine’ning haqiqiy native brauzer renderi quyidagi Grand piano bo‘limida keltirilgan.

## Joriy brauzer dalillari

- Footer butunlay olib tashlandi; menyu, sahifa sarlavhasi va darsga qaytish havolalarida “Mashqlar” nomi ishlatiladi. Brauzerda footer elementlari soni 0, eski nom yo‘q; RU/EN nomlari “Упражнения” / “Exercises”.
- Player sozlamalari 480 × 800 CSS viewport’da ekranga sig‘di, document width 480 px; tekshiruvdan keyin viewport override olib tashlandi. Ijro 03:34 da avtomatik takrorlanmay to‘xtadi.
- Kontent 345 px aylantirilganda uning yuqori cheti 84 px, header Y koordinatasi 0 va window scrollY 0 bo‘lib qoldi. Scrollbar eni 7 px: [content-scroll-light.png](../artifacts/ui-refresh/content-scroll-light.png).
- Dark playerda ijro va vaqtning siljishi, Pauza holati hamda Ko‘rinish/Ovoz tablari tekshirildi: [player-dark-settings.png](../artifacts/ui-refresh/player-dark-settings.png). Asl MIDI manbasi o‘zgarmagan.
- Brendli splash va sahifa skeletoni uchun joriy rasmlar: [splash-dark.png](../artifacts/ui-refresh/splash-dark.png), [page-skeleton-light.png](../artifacts/ui-refresh/page-skeleton-light.png). Yakuniy Mashqlar sahifasi: [exercises-final.png](../artifacts/ui-refresh/exercises-final.png).

Barcha viewport, brauzer va offline holatlar ushbu desktop sinovi bilan qamrab olingan deb hisoblanmaydi. Production offline qayta yuklashning oldingi dalili alohida tarixiy bo‘limda saqlangan.

## Katalog va manba

Bitta Still kompozitsiyasi, **12 dars, 36 umumiy mashq, 18 nazariya**. Har darsda 3 alohida MIDI bosqichi, asl kompozitsiya bilan jami **91 joriy asset**. Har bir o‘quv materialida tushuntirish, amaliy ko‘rsatma va haqiqiy MIDI bor.

Asl `backend/apps/studio/assets/still.mid`:

- SHA256: `f0713b1de241c28522911a907a4464504ce7fbcaa8340ad9e1589881c2f3e7c8`.
- 8 938 bayt, type 1, PPQ 96, 1 092 nota, 214.60416666666666 soniya.
- Track 0: 531 nota, MIDI 56–89; Track 1: 561 nota, MIDI 28–69.
- Chorak = 120. O‘lchov, tonallik, pedal, muallif/aranjirovkachi belgisi yo‘q.
- Qo‘l vazifalari yuqori/pastki trekdan chiqarilgan kuratsiya talqini. Nashr bilan alohida qiyos qilinmagan.

Birinchi ikki dars bosqichi qo‘lda tanlangan manba notalaridan, 60%/80% tezlikda tuzilgan. Uchinchi bosqich manba oralig‘ida boshlangan barcha notalarni 100% vaqtda qaytaradi. Pitch, velocity va qo‘l saqlanadi; vaqt bir xil nisbatda sekinlashadi. Oxirgi ushlash chegarada kesiladi; boshlanishdan oldin bosilgan nota qayta yaratilmaydi. [Darslarning review jadvali](../backend/apps/studio/README.md#review-lesson-by-lesson--11-october-2026).

Ko‘chirilgan workspace’da `python ops/verify_workspace.py --manifest runtime/backups/before-architecture-integrity.json` muvaffaqiyatli bajarildi: SQLite integrity OK, 91 joriy asset, original Still Score ID 2; oldingi **199 media faylining barcha SHA-256 hash’i teng**, source checksum o‘zgarmagan. Backuplarning joriy joyi `runtime/backups`. Ushbu buyruq bazani read-only ochadi.

## API chegarasi

Faol API’lar: `GET /api/studio/catalog/`, `GET /api/scores/<id>/`, `GET /api/scores/<id>/file/`; profil uchun GET/PATCH; activity state uchun GET/PATCH va visits uchun GET/PUT.

Eski kontent yozuvlari 405, retired overview/curriculum/lesson/session/demo o‘qishlari 410 bilan rad etiladi. Katalog GET eski dars yaratmasligi, profil va faollik yozuvlari esa ishlashi testlarda tekshiriladi. Ruxsat etilgan faollik saytda o‘tkazilgan vaqtni bildiradi, real ijro sifati bahosini emas.

## Oldingi versiyaning tasdiqlangan dalillari

Quyidagilar ko‘chirish va dizayn yangilanishidan **oldingi** versiyaga tegishli. Ular yangi UI tekshiruvi deb hisoblanmaydi.

- 121 frontend va 34 backend testi, TypeScript/Vite build o‘tgan. Arxitektura graph’i o‘sha vaqtda 106 source fayl, 359 import va 0 buzilish edi.
- Still darslarining barcha UZ/RU/EN stage linklari ochilgan; har darsda birinchi bosqich notalari ikkinchisida, ikkinchisidagilar uchinchisida mavjudligi testlangan. Bass A2–G2–F♯2–F2–E2 va yuqori C6–B5–B5–A5 misollari manba bilan solishtirilgan.
- Bass darsining 60%/80%/100% bosqichlari 33/25/20 soniyadan ochilgan, bosqich almashishi eski ijroni to‘xtatgan. To‘liq asarga qaytish yuqori registr darsidan 00:48 da ishlagan. URL stage tanlovi to‘liq reloadda tiklangan.
- Production offline sinovida tarmoq uzilib, to‘liq reloaddan keyin katalog, darslar va player ishlagan. WebAudio realtime context va sample voice’lar tekshirilgan. Bu offline mexanizmi ishlaganining dalili, yangi dizaynning final regressiyasi emas.
- Dashboard, kutubxona, dars, mashq, nazariya, statistika va profil navigatsiyasi, tillar, 5 daqiqalik faollik chegarasi va tor ekran tekshirilgan.

Oldingi dars skrinshoti: [still-lesson-stages.png](../artifacts/studio-final/still-lesson-stages.png). Oldingi dashboard/player skrinshotlari `artifacts/studio-final`da. Ular joriy vizual natija sifatida ko‘rsatilmaydi.

Dars review oldi backup: `runtime/local-dev/backups/before-still-lessons-20261011-224427.sqlite3`. Dastlabki kompozitsiya almashtirish oldi backup: `runtime/local-dev/backups/before-still-20261011-215847.sqlite3`. Original Score 2 saqlangan; eski Score versiyalari dars review paytida o‘chirilmagan.

## Grand piano ovozi — haqiqiy brauzer renderi

`frontend/tests/audio-audition.html` Vite development serverida ochildi va **Render audio checks** bosildi. Test fixture ishlab chiqarish build’ining entry yoki public asset’i emas. U alohida emulyatsiya emas, joriy `sampled-piano.adapter.ts`, haqiqiy mahalliy MP3 banki va brauzerning native `OfflineAudioContext` node’lari bilan 44.1 kHz stereo audio yaratadi. Sahifadagi WAV yuklab olish va audio elementlari natijani qayta tinglash imkonini beradi.

| Haqiqiy render | Peak (linear) | RMS | Clipped sample |
| --- | ---: | ---: | ---: |
| Still, dastlabki 25 soniya + xona dumi | 0.40838 | 0.05500 | 0 |
| Bir vaqtda 10 ta nota, velocity 127 | 0.96914 | 0.09688 | 0 |

Ikkala natija ham finite stereo audio berdi. Forte sinovi 100% player volume’da o‘tkazilgan. Bu tekshirilgan ijrolarning headroom dalili; barcha mumkin bo‘lgan MIDI fayllari clipping qilmasligi haqida kafolat emas.

C4 velocity ketma-ketligining attack’dan keyingi RMS qiymatlari: `40 → 0.04459`, `54 → 0.05006`, `55 → 0.05064`, `56 → 0.05165`, `80 → 0.07708`, `99 → 0.09747`, `100 → 0.09636`, `101 → 0.09700`, `120 → 0.12703`. Oldingi 55/100 chegaralarda keskin sample almashishi endi yo‘q. 100 atrofidagi kichik (~0.1 dB) mahalliy farq alohida yozilgan take’larning aralashishiga mos; matematik dynamic target monoton, haqiqiy audio RMS’i mutlaq monoton deb da’vo qilinmaydi.

**Oldingi dvigatel tekshiruvi; joriy Steinway natijalari `ivory-audio-review.md`da.** Ovoz banki o‘sha bosqichda: 90 ta mahalliy Salamander Yamaha C5 sample. Dvigatelga tor velocity crossfade, yozuvlarning attack/body energiyasiga mos gain, bitta nota uchun peak chegarasi, master headroom va forte akkordlar uchun compressor qo‘shildi. Qisqa attack/seek fade, MIDI/pedal oxiridan chiqmaydigan damper envelope va yuqori/past chastotalari yumshatilgan stereo xona ishlatiladi. Uzoq seek sample oxiridan o‘tib ketganda oxirgi millisekund qayta chalinmaydi.

15 ta audio testi o‘tdi; shu integratsiya nuqtasida umumiy frontend natijasi **139/139**, TypeScript toza va architecture checker **189 fayl / 506 import / 0 buzilish**. Regressiyalar velocity chegaralari, gain/headroom, stereo impuls, bir xil onset/end, seek/pedal davomiyligi, pauzada click-free fade va voice cleanup’ni qamrab oladi. DSP qoidalari [Web Audio spetsifikatsiyasi](https://www.w3.org/TR/webaudio/) asosida tekshirildi.

## Amaliy chegaralar

Lokal bitta profil uchun. Public deployment, ko‘p foydalanuvchili login, barcha qurilmalar va uzoq muddatli ta’lim samaradorligi ushbu tekshiruv doirasiga kirmaydi. YDP-145’ni ulash talab qilinmaydi; fizik MIDI baholash/ijro yozuvi joriy oqimda yo‘q. Salamander yozuvlari foydalanuvchining Yamaha’sidan yozilgan ovoz emas.



## 2026-10-12 — standalone errors and interface polish

- Authenticated and anonymous 404 screens use the standalone error layout. Missing-study errors also remove the header/sidebar; returning home restores navigation. Verified in Chrome with zero header/aside/nav elements on error routes and no console errors.
- A reusable musical EmptyState covers dashboard favorites/recent items, exercise/theory filter results, empty composition libraries, absent composition lessons, and statistics. Filter clearing was checked in the browser. UZ/RU/EN copy and light/dark tokens are shared. A 390 px viewport had no horizontal overflow.
- Auth language controls and light/dark controls share a compact segmented row beneath the brand. Guest appearance/language are persisted separately from account preferences. The mistakenly requested top-right placement, medium inputs and forced no-scroll auth/error layouts were reverted; the later inline switch request is retained.
- Uzbek account terminology is now “Akkaunt” in registration, sidebar and account-creation fallback errors. “Hisob” in musical calculations is intentionally unchanged.
- Frontend: 140 tests pass; TypeScript, architecture (200 files / 559 edges), formatting and production build pass. Backend: 126 tests pass.
- Visual evidence: artifacts/multiuser-review/404-standalone.png, empty-states.png and auth-switches.png. Browser checks used a disposable local account, not the owner's account.
