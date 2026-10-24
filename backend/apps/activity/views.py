from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .serializers import PersonalSerializer, VisitSerializer
from .services import learner_profile, learner_visits, personal_library, save_visit
from .models import PracticeNote
from .serializers import PracticeNoteSerializer


@api_view(["GET", "POST"])
def practice_notes(request):
    learner = learner_profile(request.user)
    notes = PracticeNote.objects.filter(profile=learner, deleted=False)
    if request.method == "GET":
        context = request.query_params.get("content")
        if context:
            notes = notes.filter(content_id=context)
        return Response(PracticeNoteSerializer(notes[:500], many=True).data)
    serializer = PracticeNoteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if notes.count() >= 500:
        return Response({"detail": "Practice note limit reached."}, status=400)
    values = serializer.validated_data
    values.pop("deleted", None)
    note = PracticeNote.objects.create(profile=learner, **values)
    return Response(PracticeNoteSerializer(note).data, status=201)


@api_view(["PATCH", "DELETE"])
def practice_note(request, note_id):
    note = get_object_or_404(PracticeNote, pk=note_id, profile=learner_profile(request.user))
    if request.method == "DELETE":
        note.deleted = True
        note.save(update_fields=["deleted", "updated_at"])
        return Response(status=204)
    if not isinstance(request.data, dict) or set(request.data) - {"text", "deleted"}:
        return Response({"detail": "Note target cannot change."}, status=400)
    serializer = PracticeNoteSerializer(note, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    for key, value in serializer.validated_data.items():
        setattr(note, key, value)
    note.save(update_fields=[*serializer.validated_data, "updated_at"])
    return Response(PracticeNoteSerializer(note).data)


@api_view(["GET", "PATCH"])
def personal_state(request):
    changes = None
    if request.method == "PATCH":
        serializer = PersonalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        changes = serializer.validated_data
    return Response(personal_library(learner_profile(request.user), changes))


@api_view(["GET", "PUT"])
def visits(request):
    learner = learner_profile(request.user)
    if request.method == "GET":
        return Response(learner_visits(learner))
    serializer = VisitSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        return Response(save_visit(learner, serializer.validated_data))
    except ValueError:
        return Response({"detail": "The activity record is invalid or belongs to another account."}, status=400)
