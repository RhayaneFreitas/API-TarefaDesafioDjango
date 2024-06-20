from django.test import TestCase
from django.contrib.auth.models import User
from api.apps.task.models import TaskProfile
from api.apps.task.models.task import TaskResponsible
from django.contrib.auth import get_user_model



class TaskProfileTestCase(TestCase):
    
    def setUp(self):
        
        self.User = get_user_model()
        
        self.user = self.User.objects.create_user(
            email='fernando@hotmail.com',
            password='fernando',
            name='fernando'
        )

    def test_task_creation(self):
        task = TaskProfile.objects.create(
            title='teste1',
            created_by=self.user
        )
        
        self.assertEqual(task.title, 'teste1')
        self.assertEqual(task.created_by, self.user)

    def test_task_responsible_creation(self):
        task = TaskProfile.objects.create(
            title='teste1',
            created_by=self.user
        )
        task_responsible = TaskResponsible.objects.create(
            task=task,
            user=self.user
        )
        self.assertEqual(task_responsible.task, task)
        self.assertEqual(task_responsible.user, self.user)

class TaskResponsibleTestCase(TestCase):
    def setUp(self):
        
        self.User = get_user_model()      
        
        self.task = TaskProfile.objects.create(title='teste1')
        self.user = User.objects.create(username='fernando@hotmail.com')

    def test_unique_together(self):
        # Cria o primeiro registro, que deve ser bem-sucedido
        TaskResponsible.objects.create(task=self.task, user=self.user)

        # Tenta criar um segundo registro com o mesmo task e user
        with self.assertRaises(Exception):
            TaskResponsible.objects.create(
                task=self.task,
                user=self.user
            )
