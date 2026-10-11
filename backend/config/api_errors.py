from django.db import OperationalError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def local_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None and isinstance(exc, OperationalError):
        # A busy or unavailable local SQLite database is a recoverable service
        # failure, not a reason to expose DEBUG paths/SQL in an API response.
        return Response({"detail": "The local database is temporarily unavailable. Please try again when it is available."}, status=503)
    return response
