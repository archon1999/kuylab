from django.db import models
import uuid


class PersonalLibrary(models.Model):
    profile = models.OneToOneField("learning.Profile", on_delete=models.CASCADE)
    progress = models.JSONField(default=dict)
    last_stages = models.JSONField(default=dict)
    comfortable_speeds = models.JSONField(default=dict)
    favorites = models.JSONField(default=list)
    recents = models.JSONField(default=list)
    positions = models.JSONField(default=dict)


class PracticeNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey("learning.Profile", on_delete=models.CASCADE)
    content_id = models.CharField(max_length=100)
    position_seconds = models.FloatField()
    text = models.CharField(max_length=1000)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "id"]
        indexes = [models.Index(fields=["profile", "content_id"], name="practice_note_context")]


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
