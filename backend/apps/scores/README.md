# MIDI and MusicXML source API

The primary player uses Standard MIDI Files (`.mid` / `.midi`); the API also
retains partwise MusicXML import compatibility. Imports must be owned, licensed,
or otherwise permitted. The API does not infer fingering or automatically verify
whole-composition completeness.

`POST /api/scores/` requires multipart `file`, `rights_confirmed=true`, and
**exactly one** of `arrangement_id` or `composition_id`. Optional fields are
`title`, `source_url`, `rights_note`, and `exact_version_confirmed`.
With `composition_id`, the API reuses that composition's default arrangement or
creates its first arrangement in the same transaction as the score. Failed
imports leave no empty arrangement. Each successful import creates an immutable
version and returns its actual `arrangement_id`; earlier versions remain intact.
Confirmation records the learner's statement, not a license verification.

Non-object JSON, unknown fields, malformed source files, and missing or conflicting
targets return 400. Local database or file availability failures return a safe
503 response; missing source files return 404. Browser writes are accepted from
the local app origins (5173/5174) and the API's same origin; unrelated origins
return 403. Local CLI requests without browser-origin headers remain available.
All API responses use `Cache-Control: private, no-store`.

`GET /api/scores/?arrangement_id=…` returns version summaries.
`GET /api/scores/<id>/` includes normalized source events and measures.
`GET /api/scores/<id>/file/` downloads the exact original source bytes. MIDI events
preserve track/channel/port, native tempo changes, key holds and separate sustain
tails. Its measures are derived navigation windows, not printed score measures.
`GET /api/scores/<id>/musicxml/` returns the validated, byte-for-byte source XML
(the root MusicXML member for a compressed file). It returns 404 for MIDI; no
notation is fabricated.

`PATCH /api/scores/<id>/` updates `hand_overrides`, `sections`, and the learner's
`exact_version_confirmed` claim. Sections use inclusive zero-based *measure
positions* (`start_index`, `end_index`), not MusicXML printed measure numbers.
For MusicXML, hand hints come from staves 1/2 of a multistaff part; single-staff
hands remain unknown. For MIDI, literal track names provide editable hand hints.

Source event offsets/durations and measure starts/lengths are in quarter-note
units. `duration_fraction` retains an exact rational representation; MusicXML
`duration/divisions` determines timing. A `chord` note shares the preceding note's
onset without advancing the cursor. Backup/forward, rests, voices, written
pitches, chromatic transposition, ties, changing keys/meters, and numeric tempos
are retained. `quarter_bpm` is the playback tempo; e.g. dotted-quarter 60 is
quarter-note 90. `playback_order` expands bounded barline repeats and basic numbered
voltas. Source events themselves remain in written order.

The MusicXML event list is a nominal study timeline, not expressive audio.
Playback must respect ties and
skip cue/grace notes as new principal attacks. Ornaments, pedal, arpeggiation,
rubato, and engraving are not assessed. D.C./D.S./Coda navigation, octave shifts,
unpitched notation, and mismatched part lengths are flagged as unsupported for
verified timed playback. Complex/unfinished repeats return written order with a
warning. `capabilities` and `warnings` must be presented honestly by consumers.

Upload limits: 8 MB input; 16 MB root XML; 128 ZIP entries, at most 32 MB declared
uncompressed archive data; 32 parts, 2,000 measures per part, 30,000 note/rest
events; 64 XML nesting levels and 250,000 elements. ZIP entries are read with a
size limit and never extracted to user-controlled paths. Normal MusicXML exports
may include the standard external `score-partwise` DOCTYPE reference: recognized
Recordare Partwise public IDs (versions 1.0–4.0) with the official
`musicxml.org/dtds/partwise.dtd` URL are accepted as metadata. Expat parameter
entity parsing is disabled, so the DTD URL is never fetched or parsed. Internal
DTD subsets (even empty ones), entity declarations/references, unfamiliar DTD
URLs, processing instructions, external resource links/images, encrypted
archives, path traversal, and malformed XML are rejected. This importer is not a
complete MusicXML XSD validator.

`GET /api/scores/demo/` and `/api/scores/demo/musicxml/` serve an original two-bar
6/8 drill authored for this project and released under CC0. It is **not** a
transcription, excerpt, or arrangement of “He's a Pirate.”

Technical references:

- [W3C MusicXML timing, voices, chords and repeats](https://www.w3.org/2021/06/musicxml40/tutorial/midi-compatible-part/)
- [W3C compressed MXL container format](https://www.w3.org/2021/06/musicxml40/tutorial/compressed-mxl-files/)
- [W3C sound tempo: quarter notes per minute](https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/sound/)
- [W3C standard MusicXML DOCTYPE example](https://www.w3.org/2021/06/musicxml40/tutorial/hello-world/)
- [Expat parameter entity parsing control](https://docs.python.org/3/library/pyexpat.html#xml.parsers.expat.xmlparser.SetParamEntityParsing)
- [Python XML security and Expat behavior](https://docs.python.org/3/library/xml.html#xml-security)
