"""Task model — UUID pk, ownership, enums, indexes, sensible ordering."""

import uuid

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TaskStatus(models.TextChoices):
    TODO = "todo", _("To do")
    IN_PROGRESS = "in_progress", _("In progress")
    DONE = "done", _("Done")


class TaskPriority(models.TextChoices):
    LOW = "low", _("Low")
    MEDIUM = "medium", _("Medium")
    HIGH = "high", _("High")


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("title"), max_length=200, validators=[MinLengthValidator(1)])
    description = models.TextField(_("description"), blank=True, default="")
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.TODO,
        db_index=True,
    )
    priority = models.CharField(
        _("priority"),
        max_length=20,
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM,
        db_index=True,
    )
    due_date = models.DateTimeField(_("due date"), null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("owner"),
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("task")
        verbose_name_plural = _("tasks")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "status"], name="task_owner_status_idx"),
            models.Index(fields=["owner", "priority"], name="task_owner_priority_idx"),
            models.Index(fields=["due_date"], name="task_due_date_idx"),
        ]

    def __str__(self) -> str:
        return self.title
