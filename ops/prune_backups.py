"""Bound only KuyLab's timestamp-named local backups after a successful backup."""
import re
import shutil
from pathlib import Path

root = Path("/opt/kuylab/backups").resolve(strict=True)
for directories, limit in [(True, 7), (False, 10)]:
    candidates = sorted((p for p in root.iterdir()
                         if not p.is_symlink() and p.is_dir() == directories
                         and re.fullmatch(r"\d{8}T\d{6}Z" + ("" if directories else r"\.dump"), p.name)), reverse=True)
    for path in candidates[limit:]:
        if path.resolve().parent != root:
            raise RuntimeError("Backup path escaped its directory")
        if directories:
            shutil.rmtree(path)
        else:
            path.unlink()
