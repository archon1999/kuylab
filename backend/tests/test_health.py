from unittest.mock import patch
from django.db import OperationalError
from django.test import SimpleTestCase, TestCase


class HealthTests(TestCase):
    def test_anonymous_readiness_checks_database(self):
        response = self.client.get("/health/ready/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class LivenessTests(SimpleTestCase):
    def test_liveness_does_not_need_database(self):
        self.assertEqual(self.client.get("/health/live/").status_code, 200)

    def test_readiness_failure_does_not_leak_connection_details(self):
        with patch("config.health.connections") as connections:
            connections.__getitem__.return_value.cursor.side_effect = OperationalError("private credentials")
            response = self.client.get("/health/ready/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": "unavailable"})
