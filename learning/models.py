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

        # Check if all steps in prerequisite track are completed
        prerequisite_steps = self.prerequisite.steps.all()
        if not prerequisite_steps.exists():
            return True

        completed_count = UserProgress.objects.filter(
            user=user,
            step__track=self.prerequisite,
            status=UserProgress.COMPLETED
        ).count()

        return completed_count == prerequisite_steps.count()

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


# ============================================================================
# AI Content Generation Models
# ============================================================================

class AIProvider(models.Model):
    """
    Configuration for AI content generation providers.

    Supports multiple providers: Claude (Anthropic), Gemini (Google),
    Ollama (local), and custom OpenAI-compatible endpoints.
    """

    # Provider types
    CLAUDE = 'claude'
    GEMINI = 'gemini'
    OLLAMA = 'ollama'
    CUSTOM = 'custom'

    PROVIDER_TYPES = (
        (CLAUDE, 'Claude (Anthropic)'),
        (GEMINI, 'Gemini (Google)'),
        (OLLAMA, 'Ollama (Local)'),
        (CUSTOM, 'Custom Model'),
    )

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome",
        help_text="Display name for this provider"
    )
    provider_type = models.CharField(
        max_length=20,
        choices=PROVIDER_TYPES,
        verbose_name="Tipo de Provider",
        help_text="Type of AI provider"
    )
    api_key = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="API Key",
        help_text="API key for authentication (leave empty for Ollama)"
    )
    api_endpoint = models.URLField(
        blank=True,
        verbose_name="API Endpoint",
        help_text="API endpoint URL"
    )
    model_name = models.CharField(
        max_length=100,
        verbose_name="Nome do Modelo",
        help_text="Model identifier"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    max_tokens = models.PositiveIntegerField(default=2000)
    temperature = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI Provider"
        verbose_name_plural = "AI Providers"
        ordering = ['-is_active', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"


class ContentTemplate(models.Model):
    """Templates for AI content generation prompts."""

    STEP_LESSON = 'step_lesson'
    STEP_QUIZ = 'step_quiz'
    QUIZ_QUESTIONS = 'quiz_questions'

    CONTENT_TYPES = (
        (STEP_LESSON, 'Step - Lesson'),
        (STEP_QUIZ, 'Step - Quiz'),
        (QUIZ_QUESTIONS, 'Quiz Questions'),
    )

    name = models.CharField(max_length=100, unique=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    system_prompt = models.TextField()
    user_prompt_template = models.TextField(
        help_text="Use {{variable}} for placeholders"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Content Template"
        verbose_name_plural = "Content Templates"

    def __str__(self):
        return f"{self.name} ({self.get_content_type_display()})"

    def render_prompt(self, **kwargs):
        """Render prompt template with variables."""
        template = self.user_prompt_template
        for key, value in kwargs.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
        return template


class GeneratedContent(models.Model):
    """Track AI-generated content for auditing."""

    provider = models.ForeignKey(AIProvider, on_delete=models.SET_NULL, null=True)
    template = models.ForeignKey(ContentTemplate, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    prompt = models.TextField()
    generated_text = models.TextField()
    parsed_content = models.JSONField(default=dict)
    tokens_used = models.PositiveIntegerField(default=0)
    generation_time = models.FloatField(default=0.0)
    was_successful = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Generated Content"
        verbose_name_plural = "Generated Contents"
        ordering = ['-created_at']

    def __str__(self):
        return f"Generated by {self.provider} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


# ============================================================================
# Gamification Models
# ============================================================================

class UserProfile(models.Model):
    """
    Extended user profile for gamification features.

    Stores XP points, calculates rank tier, tracks achievements and streaks.
    One-to-one relationship with Django's User model.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Usuário",
        help_text="The user this profile belongs to"
    )
    xp_points = models.PositiveIntegerField(
        default=0,
        db_index=True,  # Index for leaderboard queries
        verbose_name="Pontos de Experiência",
        help_text="Total experience points earned"
    )
    current_streak = models.PositiveIntegerField(
        default=0,
        verbose_name="Sequência Atual",
        help_text="Current consecutive days of activity"
    )
    longest_streak = models.PositiveIntegerField(
        default=0,
        verbose_name="Maior Sequência",
        help_text="Longest streak of consecutive days"
    )
    last_activity_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Última Atividade",
        help_text="Date of last activity for streak tracking"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil do Usuário"
        verbose_name_plural = "Perfis dos Usuários"
        ordering = ['-xp_points']  # Order by XP for leaderboards
        indexes = [
            models.Index(fields=['-xp_points']),  # For leaderboard queries
        ]

    # Rank tiers configuration (XP thresholds)
    RANK_TIERS = [
        # (min_xp, rank_name, tier_number, color, icon)
        (0, "Latão", 0, "#CD7F32", "🥉"),
        (100, "Bronze III", 1, "#8B4513", "🥉"),
        (200, "Bronze II", 2, "#A0522D", "🥉"),
        (300, "Bronze I", 3, "#B87333", "🥉"),
        (500, "Prata III", 4, "#A8A8A8", "🥈"),
        (700, "Prata II", 5, "#B8B8B8", "🥈"),
        (900, "Prata I", 6, "#C0C0C0", "🥈"),
        (1200, "Ouro III", 7, "#DAA520", "🥇"),
        (1600, "Ouro II", 8, "#FFD700", "🥇"),
        (2000, "Ouro I", 9, "#FFA500", "🥇"),
        (2500, "Platina III", 10, "#0080FF", "💎"),
        (3200, "Platina II", 11, "#00A0FF", "💎"),
        (4000, "Platina I", 12, "#00BFFF", "💎"),
        (5000, "Diamante III", 13, "#00CED1", "💠"),
        (6500, "Diamante II", 14, "#40E0D0", "💠"),
        (8000, "Diamante I", 15, "#48D1CC", "💠"),
        (10000, "Mestre III", 16, "#9370DB", "👑"),
        (13000, "Mestre II", 17, "#8A2BE2", "👑"),
        (16000, "Mestre I", 18, "#9932CC", "👑"),
        (20000, "Grão-Mestre III", 19, "#FF00FF", "⭐"),
        (25000, "Grão-Mestre II", 20, "#FF1493", "⭐"),
        (30000, "Grão-Mestre I", 21, "#FF69B4", "⭐"),
        (40000, "Lenda", 22, "#FFD700", "🏆"),
    ]

    def __str__(self):
        return f"{self.user.username} - {self.rank_name} ({self.xp_points} XP)"

    @property
    def rank_data(self):
        """
        Get complete rank information for current XP.

        Returns:
            dict: Rank data including name, tier, color, icon, progress
        """
        current_rank = None
        next_rank = None

        for i, (min_xp, name, tier, color, icon) in enumerate(self.RANK_TIERS):
            if self.xp_points >= min_xp:
                current_rank = {
                    'min_xp': min_xp,
                    'name': name,
                    'tier': tier,
                    'color': color,
                    'icon': icon
                }
                # Get next rank if exists
                if i + 1 < len(self.RANK_TIERS):
                    next_min_xp, next_name, next_tier, next_color, next_icon = self.RANK_TIERS[i + 1]
                    next_rank = {
                        'min_xp': next_min_xp,
                        'name': next_name,
                        'tier': next_tier,
                        'color': next_color,
                        'icon': next_icon
                    }
            else:
                break

        # Calculate progress to next rank
        if current_rank and next_rank:
            xp_in_current_rank = self.xp_points - current_rank['min_xp']
            xp_needed_for_next = next_rank['min_xp'] - current_rank['min_xp']
            progress_percentage = min(100, (xp_in_current_rank / xp_needed_for_next) * 100)
        else:
            xp_in_current_rank = 0
            xp_needed_for_next = 0
            progress_percentage = 100  # Max rank achieved

        return {
            'current': current_rank or self.RANK_TIERS[0],
            'next': next_rank,
            'xp_in_current_rank': xp_in_current_rank,
            'xp_needed_for_next': xp_needed_for_next,
            'progress_percentage': round(progress_percentage, 2)
        }

    @property
    def rank_name(self):
        """Get current rank name based on XP."""
        return self.rank_data['current']['name']

    @property
    def rank_tier(self):
        """Get current rank tier number."""
        return self.rank_data['current']['tier']

    @property
    def rank_color(self):
        """Get current rank color."""
        return self.rank_data['current']['color']

    @property
    def rank_icon(self):
        """Get current rank icon."""
        return self.rank_data['current']['icon']

    @property
    def next_rank_name(self):
        """Get next rank name or None if at max rank."""
        next_rank = self.rank_data['next']
        return next_rank['name'] if next_rank else None

    @property
    def xp_for_next_rank(self):
        """Get XP needed to reach next rank."""
        return self.rank_data['xp_needed_for_next']

    @property
    def progress_to_next_rank(self):
        """Get progress percentage to next rank."""
        return self.rank_data['progress_percentage']

    # Legacy properties for backwards compatibility
    @property
    def level(self):
        """Legacy property - returns rank tier number."""
        return self.rank_tier

    @property
    def xp_for_current_level(self):
        """Legacy property - returns XP in current rank."""
        return self.rank_data['xp_in_current_rank']

    @property
    def xp_for_next_level(self):
        """Legacy property - returns XP needed for next rank."""
        return self.xp_for_next_rank

    @property
    def progress_to_next_level(self):
        """Legacy property - returns progress to next rank."""
        return self.progress_to_next_rank

    def update_streak(self):
        """
        Update user's activity streak.
        Call this when user completes an activity.

        Returns:
            dict: Streak information including milestone achievements
        """
        from django.utils import timezone
        today = timezone.now().date()

        streak_info = {
            'streak_continued': False,
            'streak_broken': False,
            'milestone_reached': None,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak
        }

        if self.last_activity_date == today:
            # Already active today, no change
            return streak_info

        if self.last_activity_date == today - timezone.timedelta(days=1):
            # Consecutive day - increment streak
            self.current_streak += 1
            streak_info['streak_continued'] = True
        else:
            # Streak broken or first activity
            if self.current_streak > 0:
                streak_info['streak_broken'] = True
            self.current_streak = 1

        # Update longest streak if needed
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        # Check for milestone achievements
        milestones = [7, 15, 30, 50, 100, 365]
        if self.current_streak in milestones:
            streak_info['milestone_reached'] = self.current_streak

        self.last_activity_date = today
        self.save(update_fields=['current_streak', 'longest_streak', 'last_activity_date', 'updated_at'])

        return streak_info

    def add_xp(self, amount):
        """
        Add experience points to user profile and update streak.

        Args:
            amount: Number of XP points to add

        Returns:
            dict: Information about rank changes and streak
                - old_rank: Rank name before adding XP
                - new_rank: Rank name after adding XP
                - rank_up: Whether user ranked up
                - new_xp: Total XP after addition
                - xp_gained: Amount of XP added
                - streak_info: Current streak information
        """
        old_rank_data = self.rank_data
        old_rank = old_rank_data['current']['name']

        self.xp_points += amount
        self.save(update_fields=['xp_points', 'updated_at'])

        new_rank_data = self.rank_data
        new_rank = new_rank_data['current']['name']

        # Update streak
        streak_info = self.update_streak()

        return {
            'old_rank': old_rank,
            'new_rank': new_rank,
            'rank_up': old_rank != new_rank,
            'new_xp': self.xp_points,
            'xp_gained': amount,
            'streak_info': streak_info,
            # Legacy fields for backwards compatibility
            'old_level': old_rank_data['current']['tier'],
            'new_level': new_rank_data['current']['tier'],
            'leveled_up': old_rank != new_rank
        }


class Achievement(models.Model):
    """
    Define available achievements/badges that users can earn.

    Achievements are awarded based on specific conditions like
    completing tracks, reaching levels, or earning XP milestones.
    """

    # Achievement types
    FIRST_STEP = 'first_step'
    TRACK_COMPLETE = 'track_complete'
    AREA_COMPLETE = 'area_complete'
    RANK_MILESTONE = 'rank_milestone'
    XP_MILESTONE = 'xp_milestone'
    STREAK_MILESTONE = 'streak_milestone'
    COURSE_BADGE = 'course_badge'

    ACHIEVEMENT_TYPES = (
        (FIRST_STEP, 'Primeiro Passo Completado'),
        (TRACK_COMPLETE, 'Trilha Completada'),
        (AREA_COMPLETE, 'Área Completada'),
        (RANK_MILESTONE, 'Marco de Rank'),
        (XP_MILESTONE, 'Marco de XP'),
        (STREAK_MILESTONE, 'Marco de Sequência'),
        (COURSE_BADGE, 'Badge de Curso'),
    )

    # Icon choices for UI selection
    ICON_CHOICES = [
        ('🏆', 'Troféu'),
        ('🥇', 'Medalha de Ouro'),
        ('🥈', 'Medalha de Prata'),
        ('🥉', 'Medalha de Bronze'),
        ('⭐', 'Estrela'),
        ('🌟', 'Estrela Brilhante'),
        ('💫', 'Estrelas Giratórias'),
        ('✨', 'Brilhos'),
        ('🎯', 'Alvo'),
        ('🎖️', 'Medalha Militar'),
        ('👑', 'Coroa'),
        ('💎', 'Diamante'),
        ('💠', 'Diamante com Ponto'),
        ('🔥', 'Fogo'),
        ('⚡', 'Raio'),
        ('🚀', 'Foguete'),
        ('🎓', 'Formatura'),
        ('📚', 'Livros'),
        ('📖', 'Livro Aberto'),
        ('✅', 'Check'),
        ('💯', '100 Pontos'),
        ('🎨', 'Arte'),
        ('🧠', 'Cérebro'),
        ('💪', 'Força'),
        ('🏅', 'Medalha Esportiva'),
        ('🌈', 'Arco-Íris'),
        ('🔱', 'Tridente'),
        ('⚔️', 'Espadas Cruzadas'),
        ('🛡️', 'Escudo'),
        ('🎪', 'Tenda de Circo'),
    ]

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Nome",
        help_text="Achievement name"
    )
    description = models.TextField(
        verbose_name="Descrição",
        help_text="Description of how to earn this achievement"
    )
    achievement_type = models.CharField(
        max_length=20,
        choices=ACHIEVEMENT_TYPES,
        db_index=True,
        verbose_name="Tipo",
        help_text="Type of achievement"
    )
    icon = models.CharField(
        max_length=50,
        default='🏆',
        verbose_name="Ícone",
        help_text="Emoji or icon identifier for this achievement"
    )
    xp_reward = models.PositiveIntegerField(
        default=0,
        verbose_name="Recompensa XP",
        help_text="Bonus XP awarded when earning this achievement"
    )
    # For track/area completion achievements
    related_track = models.ForeignKey(
        Trilha,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Trilha Relacionada",
        help_text="Track this achievement is for (if applicable)"
    )
    related_area = models.ForeignKey(
        Area,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Área Relacionada",
        help_text="Area this achievement is for (if applicable)"
    )
    # For milestone achievements
    required_value = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Valor Necessário",
        help_text="Required level/XP for milestone achievements"
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Ordem",
        help_text="Display order for achievements list"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Conquista"
        verbose_name_plural = "Conquistas"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['achievement_type']),
            models.Index(fields=['order']),
        ]

    def __str__(self):
        return f"{self.icon} {self.name}"

    def clean(self):
        """
        Validate achievement data.

        Ensures milestone achievements have required_value set.
        """
        super().clean()

        if self.achievement_type in [self.LEVEL_MILESTONE, self.XP_MILESTONE]:
            if not self.required_value:
                raise ValidationError(
                    f"{self.get_achievement_type_display()} achievements must have a required_value."
                )


class UserAchievement(models.Model):
    """
    Through model linking users to their earned achievements.

    Tracks when achievements were earned and if bonus XP was awarded.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name="Usuário"
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='earned_by',
        verbose_name="Conquista"
    )
    earned_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Conquistado em",
        help_text="When this achievement was earned"
    )
    xp_awarded = models.PositiveIntegerField(
        default=0,
        verbose_name="XP Concedido",
        help_text="Bonus XP awarded for this achievement"
    )

    class Meta:
        verbose_name = "Conquista do Usuário"
        verbose_name_plural = "Conquistas dos Usuários"
        unique_together = [['user', 'achievement']]  # Each achievement earned once per user
        ordering = ['-earned_at']
        indexes = [
            models.Index(fields=['user', '-earned_at']),
            models.Index(fields=['achievement']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"
