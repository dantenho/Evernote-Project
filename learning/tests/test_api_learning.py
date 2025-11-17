"""
Integration tests for learning paths and progress API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from learning.models import UserProgress
from .factories import (
    UserFactory,
    AreaFactory,
    TopicoFactory,
    TrilhaFactory,
    LessonFactory,
    QuizFactory,
    QuestaoFactory,
    AlternativaFactory,
    CorrectAlternativaFactory,
    UserProgressFactory,
    CompletedProgressFactory,
)


@pytest.mark.django_db
@pytest.mark.integration
class TestLearningPathsAPI:
    """Test learning paths API."""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('learning-path-list')

    def test_get_learning_paths_public_access(self):
        """Test that learning paths are publicly accessible."""
        # Create some learning content
        area = AreaFactory(title="Python")
        topico = TopicoFactory(area=area, title="Basics")
        trilha = TrilhaFactory(topic=topico, title="Getting Started")
        LessonFactory(track=trilha, title="Introduction")

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['title'] == "Python"

    def test_get_learning_paths_nested_structure(self):
        """Test that learning paths return nested structure."""
        area = AreaFactory(title="Python")
        topico = TopicoFactory(area=area, title="Basics")
        trilha = TrilhaFactory(topic=topico, title="Getting Started")
        lesson = LessonFactory(track=trilha, title="Introduction")

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        data = results[0]

        # Check nesting
        assert 'topics' in data
        assert len(data['topics']) == 1
        assert data['topics'][0]['title'] == "Basics"

        assert 'tracks' in data['topics'][0]
        assert len(data['topics'][0]['tracks']) == 1
        assert data['topics'][0]['tracks'][0]['title'] == "Getting Started"

        assert 'steps' in data['topics'][0]['tracks'][0]
        assert len(data['topics'][0]['tracks'][0]['steps']) == 1
        assert data['topics'][0]['tracks'][0]['steps'][0]['title'] == "Introduction"

    def test_get_learning_paths_with_quiz(self):
        """Test learning paths include quiz questions and alternatives."""
        area = AreaFactory()
        topico = TopicoFactory(area=area)
        trilha = TrilhaFactory(topic=topico)
        quiz = QuizFactory(track=trilha, title="Python Quiz")
        question = QuestaoFactory(step=quiz, text="What is Python?")
        CorrectAlternativaFactory(question=question, text="A programming language")
        AlternativaFactory(question=question, text="A snake")

        response = self.client.get(self.url)

        results = response.data['results']
        step = results[0]['topics'][0]['tracks'][0]['steps'][0]
        assert step['content_type'] == 'quiz'
        assert 'questions' in step
        assert len(step['questions']) == 1
        assert step['questions'][0]['text'] == "What is Python?"
        assert len(step['questions'][0]['choices']) == 2

    def test_get_learning_paths_ordering(self):
        """Test that learning paths respect order fields."""
        area = AreaFactory(order=1)
        topico1 = TopicoFactory(area=area, order=2, title="Second")
        topico2 = TopicoFactory(area=area, order=1, title="First")

        response = self.client.get(self.url)

        results = response.data['results']
        topics = results[0]['topics']
        assert topics[0]['title'] == "First"
        assert topics[1]['title'] == "Second"

    def test_get_empty_learning_paths(self):
        """Test getting learning paths when none exist."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0


@pytest.mark.django_db
@pytest.mark.integration
class TestCompleteStepAPI:
    """Test step completion API."""

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.step = LessonFactory()

    def test_complete_step_authenticated(self):
        """Test completing a step when authenticated."""
        self.client.force_authenticate(user=self.user)
        url = reverse('complete-step', kwargs={'step_id': self.step.id})

        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'detail' in response.data
        assert 'progress' in response.data
        assert response.data['progress']['status'] == UserProgress.COMPLETED

        # Verify database
        progress = UserProgress.objects.get(user=self.user, step=self.step)
        assert progress.status == UserProgress.COMPLETED
        assert progress.completed_at is not None

    def test_complete_step_unauthenticated(self):
        """Test completing a step fails when not authenticated."""
        url = reverse('complete-step', kwargs={'step_id': self.step.id})

        response = self.client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_complete_step_already_exists(self):
        """Test completing a step that already has progress."""
        UserProgressFactory(user=self.user, step=self.step, status=UserProgress.IN_PROGRESS)
        self.client.force_authenticate(user=self.user)
        url = reverse('complete-step', kwargs={'step_id': self.step.id})

        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['progress']['status'] == UserProgress.COMPLETED

    def test_complete_nonexistent_step(self):
        """Test completing a non-existent step returns 404."""
        self.client.force_authenticate(user=self.user)
        url = reverse('complete-step', kwargs={'step_id': 99999})

        response = self.client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.integration
class TestMyProgressAPI:
    """Test user progress retrieval API."""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('my-progress')
        self.user = UserFactory()

    def test_get_my_progress_authenticated(self):
        """Test getting user progress when authenticated."""
        step1 = LessonFactory()
        step2 = QuizFactory()
        CompletedProgressFactory(user=self.user, step=step1)
        UserProgressFactory(user=self.user, step=step2, status=UserProgress.IN_PROGRESS)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_get_my_progress_unauthenticated(self):
        """Test getting progress fails when not authenticated."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_my_progress_only_own_progress(self):
        """Test that users only see their own progress."""
        other_user = UserFactory()
        step = LessonFactory()

        # Create progress for both users
        UserProgressFactory(user=self.user, step=step)
        UserProgressFactory(user=other_user, step=step)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_get_my_progress_empty(self):
        """Test getting progress when user has none."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.django_db
@pytest.mark.integration
class TestProgressSummaryAPI:
    """Test user progress summary API."""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('user-progress-summary')
        self.user = UserFactory()

    def test_get_progress_summary(self):
        """Test getting progress summary."""
        # Create learning content
        area1 = AreaFactory(title="Python")
        area2 = AreaFactory(title="JavaScript")
        topico1 = TopicoFactory(area=area1)
        topico2 = TopicoFactory(area=area2)
        trilha1 = TrilhaFactory(topic=topico1)
        trilha2 = TrilhaFactory(topic=topico2)

        # Create steps
        step1 = LessonFactory(track=trilha1)
        step2 = LessonFactory(track=trilha1)
        step3 = LessonFactory(track=trilha2)

        # Create progress
        CompletedProgressFactory(user=self.user, step=step1)
        UserProgressFactory(user=self.user, step=step2, status=UserProgress.IN_PROGRESS)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert 'total_steps' in response.data
        assert 'completed_steps' in response.data
        assert 'in_progress_steps' in response.data
        assert 'completion_percentage' in response.data
        assert 'areas' in response.data

        assert response.data['total_steps'] == 2
        assert response.data['completed_steps'] == 1
        assert response.data['in_progress_steps'] == 1

    def test_progress_summary_by_area(self):
        """Test progress summary breaks down by area."""
        area = AreaFactory(title="Python")
        topico = TopicoFactory(area=area)
        trilha = TrilhaFactory(topic=topico)
        step1 = LessonFactory(track=trilha)
        step2 = LessonFactory(track=trilha)

        CompletedProgressFactory(user=self.user, step=step1)
        UserProgressFactory(user=self.user, step=step2, status=UserProgress.IN_PROGRESS)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert len(response.data['areas']) >= 1
        python_area = next(a for a in response.data['areas'] if a['title'] == "Python")
        assert python_area['completed_steps'] == 1
        assert python_area['in_progress_steps'] == 1

    def test_progress_summary_unauthenticated(self):
        """Test summary fails when not authenticated."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_progress_summary_no_progress(self):
        """Test summary when user has no progress."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_steps'] == 0
        assert response.data['completed_steps'] == 0
        assert response.data['completion_percentage'] == 0


@pytest.mark.django_db
@pytest.mark.integration
class TestUserProgressViewSet:
    """Test user progress viewset endpoints."""

    def setup_method(self):
        self.client = APIClient()
        self.list_url = reverse('user-progress-list')
        self.user = UserFactory()

    def test_create_progress(self):
        """Test creating progress for a step."""
        step = LessonFactory()
        self.client.force_authenticate(user=self.user)

        data = {
            'step': step.id,
            'status': UserProgress.IN_PROGRESS
        }

        response = self.client.post(self.list_url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert UserProgress.objects.filter(user=self.user, step=step).exists()

    def test_list_user_progress(self):
        """Test listing user's progress."""
        step1 = LessonFactory()
        step2 = QuizFactory()
        UserProgressFactory(user=self.user, step=step1)
        UserProgressFactory(user=self.user, step=step2)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_update_progress(self):
        """Test updating progress status."""
        progress = UserProgressFactory(user=self.user, status=UserProgress.IN_PROGRESS)
        self.client.force_authenticate(user=self.user)

        url = reverse('user-progress-detail', kwargs={'pk': progress.id})
        data = {'status': UserProgress.COMPLETED}

        response = self.client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        progress.refresh_from_db()
        assert progress.status == UserProgress.COMPLETED
