"""Reproducible staff-separated MIDI from the reviewed TruuMoo score.

The complete MusicXML is pinned locally. No pitch split, transcription, pedal
extension or guessed note is used. This is a score rendering, not a recording.
"""
from hashlib import sha256
from pathlib import Path

from apps.scores.parser import extract_musicxml, parse_musicxml
from .midi_authoring import midi_bytes

SCORE_PATH = Path(__file__).with_name("assets") / "notation" / "passacaglia.mxl"
SCORE_SHA256 = "a4cda46a2b0e980ea890feacb6ceb4be224107c16c7d1c79fb25dee8e5bb168a"
SCORE_URL = "https://vivace-music.org/library/passacaglia-handel-halvorsen-piano/musicxml/passacaglia-handel-halvorsen.mxl"
SOURCE_PAGE = "https://vivace-music.org/sheets/passacaglia-handel-halvorsen-piano.html"
CREDIT = "TruuMoo, MuseScore score 5889760; CC0 1.0, shared via PDMX; MusicXML supplied by Vivace Music."


def notation_source():
    data = SCORE_PATH.read_bytes()
    if sha256(data).hexdigest() != SCORE_SHA256:
        raise ValueError("Passacaglia: review the changed notation before rendering MIDI.")
    parsed = parse_musicxml(extract_musicxml(data, "passacaglia.mxl"))
    if (parsed["warnings"] or parsed["metadata"]["measure_count"] != 74
            or parsed["playback_order"] != list(range(74))
            or any(e["ties"] or e["grace"] for e in parsed["events"])):
        raise ValueError("Passacaglia: notation structure changed; review its playback first.")
    return data, parsed


def rendered_midi():
    _, parsed = notation_source()
    events = [e for e in parsed["events"] if e["pitch"] and not e["rest"]]
    if len(events) != 1030 or any(e["hand"] not in {"left", "right"} for e in events):
        raise ValueError("Passacaglia: the two complete notation staves are required.")
    notes = [(e["onset_quarters"], e["duration_quarters"], int(e["pitch"]["midi"]),
              e["hand"], 84 if e["hand"] == "right" else 68) for e in events]
    return midi_bytes(notes, bpm=130, meter=(4, 4),
                      title="Passacaglia - TruuMoo score, separate hands",
                      end_quarters=parsed["metadata"]["duration_quarters"])
