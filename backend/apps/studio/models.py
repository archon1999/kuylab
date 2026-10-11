from django.db import models


class StudioAsset(models.Model):
    """Stable curated identity; the source and pedagogy live in versioned code."""
    key = models.CharField(max_length=100, primary_key=True)
    score = models.OneToOneField("scores.Score", on_delete=models.CASCADE, related_name="studio_asset")
    revision = models.CharField(max_length=40)
