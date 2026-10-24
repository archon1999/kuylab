import re
import math
from datetime import date

from django.utils import timezone
from rest_framework import serializers


class ContentId(serializers.RegexField):
    def __init__(self, **kwargs):
        super().__init__(r"^[a-zA-Z0-9:_-]{1,100}$", **kwargs)


class RecentSerializer(serializers.Serializer):
    id = ContentId()
    openedAt = serializers.DateTimeField()


class PersonalSerializer(serializers.Serializer):
    progress = serializers.DictField(child=serializers.ChoiceField(choices=["learning", "struggling", "mastered"]), required=False)
    lastStages = serializers.DictField(child=ContentId(), required=False)
    comfortableSpeeds = serializers.DictField(child=serializers.IntegerField(min_value=20, max_value=200), required=False)
    favorites = serializers.ListField(child=ContentId(), max_length=500)
    recents = RecentSerializer(many=True)
    positions = serializers.DictField(child=serializers.FloatField(min_value=0, max_value=7200))

    def validate(self, data):
        for field in ["progress", "lastStages", "comfortableSpeeds"]:
            values = data.get(field, {})
            if len(values) > 500 or any(not re.fullmatch(r"[a-zA-Z0-9:_-]{1,100}", key) for key in values):
                raise serializers.ValidationError("Invalid learning state.")
        if len(data["recents"]) > 40 or len(data["positions"]) > 500:
            raise serializers.ValidationError("Personal library limit exceeded.")
        if any(not re.fullmatch(r"[a-zA-Z0-9:_-]{1,100}", key) for key in data["positions"]):
            raise serializers.ValidationError("Invalid content ID.")
        data["favorites"] = list(dict.fromkeys(data["favorites"]))
        data["recents"] = [{"id": item["id"], "openedAt": item["openedAt"].isoformat()} for item in data["recents"]]
        return data


class PracticeNoteSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    contentId = ContentId(source="content_id")
    position = serializers.FloatField(source="position_seconds", min_value=0, max_value=7200)
    text = serializers.CharField(max_length=1000, trim_whitespace=True)
    deleted = serializers.BooleanField(required=False)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    def validate_position(self, value):
        if not math.isfinite(value):
            raise serializers.ValidationError("Invalid timestamp.")
        return value

    def validate_text(self, value):
        if "\x00" in value:
            raise serializers.ValidationError("Invalid note text.")
        return value


class VisitSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    startedAt = serializers.DateTimeField()
    seconds = serializers.IntegerField(min_value=300, max_value=86400)
    contentSeconds = serializers.DictField(child=serializers.IntegerField(min_value=0, max_value=86400))
    daySeconds = serializers.DictField(child=serializers.IntegerField(min_value=0, max_value=86400))

    def validate(self, data):
        if len(data["contentSeconds"]) > 500 or len(data["daySeconds"]) > 31:
            raise serializers.ValidationError("Visit limit exceeded.")
        if sum(data["contentSeconds"].values()) > data["seconds"] or sum(data["daySeconds"].values()) != data["seconds"]:
            raise serializers.ValidationError("Visit totals do not match.")
        if any(not re.fullmatch(r"[a-zA-Z0-9:_-]{1,100}", key) for key in data["contentSeconds"]):
            raise serializers.ValidationError("Invalid content ID.")
        start = data["startedAt"]
        now = timezone.now()
        if start > now or data["seconds"] > (now - start).total_seconds() + 10:
            raise serializers.ValidationError("Visit cannot exceed elapsed time.")
        for key in data["daySeconds"]:
            try:
                parsed = date.fromisoformat(key)
            except (ValueError, TypeError):
                raise serializers.ValidationError("Invalid visit date.")
            if parsed < timezone.localdate(start) or parsed > timezone.localdate(now):
                raise serializers.ValidationError("Visit date outside visit range.")
        return data


