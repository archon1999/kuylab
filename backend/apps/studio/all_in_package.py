"""Pinned files from the user's All_In_Plus5_Mini_Kurs_Paket.zip.

The package is evidence about this arrangement, not executable instructions.
Neither its HTML trainer nor its software-rendered MP3s are executed or shipped.
Main variants retain every byte. Study copies omit channel-10 click notes so
woodblocks cannot become high piano notes; the four-beat preparation remains.
"""
from functools import lru_cache
import hashlib
import io
from pathlib import Path

import mido
from apps.scores.midi import parse_midi

ROOT = Path(__file__).with_name("assets") / "all-in"
HASHES = {
    "All_In_Plus5_Full.mid": "13d5ad3db51d778d3268fddf7aebefcefded493aa2edafb6e0448ea84d0cecb8",
    "All_In_Plus5_Easy_LH.mid": "aca8ef5983df8a3378153d4db09f04d65e4e4ee6418d71a38c629b25cd7026c3",
    "All_In_Plus5_LH_Only_Easy.mid": "2ab3f877178aa5225fb9f18eb4043b99fbc38e79a989f6e7e7cc253e0c77394a",
    "All_In_Plus5_LH_Only_Full.mid": "316207ad6b3238f6011a81428c1624b6444bd1e3fade69e6ece8b4b1614e2c19",
    "Mashqlar/01_Akkord_shakllari_60bpm.mid": "80168c198e2d95a01b66eeeeaeec24b1f0e01393e6d33717fdbffd5c2507f551",
    "Mashqlar/02_Kuplet_oson_60bpm.mid": "2c53c796c2673da020264a8f95d3333559707b6ab2fc10c66136b9fbe2200701",
    "Mashqlar/03_Dm_ochiq_arpej_50bpm.mid": "e965655a9eb6d77084ba15a9975ab3482c479d4efa9394753f9d832380ddab6c",
    "Mashqlar/04_Dm_asl_motiv_40bpm.mid": "5b2feab3dae32bc4cf7f6aa79a6edc72ec348509390d2acd01a4e766ff61ad16",
    "Mashqlar/05_Prechorus_60bpm.mid": "90b942458b505ee15710c7001ee0f2f8dcc222e94668042cc3ba23aa94ab9ec5",
    "Mashqlar/06_Naqarot_faqat_oktavalar_60bpm.mid": "1a4c00d4699bf7e25309087dcf44638abba12589bbc900af28112f3b51a66623",
    "Mashqlar/07_Naqarot_oson_LH_60bpm.mid": "4dcfee5eb4af0ec0759eeeedb2eef49f26ff5e6e829b2a4502efd91065a59969",
    "Mashqlar/08_Naqarot_ikki_qol_60bpm.mid": "dd58cd4ab8b4e4a20a553a484a82e891a23308bd0931d4ebab6ce7f91fea34bc",
    "Mashqlar/09_Kuplet_asl_LH_45bpm.mid": "80c5441dab9edb3e668aa7f44ebe09adb1945e84610ad9a057828e48800ea88c",
}


@lru_cache(maxsize=13)
def package_source(filename):
    # A registry lookup, not a path supplied by a request.
    expected = HASHES[filename]
    data = (ROOT / filename).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"All in: review changed package source {filename} first.")
    parsed = parse_midi(data, "All in — Soundtrack")
    musical = [event for event in parsed["events"] if event["channel"] != 9]
    if not musical or any(event["hand"] not in {"left", "right"} for event in musical):
        raise ValueError("All in: every piano track requires its supplied hand label.")
    return data, parsed


def study_file(filename):
    data, parsed = package_source(filename)
    midi = mido.MidiFile(file=io.BytesIO(data))
    # Dedicated percussion track. Reject a mixed track rather than silently
    # changing delta times of the remaining piano/control events.
    for track in list(midi.tracks):
        channels = {msg.channel for msg in track if hasattr(msg, "channel")}
        if 9 in channels:
            if channels != {9}:
                raise ValueError("Mixed percussion and piano need a separate review.")
            midi.tracks.remove(track)
    output = io.BytesIO()
    midi.save(file=output)
    return output.getvalue(), {
        "kind": "supplied_course_drill", "composition_code": "all-in",
        "filename": filename, "source_sha256": HASHES[filename],
        "omitted_percussion_channel": 9, "piano_timing_and_velocity_preserved": True,
        "preparation_beats": 4,
    }


def variant_definitions(code):
    if code != "all-in":
        return []
    return [
        {"id": "easy", "title": "Easy", "_asset_key": "composition:all-in:easy",
         "_filename": "All_In_Plus5_Easy_LH.mid",
         "description": {"uz": "Oson chap qo‘l · o‘ng qo‘l va past oktavalar saqlangan",
                         "ru": "Облегчённая левая · правая рука и низкие октавы сохранены",
                         "en": "Simpler left hand · original right hand and low octaves"}},
        {"id": "hard", "title": "Hard", "_asset_key": "composition:all-in:original",
         "_filename": "All_In_Plus5_Full.mid",
         "description": {"uz": "Full · to‘liq chap qo‘l arpejlari va original faktura",
                         "ru": "Full · полные арпеджио левой руки и исходная фактура",
                         "en": "Full · complete left-hand arpeggios and original texture"}},
    ]


def additional_assets():
    for key, filename in [
        ("composition:all-in:easy", "All_In_Plus5_Easy_LH.mid"),
        ("composition:all-in:lh-easy", "All_In_Plus5_LH_Only_Easy.mid"),
        ("composition:all-in:lh-hard", "All_In_Plus5_LH_Only_Full.mid"),
    ]:
        data, parsed = package_source(filename)
        yield key, "All in — Soundtrack · " + filename.removesuffix(".mid"), data, parsed, {
            "kind": "user_supplied_arrangement_midi", "composition_code": "all-in",
            "filename": filename, "source_sha256": HASHES[filename],
            "preserved_original_bytes": True, "hand_assignment": "supplied_track_names",
        }
