from rest_framework import serializers
from .serializers import StrictFieldsMixin


class AnswersSerializer(StrictFieldsMixin, serializers.Serializer):
    answers = serializers.DictField(child=serializers.CharField(max_length=80), allow_empty=False)

    def validate_answers(self, value):
        questions = self.context["questions"]
        required = {question["id"] for question in questions}
        if set(value) != required:
            raise serializers.ValidationError("Barcha savollarga javob bering; ortiqcha yoki noma'lum savol IDsi qabul qilinmaydi.")
        for question in questions:
            if value[question["id"]] not in {choice["id"] for choice in question["choices"]}:
                raise serializers.ValidationError(f"{question['id']}: javob variantlardan biri bo'lishi kerak.")
        return value


class LessonPracticeSerializer(StrictFieldsMixin, serializers.Serializer):
    successful_repetitions = serializers.IntegerField(min_value=0, max_value=3)
    comfort = serializers.IntegerField(min_value=1, max_value=5)
    bpm = serializers.IntegerField(min_value=20, max_value=240, allow_null=True, required=False, default=None)
    reflection = serializers.CharField(max_length=2000, allow_blank=True, required=False, default="")


class PlanMinutesSerializer(StrictFieldsMixin, serializers.Serializer):
    minutes = serializers.IntegerField(min_value=5, max_value=180, required=False)
