# Ivory audio review — 2026-10-11

Chrome’dagi foydalanuvchi ochgan Ivory playerning yuklangan JS resurslari read-only tekshirildi. Ivory ilova kodi ko‘chirilmadi; quyidagi ochiq bank va DSP ishlatildi.

## Kuzatilgan faktlar

- Player: `https://ivory-app.com/player/`; audio bundle: `/_nuxt/B3WTqAiy.js` (tekshiruv paytidagi build).
- `SplendidGrandPiano`: `https://smpldsnds.github.io/sfzinstruments-splendid-grand-piano/samples` banki; OGG/M4A, PP/MP/MF/FF real yozuvlari, 1–40 velocity uchun PP + 1000 Hz low-pass.
- `decayTime: 0.5`: nota qo‘yib yuborilgandan KEYIN release. Qisqa MIDI nota uzunligini kamaytirmaydi.
- DattorroReverb AudioWorklet, default send 0.25. Stereo modulated diffusion.
- Compressor: threshold -3 dB, knee 0, ratio 20, attack .002 s, release .2 s. Keyingi trim -1.71 dB.
- smplr velocity gain: `(velocity / 127)^2`. Master ham shu egri chiziqdan foydalanadi.

Bular texnik kuzatuvlar. Warm sample timbre, to‘g‘ri release va stereo diffusion foydalanuvchi aytgan yumshoqlikni tushuntiradi degan xulosa — muhandislik talqini; subyektiv eshitish bahosi yoki bit-for-bit Ivory tengligi da’vosi emas.

## KuyLab o‘zgarishlari

- 226 ta asl OGG yozuv (barcha 4 layer), SHA-256 manifest; `smplr@1.1.0` rasmiy MIDI xaritasi.
- URL-safe lokal nomlar: sharp (`#`) belgisi Vite’da HTML fallback berishini bartaraf qiladi. Audio baytlari o‘zgarmagan.
- 0.5 s post-note-off release. Dastlabki attack 1 ms, seek fade 8 ms, explicit pause fade 6 ms.
- Xuddi shu Dattorro DSP va default parametrlari; faqat reset/dispose xabarlari qo‘shildi.
- Dry + post-volume wet send, bir xil compressor va trim; mute/reverb-zero eski tail’ni tozalaydi.
- Play tugashida tail saqlanadi; pause/seek/restart/unmount eski ovozlarni tozalaydi.
- Default reverb 25%; foydalanuvchining oldin saqlagan qiymati o‘zgartirilmaydi.
- Offline cache `kuylab-piano-splendid-v2`: 226 sample + worklet, hash tekshiruvi. Eski Salamander banki endi player tomonidan yuklanmaydi.
- Oldingi kalibrlash/impulse kodi va unga tegishli eskirgan unit testlar olib tashlandi.

## Manbalar

- https://github.com/danigb/smplr — MIT (npm package metadata), piano mapping, release va Dattorro wrapper/DSP.
- https://sfzinstruments.github.io/pianos/splendid_grand_piano/ — Steinway/AKAI, Public Domain.
- https://github.com/smpldsnds/sfzinstruments-splendid-grand-piano — brauzerga mos original sample distribution.
- https://github.com/khoin/DattorroReverbNode — asl DSP, Public Domain (upstream LICENSE).

## Tekshiruv

- Frontend: 134/134 tests. TypeScript production build va lint o‘tdi.
- Arxitektura: 189 source file, 508 import edge, 0 violation.
- Sample manifestdagi har bir fayl hajmi va SHA-256 tekshirildi.
- Worklet impulse testi: finite stereo tail; reset barcha oldingi energiyani yo‘qotadi; dispose process’ni tugatadi.
- Native Chrome render hisobotlari va audio fayllar `artifacts/audio-review`da saqlanadi.


### Yakuniy native render — 2026-10-12

Chrome: PASS. 44.1 kHz stereo, balandlik 100%. Barcha 88 klavish uchun 226 sample decode qilindi. "Still" to‘liq 214.604 soniya + 3 soniya tabiiy tail bilan render qilindi. Playerning real ijrosi ham 3:34 chegarasida avtomatik tugadi.

| Sinov | Peak | RMS | Clipped sample |
|---|---:|---:|---:|
| Still, to‘liq, reverb 25% | 0.49996 | 0.05418 | 0 |
| 10 notali forte akkord, reverb 25% | 0.85929 | 0.11237 | 0 |
| 10 notali forte akkord, reverb 100% | 0.90592 | 0.12853 | 0 |
| Nota tugaganidan keyingi release | 0.0568 | 0.01134 | 0 |
| Dry release tugagandan keyin | 0 | 0 | 0 |
| Release tugagandan keyingi stereo xona | 0.00288 | 0.00048 | 0 |

Yakuniy fixture player kabi volume/reverb qiymatlarini prepare’dan oldin qo‘llaydi. Dry release tugagach signal nol; reverb yoqilganida esa aks-sado davom etadi. Barcha renderlar finite va clipping’siz.

Artefaktlar:
- `artifacts/audio-review/native-audio-report.json` — real Chrome o‘lchovlari.
- `artifacts/audio-review/still-steinway-full.wav` — to‘liq asar, 217.604 s, original MIDI + room tail.
- `artifacts/audio-review/still-steinway-preview.wav` — 25 s tinglash namunasi.
- `artifacts/audio-review/player-steinway.png` — asosiy player tekshiruvi.

Tinglash orqali qabul qilish foydalanuvchining didiga bog‘liq. Texnik natijalar subyektiv "premium" sifat bahosi sifatida ko‘rsatilmaydi.
