"""Task serializers: input validation only; no business rules."""

from rest_framework import serializers

from apps.tasks.models import Task, TaskPriority, TaskStatus


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "owner",
            "owner_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_title(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty or whitespace.")
        return value

    def validate_status(self, value: str) -> str:
        if value not in TaskStatus.values:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(TaskStatus.values)}."
            )
        return value

    def validate_priority(self, value: str) -> str:
        if value not in TaskPriority.values:
            raise serializers.ValidationError(
                f"Priority must be one of: {', '.join(TaskPriority.values)}."
            )
        return value


class TaskSummarySerializer(serializers.ModelSerializer):
    """Lightweight fields for list endpoints."""

    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Task
        fields = ["id", "title", "status", "priority", "due_date", "owner_email", "created_at"]
