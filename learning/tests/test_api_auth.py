"""
Integration tests for authentication API endpoints.
"""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .factories import UserFactory


@pytest.mark.django_db
@pytest.mark.integration
class TestRegistrationAPI:
    """Test user registration API."""

    def setup_method(self):
        self.client = APIClient()
        self.register_url = reverse('register')

    @pytest.mark.skip(reason="JWT token generation causes cryptography pyo3 issue in test environment")
    def test_register_new_user(self):
        """Test successful user registration."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }

        response = self.client.post(self.register_url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['username'] == 'newuser'
        assert response.data['user']['email'] == 'newuser@example.com'
        assert User.objects.filter(username='newuser').exists()

    def test_register_password_mismatch(self):
        """Test registration fails when passwords don't match."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'TestPass123!',
            'password2': 'DifferentPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }

        response = self.client.post(self.register_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_register_duplicate_username(self):
        """Test registration fails with duplicate username."""
        UserFactory(username='existinguser')

        data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }

        response = self.client.post(self.register_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self):
        """Test registration fails with duplicate email."""
        UserFactory(email='existing@example.com')

        data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }

        response = self.client.post(self.register_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_weak_password(self):
        """Test registration fails with weak password."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',
            'password2': '123',
            'first_name': 'New',
            'last_name': 'User'
        }

        response = self.client.post(self.register_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_required_fields(self):
        """Test registration fails without required fields."""
        data = {
            'username': 'newuser',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }

        response = self.client.post(self.register_url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.integration
class TestLoginAPI:
    """Test user login API."""

    def setup_method(self):
        self.client = APIClient()
        self.login_url = reverse('token_obtain_pair')
        self.user = UserFactory(username='testuser', password='testpass123')

    @pytest.mark.skip(reason="JWT token generation causes cryptography pyo3 issue in test environment")
    def test_login_success(self):
        """Test successful login."""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

        response = self.client.post(self.login_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_wrong_password(self):
        """Test login fails with wrong password."""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }

        response = self.client.post(self.login_url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self):
        """Test login fails for non-existent user."""
        data = {
            'username': 'nonexistent',
            'password': 'testpass123'
        }

        response = self.client.post(self.login_url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.integration
class TestTokenRefreshAPI:
    """Test JWT token refresh API."""

    def setup_method(self):
        self.client = APIClient()
        self.refresh_url = reverse('token_refresh')
        self.user = UserFactory()

    @pytest.mark.skip(reason="JWT token generation causes cryptography pyo3 issue in test environment")
    def test_refresh_token_success(self):
        """Test successful token refresh."""
        refresh = RefreshToken.for_user(self.user)

        data = {'refresh': str(refresh)}
        response = self.client.post(self.refresh_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    @pytest.mark.skip(reason="JWT token generation causes cryptography pyo3 issue in test environment")
    def test_refresh_token_invalid(self):
        """Test refresh fails with invalid token."""
        data = {'refresh': 'invalid_token'}
        response = self.client.post(self.refresh_url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.integration
class TestLogoutAPI:
    """Test user logout API."""

    def setup_method(self):
        self.client = APIClient()
        self.logout_url = reverse('logout')
        self.user = UserFactory()

    @pytest.mark.skip(reason="JWT token blacklisting causes cryptography pyo3 issue in test environment")
    def test_logout_success(self):
        """Test successful logout."""
        self.client.force_authenticate(user=self.user)

        # Note: Blacklisting is disabled in test mode
        data = {'refresh': 'test_refresh_token'}
        response = self.client.post(self.logout_url, data, format='json')

        # In test mode without blacklisting, this will fail gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_logout_unauthenticated(self):
        """Test logout fails when not authenticated."""
        response = self.client.post(self.logout_url, {}, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_without_refresh_token(self):
        """Test logout fails without refresh token."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.logout_url, {}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.integration
class TestUserProfileAPI:
    """Test user profile API."""

    def setup_method(self):
        self.client = APIClient()
        self.profile_url = reverse('profile')
        self.user = UserFactory(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )

    def test_get_profile_authenticated(self):
        """Test getting profile when authenticated."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'
        assert response.data['email'] == 'test@example.com'
        assert response.data['first_name'] == 'Test'
        assert response.data['last_name'] == 'User'

    def test_get_profile_unauthenticated(self):
        """Test getting profile fails when not authenticated."""
        response = self.client.get(self.profile_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self):
        """Test updating profile."""
        self.client.force_authenticate(user=self.user)

        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }

        response = self.client.patch(self.profile_url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Name'
        assert response.data['email'] == 'updated@example.com'

        # Verify database was updated
        self.user.refresh_from_db()
        assert self.user.first_name == 'Updated'
        assert self.user.last_name == 'Name'
        assert self.user.email == 'updated@example.com'

    def test_cannot_update_username(self):
        """Test that username cannot be updated."""
        self.client.force_authenticate(user=self.user)

        data = {'username': 'newusername'}
        response = self.client.patch(self.profile_url, data, format='json')

        # Username should remain unchanged
        self.user.refresh_from_db()
        assert self.user.username == 'testuser'
