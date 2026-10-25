# Deeper theory activities and automatic progress

The 24 theory topics now contain 49 optional activities. Each topic keeps its
original task IDs and gains one more demanding application with UZ/RU/EN
preparation, prompt and explanation. The activities teach concepts through a
virtual keyboard and sampled listening; physical piano input is not required.

## Content review

| Topic | Additional application |
| --- | --- |
| Keyboard | Find the half step below C5, including the B–C boundary. |
| Pulse | Keep the lower pulse while the upper part adds attacks. |
| Durations | Combine a dotted quarter and an eighth into two quarter-note beats. |
| Rests | Locate the missing third attack in a four-beat pattern. |
| Intervals | Transfer the major third from C–E to D–F♯. |
| Major/minor | Lower only the third to construct C minor. |
| Triads | Build D major using the 4 + 3 semitone formula. |
| Inversions | Identify G–C–E as the second inversion without changing chord identity. |
| Tonic/dominant | Transfer tonic/dominant functions into G major. |
| Arpeggio | Recover D minor from a changed order with repeated notes. |
| Meter | Distinguish the secondary accent in four-beat grouping. |
| Syncopation | Compare an offbeat attack with a note held across a strong beat. |
| Legato | Distinguish slight overlapping release from a tempo change. |
| Dynamics | Recognize accelerating timing at unchanged velocity. |
| Voicing | Bring out a melody by adjusting its accompaniment. |
| Pedal | Choose a pedal renewal at a harmony change; no synthetic pedal evidence. |
| Phrasing | Locate a phrase peak from the sounding dynamics. |
| Practice | Join hands slowly after isolated hands are fluent. |
| Major scale | Supply B♭ in F major and understand the enharmonic keyboard label. |
| Minor scales | Compare G and G♯ in A natural/harmonic minor. |
| Seventh chords | Build C minor seventh by changing both third and seventh. |
| Voice leading | Keep E and G while C moves down to B. |
| Compound meter | Convert quarter = 120 into dotted quarter = 80. |
| Cadences | Hear G7 resolving to C, including F–E and B–C. |

Keyboard answer sets, listening attack times, velocities, chord pitch classes and
translation coverage are checked in `test_deeper_challenges.py`. No composition
MIDI source or lesson-stage score was changed.

## Progress behavior

- Merely opening a lesson leaves its status untouched. A reading scroll of at
  least 80 CSS pixels or an intentional interaction starts an untouched item,
  after an initial two-second delay and only while the page is visible.
- Each question stores its latest submitted result. Any unresolved incorrect
  result marks difficulty. All active questions answered correctly mark mastery.
  Correcting one answer cannot hide a different unresolved error.
- Answer navigation shows completed and retry states and resumes at the first
  unfinished question. Explanations can be toggled after a correct answer too.
- Identical status controls appear at the top and bottom. Manual selection is
  preserved during reading; a new checked answer updates status again.
- Existing cards, status filters and statistics read the same progress map.
- Answer results persist locally for guests and in `PersonalLibrary` per signed-in
  account. Migration `activity.0004` adds an empty JSON field without replacing
  existing user state; older clients omitting it do not erase results.
- Progress and position limits now accommodate the existing 619 study targets.

## Player scope

All embedded study players use the account-scoped `study:shared` settings context.
Composition/variant settings, notes and per-stage playback positions remain
independent. Existing per-study preferences are retained in storage but no longer
override the common study-player settings.

## Validation

Local verification: 185 backend tests and 173 frontend tests, architecture and
format checks, type checking and production build. Browser checks cover wrong
answers and retries, all-task mastery, reload persistence, explanations after a
correct answer, repeated status controls, and shared settings across lessons.
CI additionally runs PostgreSQL, production container smoke checks and deployment.
