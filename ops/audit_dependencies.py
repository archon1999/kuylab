"""Export all pinned Poetry packages for pip-audit without changing the lock."""
import sys
import tomllib
from pathlib import Path

lock = tomllib.loads((Path(__file__).resolve().parents[1] / "backend/poetry.lock").read_text())
Path(sys.argv[1]).write_text("\n".join(f"{p['name']}=={p['version']}" for p in lock["package"]) + "\n")
