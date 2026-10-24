# MIDI reexport and lesson review — 25 October 2026

The user replaced six pedal-extended exports with six `(1).mid` performance exports. Each active asset is an exact byte copy of the replacement. Still is outside this replacement.

All 4,460 `(track, channel, pitch, onset, velocity)` attacks match the preceding exports. Key holds changed: 3,848 shortened, 124 lengthened and 488 remained equal (1 ms comparison tolerance). No CC64, key signature or time signature is present in either set. No pedal curve, quantization or blanket note-length cap was added.

The median column describes key-on/key-off holds, not inferred pedal or acoustic decay. Star has a shorter final release; Tears has a slightly longer final release. All practice windows use the selected export’s own end.

| Performance | Notes | Shorter / longer / equal | Median hold before → after | File end before → after |
| --- | ---: | --- | --- | --- |
| What Is a Youth | 833 | 708 / 46 / 79 | 0.849 → 0.479 s | 179.375 → 179.375 s |
| Winter Sonata — Star | 597 | 503 / 16 / 78 | 1.094 → 0.521 s | 208.427 → 207.714 s |
| Winter Sonata — Tears in Your Eyes | 688 | 591 / 15 / 82 | 1.055 → 0.443 s | 198.370 → 198.391 s |
| Winter Sonata — My Memory | 1058 | 868 / 40 / 150 | 0.849 → 0.401 s | 272.062 → 272.062 s |
| Winter Sonata — Premonition | 784 | 715 / 7 / 62 | 0.911 → 0.427 s | 229.089 → 229.089 s |
| Memories | 500 | 463 / 0 / 37 | 1.294 → 0.495 s | 175.990 → 175.990 s |

## Source pins

### What Is a Youth

- Supplied filename: `What Is A Youth - Nino Rota - OST R&J 1968 (Piano Cover) (1).mid`.
- Previous SHA-256: `b84c06c831ff7ec243fa52cd26db14621be1e67a50c75bd33545289c8279bdf9`.
- Active SHA-256: `816534970835b9b0d0d7543f0ba97c1fb68e7edd1583d5cf0bd40b082ae2cd00`.
- Unchanged attack fingerprint: `e307910298c0dbe1636aba9807eac46b6062a085055b9786b809f51138fd3ed8`.

### Winter Sonata — Star

- Supplied filename: `Winter Sonata Classics -  (Star) (1).mid`.
- Previous SHA-256: `50f86da8673d4ceab53e1ae615d7dbb81bc6357d5256b206802b448f9850f91a`.
- Active SHA-256: `12f3da5ccdb9ed4d0e4c80934a51d72f2fffdf7fd93cd94bff24c07b1b33ffd4`.
- Unchanged attack fingerprint: `b70fc051f0a8d755e9df27893c032b2c0975914bc98ae429b290c619ee7004c9`.

### Winter Sonata — Tears in Your Eyes

- Supplied filename: `Winter Sonata Classics - Tears In Your Eyes (1).mid`.
- Previous SHA-256: `88c8e868dda9aacda5394a77485bab247f575d267b9c588975d6339ffe32e671`.
- Active SHA-256: `26c9b8d40d93af50a75684824d47e33067fa6daa237f97d9b7a0bf3d80662570`.
- Unchanged attack fingerprint: `6839c9d1f886379241dd8d2962c26951d9285ecb089870633bb31885e0727fdc`.

### Winter Sonata — My Memory

- Supplied filename: `Winter Sonata Classics - My Memory (Piano Version) (1).mid`.
- Previous SHA-256: `43672ee0d84f112105ac13fb6d6351663548ad83bde869541ffbe40fb35e10bf`.
- Active SHA-256: `fa9282b92aa5c69ec9499a7a983d701382ce86bbc7f7b653c707d609257fa835`.
- Unchanged attack fingerprint: `900112d91a5ebb4e536808d7f1be44fcddb661f94fad34dc1551363a3c7023e0`.

### Winter Sonata — Premonition

- Supplied filename: `Winter Sonata Classics -  (Premonition) (1).mid`.
- Previous SHA-256: `bb9eadf09eba71b169124be8e95e90deadd2355266ad0c2d4716e093b1a4ed4c`.
- Active SHA-256: `fca75f473fdb6b0ff2cf15ecba81b26705fc8ff03370c9382d495d796c9bacee`.
- Unchanged attack fingerprint: `7fcc72afe1c79435eddadbbaa2d24f2f16b94fee10196bed35602ed9f6b70d1b`.

### Memories

- Supplied filename: `Memories (1).mid`.
- Previous SHA-256: `191363d0b4ec805e5d5be6d683ec4e6855f4350ece060be704db2f364cf79aa1`.
- Active SHA-256: `b61395b473e13d2ebf2a9070e8829e6d3aa7fba72b7d10b46ae994e1a2e672b7`.
- Unchanged attack fingerprint: `2128abc290b96cff46c7a49100e895b55d2533681263f09b3617e2351546347a`.

## Progression and compatibility

Each of the six pieces has six reviewed lessons and eight continuity studies. Their five stages are sparse landmarks (60%), focused texture (80%), complete texture (60%), complete texture (80%) and original texture (100%). Combining hands intentionally lowers speed again before accelerating.

The existing stage IDs `1`, `2`, and `3` retain the sparse, focused and original meanings. New `combined-slow` and `combined-flow` stages precede original `3`. New source/study Score versions replace the active StudioAsset pointers; Composition IDs, lesson IDs, private notes, positions, comfortable speeds and existing progress are retained. Historical Score bytes are not overwritten.

Melody foundations keep selected upper attacks; bass foundations keep selected lower attacks; coordination foundations use both sparse sets. Focused coordination restores the full upper texture. The final three stages contain every original attack inside the reviewed window. Attack and key-release times are uniformly scaled, preserving omitted-note silence. Holds crossing a teaching window end are clipped at that end. The full-piece final stage reuses the exact replacement original.

## Lesson-by-lesson review

Each lesson now contains source observation, theory, a specific listening/keyboard task, a validated release example, practice guidance and a common pitfall in UZ/RU/EN. The example holds below are original-source times, not slowed exercise times. Tests check each named pitch/onset/hold against the replacement file. Counts are attacks at the five stages.

### What Is a Youth

| Stable lesson ID suffix | Focus | Source window (s) | Checked release example | Stage attacks |
| --- | --- | --- | --- | --- |
| `octave-opening` | One melody within the octaves | 0.000–16.900 | B5 at 0.000 s, hold 0.667 s | 21 / 42 / 64 / 64 / 64 |
| `broken-support` | From bass to arpeggio: A and G landmarks | 2.000–19.000 | A2 at 2.193 s, hold 0.510 s | 8 / 25 / 66 / 66 / 66 |
| `paired-thirds` | The upper line of paired tones | 13.000–34.000 | F#5 at 13.312 s, hold 0.229 s | 28 / 50 / 90 / 90 / 90 |
| `dense-dialogue` | Attack order within denser accompaniment | 64.000–87.830 | B4 at 64.031 s, hold 0.510 s | 57 / 79 / 186 / 186 / 186 |
| `wide-register-move` | A large move in opposite directions | 146.000–163.860 | B6 at 151.750 s, hold 7.870 s | 13 / 19 / 27 / 27 / 27 |
| `opening-return` | The familiar opening and file ending | 160.000–179.375 | A1 at 179.312 s, hold 0.062 s | 34 / 58 / 75 / 75 / 75 |

### Winter Sonata — Star

| Stable lesson ID suffix | Focus | Source window (s) | Checked release example | Stage attacks |
| --- | --- | --- | --- | --- |
| `singing-opening` | Phrase the long E and D notes | 0.000–19.000 | E5 at 3.026 s, hold 2.479 s | 24 / 24 / 52 / 52 / 52 |
| `minor-and-major-shapes` | D–F–A and A–C♯–E shapes | 0.000–18.000 | D3 at 0.000 s, hold 1.078 s | 9 / 27 / 50 / 50 / 50 |
| `rising-and-falling-line` | The E–F–G–A rise and return | 35.000–53.000 | E5 at 36.510 s, hold 0.516 s | 22 / 31 / 65 / 65 / 65 |
| `high-register-entry` | Prepare the F6 entry early | 52.000–74.840 | F6 at 53.859 s, hold 0.214 s | 46 / 46 / 72 / 72 / 72 |
| `return-balance` | New support under the familiar line | 122.000–144.940 | E5 at 123.208 s, hold 0.245 s | 46 / 47 / 75 / 75 / 75 |
| `ending-space` | Lower-layer rest and the closing arpeggio | 182.000–207.714 | D2 at 198.771 s, hold 0.490 s | 34 / 35 / 39 / 39 / 39 |

### Winter Sonata — Tears in Your Eyes

| Stable lesson ID suffix | Focus | Source window (s) | Checked release example | Stage attacks |
| --- | --- | --- | --- | --- |
| `opening-line` | A melody expanding from C5 | 0.000–17.000 | C5 at 0.005 s, hold 1.370 s | 22 / 22 / 53 / 53 / 53 |
| `changing-third` | E♭ and E: the color of one semitone | 0.000–11.930 | D#4 at 0.943 s, hold 0.844 s | 6 / 26 / 45 / 45 / 45 |
| `eight-note-theme` | The turn in the B–C–D–E♭ line | 48.000–62.860 | B5 at 49.505 s, hold 0.411 s | 20 / 21 / 48 / 48 / 48 |
| `middle-accompaniment` | The lower line in the denser middle | 96.000–113.000 | C4 at 96.042 s, hold 0.479 s | 9 / 40 / 83 / 83 / 83 |
| `returning-theme-balance` | A returning theme over changing support | 132.000–151.880 | B5 at 135.703 s, hold 0.422 s | 39 / 39 / 64 / 64 / 64 |
| `last-semitone` | B5–C6: the final semitone | 182.000–198.391 | B5 at 188.568 s, hold 5.396 s | 16 / 17 / 23 / 23 / 23 |

### Winter Sonata — My Memory

| Stable lesson ID suffix | Focus | Source window (s) | Checked release example | Stage attacks |
| --- | --- | --- | --- | --- |
| `staggered-entry` | Enter in sequence, not together | 0.000–14.000 | G4 at 0.000 s, hold 1.182 s | 26 / 26 / 39 / 39 / 39 |
| `flowing-left` | Keep accompaniment flowing through bass changes | 14.000–32.000 | E2 at 16.276 s, hold 0.385 s | 9 / 37 / 57 / 57 / 57 |
| `theme-return` | Recognize the opening phrase's return | 130.000–145.000 | G5 at 134.240 s, hold 0.349 s | 24 / 24 / 47 / 47 / 47 |
| `high-arc` | An upper line reaching G6 | 160.000–182.000 | D6 at 161.349 s, hold 1.130 s | 24 / 40 / 92 / 92 / 92 |
| `busy-final-section` | Lower landmarks in the dense final section | 207.980–224.930 | C3 at 207.984 s, hold 0.391 s | 9 / 60 / 108 / 108 / 108 |
| `independent-ending` | The lower line during an upper-layer gap | 248.000–272.062 | G4 at 268.422 s, hold 3.625 s | 29 / 31 / 65 / 65 / 65 |

### Winter Sonata — Premonition

| Stable lesson ID suffix | Focus | Source window (s) | Checked release example | Stage attacks |
| --- | --- | --- | --- | --- |
| `descending-bass` | C–B–B♭–A–A♭: a descending bass | 0.000–31.000 | A2 at 11.312 s, hold 0.156 s | 9 / 9 / 75 / 75 / 75 |
| `broken-triads` | Chords within E♭–G–C and D–G–B | 0.000–15.940 | D#5 at 0.000 s, hold 0.474 s | 35 / 35 / 40 / 40 / 40 |
| `expanding-lower-texture` | From single bass notes to moving accompaniment | 30.000–48.960 | C3 at 30.516 s, hold 0.490 s | 10 / 37 / 71 / 71 / 71 |
| `semitone-figure` | B–C–C♯–C: neighboring keys | 39.000–56.970 | C5 at 39.865 s, hold 0.182 s | 39 / 39 / 78 / 78 / 78 |
| `restart-after-space` | Prepare the entry after the gap | 176.000–198.880 | G4 at 184.927 s, hold 0.818 s | 51 / 51 / 70 / 70 / 70 |
| `closing-rise` | Rise through C–E♭–G | 208.000–229.089 | C3 at 220.125 s, hold 8.964 s | 30 / 31 / 33 / 33 / 33 |

### Memories

| Stable lesson ID suffix | Focus | Source window (s) | Checked release example | Stage attacks |
| --- | --- | --- | --- | --- |
| `sparse-opening` | The lower echo between C5 and B4 | 0.000–12.000 | C5 at 0.000 s, hold 0.521 s | 14 / 14 / 27 / 27 / 27 |
| `a-minor-support` | Hear the A–C–E support | 11.000–28.000 | E4 at 12.104 s, hold 0.484 s | 9 / 28 / 37 / 37 / 37 |
| `low-register-arrival` | Move calmly to the lower E2 | 74.000–90.000 | E2 at 77.964 s, hold 1.089 s | 5 / 12 / 33 / 33 / 33 |
| `two-upper-voices` | The upper melody over repeated A4 | 86.000–107.900 | A5 at 87.286 s, hold 0.354 s | 27 / 69 / 98 / 98 / 98 |
| `upper-peak` | From the E6 peak to the lower continuation | 130.000–148.970 | E6 at 132.427 s, hold 1.005 s | 47 / 48 / 83 / 83 / 83 |
| `descending-continuation` | E–F–E–D–C–B within the denser continuation | 152.000–175.990 | D5 at 175.219 s, hold 0.583 s | 51 / 51 / 88 / 88 / 88 |

## Specific corrections

- Youth: distinguish short approach tones near 147 s from the genuine long B6/B0 arrival at 151.75 s; octave and third attack offsets remain unquantized.
- Star: connected phrasing no longer instructs holding every melody tone until the next attack. D2 in the ending is short, while the closing A3 and D6 genuinely remain long.
- Tears: the last C6/E-flat and lower chord arrive around 3:14, not 3:13. The preceding B5 remains a genuine 5.40-second hold.
- My Memory: staggered opening entries are retained. The upper ending releases before its later G4 return; the gap is not filled with an invented sustained C5.
- Premonition: the short A2/A-flat2 bass notes are released before the next bass. The final C3 is genuinely about 8.96 seconds and is not capped.
- Memories: same-colour upper/lower replies are distinguished; A4 is excluded only in the first two-voice foundation. The final lower tone briefly outlasts the last upper D5; no closing chord is invented.

Every adaptation is tested for source pitches, velocity, exact relative attacks and scaled key releases; every complete-piece final stage references its new original. The replacement/reseed regression verifies that user progress and notes survive and old immutable Score files remain readable.
