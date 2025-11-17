"""
Serializers for the learning app API.

This module provides REST framework serializers for converting model instances
to/from JSON, with validation and nested relationships.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.validators import UniqueValidator

from .models import (
    Area,
    Topico,
    Trilha,
    Passo,
    Questao,
    Alternativa,
    UserProgress,
    UserProfile,
    Achievement,
    UserAchievement,
)


# ============================================================================
# Gamification Serializers (defined early for use in UserSerializer)
# ============================================================================

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile with gamification data.

    Includes XP points, calculated level, and progress to next level.
    """

    level = serializers.IntegerField(
        read_only=True,
        help_text="User level calculated from XP (level = xp // 100)"
    )
    xp_for_current_level = serializers.IntegerField(
        read_only=True,
        help_text="XP earned in current level (0-99)"
    )
    xp_for_next_level = serializers.IntegerField(
        read_only=True,
        help_text="XP needed to reach next level"
    )
    progress_to_next_level = serializers.FloatField(
        read_only=True,
        help_text="Progress percentage to next level (0-100)"
    )

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'xp_points',
            'level',
            'xp_for_current_level',
            'xp_for_next_level',
            'progress_to_next_level',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'xp_points', 'created_at', 'updated_at')


# ============================================================================
# Authentication Serializers
# ============================================================================

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Validates password matching and enforces Django's password validation rules.
    Creates new user accounts with hashed passwords.
    """

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="A user with this email already exists."
        )]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text="Password must meet Django's validation requirements"
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Enter the same password again for verification"
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {
                'required': True,
                'allow_blank': False,
                'help_text': "User's first name"
            },
            'last_name': {
                'required': True,
                'allow_blank': False,
                'help_text': "User's last name"
            },
            'username': {
                'help_text': "Unique username for login"
            }
        }

    def validate(self, attrs):
        """
        Validate that passwords match.

        Args:
            attrs: Dictionary of attribute values

        Returns:
            dict: Validated attributes

        Raises:
            ValidationError: If passwords don't match
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs

    def validate_username(self, value):
        """
        Validate username format.

        Args:
            value: Username string

        Returns:
            str: Validated username

        Raises:
            ValidationError: If username is invalid
        """
        if len(value) < 3:
            raise serializers.ValidationError(
                "Username must be at least 3 characters long."
            )
        return value

    def create(self, validated_data):
        """
        Create a new user with hashed password.

        Args:
            validated_data: Validated data from serializer

        Returns:
            User: Newly created user instance
        """
        # Remove password2 as it's not needed for user creation
        validated_data.pop('password2')

        # Create user with hashed password
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.

    Provides read and update access to user profile data.
    Username and date_joined are read-only.
    Includes gamification profile with XP and level.
    """

    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'profile')
        read_only_fields = ('id', 'username', 'date_joined', 'profile')

    def validate_email(self, value):
        """
        Validate that email is unique (excluding current user).

        Args:
            value: Email address

        Returns:
            str: Validated email

        Raises:
            ValidationError: If email is already in use
        """
        user = self.context.get('request').user if self.context.get('request') else None
        if user and User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value


# ============================================================================
# Learning Content Serializers
# ============================================================================

class AlternativaSerializer(serializers.ModelSerializer):
    """
    Serializer for quiz answer choices.

    Note: is_correct field should be filtered in views based on user permissions.
    Regular users should not see correct answers before submitting.
    """

    class Meta:
        model = Alternativa
        fields = ('id', 'text', 'is_correct', 'order')
        read_only_fields = ('id',)

    def to_representation(self, instance):
        """
        Customize representation based on context.

        Hide is_correct for unauthenticated or non-admin users
        unless quiz has been submitted.
        """
        representation = super().to_representation(instance)

        # Check if we should hide the correct answer
        request = self.context.get('request')
        hide_correct = self.context.get('hide_correct_answers', False)

        if hide_correct and not (request and request.user.is_staff):
            representation.pop('is_correct', None)

        return representation


class QuestaoSerializer(serializers.ModelSerializer):
    """
    Serializer for quiz questions with multiple choice answers.

    Includes all choices for the question, ordered appropriately.
    """

    choices = AlternativaSerializer(many=True, read_only=True)

    class Meta:
        model = Questao
        fields = ('id', 'text', 'explanation', 'order', 'choices')
        read_only_fields = ('id',)

    def validate(self, attrs):
        """
        Validate question data.

        Ensures question belongs to a quiz-type step.
        """
        if self.instance:
            try:
                self.instance.full_clean()
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.message_dict)
        return attrs


class PassoSerializer(serializers.ModelSerializer):
    """
    Serializer for learning steps (lessons and quizzes).

    Includes nested questions for quiz-type steps.
    Content varies based on step type.
    """

    questions = QuestaoSerializer(many=True, read_only=True)

    class Meta:
        model = Passo
        fields = (
            'id',
            'title',
            'content_type',
            'text_content',
            'video_url',
            'estimated_time',
            'order',
            'questions',
        )
        read_only_fields = ('id',)

    def validate(self, attrs):
        """
        Validate step data.

        Ensures lessons have content (text or video).
        """
        if self.instance:
            try:
                self.instance.full_clean()
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.message_dict)
        return attrs

    def to_representation(self, instance):
        """
        Customize representation based on content type.

        For quizzes, include questions with potentially hidden answers.
        """
        representation = super().to_representation(instance)

        # Pass context to nested serializers
        if instance.content_type == Passo.QUIZ:
            # Create context for hiding correct answers before submission
            context = self.context.copy()
            context['hide_correct_answers'] = context.get('hide_quiz_answers', False)

            # Re-serialize questions with updated context
            questions_serializer = QuestaoSerializer(
                instance.questions.all(),
                many=True,
                context=context
            )
            representation['questions'] = questions_serializer.data

        return representation


class TrilhaSerializer(serializers.ModelSerializer):
    """
    Serializer for learning tracks.

    A track is a collection of related steps within a topic.
    Includes information about prerequisites if applicable.
    """

    steps = PassoSerializer(many=True, read_only=True)
    is_unlocked = serializers.SerializerMethodField()

    class Meta:
        model = Trilha
        fields = ('id', 'title', 'description', 'order', 'prerequisite', 'steps', 'is_unlocked')
        read_only_fields = ('id',)

    def get_is_unlocked(self, obj):
        """
        Check if track is unlocked for the current user.

        Args:
            obj: Trilha instance

        Returns:
            bool: True if unlocked, False otherwise
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return True  # Allow viewing for unauthenticated users

        return obj.is_unlocked_for_user(request.user)


class TopicoSerializer(serializers.ModelSerializer):
    """
    Serializer for learning topics.

    A topic contains multiple tracks and belongs to an area.
    """

    tracks = TrilhaSerializer(many=True, read_only=True)

    class Meta:
        model = Topico
        fields = ('id', 'title', 'description', 'order', 'tracks')
        read_only_fields = ('id',)


class AreaSerializer(serializers.ModelSerializer):
    """
    Serializer for top-level learning areas.

    An area contains multiple topics and represents the highest
    level of content organization.
    """

    topics = TopicoSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ('id', 'title', 'description', 'order', 'topics')
        read_only_fields = ('id',)


# ============================================================================
# User Progress Serializers
# ============================================================================

class UserProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for user progress records.

    Tracks a user's progress through individual learning steps,
    including status and completion timestamp.
    """

    step_title = serializers.CharField(source='step.title', read_only=True)
    step_type = serializers.CharField(source='step.content_type', read_only=True)
    track_title = serializers.CharField(source='step.track.title', read_only=True)

    class Meta:
        model = UserProgress
        fields = (
            'id',
            'step',
            'step_title',
            'step_type',
            'track_title',
            'status',
            'completed_at',
            'attempts',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'completed_at')

    def validate(self, attrs):
        """
        Validate progress data.

        Ensures user cannot have duplicate progress for same step.
        """
        user = self.context['request'].user
        step = attrs.get('step')

        if not self.instance and step:
            # Check for existing progress
            if UserProgress.objects.filter(user=user, step=step).exists():
                raise serializers.ValidationError({
                    'step': 'Progress already exists for this step.'
                })

        return attrs


class UserProgressDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for user progress with full step information.

    Includes complete step data with questions and content.
    """

    step = PassoSerializer(read_only=True)

    class Meta:
        model = UserProgress
        fields = (
            'id',
            'step',
            'status',
            'completed_at',
            'attempts',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class CompleteStepSerializer(serializers.Serializer):
    """
    Serializer for marking a step as complete.

    Validates step existence and handles completion logic.
    """

    step_id = serializers.IntegerField(
        help_text="ID of the step to mark as complete"
    )

    def validate_step_id(self, value):
        """
        Validate that the step exists.

        Args:
            value: Step ID

        Returns:
            int: Validated step ID

        Raises:
            ValidationError: If step doesn't exist
        """
        try:
            Passo.objects.get(id=value)
        except Passo.DoesNotExist:
            raise serializers.ValidationError("Step does not exist.")
        return value


class QuizSubmissionSerializer(serializers.Serializer):
    """
    Serializer for quiz answer submissions.

    Validates submitted answers and calculates score.
    """

    answers = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Dictionary mapping question_id to choice_id"
    )

    def validate_answers(self, value):
        """
        Validate that all answers correspond to valid questions and choices.

        Args:
            value: Dictionary of answers

        Returns:
            dict: Validated answers

        Raises:
            ValidationError: If any answer is invalid
        """
        for question_id, choice_id in value.items():
            # Validate question exists
            try:
                question = Questao.objects.get(id=question_id)
            except Questao.DoesNotExist:
                raise serializers.ValidationError(
                    f"Question with id {question_id} does not exist."
                )

            # Validate choice belongs to question
            if not question.choices.filter(id=choice_id).exists():
                raise serializers.ValidationError(
                    f"Choice with id {choice_id} does not belong to question {question_id}."
                )

        return value


class UserProgressSummarySerializer(serializers.Serializer):
    """
    Serializer for user progress summary statistics.

    Provides aggregate data about user's overall learning progress,
    broken down by area.
    """

    total_steps = serializers.IntegerField(
        help_text="Total number of steps user has started"
    )
    completed_steps = serializers.IntegerField(
        help_text="Number of steps marked as complete"
    )
    in_progress_steps = serializers.IntegerField(
        help_text="Number of steps currently in progress"
    )
    completion_percentage = serializers.FloatField(
        help_text="Overall completion rate as percentage"
    )
    areas = serializers.ListField(
        child=serializers.DictField(),
        help_text="Progress breakdown by learning area"
    )


# ============================================================================
# Achievement Serializers
# ============================================================================

class AchievementSerializer(serializers.ModelSerializer):
    """
    Serializer for available achievements.

    Shows achievement details including type, requirements, and rewards.
    """

    achievement_type_display = serializers.CharField(
        source='get_achievement_type_display',
        read_only=True,
        help_text="Human-readable achievement type"
    )

    class Meta:
        model = Achievement
        fields = (
            'id',
            'name',
            'description',
            'achievement_type',
            'achievement_type_display',
            'icon',
            'xp_reward',
            'related_track',
            'related_area',
            'required_value',
            'order',
        )
        read_only_fields = ('id',)


class UserAchievementSerializer(serializers.ModelSerializer):
    """
    Serializer for user's earned achievements.

    Includes achievement details and when it was earned.
    """

    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = (
            'id',
            'achievement',
            'earned_at',
            'xp_awarded',
        )
        read_only_fields = ('id', 'earned_at', 'xp_awarded')


class UserAchievementSummarySerializer(serializers.Serializer):
    """
    Serializer for user achievement statistics.

    Provides summary of earned achievements and progress.
    """

    total_achievements = serializers.IntegerField(
        help_text="Total number of achievements available"
    )
    earned_achievements = serializers.IntegerField(
        help_text="Number of achievements earned by user"
    )
    completion_percentage = serializers.FloatField(
        help_text="Percentage of achievements earned"
    )
    recent_achievements = UserAchievementSerializer(
        many=True,
        help_text="Recently earned achievements"
    )
