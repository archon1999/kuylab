"""Session accounts. Curated scores are shared; learner state never is."""
import json
import re
from django.contrib.auth import authenticate, get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.middleware.csrf import get_token
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from .models import Profile


class AccountThrottle(AnonRateThrottle):
    rate = '20/hour'
    scope = 'account'


def user_profile(user):
    return Profile.objects.get_or_create(user=user, defaults={"display_name": user.username, "instrument_model": ""})[0]


def identity(request):
    if not request.user.is_authenticated:
        return None
    profile = user_profile(request.user)
    return {"id": request.user.pk, "username": request.user.username, "display_name": profile.display_name,
            "player_preferences": profile.player_preferences}


@api_view(["GET"])
@permission_classes([AllowAny])
def session(request):
    return Response({"user": identity(request), "csrfToken": get_token(request)})


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AccountThrottle])
def sign_in(request):
    SessionAuthentication().enforce_csrf(request)
    if not isinstance(request.data.get("password", ""), str) or len(request.data.get("password", "")) > 1024:
        return Response({"detail": "Invalid credentials."}, status=400)
    user = authenticate(request, username=str(request.data.get("username", ""))[:150], password=request.data.get("password", ""))
    if not user:
        return Response({"detail": "Login yoki parol noto‘g‘ri."}, status=400)
    login(request, user)
    return Response({"user": identity(request), "csrfToken": get_token(request)})


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AccountThrottle])
def register(request):
    SessionAuthentication().enforce_csrf(request)
    User = get_user_model()
    username = str(request.data.get("username", "")).strip()
    password = request.data.get("password", "")
    if not isinstance(password, str) or len(password) > 1024:
        return Response({"detail": "Invalid password."}, status=400)
    display_name = str(request.data.get("display_name", username)).strip()[:80]
    try:
        user = User(username=username)
        user.full_clean(exclude=["password"])
        validate_password(password, user)
        with transaction.atomic():
            user.set_password(password)
            user.save()
            Profile.objects.create(user=user, display_name=display_name or username, instrument_model="")
    except (ValidationError, IntegrityError, TypeError) as error:
        return Response({"detail": error.messages if isinstance(error, ValidationError) else "Akkaunt yaratib bo‘lmadi."}, status=400)
    login(request, user)
    return Response({"user": identity(request), "csrfToken": get_token(request)}, status=201)


@api_view(["POST"])
def sign_out(request):
    logout(request)
    return Response({"user": None, "csrfToken": get_token(request)})


@api_view(["POST"])
def password(request):
    current = request.data.get("current_password", "")
    if not isinstance(current, str) or len(current) > 1024 or not request.user.check_password(current):
        return Response({"detail": "Joriy parol noto‘g‘ri."}, status=400)
    new_password = request.data.get("new_password", "")
    if not isinstance(new_password, str) or len(new_password) > 1024:
        return Response({"detail": "Invalid password."}, status=400)
    try:
        validate_password(new_password, request.user)
    except (ValidationError, TypeError) as error:
        return Response({"detail": getattr(error, "messages", ["Parol noto‘g‘ri."])}, status=400)
    request.user.set_password(new_password)
    request.user.save(update_fields=["password"])
    update_session_auth_hash(request, request.user)
    return Response({"saved": True})


@api_view(["GET", "PATCH"])
def player_preferences(request):
    profile = user_profile(request.user)
    context = request.query_params.get("context")
    if context is not None and not re.fullmatch(r"[a-zA-Z0-9:_-]{1,100}", context):
        return Response({"detail": "Invalid preference context."}, status=400)
    if request.method == "PATCH":
        value = request.data
        if not isinstance(value, dict) or len(json.dumps(value)) > 4096:
            return Response({"detail": "Invalid preferences."}, status=400)
        allowed = {"noteNames", "keyNames", "shadows", "particles", "velocityGradients", "left", "right", "leftColor", "rightColor", "lookahead", "volume", "reverb", "speed", "leftVolume", "rightVolume", "countIn", "focusKeys", "compactNoteLengths", "keyboardZoom", "visibleKeys"}
        if set(value) - allowed:
            return Response({"detail": "Unknown preference."}, status=400)
        if context:
            with transaction.atomic():
                profile = Profile.objects.select_for_update().get(pk=profile.pk)
                if context not in profile.player_context_preferences and len(profile.player_context_preferences) >= 500:
                    return Response({"detail": "Preference context limit reached."}, status=400)
                profile.player_context_preferences = {**profile.player_context_preferences, context: value}
                profile.save(update_fields=["player_context_preferences"])
        else:
            profile.player_preferences = value
            profile.save(update_fields=["player_preferences"])
    return Response(profile.player_context_preferences.get(context, {}) if context else profile.player_preferences)
