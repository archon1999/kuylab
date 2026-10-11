"""Authenticated learner fixtures for historical endpoint tests.

Security tests use DRF's original APIClient and explicit independent accounts.
"""
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from apps.learning.models import Profile

class LearnerClient(APIClient):
    def request(self, **kwargs):
        user, _ = get_user_model().objects.get_or_create(username="fixture-learner")
        profile, _ = Profile.objects.get_or_create(pk=1)
        if profile.user_id is None:
            profile.user = user
            profile.save(update_fields=["user"])
        self.force_authenticate(user)
        return super().request(**kwargs)

class LearnerTestCase(APITestCase):
    client_class = LearnerClient
