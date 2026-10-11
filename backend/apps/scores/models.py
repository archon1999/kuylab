import uuid
from django.db import models


def score_path(instance, filename):
    # Never use the uploaded filename as a filesystem path.
    extension = "mid" if instance.file_format == "midi" else "musicxml"
    return f"scores/{uuid.uuid4().hex}.{extension}"


class Score(models.Model):
    """An immutable imported score version, with separately editable study notes."""
    arrangement = models.ForeignKey("learning.Arrangement", on_delete=models.CASCADE, related_name="scores")
    version = models.PositiveIntegerField()
    file_format = models.CharField(max_length=12, default="musicxml", choices=[("musicxml", "MusicXML"), ("midi", "MIDI")])
    source_url = models.URLField(max_length=1000, blank=True)
    source_provenance = models.JSONField(default=dict)
    completeness_verified_at = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=180)
    original_filename = models.CharField(max_length=255)
    # Historical field name; stores the original source in its declared format.
    musicxml = models.FileField(upload_to=score_path)
    content_sha256 = models.CharField(max_length=64)
    rights_note = models.TextField(max_length=2000, blank=True)
    rights_confirmed_at = models.DateTimeField()
    exact_version_confirmed = models.BooleanField(default=False)
    parsed = models.JSONField()
    hand_overrides = models.JSONField(default=dict)
    sections = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [models.UniqueConstraint(fields=["arrangement", "version"], name="score_arrangement_version")]
