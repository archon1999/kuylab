"""Reviewed source registry. Original files are immutable; hand roles are authored."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import hashlib

from apps.scores.midi import parse_midi
from .midi_authoring import SOURCE_SHA256, source_data


@dataclass(frozen=True)
class Source:
    code: str
    title: str
    filename: str
    sha256: str
    slug: str
    composer: str = ""
    collection: str = "Winter Sonata"

    @property
    def composition_key(self):
        return "studio-winter-sonata-still" if self.code == "still" else "studio-" + self.slug

    @property
    def arrangement_key(self):
        return f"studio-{self.code}-original"

    @property
    def asset_key(self):
        return f"composition:{self.code}:original"


SOURCES = (
    Source("still", "Winter Sonata — Still", "Winter Sonata Classics - Still.mid", SOURCE_SHA256, "winter-sonata-still"),
    Source("youth", "What Is a Youth", "What Is A Youth - Nino Rota - OST R&J 1968 (Piano Cover).mid", "b84c06c831ff7ec243fa52cd26db14621be1e67a50c75bd33545289c8279bdf9", "what-is-a-youth", "Nino Rota", "Romeo & Juliet · 1968"),
    Source("star", "Winter Sonata — Star", "Winter Sonata Classics -  (Star).mid", "50f86da8673d4ceab53e1ae615d7dbb81bc6357d5256b206802b448f9850f91a", "winter-sonata-star"),
    Source("tears", "Winter Sonata — Tears in Your Eyes", "Winter Sonata Classics - Tears In Your Eyes.mid", "88c8e868dda9aacda5394a77485bab247f575d267b9c588975d6339ffe32e671", "winter-sonata-tears-in-your-eyes"),
    Source("my-memory", "Winter Sonata — My Memory", "Winter Sonata Classics - My Memory (Piano Version).mid", "43672ee0d84f112105ac13fb6d6351663548ad83bde869541ffbe40fb35e10bf", "winter-sonata-my-memory"),
    Source("premonition", "Winter Sonata — Premonition", "Winter Sonata Classics -  (Premonition).mid", "bb9eadf09eba71b169124be8e95e90deadd2355266ad0c2d4716e093b1a4ed4c", "winter-sonata-premonition"),
    Source("memories", "Memories", "Memories.mid", "191363d0b4ec805e5d5be6d683ec4e6855f4350ece060be704db2f364cf79aa1", "memories", collection=""),
)
SOURCE_BY_CODE = {source.code: source for source in SOURCES}


@lru_cache(maxsize=7)
def repertoire_source(code):
    if code == "still":
        return source_data()
    source = SOURCE_BY_CODE[code]
    content = (Path(__file__).with_name("assets") / f"{code}.mid").read_bytes()
    if hashlib.sha256(content).hexdigest() != source.sha256:
        raise ValueError(f"{source.code}: source changed; review and version its curriculum first.")
    parsed = parse_midi(content, source.title)
    # Each supplied export has two unnamed layers. Upper/lower ranges and
    # source-event review support these roles; they are not literal hand labels.
    if {event["track_index"] for event in parsed["events"]} != {0, 1}:
        raise ValueError(f"{code}: source layers changed.")
    for event in parsed["events"]:
        event["hand"] = "right" if event["track_index"] == 0 else "left"
        event["hand_evidence"] = "curated_track_role_inference"
    for part in parsed["parts"]:
        part["hand"] = "right" if part["index"] == 0 else "left"
        part["hand_evidence"] = "curated_track_role_inference"
    parsed["capabilities"]["hand_assignment"] = "curated_track_role_inference"
    return content, parsed
