from datetime import timedelta
from django.apps import apps
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Composition, PracticePlan, PracticeSession, PracticeTask, Profile
from .plans import create_draft_plan
from .serializers import CompositionSerializer, PlanSerializer, ProfileSerializer, SessionSerializer, TaskSerializer, TaskUpdateSerializer
from .localization import localized_legacy_plan, request_language


def local_profile(request):
    from .accounts import user_profile
    return user_profile(request.user)


def compositions_queryset():
    return Composition.objects.prefetch_related("arrangements", "sessions").all()


@api_view(["GET"])
def overview(request):
    profile = local_profile(request)
    language = request_language(request, profile)
    compositions = list(compositions_queryset())
    active = next((item for item in compositions if item.status == "active"), compositions[0] if compositions else None)
    active_arrangement = active.arrangements.first() if active else None
    plan = PracticePlan.objects.filter(arrangement=active_arrangement, profile=profile).prefetch_related("tasks").first() if active_arrangement else None
    sessions = PracticeSession.objects.filter(profile=profile).select_related("composition")
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    week_sessions = sessions.filter(created_at__date__gte=week_start)
    def duration_minutes(queryset):
        seconds = sum(item.duration_seconds if item.duration_seconds is not None else float(item.minutes) * 60 for item in queryset)
        return round(seconds / 60, 2)
    return Response({
        "mode": "local_prototype", "profile": ProfileSerializer(profile).data,
        "compositions": CompositionSerializer(compositions, many=True, context={"language": language}).data,
        "active_composition": CompositionSerializer(active, context={"language": language}).data if active else None,
        "active_plan": localized_legacy_plan(PlanSerializer(plan, context={"language": language}).data, language) if plan else None,
        "sessions": SessionSerializer(sessions.order_by("-created_at")[:50], many=True).data,
        "stats": {
            "week_minutes": duration_minutes(week_sessions),
            "total_minutes": duration_minutes(sessions),
            "total_sessions": sessions.count(),
            "practiced_days": len({timezone.localdate(item.created_at) for item in week_sessions}),
        },
        "capabilities": {"automatic_evaluation": False, "score_import": apps.is_installed("scores"), "midi_evaluation": False,
                         "authored_lessons": True, "diagnostic": True, "adaptive_recommendations": True},
    })


@api_view(["GET", "POST"])
def compositions(request):
    language = request_language(request, local_profile(request))
    if request.method == "GET":
        return Response(CompositionSerializer(compositions_queryset(), many=True, context={"language": language}).data)
    serializer = CompositionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    source_url = serializer.validated_data.pop("source_url", "")
    arrangement_title = serializer.validated_data.pop("arrangement_title", "")
    with transaction.atomic():
        composition = serializer.save()
        create_draft_plan(composition, local_profile(request), source_url, arrangement_title)
    return Response(CompositionSerializer(composition, context={"language": language}).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def composition_plan(request, pk):
    composition = get_object_or_404(Composition, pk=pk)
    plan = get_object_or_404(PracticePlan.objects.prefetch_related("tasks"), arrangement=composition.arrangements.first(), profile=local_profile(request))
    language = request_language(request, local_profile(request))
    return Response(localized_legacy_plan(PlanSerializer(plan, context={"language": language}).data, language))


@api_view(["GET", "PATCH"])
def profile(request):
    item = local_profile(request)
    if request.method == "GET":
        return Response(ProfileSerializer(item).data)
    serializer = ProfileSerializer(item, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["GET", "POST"])
def sessions(request):
    profile = local_profile(request)
    if request.method == "GET":
        return Response(SessionSerializer(profile.sessions.select_related("composition").order_by("-created_at")[:100], many=True).data)
    serializer = SessionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(profile=profile)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
def task(request, pk):
    item = get_object_or_404(PracticeTask, pk=pk, plan__profile=local_profile(request))
    serializer = TaskUpdateSerializer(item, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(TaskSerializer(item).data)
