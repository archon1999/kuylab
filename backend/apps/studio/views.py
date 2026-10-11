from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.learning.models import Profile
from apps.learning.localization import request_language
from .services import CatalogNotPrepared, studio_catalog


@api_view(["GET"])
def catalog(request):
    # A read never creates the profile or mutates content.
    from apps.learning.accounts import user_profile
    profile = user_profile(request.user)
    language = request_language(request, profile)
    try:
        result = studio_catalog(language)
    except CatalogNotPrepared as error:
        return Response({"detail": str(error)}, status=503)
    response = Response(result)
    response["Content-Language"] = language
    response["Vary"] = "Accept-Language"
    return response
