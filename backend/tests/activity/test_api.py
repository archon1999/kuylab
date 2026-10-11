from datetime import timedelta
from uuid import uuid4
from django.test import TestCase
from django.utils import timezone
from tests.support import LearnerClient as APIClient
from apps.activity.models import SiteVisit


class ActivityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.now = timezone.now()

    def visit(self, seconds=300, identity=None):
        return {"id": str(identity or uuid4()), "startedAt": (self.now - timedelta(seconds=1000)).isoformat(),
                "seconds": seconds, "contentSeconds": {"composition:1": seconds},
                "daySeconds": {timezone.localdate(self.now).isoformat(): seconds}}

    def test_visits_under_five_minutes_not_stored(self):
        response = self.client.put('/api/activity/visits/', self.visit(299), format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(SiteVisit.objects.exists())

    def test_cumulative_updates_idempotent_and_never_rewind(self):
        data = self.visit()
        self.assertEqual(self.client.put('/api/activity/visits/', data, format='json').status_code, 200)
        extended = self.visit(450, data['id'])
        extended['startedAt'] = data['startedAt']
        self.client.put('/api/activity/visits/', extended, format='json')
        self.client.put('/api/activity/visits/', data, format='json')
        self.assertEqual(SiteVisit.objects.count(), 1)
        self.assertEqual(SiteVisit.objects.get().seconds, 450)

    def test_inconsistent_or_future_activity_rejected(self):
        data = self.visit()
        data['daySeconds'] = {}
        self.assertEqual(self.client.put('/api/activity/visits/', data, format='json').status_code, 400)
        data = self.visit(1200)
        self.assertEqual(self.client.put('/api/activity/visits/', data, format='json').status_code, 400)

    def test_personal_state_only_stores_user_preferences(self):
        data = {"favorites": ['composition:1','exercise-scale-easy'], "recents": [{"id": 'composition:1', "openedAt": self.now.isoformat()}], "positions": {"composition:1": 42.3}}
        self.assertEqual(self.client.patch('/api/activity/state/', data, format='json').status_code, 200)
        result = self.client.get('/api/activity/state/').json()
        self.assertEqual(result['favorites'], data['favorites'])
        self.assertEqual(result['positions'], data['positions'])

    def test_cross_origin_write_is_rejected(self):
        response = self.client.put('/api/activity/visits/', self.visit(), format='json', HTTP_ORIGIN='https://unrelated.example')
        self.assertEqual(response.status_code, 403)

    def test_malformed_body_returns_validation_error(self):
        response = self.client.put('/api/activity/visits/', ['bad'], format='json')
        self.assertEqual(response.status_code, 400)
