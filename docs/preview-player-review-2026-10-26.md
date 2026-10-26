# Audible previews and shared player preferences

Composition cards now play their actual MIDI excerpt through the same Splendid
Steinway sampler as the full player. Samples load only after an explicit Play.
The audio clock anchors one CSS animation group; loading stays paused. Pause and
resume retain the passage position, a fresh preview takes audio focus, hidden or
offscreen previews pause, and the excerpt ends once without looping. Cancelled
or unmounted preparation cannot start late. Reduced-motion users can listen with
a static roll. Failed sample loading leaves a localized retry control.

The excerpt API preserves key-block length separately from audible sustain,
clipping both to its ending. Native piano contexts are released after a brief
pause fade and can be prepared again without retaining disconnected hand nodes.
No original MIDI file, source tempo map, note attack, or main score is changed.

All full players, study players and previews read the same account preferences.
The owner explicitly chose to share speed as well as sound and appearance.
Updates reach open views and other tabs through account-scoped local storage;
server synchronization uses the global player-preferences endpoint. Old scoped
records remain compatible but are no longer selected by the player composition
root. Resume positions, bookmarks and stage progress remain scoped to content.

Card, detail and dashboard player actions are real anchors with valid URLs.
Plain clicks use SPA navigation; Ctrl/Command/middle/Shift clicks keep native
browser behavior. Study links follow the same modifier rule.

Library state uses `q`, `difficulty`, `collection`, `favorites`, `sort`, `p` and
`size` query parameters. Each account has separate tab-session storage. Explicit
URL state wins; fresh bare visits restore the session. Typing replaces history,
filter/page changes add entries, and Back/Forward restore controls and results.
Invalid page sizes and sort values normalize; page numbers clamp to real results.
Blocked session storage still leaves URL controls usable.

Tempo audit: the owner's global multiplier was 100%; Rondo alla Turca's source
contains a 60-quarter-BPM tempo, and its existing override was 200%. Some editions
are notation renders rather than human performance exports. A blanket multiplier
would change correctly timed editions too, so source timings remain intact. The
shared speed control makes the owner's chosen multiplier consistent across players.
