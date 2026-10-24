from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from apps.activity.models import PracticeNote


class NotebookTests(TestCase):
    def setUp(self):
        self.a = APIClient()
        self.b = APIClient()
        self.a.force_authenticate(get_user_model().objects.create_user(username="notes-a"))
        self.b.force_authenticate(get_user_model().objects.create_user(username="notes-b"))

    def note(self):
        response = self.a.post('/api/activity/notes/', {"contentId":"composition:8", "position":112.5, "text":"Chap qo‘lni oldindan tayyorlash"}, format='json')
        self.assertEqual(response.status_code,201)
        return response.data

    def test_timestamp_notes_are_private_editable_and_recoverable(self):
        note = self.note()
        endpoint = f'/api/activity/notes/{note["id"]}/'
        self.assertEqual(self.b.get('/api/activity/notes/').data,[])
        self.assertEqual(self.b.patch(endpoint,{"text":"intrusion"},format='json').status_code,404)
        self.assertEqual(self.b.delete(endpoint).status_code,404)
        self.assertEqual(self.a.patch(endpoint,{"contentId":"composition:9"},format='json').status_code,400)
        edited = self.a.patch(endpoint,{"text":"Yangilangan qayd"},format='json')
        self.assertEqual(edited.data['position'],112.5)
        self.assertEqual(edited.data['text'],'Yangilangan qayd')
        self.assertEqual(self.a.delete(endpoint).status_code,204)
        self.assertTrue(PracticeNote.objects.get(pk=note['id']).deleted)
        self.assertEqual(self.a.get('/api/activity/notes/').data,[])
        self.assertEqual(self.a.patch(endpoint,{"deleted":False},format='json').status_code,200)
        self.assertEqual(len(self.a.get('/api/activity/notes/?content=composition%3A8').data),1)
        self.assertEqual(self.a.get('/api/activity/notes/?content=composition%3A9').data,[])

    def test_note_validation_and_anonymous_access(self):
        self.assertIn(APIClient().get('/api/activity/notes/').status_code,[401,403])
        for changes in [{"position":-1},{"position":7201},{"text":" "},{"text":"x"*1001},{"contentId":"../../other"}]:
            response = self.a.post('/api/activity/notes/',{"contentId":"theory:triads","position":0,"text":"OK",**changes},format='json')
            self.assertEqual(response.status_code,400)

    def test_stage_status_and_comfortable_speed_preserve_legacy_state(self):
        state={"favorites":["theory:triads"],"recents":[],"positions":{"composition:8":112},"progress":{"lesson:still:opening-listen":"mastered","lesson:still:opening-listen:stage:1":"learning"},"comfortableSpeeds":{"lesson:still:opening-listen:stage:1":65}}
        self.assertEqual(self.a.patch('/api/activity/state/',state,format='json').status_code,200)
        self.assertEqual(self.a.get('/api/activity/state/').data['comfortableSpeeds'],state['comfortableSpeeds'])
        self.assertEqual(self.b.get('/api/activity/state/').data['comfortableSpeeds'],{})
        old = {key:value for key,value in state.items() if key not in ['comfortableSpeeds','progress']}
        self.a.patch('/api/activity/state/',old,format='json')
        self.assertEqual(self.a.get('/api/activity/state/').data['comfortableSpeeds'],state['comfortableSpeeds'])
        for speed in [0,201,-1]:
            self.assertEqual(self.a.patch('/api/activity/state/',{**state,"comfortableSpeeds":{"theory:triads":speed}},format='json').status_code,400)

    def test_player_contexts_do_not_overwrite_other_content_or_accounts(self):
        first='/api/auth/player-preferences/?context=composition%3A8'
        second='/api/auth/player-preferences/?context=theory%3Atriads'
        self.assertEqual(self.a.patch(first,{"speed":.7,"left":True},format='json').status_code,200)
        self.assertEqual(self.a.patch(second,{"speed":.9,"right":False},format='json').status_code,200)
        self.assertEqual(self.a.get(first).data,{"speed":.7,"left":True})
        self.assertEqual(self.b.get(first).data,{})
        self.assertEqual(self.a.get('/api/auth/player-preferences/').data,{})
        self.assertEqual(self.a.patch('/api/auth/player-preferences/?context=../other',{},format='json').status_code,400)
