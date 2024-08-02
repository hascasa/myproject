from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.conf import settings

# User Testing
class CustomUserModelTests(TestCase):
    # Test to create a user with all the required fields
    def test_create_user_successful(self):
        username = 'newuser'
        email = 'newuser@example.com'
        password = 'SecurePass123'
        full_name = 'New User'
        role = 'student'
        user = get_user_model().objects.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role=role,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.full_name, full_name)
        self.assertEqual(user.role, role)
        self.assertTrue(user.is_active)

    # Test to create a user without an email
    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                username='invaliduser',
                email=None,
                password='invalidpass123',
                full_name='Invalid User',
                role='student',
            )

# API Testing
class UserAPITests(APITestCase):
    # Set up a superuser for API testing
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username='adminuser',
            email='adminuser@api.com',
            password='AdminPass123',
        )
        self.client.force_authenticate(user=self.user)

    # Test to retrieve the list of users from the API
    def test_list_users(self):
        url = reverse('users-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test to create a user with valid inputs
    def test_create_user_valid(self):
        test_image_path = os.path.join(os.path.dirname(__file__), 'test_images', 'sample_image.png')

        with open(test_image_path, 'rb') as image:
            image_content = SimpleUploadedFile(name='sample_image.png', content=image.read(), content_type='image/png')

        payload = {
            'username': 'validuser',
            'email': 'validuser@example.com',
            'password': 'ValidPass123',
            'full_name': 'Valid User',
            'role': 'teacher',
            'photo': image_content,
        }
        url = reverse('users-list')
        response = self.client.post(url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Test to create a user with invalid inputs
    def test_create_user_invalid(self):
        payload = {
            'username': '',
            'email': 'invalidemail.com',
            'password': 'short',
            'full_name': '',
            'role': 'invalidrole',
            'photo': 'invalidphoto'
        }
        url = reverse('users-list')
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test to retrieve specific user details based on the user ID
    def test_user_detail(self):
        url = reverse('users-detail', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)

    # Test to update the full_name of the user
    def test_update_user_valid(self):
        payload = {'full_name': 'Updated User Name'}
        url = reverse('users-detail', args=[self.user.id])
        response = self.client.patch(url, payload)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.full_name, 'Updated User Name')

    # Test to delete a user using the API
    def test_delete_user(self):
        url = reverse('users-detail', args=[self.user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(get_user_model().objects.filter(id=self.user.id).exists())

    # Clean up the test files from the media/profile_photos folder after unit tests
    def tearDown(self):
        if self.user.photo:
            if os.path.isfile(self.user.photo.path):
                os.remove(self.user.photo.path)
            self.user.photo.delete(save=True)

        test_image_path = os.path.join(settings.MEDIA_ROOT, 'profile_photos', 'sample_image.png')
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
