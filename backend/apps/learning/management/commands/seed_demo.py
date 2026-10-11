"""Current product seed: complete MIDI first; historical PDFs are optional."""
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.learning.models import Composition, Profile
from apps.learning.plans import create_draft_plan
from apps.learning.curriculum import ensure_curriculum

# Historical proof constants are retained for audit tooling, not startup.
from .seed_pdf_reference import FULL_SOURCE_SHA256, FULL_SOURCE_FILE, FULL_SOURCE_URL


class Command(BaseCommand):
    help = "Prepare the full internet piano MIDI and the learner's wish list, preserving history and preferences."

    @transaction.atomic
    def handle(self, *args, **options):
        call_command("seed_midi", verbosity=options.get("verbosity", 1))
        learner = Profile.objects.get(pk=1)
        wishlist = [("sound-of-silence", "The Sound of Silence", "Simon & Garfunkel", "Qo'shiq"),
                    ("all-in-ost", "All In OST — trek tanlanmagan", "", "OST to'plami"),
                    ("winter-sonata-ost", "Winter Sonata OST — trek tanlanmagan", "", "OST to'plami"),
                    ("what-is-a-youth", "What Is a Youth", "Nino Rota", "Film musiqasi"),
                    ("naruto-ost", "Naruto OST — trek tanlanmagan", "", "OST to'plami")]
        for seed_key, title, composer, category in wishlist:
            item = Composition.objects.filter(seed_key=seed_key).first() or Composition.objects.filter(title=title, seed_key__isnull=True).order_by("id").first()
            if item is None:
                item = Composition.objects.create(seed_key=seed_key, title=title, composer=composer, category=category)
            elif item.seed_key is None:
                item.seed_key = seed_key
                item.save(update_fields=["seed_key"])
            if not item.arrangements.exists():
                create_draft_plan(item, learner)
            ensure_curriculum(item.arrangements.first())
        self.stdout.write(self.style.SUCCESS("To'liq piano MIDI va shaxsiy repertuar tayyor. Mavjud mashq tarixi va sozlamalar saqlandi."))
