from django.db import models


class PersonalLibrary(models.Model):
    profile = models.OneToOneField("learning.Profile", on_delete=models.CASCADE)
    progress = models.JSONField(default=dict)
    last_stages = models.JSONField(default=dict)
    favorites = models.JSONField(default=list)
    recents = models.JSONField(default=list)
    positions = models.JSONField(default=dict)


class SiteVisit(models.Model):
    """A cumulative, idempotent visit; only five-minute visits are accepted."""
    id = models.UUIDField(primary_key=True, editable=False)
    profile = models.ForeignKey("learning.Profile", on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    seconds = models.PositiveIntegerField()
    content_seconds = models.JSONField(default=dict)
    day_seconds = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-started_at"]
