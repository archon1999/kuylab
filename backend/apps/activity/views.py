from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import PersonalSerializer, VisitSerializer
from .services import learner_profile, learner_visits, personal_library, save_visit


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
    except ValueError as error:
        return Response({"detail": str(error)}, status=400)
