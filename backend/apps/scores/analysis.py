"""Describe an actual imported passage without inferring skill or fingering.

Facts refer to the written principal-note timeline, not expressive performance.
Suggested tempo and practice order are product choices, explicitly distinguished
from source facts. Chord tones are excluded from melodic leap calculations.
"""
from collections import defaultdict
from collections.abc import Mapping
import math

PIANO_LOW, PIANO_HIGH = 21, 108  # 88-key piano: A0 through C8.
HANDS = ("right", "left", "unknown")
BEAT_NAMES = {"quarter": "chorak", "dotted_quarter": "nuqtali chorak", "half": "yarim", "eighth": "sakkizlik"}
MAX_EXAMPLES = 24


def pitch_name(pitch):
    alter = pitch.get("alter", 0)
    if float(alter).is_integer():
        alteration = "♯" * int(alter) if alter >= 0 else "♭" * -int(alter)
    else:
        alteration = f"({alter:+g})"
    return f"{pitch['step']}{alteration}{pitch['octave']}"


def is_principal(event):
    return event.get("pitch") is not None and not any(event.get(flag, False) for flag in ("rest", "grace", "cue"))


def is_playable(event):
    midi = event["pitch"].get("midi")
    return isinstance(midi, (int, float)) and math.isfinite(midi) and float(midi).is_integer() and PIANO_LOW <= midi <= PIANO_HIGH


def source_chord_groups(events):
    """Use explicit <chord> membership, never guess harmony from simultaneity."""
    last, groups = {}, []
    for event in events:
        key = (event.get("part_id"), event.get("measure_index"))
        if not is_principal(event):
            last.pop(key, None)
            continue
        if event.get("chord") and key in last:
            groups[last[key]].append(event)
        else:
            groups.append([event])
            last[key] = len(groups) - 1
    return [group for group in groups if len(group) > 1]


def attack_ids(events):
    """A matched tied continuation is not a new principal attack."""
    active, result = {}, set()
    for event in sorted((e for e in events if is_principal(e)), key=lambda e: (e["onset_quarters"], e["id"])):
        key = (event.get("part_id"), event.get("staff"), event.get("voice"), event["pitch"].get("midi"))
        ties = event.get("ties", [])
        predecessor = active.get(key)
        continuation = "stop" in ties and predecessor is not None and abs(predecessor - event["onset_quarters"]) < 1e-8
        if not continuation:
            result.add(event["id"])
        if "start" in ties:
            active[key] = event["onset_quarters"] + event["duration_quarters"]
        else:
            active.pop(key, None)
    return result


def analyze_passage(parsed, start_index=0, end_index=None, hand_overrides=None, *, tempo_bpm=40, beat_unit="quarter"):
    """Return facts and four study steps for inclusive measure positions.

    `pitched_note_count` counts written principal pitched events, including tied
    segments. `playable_pitch_count` restricts those events to integer pitches in
    the learner's 88-key range. `attack_count` excludes tied continuations whose
    actual source predecessor exists, even before the selected range.
    """
    measures = parsed.get("measures", [])
    if not measures:
        raise ValueError("Nota taktlarisiz parcha tahlil qilinmaydi.")
    if end_index is None:
        end_index = min(start_index + 1, len(measures) - 1) if isinstance(start_index, int) else None
    if any(not isinstance(value, int) or isinstance(value, bool) for value in (start_index, end_index)) or not 0 <= start_index <= end_index < len(measures):
        raise ValueError("Parcha takt oralig'i nota chegarasidan tashqarida.")
    if not isinstance(tempo_bpm, (int, float)) or isinstance(tempo_bpm, bool) or not math.isfinite(tempo_bpm) or not 20 <= tempo_bpm <= 240 or beat_unit not in BEAT_NAMES:
        raise ValueError("Mashq tempi va urish birligi noto'g'ri.")
    overrides = hand_overrides or {}
    if not isinstance(overrides, Mapping) or any(hand not in HANDS for hand in overrides.values()):
        raise ValueError("Qo'l belgilari noto'g'ri.")

    def hand(event):
        value = overrides.get(event["id"], event.get("hand", "unknown"))
        return value if value in HANDS else "unknown"

    def range_data(beginning, ending):
        return {"start_index": beginning, "end_index": ending, "measure_numbers": [str(measures[i]["number"]) for i in range(beginning, ending + 1)]}

    def location(event):
        return {"event_id": event["id"], "pitch": pitch_name(event["pitch"]), "midi": event["pitch"]["midi"],
                "measure_index": event["measure_index"], "measure_number": str(event["measure_number"]), "offset_quarters": event["offset_quarters"]}

    all_events = parsed.get("events", [])
    selected = [event for event in all_events if start_index <= event["measure_index"] <= end_index]
    principal = [event for event in selected if is_principal(event)]
    principal.sort(key=lambda event: (event["onset_quarters"], event["part_id"], str(event["voice"]), event["staff"], event["id"]))
    attacks = attack_ids(all_events)
    chords = source_chord_groups(all_events)
    selected_chords = [group for group in chords if start_index <= group[0]["measure_index"] <= end_index]
    chord_members = {event["id"] for group in chords for event in group}
    counts = {label: sum(hand(event) == label for event in principal) for label in HANDS}

    tracks, leaps = defaultdict(list), {label: None for label in HANDS}
    for event in principal:
        if event["id"] in chord_members or event["id"] not in attacks or not is_playable(event):
            continue
        tracks[(event["part_id"], event["staff"], event["voice"], hand(event))].append(event)
    for key, track in tracks.items():
        for previous, current in zip(track, track[1:]):
            semitones = abs(current["pitch"]["midi"] - previous["pitch"]["midi"])
            label = key[-1]
            if leaps[label] is None or semitones > leaps[label]["semitones"]:
                leaps[label] = {"semitones": int(semitones), "from": location(previous), "to": location(current),
                                "part_id": key[0], "staff": key[1], "voice": key[2]}

    # Compare written rhythm and pitch/rhythm separately. Preserve voice/staff,
    # rests, ties and measure lengths; repeated timing does not prove same notes.
    rhythm_patterns, note_patterns, pitch_patterns = {}, {}, {}
    by_measure = defaultdict(list)
    for event in selected:
        by_measure[event["measure_index"]].append(event)
    for i in range(start_index, end_index + 1):
        rhythmic, pitched = [], []
        pitch_tracks = defaultdict(list)
        for event in sorted(by_measure[i], key=lambda event: (event["offset_quarters"], event["id"])):
            if event.get("grace") or event.get("cue"):
                continue
            base = (event["part_id"], event["staff"], str(event["voice"]), round(event["offset_quarters"], 9), round(event["duration_quarters"], 9),
                    bool(event.get("rest")), bool(event.get("chord")), tuple(sorted(event.get("ties", []))))
            rhythmic.append(base)
            pitched.append(base + (event["pitch"]["midi"] if event.get("pitch") else None,))
            if is_principal(event):
                pitch_tracks[(event["part_id"], event["staff"], str(event["voice"]))].append(event["pitch"]["midi"])
        # Empty measures alone should not become a note repetition claim.
        if rhythmic:
            rhythm_patterns[i] = (round(measures[i]["length_quarters"], 9), tuple(sorted(rhythmic)))
            note_patterns[i] = (round(measures[i]["length_quarters"], 9), tuple(sorted(pitched)))
        if pitch_tracks:
            pitch_patterns[i] = tuple((track, tuple(values)) for track, values in sorted(pitch_tracks.items()))

    def pattern_pairs(patterns):
        groups, examples, total = defaultdict(list), [], 0
        for index, pattern in patterns.items():
            groups[pattern].append(index)
        for positions in groups.values():
            total += len(positions) * (len(positions) - 1) // 2
            for position, first in enumerate(positions):
                if len(examples) >= MAX_EXAMPLES:
                    break
                for second in positions[position + 1:]:
                    examples.append({"first_index": first, "second_index": second, "first_number": str(measures[first]["number"]), "second_number": str(measures[second]["number"])})
                    if len(examples) >= MAX_EXAMPLES:
                        break
        return examples, total

    rhythm_pairs, rhythm_count = pattern_pairs(rhythm_patterns)
    note_pairs, note_count = pattern_pairs(note_patterns)
    pitch_pairs, pitch_count = pattern_pairs(pitch_patterns)
    rhythm_only_pairs = [pair for pair in rhythm_pairs if note_patterns[pair["first_index"]] != note_patterns[pair["second_index"]]]

    facts = {
        "pitched_note_count": len(principal), "playable_pitch_count": sum(is_playable(event) for event in principal),
        "pitch_scope": "88_key_piano_A0_C8", "attack_count": sum(event["id"] in attacks for event in principal),
        "chord_group_count": len(selected_chords), "chord_groups": [[location(event) for event in group] for group in selected_chords[:MAX_EXAMPLES]],
        "chord_groups_truncated": len(selected_chords) > MAX_EXAMPLES,
        "rest_count": sum(bool(event.get("rest")) and not event.get("cue") and not event.get("grace") for event in selected),
        "tie_count": sum(bool(event.get("ties")) for event in principal),
        "grace_count": sum(bool(event.get("grace")) for event in selected), "cue_count": sum(bool(event.get("cue")) for event in selected),
        "hand_counts": counts, "max_leaps": leaps,
        "rhythm_repetition": {"pairs": rhythm_pairs, "pair_count": rhythm_count, "note_pairs": note_pairs, "note_pair_count": note_count,
                              "rhythm_only_pairs": rhythm_only_pairs, "rhythm_only_pair_count": rhythm_count - note_count,
                              "pitch_sequence_pairs": pitch_pairs, "pitch_sequence_pair_count": pitch_count, "examples_truncated": max(rhythm_count, note_count, pitch_count) > MAX_EXAMPLES},
        "short_pitch_names": [pitch_name(event["pitch"]) for event in principal] if len(principal) <= 24 else None,
    }
    passage = range_data(start_index, end_index)
    labels = ", ".join(passage["measure_numbers"])
    tempo = {"bpm": tempo_bpm, "beat_unit": beat_unit, "basis": "practice_choice"}
    cautions = []
    if counts["unknown"]:
        cautions.append("Ayrim notalarning qo'li belgilanmagan; qo'lni notadan yoki o'zingizning aranjirovkangizdan belgilang.")
    if any(event["id"] not in overrides for event in principal if hand(event) != "unknown"):
        cautions.append("Qo'l belgilari staff joylashuvidan olingan taxminiy ko'rsatkich; barmoqlash dalili emas.")
    if facts["playable_pitch_count"] < facts["pitched_note_count"]:
        cautions.append("Ayrim tovushlar 88 klavish diapazonidan tashqarida yoki mikrotonli; variantni va kerakli klavishlarni tekshiring.")
    if not parsed.get("capabilities", {}).get("timed_notes", True):
        cautions.append("Importda avtomatik vaqtli ijro uchun tekshirilmagan belgilar bor; original notaga qarab qo'lda mashq qiling.")
    if facts["grace_count"] or facts["cue_count"]:
        cautions.append("Bu hisob asosiy notalarga tegishli; forşlag va cue notalari original notada alohida ko'rinadi.")

    instruction = f"{labels} raqamli taktlar. {facts['pitched_note_count']} ta asosiy nota yozuvi, {facts['rest_count']} ta pauza va {facts['tie_count']} ta bog'langan nota yozuvini original notada toping."
    if facts["short_pitch_names"]:
        instruction += " Yozilgan tovushlar: " + ", ".join(facts["short_pitch_names"]) + "."
    if rhythm_only_pairs:
        pair = rhythm_only_pairs[0]
        instruction += f" {pair['first_number']} va {pair['second_number']} taktlarida vaqt shakli bir xil, tovushlar farq qiladi."
    separate = "Avval o'ng qo'lni, keyin chap qo'lni shu taktlar oralig'ida alohida chaling." if counts["right"] and counts["left"] else "Belgilangani o'ng qo'l partiyasini shu taktlar oralig'ida ajrating." if counts["right"] else "Belgilangani chap qo'l partiyasini shu taktlar oralig'ida ajrating." if counts["left"] else "Notadagi qo'llarni belgilang; har bir belgilangan partiyani shu taktlar oralig'ida alohida tekshiring."
    largest = max((value for value in leaps.values() if value), key=lambda value: value["semitones"], default=None)
    if largest and largest["semitones"] > 7:
        separate += f" {largest['from']['pitch']} → {largest['to']['pitch']} orasida {largest['semitones']} yarim ton ({largest['from']['measure_number']} → {largest['to']['measure_number']} takt). Keyingi klavishga tushishni alohida sinang: bilak va qo'lni erkin ko'chiring, barmoqlarni majburan cho'zmang."
    unit = BEAT_NAMES[beat_unit]
    combine = f"Boshlang'ich mashq tempi: {unit} = {tempo_bpm}/min. Shu birlikni sanab, belgilangan partiyalarni birlashtiring. Bir vaqtning o'zida tushadigan yozilgan akkordlar va ushlanadigan tie notalarini original notadan tekshiring; qulaylikka qarab tempni o'zgartiring."
    if not principal:
        separate = "Bu oralig'da asosiy nota hujumi yo'q; yozilgan pauza davomiyligini birlik bilan sanang."
        combine = f"{unit} = {tempo_bpm}/min boshlang'ich tempda pauzalar orasidagi sanashni davom ettiring."
    context_start = max(0, start_index - 1)
    context_end = end_index if start_index > 0 else min(len(measures) - 1, end_index + 1)
    context_range = range_data(context_start, context_end)
    transfer = "Oldingi taktdan boshlang va tanlangan parchaning oxirigacha ulang." if start_index else "Tanlangan parchani undan keyingi takt bilan ulang." if context_end > end_index else "Shu yozilgan parchani yana boshidan sinang."
    transfer += " Bir o'tish ravon chiqqanini va qayerda to'xtaganingizni o'zingiz qayd eting."
    steps = [
        {"kind": "inspect", "title": "Aynan parchani o'qing", "instruction": instruction, "range": passage, "hand": "both", "tempo": None, "basis": "source_events"},
        {"kind": "separate", "title": "Qo'llarni ajrating", "instruction": separate, "range": passage, "hand": "separate", "tempo": tempo, "basis": "source_events_and_practice_choice"},
        {"kind": "combine", "title": "Sekin tempda ulang", "instruction": combine, "range": passage, "hand": "both", "tempo": tempo, "basis": "practice_choice"},
        {"kind": "transition", "title": "O'tishni kontekstda sinang", "instruction": transfer, "range": context_range, "hand": "both", "tempo": tempo, "basis": "practice_choice"},
    ]
    return {"schema_version": 1, "provenance": "imported_musicxml_events", "range": passage, "facts": facts, "steps": steps, "cautions": cautions,
            "claims": {"fingering_inferred": False, "difficulty_inferred": False, "performance_assessed": False, "mastery_inferred": False}}
