from django.test import TestCase
from django.contrib.auth.models import User
from api.apps.task.models import TaskProfile
from api.apps.task.models.task import TaskResponsible
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


class TaskProfileTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

    def test_task_creation(self):
        task = TaskProfile.objects.create(
            title='Test Task created',
            created_by=self.user
        )
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.created_by, self.user)

    def test_task_responsible_creation(self):
        task = TaskProfile.objects.create(
            title='Test Task created',
            created_by=self.user
        )
        task_responsible = task.TaskResponsible.objects.create(
            task=task,
            user=self.user
        )
        self.assertEqual(task_responsible.task, task)
        self.assertEqual(task_responsible.user, self.user)

# Teste Lógica:
class TaskResponsibleTestCase(TestCase):
    def setUp(self):
        self.task = TaskProfile.objects.create(name='Task 1')
        self.user = User.objects.create(username='user1')

    def test_unique_together(self):
        # Cria o primeiro registro, que deve ser bem-sucedido
        TaskResponsible.objects.create(task=self.task, user=self.user)

        # Tenta criar um segundo registro com o mesmo task e user
        with self.assertRaises(IntegrityError):
            TaskResponsible.objects.create(task=self.task, user=self.user)
