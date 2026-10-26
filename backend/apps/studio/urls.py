from django.urls import path
from .views import catalog, preview

urlpatterns = [path("studio/catalog/", catalog),
               path("studio/compositions/<int:composition_id>/preview/", preview)]
