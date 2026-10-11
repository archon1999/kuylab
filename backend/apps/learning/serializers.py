import re
from collections.abc import Mapping
from decimal import Decimal, ROUND_HALF_UP
from rest_framework import serializers
from .models import Arrangement, Composition, PracticePlan, PracticeSession, PracticeTask, Profile


class StrictFieldsMixin:
    """Reject fields that would otherwise imply unsupported data was accepted."""
    def to_internal_value(self, data):
        if not isinstance(data, Mapping):
            return super().to_internal_value(data)
        unknown = set(data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError({key: "Bu maydon qo'llab-quvvatlanmaydi." for key in sorted(unknown)})
        return super().to_internal_value(data)


class ProfileSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    def update(self, instance, validated_data):
        # Independent PATCHes may load the same profile snapshot. Persist only
        # supplied fields so a theme change cannot undo a simultaneous rename.
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if validated_data:
            instance.save(update_fields=list(validated_data))
        return instance

    def validate_display_name(self, value):
        value = value.strip()
        if not value or any(ord(character) < 32 or ord(character) == 127 for character in value):
            raise serializers.ValidationError("Ism bo'sh yoki nazorat belgilaridan iborat bo'lishi mumkin emas.")
        return value

    class Meta:
        model = Profile
        fields = ["id", "display_name", "instrument_model", "keys", "practice_minutes", "level", "goal", "language", "theme"]
        read_only_fields = ["id"]


class ArrangementSerializer(serializers.ModelSerializer):
    full_score_file_url = serializers.SerializerMethodField()
    full_score_pages = serializers.SerializerMethodField()
    active_score_id = serializers.SerializerMethodField()
    active_score_format = serializers.SerializerMethodField()
    active_score_completeness_verified_at = serializers.SerializerMethodField()
    midi_file_url = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        language = self.context.get("language", "uz")
        if language == "uz":
            return data
        if instance.seed_key == "hes-a-pirate-bitmidi-full" and instance.title == "He's a Pirate · to'liq ikki qo'lli piano MIDI":
            data["title"] = "He's a Pirate · complete two-hand piano MIDI" if language == "en" else "He's a Pirate · полный MIDI для двух рук"
        elif instance.composition.seed_key in {"sound-of-silence", "all-in-ost", "winter-sonata-ost", "what-is-a-youth", "naruto-ost"} and instance.title == "Aniq variant hali tanlanmagan":
            data["title"] = "Exact version not selected yet" if language == "en" else "Точная версия пока не выбрана"
        return data

    def get_full_score_file_url(self, obj):
        return f"/api/arrangements/{obj.id}/full-score/" if obj.full_score_file and obj.full_score_format == "pdf" else ""

    def get_active_score_id(self, obj):
        score = obj.scores.first()
        return score.id if score else None

    def get_active_score_format(self, obj):
        score = obj.scores.first()
        return score.file_format if score else None

    def get_active_score_completeness_verified_at(self, obj):
        score = obj.scores.first()
        return score.completeness_verified_at if score else None

    def get_midi_file_url(self, obj):
        score = obj.scores.first()
        return f"/api/scores/{score.id}/file/" if score and score.file_format == "midi" else ""

    def get_full_score_pages(self, obj):
        from .full_scores import verified_page_paths
        return [{"number": number, "url": f"/api/arrangements/{obj.id}/full-score/pages/{number}/"} for number, _ in enumerate(verified_page_paths(obj), 1)]

    class Meta:
        model = Arrangement
        fields = ["id", "title", "is_default", "source_url", "reference_video_url", "full_score_url", "full_score_format", "full_score_verified_at", "full_score_file_url", "full_score_pages", "active_score_id", "active_score_format", "active_score_completeness_verified_at", "midi_file_url", "source_kind", "arranger", "rights_status", "rights_note", "exact_version_confirmed", "workflow_status", "key_signature", "time_signature", "tempo_bpm", "tempo_beat_unit", "page_count"]


class CompositionSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    arrangement = serializers.SerializerMethodField()
    session_count = serializers.SerializerMethodField()
    source_url = serializers.URLField(write_only=True, required=False, allow_blank=True, max_length=1000)
    arrangement_title = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=180)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        titles = {"all-in-ost": "All In OST", "winter-sonata-ost": "Winter Sonata OST", "naruto-ost": "Naruto OST"}
        base = titles.get(instance.seed_key)
        language = self.context.get("language", "uz")
        if base and language != "uz" and instance.title == f"{base} — trek tanlanmagan":
            data["title"] = f"{base} — track not selected" if language == "en" else f"{base} — трек не выбран"
        return data

    class Meta:
        model = Composition
        fields = ["id", "title", "composer", "category", "goal", "color", "status", "arrangement", "session_count", "source_url", "arrangement_title"]
        read_only_fields = ["id", "arrangement", "session_count"]

    def get_arrangement(self, obj):
        item = next(iter(obj.arrangements.all()), None)
        return ArrangementSerializer(item, context=self.context).data if item else None

    def get_session_count(self, obj):
        return obj.sessions.count()

    def validate_color(self, value):
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise serializers.ValidationError("Rang #RRGGBB ko'rinishida bo'lishi kerak.")
        return value


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeTask
        fields = ["id", "order", "kind", "title", "instructions", "minutes", "concept", "success_criterion", "completed"]


class TaskUpdateSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = PracticeTask
        fields = ["completed"]


class PlanSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    arrangement = ArrangementSerializer(read_only=True)
    composition_id = serializers.IntegerField(source="arrangement.composition_id", read_only=True)

    class Meta:
        model = PracticePlan
        fields = ["id", "composition_id", "title", "summary", "readiness", "is_demo", "arrangement", "tasks"]


class SessionSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    minutes = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=Decimal("0.01"), max_value=240, required=False, coerce_to_string=False)
    duration_seconds = serializers.IntegerField(min_value=1, max_value=14400, required=False, allow_null=True)
    composition_title = serializers.CharField(source="composition.title", read_only=True)
    evidence = serializers.SerializerMethodField()

    class Meta:
        model = PracticeSession
        fields = ["id", "composition", "composition_title", "minutes", "duration_seconds", "bpm", "comfort", "notes", "input_mode", "created_at", "evidence"]
        read_only_fields = ["id", "composition_title", "input_mode", "created_at", "evidence"]

    def get_evidence(self, obj):
        return "user_reported"

    def validate(self, attrs):
        seconds = attrs.get("duration_seconds")
        minutes = attrs.get("minutes")
        if seconds is None and minutes is None:
            raise serializers.ValidationError({"minutes": "Daqiqa yoki duration_seconds kiriting."})
        if seconds is not None:
            attrs["minutes"] = (Decimal(seconds) / 60).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return attrs
