from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.apps.task.models import TaskProfile
from django.contrib.auth.models import (
    User as AuthUser,
)

# Testes estão sendo feitos nos serializers

class TaskTest(APITestCase):
    
    def setUp(self):
        self.user = AuthUser.objects.create_user(username='Rhayane', 
            password='admin')
        self.client.force_authenticate(user=self.user)    
    
    def test_permission_create_task_without_title(self): # Começar sempre com a palavra teste para ser executado
        url = reverse('task-view')
        data = {
            'description': 'Descrição sem título',
        }
        response = self.client.post(url, data, format='json')
    
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertEqual(response.data['title'][0], 'O título é obrigatório.')

    def test_date_not_before_2000(self):
        url = reverse('task-view')
        data = {
            'release': '1999-12-31',
            'deadline': '1999-12-31',
            'title': 'Tarefa1'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['date_field'][0], 'A data não pode ser anterior ao ano 2000')
    
    def test_after_2000(self):
        url = reverse('task-list')
        data = {
            'release' : '2000-01-01',
            'deadline' :  '2000-01-01'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
