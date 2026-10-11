from collections.abc import Mapping
from rest_framework import serializers
from apps.learning.models import Arrangement, Composition
from .models import Score
from .parser import MAX_UPLOAD_BYTES


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if not isinstance(data, Mapping):
            return super().to_internal_value(data)
        unknown = set(data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError({key: "Bu maydon qo'llab-quvvatlanmaydi." for key in sorted(unknown)})
        return super().to_internal_value(data)


class ImportSerializer(StrictSerializer):
    file = serializers.FileField()
    arrangement_id = serializers.PrimaryKeyRelatedField(queryset=Arrangement.objects.all(), source="arrangement", required=False)
    composition_id = serializers.PrimaryKeyRelatedField(queryset=Composition.objects.all(), source="composition", required=False)
    rights_confirmed = serializers.BooleanField()
    exact_version_confirmed = serializers.BooleanField(default=False)
    rights_note = serializers.CharField(max_length=2000, allow_blank=True, default="")
    title = serializers.CharField(max_length=180, allow_blank=True, default="")
    source_url = serializers.URLField(max_length=1000, allow_blank=True, default="")

    def validate_file(self, value):
        if not value.size or value.size > MAX_UPLOAD_BYTES:
            raise serializers.ValidationError("Bo'sh fayl yoki 8 MB chegaradan katta fayl.")
        return value

    def validate_rights_confirmed(self, value):
        if not value:
            raise serializers.ValidationError("O'zingizga tegishli yoki foydalanishga ruxsat berilgan nota nusxasini tasdiqlang.")
        return value

    def validate(self, attrs):
        if ("arrangement" in attrs) == ("composition" in attrs):
            raise serializers.ValidationError({"arrangement_id": "Choose exactly one arrangement_id or composition_id."})
        return attrs


class ScoreSerializer(serializers.ModelSerializer):
    arrangement_id = serializers.IntegerField(read_only=True)
    musicxml_url = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    is_demo = serializers.BooleanField(default=False, read_only=True)
    rights_basis = serializers.SerializerMethodField()

    class Meta:
        model = Score
        fields = ["id", "arrangement_id", "version", "file_format", "source_url", "source_provenance", "completeness_verified_at", "title", "original_filename", "content_sha256", "metadata", "parsed",
                  "musicxml_url", "file_url", "rights_note", "rights_basis", "rights_confirmed_at", "exact_version_confirmed", "hand_overrides", "sections", "created_at", "is_demo"]
        read_only_fields = fields

    def get_musicxml_url(self, obj):
        return f"/api/scores/{obj.pk}/musicxml/" if obj.file_format == "musicxml" else ""

    def get_file_url(self, obj):
        return f"/api/scores/{obj.pk}/file/"

    def get_metadata(self, obj):
        return obj.parsed["metadata"]

    def get_rights_basis(self, obj):
        kind = obj.source_provenance.get("kind")
        return {"curated_public_midi":"public_download_source", "user_supplied_original_midi":"user_supplied_copy",
                "teaching_adaptation":"user_source_teaching_adaptation", "original_authored_study":"original_authored_study"}.get(kind,"user_confirmed_copy")


class ScoreSummarySerializer(ScoreSerializer):
    class Meta(ScoreSerializer.Meta):
        fields = [field for field in ScoreSerializer.Meta.fields if field != "parsed"]


class SectionSerializer(StrictSerializer):
    id = serializers.CharField(max_length=80)
    title = serializers.CharField(max_length=120)
    start_index = serializers.IntegerField(min_value=0)
    end_index = serializers.IntegerField(min_value=0)
    notes = serializers.CharField(max_length=2000, allow_blank=True, default="")


class ScoreUpdateSerializer(StrictSerializer):
    hand_overrides = serializers.DictField(child=serializers.ChoiceField(choices=["right", "left", "unknown"]), required=False)
    sections = SectionSerializer(many=True, required=False)
    exact_version_confirmed = serializers.BooleanField(required=False)

    def validate_hand_overrides(self, value):
        events = {event["id"] for event in self.context["score"].parsed["events"]}
        if not set(value).issubset(events):
            raise serializers.ValidationError("Qo'l belgilashda mavjud bo'lmagan nota IDsi bor.")
        return value

    def validate_sections(self, value):
        count = self.context["score"].parsed["metadata"]["measure_count"]
        if len(value) > 100 or len({section["id"] for section in value}) != len(value):
            raise serializers.ValidationError("Bo'limlar 100 tadan ko'p yoki IDlar takrorlangan.")
        for section in value:
            if section["start_index"] > section["end_index"] or section["end_index"] >= count:
                raise serializers.ValidationError("Bo'lim takt oralig'i mavjud nota chegarasidan tashqarida.")
        return value
