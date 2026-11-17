"""Task viewset: authentication + ownership scoping + filtering/search/ordering."""

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Task
from .permissions import IsTaskOwner
from .serializers import TaskSerializer, TaskSummarySerializer


@extend_schema_view(
    list=extend_schema(
        operation_id="tasks_list", tags=["tasks"], summary="List the authenticated user's tasks."
    ),
    create=extend_schema(
        operation_id="tasks_create",
        tags=["tasks"],
        summary="Create a task owned by the current user.",
    ),
    retrieve=extend_schema(operation_id="tasks_retrieve", tags=["tasks"]),
    update=extend_schema(operation_id="tasks_update", tags=["tasks"]),
    partial_update=extend_schema(operation_id="tasks_partial_update", tags=["tasks"]),
    destroy=extend_schema(operation_id="tasks_destroy", tags=["tasks"]),
)
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "priority"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "priority"]
    ordering = ["-created_at"]

    def get_queryset(self):
        # Hard ownership scoping: users only ever see their own tasks.
        # Schema generation has no real user; return an empty typed queryset.
        if getattr(self, "swagger_fake_view", False):
            return Task.objects.none()
        return Task.objects.filter(owner=self.request.user).select_related("owner")

    def get_serializer_class(self):
        if self.action == "list":
            return TaskSummarySerializer
        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
