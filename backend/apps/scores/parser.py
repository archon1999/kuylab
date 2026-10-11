"""Bounded MusicXML partwise import; original XML remains the notation authority.

Timing follows MusicXML division units, backup/forward and chord semantics.
References: https://www.w3.org/2021/06/musicxml40/tutorial/midi-compatible-part/
https://www.w3.org/2021/06/musicxml40/tutorial/compressed-mxl-files/
This is deliberately not a transcription or fingering generator.
"""
import io
import re
from fractions import Fraction
from pathlib import PurePosixPath
from xml.etree.ElementTree import TreeBuilder
from xml.parsers import expat
import zipfile

MAX_UPLOAD_BYTES = 8 * 1024 * 1024
MAX_XML_BYTES = 16 * 1024 * 1024
MAX_ZIP_MEMBERS = 128
MAX_ELEMENTS = 250_000
MAX_NOTES = 30_000
MAX_MEASURES = 2_000
MAX_PARTS = 32
MAX_PLAYBACK_MEASURES = 8_000
BEAT_QUARTERS = {"whole": 4, "half": 2, "quarter": 1, "eighth": .5, "16th": .25, "32nd": .125, "64th": .0625}
MUSICXML_PUBLIC_IDS = {f"-//Recordare//DTD MusicXML {version} Partwise//EN" for version in ["1.0", "1.1", "2.0", "3.0", "3.1", "4.0"]}
MUSICXML_SYSTEM_IDS = {"http://www.musicxml.org/dtds/partwise.dtd", "https://www.musicxml.org/dtds/partwise.dtd"}


class ScoreImportError(ValueError):
    pass


def safe_xml(data):
    """Accept the standard reference-only DOCTYPE; never read or expand a DTD."""
    if not data or len(data) > MAX_XML_BYTES:
        raise ScoreImportError("XML bo'sh yoki 16 MB chegaradan katta.")
    builder = TreeBuilder()
    parser = expat.ParserCreate(namespace_separator="}")
    # This also prevents reading the external DTD subset on normal exports.
    parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_NEVER)
    depth = count = note_count = measure_count = 0

    def name(value):
        return "{" + value if "}" in value else value

    def start(tag, attrs):
        nonlocal depth, count, note_count, measure_count
        depth += 1
        count += 1
        local = tag.rsplit("}", 1)[-1]
        note_count += local == "note"
        measure_count += local == "measure"
        if depth > 64 or count > MAX_ELEMENTS or note_count > MAX_NOTES or measure_count > MAX_MEASURES * MAX_PARTS:
            raise ScoreImportError("Nota fayli tuzilishi yoki hajmi import chegarasidan katta.")
        if local in {"image", "credit-image", "part-link", "opus", "script"} or any(k.rsplit("}", 1)[-1] == "href" for k in attrs):
            raise ScoreImportError("Tashqi rasm yoki havola resurslari import qilinmaydi. Mustaqil MusicXML eksport qiling.")
        builder.start(name(tag), {name(k): v for k, v in attrs.items()})

    def end(tag):
        nonlocal depth
        builder.end(name(tag))
        depth -= 1

    def reject(*args):
        raise ScoreImportError("Ichki DTD, entity va XML stylesheet qo'llab-quvvatlanmaydi.")

    def doctype(name, system_id, public_id, has_internal_subset):
        # W3C's own Hello World example includes this external reference.
        # Recognize it as metadata only; no URL is opened and no DTD is parsed.
        if has_internal_subset or name != "score-partwise" or public_id not in MUSICXML_PUBLIC_IDS or system_id not in MUSICXML_SYSTEM_IDS:
            raise ScoreImportError("Faqat standart tashqi MusicXML Partwise DOCTYPE, ichki DTDsiz, qo'llab-quvvatlanadi.")

    parser.StartElementHandler = start
    parser.EndElementHandler = end
    parser.CharacterDataHandler = builder.data
    parser.StartDoctypeDeclHandler = doctype
    parser.EntityDeclHandler = reject
    parser.ExternalEntityRefHandler = reject
    parser.SkippedEntityHandler = reject
    parser.ProcessingInstructionHandler = reject
    try:
        for offset in range(0, len(data), 64 * 1024):
            parser.Parse(data[offset:offset + 64 * 1024], False)
        parser.Parse(b"", True)
        root = builder.close()
    except (expat.ExpatError, LookupError, UnicodeError) as exc:
        raise ScoreImportError("XML buzilgan yoki tugallanmagan.") from exc
    # Namespace-qualified MusicXML exports use the same element semantics.
    for element in root.iter():
        element.tag = element.tag.rsplit("}", 1)[-1]
    return root


def extract_musicxml(data, filename):
    if len(data) > MAX_UPLOAD_BYTES:
        raise ScoreImportError("Fayl 8 MB chegaradan katta.")
    suffix = PurePosixPath(filename.replace("\\", "/")).suffix.lower()
    if suffix not in {".musicxml", ".xml", ".mxl"}:
        raise ScoreImportError(".musicxml, .xml yoki .mxl faylini tanlang.")
    if suffix != ".mxl":
        return data
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = archive.infolist()
            if not members or len(members) > MAX_ZIP_MEMBERS:
                raise ScoreImportError("MXL arxivida fayllar soni chegaradan katta.")
            names = set()
            total = 0
            for member in members:
                path = PurePosixPath(member.filename)
                if member.filename in names or path.is_absolute() or ".." in path.parts or "\\" in member.filename or ":" in member.filename:
                    raise ScoreImportError("MXL ichidagi fayl yo'li noto'g'ri.")
                names.add(member.filename)
                total += member.file_size
                if member.flag_bits & 1 or member.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}:
                    raise ScoreImportError("Shifrlangan yoki noodatiy siqilgan MXL qo'llab-quvvatlanmaydi.")
                if member.file_size > MAX_XML_BYTES or total > MAX_XML_BYTES * 2:
                    raise ScoreImportError("MXL ochilgandagi hajm chegaradan katta.")
            if "META-INF/container.xml" not in names:
                raise ScoreImportError("MXL META-INF/container.xml fayli topilmadi.")

            def bounded_read(name, limit):
                info = archive.getinfo(name)
                if info.file_size > limit:
                    raise ScoreImportError("MXL ichidagi XML chegaradan katta.")
                with archive.open(info) as stream:
                    content = stream.read(limit + 1)
                if len(content) > limit:
                    raise ScoreImportError("MXL ochilgandagi hajm chegaradan katta.")
                return content

            container = safe_xml(bounded_read("META-INF/container.xml", 64 * 1024))
            roots = container.findall("./rootfiles/rootfile")
            if container.tag != "container" or not roots:
                raise ScoreImportError("MXL rootfile ma'lumoti noto'g'ri.")
            # The first rootfile is the MusicXML score, per the container spec.
            target = roots[0].get("full-path", "")
            if target not in names or archive.getinfo(target).is_dir():
                raise ScoreImportError("MXL ichidagi asosiy nota topilmadi.")
            return bounded_read(target, MAX_XML_BYTES)
    except (zipfile.BadZipFile, RuntimeError, OSError, KeyError, NotImplementedError) as exc:
        raise ScoreImportError("MXL arxivi buzilgan yoki o'qib bo'lmaydi.") from exc


def text(element, path, default=""):
    result = element.findtext(path)
    return result.strip() if result is not None else default


def number(value, label, minimum=None, maximum=None):
    # MusicXML decimal values need no exponent or rational-expression parsing.
    # Bound the token before constructing Fraction (e.g. hostile huge exponents).
    if not isinstance(value, str) or len(value) > 64 or not re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)", value):
        raise ScoreImportError(f"{label} qiymati noto'g'ri.")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError, TypeError) as exc:
        raise ScoreImportError(f"{label} qiymati noto'g'ri.") from exc
    if result.denominator > 1_000_000 or result.numerator.bit_length() > 64 or (minimum is not None and result < minimum) or (maximum is not None and result > maximum):
        raise ScoreImportError(f"{label} qiymati chegaradan tashqarida.")
    return result


def integer(value, label, minimum, maximum):
    result = number(value, label, minimum, maximum)
    if result.denominator != 1:
        raise ScoreImportError(f"{label} butun son bo'lishi kerak.")
    return int(result)


def parse_time(element):
    beats = element.findall("beats")
    types = element.findall("beat-type")
    if not beats or len(beats) != len(types):
        return None
    groups = []
    for beat, beat_type in zip(beats, types):
        beat_text = (beat.text or "").strip()
        counts = [integer(item, "Takt", 1, 64) for item in beat_text.split("+")]
        denominator = integer(beat_type.text, "Takt maxraji", 1, 128)
        groups.append({"beats": beat_text, "beat_type": denominator, "count": sum(counts)})
    return {"beats": "+".join(item["beats"] for item in groups), "beat_type": groups[0]["beat_type"], "groups": groups,
            "length_quarters": float(sum((Fraction(item["count"] * 4, item["beat_type"]) for item in groups), Fraction(0)))}


def parse_tempo(element, offset):
    metronome = element.find("./direction-type/metronome")
    sound = element.find("sound") if element.tag == "direction" else element
    raw_sound = sound.get("tempo") if sound is not None else None
    beat_unit, dots, bpm, qpm = "quarter", 0, None, None
    if metronome is not None and text(metronome, "per-minute"):
        beat_unit = text(metronome, "beat-unit", "quarter")
        dots = len(metronome.findall("beat-unit-dot"))
        # Numeric metronome markings only. Text such as "ca. 80" remains in XML.
        try:
            bpm = float(number(text(metronome, "per-minute"), "Temp", 1, 1000))
        except ScoreImportError:
            bpm = None
        if bpm is not None and beat_unit in BEAT_QUARTERS and dots <= 3:
            qpm = bpm * BEAT_QUARTERS[beat_unit] * sum(.5 ** dot for dot in range(dots + 1))
    if raw_sound is not None:
        qpm = float(number(raw_sound, "Temp", 1, 1000))
    if qpm is None:
        return None
    return {"offset_quarters": float(offset), "quarter_bpm": qpm, "beat_unit": beat_unit, "beat_unit_dots": dots, "bpm": bpm if bpm is not None else qpm}


def expand_repeats(measures, warnings):
    """Expand bounded barline repeats; complex navigation is explicitly unsupported."""
    stack, regions, active_endings, ending_sets, unsupported = [], [], set(), [], False
    for measure in measures:
        i, repeat = measure["index"], measure["repeat"]
        for ending in measure["endings"]:
            if ending["type"] == "start":
                active_endings = {int(n.strip()) for n in ending["number"].split(",") if n.strip().isdigit()}
                if not active_endings:
                    warnings.add("Noodatiy volta yozuvi: takrorlashni nota bilan tekshiring.")
                    unsupported = True
        ending_sets.append(set(active_endings))
        if repeat["forward"]:
            stack.append(i)
        if repeat["backward"]:
            start = stack.pop() if stack else 0
            regions.append((start, i, repeat["times"]))
        if any(e["type"] in {"stop", "discontinue"} for e in measure["endings"]):
            active_endings = set()
    if stack:
        warnings.add("Yakunlanmagan takrorlash belgisi: yozilgan tartibda tinglang.")
        unsupported = True
    # Recursive disjoint/nested regions; identical starts would be ambiguous.
    if unsupported or len({r[0] for r in regions}) != len(regions):
        warnings.add("Murakkab takrorlash: ijro tartibi yozilgan taktlar bilan cheklangan.")
        return list(range(len(measures))), False
    by_start = {start: (end, times) for start, end, times in regions}
    result = []

    def append_range(start, end, iteration=1, omit_region=None, depth=0):
        if depth > 8:
            raise ScoreImportError("Takrorlashlar juda chuqur.")
        i, current_pass = start, iteration
        while i <= end:
            region = by_start.get(i) if i != omit_region else None
            if region and region[0] <= end:
                last, times = region
                for turn in range(1, times + 1):
                    append_range(i, last, turn, i, depth + 1)
                current_pass = times
                i = last + 1
                continue
            if not ending_sets[i] or current_pass in ending_sets[i]:
                result.append(i)
                if len(result) > MAX_PLAYBACK_MEASURES:
                    raise ScoreImportError("Takrorlangan ijro tartibi juda uzun.")
            i += 1

    append_range(0, len(measures) - 1)
    return result, True


def parse_musicxml(data):
    root = safe_xml(data)
    if root.tag != "score-partwise":
        raise ScoreImportError("Hozir score-partwise MusicXML qo'llab-quvvatlanadi. Partwise formatda eksport qiling.")
    parts = root.findall("part")
    if not parts or len(parts) > MAX_PARTS:
        raise ScoreImportError("Partlar soni noto'g'ri yoki 32 tadan ko'p.")
    names = {item.get("id"): text(item, "part-name") for item in root.findall("./part-list/score-part")}
    seen_parts, events, part_meta, measure_map, warnings = set(), [], [], {}, set()
    unsupported_playback = False
    event_count = 0
    for part in parts:
        part_id = part.get("id", "")
        if not part_id or len(part_id) > 80 or part_id in seen_parts:
            raise ScoreImportError("Part identifikatori bo'sh yoki takrorlangan.")
        seen_parts.add(part_id)
        part_measures = part.findall("measure")
        if not part_measures or len(part_measures) > MAX_MEASURES:
            raise ScoreImportError("Taktlar soni noto'g'ri yoki 2000 tadan ko'p.")
        divisions, time, key, staff_count, transpose = Fraction(1), None, None, 1, Fraction(0)
        measure_lengths = []
        for index, measure in enumerate(part_measures):
            label = measure.get("number", str(index + 1))[:80]
            record = measure_map.setdefault(index, {"index": index, "number": label, "length_quarters": 0.0, "time": None, "key": None,
                 "repeat": {"forward": False, "backward": False, "times": 2}, "endings": [], "tempos": []})
            cursor, extent, last_onset, last_was_rest = Fraction(0), Fraction(0), None, False
            for child in measure:
                if child.tag == "attributes":
                    if text(child, "divisions"):
                        divisions = number(text(child, "divisions"), "Divisions", Fraction(1, 1000), 1_000_000)
                    if child.find("time") is not None:
                        time = parse_time(child.find("time"))
                        if time is None:
                            warnings.add("Erkin metr: ijro uzunligi nota davomiyligidan olinadi.")
                    if child.find("key") is not None:
                        fifths = text(child, "key/fifths")
                        if fifths:
                            key = {"fifths": integer(fifths, "Tonallik", -7, 7), "mode": text(child, "key/mode", "unspecified")}
                        else:
                            warnings.add("Noodatiy tonallik kaliti asl notada saqlangan.")
                    if text(child, "staves"):
                        staff_count = integer(text(child, "staves"), "Staff", 1, 8)
                    if child.find("transpose") is not None:
                        tr = child.find("transpose")
                        transpose = number(text(tr, "chromatic", "0"), "Transpozitsiya", -48, 48) + integer(text(tr, "octave-change", "0"), "Oktava", -4, 4) * 12
                elif child.tag in {"backup", "forward"}:
                    duration = number(text(child, "duration"), "Davomiylik", Fraction(1, 1_000_000), 1_000_000) / divisions
                    cursor += duration * (-1 if child.tag == "backup" else 1)
                    if cursor < 0 or cursor > 256:
                        raise ScoreImportError("Backup/forward takt chegarasidan tashqarida.")
                    extent = max(extent, cursor)
                    last_onset = None
                elif child.tag == "note":
                    event_count += 1
                    if event_count > MAX_NOTES:
                        raise ScoreImportError("Notalar soni 30000 chegaradan katta.")
                    grace, chord, rest, cue = child.find("grace") is not None, child.find("chord") is not None, child.find("rest") is not None, child.find("cue") is not None
                    if sum(child.find(tag) is not None for tag in {"pitch", "rest", "unpitched"}) != 1:
                        raise ScoreImportError("Notada bitta pitch, rest yoki unpitched turi bo'lishi kerak.")
                    duration = Fraction(0) if grace else number(text(child, "duration"), "Nota davomiyligi", Fraction(1, 1_000_000), 1_000_000) / divisions
                    if duration > 256:
                        raise ScoreImportError("Nota davomiyligi juda katta.")
                    if chord and (last_onset is None or last_was_rest):
                        raise ScoreImportError("Akkord notasi oldingi nota bilan bog'lanmagan.")
                    onset = last_onset if chord else cursor
                    staff = integer(text(child, "staff", "1"), "Staff", 1, 8)
                    staff_count = max(staff_count, staff)
                    pitch = None
                    if child.find("pitch") is not None:
                        pitch_el = child.find("pitch")
                        step = text(pitch_el, "step")
                        if step not in "CDEFGAB" or len(step) != 1:
                            raise ScoreImportError("Nota balandligi noto'g'ri.")
                        octave = integer(text(pitch_el, "octave"), "Nota oktavasi", -1, 9)
                        alter = number(text(pitch_el, "alter", "0"), "Alteratsiya", -4, 4)
                        written = (octave + 1) * 12 + {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[step] + alter
                        midi = written + transpose
                        if not 0 <= midi <= 127:
                            warnings.add("MIDI diapazonidan tashqari notalar baholashga kiritilmaydi.")
                        if midi.denominator != 1:
                            warnings.add("Mikrotonlar MIDI klaviatura baholashiga mos emas.")
                        pitch = {"step": step, "alter": float(alter), "octave": octave, "written_midi": float(written), "midi": float(midi)}
                    elif not rest:
                        warnings.add("Balandligi ko'rsatilmagan notalar faqat notada ko'rsatiladi.")
                        unsupported_playback = True
                    ties = sorted({item.get("type") for item in child.findall("tie") + child.findall("./notations/tied") if item.get("type") in {"start", "stop"}})
                    events.append({"id": f"{part_id}:{index}:{event_count}", "part_id": part_id, "measure_index": index, "measure_number": label,
                        "offset_quarters": float(onset), "duration_quarters": float(duration), "duration_fraction": str(duration),
                        "pitch": pitch, "staff": staff, "voice": text(child, "voice", "1")[:80], "hand": "unknown", "rest": rest,
                        "chord": chord, "grace": grace, "cue": cue, "ties": ties})
                    if grace:
                        warnings.add("Forşlaglar notada saqlanadi; mashq audiosi asosiy notalarni ijro etadi.")
                    if not chord:
                        last_onset, last_was_rest = onset, rest
                        cursor += duration
                    extent = max(extent, onset + duration)
                elif child.tag in {"direction", "sound"}:
                    offset = cursor + number(text(child, "offset", "0"), "Temp joylashuvi", -1_000_000, 1_000_000) / divisions if child.tag == "direction" else cursor
                    if offset < 0 or offset > 256:
                        raise ScoreImportError("Temp joylashuvi takt chegarasidan tashqarida.")
                    tempo = parse_tempo(child, offset)
                    if tempo and tempo not in record["tempos"]:
                        record["tempos"].append(tempo)
                    sound = child.find("sound") if child.tag == "direction" else child
                    if sound is not None and any(sound.get(attr) for attr in {"dacapo", "dalsegno", "tocoda", "fine", "segno", "coda"}):
                        warnings.add("D.C./D.S./Coda ijro o'tishlari qo'lda tekshirilishi kerak; yozilgan tartibda mashq qiling.")
                        unsupported_playback = True
                    if child.find("./direction-type/octave-shift") is not None:
                        warnings.add("Oktava ko'chishi asl notada saqlangan; avtomatik audio tekshirilmagan.")
                        unsupported_playback = True
                elif child.tag == "barline":
                    repeat_el = child.find("repeat")
                    if repeat_el is not None:
                        direction = repeat_el.get("direction")
                        if direction not in {"forward", "backward"}:
                            raise ScoreImportError("Takrorlash yo'nalishi noto'g'ri.")
                        record["repeat"][direction] = True
                        if direction == "backward":
                            record["repeat"]["times"] = integer(repeat_el.get("times", "2"), "Takrorlash soni", 2, 8)
                    for ending in child.findall("ending"):
                        value = {"number": ending.get("number", "")[:80], "type": ending.get("type", "")}
                        if value not in record["endings"]:
                            record["endings"].append(value)
            if extent > 256:
                raise ScoreImportError("Takt davomiyligi 256 chorakdan katta.")
            length = extent
            if time and measure.get("implicit") != "yes":
                length = max(length, Fraction(str(time["length_quarters"])))
            record["length_quarters"] = max(record["length_quarters"], float(length))
            if record["time"] is None:
                record["time"] = time
            if record["key"] is None:
                record["key"] = key
            measure_lengths.append(float(length))
        part_meta.append({"id": part_id, "name": names.get(part_id, part_id)[:240], "staff_count": staff_count, "measure_count": len(part_measures)})
        # Staff describes notation layout, not guaranteed fingering or hand allocation.
        for event in events:
            if event["part_id"] == part_id and staff_count >= 2:
                event["hand"] = "right" if event["staff"] == 1 else "left" if event["staff"] == 2 else "unknown"
    if not events:
        raise ScoreImportError("Faylda nota yoki pauza topilmadi.")
    measures = [measure_map[i] for i in sorted(measure_map)]
    onset = 0.0
    for measure in measures:
        measure["start_quarters"] = onset
        onset += measure["length_quarters"]
    for event in events:
        event["onset_quarters"] = measures[event["measure_index"]]["start_quarters"] + event["offset_quarters"]
    if len({p["measure_count"] for p in part_meta}) > 1:
        warnings.add("Partlarda taktlar soni farq qiladi; joylashuvni asl nota bilan tekshiring.")
        unsupported_playback = True
    order, repeats_supported = expand_repeats(measures, warnings)
    tempos = [tempo for measure in measures for tempo in measure["tempos"]]
    tempo = tempos[0] if tempos else None
    if not tempo:
        warnings.add("Manbada raqamli temp yo'q; mashq tempini o'zingiz tanlang.")
    metadata = {"title": text(root, "work/work-title") or text(root, "movement-title") or "Yuklangan nota",
        "composer": next((item.text.strip() for item in root.findall("./identification/creator") if item.get("type") == "composer" and item.text), ""),
        "part_count": len(parts), "measure_count": len(measures), "event_count": len(events), "key": measures[0]["key"],
        "time": measures[0]["time"], "tempo": tempo, "duration_quarters": onset}
    return {"schema_version": 1, "metadata": metadata, "parts": part_meta, "events": events, "measures": measures,
        "playback_order": order, "warnings": sorted(warnings),
        "capabilities": {"notation_source": "original_musicxml", "timed_notes": not unsupported_playback, "repeats_expanded": repeats_supported,
                         "automatic_fingering": False, "hand_assignment": "staff_hint_editable", "expressive_audio": False}}
