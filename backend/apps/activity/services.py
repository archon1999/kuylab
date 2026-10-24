from django.db import transaction

from apps.learning.models import Profile
from .models import PersonalLibrary, SiteVisit


def learner_profile(user):
    from apps.learning.accounts import user_profile
    return user_profile(user)


def personal_library(learner, changes=None):
    item, _ = PersonalLibrary.objects.get_or_create(profile=learner)
    if changes is not None:
        for key, value in changes.items():
            setattr(item, {"lastStages": "last_stages", "comfortableSpeeds": "comfortable_speeds"}.get(key, key), value)
        item.save(update_fields=[{"lastStages": "last_stages", "comfortableSpeeds": "comfortable_speeds"}.get(key, key) for key in changes])
    return {"favorites": item.favorites, "recents": item.recents, "positions": item.positions, "progress": item.progress, "lastStages": item.last_stages, "comfortableSpeeds": item.comfortable_speeds}


def visit_data(item):
    return {"id": str(item.id), "startedAt": item.started_at.isoformat(), "seconds": item.seconds,
            "contentSeconds": item.content_seconds, "daySeconds": item.day_seconds}


def learner_visits(learner):
    return [visit_data(item) for item in SiteVisit.objects.filter(profile=learner)]


def save_visit(learner, data):
    with transaction.atomic():
        if SiteVisit.objects.filter(id=data["id"]).exclude(profile=learner).exists():
            raise ValueError("Invalid visit identity.")
        item, created = SiteVisit.objects.select_for_update().get_or_create(
            id=data["id"], profile=learner,
            defaults={"started_at": data["startedAt"], "seconds": data["seconds"],
                      "content_seconds": data["contentSeconds"], "day_seconds": data["daySeconds"]})
        if not created and data["startedAt"] != item.started_at:
            raise ValueError("Visit identity cannot change.")
        if not created and data["seconds"] > item.seconds:
            item.seconds = data["seconds"]
            item.content_seconds = data["contentSeconds"]
            item.day_seconds = data["daySeconds"]
            item.save(update_fields=["seconds", "content_seconds", "day_seconds", "updated_at"])
    return visit_data(item)
