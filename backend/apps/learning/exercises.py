"""Render original teaching drills, independent of any copyrighted song score."""
import math
import re
from fractions import Fraction
from xml.etree import ElementTree as ET


def child(parent, name, text=None, **attributes):
    element = ET.SubElement(parent, name, attributes)
    if text is not None:
        element.text = str(text)
    return element


def pitch(note_name):
    match = re.fullmatch(r"([A-G])([♯♭#b]*)([0-8])", note_name)
    if not match:
        raise ValueError("Original mashq nota nomi noto'g'ri.")
    letter, accidental, octave = match.groups()
    return letter, accidental.count("♯") + accidental.count("#") - accidental.count("♭") - accidental.count("b"), int(octave)


def authored_hands(lesson):
    exercise = lesson.content.get("exercise", {})
    hands = set()
    for index, name in enumerate(exercise.get("notes", [])):
        hand = exercise.get("note_hands", [])[index] if index < len(exercise.get("note_hands", [])) else "left" if pitch(name)[2] <= 3 else "right"
        hands.add(hand)
    if exercise.get("chords"):
        hands.add("right")
    if exercise.get("left_hand"):
        hands.add("left")
    return [hand for hand in ["right", "left"] if hand in hands]


def drill_xml(lesson):
    exercise = lesson.content.get("exercise", {})
    note_names = exercise.get("notes", [])
    if not note_names and not exercise.get("chords"):
        raise ValueError("Bu darsda original nota mashqi yo'q.")
    divisions = 48
    signature = exercise.get("time_signature", "4/4")
    beats, denominator = [int(value) for value in signature.split("/")]
    measure_length = Fraction(beats * 4, denominator)
    durations = exercise.get("duration_quarters")
    if durations is None:
        durations = [Fraction(str(value)) / 2 for value in exercise.get("duration_eighths", [2] * len(note_names))]
    if len(durations) != len(note_names):
        raise ValueError("Original mashq davomiyliklari notalarga mos emas.")
    events = []
    position = Fraction(0)
    for index, (name, duration) in enumerate(zip(note_names, durations)):
        duration = Fraction(str(duration))
        hand = exercise.get("note_hands", [])[index] if index < len(exercise.get("note_hands", [])) else "left" if pitch(name)[2] <= 3 else "right"
        events.append({"notes": [name], "start": position, "duration": duration, "hand": hand})
        position += duration
    for chord in exercise.get("chords", []):
        events.append({"notes": chord, "start": position, "duration": Fraction(2), "hand": "right"})
        position += 2
    for left in exercise.get("left_hand", []):
        start = Fraction(str(left["start_quarters"])) if "start_quarters" in left else Fraction(str(left["start_eighth"])) / 2
        duration = Fraction(str(left["duration_quarters"])) if "duration_quarters" in left else Fraction(str(left["duration_eighths"])) / 2
        events.append({"notes": [left["note"]], "start": start, "duration": duration, "hand": "left"})
    total = max(event["start"] + event["duration"] for event in events)
    count = math.ceil(total / measure_length)
    hands = authored_hands(lesson)
    root = ET.Element("score-partwise", version="4.0")
    child(child(root, "work"), "work-title", "KuyLab original · " + lesson.title)
    identification = child(root, "identification")
    child(identification, "creator", "KuyLab", type="composer")
    child(identification, "rights", "Original exercise authored for KuyLab. CC0. Not a song transcription.")
    score_part = child(child(root, "part-list"), "score-part", id="P1")
    child(score_part, "part-name", "Piano")
    part = child(root, "part", id="P1")
    for measure_index in range(count):
        measure = child(part, "measure", number=str(measure_index + 1))
        if measure_index == 0:
            attributes = child(measure, "attributes")
            child(attributes, "divisions", divisions)
            key = exercise.get("key_signature")
            if key:
                key_element = child(attributes, "key")
                child(key_element, "fifths", key["fifths"])
                if key.get("mode"):
                    child(key_element, "mode", key["mode"])
            time = child(attributes, "time")
            child(time, "beats", beats)
            child(time, "beat-type", denominator)
            child(attributes, "staves", len(hands))
            for staff, hand in enumerate(hands, 1):
                clef = child(attributes, "clef", number=str(staff))
                child(clef, "sign", "G" if hand == "right" else "F")
                child(clef, "line", 2 if hand == "right" else 4)
            direction = child(measure, "direction", placement="above")
            metronome = child(child(direction, "direction-type"), "metronome")
            unit = exercise.get("beat_unit", "quarter")
            child(metronome, "beat-unit", "quarter" if unit == "dotted_quarter" else unit)
            if unit == "dotted_quarter":
                child(metronome, "beat-unit-dot")
            bpm = exercise.get("bpm", 50)
            child(metronome, "per-minute", bpm)
            child(direction, "sound", tempo=str(bpm * {"half": 2, "quarter": 1, "eighth": 0.5, "dotted_quarter": 1.5}.get(unit, 1)))
        start = measure_index * measure_length
        end = start + measure_length
        for staff, hand in enumerate(hands, 1):
            if staff > 1:
                child(child(measure, "backup"), "duration", int(measure_length * divisions))
            cursor = start
            staff_events = sorted([event for event in events if event["hand"] == hand and event["start"] < end and event["start"] + event["duration"] > start], key=lambda event: event["start"])
            for event in staff_events:
                beginning = max(start, event["start"])
                finish = min(end, event["start"] + event["duration"])
                if beginning > cursor:
                    append_note(measure, None, beginning - cursor, divisions, staff)
                for chord_index, name in enumerate(event["notes"]):
                    append_note(measure, name, finish - beginning, divisions, staff, chord=chord_index > 0,
                                tie_start=finish < event["start"] + event["duration"], tie_stop=beginning > event["start"])
                cursor = finish
            if cursor < end:
                append_note(measure, None, end - cursor, divisions, staff)
        if measure_index == count - 1:
            child(child(measure, "barline", location="right"), "bar-style", "light-heavy")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def append_note(measure, name, duration, divisions, staff, chord=False, tie_start=False, tie_stop=False):
    note = child(measure, "note")
    if chord:
        child(note, "chord")
    if name is None:
        child(note, "rest")
    else:
        letter, accidental, octave = pitch(name)
        value = child(note, "pitch")
        child(value, "step", letter)
        if accidental:
            child(value, "alter", accidental)
        child(value, "octave", octave)
    child(note, "duration", int(duration * divisions))
    for condition, kind in [(tie_stop, "stop"), (tie_start, "start")]:
        if condition:
            child(note, "tie", type=kind)
    child(note, "voice", staff)
    types = {Fraction(4): ("whole", False), Fraction(3): ("half", True), Fraction(2): ("half", False), Fraction(3, 2): ("quarter", True), Fraction(1): ("quarter", False), Fraction(3, 4): ("eighth", True), Fraction(1, 2): ("eighth", False), Fraction(1, 4): ("16th", False)}
    if duration in types:
        type_name, dotted = types[duration]
        child(note, "type", type_name)
        if dotted:
            child(note, "dot")
    child(note, "staff", staff)
    if tie_stop or tie_start:
        notations = child(note, "notations")
        if tie_stop:
            child(notations, "tied", type="stop")
        if tie_start:
            child(notations, "tied", type="start")
