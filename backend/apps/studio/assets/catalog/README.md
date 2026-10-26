# Curated piano editions · 26 October 2026

These thirty MIDI editions are bundled in the public KuyLab repository and
prepared locally during `seed_studio`. Playback never downloads external music.
The adjacent [manifest](manifest.json) pins every file's SHA-256, note count,
duration, source URL, credits, display-layer mapping and teaching windows.

The project owner explicitly stated that they hold the permissions and requested
public repository inclusion on 26 October 2026. The twenty contemporary entries
record `owner_confirmed_redistribution`, covering the MIDI files and teaching
adaptations in the website and public repository. This is the owner's confirmation,
not a claim that those compositions or transcriptions are public domain, Creative
Commons, or covered by the application's code license. Original music rights remain
with their respective holders. Unknown transcribers are identified as unknown.

The ten classical entries use the individual published terms below. The two
share-alike editions and adaptations of them retain their respective CC BY-SA
licenses. Teaching adaptations select actual source events, remove other layers
or thin landmarks, clip passage boundaries and uniformly scale time to 60/80/100%.
The full-piece path finishes at the same complete source score as the main player.
No endorsement by any source author is implied.

| Edition | Source / transcription credit | Terms |
| --- | --- | --- |
| Ode to Joy | [Mutopia 528](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=528), Peter Chubb | Public Domain |
| Prelude in C major BWV 846 | [Mutopia 5](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=5), Tobias Erbsland | Public Domain |
| Gymnopédie No. 1 | [Mutopia 37](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=37), Evin Robertson | Public Domain |
| Moonlight Sonata I | [Mutopia 276](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=276), Stewart Holmes | [CC BY-SA 2.5](https://creativecommons.org/licenses/by-sa/2.5/) |
| Für Elise | [Mutopia 931](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=931), Stelios Samelis | Public Domain |
| Prelude in E minor Op. 28 No. 4 | [Mutopia 468](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=468), Magnus Lewis-Smith | Public Domain |
| Waltz in A minor B. 150 | [MuseTrainer score library](https://github.com/musetrainer/library), score originally identified as MuseScore 1749181; KuyLab MIDI render | Public Domain |
| Nocturne Op. 9 No. 2 | [Mutopia 1590](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1590), Renato Biolcati Rinaldi | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) |
| Rondo alla Turca | [Mutopia 108](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=108), Rune Zedeler and Chris Sawer | Public Domain |
| Clair de lune | [Mutopia 1778](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1778), Keith O’Hara | Public Domain |
| River Flows in You | [Pianist8](https://github.com/joann8512/Pianist8), transcriber unspecified | Owner-confirmed redistribution |
| Kiss the Rain | Pianist8, transcriber unspecified | Owner-confirmed redistribution |
| May Be | Pianist8, transcriber unspecified | Owner-confirmed redistribution |
| Nuvole Bianche | Pianist8, transcriber unspecified | Owner-confirmed redistribution |
| Una Mattina | [MIDI Find 38414](https://midifind.com/files/l/ludovico_einaudi/ludovico_einaudi_una_mattina_2/1275-1-0-38414), transcriber unspecified | Owner-confirmed redistribution |
| Experience | [Marble Music MIDI library](https://playmarblemusic.com/midis), community edition, creator unspecified | Owner-confirmed redistribution |
| I Giorni | Pianist8, transcriber unspecified | Owner-confirmed redistribution |
| Comptine d’un autre été | [ADL Piano MIDI](https://github.com/lucasnfe/adl-piano-midi), underlying transcriber unspecified | Owner-confirmed redistribution |
| Mariage d’Amour | ADL Piano MIDI, underlying transcriber unspecified | Owner-confirmed redistribution |
| Ballade pour Adeline | ADL Piano MIDI, underlying transcriber unspecified | Owner-confirmed redistribution |
| Cornfield Chase | Marble Music MIDI library, community edition, creator unspecified | Owner-confirmed redistribution |
| Time | [ScoreBase 220030](https://scorebase.org/scores/220030), transcriber unspecified | Owner-confirmed redistribution |
| He’s a Pirate | [MIDI Find 8824](https://midifind.com/files/movies_tv_show/pirates_of_the_caribbean_he_39_s_a_pirate_piano/377-1-0-8824), transcriber unspecified | Owner-confirmed redistribution |
| One Summer’s Day | Pianist8, transcriber unspecified | Owner-confirmed redistribution |
| Merry-Go-Round of Life | [Online Sequencer 2571108](https://onlinesequencer.net/2571108), uploader unspecified | Owner-confirmed redistribution |
| La Valse d’Amélie | ADL Piano MIDI, underlying transcriber unspecified | Owner-confirmed redistribution |
| Love Story | [Online Sequencer 4524466](https://onlinesequencer.net/4524466), uploader unspecified | Owner-confirmed redistribution |
| Mia & Sebastian’s Theme | [Online Sequencer 4506732](https://onlinesequencer.net/4506732), Tmoni1738 | Owner-confirmed redistribution |
| Theme from Schindler’s List | ADL Piano MIDI, underlying transcriber unspecified | Owner-confirmed redistribution |
| My Heart Will Go On | Marble Music MIDI library, community advanced piano edition, creator unspecified | Owner-confirmed redistribution |

ADL corpus authors: Lucas N. Ferreira, Levi H. S. Lelis and Jim Whitehead.
The corpus credit does not identify the underlying transcription authors.
Pianist8 source files are pinned to commit
`4ce87d6395bc85137e12ed6caddfaf405ca6b8d9`; exact URLs and archive members are in
the manifest. All downloaded MIDI bytes are unchanged.

The sole rendered edition is Waltz B. 150: [bundled MusicXML](sources/waltz-a-minor.mxl)
is expanded with music21 10.5.1; the MIDI uses sounding pitches, separate staff
channels and explicit A-minor metadata. Forty written grace notes receive
1/8-quarter lead-in durations while principal beat positions stay fixed. Reproduce
with `ops/render_public_waltz.py` using music21 10.5.1 and mido 1.3.3 in an isolated
authoring environment. Neither library is newly required by the application.

Display colours identify reviewed staff roles or a C4 register split, not verified
physical hands or fingering. Source grid/key metadata are preserved even when a
sequencer's export grid differs from musical phrasing. MIDI key holds remain
separate from CC64 sustain; genuine long notes are not globally shortened.
The Ode to Joy file is a complete short hymn-theme reduction; Moonlight is the
first movement only. He’s a Pirate and Schindler’s List are complete short piano
arrangements of 77 and 96 seconds respectively. Other arrangements are likewise
the selected editions, not claims of identity with another publisher's score.
