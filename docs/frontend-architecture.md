# Frontend arxitekturasi

Joriy manzil: `C:\Users\Asus\Documents\KuyLab.uz\frontend`. Tuzilma `C:\Users\Asus\Documents\Deenly.uz\frontend` referensidagi app composition, modul qatlamlari, repository/DTO/mapper va sahifa papkalari tartibiga moslashtirildi. Referens loyiha o‘zgartirilmadi. Oldingi `cp_uz` talabi ushbu tuzilma bilan yangilandi.

Stack: React, TypeScript, MUI, Vite; API — Django. Mavjud mahsulot va API kontrakti saqlanadi; Deenly’ning biznes modullari ko‘chirilmaydi.

## Papkalar va qatlamlar

```text
frontend/src/
  app/
    providers/index.tsx       # profil → bildirishnoma → activity → studio
    routes/                   # app router, lazy yuklash va route boundary
    layouts/studio/           # header, sidebar, focused player shell
    theme/index.tsx           # MUI light/dark theme
    styles/                   # umumiy uslub va app chrome
  modules/
    studio/
      domain/
        entities/             # Catalog, StudyItem, StudyStage
        contracts/            # repository porti
        studio.logic.ts       # sof tanlash/filtrlash funksiyalari
      application/            # provider, katalog va score resurslari
      data-access/
        dto/                  # API response turlari
        mappers/              # DTO → domain moslashuvi
        repository/           # HTTP/kesh adapteri
      ui/
        pages/<Page>/         # Page.tsx va index.ts
        shared/               # modulga tegishli qayta ishlatiladigan UI
        studio.css
      index.ts                # tashqi public entrypoint
    practice/
      domain/                 # tempo clock, StudioTransport, preference validator
        entities/             # Score, session, preferences va timeline turlari
        contracts/            # audio va repository portlari
      application/            # player scheduler va preference controller
      data-access/
        adapters/             # sampled-piano va legacy playback adapterlari
        repository/           # score, session, player-preference implementatsiyalari
      ui/
        pages/PracticePage/   # saqlangan legacy sahifa
        shared/               # StudioPlayerView, StudioRoll, StudioTimeline
        studioPlayer.css
      studio.tsx              # konkret audio/prefs adapterlarini ulash
    activity/                 # domain entities/contracts, provider, repository
    profile/                  # shaxsiy profil, til va tema
    repertoire/               # saqlangan legacy modul
    learning/                 # saqlangan legacy modul
  shared/
    api/                      # HTTP va transport deadline/error handling
    i18n/                     # UZ/RU/EN va preference contracti
    routing/                  # URL query navigatsiyasi
    offline/                  # katalog/Score/audio cache va SW registratsiyasi
    lib/                      # lokal saqlash vositalari
    ui/                       # BrandMark, splash, skeleton va umumiy primitivlar
```

`domain` React, MUI, brauzer va HTTPdan mustaqil. `application` hook/use-case’larni beradi. `data-access` portlarni amalga oshiradi; tarmoqqa chiqish va brauzer saqlashi shu qatlamda. `ui` bevosita `fetch` yoki transport adapterini chaqirmaydi. Konkret implementatsiya public composition entrypoint yoki `app`da ulanadi.

Modul `app`ga bog‘lanmaydi, `shared` mahsulot modullarini import qilmaydi. Boshqa modulga kirish public `index`, `domain/index` yoki `application/index` orqali. App router e’lon qilingan sahifa entrypointlariga murojaat qiladi. Aliaslar: `@app/*`, `@modules/*`, `@shared/*`; relative, dynamic va type-only importlar ham AST tekshiruvga kiradi.

## Sahifalar va kontent

Faol route’lar: dashboard, kompozitsiyalar kutubxonasi, tafsilot, katta player, umumiy mashqlar, amaliy nazariya, o‘quv materiali, statistika va profil sozlamalari. `lesson` qiymati yangi `study` sahifasiga yo‘naltiriladi. Mashq va nazariya kutubxonalari bitta `StudyLibraryPage`dan foydalanadi.

`StudioProvider` `/api/studio/catalog/`ni, `useStudyScore` `/api/scores/<id>/`ni oladi. So‘rov avlodi nazorati oldingi til/score javobining yangi tanlovni almashtirishiga yo‘l qo‘ymaydi. UI eski Score’ni yangi bosqichning sarlavhasi ostida ko‘rsatmaydi.

Asosiy player to‘liq Still MIDI’sini oladi. Har darsda uchta alohida Score bor: soddalashtirilgan 60%, kengaytirilgan 80%, asl parcha 100%. `stage` URL parametri tanlangan bosqichni saqlaydi; yaroqsiz qiymat birinchi bosqichga qaytadi. Bosqich almashtirilganda avvalgi ijro to‘xtaydi. To‘liq asarga qaytish darsning manba boshlanishidan ochiladi.

Saytda kontent yozish/import, MIDI variant saralash, baholash yoki majburiy reja oqimi yo‘q. Sevimlilar, oxirgi ochilganlar, ijro pozitsiyasi va profil — shaxsiy holat.

Legacy `repertoire`, `learning`, `ScoreWorkspace`, `PracticePage`, MIDI device adapteri va manual `Sessions` regressiya uchun saqlangan. Faol router/provider daraxti ularni ishlatmaydi. Eski API’larning yopilishi backend tomonidan ta’minlanadi.

## Player, audio va sozlamalar

Public contract: `StudioPlayer({ score, compact?, onBack?, initialPosition?, onPositionChange?, onPlaybackChange? })`. Score caller tomonidan beriladi. Pozitsiya callback’i resume holatini, playback callback’i faollikni yangilaydi. Pauza, tugash va unmount audio ijrosini tozalaydi.

`StudioTransport` manba soniyalari bilan ishlaydi. Tezlik o‘zgarishi joriy joyni saqlaydi va keyingi wall-clock vaqtini o‘zgartiradi. Yarim ochiq scheduling oraliqlari chegara notalarini ikki marta chalishdan saqlaydi. Audio oxirgi source release’da tugaydi; keyingi aylana hisoblanmaydi. Qo‘lda Ijro/Boshidan bosish qayta boshlashi mumkin.

`StudioTimeline` bosish va tortishni oddiy seek sifatida ishlatadi; o‘ynatiladigan oraliq ajratilmaydi. Chap/o‘ng strelka 5 soniya, Home boshiga, timeline fokusidagi End oxiriga o‘tadi. Space — ijro/pauza, `−`/`+` — tezlik. `L`, avtomatik takrorlash, takror intervali va loop sozlamalari olib tashlangan.

Seek paytida hali jaranglayotgan notalar to‘g‘ri sample offset bilan tiklanadi. Vizual klavish ushlanishi pedal cho‘zgan jarangdan alohida. `StudioRoll` Canvas’da doim 88 klavish va ikki qo‘l rangini chizadi; nota/klavish nomlari yashiriladi, lookahead tempdan mustaqil sozlanadi. `rollVisuals.ts` MIDI velocity’dan nota gradienti va opacity’ni hisoblaydi; bu faqat ko‘rinishga ta’sir qiladi. `StrikeParticlePool` qayta ishlatiladigan 144 zarrachali hovuz: zich akkordlarda ham yangi zarrachalar soni cheklanadi. Seek/pauza effektlarni tozalaydi, `prefers-reduced-motion: reduce` ularni majburan o‘chiradi.

`data-access/adapters/sampled-piano.adapter.ts` mahalliy Splendid Grand Piano (AKAI Steinway) bankini chaladi: 226 OGG yozuv, to‘rt real velocity layer va yumshoq PPP filtri. `smplr@1.1.0` rasmiy pitch/velocity xaritasini beradi. Lokal fayllar URL-safe nomlangan; audio baytlari o‘zgarmagan. SHA-256 manifest va litsenziyalar `frontend/public/audio/splendid`da.

Nota MIDI/pedal oxirigacha to‘liq ushlanadi, keyin 0.5 soniya akustik release qo‘shiladi. Seek sample ichidagi tegishli decay offset’dan davom etadi. Master’dan alohida Dattorro stereo AudioWorklet send chiqadi; compressor va output trim Ivory’da kuzatilgan qiymatlarga mos. Pause/seek 6 ms fade, future-onset cancellation va room reset bilan bajariladi. Tabiiy tugash oxirgi nota va xona aks-sadosini kesmaydi; keyingi play avvalgi tail’ni tozalaydi. Reverb defaults 25%, avval saqlangan foydalanuvchi sozlamalari saqlanadi. Worklet lokal va offline manifestga kiradi. `tests/audio-audition.html` real OfflineAudioContext’da render qiladi va production build’ga kiritilmaydi. Tekshiruv: `docs/ivory-audio-review.md`.

`StudioSettings` Ko‘rinish va Ovoz tablarini beradi. Label, soyalar, velocity gradienti, zarrachalar, lookahead va qo‘llar birinchi tabda; volume/reverb ikkinchisida.

Player ko‘rinishi, ranglar, zarracha/gradient tanlovi, lookahead, ovoz, reverb va tezlik `StudioPreferencePort` orqali saqlanadi. Validator tur/rang/son chegaralarini tekshiradi; eski `loopDelay` hamda boshqa noma’lum maydonlarni chiqarib tashlaydi. Score ID, ijro holati va pozitsiya global preference’ga kirmaydi. Pozitsiyalar activity holatida content ID bo‘yicha saqlanadi.

## Dizayn va yuklanish

MUI theme va app CSS bir xil Ivory palitrasidan foydalanadi. Light fon `#faf8f5`, surface `#fffdfa`; dark fon `#18122b`, surface `#292043`, elevated rang `#32284e`, matn `#f5edc9`, aksent `#eba165`. Alan Sans UI, Lora sarlavha va Inter kirill yozuvidagi UI uchun ishlatiladi. Pianino belgisi shared `BrandMark` va favicon orqali izchil ko‘rsatiladi.

Header va sidebar joyida qoladi; `.main-content` viewportning qolgan qismida alohida scroll qiladi. `html/body` scroll qilmaydi. Scrollbar’lar tor, light/dark palitraga mos; fokuslangan player viewportni to‘liq egallaydi.

Boshlang‘ich splash, route/data skeleton va error/retry holatlari mavjud. Skeletonlar sahifa joylashuvini saqlaydi. Audio sample yuklanishi playerning o‘zida ko‘rsatiladi; bu o‘quv progressi sifatida talqin qilinmaydi. “Offline tayyor” readiness belgisi UI’dan olib tashlangan.

Pianino ovozi va shriftlar attribution’i `public/licenses.html`da saqlanadi. Sozlamalar sahifasining pastidagi lokalizatsiyalangan havola uni yangi tabda ochadi; playerda kredit banneri yoki tashqi sample havolasi yo‘q. Litsenziya matnlari va sample manifestlari joyida qoladi.

## Activity va offline

Sayt ko‘rinib turganda yoki ijro ketayotganda vaqt sanaladi. Kamida 300 soniyaga yetgan tashrif dastlabki besh daqiqasi bilan statistikaga kiradi. Monotonic clock, Asia/Tashkent kun chegarasi va Web Locks bir nechta tab holatini boshqaradi. Kumulyativ ID offline sinxronlashda vaqtni dublikat qilmaydi.

`shared/offline` katalog va Score’ni til bo‘yicha saqlaydi. Profil/activity API’lari service worker keshiga olinmaydi. Pianino banki manifest va SHA-256 orqali tekshiriladi. Offline tayyorlikning ichki tekshiruvi saqlanadi, lekin badge chiqarilmaydi.

`frontend/scripts/studio-sw.js` app resurslari va audio uchun. Vite production build shell manifest/revision beradi. To‘liq keshlanmagan yangi shell eski ishlaydigan workerni almashtirmaydi. Offline faqat oldindan saqlangan resurslar uchun ishlaydi.

## Tekshiruv

```powershell
npm.cmd run lint:architecture
npm.cmd test
npm.cmd run build
```

`npm run lint` arxitektura va Prettier tekshiruvlarini birlashtiradi. AST checker `scripts/check-architecture.mjs`, qatlam qoidalari testlari `tests/architecture.test.mjs`da. Aniq fayl/import/test sonlari o‘zgarishi mumkin; joriy natijalar [studio-verification.md](studio-verification.md)ga yoziladi.

Testlar audio/timeline chegaralari, MIDI tempo, preference migratsiyasi, asset hashlar, katalog/DTO mapping, activity va offline regressiyalarini qamrab oladi. Eski kodning saqlanganligi uning barcha tarixiy endpointlari yana ochilganini anglatmaydi.
