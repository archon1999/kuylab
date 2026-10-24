"""Deterministic original exercises and transparent reductions of the supplied MIDI.

Adaptations keep source timing at 120 quarter BPM, except explicitly authored
reductions. They are teaching examples, never presented as the original score.
"""
from collections import defaultdict
from pathlib import Path
import hashlib
import io
import mido
from apps.scores.midi import parse_midi

SOURCE_PATH = Path(__file__).with_name("assets") / "still.mid"
SOURCE_SHA256 = "f0713b1de241c28522911a907a4464504ce7fbcaa8340ad9e1589881c2f3e7c8"
PPQ = 480


def source_data():
    content = SOURCE_PATH.read_bytes()
    if hashlib.sha256(content).hexdigest() != SOURCE_SHA256:
        raise ValueError("The supplied Still source changed; review and version the curriculum first.")
    parsed = parse_midi(content, "Winter Sonata — Still")
    # The file has two unnamed tracks. This is an authored role assignment,
    # not a literal hand label, fingering, key signature or meter from the file.
    for event in parsed["events"]:
        event["hand"] = "right" if event["track_index"] == 0 else "left"
        event["hand_evidence"] = "curated_track_role_inference"
    for part in parsed["parts"]:
        part["hand"] = "right" if part["index"] == 0 else "left"
        part["hand_evidence"] = "curated_track_role_inference"
    parsed["capabilities"]["hand_assignment"] = "curated_track_role_inference"
    return content, parsed


def midi_bytes(notes, bpm=80, pedal=None, meter=(4, 4), title="KuyLab original study", end_quarters=None):
    """notes: (start quarters, duration quarters, pitch, hand, velocity)."""
    midi = mido.MidiFile(type=1, ticks_per_beat=PPQ)
    conductor = mido.MidiTrack()
    conductor.extend([mido.MetaMessage("track_name", name=title[:100]), mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm))])
    if meter:
        conductor.append(mido.MetaMessage("time_signature", numerator=meter[0], denominator=meter[1]))
    last_quarter = max(n[0] + n[1] for n in notes)
    conductor.append(mido.MetaMessage("end_of_track", time=max(1, round(max(last_quarter, end_quarters or 0) * PPQ))))
    midi.tracks.append(conductor)
    for hand, channel in [("right", 0), ("left", 1)]:
        selected = [n for n in notes if n[3] == hand]
        if not selected:
            continue
        events = [(0, 0, mido.MetaMessage("track_name", name=f"{hand.title()} hand")), (0, 1, mido.Message("program_change", channel=channel, program=0))]
        for start, duration, pitch, _, velocity in selected:
            events.extend([(round(start * PPQ), 3, mido.Message("note_on", channel=channel, note=pitch, velocity=velocity)),
                           (round((start + max(duration, 1 / PPQ)) * PPQ), 2, mido.Message("note_off", channel=channel, note=pitch, velocity=0))])
        for quarter, down in pedal or []:
            events.append((round(quarter * PPQ), 1, mido.Message("control_change", channel=channel, control=64, value=127 if down else 0)))
        track, previous = mido.MidiTrack(), 0
        for ticks, _, message in sorted(events, key=lambda e: (e[0], e[1])):
            track.append(message.copy(time=max(0, ticks - previous)))
            previous = ticks
        track.append(mido.MetaMessage("end_of_track"))
        midi.tracks.append(track)
    output = io.BytesIO()
    midi.save(file=output)
    return output.getvalue()


def adapt_source(parsed, start, end, mode="both"):
    events = [event for event in parsed["events"] if start <= event["onset_seconds"] < end]
    if mode in {"left", "right"}:
        events = [event for event in events if event["hand"] == mode]
    elif mode == "bass":
        buckets = defaultdict(list)
        for event in events:
            if event["hand"] == "left":
                buckets[int((event["onset_seconds"] - start) / 2)].append(event)
        # A transparent reduction: lowest note in each two-second source window.
        events = sorted([min(group, key=lambda e: (e["pitch"]["midi"], e["onset_seconds"])) for group in buckets.values()], key=lambda e: e["onset_seconds"])
    elif mode == "melody":
        buckets = defaultdict(list)
        for event in events:
            if event["hand"] == "right":
                buckets[round(event["onset_seconds"] * 10)].append(event)
        events = sorted([max(group, key=lambda e: e["pitch"]["midi"]) for group in buckets.values()], key=lambda e: e["onset_seconds"])
    if not events:
        raise ValueError("Empty teaching selection")
    notes = [((e["onset_seconds"] - start) * 2, min(e["duration_seconds"], end - e["onset_seconds"]) * 2,
              e["pitch"]["midi"], e["hand"], e["velocity"]) for e in events]
    return midi_bytes(notes, bpm=120, meter=None, title="Still teaching adaptation"), [event["id"] for event in events]


def lesson_stage_midi(parsed, start, end, selection, speed_percent, title="Still reviewed teaching stage"):
    """Curated source-event indices, never an arbitrary time-bucket melody guess.

    Selection maps each hand to reviewed indices within the source range, or
    'all'. A single tempo scales all attacks/releases equally, including the
    initial rest. The conductor retains the entire teaching window's silence.
    """
    if not 0 <= start < end <= parsed["metadata"]["duration_seconds"] + 1e-6:
        raise ValueError("Invalid lesson range")
    if speed_percent not in (60, 80, 100):
        raise ValueError("Unsupported teaching tempo")
    selected = []
    for hand, indices in selection.items():
        if hand not in ("left", "right"):
            raise ValueError("Unknown teaching hand")
        candidates = sorted(
            (event for event in parsed["events"] if event["hand"] == hand and start <= event["onset_seconds"] < end),
            key=lambda event: event["onset_seconds"],
        )
        if indices == "all":
            selected.extend(candidates)
        else:
            if len(indices) != len(set(indices)) or any(i < 0 or i >= len(candidates) for i in indices):
                raise ValueError("Invalid curated source-note index")
            selected.extend(candidates[i] for i in indices)
    selected.sort(key=lambda event: (event["onset_seconds"], event["id"]))
    if not selected:
        raise ValueError("Empty lesson stage")
    notes = [((e["onset_seconds"] - start) * 2,
              min(e["duration_seconds"], end - e["onset_seconds"]) * 2,
              e["pitch"]["midi"], e["hand"], e["velocity"]) for e in selected]
    data = midi_bytes(notes, bpm=120 * speed_percent / 100, meter=None,
                      title=title, end_quarters=(end-start)*2)
    return data, [event["id"] for event in selected]


def exercise_notes(family, level):
    """Twelve authored patterns at three substantially different difficulties."""
    notes, pedal = [], []
    speed = [66, 80, 96][level]
    repetitions = [2, 3, 4][level]
    def add(start, pitch, duration=.8, hand="right", velocity=72):
        notes.append((start, duration, pitch, hand, velocity))
    scale = [0, 2, 4, 5, 7, 9, 11, 12]
    for r in range(repetitions):
        base = r * 16
        if family == "five-finger":
            pattern = [[0, 2, 4, 5, 7, 5, 4, 2], [0, 4, 2, 5, 4, 7, 5, 2], [0, 5, 2, 7, 4, 2, 5, 4]][level]
            for i, interval in enumerate(pattern * 2):
                add(base + i, 60 + interval, .8, "right")
                add(base + i, 48 + (interval if level < 2 else pattern[-1-i % 8]), .8, "left", 58)
        elif family == "scales":
            count = 1 if level == 0 else 2
            pattern = [*scale[:-1], *[x + 12 for x in scale]] if count == 2 else scale
            pattern = pattern + pattern[-2:0:-1]
            step = 16 / len(pattern)
            for i, interval in enumerate(pattern):
                add(base + i * step, 60 + interval, step * .9)
                if level:
                    add(base + i * step, 48 + (interval if level == 1 else 24 - interval), step * .9, "left", 60)
        elif family == "arpeggios":
            pattern = [[0,4,7,4], [0,4,7,12,7,4], [0,4,7,12,16,19,24,19,16,12,7,4]][level]
            for i in range(24 if level == 2 else 16):
                step = 16 / (24 if level == 2 else 16)
                add(base+i*step, 60+pattern[i%len(pattern)], step*.85)
                if level: add(base+i*step, 36+pattern[i%len(pattern)], step*.85, "left", 56)
        elif family == "chords":
            voicings = [[60,64,67],[60,65,69],[59,62,67],[60,64,67]] if level else [[60,64,67]]*4
            if level == 2: voicings = [[60,64,67,71],[60,64,69,72],[59,62,65,69],[60,64,67,72]]
            for i, chord in enumerate(voicings):
                for pitch in chord: add(base+i*4, pitch, 3.2)
                add(base+i*4, [48,41,43,48][i], 3.2, "left", 56)
        elif family == "coordination":
            right_step = [1,.5,.5][level]
            left_step = [2,1,.75][level]
            for i in range(round(16/right_step)): add(base+i*right_step, 60+[0,2,4,5,7,5,4,2][i%8], right_step*.8)
            for i in range(int(16/left_step)): add(base+i*left_step, 48+[0,7,4,7][i%4], left_step*.7, "left", 56)
        elif family == "rhythm":
            pattern = [[1,1,2],[.75,.25,1,2],[.5,.5,1/3,1/3,1/3,1,1]][level]
            at = base
            while at < base+16-1e-6:
                for duration in pattern:
                    if at >= base+16: break
                    add(at, 60, min(duration*.7,base+16-at)); at+=duration
            for i in range(16): add(base+i, 48, .15, "left", 48)
        elif family == "leaps":
            distance = [7,12,19][level]
            for i in range(16): add(base+i, 48+(distance if i%2 else 0), .45, "left", 66)
            if level:
                for i in range(8): add(base+i*2, 72+[0,2,4,2][i%4], 1.6)
        elif family == "octaves":
            for i in range(8 if level == 0 else 16):
                step = 2 if level == 0 else 1
                pitch = 60+([0,2,4,5,7,5,4,2][i%8] if level else 0)
                for p in [pitch,pitch+12]: add(base+i*step,p,step*.5)
                if level == 2:
                    for p in [pitch-24,pitch-12]: add(base+i*step,p,step*.5,"left",56)
        elif family == "articulation":
            for i in range(16):
                short = i>=8 if level==0 else i%2==1
                add(base+i,60+[0,2,4,5,7,5,4,2][i%8],.2 if short else .98)
                if level: add(base+i,48+[0,4,7,4][i%4], .98 if level==2 and short else .2,"left",54)
        elif family == "balance":
            for i in range(16):
                velocity = 70 if level==0 else 56+round(30*(1-abs(7.5-i)/7.5))
                add(base+i,72+[0,2,4,5,7,5,4,2][i%8],.9,velocity=velocity)
                lower = [48,55,60,55][i%4]
                add(base+i,lower,.8,"left",38 if level<2 else 32+(i%4)*3)
        elif family == "pedal":
            for i, root in enumerate([48,53,55,48]):
                at = base+i*4
                for pitch in [root,root+4 if root !=53 else root+4,root+7]: add(at,pitch,1.2,"left",55)
                pedal.extend([(at,False),(at+.12,True),(at+3.85,False)])
                if level:
                    for j in range(4): add(at+j,72+[0,4,7,4][j],.7,velocity=64)
                if level==2:
                    pedal.extend([(at+2,False),(at+2.1,True)])
        elif family == "continuity":
            melody = [0,2,4,7,5,4,2,0,4,5,7,9,7,4,2,0]
            for i,p in enumerate(melody):
                if level==2 and i%4==3: continue
                add(base+i,60+p,.85)
                if level: add(base+i,48+[0,7,4,7][i%4],.7,"left",50)
        else: raise ValueError(f"Unknown study family: {family}")
    return midi_bytes(notes, speed, pedal=pedal), {"authored_bpm":speed,"pedal_demonstration":bool(pedal)}


def theory_midi(topic):
    """One concrete audible demonstration for every authored practical concept."""
    notes, pedal = [], []
    def chord(at, pitches, duration=2, velocity=70, hand="right"):
        notes.extend((at,duration,p,hand,velocity) for p in pitches)
    if topic == "keyboard":
        for i,p in enumerate([60,61,62,63,64,65,66,67]): chord(i,[p],.8)
    elif topic == "pulse":
        for i in range(16): chord(i,[48],.12,45,"left")
        for i in [0,2,3,4,4.5,5,6,8,10,12,14]: chord(i,[64],.35)
    elif topic == "durations":
        at=0
        for d in [4,2,2,1,1,1,1,.5,.5,.5,.5,.5,.5,.5,.5]: chord(at,[60],d*.9);at+=d
    elif topic == "rests":
        for i in [0,1,4,6,8,9,12,14]: chord(i,[60],.75)
    elif topic == "intervals":
        for i,p in enumerate([62,64,65,67,69,71,72]): chord(i*3,[60],.8);chord(i*3+1,[p],1.5)
    elif topic == "major-minor": chord(0,[60,64,67],3);chord(4,[60,63,67],3)
    elif topic == "triads":
        for i,p in enumerate([60,64,67]): chord(i,[p],.8)
        chord(4,[60,64,67],4)
    elif topic == "inversions":
        for i,p in enumerate([[60,64,67],[64,67,72],[67,72,76]]): chord(i*4,p,3)
    elif topic == "tonic-dominant":
        for i,p in enumerate([[60,64,67],[59,62,67],[60,64,67]]): chord(i*4,p,3)
    elif topic == "arpeggio":
        chord(0,[60,64,67],3)
        for i,p in enumerate([60,64,67,72,67,64,60]): chord(4+i*.5,[p],.45)
    elif topic == "meter":
        for i in range(12): chord(i,[60],.4,85 if i%3==0 else 50)
    elif topic == "syncopation":
        for i in range(8): chord(i,[48],.1,45,"left");chord(i+.5,[64],.8)
    elif topic == "legato":
        for i,p in enumerate([60,62,64,65,67,65,64,62]): chord(i,[p],.98 if i<4 else .2)
    elif topic == "dynamics":
        for i in range(16): chord(i,[60],.8,35+round(50*(1-abs(7.5-i)/7.5)))
    elif topic == "voicing":
        for i,p in enumerate([72,74,76,74,72,71,69,72]):
            chord(i,[p],.9,78);chord(i,[48,55,60],.8,38,"left")
    elif topic == "pedal":
        chord(0,[60,64,67],1);chord(4,[60,65,69],1)
        pedal=[(.1,True),(3.9,False),(4.1,True),(7.5,False)]
    elif topic == "phrasing":
        for i,p in enumerate([60,62,64,67,65,64,62,60]): chord(i,[p],.7 if i==3 else .9,64 if i<4 else 58)
    elif topic == "practice":
        for repeat in range(3):
            for i,p in enumerate([60,64,67,64]): chord(repeat*6+i,[p],.8)
    else: raise ValueError(topic)
    return midi_bytes(notes,bpm=76,pedal=pedal,meter=(3,4) if topic=="meter" else (4,4))
