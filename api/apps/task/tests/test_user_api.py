from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# Testes Realizados nos usuários.
CREATE_USER_URL = reverse('create-user')

def create_user(**params): 
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        
        payload = {
            'email': 'fernando@hotmail.com',
            'password':'fernando',
            'name': 'Fernando',
        }
        res = self.client.post(CREATE_USER_URL, payload)
    
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        print(f"User: {user}")
        print(f"Password: {payload['password']}")
        self.assertTrue(user.check_password(payload['password']))
        
        self.assertNotEqual(user.password, payload['password'])
        
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
    # Teste retornando erro se o email ja existir.
        payload = {
            'email': 'fernando@hotmail.com',
            'password': 'fernando',
            'name': 'Fernando',
        }
        get_user_model().objects.create(**payload)
        res = self.client.post(CREATE_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        payload = {
            'email': 'fernando@hotmail.com',
            'password': 'fe',
            'name': 'Fernando',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)