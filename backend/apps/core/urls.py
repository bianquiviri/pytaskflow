"""URL router for /api/v1/: health endpoint plus app routers."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.core.views import HealthView, ReadyView
from apps.tasks.views import TaskViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("ready/", ReadyView.as_view(), name="ready"),
    path("auth/", include("apps.accounts.urls")),
    path("", include(router.urls)),
]
