# KuyLab teaching API

> **Historical API documentation — superseded.** The import, Pirate curriculum, diagnostic, quiz, adaptive-plan and manual-session routes described below belong to the retired prototype. In the curated studio, legacy content writes return 405 and retired reads return 410; the current profile, activity, catalog and score API is documented in [studio-contract.md](studio-contract.md). See [README](../README.md) for current setup and supported product flows. Retained examples and old test results are historical evidence, not a statement that these routes remain available.

This build serves one local learner (`Profile(pk=1)`). Name, Yamaha model,
practice minutes, language (`uz`, `ru`, `en`) and theme (`light`, `dark`) persist
through `/api/profile/`. There is no account or teacher review workflow.
Browser mutations accept the app's configured local origins (5173/5174) or the
API's same origin; unrelated browser origins return 403. Local CLI requests
without browser-origin headers remain available. API responses are private and
not cached. Invalid score payload shapes/fields return 400; local database or
file availability failures return a safe 503, while missing files return 404.

## Complete MIDI source and immutable versions

`seed_demo` installs the verified full two-hand He's a Pirate MIDI and the five
other requested repertoire entries. The exact BitMidi source is 11,918 bytes,
SHA256 `853c5d63d49fdfc685f4215092affa83794298347a52e328ee24fe2ee86da522`,
with 1,255 notes (Right Hand 557 / Left Hand 698) and a 77.625-second timeline.
The source's 6/8, quarter-note tempo 200 and literal key-signature metadata **F**
are preserved. Local chord analysis is separate from the key metadata.
The file's ending was checked independently. Its public download is not labelled
CC or public domain; attribution and copyright metadata accompany the asset.

`POST /api/scores/` accepts multipart `.mid` / `.midi` files alongside the historical
MusicXML importer. Required fields are `file`, `rights_confirmed=true`, and
**exactly one** of `arrangement_id` or `composition_id`. A composition target
reuses its default arrangement or atomically creates its first arrangement with
the imported score. The response includes the actual `arrangement_id`; failed
imports leave no empty arrangement. `title`, `source_url`, `rights_note`, and
`exact_version_confirmed` are optional. Every import creates an immutable version.
User confirmation does not establish whole-composition completeness.

`GET /api/scores/{id}/` provides `file_format`, `file_url`, parsed events,
tempo/meter/key maps, provenance, sections, and hand overrides.
`GET /api/scores/{id}/file/` downloads the exact original bytes. MIDI has an empty
`musicxml_url`; its notation route returns 404. No notation is fabricated.

Arrangement fields `active_score_id` and `active_score_format` describe its newest
version. `active_score_completeness_verified_at` belongs to that version, not the
arrangement's historical source. A new upload has no completeness timestamp.
`midi_file_url` is empty when the latest version is not MIDI. Historical PDF,
Musicnotes and their learner records remain archived and do not replace the MIDI
default. Seed reruns preserve imported versions, preferences and practice history.

## MIDI timeline contract

The normalized `parsed` shape is compatible with the score player's timeline:

- `events`: stable source IDs, MIDI pitch, track, channel, port, velocity, hand,
  onset/duration in quarters and seconds, and original tick coordinates.
- `tempo_map`: `onset_quarters`, `onset_seconds`, `onset_ticks`, `quarter_bpm`,
  and microseconds per quarter. Native playback integrates every tempo change.
- `time_signature_map` and `key_signature_map`: explicit source metadata only.
- `pedal_events` and `control_events`: source CC events, channel and MIDI port.
- `measures`: derived beat navigation windows, **not printed score measures**.
  Missing source meter remains null; four-quarter navigation is then just a grid.

`duration_*` describes physical key hold until note release.
`sound_duration_*` separately includes CC64 sustain; tails stop at pedal release,
controller reset, all-sound-off or the complete file boundary. Pedal state is
isolated by port/channel. Track names are hand hints; unknown hands remain unknown
until the learner assigns them. MIDI does not contain fingering or enharmonic
notation. Channel-10 percussion is flagged and excluded from piano lessons.

## Source-derived lessons and separate fragment player

`GET /api/compositions/{id}/curriculum/` chooses the default arrangement's newest
score; `?arrangement_id={id}` selects another arrangement of that composition.
It returns arrangement, source status, skills, diagnostic, lessons and adaptive
plan. Invalid and oversized IDs return 400; unrelated IDs return 404.

The primary MIDI course has six actual source fragments: opening rhythm,
left-hand key distance, a melodic interval, a simultaneous chord, hand coordination,
and the ending/recall. Their notes are copied from source events, not generic
exercises. The opening's 6/8 long-short theory is selected only when its actual
attack gaps match `1, .5, 1, .5` quarters; key-hold timing is explained separately.
Other meters and note patterns are not assigned this grouping by assumption.

`GET /api/lessons/{id}/` includes explanation, steps, criterion, quiz choices,
practice link and progress. Answer keys are absent from GET responses.
MIDI lessons have `kind=source_excerpt`, `exercise.original=false`,
`exercise.type=midi_source_fragment`, `score_id`, exact source `event_ids`,
`start/end_seconds`, `start/end_quarters`, and `fragment_url`.

`GET /api/lessons/{id}/exercise/` returns a Score-shaped fragment for the lesson's
small player. Onsets, tempo maps and controller ticks rebase to zero. Key and sound
durations stop at the fragment boundary. The unchanged source event IDs and
`source_onset_*`, `source_duration_*`, `source_*ticks` preserve original evidence.
`parsed.fragment` records the source score ID/hash and native time boundaries.
Clipped navigation windows preserve source meter and
`meter_offset_quarters`, so starting mid-beat does not invent a new downbeat.
Full-source sections are omitted from this fragment response.

The main practice route plays the full selected source. `practice_link` can pass
an exact seconds range plus the declared starting choice `bpm=100&beat_unit=quarter`.
That practice choice does not alter the source's native tempo map. A new score
version or changed fragment identity gets new lesson progress; prior evidence
remains available in the database.

## Language, diagnostic and adaptation

Use `?lang=uz|ru|en`; otherwise weighted `Accept-Language`, then the saved profile
language applies. Language changes retain source/event IDs and answer choice IDs.
Lessons, quizzes, feedback, diagnostics and plan reasons have authored translations.

`POST /api/compositions/{id}/diagnostic/` accepts `{"answers":{"question-id":"choice-id"}}`.
Submit all question IDs advertised by that curriculum. MIDI diagnostics assess
keyboard/register, intervals/chords, rhythm, key release/pedal, practice strategy
and learner-reported coordination; staff reading is not required. Knowledge and
self-reported skill remain separate. Unknown self-report remains unassessed.

`GET` or `POST /api/compositions/{id}/adaptive-plan/` accepts optional `minutes`
from 5 to 180. A deterministic scheduler selects useful composition fragments,
unassessed or weaker skills and due reviews. Each item states its selection reason;
integer allocations sum to the requested time budget. It is not an AI performance
assessment.

`POST /api/lessons/{id}/quiz/` uses the same answers object and persists every
attempt. The response includes correct-choice feedback. The latest attempt is
the current knowledge evidence; a quiz does not prove piano performance.

`POST /api/lessons/{id}/practice/` accepts `successful_repetitions` (0–3),
`comfort` (1–5), optional `bpm` (20–240), and `reflection` (up to 2000 characters).
This is explicitly learner-reported evidence. Initial review requires a passing
quiz (80%) and three comfortable repetitions, then waits two days. Review needs
fresh quiz and practice after the due time; repeated clicks cannot bypass the wait.
The API never asserts complete composition mastery from these records.

## Verification

Run `python manage.py test learning scores` from backend with the root virtual
environment. Tests cover immutable imports, exact verified source bytes/end,
tempo integration, MIDI ports/controllers/sustain, malformed files, source-specific
fragment bounds in three languages, adaptive budgets, delayed review, preference
and history preservation, and safe input boundaries.
