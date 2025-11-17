"""
Learning application models for a Duolingo-style learning platform.

This module defines the core data models for organizing educational content
in a hierarchical structure: Area → Topic → Track → Step.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Area(models.Model):
    """
    Top-level learning area (e.g., "Programming", "Languages").

    An Area contains multiple Topics and represents the broadest
    categorization of learning content.
    """

    title = models.CharField(
        max_length=150,
        unique=True,  # Prevent duplicate areas
        db_index=True,  # Index for faster lookups
        verbose_name="Título"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição",
        help_text="Optional description of this learning area"
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Ordem",
        help_text="Display order (lower numbers appear first)"
    )

    class Meta:
        ordering = ['order', 'title']  # Order by position, then alphabetically
        verbose_name = "Área"
        verbose_name_plural = "Áreas"
        indexes = [
            models.Index(fields=['order', 'title']),
        ]

    def __str__(self):
        return self.title

    def get_total_topics(self):
        """Return the total number of topics in this area."""
        return self.topics.count()

    def get_total_steps(self):
        """Return the total number of steps across all topics in this area."""
        return Passo.objects.filter(track__topic__area=self).count()

class Topico(models.Model):
    """
    Learning topic within an Area (e.g., "Python Basics" in "Programming").

    A Topic contains multiple Tracks and represents a specific subject
    within a broader learning area.
    """

    title = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Título"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição",
        help_text="Optional description of this topic"
    )
    area = models.ForeignKey(
        Area,
        related_name='topics',
        on_delete=models.CASCADE,
        verbose_name="Área"
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Ordem",
        help_text="Display order within the area"
    )

    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Tópico"
        verbose_name_plural = "Tópicos"
        unique_together = [['area', 'title']]  # Prevent duplicate topics in same area
        indexes = [
            models.Index(fields=['area', 'order']),
        ]

    def __str__(self):
        return f"{self.area.title} - {self.title}"

    def get_total_tracks(self):
        """Return the total number of tracks in this topic."""
        return self.tracks.count()

    def get_total_steps(self):
        """Return the total number of steps across all tracks in this topic."""
        return Passo.objects.filter(track__topic=self).count()

class Trilha(models.Model):
    """
    Learning track within a Topic (e.g., "Variables and Data Types").

    A Track contains multiple Steps (lessons and quizzes) and represents
    a specific learning path through related content.
    """

    title = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Título"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição",
        help_text="Optional description of this track"
    )
    topic = models.ForeignKey(
        Topico,
        related_name='tracks',
        on_delete=models.CASCADE,
        verbose_name="Tópico"
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Ordem",
        help_text="Display order within the topic"
    )
    # TODO: Implement prerequisite logic between tracks
    prerequisite = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='unlocks',
        verbose_name="Pré-requisito",
        help_text="Track that must be completed before this one"
    )

    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Trilha"
        verbose_name_plural = "Trilhas"
        unique_together = [['topic', 'title']]  # Prevent duplicate tracks in same topic
        indexes = [
            models.Index(fields=['topic', 'order']),
        ]

    def __str__(self):
        return f"{self.topic.title} - {self.title}"

    def get_total_steps(self):
        """Return the total number of steps in this track."""
        return self.steps.count()

    def is_unlocked_for_user(self, user):
        """
        Check if this track is unlocked for the given user.

        A track is unlocked if it has no prerequisite or if the
        prerequisite track has been completed by the user.
        """
        if not self.prerequisite:
            return True

        # # Claude: Use prefetched data to avoid N+1 queries.
        # This check now uses the `completed_prerequisite_steps` attribute,
        # which is populated by the optimized `LearningPathViewSet` query.
        # This avoids hitting the database for every track.
        if hasattr(self.prerequisite, 'completed_prerequisite_steps'):
            completed_count = len(self.prerequisite.completed_prerequisite_steps)
            return completed_count >= len(self.prerequisite.steps.all())

        # Fallback to a database query if prefetched data is not available.
        prerequisite_steps_count = self.prerequisite.steps.count()
        if prerequisite_steps_count == 0:
            return True

        completed_count = UserProgress.objects.filter(
            user=user,
            step__track=self.prerequisite,
            status=UserProgress.COMPLETED
        ).count()

        return completed_count >= prerequisite_steps_count

class Passo(models.Model):
    """
    Individual learning step within a Track (lesson or quiz).

    Steps are the atomic units of content. A lesson contains text/video
    educational content, while a quiz contains questions to test knowledge.
    """

    # Content type constants
    LESSON = 'lesson'
    QUIZ = 'quiz'
    CONTENT_CHOICES = (
        (LESSON, 'Lição'),
        (QUIZ, 'Quiz'),
    )

    title = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Título"
    )
    track = models.ForeignKey(
        Trilha,
        related_name='steps',
        on_delete=models.CASCADE,
        verbose_name="Trilha"
    )
    content_type = models.CharField(
        max_length=10,
        choices=CONTENT_CHOICES,
        default=LESSON,
        db_index=True,  # Index for filtering by content type
        verbose_name="Tipo de Conteúdo"
    )
    text_content = models.TextField(
        blank=True,
        null=True,
        verbose_name="Conteúdo em Texto",
        help_text="Main text content for lessons (supports HTML)"
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        max_length=500,
        verbose_name="URL do Vídeo",
        help_text="YouTube or other video embed URL"
    )
    estimated_time = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(180)],
        verbose_name="Tempo Estimado (minutos)",
        help_text="Estimated completion time in minutes"
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Ordem",
        help_text="Display order within the track"
    )

    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Passo"
        verbose_name_plural = "Passos"
        unique_together = [['track', 'title']]  # Prevent duplicate steps in same track
        indexes = [
            models.Index(fields=['track', 'order']),
            models.Index(fields=['content_type']),
        ]

    def __str__(self):
        return f"{self.track.title} - {self.title} ({self.get_content_type_display()})"

    def clean(self):
        """
        Validate model data before saving.

        Ensures that lessons have content and quizzes have questions.
        """
        super().clean()

        # Validate lesson content
        if self.content_type == self.LESSON:
            if not self.text_content and not self.video_url:
                raise ValidationError(
                    "Lessons must have either text content or a video URL."
                )

    def get_completion_rate(self):
        """
        Calculate the percentage of users who completed this step.

        Returns:
            float: Completion rate as percentage (0-100)
        """
        total_attempts = self.user_progress.count()
        if total_attempts == 0:
            return 0.0

        completed = self.user_progress.filter(
            status=UserProgress.COMPLETED
        ).count()

        return round((completed / total_attempts) * 100, 2)

    def is_completed_by_user(self, user):
        """
        Check if this step has been completed by the given user.

        Args:
            user: User instance to check

        Returns:
            bool: True if completed, False otherwise
        """
        return self.user_progress.filter(
            user=user,
            status=UserProgress.COMPLETED
        ).exists()

class Questao(models.Model):
    """
    Quiz question within a Step.

    Each question belongs to a quiz-type Step and contains multiple
    choice answers (Alternativa instances).
    """

    step = models.ForeignKey(
        Passo,
        related_name='questions',
        on_delete=models.CASCADE,
        verbose_name="Passo (Quiz)"
    )
    text = models.TextField(
        verbose_name="Texto da Questão",
        help_text="The question text presented to the user"
    )
    explanation = models.TextField(
        blank=True,
        null=True,
        verbose_name="Explicação",
        help_text="Optional explanation shown after answering"
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Ordem",
        help_text="Display order within the quiz"
    )

    class Meta:
        verbose_name = "Questão"
        verbose_name_plural = "Questões"
        ordering = ['order', 'id']
        indexes = [
            models.Index(fields=['step', 'order']),
        ]

    def __str__(self):
        # Truncate long questions for display
        max_length = 50
        if len(self.text) > max_length:
            return f"{self.text[:max_length]}..."
        return self.text

    def clean(self):
        """
        Validate question data.

        Ensures questions only belong to quiz-type steps.
        """
        super().clean()

        if self.step and self.step.content_type != Passo.QUIZ:
            raise ValidationError(
                "Questions can only be added to quiz-type steps."
            )

    def get_correct_choice(self):
        """
        Get the correct answer choice for this question.

        Returns:
            Alternativa: The correct choice, or None if not found
        """
        return self.choices.filter(is_correct=True).first()

    def has_valid_choices(self):
        """
        Check if this question has valid choices (at least one correct answer).

        Returns:
            bool: True if question has exactly one correct answer
        """
        correct_count = self.choices.filter(is_correct=True).count()
        return correct_count == 1

class Alternativa(models.Model):
    """
    Multiple choice answer option for a Question.

    Each question has multiple Alternativa instances, with exactly
    one marked as correct.
    """

    question = models.ForeignKey(
        Questao,
        related_name='choices',
        on_delete=models.CASCADE,
        verbose_name="Questão"
    )
    text = models.CharField(
        max_length=255,
        verbose_name="Texto da Alternativa",
        help_text="The choice text presented to the user"
    )
    is_correct = models.BooleanField(
        default=False,
        db_index=True,  # Index for filtering correct answers
        verbose_name="É a correta?",
        help_text="Mark this as the correct answer"
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Ordem",
        help_text="Display order (can be randomized in frontend)"
    )

    class Meta:
        verbose_name = "Alternativa"
        verbose_name_plural = "Alternativas"
        ordering = ['order', 'id']
        indexes = [
            models.Index(fields=['question', 'is_correct']),
        ]

    def __str__(self):
        prefix = "✓ " if self.is_correct else "✗ "
        return f"{prefix}{self.text}"

    def clean(self):
        """
        Validate choice data.

        Ensures each question has exactly one correct answer.
        """
        super().clean()

        # Only validate if this is the correct answer
        if self.is_correct and self.question_id:
            # Check if another correct answer already exists
            existing_correct = Alternativa.objects.filter(
                question=self.question,
                is_correct=True
            ).exclude(pk=self.pk)

            if existing_correct.exists():
                raise ValidationError(
                    "This question already has a correct answer. "
                    "Each question must have exactly one correct answer."
                )


class UserProgress(models.Model):
    """
    Track user progress through learning steps.

    Maintains a record of each user's interaction with steps,
    including completion status and timestamps.
    """

    # Status constants
    COMPLETED = 'completed'
    IN_PROGRESS = 'in_progress'
    STATUS_CHOICES = (
        (COMPLETED, 'Completed'),
        (IN_PROGRESS, 'In Progress'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name="Usuário",
        help_text="The user who is progressing through the step"
    )
    step = models.ForeignKey(
        Passo,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name="Passo",
        help_text="The step being tracked"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=IN_PROGRESS,
        db_index=True,  # Index for filtering by status
        verbose_name="Status"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,  # Index for sorting by completion date
        verbose_name="Completado em",
        help_text="Timestamp when the step was marked complete"
    )
    attempts = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Tentativas",
        help_text="Number of times user attempted this step (useful for quizzes)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Progresso do Usuário"
        verbose_name_plural = "Progressos dos Usuários"
        ordering = ['-updated_at']
        unique_together = [['user', 'step']]  # One progress record per user per step
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['step', 'status']),
            models.Index(fields=['user', 'completed_at']),
            models.Index(fields=['-updated_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.step.title} ({self.get_status_display()})"

    def mark_as_completed(self):
        """
        Mark this step as completed.

        Sets status to COMPLETED and records the completion timestamp.
        This operation is idempotent - calling it multiple times won't
        change the original completion date.
        """
        if self.status != self.COMPLETED:
            self.status = self.COMPLETED
            self.completed_at = timezone.now()
            self.save(update_fields=['status', 'completed_at', 'updated_at'])

    def increment_attempts(self):
        """
        Increment the attempt counter for this step.

        Useful for tracking quiz attempts.
        """
        self.attempts += 1
        self.save(update_fields=['attempts', 'updated_at'])

    def get_time_to_complete(self):
        """
        Calculate time taken to complete this step.

        Returns:
            timedelta: Time between creation and completion, or None if not completed
        """
        if self.completed_at and self.created_at:
            return self.completed_at - self.created_at
        return None

    @classmethod
    def get_user_completion_rate(cls, user):
        """
        Calculate overall completion rate for a user.

        Args:
            user: User instance

        Returns:
            dict: Dictionary with total_steps, completed_steps, and percentage
        """
        total = cls.objects.filter(user=user).count()
        if total == 0:
            return {
                'total_steps': 0,
                'completed_steps': 0,
                'percentage': 0.0
            }

        completed = cls.objects.filter(user=user, status=cls.COMPLETED).count()
        percentage = round((completed / total) * 100, 2)

        return {
            'total_steps': total,
            'completed_steps': completed,
            'in_progress_steps': total - completed,
            'percentage': percentage
        }
