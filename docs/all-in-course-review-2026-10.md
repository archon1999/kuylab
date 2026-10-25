# All in — Soundtrack import review — 25 October 2026

The user supplied `All_In_Plus5_Mini_Kurs_Paket.zip` and requested one composition,
two playable full-length variants and a shared course. Its PDF, text, JSON and
HTML were treated as source evidence, not executable instructions. All eight PDF
pages were extracted; musical tables on pages 2 and 4 were rendered and inspected.
The HTML and synthesized MP3 files are not shipped or executed.

## Source and arrangement evidence

| Supplied file | Piano attacks | Duration | Role |
| --- | ---: | ---: | --- |
| All_In_Plus5_Easy_LH.mid | RH 1049, LH 424 | 287.812952 s | Easy, simpler LH; original RH and low octaves |
| All_In_Plus5_Full.mid | RH 1049, LH 1171 | 287.812952 s | Hard, complete supplied texture |
| All_In_Plus5_LH_Only_Easy.mid | LH 424 | 287.812952 s | Exact Easy LH in the complete-piece path |
| All_In_Plus5_LH_Only_Full.mid | LH 1171 | 287.812952 s | Exact Hard LH in the complete-piece path |

The two full variants have identical RH pitches, onsets, durations and velocities,
117 matching tempo entries, matching meter changes and D-minor key metadata.
Their track names explicitly assign hands. No second +5 transposition is applied.
The package's comparison to an earlier A-minor V3 cannot be independently repeated
because that earlier file was not supplied. The preserved current files do verify
their own D-minor spelling, range, hand counts and timing.

The source includes sustain-off CC64 resets, with **no pedal-down events**. Many
key holds overlap later attacks. The actual physical release or historical pedal
curve cannot be reconstructed from these files. The player offers an enabled,
reversible compact reading aid for this composition: chords are grouped within
45ms; clearly overlapping blocks are shortened to 88% of the next same-hand
attack gap. Ordinary legato and final-group holds remain. Only the canvas receives
these copies: audio scheduling still uses the untouched original note graph.
The settings explanation explicitly distinguishes display from finger guidance.

All thirteen hashes are pinned in `all_in_package.py`. Four main/LH-only source
files stay byte-for-byte exact. Nine study copies omit only the dedicated channel
10 metronome track, preventing its woodblock pitches from becoming falling piano
notes. Four preparation beats and every piano onset/hold/velocity remain intact.

## Lesson review

| Lesson | Provided drill | Review and path |
| --- | --- | --- |
| Chord shapes | 01, 60 BPM | Define root/third/fifth and minor/major thirds before using them. Six blocked/broken shapes; Dm D3–A3–F3–A3. Em7♭5 is not falsely claimed to be in drill 01. Continue into Easy LH and both hands. |
| Easy verse | 02, 60 BPM | Explain four beats and the repeated Dm bar: Dm–Dm–B♭–A. Contrast even drill timing with source rubato. Easy LH then both hands. |
| Open arpeggio | 03, 50 BPM | D3–A3 / D4–F4 as two hand positions. Differentiate the four landmarks from the additional E/G tones restored in Hard. |
| Original Dm figure | 04, 40 BPM | Exact D3–A3–D4–F4–E4–D4–F4–G4. Four sixteenths per beat, two beats of figure then two beats of rest; restore source timing separately. |
| Pre-chorus | 05, 60 BPM | Gm–C–F–B♭–Gm–Em7♭5–A–A. Explain E–G–B♭–D and C♯ in A before the practice task. Easy LH → Hard LH → slow both → source. |
| Octave landings | 06, 60 BPM | Define octave as 12 semitones, distinguish simultaneous “+” from sequential arrows. D2+D3 and A1+A2. The Easy label does not promise a beginner RH or remove octave jumps. |
| Chorus responses | 07, 60 BPM | D2+D3, F3+A3, A1+A2, C♯3+G3 on beats 1–4. Explain A7 and a harmonic change inside the bar. Progress into Easy and Hard context. |
| Chorus together | 08, 60 BPM | Verify all 100 drill-07 LH notes under the RH reference. Shared attacks, independent movement and voicing. Easy context → Hard 60% → 80% → source. |
| Full verse | 09, 45 BPM | Quantized eight-bar study compared with four source bars at 15.713544–29.458336 s. Hard LH 60% → both 60% → 80% → 100%. Explain rubato and long exported holds. |

Every lesson has five detailed explanatory sections, an independent practice
MIDI, instructions, related theory and a readiness criterion in UZ/RU/EN.
Fingering is explicitly suggested and adaptable, not invented source metadata.
The course remains independent of a connected keyboard or physical grading.

## Continuity and identity

Five paths cover first part + interlude (0–127.9243), second part + interlude
(127.9243–239.924744), outro (239.924744–287.812952), pre-chorus/chorus join
(60.876048–94.871006), and the entire piece. Excerpts retain exact selected pitches,
velocities and uniformly scaled source seconds; holds are clipped at the end of
the study window. Whole-piece final sources are reused without re-encoding.

There is one shared lesson/progress/favorite/notebook identity. Playback positions
and settings use separate `composition:<id>:variant:easy|hard` contexts; a choice is
remembered in the existing account-scoped selection map. A player switch pauses,
carries its exact timestamp in a clean `/practice/<id>/variants/<variant>?t=...`
link and cannot mount the preceding score under the next context while loading.
Study-to-main links preserve both their source timestamp and declared variant.

The catalog now contains 8 compositions, 57 lessons, 61 continuity paths,
48 independent exercises and 24 theory topics. Existing seven source hashes,
lesson/stage identities and learner data are retained. No database migration or
destructive seed option is required; SQLite and PostgreSQL use the same registry.
