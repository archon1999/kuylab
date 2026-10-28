"""Reproduce the public-domain Waltz B.150 MIDI (authoring tool only).

Requires music21==10.5.1 and mido==1.3.3 in an isolated authoring environment.
MusicXML pitches already include the ottava's sounding transposition. Export
the expanded, tied note stream directly: ornament realization in music21's
general MIDI writer can generate unmatched releases for this particular score.
No runtime dependency, network request or performance synthesis is involved.
"""
from pathlib import Path

import mido
from music21 import converter


ROOT = Path(__file__).resolve().parents[1] / "backend/apps/studio/assets/catalog"
TICKS = 10080


def render():
    score = converter.parse(ROOT / "sources/waltz-a-minor.mxl").expandRepeats()
    score = score.stripTies()
    midi = mido.MidiFile(type=1, ticks_per_beat=TICKS)
    conductor = mido.MidiTrack([
        mido.MetaMessage("set_tempo", tempo=500000),
        mido.MetaMessage("key_signature", key="Am"),
        mido.MetaMessage("time_signature", numerator=3, denominator=4),
        mido.MetaMessage("end_of_track", time=round(float(score.duration.quarterLength) * TICKS)),
    ])
    midi.tracks.append(conductor)
    for index, part in enumerate(score.parts):
        channel = index
        track = mido.MidiTrack([
            mido.MetaMessage("track_name", name="Right hand" if index == 0 else "Left hand"),
            mido.Message("program_change", channel=channel, program=0),
        ])
        events = []
        notes = list(part.flatten().notes)
        for position, note in enumerate(notes):
            start = round(float(note.offset) * TICKS)
            finish = round(float(note.offset + note.duration.quarterLength) * TICKS)
            if finish <= start:
                # Forty written grace notes form two-note lead-ins. Give each
                # an eighth of a quarter before its anchor; main beats stay put.
                if not note.duration.isGrace:
                    raise ValueError("Unexpected zero-duration principal note")
                following = sum(1 for later in notes[position + 1:]
                                if later.offset == note.offset and later.duration.isGrace)
                finish = start - following * (TICKS // 8)
                start = finish - TICKS // 8
            for pitch in note.pitches:
                events.append((start, 1, pitch.midi))
                events.append((finish, 0, pitch.midi))
        previous = 0
        for tick, attack, pitch in sorted(events):
            track.append(mido.Message("note_on" if attack else "note_off", channel=channel,
                                      note=pitch, velocity=(90 if index == 0 else 81) if attack else 0,
                                      time=tick - previous))
            previous = tick
        track.append(mido.MetaMessage("end_of_track", time=max(0, conductor[-1].time - previous)))
        midi.tracks.append(track)
    midi.save(ROOT / "waltz-a-minor.mid")


if __name__ == "__main__":
    render()
