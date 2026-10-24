from django.urls import path
from .views import personal_state, visits, practice_notes, practice_note

urlpatterns = [path("activity/state/", personal_state), path("activity/visits/", visits),
               path("activity/notes/", practice_notes), path("activity/notes/<uuid:note_id>/", practice_note)]
