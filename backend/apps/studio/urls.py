from django.urls import path
from .views import catalog

urlpatterns = [path("studio/catalog/", catalog)]
