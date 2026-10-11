# Curated Still studio

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

All source bytes are preserved. The source is structurally complete and all its
events are included; correspondence to any published full arrangement has not
been independently verified. The file's personal-use provision does not establish
a redistribution license. No arranger/composer identity is invented.

## Authored material

The catalog contains 12 Still lessons with **three MIDI stages each**, 36 general
exercises and 18 practical theory topics: 91 current MIDI assets including the
original. Every lesson has a concept, a verified source-note example, listening
guidance, three practice instructions and a self-check. Uzbek includes Russian
terminology; RU and EN are authored too. Reviewed lessons live in
`still_lessons.py`; independent studies remain in `content.py`.

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

General exercises are independently authored, with 12 families × 3 different
levels: five-finger control, scales, arpeggios, chord changes, hand coordination,
rhythm, leaps, octaves, articulation, balance, pedal and continuity. Difficulty
changes musical texture/rhythm/range as well as example length. Pedal studies
include actual CC64 messages; pedal is never retroactively attributed to Still.

Theory examples cover keyboard intervals, pulse, durations, rests, intervals,
major/minor, triads, inversions, tonic/dominant, arpeggios, meter, syncopation,
legato, dynamics, voicing, pedal, phrasing and fragment practice.

## Prepare or update

Back up the live SQLite database before replacing a repertoire. Then:

```powershell
poetry run python manage.py migrate
poetry run python manage.py seed_studio --replace-compositions
```

The explicit flag deletes other Composition records and their dependent history.
The Profile is preserved. Without the flag, existing unrelated compositions cause
a clear refusal before mutation. A repeat run keeps stable score IDs and files.
New/changed examples create a new immutable Score version; a missing backing file
is repaired by a new version. All MIDI assets are generated and validated before
the transaction begins, and failed new files are cleaned up on rollback.

The existing Score model requires an arrangement parent: studio examples share
the curated Still arrangement as a storage owner. Only lessons are exposed as
composition-related in the catalog; original general exercises and theory remain
independent content. `StudioAsset.key` is their stable public identity.

```powershell
poetry run python manage.py test tests.studio --settings=config.settings.test --noinput
```

15 studio tests cover original bytes/metadata, all 90 teaching assets, multilingual
identities, all 36 stage URLs, nested private-field exclusion, uniformly scaled
timing/holds/velocity/hand, increasing source-note sets, complete final excerpts,
the taught bass/melody landmarks, ending release, missing-stage failure,
idempotence, explicit replacement, profile preservation and retired route safety.
