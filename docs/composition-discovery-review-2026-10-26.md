# Composition discovery and dashboard resume review

The dashboard now searches the complete recent-study history for unfinished work.
Mastered lessons are skipped. In a staged course it keeps the last chosen
unfinished stage, or moves to an unfinished active/first remaining stage when the
remembered one is complete. If every recent study is complete, no misleading
resume recommendation is displayed. Historical recents remain visible.

The library now supports title/composer/collection search, 1–5-star difficulty,
collection and favorite filters, four sort orders, and 6/12/24-item pagination.
Filters reset to page one; shrinking results clamp the active page. A matching
variant supplies the card's rating, duration, preview and player link. For All in,
Easy is 2/5 and Hard 4/5. Ratings are curated for these supplied performances and
are not external examination grades.

`composition_showcase.py` records source-specific excerpt landmarks. The private
GET preview endpoint sends every overlapping source note in a 14–16 second
window, preserving pitch, velocity, inferred hand roles and clipped key-release
timing. No hand, chord voice or short attack is sampled out. A held note crossing
the window start is retained. Preview requests never change score files or user
activity. Catalog responses keep note graphs out of their main payload.

Cards request their excerpts only after entering the viewport; their repository
deduplicates successful requests and permits failed requests to retry. Late
responses cannot replace another variant. SVG note groups animate silently once;
keyboard highlights follow each displayed key duration. Previews start paused,
with a centered Play button; no source timestamp badge is shown. Motion pauses offscreen,
in a hidden tab or with the pause button. Reduced-motion users get a static
preview and can open the full player. Replay is explicit; the main player gains no looping behavior and no
audio samples are downloaded for library previews. All in retains the existing
visual hold-shortening aid without dropping source attacks.

New UI text is authored in UZ/RU/EN. Shared shape, palette and type tokens remain
consistent in both themes, with compact mobile filters and pagination. The
30 proposed repertoire additions are kept in the separate candidate document;
they are not presented as playable assets before selecting their actual MIDIs.

Validation covers completed-lesson/stage selection, compound search and filters,
variant matching, pagination across a future 38-piece collection, exact source
note-set retention, clipping boundaries, authorization, read-only API behavior
and the existing full test suites. Deployment smoke checks verify the eight
preview endpoints against real source scores.

Composition detail URLs use the curated slug, such as
`/compositions/winter-sonata-still`. Legacy numeric detail bookmarks replace
themselves with that canonical slug after catalog resolution. Card links,
dashboard links, lesson returns, player Back and document titles resolve the
same composition; playback identity and existing practice URLs stay stable.
