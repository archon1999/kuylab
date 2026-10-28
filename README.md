# KuyLab

A composition-first piano learning studio built with Django, React, TypeScript and
MUI. Learn with a falling-note MIDI player, separately authored composition
lessons, general exercises and music theory. Interface languages: Uzbek, Russian
and English; light and dark themes.

Each account has its own favorites, playback positions, learning progress,
preferences and activity statistics. The musical catalog is curated in code;
users do not upload or edit shared content through the website.

Personal timestamp notes open the player at the saved moment and can be edited or
removed with undo. Color-coded learning status is stored per lesson stage and
appears on study cards, filters and statistics. Sound, appearance, visible key
count and playback speed share one settings profile per account across all
players. Playback positions remain separate.
Still includes eight continuity studies (four
parts, three joins and a full-piece path) alongside its 12 lessons. The independent
curriculum has 48 exercises in 16 families and 24 theory topics, each with a
source-matched MIDI explanation, practice method, pitfalls and a self-check.
Theory includes 49 optional keyboard/ear activities with explanations and sampled
piano audition, including a deeper application task in every topic. Answers are
saved per account: a wrong answer marks a difficulty, and completing every task
marks mastery. Reading or interacting starts an untouched lesson; opening a route
alone does not. The status controls at the top and bottom also allow manual
updates. Activities do not grade physical playing or lock other lessons.

The dashboard resumes unfinished recent studies and stages. The composition
library offers arrangement-specific 1–5-star difficulty, search, collection and
favorite filters, sorting and pagination. Each card previews all source notes in
a reviewed passage with a paused falling-note preview, synchronized keys and
sampled piano audio after pressing Play.
The [30-piece candidate list](docs/repertoire-candidates-2026-10-26.md) records
repertoire choices and sources for the playable catalog.

## Structure

- `backend/apps`: learning, scores, studio and activity domains.
- `backend/config/settings`: local SQLite, test SQLite/PostgreSQL, production PostgreSQL.
- `frontend/src/app`: routes, layouts, providers and theme.
- `frontend/src/modules`: domain, application, data-access and UI layers.
- `frontend/src/shared`: transport, localization, UI and playback helpers.
- `frontend/public-site`: prerendered UZ/RU/EN public pages and educational guides.
- `ops`: production deployment, backup and Nginx configuration.

## Local development

Python 3.12, Poetry 2.3.2 and Node 24 LTS are used by CI. SQLite is the local default.

```sh
cd backend
poetry install
poetry run python manage.py migrate
poetry run python manage.py seed_studio
poetry run python manage.py runserver 127.0.0.1:8000
```

In a second terminal:

```sh
cd frontend
npm ci
npm run dev
```

Open http://127.0.0.1:5173 for the public site, then `/studio` to create an account.
For a different local backend port, set `KUYLAB_API_PROXY` before starting Vite.
Local session/CSRF cookie names are isolated from other Django projects.
No default production password or
administrator is shipped. `seed_studio` preserves existing learner state; the
explicit destructive replacement flag is not part of normal setup or deployment.

## Verification

```sh
cd backend
poetry run python manage.py test tests --settings=config.settings.test --noinput
poetry run python manage.py audit_midi_catalog
```

```sh
cd frontend
npm run typecheck
npm test
npm run lint
npm run build
```

CI repeats backend tests against PostgreSQL, checks migrations and production
security settings, builds both Docker images, and runs CodeQL. Successful main
commits deploy through a dedicated restricted SSH identity.

## Production

See [deployment and recovery](docs/deployment.md) for Docker, PostgreSQL, Nginx,
DNS/TLS, backup and rollback procedures. Secrets, databases, media and learner
records stay outside Git. Production is configured for `kuylab.uz`.

## Content and attribution

Public pages are generated at build time, including canonical/hreflang links,
Open Graph images, visible educational content and matching JSON-LD. `/robots.txt`
and `/sitemap.xml` list the public site; authenticated studio routes send `noindex`.
Existing composition/player links and legacy query-string bookmarks remain valid.
The service worker keeps public HTML separate from `/studio.html` so visiting a
public guide cannot replace the offline studio shell. No analytics tracker runs
on the public site. `llms.txt` is a content directory, not an indexing guarantee.

When changing public content, edit all three languages in
`frontend/public-site/content.mjs`, update its actual review date, and rebuild.
Google Search Console uses DNS ownership verification; retain its root TXT record.
Submit `https://kuylab.uz/sitemap.xml` and inspect public URLs after deployment.
Check PageSpeed on mobile and desktop; lab scores are separate from field data.

The curated repertoire contains 103 compositions: the original eight, 24 retained
classical/contemporary editions, and 71 additional works. The 87 owner-supplied
Ivory performances form 72 work groups, including an additional recording for
the existing What Is a Youth course. [The Ivory manifest](backend/apps/studio/assets/ivory/manifest.json)
pins each arrangement, difficulty, preview, source attribution and import hash.
Multiple performances share one composition and expose separate player variants.
Ode to Joy, Moonlight Sonata I, Rondo alla Turca, Time, He’s a Pirate and My Heart
Will Go On use the replacement performances while retaining their composition IDs
and slugs. Nine confirmed channel jingles and Rondo's unrelated end-card music
are omitted; 75 exports retain their
original bytes, and Blue Bell's first performance has one documented user-directed
B5 addition after G5. Original downloads, precise cuts and editorial provenance
remain available for audit.
The Sound of Silence is transposed down one semitone in the MIDI itself; its
untransposed download is retained alongside exact timing/velocity verification.
Interstellar Main Theme has Pietschmann and The Piano Lab variants, separate from
Cornfield Chase. A Time for Us is a Fabrizio Caligaris recording of the Romeo &
Juliet theme; the original What Is a Youth edition and its six lessons remain
the default, with their existing IDs, saved positions and timestamp notes intact.
The earlier source-specific lessons for replaced editions are retired from the
active catalog; learner history is preserved. Eleven reviewed recordings now
have three focused UZ/RU/EN lessons each, five progressive MIDI stages per lesson,
and a complete-piece path at 60%, 80% and the original speed. These courses pin
their exact source hash and note selections; another performance does not inherit
their timestamps. The 24 retained editions in
[the earlier catalog manifest](backend/apps/studio/assets/catalog/manifest.json)
keep their reviewed UZ/RU/EN courses. There are 162 composition lessons and 96
continuity paths in total. The library supports list and grid views, with the
selected view, filters and pagination retained in URLs and per-account sessions.
Browsing groups are independent of source albums: Classical groups editions by
composer, Anime groups Naruto/Boruto and Shiki, and Dramas groups Winter Sonata
and All in. Choose a group before narrowing to its collections; original album
metadata and existing collection links remain available. Imported editions also
scope playback positions and timestamp notes to their source revision, so a new
arrangement never inherits a timestamp from a different performance.

`audit_midi_catalog` checks all 120 full performances for parse warnings, invalid
timelines, keyboard range, layer roles and unexpected duplicate/overlapping
attacks. Existing source voices and long holds are retained rather than globally
shortened or deduplicated. Reviewed diagnostic receipts are bound to exact bytes.
Gymnopédie No. 1 discards only two orphan release messages while retaining every
musical event; its original download is bundled. The audit establishes technical
integrity, not equivalence to an unavailable published score.
All in
has two byte-preserved full-length arrangements, Easy and Hard, in one player
with nine shared lessons and five continuity paths. Variant switching pauses
playback at the same timestamp; resume positions are scoped per variant.
Player settings, including speed, volume, hand balance, reverb and appearance,
are shared across all compositions, lessons and previews within the same account.
Other open player tabs receive changes through account-scoped browser storage.
Its optional compact note display abbreviates overlapping long blocks
without changing sound or claiming to reconstruct finger releases. The six
earlier replacement exports each include six source-specific lessons and eight continuity studies,
all with five MIDI stages: sparse landmarks, focused layer, complete hands at
60%, complete hands at 80%, and the 100% original. The six current files are the
user's replacement exports without pedal-extended key durations; every original
pitch, attack time and velocity is preserved. Still retains its twelve lessons
and eight studies with their existing three-stage progression.
Every complete-piece path ends with the unchanged supplied original. General
exercises are independently authored examples. Source bytes and
provenance are documented in [the studio notes](backend/apps/studio/README.md).
Composition previews load piano samples only after Play, use the main player's
Steinway engine, and pause on focus loss, backgrounding or leaving the viewport.
Only one preview plays at a time. The library keeps search, filters, sort, page
and page size in URLs such as `/compositions?q=Yiruma` or `/compositions?p=2&size=12`, backed by
per-account `sessionStorage`. Explicit URL values take priority; Back/Forward and
native Ctrl/Command/middle-click player links retain normal browser behavior.
The ten added classical editions retain their public-domain or individual CC terms.
For the twenty added contemporary editions, the project owner explicitly confirmed
permission to include MIDI files and adaptations in the website and public repository
on 2026-10-26. [Edition notices](backend/apps/studio/assets/catalog/README.md) record
that basis and source attribution; the code license does not relicense musical content.

Piano samples, fonts, MUI and audio worklet notices are in
[third-party notices](frontend/THIRD_PARTY_NOTICES.md) and the app's `/licenses.html`.

Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md).
