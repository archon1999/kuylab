# Interface foundation

KuyLab uses the free **Material UI Dashboard** template's `MenuContent.tsx` as the starting code for its sidebar menu. The original two-list Stack, ListItem, ListItemButton, ListItemIcon and ListItemText composition is retained; labels, icons, selected route handling and styling are adapted to a personal piano learning workspace.

Original source: https://github.com/mui/material-ui/blob/master/docs/data/material/getting-started/templates/dashboard/components/MenuContent.tsx

Template catalog: https://mui.com/material-ui/getting-started/templates/

License: MIT, Copyright (c) 2014 Call-Em-All. Full upstream license is in `MUI-LICENSE.txt`.

The lesson cards and practice workspace use independently authored styling, informed by the functional patterns of flowkey (composition catalog), Soundslice (timeline navigation) and Piano Marvel (small practice steps). No commercial design code or brand assets were copied. Keyboard diagrams and the piano logo are independently authored. Composition lessons use the selected MIDI’s actual events; optional original drills are labeled separately.


Updated visual direction: the public Ivory homepage (https://ivory-app.com/) informed the warm cream background, brown accent, serif headings, generous spacing and restrained controls. Ivory code, logo and piano artwork were not copied. The interface uses the same open-source Alan Sans family, installed independently through Fontsource; Lora is the display serif, with Inter for Cyrillic interface text. The application retains the adapted MIT MUI navigation structure above, now arranged vertically in the left sidebar.


The curated studio uses the user-supplied **Winter Sonata Classics - Still.mid**, copied without modifying its bytes. Provenance and known/unknown source metadata are documented in `../backend/apps/studio/README.md`. No composer or arranger is invented where the file provides none. Lesson adaptations are separate, explicitly labeled teaching examples; general exercises are independently authored. Providing a personal MIDI copy does not establish a public-domain or redistribution license. The former He’s a Pirate catalog and public import interface are retired.

## Sampled piano audio

Public audio and font credits are available at `/licenses.html`, linked from
Settings. The practice player does not display an attribution banner.

The studio bundles **Salamander Grand Piano V3** recordings by **Alexander Holm**, under [Creative Commons Attribution 3.0 Unported](https://creativecommons.org/licenses/by/3.0/). The complete license is retained at [public/audio/salamander/LICENSE.txt](public/audio/salamander/LICENSE.txt).

The 90 bundled MP3 files are the unmodified three-velocity-layer subset distributed by [Tone Piano at commit 0cd2c034f820c53e83ab22f5c13bd490b9e4de85](https://github.com/tambien/Piano/tree/0cd2c034f820c53e83ab22f5c13bd490b9e4de85/audio). Original bank: [Salamander Grand Piano V3](https://archive.org/details/SalamanderGrandPianoV3). The recordings are served locally; sample selection, pitch shifting, MIDI duration/velocity and optional synthetic room reverb are applied during playback. The samples are of a Yamaha C5, not a recording of the user’s YDP-145. No author endorsement is implied.

Per-file hashes and byte sizes are in [public/audio/salamander/manifest.json](public/audio/salamander/manifest.json); source and processing notes are in [public/audio/salamander/README.md](public/audio/salamander/README.md).


## Fonts

Alan Sans, Lora and Inter are bundled locally through `@fontsource-variable` npm packages under the SIL Open Font License 1.1. Their OFL texts are retained in `public/fonts/licenses/`. Alan Sans matches the UI font observed on Ivory; Lora is an open display-serif alternative to its Freight headings. Ivory dark tokens observed on 2026-10-11: canvas `#18122b`, surface `#292043`, raised `#32284e`, text `#f5edc9`, accent `#eba165`.


## Current piano engine (2026-10-11)

- Splendid Grand Piano: AKAI Steinway recordings, Public Domain, all 226 OGG samples from https://github.com/smpldsnds/sfzinstruments-splendid-grand-piano .
- smplr 1.1.0 by danigb, MIT (npm metadata): https://github.com/danigb/smplr . Used for the sample/velocity mapping; packaged Dattorro DSP is hosted locally.
- DattorroReverbNode: Public Domain, full upstream license in `public/audio/splendid/LICENSE.txt`. Worklet modifications only add reset/dispose lifecycle handling.
- Previous Salamander samples remain archived with their original attribution; the player no longer loads them.
