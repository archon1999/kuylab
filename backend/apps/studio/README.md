# Curated piano studio

The website exposes read-only musical content. The profile and personal activity
remain writable through their own APIs. `CuratedContentMiddleware` rejects legacy
content mutations and retires older curriculum reads that could create lessons.
The current API is `GET /api/studio/catalog/` plus the existing score GET endpoints.
`Accept-Language: uz`, `ru`, or `en` selects authored translations.

## Source evidence

`assets/still.mid` is a byte-for-byte copy of the file supplied by the user:
`Winter Sonata Classics - Still.mid`.

- SHA256: `f0713b1de241c28522911a907a4464504ce7fbcaa8340ad9e1589881c2f3e7c8`
- 8,938 bytes; type 1, 96 ticks per quarter; 1,092 note attacks.
- Duration: 214.60416666666666 seconds; final note releases at the file end.
- Explicit tempo: quarter = 120. No key signature, meter, pedal, arranger,
  composer, or copyright metadata is present.
- Track 0: 531 notes, MIDI 56–89, upper texture. Track 1: 561 notes,
  MIDI 28–69, lower texture. Assigning these to right and left hand respectively
  is a curated role inference, not a label recovered from the source.

All currently selected source bytes are preserved. The source is structurally complete and all its
events are included; correspondence to any published full arrangement has not
been independently verified. The file's personal-use provision does not establish
a redistribution license. No arranger/composer identity is invented.

## Authored material

The Still course contains 12 lessons with **three MIDI stages each**. The independent
curriculum contains **48 exercises in 16 families and 24 practical theory topics**,
with 49 optional activities and five paired listening comparisons. Every lesson
has a concept, a verified source-note example, listening
guidance, three practice instructions and a self-check. Uzbek includes Russian
terminology; RU and EN are authored too. Reviewed lessons live in
`still_lessons.py`; independent study definitions live in `content.py`, with
reviewed coaching in `practice_reviews.py` and `theory_reviews.py` and additional
original MIDI in `practical_midi.py`. See the [independent curriculum audit](../../../docs/practical-curriculum-review-2026-10.md).

`interactive_extensions.py` adds one more demanding application to each theory
topic, following its original foundation tasks. All 49 tasks include preparation,
an explanation available before or after checking, and authored UZ/RU/EN text.
Account-owned answer results drive learning/difficulty/mastery and remain
independent of other accounts. Main compositions retain separate player settings;
study players use the shared `study:shared` context while resume positions stay
specific to the example or stage. See the [task review](../../../docs/deeper-theory-review-2026-10.md).

The 12 lessons use source ranges 0–16, 0–20, 16–32, 48–64, 112–128,
196–214.604 and 0–10 seconds. These are teaching selections, not asserted formal
sections or printed bars. Stage 1 uses explicitly reviewed note indices at 60%
source speed. Stage 2 restores notes at 80%. Stage 3 contains every attack from
both source tracks in the window at 100%. Original pitches and velocities are
retained; time is scaled uniformly, not quantized. Key holds are clipped at the
window end. Attacks before the window are not retriggered; the full-piece link
provides context. The entire window duration is preserved, including silence.
Provenance records source SHA, event IDs, hand selection and time scale. The
original file remains byte-for-byte unchanged and keeps Score ID 2 in the live DB.

### Review, lesson by lesson — 11 October 2026

Each row was checked against the supplied MIDI, rather than inferred from the
composition title. Counts are attacks in foundation / bridge / original stages.

| Lesson | Teaching repair and progression | Notes |
|---|---|---|
| Opening listening | Explain melody vs accompaniment; selected top line → full RH with bass landmarks → both tracks. | 14 / 37 / 68 |
| Bass path | Explicit A–G–F♯–F–E landmarks replace lowest-note time buckets; explain bass vs chord root and semitones. | 10 / 55 / 92 |
| Opening LH | A2–E3–A3 interval example; first rises → full LH including returns → both hands. | 20 / 38 / 68 |
| Opening RH | Explain the E4–D5 minor seventh and G♯; melodic landmarks → complete RH → accompaniment added. | 14 / 30 / 68 |
| Together | Explain near-coincident but distinct entries; two sparse lines → full RH over bass → full LH restored. | 21 / 37 / 68 |
| Early melody | Review the top of rolled pairs explicitly; C6–B5–A5, major/minor thirds → lower pair tones → both hands. | 35 / 56 / 93 |
| Early support | Compare A/G/F♯ bass under E–A–C; bass anchors → all LH → full texture. | 10 / 37 / 93 |
| Middle RH | Identify E6–G♯5–D6 travel; top notes → complete pairs → both hands. | 35 / 54 / 107 |
| Middle balance | Distinguish loudness from balance; full RH with sparse bass → full texture slow → source speed. | 64 / 107 / 107 |
| Later LH | F2–E2–A2–D3 landing preparation; basses → intervening LH notes → RH added. | 9 / 35 / 81 |
| Ending | Sparse A/C repetitions and bass → all RH repetitions → full ending through final release; no invented pedal. | 21 / 40 / 65 |
| Timing | Distinguish pulse, note density and MIDI time unit; sparse bass → RH added → complete attacks. No invented meter. | 5 / 26 / 46 |

All stages remain freely selectable. A learner can increase player speed in small
steps, repeat comfortably and return to an easier stage without a quiz or gate.
The main-player link opens the lesson's source start, not an unrelated resume
position. Lesson stages store separate playback positions.

Theory reference cross-checks: [intervals](https://musictheory.pugetsound.edu/mt21c/Intervals.html),
[triads](https://www.musictheory.net/lessons/40),
[melody/accompaniment texture](https://viva.pressbooks.pub/openmusictheory/chapter/texture/).
These references do not supply the Still analysis; note names and timings above
come from the user's actual file.

General exercises are independently authored, with 16 families × 3 different
levels: five-finger control, scales, arpeggios, chord changes, hand coordination,
rhythm, leaps, octaves, articulation, balance, pedal, continuity, double notes,
Alberti-style accompaniment, held syncopation and within-hand voicing. Difficulty
changes musical texture/rhythm/range as well as example length. Pedal studies
include actual CC64 messages; pedal is never retroactively attributed to Still.

Theory examples cover keyboard intervals, pulse, durations, rests, intervals,
major/minor, triads, inversions, tonic/dominant, arpeggios, meter, syncopation,
legato, dynamics, voicing, pedal, phrasing, fragment practice, major scales,
natural/harmonic minor, seventh chords, voice leading, compound meter and cadences.

## Prepare or update

### Continuity path and interactive studies — 24 October 2026

Eight separately authored studies cover 0–48, 48–112, 112–196 and 196–214.604
seconds, joins at 40–56, 104–120 and 188–204, and the full supplied performance.
They are practice windows, not asserted formal sections. Foundation keeps the
highest upper-track note within each 45ms attack group and all left-track attacks
at C3 or below. Bridge restores the entire upper track over those bass landmarks.
Both keep source pitches, velocities and timing at 60% and 80% source speed. The
third stage restores all attacks at source speed. The complete path's third stage
references the original immutable score directly. No key, meter, chord root or
pedal information is invented. Original source SHA and existing stage IDs remain
unchanged. `tests/studio/test_journey.py` checks nested source-note selections and
full window duration, including omitted-note silence.

The theory catalog also contains 19 optional activities: virtual-keyboard note,
interval, triad and inversion construction, listening identification, and two
reasoning checks using the main pedal/practice examples. All prompts and feedback
are authored in UZ/RU/EN. Audition material is original. Exercises remain freely
accessible and produce no physical-performance score.

To add/update the registered repertoire without deleting existing users or progress:

```powershell
poetry run python manage.py migrate
poetry run python manage.py seed_studio
```

The optional `--replace-compositions` flag deletes unregistered Composition records
and their dependent history. Profiles are preserved. Without that flag, unrelated compositions cause
a clear refusal before mutation. A repeat run keeps stable score IDs and files.
New/changed examples create a new immutable Score version; a missing backing file
is repaired by a new version. All MIDI assets are generated and validated before
the transaction begins, and failed new files are cleaned up on rollback.

Source adaptations belong to their own composition's arrangement. Independently
authored general exercises and theory retain the Still arrangement as their
legacy storage owner, without becoming composition-specific lessons.
`StudioAsset.key` remains their stable public identity.

```powershell
poetry run python manage.py test tests.studio --settings=config.settings.test --noinput
```

Studio tests cover original bytes/metadata, every teaching asset, multilingual
identities, all stage URLs, nested private-field exclusion, uniformly scaled
timing/holds/velocity/hand, increasing source-note sets, complete final excerpts,
the taught bass/melody landmarks, ending release, missing-stage failure,
idempotence, explicit replacement, profile preservation and retired route safety.

## Six additional user-supplied performances — 25 October 2026

`repertoire.py` pins every original by SHA-256, retains the exact filename and
attributes Nino Rota from the user-supplied filename. Memories deliberately has no
invented composer or soundtrack attribution. All six exports contain two unnamed
tracks, one explicit 120-quarter-BPM tempo, no key/meter declaration and no CC64.
Upper/lower track roles are reviewed inferences, not literal physical fingering.

| Source | Notes | File duration | Main teaching observations |
| --- | ---: | ---: | --- |
| What Is a Youth | 833 | 179.375 s | Octaves, changing thirds, broken F♯–A–C♯ support, opposing register moves at 151.75 s |
| Star | 597 | 207.714 s | Long melody holds, D–F–A / A–C♯–E shapes, F6 entry, sparse ending |
| Tears in Your Eyes | 688 | 198.391 s | E♭/E contrast, repeated eight-note upper motif, final B5→C6 and held layers |
| My Memory | 1058 | 272.063 s | Staggered opening, recurring theme, high G6, dense lower texture and independent ending |
| Premonition | 784 | 229.089 s | C–B–B♭–A–A♭–G bass, broken triads, B–C–C♯ figures, closing C–E♭–G rise |
| Memories | 500 | 175.990 s | Sparse responses, A–C–E support, repeated A4 under the upper melody and E6 register change |

`repertoire_courses.py` contains 36 individually authored lesson plans in UZ/RU/EN.
`repertoire_pedagogy.py` adds reviewed listening/keyboard tasks, common pitfalls
and a source-checked onset/release example for **every** lesson. These expand each
lesson into six teaching sections. The theory distinguishes pitch collection,
actual attack order, note release, silence, voice balance and keyboard movement.

The six active files are the user's `(1).mid` replacement exports. They preserve
all 4,460 original pitches, attack times and velocities while correcting the
previous pedal-extended key holds. They still contain no CC64 messages: no pedal
curve is invented, and genuinely long notes remain intact. Exact hashes and the
lesson-by-lesson audit are in [the reexport review](reexport-review.md).

`repertoire_studies.py` compiles source-only selections into **five** stages:
landmarks at 60%, focused texture at 80%, complete texture back at 60%, complete
texture at 80%, and the original at 100%. The deliberate speed drop separates
combining hands from increasing tempo. Existing `:stage:1`, `:stage:2` and
`:stage:3` identities retain their meanings; the new `combined-slow` and
`combined-flow` stages are inserted before the original `:stage:3`.
Melody studies keep selected upper attacks, then the whole upper track;
bass studies do the equivalent for the lower track. Coordination studies restore
the full upper layer before the lower inner notes. The Memories two-voice
study specifically omits upper-track pitches below C5 to expose its A–G–F–E–D
line; the original A4 time slots are preserved.

Each piece also has four longer parts, three boundary joins and a complete-file
path. These are practice windows, not inferred formal sections or notation bars.
Sparse upper landmarks choose the highest note within 45 ms attack groups. Lower
landmarks retain the lowest original attack in each two-second study window.
These transparent reductions do not infer chord roots. All variants preserve the
selected source pitches, velocities, onsets and clipped holds under uniform time
scaling. The last complete-file stage reuses the original score and its bytes.

The complete catalog has 8 compositions, 57 lessons, 61 continuity studies, 48
independent exercises and 24 theory topics with 49 optional activities. The catalog
queries IDs and small scalar source metadata rows, avoiding every study's parsed graph.
Tests verify the exact musical landmarks, all 420 stage selections for these six
pieces, release evidence, original hashes, piece ownership, localization,
complete coverage and stable reseeding. An active source replacement creates a
new immutable Score version and retargets StudioAsset; existing composition IDs,
personal notes, progress, comfortable speeds and historical source files remain.

## All in — Soundtrack: shared course and two arrangements

`all_in_package.py` pins all thirteen supplied MIDI files. The original Full
arrangement is `composition:all-in:original`; Easy is `composition:all-in:easy`.
Both are one Composition and keep their exact source bytes. Easy is the initial
player choice, then each account's last choice is restored. Only All in opts into
the reversible compact-display reading aid; its audio and source files stay exact.
The package has sustain-off CC64 resets but no pedal-down events. Long overlapping
note-offs do not reveal physical finger releases, so compact visual lengths are
explicitly described as a reading aid.

Nine common lessons adapt the supplied PDF, nine drills and exact source passages
in UZ/RU/EN. Drill copies omit the separate percussion track and retain the
four-beat preparation, piano timings, pitches, holds and velocities. The five
continuity paths include two complete LH-only sources; the complete path ends at
the unchanged Hard performance. Main versions are not duplicated lesson catalogs.
See [the import audit](../../../docs/all-in-course-review-2026-10.md).
