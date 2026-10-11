from pathlib import Path
from django.conf import settings


def verified_pdf_path(arrangement):
    if not arrangement.full_score_verified_at or arrangement.full_score_format != "pdf" or not arrangement.full_score_file:
        return None
    root = Path(settings.MEDIA_ROOT).resolve()
    candidate = (root / arrangement.full_score_file.name).resolve()
    if not candidate.is_relative_to(root) or candidate.suffix.lower() != ".pdf" or not candidate.is_file():
        return None
    return candidate


def verified_page_paths(arrangement):
    pdf = verified_pdf_path(arrangement)
    if pdf is None or not arrangement.page_count or arrangement.page_count > 200:
        return []
    candidates = [pdf.with_name(f"{pdf.stem}-page-{page}.png") for page in range(1, arrangement.page_count + 1)]
    return candidates if all(candidate.is_file() and candidate.parent == pdf.parent for candidate in candidates) else []
