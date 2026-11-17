import factory

from apps.tasks.models import Task, TaskPriority, TaskStatus
from tests.factories.users import UserFactory


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task
        skip_postgeneration_save = True

    title = factory.Sequence(lambda n: f"Task {n}")
    description = factory.Faker("sentence")
    status = TaskStatus.TODO
    priority = TaskPriority.MEDIUM
    owner = factory.SubFactory(UserFactory)
    due_date = None
