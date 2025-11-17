"""
Tests for the learning app API views.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from learning.models import Area, Topico, Trilha, Passo, UserProgress
from learning.tests.factories import (
    UserProgressFactory,
    AreaFactory,
    TopicoFactory,
    TrilhaFactory,
    LessonFactory,
    QuizFactory,
    QuestaoFactory,
    AlternativaFactory,
    CorrectAlternativaFactory,
    UserFactory,
)
from django.core.cache import cache

# Mark all tests in this file as Django tests that require database access.
pytestmark = pytest.mark.django_db


# ============================================================================
# Authentication Tests
# ============================================================================

@pytest.mark.unit
class TestRegisterView:
    """
    Test suite for the RegisterView API endpoint.
    """
    def test_register_user_success(self):
        """
        Ensure user can register successfully with valid data.
        """
        client = APIClient()
        url = reverse('register')
        data = {
            'username': 'testuser',
            'password': 'a-very-strong-password',
            'password2': 'a-very-strong-password',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.count() == 1
        assert User.objects.get().username == 'testuser'
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_register_user_password_mismatch(self):
        """
        Ensure registration fails if passwords do not match.
        """
        client = APIClient()
        url = reverse('register')
        data = {
            'username': 'testuser',
            'password': 'password123',
            'password2': 'password456',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_register_user_existing_email(self):
        """
        Ensure registration fails if email is already in use.
        """
        UserFactory(email='testuser@example.com')
        client = APIClient()
        url = reverse('register')
        data = {
            'username': 'testuser',
            'password': 'password123',
            'password2': 'password123',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data


@pytest.mark.unit
class TestUserProfileView:
    """
    Test suite for the UserProfileView API endpoint.
    """
    def test_get_profile_authenticated(self):
        """
        Ensure authenticated user can retrieve their profile.
        """
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse('profile')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username

    def test_get_profile_unauthenticated(self):
        """
        Ensure unauthenticated user cannot retrieve a profile.
        """
        client = APIClient()
        url = reverse('profile')
        response = client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile_authenticated(self):
        """
        Ensure authenticated user can update their profile.
        """
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse('profile')
        data = {'first_name': 'New', 'last_name': 'Name'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == 'New'
        assert user.last_name == 'Name'


@pytest.mark.unit
class TestLogoutView:
    """
    Test suite for the logout_view API endpoint.
    """
    def test_logout_authenticated(self):
        """
        Ensure authenticated user can log out.
        """
        user = UserFactory(password='a-very-strong-password')
        client = APIClient()
        client.force_authenticate(user=user)

        # First, get a refresh token
        login_url = reverse('token_obtain_pair')
        login_data = {'username': user.username, 'password': 'a-very-strong-password'}
        login_response = client.post(login_url, login_data)
        refresh_token = login_response.data['refresh']

        # Then, log out
        logout_url = reverse('logout')
        logout_data = {'refresh': refresh_token}
        response = client.post(logout_url, logout_data)

        # Check that the response is successful
        assert response.status_code == status.HTTP_200_OK

        # Verify that the refresh token is blacklisted
        refresh_url = reverse('token_refresh')
        refresh_data = {'refresh': refresh_token}
        refresh_response = client.post(refresh_url, refresh_data)
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# Learning Content Tests
# ============================================================================

@pytest.mark.integration
class TestLearningPathViewSet:
    """
    Test suite for the LearningPathViewSet API endpoint.
    """
    def test_list_learning_paths(self):
        """
        Ensure API returns a list of learning paths with nested structure.
        """
        cache.clear()
        # Create a complete learning path
        area = AreaFactory()
        topic = TopicoFactory(area=area)
        track = TrilhaFactory(topic=topic)
        LessonFactory(track=track)
        QuizFactory(track=track)

        client = APIClient()
        url = reverse('learning-path-list')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == area.title
        assert len(response.data['results'][0]['topics']) == 1
        assert len(response.data['results'][0]['topics'][0]['tracks']) == 1
        assert len(response.data['results'][0]['topics'][0]['tracks'][0]['steps']) == 2

    def test_retrieve_learning_path(self):
        """
        Ensure API can retrieve a single learning path by ID.
        """
        area = AreaFactory()
        client = APIClient()
        url = reverse('learning-path-detail', kwargs={'pk': area.pk})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == area.title

    def test_learning_path_caching(self):
        """
        Ensure the learning path list is cached.
        """
        cache.clear()
        client = APIClient()
        url = reverse('learning-path-list')

        # First request, should populate the cache
        AreaFactory()
        response1 = client.get(url)
        assert response1.status_code == status.HTTP_200_OK
        assert cache.get('learning_paths_full') is not None

        # Second request, should hit the cache
        from django.test import TestCase
        with TestCase().assertNumQueries(0):
            response2 = client.get(url)
            assert response2.status_code == status.HTTP_200_OK


# ============================================================================
# User Progress Tests
# ============================================================================

@pytest.mark.integration
class TestUserProgressViewSet:
    """
    Test suite for the UserProgressViewSet API endpoint.
    """
    def test_list_user_progress_authenticated(self):
        """
        Ensure authenticated user can list their own progress.
        """
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse('user-progress-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_list_user_progress_unauthenticated(self):
        """
        Ensure unauthenticated user cannot list progress.
        """
        client = APIClient()
        url = reverse('user-progress-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_user_progress(self):
        """
        Ensure authenticated user can create a progress record.
        """
        user = UserFactory()
        step = LessonFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse('user-progress-list')
        data = {'step': step.pk, 'status': 'in_progress'}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_update_user_progress(self):
        """
        Ensure authenticated user can update their progress.
        """
        user = UserFactory()
        progress = UserProgressFactory(user=user)
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse('user-progress-detail', kwargs={'pk': progress.pk})
        data = {'status': 'completed'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        progress.refresh_from_db()
        assert progress.status == 'completed'

    def test_delete_user_progress(self):
        """
        Ensure authenticated user can delete their progress.
        """
        user = UserFactory()
        progress = UserProgressFactory(user=user)
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse('user-progress-detail', kwargs={'pk': progress.pk})
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not UserProgress.objects.filter(pk=progress.pk).exists()

    def test_cannot_access_other_user_progress(self):
        """
        Ensure user cannot access another user's progress.
        """
        user1 = UserFactory()
        user2 = UserFactory()
        progress = UserProgressFactory(user=user2)
        client = APIClient()
        client.force_authenticate(user=user1)
        url = reverse('user-progress-detail', kwargs={'pk': progress.pk})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
class TestCompleteStepView:
    """
    Test suite for the complete_step API endpoint.
    """
    def test_complete_step_success(self):
        """
        Ensure authenticated user can mark a step as complete.
        """
        user = UserFactory()
        step = LessonFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse('complete-step', kwargs={'step_id': step.pk})
        response = client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert UserProgress.objects.filter(user=user, step=step, status='completed').exists()

    def test_complete_step_nonexistent(self):
        """
        Ensure completing a nonexistent step returns a 404.
        """
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse('complete-step', kwargs={'step_id': 999})
        response = client.post(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
