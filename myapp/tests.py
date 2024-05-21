from django.test import TestCase

# Create your tests here.

from django.contrib.auth.models import User
from django.urls import reverse

class UserRegistrationTest(TestCase):
    def test_user_registration(self):
        data = {
            'username': 'newuser',
            'password1': 'testpassword',
            'password2': 'testpassword'
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(User.objects.filter(username='newuser').exists())  

class UserLoginTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_success(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)  

    def test_login_failure(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)  
        self.assertTrue('ログインに失敗しました' in response.content.decode())  


