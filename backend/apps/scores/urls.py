from django.urls import path
from . import views

urlpatterns = [
    path("scores/", views.scores),
    path("scores/demo/", views.demo),
    path("scores/demo/musicxml/", views.demo_musicxml),
    path("scores/<int:pk>/", views.score_detail),
    path("scores/<int:pk>/musicxml/", views.score_musicxml),
    path("scores/<int:pk>/file/", views.score_file),
]
