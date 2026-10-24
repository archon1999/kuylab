from datetime import timedelta
from uuid import uuid4
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from apps.learning.models import Profile


class AccountTests(TestCase):
    def setUp(self):
        cache.clear()
        self.legacy = Profile.objects.create(display_name="Original owner")
        self.a = APIClient(enforce_csrf_checks=True)
        self.b = APIClient(enforce_csrf_checks=True)

    def register(self, client, name):
        token = client.get('/api/auth/session/').json()['csrfToken']
        result = client.post('/api/auth/register/', {"username":name, "password":"piano-Strong-8247!", "display_name":name}, format='json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(result.status_code,201,result.content)
        return result.json()['user']

    def patch(self, client, url, data, **headers):
        return client.patch(url, data, format='json', HTTP_X_CSRFTOKEN=client.cookies[settings.CSRF_COOKIE_NAME].value, **headers)

    def test_anonymous_cannot_read_or_write_personal_state(self):
        for path in ['/api/profile/','/api/activity/state/','/api/activity/visits/','/api/auth/player-preferences/','/api/studio/catalog/']:
            self.assertIn(self.a.get(path).status_code,[403,404],path)
        self.assertEqual(self.a.patch('/api/profile/', {'display_name':'Intruder'},format='json').status_code,403)

    def test_registration_never_claims_legacy_profile_and_rotates_session(self):
        a = self.register(self.a,'learner_a')
        self.legacy.refresh_from_db()
        self.assertIsNone(self.legacy.user_id)
        self.assertNotEqual(self.a.get('/api/profile/').json()['id'],self.legacy.id)
        self.assertEqual(self.a.get('/api/auth/session/').json()['user']['id'],a['id'])

    def test_two_learners_cannot_read_or_overwrite_each_other(self):
        a = self.register(self.a,'learner_a')
        b = self.register(self.b,'learner_b')
        state = {'favorites':['theory:voicing'], 'recents':[], 'positions':{'theory:voicing':12}, 'progress':{'theory:voicing':'struggling'}, 'lastStages':{'lesson:still:opening-listen':'lesson:still:opening-listen:2'}}
        self.assertEqual(self.patch(self.a,'/api/activity/state/',state).status_code,200)
        self.assertEqual(self.b.get('/api/activity/state/').json()['favorites'],[])
        self.patch(self.b,'/api/profile/',{'display_name':'Second learner','theme':'dark'})
        self.assertEqual(self.a.get('/api/profile/').json()['display_name'],'learner_a')
        self.assertEqual(self.patch(self.b,'/api/activity/state/',state,HTTP_X_KUYLAB_USER=str(a['id'])).status_code,401)
        self.assertNotEqual(a['id'],b['id'])

    def test_visit_id_collision_does_not_expose_other_user_or_cause_500(self):
        self.register(self.a,'learner_a'); self.register(self.b,'learner_b')
        now = timezone.now()
        data = {'id':str(uuid4()),'startedAt':(now-timedelta(seconds=400)).isoformat(),'seconds':300,'contentSeconds':{},'daySeconds':{timezone.localdate(now).isoformat():300}}
        def put(client): return client.put('/api/activity/visits/',data,format='json',HTTP_X_CSRFTOKEN=client.cookies[settings.CSRF_COOKIE_NAME].value)
        self.assertEqual(put(self.a).status_code,200)
        self.assertEqual(put(self.b).status_code,400)
        self.assertEqual(self.b.get('/api/activity/visits/').json(),[])

    def test_login_and_registration_require_csrf_even_when_anonymous(self):
        self.a.get('/api/auth/session/')
        for path in ['login','register']:
            self.assertEqual(self.a.post(f'/api/auth/{path}/',{'username':'tester','password':'strong_password'},format='json').status_code,403)

    def test_logout_invalidates_session(self):
        self.register(self.a,'learner_a')
        self.assertEqual(self.a.post('/api/auth/logout/',{},format='json',HTTP_X_CSRFTOKEN=self.a.cookies[settings.CSRF_COOKIE_NAME].value).status_code,200)
        self.assertIsNone(self.a.get('/api/auth/session/').json()['user'])
        self.assertEqual(self.a.get('/api/activity/state/').status_code,403)

    def test_player_preferences_are_per_user_and_survive_new_session(self):
        self.register(self.a,'learner_a'); self.register(self.b,'learner_b')
        self.patch(self.a,'/api/auth/player-preferences/',{'leftVolume':0,'rightVolume':80,'focusKeys':True})
        self.assertEqual(self.b.get('/api/auth/player-preferences/').json(),{})
        other = APIClient(enforce_csrf_checks=True)
        token = other.get('/api/auth/session/').json()['csrfToken']
        self.assertEqual(other.post('/api/auth/login/',{'username':'learner_a','password':'piano-Strong-8247!'},format='json',HTTP_X_CSRFTOKEN=token).status_code,200)
        self.assertEqual(other.get('/api/auth/player-preferences/').json()['leftVolume'],0)

    def test_weak_password_rejected_without_creating_account(self):
        token=self.a.get('/api/auth/session/').json()['csrfToken']
        response=self.a.post('/api/auth/register/',{'username':'learner_a','password':'123'},format='json',HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code,400)
        self.assertFalse(get_user_model().objects.exists())

    def test_all_private_responses_are_not_cacheable(self):
        self.register(self.a,'learner_a')
        for url in ['/api/auth/session/','/api/profile/','/api/activity/state/']:
            self.assertEqual(self.a.get(url)['Cache-Control'],'private, no-store')

    def test_invalid_progress_cannot_be_saved(self):
        self.register(self.a,'learner_a')
        response=self.patch(self.a,'/api/activity/state/',{'favorites':[],'recents':[],'positions':{},'progress':{'theory:voicing':'automatic_score_100'}})
        self.assertEqual(response.status_code,400)
