import re
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
    favorites = serializers.ListField(child=ContentId(), max_length=500)
    recents = RecentSerializer(many=True)
    positions = serializers.DictField(child=serializers.FloatField(min_value=0, max_value=7200))

    def validate(self, data):
        for field in ["progress", "lastStages"]:
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


