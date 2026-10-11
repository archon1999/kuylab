import hashlib
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from apps.learning.models import Arrangement, Composition, PracticePlan, PracticeTask, Profile
from apps.learning.plans import create_draft_plan
from apps.learning.curriculum import ensure_curriculum

FULL_SOURCE_URL = "https://unpianiste.com/wp-content/uploads/partitions/He%27s_a_pirate_%282cles%29.pdf"
FULL_SOURCE_SHA256 = "4b4188a69af132186b8afbcd5f372b9dde6b3032cd360e43fab4641bbde97067"
FULL_SOURCE_FILE = "reference/unpianiste-hes-a-pirate.pdf"


def ensure_full_file():
    destination = Path(settings.MEDIA_ROOT) / FULL_SOURCE_FILE
    if destination.exists():
        data = destination.read_bytes()
    else:
        baseline = settings.BASE_DIR / "apps" / "learning" / "reference_assets" / "unpianiste-pirate" / destination.name
        if baseline.exists():
            data = baseline.read_bytes()
        else:
            raise CommandError("Bundled, verified full piano score is missing.")
        if hashlib.sha256(data).hexdigest() != FULL_SOURCE_SHA256:
            raise CommandError("Full score content changed; verify all pages before replacing the source.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    if hashlib.sha256(data).hexdigest() != FULL_SOURCE_SHA256:
        raise CommandError("Full score checksum differs from the visually verified four-page edition.")
    for page in range(1, 5):
        name = f"unpianiste-hes-a-pirate-page-{page}.png"
        bundled = settings.BASE_DIR / "apps" / "learning" / "reference_assets" / "unpianiste-pirate" / name
        if not bundled.exists():
            raise CommandError("A verified full score page image is missing.")
        image = destination.with_name(name)
        image_data = bundled.read_bytes()
        if image.exists() and hashlib.sha256(image.read_bytes()).digest() != hashlib.sha256(image_data).digest():
            raise CommandError("An existing curated page differs from the verified bundled render.")
        if not image.exists():
            image.write_bytes(image_data)
    return FULL_SOURCE_FILE


class Command(BaseCommand):
    help = "Seed a complete, verified piano score and authored lessons; preserve existing learner history."

    @transaction.atomic
    def handle(self, *args, **options):
        full_file = ensure_full_file()
        profile, _ = Profile.objects.get_or_create(pk=1)
        if profile.instrument_model == "Yamaha — model hali kiritilmagan":
            profile.instrument_model = "Yamaha YDP-145"
            profile.save(update_fields=["instrument_model"])
        composition = Composition.objects.filter(seed_key="hes-a-pirate").first() or Composition.objects.filter(title="He's a Pirate", seed_key__isnull=True).order_by("id").first()
        if composition is None:
            composition = Composition.objects.create(title="He's a Pirate", seed_key="hes-a-pirate",
                composer="Klaus Badelt, Hans Zimmer, Geoff Zanelli", category="Film musiqasi", status="active", color="#D09B65",
                goal="Tanlagan to'liq aranjirovkamni ravon chalish va nazariyasini tushunish")
        elif composition.seed_key is None:
            composition.seed_key = "hes-a-pirate"
            composition.save(update_fields=["seed_key"])
        arrangement, created = Arrangement.objects.get_or_create(seed_key="hes-a-pirate-unpianiste-full", defaults={
            "composition": composition, "is_default": True, "title": "He's a Pirate — Alexis Quoniam · to'liq ikki kalitli nota",
            "arranger": "Alexis Quoniam / Unpianiste", "source_url": "https://unpianiste.com/partitions-piano",
            "reference_video_url": "https://www.youtube.com/watch?v=nvYwpFb2oA4", "source_kind": "licensed",
            "full_score_url": FULL_SOURCE_URL, "full_score_format": "pdf", "full_score_file": full_file,
            "full_score_verified_at": timezone.now(), "exact_version_confirmed": True, "workflow_status": "full_score_ready",
            "key_signature": "D minor", "time_signature": "6/8", "tempo_bpm": None, "tempo_beat_unit": "", "page_count": 4,
            "rights_status": "licensed", "rights_note": "Alexis Quoniam / Unpianiste: CC BY-NC-SA 3.0 France (https://unpianiste.com/informations-legales). To'liq 4 sahifa, 1–103 takt va yakuniy Dm/final chiziq vizual tekshirildi. Manbada temp yozilmagan. Fayl shaxsiy mahalliy mashg'ulot uchun; muallif va manba ko'rsatiladi.",
        })
        if created:
            for previous in composition.arrangements.exclude(pk=arrangement.pk):
                if "MN0224234" in previous.source_url:
                    previous.is_default = False
                    previous.workflow_status = "archived_source"
                    previous.save(update_fields=["is_default", "workflow_status"])
            plan = PracticePlan.objects.create(arrangement=arrangement, profile=profile,
                title="He's a Pirate: to'liq nota bilan o'rganish", readiness="ready", is_demo=False,
                summary="Alexis Quoniamning 4 sahifali, 103 taktli to'liq pianino aranjirovkasi. D minor, 6/8; manbada temp belgisi yo'q. PDFdagi aniq joylarga nazariya va original tayyorlov bog'lanadi.")
            tasks = [
                ("listen", "To'liq nota va ijro", "To'rt sahifali notani oching. Birinchi va oxirgi sahifani ko'ring; 1–103 taktlar to'liq mavjud. Manba ijrosini tinglang.", 4, "Forma", "To'liq nota va tanlangan aranjirovka bilan tanishdim."),
                ("theory", "6/8 ichida ikki katta urish", "1-sahifa, 18–23 taktlarda ikki katta urishni sanang. Avval original 6/8 tayyorlovini chaling, keyin PDFga qayting.", 6, "6/8", "Ikki katta urish va uchlik ichki bo'linma saqlandi."),
                ("technique", "Chap qo'lning sakkizliklari", "3-sahifa, 72–83 taktlardagi uzluksiz chap qo'l sakkizliklarini kichik guruhda, qulay tempda tekshiring. Avval notadan o'qing, so'ng ikki qo'lni birlashtiring.", 7, "Koordinatsiya", "Tanlangan kichik guruh uch urinishda qulay chalinadi."),
                ("piece", "Garmoniya va yakun", "2-sahifa, 38–39 taktlardagi A akkordi/C♯ va 40-taktdagi Dm ga qaytishni tinglang. Keyin 4-sahifa, 97–103 taktlardagi yakunni qulay tempda ulang.", 10, "D minor va ifoda", "Tanlagan o'tishimni to'xtamasdan chaldim."),
                ("reflect", "Keyingi urinish", "Bitta qiyin joy, qulay temp birligi va uchta urinish natijasini yozing. Keyingi kuni shu joyni avval bir marta sinang.", 3, "Qayta tekshirish", "Aniq keyingi maqsad saqlandi."),
            ]
            PracticeTask.objects.bulk_create([PracticeTask(plan=plan, order=index, kind=kind, title=title,
                instructions=instructions, minutes=minutes, concept=concept, success_criterion=criterion)
                for index, (kind, title, instructions, minutes, concept, criterion) in enumerate(tasks, 1)])
        ensure_curriculum(arrangement)
        if not created:
            arrangement.plan.tasks.filter(kind="piece", title="Garmoniya va yakun", instructions__startswith="2-sahifa, 38–39").update(
                instructions="2-sahifa, 38–39 taktlardagi A akkordi/C♯ va 40-taktdagi Dm ga qaytishni tinglang. Keyin 4-sahifa, 97–103 taktlardagi yakunni qulay tempda ulang.")
        wishlist = [("sound-of-silence", "The Sound of Silence", "Simon & Garfunkel", "Qo'shiq"),
                    ("all-in-ost", "All In OST — trek tanlanmagan", "", "OST to'plami"),
                    ("winter-sonata-ost", "Winter Sonata OST — trek tanlanmagan", "", "OST to'plami"),
                    ("what-is-a-youth", "What Is a Youth", "Nino Rota", "Film musiqasi"),
                    ("naruto-ost", "Naruto OST — trek tanlanmagan", "", "OST to'plami")]
        for seed_key, title, composer, category in wishlist:
            item = Composition.objects.filter(seed_key=seed_key).first() or Composition.objects.filter(title=title, seed_key__isnull=True).order_by("id").first()
            if item is None:
                item = Composition.objects.create(title=title, composer=composer, category=category, seed_key=seed_key)
            if item.seed_key is None:
                item.seed_key = seed_key
                item.save(update_fields=["seed_key"])
            if not item.arrangements.exists():
                create_draft_plan(item, profile)
            ensure_curriculum(item.arrangements.first())
        self.stdout.write(self.style.SUCCESS("To'liq 4 sahifali nota va kompozitsiya darslari tayyor; mavjud mashq tarixi saqlandi."))
