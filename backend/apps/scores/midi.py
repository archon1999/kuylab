"""Standard MIDI File timeline; preserve key holds separately from CC64 tails.

Source: https://mido.readthedocs.io/en/stable/files/midi.html
Beat windows are navigation coordinates, never claimed to be printed measures.
"""
from bisect import bisect_right
from collections import defaultdict, deque
import io
import math
import re
import mido
from .parser import MAX_UPLOAD_BYTES, ScoreImportError

MAX_MIDI_MESSAGES = 120_000
MAX_MIDI_NOTES = 30_000
MAX_MIDI_TRACKS = 64
MAX_MIDI_WINDOWS = 2_000
MAX_MIDI_SECONDS = 7200


def key_signature(raw):
    major = ["Cb", "Gb", "Db", "Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E", "B", "F#", "C#"]
    minor = ["Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#"]
    mode = "minor" if raw.endswith("m") else "major"
    tonic = raw[:-1] if mode == "minor" else raw
    entries = minor if mode == "minor" else major
    return {"fifths": entries.index(tonic) - 7, "mode": mode, "midi_key": raw, "provenance": "midi_key_signature_meta"} if tonic in entries else None


def midi_pitch(value):
    # MIDI has no enharmonic spelling; these names are display conventions only.
    names = [("C", 0), ("C", 1), ("D", 0), ("D", 1), ("E", 0), ("F", 0), ("F", 1), ("G", 0), ("G", 1), ("A", 0), ("A", 1), ("B", 0)]
    step, alter = names[value % 12]
    return {"midi": value, "step": step, "alter": alter, "octave": value // 12 - 1, "spelling_basis": "midi_display_convention"}


def track_hand(name):
    normalized = name.strip().lower()
    if re.search(r"\b(?:right\s*hand|right|rh)\b", normalized):
        return "right"
    if re.search(r"\b(?:left\s*hand|left|lh)\b", normalized):
        return "left"
    return "unknown"


def parse_midi(data, title="MIDI performance"):
    if not isinstance(data, bytes) or not data or len(data) > MAX_UPLOAD_BYTES or not data.startswith(b"MThd"):
        raise ScoreImportError("Choose a complete Standard MIDI File (.mid/.midi), at most 8 MB.")
    try:
        midi = mido.MidiFile(file=io.BytesIO(data), clip=False)
    except (OSError, EOFError, ValueError, TypeError, IndexError, KeyError) as error:
        raise ScoreImportError("The MIDI file is malformed or truncated.") from error
    if midi.type not in [0, 1]:
        raise ScoreImportError("Asynchronous type-2 MIDI tracks do not share a single composition timeline.")
    if midi.type == 0 and len(midi.tracks) != 1:
        raise ScoreImportError("A type-0 MIDI must contain exactly one track.")
    if not 1 <= len(midi.tracks) <= MAX_MIDI_TRACKS or not 1 <= midi.ticks_per_beat <= 32767:
        raise ScoreImportError("Unsupported track count or SMPTE time division; export a PPQ type-0/1 MIDI.")
    messages, tracks, warnings, copyrights = [], [], [], []
    for track_index, track in enumerate(midi.tracks):
        ticks = 0
        name = track.name.strip()[:240] or f"Track {track_index + 1}"
        channels, programs = set(), {}
        if not track or track[-1].type != "end_of_track":
            raise ScoreImportError("Every track must have its complete end-of-track boundary.")
        for order, message in enumerate(track):
            if not isinstance(message.time, int) or message.time < 0:
                raise ScoreImportError("MIDI delta ticks must be nonnegative integers.")
            ticks += message.time
            messages.append((ticks, track_index, order, message))
            if len(messages) > MAX_MIDI_MESSAGES:
                raise ScoreImportError("MIDI message count exceeds the import limit.")
            if hasattr(message, "channel"):
                channels.add(message.channel)
            if message.type == "program_change":
                programs[str(message.channel)] = message.program
            if message.type == "copyright":
                copyrights.append(message.text[:2000])
        tracks.append({"id": f"T{track_index}", "index": track_index, "name": name, "channels": sorted(channels), "programs": programs,
                       "hand": track_hand(name), "hand_evidence": "track_name_hint" if track_hand(name) != "unknown" else "unknown", "end_ticks": ticks})
    messages.sort(key=lambda item: item[:3])
    file_end_ticks = max(item[0] for item in messages)
    if file_end_ticks <= 0:
        raise ScoreImportError("The MIDI has no positive-duration composition timeline.")
    tempo_map = [{"onset_ticks": 0, "onset_quarters": 0.0, "microseconds_per_quarter": 500000, "quarter_bpm": 120.0, "beat_unit": "quarter", "bpm": 120.0, "explicit": False}]
    time_map, key_map = [], []
    for tick, _, _, message in messages:
        q = tick / midi.ticks_per_beat
        if message.type == "set_tempo":
            if not 1 <= message.tempo <= 0xFFFFFF:
                raise ScoreImportError("A MIDI tempo must be a positive microsecond value.")
            value = {"onset_ticks": tick, "onset_quarters": q, "microseconds_per_quarter": message.tempo, "quarter_bpm": 60_000_000 / message.tempo, "beat_unit": "quarter", "bpm": 60_000_000 / message.tempo, "explicit": True}
            if tempo_map[-1]["onset_ticks"] == tick:
                tempo_map[-1] = value
            else:
                tempo_map.append(value)
        elif message.type == "time_signature":
            if not 1 <= message.numerator <= 64 or message.denominator not in [1, 2, 4, 8, 16, 32, 64, 128]:
                raise ScoreImportError("Unsupported MIDI time signature.")
            value = {"onset_ticks": tick, "onset_quarters": q, "beats": str(message.numerator), "beat_type": message.denominator,
                     "groups": [{"beats": str(message.numerator), "beat_type": message.denominator, "count": message.numerator}],
                     "length_quarters": message.numerator * 4 / message.denominator, "provenance": "midi_time_signature_meta"}
            if time_map and time_map[-1]["onset_ticks"] == tick:
                time_map[-1] = value
            else:
                time_map.append(value)
        elif message.type == "key_signature":
            value = key_signature(message.key)
            if value:
                key_map.append({"onset_ticks": tick, "onset_quarters": q, **value})
    elapsed = 0.0
    for index, tempo in enumerate(tempo_map):
        if index:
            previous = tempo_map[index - 1]
            elapsed += (tempo["onset_ticks"] - previous["onset_ticks"]) / midi.ticks_per_beat * previous["microseconds_per_quarter"] / 1_000_000
        tempo["onset_seconds"] = elapsed
    tempo_ticks = [tempo["onset_ticks"] for tempo in tempo_map]

    def seconds(tick):
        tempo = tempo_map[bisect_right(tempo_ticks, tick) - 1]
        return tempo["onset_seconds"] + (tick - tempo["onset_ticks"]) / midi.ticks_per_beat * tempo["microseconds_per_quarter"] / 1_000_000

    file_duration = seconds(file_end_ticks)
    if not math.isfinite(file_duration) or not 0 < file_duration <= MAX_MIDI_SECONDS:
        raise ScoreImportError("The MIDI duration is outside the supported two-hour range.")
    active, pedal_down, sustained = defaultdict(deque), defaultdict(bool), defaultdict(list)
    track_ports = defaultdict(int)
    notes, pedal_events, control_events = [], [], []

    def release(note, tick, reason):
        note["end_ticks"] = tick
        note["end_reason"] = reason
        if pedal_down[(note["port"], note["channel"])] and reason != "all_sound_off":
            sustained[(note["port"], note["channel"])].append(note)
        else:
            note["sound_end_ticks"] = tick

    for tick, track_index, order, message in messages:
        if message.type == "midi_port":
            track_ports[track_index] = message.port
            continue
        port = track_ports[track_index]
        if message.type == "note_on" and message.velocity > 0:
            note = {"id": f"T{track_index}:C{message.channel}:N{order}", "track_index": track_index, "channel": message.channel, "port": port, "midi": message.note,
                    "velocity": message.velocity, "start_ticks": tick, "end_ticks": None, "sound_end_ticks": None, "percussion": message.channel == 9}
            active[(port, track_index, message.channel, message.note)].append(note)
            notes.append(note)
            if len(notes) > MAX_MIDI_NOTES:
                raise ScoreImportError("MIDI note count exceeds the import limit.")
        elif message.type == "note_off" or message.type == "note_on" and message.velocity == 0:
            queue = active[(port, track_index, message.channel, message.note)]
            if not queue:
                # Tracks are synchronized views of a port/channel stream.
                # An off event may live in a different track from its on event.
                alternatives = [candidate for (candidate_port, _, channel, pitch), candidate in active.items()
                                if candidate and candidate_port == port and channel == message.channel and pitch == message.note]
                queue = min(alternatives, key=lambda candidate: candidate[0]["start_ticks"]) if alternatives else queue
            if queue:
                release(queue.popleft(), tick, "note_off" if message.type == "note_off" else "note_on_zero_velocity")
            elif len(warnings) < 30:
                warnings.append(f"Unmatched note release in track {track_index + 1}, channel {message.channel + 1}, MIDI {message.note}.")
        elif message.type == "control_change":
            value = {"onset_ticks": tick, "onset_quarters": tick / midi.ticks_per_beat, "onset_seconds": seconds(tick), "track_index": track_index,
                     "channel": message.channel, "port": port, "controller": message.control, "value": message.value}
            control_events.append(value)
            if message.control == 64:
                down = message.value >= 64
                pedal_events.append({**value, "down": down})
                if pedal_down[(port, message.channel)] and not down:
                    for note in sustained[(port, message.channel)]:
                        note["sound_end_ticks"] = tick
                    sustained[(port, message.channel)].clear()
                pedal_down[(port, message.channel)] = down
            elif message.control == 121:
                for note in sustained[(port, message.channel)]:
                    note["sound_end_ticks"] = tick
                sustained[(port, message.channel)].clear()
                pedal_down[(port, message.channel)] = False
                pedal_events.append({**value, "down": False, "reset_controllers": True})
            elif message.control in [120, 123]:
                for (candidate_port, _, channel, _), queue in active.items():
                    if candidate_port == port and channel == message.channel:
                        while queue:
                            release(queue.popleft(), tick, "all_sound_off" if message.control == 120 else "all_notes_off")
                if message.control == 120:
                    for note in sustained[(port, message.channel)]:
                        note["sound_end_ticks"] = tick
                    sustained[(port, message.channel)].clear()
    if any(active.values()):
        raise ScoreImportError("The MIDI has unreleased notes at its end; provide the complete exported file.")
    if not notes:
        raise ScoreImportError("The MIDI contains no note attacks.")
    for pending in sustained.values():
        for note in pending:
            note["sound_end_ticks"] = file_end_ticks
    total_quarters = file_end_ticks / midi.ticks_per_beat
    # When the file has no meter, use four-quarter navigation windows without
    # pretending the MIDI contained a 4/4 time-signature event.
    grids = time_map if time_map and time_map[0]["onset_ticks"] == 0 else [{"onset_ticks": 0, "onset_quarters": 0.0, "length_quarters": 4.0, "provenance": "navigation_default"}, *time_map]
    measures = []
    for grid_index, grid in enumerate(grids):
        start = grid["onset_quarters"]
        end = grids[grid_index + 1]["onset_quarters"] if grid_index + 1 < len(grids) else total_quarters
        while start < end - 1e-9:
            finish = min(start + grid["length_quarters"], end)
            current_keys = [key for key in key_map if key["onset_quarters"] <= start]
            measures.append({"index": len(measures), "number": str(len(measures) + 1), "start_quarters": start, "length_quarters": finish - start,
                             "start_seconds": seconds(round(start * midi.ticks_per_beat)), "end_seconds": seconds(round(finish * midi.ticks_per_beat)),
                             "key": {key: value for key, value in current_keys[-1].items() if key not in ["onset_ticks", "onset_quarters"]} if current_keys else None,
                             "time": {key: value for key, value in grid.items() if key not in ["onset_ticks", "onset_quarters"]} if grid.get("beats") else None,
                             "repeat": {}, "endings": [], "tempos": [{**tempo, "offset_quarters": tempo["onset_quarters"] - start} for tempo in tempo_map if start <= tempo["onset_quarters"] < finish],
                             "provenance": "midi_beat_navigation_window"})
            if len(measures) > MAX_MIDI_WINDOWS:
                raise ScoreImportError("Too many beat navigation windows.")
            start = finish
    starts = [measure["start_quarters"] for measure in measures]
    events, grouped = [], defaultdict(list)
    for note in sorted(notes, key=lambda note: (note["start_ticks"], note["track_index"], note["id"])):
        q = note["start_ticks"] / midi.ticks_per_beat
        index = max(0, bisect_right(starts, q) - 1)
        track = tracks[note["track_index"]]
        end_tick = note["end_ticks"]
        sound_end = note["sound_end_ticks"] if note["sound_end_ticks"] is not None else end_tick
        event = {"id": note["id"], "part_id": track["id"], "measure_index": index, "measure_number": str(index + 1), "onset_quarters": q,
                 "offset_quarters": q - starts[index], "duration_quarters": (end_tick - note["start_ticks"]) / midi.ticks_per_beat,
                 "duration_fraction": f"{end_tick - note['start_ticks']}/{midi.ticks_per_beat}", "onset_seconds": seconds(note["start_ticks"]),
                 "duration_seconds": seconds(end_tick) - seconds(note["start_ticks"]), "sound_duration_quarters": (sound_end - note["start_ticks"]) / midi.ticks_per_beat,
                 "sound_duration_seconds": seconds(sound_end) - seconds(note["start_ticks"]), "pitch": midi_pitch(note["midi"]), "staff": 2 if track["hand"] == "left" else 1,
                 "voice": str(note["channel"] + 1), "hand": track["hand"], "hand_evidence": track["hand_evidence"], "channel": note["channel"], "port": note["port"], "track_index": note["track_index"],
                 "velocity": note["velocity"], "percussion": note["percussion"], "rest": False, "chord": False, "grace": False, "cue": False, "ties": [],
                 "start_ticks": note["start_ticks"], "end_ticks": end_tick, "sound_end_ticks": sound_end, "end_reason": note["end_reason"], "provenance": "midi_note_on_off"}
        events.append(event)
        grouped[(note["track_index"], note["channel"], note["start_ticks"])].append(event)
    for group in grouped.values():
        for event in group[1:]:
            event["chord"] = True
            event["chord_basis"] = "simultaneous_midi_onsets"
    if any(note["percussion"] for note in notes):
        warnings.append("Channel 10 contains percussion; select piano tracks before keyboard exercises.")
    note_parts = [track for track in tracks if any(event["part_id"] == track["id"] for event in events)]
    parts = [{**track, "staff_count": 1, "measure_count": len(measures), "note_count": sum(event["part_id"] == track["id"] for event in events)} for track in note_parts]
    metadata = {"title": title[:240], "composer": "", "key": key_signature(key_map[0]["midi_key"]) if key_map and key_map[0]["onset_ticks"] == 0 else None,
                "time": {key: value for key, value in time_map[0].items() if key not in ["onset_ticks", "onset_quarters"]} if time_map and time_map[0]["onset_ticks"] == 0 else None,
                "tempo": {"quarter_bpm": tempo_map[0]["quarter_bpm"], "bpm": tempo_map[0]["quarter_bpm"], "beat_unit": "quarter", "beat_unit_dots": 0, "explicit": tempo_map[0]["explicit"]},
                "measure_count": len(measures), "event_count": len(events), "part_count": len(parts), "total_quarters": total_quarters,
                "duration_seconds": file_duration, "ticks_per_beat": midi.ticks_per_beat, "midi_type": midi.type, "tracks": tracks, "copyright": copyrights,
                "source_format": "midi", "notation_available": False, "window_basis": "derived_midi_beat_windows", "pitch_range": {"min": min(note["midi"] for note in notes), "max": max(note["midi"] for note in notes)}, "file_end_ticks": file_end_ticks}
    return {"schema_version": 1, "source_format": "midi", "metadata": metadata, "parts": parts, "events": events, "measures": measures,
            "playback_order": list(range(len(measures))), "tempo_map": tempo_map, "time_signature_map": time_map, "key_signature_map": key_map,
            "pedal_events": pedal_events, "control_events": control_events, "warnings": warnings,
            "capabilities": {"timed_notes": True, "fingering": False, "automatic_fingering": False, "hand_assignment": "literal_track_name_hint_editable", "expressive_audio": False, "notation": False, "key_holds_separate_from_sustain": True}}


def quarters_at_seconds(parsed, value):
    entries = parsed["tempo_map"]
    entry = entries[max(0, bisect_right([entry["onset_seconds"] for entry in entries], value) - 1)]
    return entry["onset_quarters"] + (value - entry["onset_seconds"]) * entry["quarter_bpm"] / 60
