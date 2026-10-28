"""Versioned user-supplied exports. Hand roles are authored, not fingerings.

The six (1) exports replace pedal-extended key holds with the user's note releases.
All 4,460 pitches, attack times and velocities match the previous exports.
"""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import hashlib

from apps.scores.midi import parse_midi
from .midi_authoring import SOURCE_SHA256, source_data
from .curated_repertoire import active_entries, edition_source
from .ivory_repertoire import GROUPS as IVORY_GROUPS, GROUP_BY_CODE as IVORY_BY_CODE, performance_source


@dataclass(frozen=True)
class Source:
    code: str
    title: str
    filename: str
    sha256: str
    slug: str
    composer: str = ""
    collection: str = "Winter Sonata"
    course_kind: str = "standard"

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
    Source("youth", "What Is a Youth", "What Is A Youth - Nino Rota - OST R&J 1968 (Piano Cover) (1).mid", "816534970835b9b0d0d7543f0ba97c1fb68e7edd1583d5cf0bd40b082ae2cd00", "what-is-a-youth", "Nino Rota", "Romeo & Juliet · 1968"),
    Source("star", "Winter Sonata — Star", "Winter Sonata Classics -  (Star) (1).mid", "12f3da5ccdb9ed4d0e4c80934a51d72f2fffdf7fd93cd94bff24c07b1b33ffd4", "winter-sonata-star"),
    Source("tears", "Winter Sonata — Tears in Your Eyes", "Winter Sonata Classics - Tears In Your Eyes (1).mid", "26c9b8d40d93af50a75684824d47e33067fa6daa237f97d9b7a0bf3d80662570", "winter-sonata-tears-in-your-eyes"),
    Source("my-memory", "Winter Sonata — My Memory", "Winter Sonata Classics - My Memory (Piano Version) (1).mid", "fa9282b92aa5c69ec9499a7a983d701382ce86bbc7f7b653c707d609257fa835", "winter-sonata-my-memory"),
    Source("premonition", "Winter Sonata — Premonition", "Winter Sonata Classics -  (Premonition) (1).mid", "fca75f473fdb6b0ff2cf15ecba81b26705fc8ff03370c9382d495d796c9bacee", "winter-sonata-premonition"),
    Source("memories", "Memories", "Memories (1).mid", "b61395b473e13d2ebf2a9070e8829e6d3aa7fba72b7d10b46ae994e1a2e672b7", "memories", collection=""),
    Source("all-in", "All in — Soundtrack", "All_In_Plus5_Full.mid", "13d5ad3db51d778d3268fddf7aebefcefded493aa2edafb6e0448ea84d0cecb8", "all-in-soundtrack", collection="All in / Va-bank", course_kind="package"),
)
SOURCES += tuple(Source(entry["code"], entry["title"], entry["code"] + ".mid", entry["sha256"],
                        entry["slug"], entry["composer"], entry["collection"], "curated")
                 for entry in active_entries())
_existing_codes = {source.code for source in SOURCES}


def ivory_source(group):
    variant = group["variants"][0]
    return Source(group["code"], group["title"], variant["filename"], variant["sha256"],
                  group["slug"], group.get("composer", ""), group.get("collection", ""), "ivory")


# Replacing an edition keeps its stable composition code, slug and database key.
SOURCES = tuple(ivory_source(IVORY_BY_CODE[source.code])
                if source.code in IVORY_BY_CODE and not IVORY_BY_CODE[source.code].get("base_variant")
                else source for source in SOURCES)
SOURCES += tuple(ivory_source(group) for group in IVORY_GROUPS if group["code"] not in _existing_codes)
SOURCE_BY_CODE = {source.code: source for source in SOURCES}


@lru_cache(maxsize=40)
def repertoire_source(code):
    if code in IVORY_BY_CODE and not IVORY_BY_CODE[code].get("base_variant"):
        return performance_source(code)
    if code == "still":
        return source_data()
    if code == "all-in":
        from .all_in_package import package_source
        return package_source("All_In_Plus5_Full.mid")
    source = SOURCE_BY_CODE[code]
    if source.course_kind == "curated":
        return edition_source(code)
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
