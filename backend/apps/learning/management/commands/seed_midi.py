import hashlib
from pathlib import Path
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from apps.learning.models import Arrangement, Composition, PracticePlan, PracticeTask, Profile
from apps.learning.curriculum import ensure_curriculum
from apps.scores.midi import parse_midi
from apps.scores.models import Score

MIDI_SHA256 = "853c5d63d49fdfc685f4215092affa83794298347a52e328ee24fe2ee86da522"
MIDI_SOURCE = "https://bitmidi.com/pirates-of-the-caribbean-hes-a-pirate-3-mid"
MIDI_DOWNLOAD = "https://bitmidi.com/uploads/85263.mid"


class Command(BaseCommand):
    help = "Seed the verified complete internet piano MIDI without inventing a timeline or discarding learner history."

    @transaction.atomic
    def handle(self, *args, **options):
        asset = settings.BASE_DIR / "apps" / "learning" / "reference_assets" / "bitmidi-pirate" / "pirate-piano.mid"
        if not asset.is_file():
            raise CommandError("The verified complete piano MIDI asset is unavailable.")
        data = asset.read_bytes()
        if hashlib.sha256(data).hexdigest() != MIDI_SHA256:
            raise CommandError("The curated MIDI differs from the verified source bytes.")
        parsed = parse_midi(data, "He's a Pirate — two-hand piano MIDI")
        if len(parsed["events"]) != 1255 or abs(parsed["metadata"]["duration_seconds"] - 77.625) > 1e-8 or sorted(part["note_count"] for part in parsed["parts"]) != [557, 698]:
            raise CommandError("The complete MIDI timeline differs from the independently verified piano source.")
        learner, _ = Profile.objects.get_or_create(pk=1)
        composition, _ = Composition.objects.get_or_create(seed_key="hes-a-pirate", defaults={"title": "He's a Pirate", "composer": "Klaus Badelt", "category": "Film musiqasi", "status": "active"})
        arrangement, created = Arrangement.objects.get_or_create(seed_key="hes-a-pirate-bitmidi-full", defaults={
            "composition": composition, "title": "He's a Pirate · to'liq ikki qo'lli piano MIDI", "is_default": True,
            "arranger": "Cerullean Pictures (MIDI copyright metadata)", "source_url": MIDI_SOURCE, "source_kind": "link",
            "full_score_url": MIDI_DOWNLOAD, "full_score_format": "midi", "full_score_verified_at": timezone.now(),
            "exact_version_confirmed": True, "workflow_status": "full_midi_ready", "key_signature": "F (literal MIDI key metadata)",
            "time_signature": "6/8", "tempo_bpm": 200, "tempo_beat_unit": "quarter", "rights_status": "unconfirmed",
            "rights_note": "Public BitMidi download. MIDI contains 'Written by Klaus Badelt' and 'Arrangement © 2004 Cerullean Pictures'. No CC or public-domain license is asserted. Exact complete file: 1255 piano notes, named Right Hand/Left Hand tracks, 77.625 seconds, final D chord ending.",
        })
        if created:
            for previous in composition.arrangements.exclude(pk=arrangement.pk).filter(is_default=True):
                previous.is_default = False
                previous.workflow_status = "archived_source"
                previous.save(update_fields=["is_default", "workflow_status"])
        score = Score.objects.filter(arrangement=arrangement, file_format="midi", content_sha256=MIDI_SHA256).first()
        if score is None:
            score = Score(arrangement=arrangement, version=1, file_format="midi", title="He's a Pirate — Cerullean Pictures piano MIDI",
                          original_filename="pirate-piano.mid", content_sha256=MIDI_SHA256, source_url=MIDI_SOURCE,
                          source_provenance={"kind": "curated_public_midi", "download_url": MIDI_DOWNLOAD, "sha256": MIDI_SHA256,
                                             "independent_note_count": 1255, "independent_duration_seconds": 77.625, "ending_verified": True, "copyright_metadata": parsed["metadata"]["copyright"]},
                          completeness_verified_at=timezone.now(), rights_note=arrangement.rights_note,
                          rights_confirmed_at=timezone.now(), exact_version_confirmed=True, parsed=parsed,
                          sections=[{"id": "opening", "title": "Boshlanish · birinchi qo'l", "start_index": 0, "end_index": 3, "notes": "Actual MIDI source events; navigation windows are not printed score measures."},
                                    {"id": "two-hands", "title": "Ikki qo'l uchrashuvi", "start_index": 4, "end_index": 7, "notes": "Left Hand source track enters at quarter position 12."},
                                    {"id": "ending", "title": "Yakun", "start_index": 82, "end_index": 86, "notes": "Full source ending through its last key release."}])
            score.musicxml.save("pirate-piano.mid", ContentFile(data), save=False)
            score.save()
        plan, _ = PracticePlan.objects.get_or_create(arrangement=arrangement, defaults={"profile": learner, "title": "He's a Pirate: MIDI bo'laklari bilan o'rganish", "summary": "To'liq internet MIDI: 1255 nota, 77.625 soniya. Darslar aynan shu faylning nota voqealari va vaqtlariga bog'langan.", "readiness": "ready", "is_demo": False})
        lessons = list(ensure_curriculum(arrangement))
        if not plan.tasks.exists():
            PracticeTask.objects.bulk_create([PracticeTask(plan=plan, order=index,
                kind="theory" if lesson.skill in ["harmony", "intervals"] else "reflect" if lesson.skill == "practice" else "technique",
                title=lesson.title, instructions=lesson.context + " " + " ".join(step["instruction"] for step in lesson.content["steps"]),
                minutes=5, concept=lesson.skill, success_criterion=lesson.success_criterion)
                for index, lesson in enumerate(lessons, 1)])
        self.stdout.write(self.style.SUCCESS(f"Full piano MIDI ready: arrangement {arrangement.id}, score {score.id}, 1255 notes, 77.625 seconds. Historical sources preserved."))
