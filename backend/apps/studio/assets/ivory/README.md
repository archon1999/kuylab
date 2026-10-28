# Reviewed Ivory imports — 28 October 2026

The owner supplied 83 Performance MIDI exports and requested import into KuyLab.
The pedal-duration extension was disabled for every export. The catalog groups
these into 69 works; 14 additional performances appear as variants of those works.
Variant labels identify the supplied performer when known, otherwise a neutral
localized performance number. They do not invent Easy/Hard editions.

Six existing composition identities are retained while their active MIDI source
is replaced: Ode to Joy, Moonlight Sonata (first movement), Rondo alla Turca, Time,
He's a Pirate and My Heart Will Go On. The third movement of Moonlight Sonata is
a separate composition. Old source-specific lessons are retired from the active
catalog; their historical scores and learner records are preserved.

Maisou (Burial) uses the owner's later replacement video
<https://www.youtube.com/watch?v=68imoEsMRyw>: 1,119 notes, 310.130208 seconds,
SHA-256 `982b67ac99f1adc0e3463807e293792a2ecfe3026ef30e4e2fd840d071e9b2ba`.
Its connected musical opening contains neither shared channel-jingle signature,
so the replacement is retained without a prefix cut.

`manifest.json` pins each imported SHA-256, original export SHA-256, YouTube and
Ivory references, arrangement difficulty, preview passage and display-layer
inference. Unknown composers remain blank. The original rights are retained by
their owners; these files are not relabeled as public-domain editions.

Seventy-four exports retain every original byte. Nine reviewed recordings begin
with shared channel-jingle pitch/timing signatures also present before unrelated
pieces. Only those demonstrated prefixes were removed. The untouched exports for
these nine are retained in `originals/` for audit. Cuts are MIDI timeline seconds,
not claims about YouTube video offsets:

| Export | Cut at seconds | Omitted attacks |
| --- | ---: | ---: |
| beethoven-ode-to-joy.mid | 4.776042 | 13 |
| pirates-of-the-caribbean-hes-a-pirate-2.mid | 5.979167 | 18 |
| pirates-of-the-caribbean-hes-a-pirate-3.mid | 5.984375 | 13 |
| frozen-let-it-go.mid | 5.031250 | 18 |
| two-steps-from-hell-victory.mid | 3.447917 | 13 |
| thomas-bergersen-children-of-the-sun.mid | 3.687500 | 12 |
| ievan-polkka.mid | 4.265625 | 14 |
| skyrim-dragonborn.mid | 4.265625 | 13 |
| chariots-of-fire.mid | 4.328125 | 13 |

All retained note pitches, velocities, durations, and relative attack times are
unchanged. Source tempo/program/controller state is restored at the new origin.
No generic onset-gap trimming, quantization or removal of musical introductions
runs during preparation or deployment. Track roles are inferred from the two
musical tracks' median pitches; other layouts use a C4 display split. These
roles are visual layers, not verified physical hand or fingering information.

`build_ivory_catalog --plan <reviewed-plan.json> --source-dir <export-folder>`
validates and prepares these assets offline. Normal `seed_studio` imports them
idempotently into SQLite or PostgreSQL without downloading content or deleting
users, saved progress or historical score versions.
