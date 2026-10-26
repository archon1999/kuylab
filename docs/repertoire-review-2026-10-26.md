# Thirty piano editions and introductory courses

All thirty candidates are included alongside the eight existing compositions.
The complete catalog now has 38 compositions, 147 composition lessons, 91
continuity paths, 48 independent exercises and 24 theory topics. Existing source
files, content IDs, progress and saved practice positions retain their identities.

Each added composition has three focused lessons: melodic line, bass/accompaniment,
and coordination. Each contains a piece-specific explanation in Uzbek, Russian and
English, definitions before tasks, and four concrete pitch/onset examples read from
its actual source window. The complete-piece course covers the entire selected
edition. These are introductory courses, rather than a claim of a full conservatory
curriculum for every work.

All four paths offer five separately playable stages:

1. Sparse melodic/bass landmarks at 60% source speed.
2. The focused layer, or full upper texture over sparse bass, at 80%.
3. Every source note in the passage at 60%.
4. The same complete note set at 80%.
5. Every source note at 100%; a complete-piece finale reuses the main player score.

Pitch, velocity, source attack order and key releases are retained. Time is scaled
uniformly; passage endings are clipped explicitly. There is no automatic looping.
Tests compare each generated stage with its selected source events and check that
the complete stages contain equal sets. Preview tests verify every overlapping
source event, rather than a decorative or melody-only sample.

Two source staves are mapped where available. Ten one-track files use a declared
C4 register split for display colours; this is not reconstructed physical fingering.
Theory therefore describes upper/lower layers and does not invent finger numbers.
Sequencer grids are retained as source metadata, not presented as authoritative
printed measures. The Waltz rendering documents its grace-note realization.

Rejected candidates included melody-only Merry-Go-Round, a 36-second Mia fragment,
an orchestral Time, a guitar Nuvole Bianche, an accompaniment-only Titanic file and
an Experience export with a long trailing silence. Full selected piano editions
replace these candidates. Source provenance and individual license/owner permission
records are bundled in the [catalog notices](../backend/apps/studio/assets/catalog/README.md).

The Ode to Joy hymn-theme reduction contains chords and is rated 2 stars instead
of the planned single-line 1-star version. The selected Love Story and advanced
Titanic editions are rated 3 and 4 stars respectively after texture review.
He’s a Pirate and Schindler’s List are complete short arrangements, not claimed
to match every measure of another published version. Moonlight contains movement I.

Music21 is an isolated authoring dependency for the public-domain Waltz only.
The server still uses its existing MIDI parser and installs no new runtime package.
All thirty final MIDI files are pinned and available without external downloads
on SQLite locally and PostgreSQL in production.

| Edition | Stars | Duration | Notes | Preview starts |
| --- | --- | --- | --- | --- |
| Ode to Joy | 2 | 0:38 | 238 | 0 s |
| Prelude in C major · BWV 846 | 2 | 2:20 | 549 | 0 s |
| Gymnopédie No. 1 | 2 | 2:21 | 282 | 8 s |
| Moonlight Sonata · I | 3 | 4:36 | 1142 | 8 s |
| Für Elise | 4 | 2:10 | 905 | 0 s |
| Prelude in E minor · Op. 28 No. 4 | 3 | 1:48 | 600 | 0 s |
| Waltz in A minor · B. 150 | 3 | 2:00 | 920 | 0 s |
| Nocturne · Op. 9 No. 2 | 4 | 3:22 | 1242 | 0 s |
| Rondo alla Turca | 4 | 4:15 | 1614 | 0 s |
| Clair de lune | 5 | 5:22 | 1468 | 0 s |
| River Flows in You | 3 | 3:29 | 1124 | 16 s |
| Kiss the Rain | 3 | 4:13 | 1432 | 24 s |
| May Be | 3 | 4:16 | 1210 | 8 s |
| Nuvole Bianche | 3 | 5:49 | 2650 | 24 s |
| Una Mattina | 3 | 3:12 | 742 | 8 s |
| Experience | 4 | 5:50 | 2630 | 32 s |
| I Giorni | 3 | 5:57 | 1969 | 16 s |
| Comptine d’un autre été : L’Après-midi | 3 | 2:21 | 811 | 8 s |
| Mariage d’Amour | 4 | 4:01 | 1137 | 16 s |
| Ballade pour Adeline | 3 | 2:49 | 844 | 8 s |
| Cornfield Chase | 3 | 2:06 | 1311 | 16 s |
| Time | 3 | 4:47 | 541 | 32 s |
| He’s a Pirate | 4 | 1:17 | 1255 | 8 s |
| One Summer’s Day | 4 | 3:45 | 960 | 16 s |
| Merry-Go-Round of Life | 4 | 5:17 | 2344 | 32 s |
| La Valse d’Amélie | 3 | 2:37 | 766 | 8 s |
| Love Story · Theme | 3 | 2:23 | 742 | 8 s |
| Mia & Sebastian’s Theme | 3 | 2:03 | 572 | 0 s |
| Theme from Schindler’s List | 3 | 1:36 | 816 | 8 s |
| My Heart Will Go On | 4 | 4:41 | 1369 | 24 s |
