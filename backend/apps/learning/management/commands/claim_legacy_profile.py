"""Explicit local administrator action; registration never claims another profile."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.learning.models import Profile


class Command(BaseCommand):
    help = "Assign the preserved legacy learner profile to an existing registered account."

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("--profile", type=int, default=1)

    @transaction.atomic
    def handle(self, *args, **options):
        user = get_user_model().objects.filter(username=options["username"]).first()
        old = Profile.objects.select_for_update().filter(pk=options["profile"], user__isnull=True).first()
        if not user or not old:
            raise CommandError("Existing account and an unclaimed legacy profile are required.")
        current = Profile.objects.filter(user=user).first()
        # Preserve both profiles. Reassign all related personal records, rejecting conflicts.
        if current:
            for relation in Profile._meta.related_objects:
                model, field = relation.related_model, relation.field.name
                if model.objects.filter(**{field: current}).exists():
                    raise CommandError("The account already has personal activity. Merge explicitly before claiming; no data was changed.")
            current.user = None
            current.save(update_fields=["user"])
        old.user = user
        old.save(update_fields=["user"])
        self.stdout.write(self.style.SUCCESS("Legacy profile assigned; all original records preserved."))
