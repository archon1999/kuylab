from django.urls import path
from .views import personal_state, visits

urlpatterns = [path("activity/state/", personal_state), path("activity/visits/", visits)]
