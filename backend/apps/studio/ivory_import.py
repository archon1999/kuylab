"""Offline preparation of a reviewed import plan; never guesses intro cuts."""
from collections import defaultdict, deque
from hashlib import sha256
import io
import json
from pathlib import Path
import re
from statistics import median

import mido
from apps.scores.midi import parse_midi


def trim_channel_intro(data, start_seconds):
    """Drop attacks before an explicit boundary, preserving all later timing.

    Notes crossing the boundary belong to the removed intro and are not
    retriggered. Active tempo/program/controller state is restored at zero.
    No onset-gap heuristic or automatic musical-intro removal runs here.
    """
    if start_seconds == 0:
        return data, 0, 0.0
    original = mido.MidiFile(file=io.BytesIO(data))
    elapsed, last_tick, tempo = 0.0, 0, 500000
    all_messages = []
    for track_index, track in enumerate(original.tracks):
        tick = 0
        for order, message in enumerate(track):
            tick += message.time
            all_messages.append((tick, track_index, order, message))
    all_messages.sort(key=lambda row: row[:3])
    cut_tick = None
    for tick, _, _, message in all_messages:
        seconds = elapsed + mido.tick2second(tick - last_tick, original.ticks_per_beat, tempo)
        if seconds >= start_seconds:
            cut_tick = last_tick + round(mido.second2tick(start_seconds - elapsed, original.ticks_per_beat, tempo))
            break
        if message.type == "set_tempo":
            elapsed, last_tick, tempo = seconds, tick, message.tempo
    if cut_tick is None:
        raise ValueError("Intro boundary lies beyond this MIDI.")
    actual_seconds = elapsed + mido.tick2second(cut_tick-last_tick, original.ticks_per_beat, tempo)
    if cut_tick <= 0:
        raise ValueError("A positive reviewed intro boundary is required.")
    global_meta, channel_states, track_ports = {}, {}, defaultdict(int)
    state_types = {"program_change", "control_change", "pitchwheel", "aftertouch", "polytouch"}
    for sequence, (tick, track_index, _, message) in enumerate(all_messages):
        if tick >= cut_tick:
            break
        if message.type == "midi_port":
            track_ports[track_index] = message.port
        if message.type in {"set_tempo", "key_signature", "time_signature"}:
            global_meta[message.type] = message
        elif message.type in state_types:
            # Channel state belongs to its MIDI port/channel, even when later
            # updates live in another track. Replay final updates in their
            # original stream order (including bank/program and reset order).
            key = (track_ports[track_index], message.channel, message.type,
                   getattr(message,"control",None), getattr(message,"note",None))
            channel_states[key] = (sequence,track_ports[track_index],message)
    if "set_tempo" not in global_meta:
        global_meta["set_tempo"] = mido.MetaMessage("set_tempo", tempo=500000)
    output = mido.MidiFile(type=original.type, ticks_per_beat=original.ticks_per_beat)
    for track_index, track in enumerate(original.tracks):
        tick, states, retained, active = 0, {}, [], defaultdict(deque)
        for order, message in enumerate(track):
            tick += message.time
            if message.type == "note_on" and message.velocity > 0:
                keep = tick >= cut_tick
                active[(message.channel, message.note)].append(keep)
                if keep:
                    retained.append((tick-cut_tick, order, message))
            elif message.type in {"note_on", "note_off"}:
                queue = active[(message.channel, message.note)]
                if queue and queue.popleft():
                    retained.append((max(0,tick-cut_tick), order, message))
            elif message.type == "end_of_track":
                retained.append((max(0,tick-cut_tick), order, message))
            elif tick >= cut_tick:
                retained.append((tick-cut_tick, order, message))
            elif message.type not in state_types | {"set_tempo", "key_signature", "time_signature", "text", "lyrics", "marker", "cue_marker"}:
                state_key = (message.type, getattr(message,"channel",None), getattr(message,"control",None))
                states[state_key] = message
        new_track = mido.MidiTrack()
        output.tracks.append(new_track)
        if track_index == 0:
            new_track.extend(message.copy(time=0) for message in global_meta.values())
        new_track.extend(message.copy(time=0) for message in states.values())
        if track_index == 0 and channel_states:
            current_port = track_ports[0]
            for _,port,message in sorted(channel_states.values(),key=lambda value:value[0]):
                if port != current_port:
                    new_track.append(mido.MetaMessage("midi_port",port=port,time=0))
                    current_port = port
                new_track.append(message.copy(time=0))
            if current_port != track_ports[0]:
                new_track.append(mido.MetaMessage("midi_port",port=track_ports[0],time=0))
        previous = 0
        for tick, _, message in retained:
            new_track.append(message.copy(time=tick-previous))
            previous = tick
    buffer = io.BytesIO()
    output.save(file=buffer)
    return buffer.getvalue(), cut_tick, actual_seconds


def display_roles(parsed):
    tracks = defaultdict(list)
    for event in parsed["events"]:
        if event.get("pitch") and not event.get("percussion"):
            tracks[event["track_index"]].append(event["pitch"]["midi"])
    if len(tracks) == 2:
        ordered = sorted(tracks, key=lambda index:(median(tracks[index]), index))
        return {"method":"tracks", "tracks":{str(ordered[0]):"left", str(ordered[1]):"right"},
                "evidence":"reviewed_export_track_median_pitch_roles_not_fingering"}
    return {"method":"pitch_split", "split_pitch":60,
            "evidence":"curated_C4_display_layer_split_not_physical_hands"}


def build_catalog(plan, source_dir, target_dir, expected_count=83):
    source_dir, target_dir = Path(source_dir).resolve(), Path(target_dir).resolve()
    groups = plan["groups"] if isinstance(plan, dict) else plan
    download_manifest = json.loads((source_dir/"manifest.json").read_text(encoding="utf-8"))
    downloads = {item["filename"]:item for item in download_manifest["items"]}
    selected = [variant for group in groups for variant in group["variants"]]
    if len(selected) != expected_count or {item["filename"] for item in selected} != set(downloads):
        raise ValueError("Import plan must account for every supplied MIDI exactly once.")
    if len({group["code"] for group in groups}) != len(groups) or len({group["slug"] for group in groups}) != len(groups):
        raise ValueError("Composition codes and slugs must be unique.")
    prepared, original_files, output_groups = {}, {}, []
    for group in groups:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",group["code"]) or len(group["code"])>56:
            raise ValueError("Invalid stable composition code.")
        if not group["variants"] or len({v["id"] for v in group["variants"]})!=len(group["variants"]):
            raise ValueError("Each composition needs uniquely identified performances.")
        entry = {key:group[key] for key in ("code","slug","title","composer","collection")}
        entry["replaces_existing"] = bool(group.get("existing_code"))
        entry["variants"] = []
        for variant in group["variants"]:
            name, identifier = variant["filename"],variant["id"]
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*\.mid",name) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",identifier) or len(identifier)>32:
                raise ValueError("Unsafe MIDI filename or performance identity.")
            if len(f"composition:{group['code']}:{identifier}")>100:
                raise ValueError("Performance identity exceeds the stable asset key limit.")
            original = downloads[name]
            data = (source_dir/name).read_bytes()
            digest = sha256(data).hexdigest()
            if digest!=original["validation"]["sha256"] or digest!=variant.get("source_sha256",digest):
                raise ValueError(f"{name}: supplied checksum changed.")
            start = float(variant.get("trim_start_seconds",0))
            if start<0 or start and not variant.get("trim_reason"):
                raise ValueError("Only an explicitly reviewed channel-intro cut is supported.")
            content, tick, actual_start = trim_channel_intro(data,start)
            parsed = parse_midi(content,group["title"])
            if parsed["pedal_events"]:
                raise ValueError(f"{name}: a pedal-free performance was expected.")
            if any(e.get("percussion") for e in parsed["events"]):
                raise ValueError(f"{name}: percussion requires a separate review.")
            preview_start = float(variant.get("preview_start",0))
            duration = parsed["metadata"]["duration_seconds"]
            if not 0<=preview_start<duration or variant["difficulty"] not in range(1,6):
                raise ValueError(f"{name}: preview or difficulty needs review.")
            value = {**variant, "sha256":sha256(content).hexdigest(), "source_sha256":digest,
                     "trim_start_seconds":actual_start, "trim_start_ticks":tick,
                     "note_count":len(parsed["events"]), "duration_seconds":duration,
                     "omitted_note_count":original["validation"]["note_count"]-len(parsed["events"]),
                     "hand_roles":display_roles(parsed), "preview_start":preview_start,
                     "preview_duration":min(float(variant.get("preview_duration",16)),duration-preview_start),
                     "source_url":variant.get("source_url",original["url"]),
                     "ivory_player_url":original["ivory_player_url"]}
            if original.get("performer") and not value.get("performer"):
                value["performer"] = original["performer"]
            prepared[name] = content
            if start:
                original_files[name] = data
            entry["variants"].append(value)
        output_groups.append(entry)
    target_dir.mkdir(parents=True,exist_ok=True)
    for name,content in prepared.items():
        (target_dir/name).write_bytes(content)
    if original_files:
        (target_dir/"originals").mkdir(exist_ok=True)
        for name,content in original_files.items():
            (target_dir/"originals"/name).write_bytes(content)
    temporary = target_dir/"manifest.json.tmp"
    temporary.write_text(json.dumps(output_groups,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    temporary.replace(target_dir/"manifest.json")
    return output_groups
