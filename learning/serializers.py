"""
Serializers for the learning app API.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

from .models import (
    Area,
    Topico,
    Trilha,
    Passo,
    Questao,
    Alternativa,
    UserProgress,
)


# Authentication Serializers

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'username', 'date_joined')


# Learning Content Serializers

class AlternativaSerializer(serializers.ModelSerializer):
    """Serializer for quiz alternatives."""

    class Meta:
        model = Alternativa
        fields = ('id', 'text', 'is_correct')
        # Don't expose is_correct to non-admin users in actual API calls
        # This can be controlled in the view


class QuestaoSerializer(serializers.ModelSerializer):
    """Serializer for quiz questions."""

    choices = AlternativaSerializer(many=True, read_only=True)

    class Meta:
        model = Questao
        fields = ('id', 'text', 'choices')


class PassoSerializer(serializers.ModelSerializer):
    """Serializer for learning steps."""

    questions = QuestaoSerializer(many=True, read_only=True)

    class Meta:
        model = Passo
        fields = (
            'id',
            'title',
            'content_type',
            'text_content',
            'video_url',
            'order',
            'questions',
        )


class TrilhaSerializer(serializers.ModelSerializer):
    """Serializer for learning tracks."""

    steps = PassoSerializer(many=True, read_only=True)

    class Meta:
        model = Trilha
        fields = ('id', 'title', 'order', 'steps')


class TopicoSerializer(serializers.ModelSerializer):
    """Serializer for topics."""

    tracks = TrilhaSerializer(many=True, read_only=True)

    class Meta:
        model = Topico
        fields = ('id', 'title', 'order', 'tracks')


class AreaSerializer(serializers.ModelSerializer):
    """Serializer for learning areas."""

    topics = TopicoSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ('id', 'title', 'order', 'topics')


# User Progress Serializers

class UserProgressSerializer(serializers.ModelSerializer):
    """Serializer for user progress."""

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
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class UserProgressDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for user progress with nested step information."""

    step = PassoSerializer(read_only=True)

    class Meta:
        model = UserProgress
        fields = (
            'id',
            'step',
            'status',
            'completed_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class CompleteStepSerializer(serializers.Serializer):
    """Serializer for completing a step."""

    step_id = serializers.IntegerField()

    def validate_step_id(self, value):
        """Validate that the step exists."""
        if not Passo.objects.filter(id=value).exists():
            raise serializers.ValidationError("Step does not exist.")
        return value


class UserProgressSummarySerializer(serializers.Serializer):
    """Serializer for user progress summary statistics."""

    total_steps = serializers.IntegerField()
    completed_steps = serializers.IntegerField()
    in_progress_steps = serializers.IntegerField()
    completion_percentage = serializers.FloatField()
    areas = serializers.ListField(child=serializers.DictField())
