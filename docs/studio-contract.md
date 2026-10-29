# Curated studio API and product contract

Updated 2026-10-11 after the move to `C:\Users\Asus\Documents\KuyLab.uz`. A personal, composition-first piano studio using the supplied **Winter Sonata — Still** MIDI. The musical catalog is curated in code; the website has no import, content editing, grading, compulsory plans, MIDI-device requirement or manual practice timer.

## Catalog API

`GET /api/studio/catalog/` returns authored strings selected by `Accept-Language: uz`, `ru`, or `en`. The response includes `Content-Language` and varies by language. `?lang=uz|ru|en` is also supported; invalid explicit language values return 400.

```ts
type StudyItem = {
  id: string;
  kind: 'lesson' | 'exercise' | 'theory';
  title: string;
  subtitle: string;
  category: string;
  goals: string[];
  level: 'easy' | 'intermediate' | 'advanced' | null;
  minutes: number;
  score_id: number;
  composition_id?: number;
  intro: string;
  explanation: { title: string; text: string }[];
  steps: { title: string; instruction: string }[];
  fingering?: string;
  related_ids?: string[];
  ready_when?: string;
  stages?: {
    id: string;
    title: string;
    instruction: string;
    score_id: number;
    source_speed_percent: number;
  }[];
  source?: {
    start_seconds: number;
    end_seconds: number;
    transformation: string;
    composition_variant_id?: string;
    playback_revision?: string;
  };
};
type Catalog = {
  revision: string;
  compositions: {
    id: number;
    slug: string;
    title: string;
    subtitle: string;
    composer: string;
    score_id: number;
    duration_seconds: number;
    lesson_ids: string[];
  }[];
  lessons: StudyItem[];
  exercises: StudyItem[];
  theory: StudyItem[];
  categories: { id: string; label: string }[];
  goals: { id: string; label: string }[];
};
```

Category and goal values on study items are IDs resolved through their catalog arrays. Item IDs are stable strings, for example `lesson:still:opening-left`, `exercise:scales:easy` and `theory:inversions`. `minutes` is an approximate reading/practice suggestion, not an enforced task duration.

The current catalog revision is `playable-piano-expanded-courses-2026-10-v16`: 103 compositions, 198 composition lessons, 108 continuity studies, 48 independent exercises and 24 theory topics. Fifty-five compositions have reviewed courses; the remaining works are available in the player. A study's top-level `score_id` points to its first stage; each stage has its own score and personal playback position. Focused performance lessons progress through selected landmarks at 60%, the complete focused layer at 80%, both full layers at 60%, 80% and 100%. Full-piece paths retain every note at all three speeds and reuse the original score at the last stage. Existing Still/package courses retain their established stage IDs and structure. Composition lessons and continuity studies have `composition_id`; general exercises/theory remain independent. A source-bound course carries its exact `playback_revision` and, when applicable, `composition_variant_id`. The player, detail page and lesson-to-source link use that binding; aligned All in variants retain their shared course.

`/piano` is a private app route with a live sampled grand piano. The same input
layer covers the keyboard of each composition/lesson player. Each pointer or
computer key owns a hold; multiple inputs on one pitch share a voice until the
last release. Individual releases ramp down only that sample. Pending loads are
invalidated by release or stop; blur, hidden tabs and unmount stop manual voices.
The focused computer mapping starts at C4 (A/W/S/E…); arrows move note focus,
Space/Enter hold that note, and Escape releases every manual note. Keys receive
multi-touch/glissando while the roll above retains pan/pinch gestures. Manual
playing claims audio focus, pausing another demonstration rather than overlapping
two transports. Shared account volume/reverb and visible-key settings apply.

`GET /api/scores/<id>/` returns the existing Score domain object and parsed MIDI timeline. `GET /api/scores/<id>/file/` serves the actual MIDI. The original composition preserves all supplied bytes; lesson adaptations carry explicit source and transformation provenance. Missing seed assets return 503 instead of a placeholder catalog.

## Player integration

The practice module exposes:

```ts
type StudioPlayerProps = {
  score: Score;
  compact?: boolean;
  onBack?: () => void;
  onPositionChange?: (seconds: number) => void;
  initialPosition?: number;
  onPlaybackChange?: (playing: boolean) => void;
};
```

`StudioPlayer` does not fetch or import scores. Its caller supplies a loaded Score. Full mode fills the workspace; compact mode supports study pages. The player uses continuous playback, 88 keys, sampled piano, tempo control, click/drag seeking across the complete source, adjustable lookahead, optional letter names, two hand colors and keyboard shortcuts. Playback stops at the final release; restarting is an explicit action. There is no automatic repeat, range selection, repeat delay or `L` shortcut. Its light/dark appearance follows the app theme.

Velocity gradients change the note brightness/opacity from the existing MIDI velocity without changing pitch, duration or sound. Strike effects use a reused pool capped at 144 particles. They run only during continuous playback, clear on seeks/pause, and are disabled by the operating system’s reduced-motion preference even when the saved preference is enabled.

The default study flow is sample first, then explanation and practice. A lesson can isolate a hand, simplify a source texture or teach a theoretical idea; it need not reproduce one unchanged formal section. Original and teaching versions remain distinct.

Player settings use separate Visual and Audio tabs. The Visual tab controls note/key labels, shadows, velocity gradients, strike particles, lookahead and hand visibility/colors; Audio contains volume and reverb. These preferences and tempo persist locally across routes and reloads. Obsolete repeat settings are discarded on normalization. Playback positions are stored per content item in personal state. Persistence is injected through the practice module's data-access adapter, not accessed directly by UI components.

## Personal state and activity

`GET/PATCH /api/profile/` stores profile, language and theme.

`GET/PATCH /api/activity/state/` handles the personal library. A PATCH supplies the complete personal state:

```ts
type PersonalState = {
  favorites: string[];
  recents: { id: string; openedAt: string }[];
  positions: Record<string, number>;
};
```

Content IDs use `composition:<id>` or a StudyItem ID. Positions are source seconds. Favorites and recents do not imply assessed mastery.

`GET/PUT /api/activity/visits/` reads or cumulatively updates activity visits:

```ts
type ActivitySession = {
  id: string; // UUID, stable for this visit
  startedAt: string; // ISO date-time, immutable for this UUID
  seconds: number;
  contentSeconds: Record<string, number>;
  daySeconds: Record<string, number>; // YYYY-MM-DD in Asia/Tashkent
};
```

The backend accepts visits of at least 300 seconds. Updates are idempotent and never lower an already stored cumulative duration. The day totals must equal visit seconds; per-content totals cannot exceed them. The UI counts time while the page is visible or player playback is active; this is site activity, not verified piano practice. A qualifying visit includes its first five minutes.

The activity provider exposes favorites, recents, positions, sessions, derived stats, `toggleFavorite`, `recordOpen`, `setPosition`, `setContent` and `setPlaying`. Dashboard statistics are compact; the statistics page is separate.

## Routes and read-only enforcement

Page IDs include dashboard, library, detail, practice, exercises, theory, study, statistics and settings. Study URLs use `item=<StudyItem.id>`; practice URLs use `score=<scoreid>&composition=<id>` when associated with the full composition. The app shell keeps a left sidebar and localized header; full practice can use the focused shell.

The server blocks legacy musical-content writes with 405 and retired overview/curriculum/quiz/session/demo reads with 410. This also stops legacy GET handlers from creating automatic lessons. Profile and activity writes remain available.

`seed_studio` prepares the catalog idempotently. Copy-only teaching instruction changes retain existing score versions; source bytes, selected events and timing remain part of score identity. If unrelated compositions exist, replacing them requires `--replace-compositions`, after a database/media backup. The flag removes other compositions and dependent records, preserves Profile, and is never used by the ordinary setup commands.

## Shell, theme and loading

The application uses a left navigation rail, UZ/RU/EN selector, light/dark switch and profile access. Visual references are Ivory and the supplied screenshots. The interface uses Alan Sans for controls, Lora for editorial headings and Inter for Cyrillic interface text. Dark surfaces use Ivory's purple family (`#18122b`, `#292043`, `#32284e`) with warm text (`#f5edc9`) and accent (`#eba165`); light surfaces use `#faf8f5` and `#fffdfa`.

The header and navigation remain fixed while the main workspace content scrolls. The document itself does not scroll; overflow regions use thin, theme-aware scrollbar thumbs. The focused full player occupies its own viewport without an extra page scroll.

Initial startup has a branded splash. Route and data loading use skeletons that preserve the expected layout; errors offer a retry. The offline cache remains available but the interface does not show an “Offline tayyor” readiness badge. Loading and cache state must not appear as learning progress.

Audio and font credits are available at `/licenses.html`, linked from the profile Settings page in UZ/RU/EN. The player and its settings panel contain no attribution banner or external sample-credit link. Full audio and font license files remain bundled.

## Repository architecture

The project follows the structure of the read-only reference `C:\Users\Asus\Documents\Deenly.uz`: `backend/apps`, split `backend/config/settings`, centralized `backend/tests`, frontend app composition and domain modules, plus root `runtime` and `ops`. No local PowerShell launcher files are part of the project. Backend startup uses Poetry/Django commands; frontend startup uses npm/Vite. See the [README](../README.md) for the exact commands and [frontend architecture](frontend-architecture.md) for layer boundaries.

## Source evidence and verification

The supplied MIDI is 8,938 bytes, 1,092 notes and 214.60416666666666 seconds. SHA256: `f0713b1de241c28522911a907a4464504ce7fbcaa8340ad9e1589881c2f3e7c8`. Its explicit quarter tempo is 120, with no meter, key, pedal or composer/arranger metadata. Upper/lower-track hand assignments are curated inference. Full-byte preservation does not establish independent equivalence to a complete published arrangement.

Implementation details and provenance are in [backend/apps/studio/README.md](../backend/apps/studio/README.md). Verification evidence and limits are in [studio-verification.md](studio-verification.md).
