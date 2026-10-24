"""Original, inspectable MIDI for the expanded independent curriculum.

The writer is injected to avoid coupling this module to source adaptations.
All durations/onsets below are quarter-note units. No sustain is inferred.
"""

EXTRA_FAMILIES = {"intervals", "broken-chords", "syncopation", "voicing"}


def extra_exercise(family, level, write):
    notes = []
    bpm = [66, 80, 96][level]
    cycles = [2, 3, 4][level]

    def add(at, pitches, duration, hand="right", velocity=72):
        notes.extend((at, duration, pitch, hand, velocity) for pitch in pitches)

    for repeat in range(cycles):
        base = repeat*16
        if family == "intervals":
            white = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16]
            contour = [0, 1, 2, 3, 4, 3, 2, 1]
            distance = 5 if level == 1 else 2
            for i in range(8 if level == 0 else 16):
                degree = contour[i % 8]
                step = 2 if level == 0 else 1
                add(base+i*step, [60+white[degree], 60+white[degree+distance]], step*.75)
                if level == 2:
                    add(base+i, [48+white[degree], 48+white[degree+distance]], .75, "left", 52)
        elif family == "broken-chords":
            for bar, root in enumerate([48, 53, 55, 48] if level == 2 else [48]*4):
                for i, interval in enumerate([0, 7, 4, 7]*2):
                    add(base+bar*4+i*.5, [root+interval], .4, "left", 48)
                if level:
                    melody = [[72,76,79,76], [72,77,81,77], [71,74,79,74], [72,76,79,72]][bar] if level == 2 else [72,74,76,74]
                    for i, pitch in enumerate(melody):
                        add(base+bar*4+i, [pitch], .85, velocity=76)
        elif family == "syncopation":
            for i in range(16):
                add(base+i, [48], .16, "left", 48)
            for bar in range(4):
                attacks = [(.5, 1.25), (2.5, 1.25)] if level == 0 else [(i+.5, .8) for i in range(4)] if level == 1 else [(.5, 1.25), (2, 1.25), (3.5, .5)]
                for i, (at, duration) in enumerate(attacks):
                    add(base+bar*4+at, [64 if level == 0 else [64,67,65,64][i]], duration)
        elif family == "voicing":
            shapes = [[60,64,67]]*4 if level == 0 else [[60,64,67],[60,65,69],[59,62,67],[60,64,67]]
            for bar, pitches in enumerate(shapes):
                for at in [0, 2] if level != 1 else [0]:
                    start = base+bar*4+at
                    for pitch in pitches:
                        duration = (1.8 if pitch == max(pitches) else .6) if level == 2 else (1.5 if level == 0 else 3.2)
                        add(start, [pitch], duration, velocity=86 if pitch == max(pitches) else 42)
                if level == 2:
                    add(base+bar*4, [[48,41,43,48][bar]], 3.2, "left", 34)
        else:
            raise ValueError(family)
    return write(notes, bpm=bpm, end_quarters=cycles*16), {"authored_bpm":bpm, "pedal_demonstration":False}


def extra_theory(topic, write):
    notes = []
    meter, bpm, end = (4, 4), 76, None

    def add(at, pitches, duration=.85, velocity=72, hand="right"):
        notes.extend((at, duration, pitch, hand, velocity) for pitch in pitches)

    if topic == "major-scale":
        for base, pitches in [(0,[60,62,64,65,67,69,71,72]), (8,[67,69,71,72,74,76,78,79]), (16,[65,67,69,70,72,74,76,77])]:
            for i, pitch in enumerate(pitches):
                add(base+i, [pitch])
        end = 24
    elif topic == "minor-scales":
        for base, seventh in [(0,79), (16,80)]:
            pitches = [69,71,72,74,76,77,seventh,81]
            for i, pitch in enumerate(pitches+pitches[-2::-1]):
                add(base+i, [pitch])
        end = 32
    elif topic == "seventh-chords":
        for i, pitches in enumerate([[60,64,67,71], [60,64,67,70], [60,63,67,70]]):
            add(i*4, pitches, 3.2)
        end = 12
    elif topic == "voice-leading":
        for i, pitches in enumerate([[60,64,67], [60,65,69], [59,62,67], [60,64,67]]):
            add(i*4, pitches, 3.2)
            add(i*4, [[48,41,43,48][i]], 3.2, 46, "left")
        end = 16
    elif topic == "compound-meter":
        meter, bpm, end = (6, 8), 90, 6
        for i in range(12):
            add(i*.5, [60], .3, 88 if i % 6 == 0 else 72 if i % 3 == 0 else 48)
    elif topic == "cadences":
        # Three separated endings: V–I, IV–I, then I–V (half cadence).
        for base, chords in [(0,[[59,62,67],[60,64,67]]), (12,[[60,65,69],[60,64,67]]), (24,[[60,64,67],[59,62,67]])]:
            for i, pitches in enumerate(chords):
                add(base+i*4, pitches, 3.2)
                root = 43 if pitches == [59,62,67] else 41 if pitches == [60,65,69] else 48
                add(base+i*4, [root], 3.2, 48, "left")
        end = 32
    else:
        raise ValueError(f"Unknown theory topic: {topic}")
    return write(notes, bpm=bpm, meter=meter, end_quarters=end)
