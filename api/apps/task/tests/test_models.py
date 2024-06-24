from django.test import TestCase
from django.contrib.auth import get_user_model


class UsersModelsTests(TestCase):
    
    def test_create_user_with_email_successful(self):
        email = 'fernando@hotmail.com'
        password='fernando'
        name = 'fernando'
        
        user = get_user_model().objects.create_user(
            email = email,
            password = password,
            name = name
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.name, name)
        
        
    def test_new_user_email_normalized(self):
        
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)
               
    def test_new_user_without_email_raises_error(self):

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')
            
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'fernando@hotmail.com',
            'fernando',
            'fernando'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)