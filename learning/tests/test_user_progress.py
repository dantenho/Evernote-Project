"""
Tests for UserProgress model.
"""
import pytest
from django.utils import timezone
from django.db import IntegrityError

from learning.models import UserProgress
from .factories import (
    UserFactory,
    PassoFactory,
    LessonFactory,
    QuizFactory,
    UserProgressFactory,
    CompletedProgressFactory,
)


@pytest.mark.django_db
@pytest.mark.unit
class TestUserProgressModel:
    """Test cases for UserProgress model."""

    def test_create_user_progress(self):
        """Test creating a UserProgress instance."""
        user = UserFactory()
        step = LessonFactory()
        progress = UserProgressFactory(user=user, step=step)

        assert progress.user == user
        assert progress.step == step
        assert progress.status == UserProgress.IN_PROGRESS
        assert progress.completed_at is None
        assert progress.pk is not None

    def test_user_progress_str_representation(self):
        """Test UserProgress __str__ method."""
        user = UserFactory(username="testuser")
        step = LessonFactory(title="Test Lesson")
        progress = UserProgressFactory(
            user=user,
            step=step,
            status=UserProgress.COMPLETED
        )

        assert str(progress) == "testuser - Test Lesson (completed)"

    def test_user_progress_default_status(self):
        """Test UserProgress defaults to IN_PROGRESS."""
        progress = UserProgressFactory()
        assert progress.status == UserProgress.IN_PROGRESS

    def test_completed_progress(self):
        """Test creating a completed progress."""
        progress = CompletedProgressFactory()

        assert progress.status == UserProgress.COMPLETED
        assert progress.completed_at is not None

    def test_mark_as_completed(self):
        """Test marking a progress as completed."""
        progress = UserProgressFactory(status=UserProgress.IN_PROGRESS)

        assert progress.status == UserProgress.IN_PROGRESS
        assert progress.completed_at is None

        # Mark as completed
        progress.mark_as_completed()

        assert progress.status == UserProgress.COMPLETED
        assert progress.completed_at is not None
        assert isinstance(progress.completed_at, type(timezone.now()))

    def test_user_progress_unique_together(self):
        """Test user and step combination must be unique."""
        user = UserFactory()
        step = LessonFactory()

        # Create first progress
        UserProgressFactory(user=user, step=step)

        # Try to create duplicate - should raise IntegrityError
        with pytest.raises(IntegrityError):
            UserProgressFactory(user=user, step=step)

    def test_user_can_have_multiple_progress_for_different_steps(self):
        """Test a user can have progress for multiple steps."""
        user = UserFactory()
        step1 = LessonFactory()
        step2 = QuizFactory()
        step3 = LessonFactory()

        progress1 = UserProgressFactory(user=user, step=step1)
        progress2 = UserProgressFactory(user=user, step=step2)
        progress3 = UserProgressFactory(user=user, step=step3)

        assert user.progress.count() == 3
        assert set(user.progress.all()) == {progress1, progress2, progress3}

    def test_step_can_have_progress_from_multiple_users(self):
        """Test a step can have progress from multiple users."""
        step = LessonFactory()
        user1 = UserFactory()
        user2 = UserFactory()
        user3 = UserFactory()

        progress1 = UserProgressFactory(user=user1, step=step)
        progress2 = UserProgressFactory(user=user2, step=step)
        progress3 = UserProgressFactory(user=user3, step=step)

        assert step.user_progress.count() == 3
        assert set(step.user_progress.all()) == {progress1, progress2, progress3}

    def test_user_progress_ordering(self):
        """Test UserProgress is ordered by -updated_at."""
        user = UserFactory()
        progress1 = UserProgressFactory(user=user)
        progress2 = UserProgressFactory(user=user)
        progress3 = UserProgressFactory(user=user)

        # Latest updated should be first
        all_progress = UserProgress.objects.filter(user=user)
        assert all_progress.first() == progress3

    def test_user_progress_cascade_delete_user(self):
        """Test deleting a user cascades to their progress."""
        user = UserFactory()
        progress1 = UserProgressFactory(user=user)
        progress2 = UserProgressFactory(user=user)

        assert UserProgress.objects.filter(user=user).count() == 2

        user.delete()

        assert UserProgress.objects.filter(pk=progress1.pk).count() == 0
        assert UserProgress.objects.filter(pk=progress2.pk).count() == 0

    def test_user_progress_cascade_delete_step(self):
        """Test deleting a step cascades to its progress records."""
        step = LessonFactory()
        user1 = UserFactory()
        user2 = UserFactory()
        progress1 = UserProgressFactory(user=user1, step=step)
        progress2 = UserProgressFactory(user=user2, step=step)

        assert UserProgress.objects.filter(step=step).count() == 2

        step.delete()

        assert UserProgress.objects.filter(pk=progress1.pk).count() == 0
        assert UserProgress.objects.filter(pk=progress2.pk).count() == 0

    def test_user_progress_timestamps(self):
        """Test UserProgress timestamps are set correctly."""
        progress = UserProgressFactory()

        assert progress.created_at is not None
        assert progress.updated_at is not None
        assert isinstance(progress.created_at, type(timezone.now()))
        assert isinstance(progress.updated_at, type(timezone.now()))

    def test_filter_progress_by_status(self):
        """Test filtering progress by status."""
        user = UserFactory()
        progress1 = UserProgressFactory(user=user, status=UserProgress.IN_PROGRESS)
        progress2 = CompletedProgressFactory(user=user)
        progress3 = UserProgressFactory(user=user, status=UserProgress.IN_PROGRESS)

        in_progress = user.progress.filter(status=UserProgress.IN_PROGRESS)
        completed = user.progress.filter(status=UserProgress.COMPLETED)

        assert in_progress.count() == 2
        assert completed.count() == 1
        assert set(in_progress) == {progress1, progress3}
        assert list(completed) == [progress2]

    def test_user_progress_verbose_names(self):
        """Test UserProgress meta verbose names."""
        assert UserProgress._meta.verbose_name == "Progresso do Usuário"
        assert UserProgress._meta.verbose_name_plural == "Progressos dos Usuários"


@pytest.mark.django_db
@pytest.mark.integration
class TestUserProgressIntegration:
    """Integration tests for UserProgress."""

    def test_complete_track_workflow(self):
        """Test completing all steps in a track."""
        from .factories import TrilhaFactory

        user = UserFactory()
        trilha = TrilhaFactory()

        # Create 5 steps in the track
        steps = [LessonFactory(track=trilha, order=i) for i in range(1, 6)]

        # User starts completing steps
        for step in steps[:3]:
            progress = UserProgressFactory(user=user, step=step)
            progress.mark_as_completed()

        # Check progress
        completed_count = user.progress.filter(status=UserProgress.COMPLETED).count()
        assert completed_count == 3

        # Complete remaining steps
        for step in steps[3:]:
            progress = UserProgressFactory(user=user, step=step)
            progress.mark_as_completed()

        # All steps completed
        completed_count = user.progress.filter(status=UserProgress.COMPLETED).count()
        assert completed_count == 5

    def test_multiple_users_different_progress(self):
        """Test multiple users with different progress on same content."""
        from .factories import TrilhaFactory

        trilha = TrilhaFactory()
        steps = [LessonFactory(track=trilha, order=i) for i in range(1, 4)]

        user1 = UserFactory(username="user1")
        user2 = UserFactory(username="user2")
        user3 = UserFactory(username="user3")

        # User 1 completes all steps
        for step in steps:
            progress = UserProgressFactory(user=user1, step=step)
            progress.mark_as_completed()

        # User 2 completes only first step
        progress = UserProgressFactory(user=user2, step=steps[0])
        progress.mark_as_completed()

        # User 3 has progress on first two steps but not completed
        UserProgressFactory(user=user3, step=steps[0], status=UserProgress.IN_PROGRESS)
        UserProgressFactory(user=user3, step=steps[1], status=UserProgress.IN_PROGRESS)

        # Verify each user's progress
        assert user1.progress.filter(status=UserProgress.COMPLETED).count() == 3
        assert user2.progress.filter(status=UserProgress.COMPLETED).count() == 1
        assert user3.progress.filter(status=UserProgress.COMPLETED).count() == 0
        assert user3.progress.filter(status=UserProgress.IN_PROGRESS).count() == 2

    def test_user_progress_statistics(self):
        """Test calculating user progress statistics."""
        from .factories import AreaFactory, TopicoFactory, TrilhaFactory

        user = UserFactory()

        # Create hierarchy with multiple steps
        area = AreaFactory()
        topico = TopicoFactory(area=area)
        trilha1 = TrilhaFactory(topic=topico, order=1)
        trilha2 = TrilhaFactory(topic=topico, order=2)

        # Create steps
        steps_trilha1 = [LessonFactory(track=trilha1, order=i) for i in range(1, 4)]
        steps_trilha2 = [QuizFactory(track=trilha2, order=i) for i in range(1, 3)]

        # User completes some steps
        for step in steps_trilha1:
            progress = UserProgressFactory(user=user, step=step)
            progress.mark_as_completed()

        # Start but not complete one step from trilha2
        UserProgressFactory(user=user, step=steps_trilha2[0], status=UserProgress.IN_PROGRESS)

        # Calculate statistics
        total_progress = user.progress.count()
        completed = user.progress.filter(status=UserProgress.COMPLETED).count()
        in_progress = user.progress.filter(status=UserProgress.IN_PROGRESS).count()

        assert total_progress == 4
        assert completed == 3
        assert in_progress == 1
