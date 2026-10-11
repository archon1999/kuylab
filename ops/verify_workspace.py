"""Read-only integrity check for the local KuyLab database and MIDI library."""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
SOURCE_SHA256 = "f0713b1de241c28522911a907a4464504ce7fbcaa8340ad9e1589881c2f3e7c8"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, help="Compare media files with a saved migration manifest.")
    args = parser.parse_args()
    database = BACKEND / "db.sqlite3"
    source = BACKEND / "apps/studio/assets/still.mid"
    if not database.is_file() or sha256(source) != SOURCE_SHA256:
        raise SystemExit("Missing database or changed original Still MIDI.")
    connection = sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise SystemExit(f"SQLite integrity check failed: {integrity}")
        assets = connection.execute("SELECT key, score_id FROM studio_studioasset").fetchall()
        missing = [name for (name,) in connection.execute("SELECT musicxml FROM scores_score")
                   if not (BACKEND / "media" / name).is_file()]
        if missing:
            raise SystemExit(f"Missing score files: {missing}")
        original = dict(assets).get("composition:still:original")
        if original is None:
            raise SystemExit("The original Still score is missing from the catalog.")
        print(f"SQLite OK; {len(assets)} catalog assets; original Still score ID {original}.")
    finally:
        connection.close()
    if args.manifest:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        media = {name: expected for name, expected in manifest.items() if name.startswith("media")}
        for name, expected in media.items():
            path = (BACKEND / name).resolve()
            if not path.is_relative_to(BACKEND / "media") or sha256(path) != expected:
                raise SystemExit(f"Media file changed: {name}")
        print(f"All {len(media)} pre-migration media hashes match.")
    print("Original Still source checksum matches.")


if __name__ == "__main__":
    main()
