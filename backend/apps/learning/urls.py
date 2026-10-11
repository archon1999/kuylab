from django.urls import path
from . import views, teaching_views

urlpatterns = [
    path("overview/", views.overview),
    path("compositions/", views.compositions),
    path("compositions/<int:pk>/plan/", views.composition_plan),
    path("profile/", views.profile),
    path("sessions/", views.sessions),
    path("tasks/<int:pk>/", views.task),
    path("compositions/<int:pk>/curriculum/", teaching_views.curriculum),
    path("compositions/<int:pk>/diagnostic/", teaching_views.diagnostic),
    path("compositions/<int:pk>/adaptive-plan/", teaching_views.recommendation),
    path("lessons/<int:pk>/", teaching_views.lesson_detail),
    path("lessons/<int:pk>/quiz/", teaching_views.lesson_quiz),
    path("lessons/<int:pk>/practice/", teaching_views.lesson_practice),
    path("lessons/<int:pk>/exercise/", teaching_views.lesson_exercise),
    path("lessons/<int:pk>/exercise/musicxml/", teaching_views.lesson_exercise_musicxml),
    path("arrangements/<int:pk>/full-score/", teaching_views.arrangement_full_score),
    path("arrangements/<int:pk>/full-score/pages/<int:page>/", teaching_views.arrangement_full_score_page),
]
