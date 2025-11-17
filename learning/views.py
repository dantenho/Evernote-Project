"""
API views for the learning app.
"""
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db.models import Count, Q, Prefetch
from django.shortcuts import get_object_or_404

from .models import (
    Area,
    Topico,
    Trilha,
    Passo,
    UserProgress,
)
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    AreaSerializer,
    UserProgressSerializer,
    UserProgressDetailSerializer,
    CompleteStepSerializer,
    UserProgressSummarySerializer,
)


# Authentication Views

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    POST /api/v1/auth/register/
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for viewing and updating user profile.
    GET/PUT/PATCH /api/v1/auth/profile/
    """
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    API endpoint for user logout (blacklist refresh token).
    POST /api/v1/auth/logout/
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'detail': 'Successfully logged out.'},
                status=status.HTTP_200_OK
            )
        return Response(
            {'detail': 'Refresh token is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'detail': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


# Learning Content Views

class LearningPathViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing learning paths.
    GET /api/v1/learning-paths/
    """
    queryset = Area.objects.all().prefetch_related(
        'topics',
        'topics__tracks',
        'topics__tracks__steps',
        'topics__tracks__steps__questions',
        'topics__tracks__steps__questions__choices',
    )
    serializer_class = AreaSerializer
    permission_classes = (AllowAny,)


# User Progress Views

class UserProgressViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user progress.
    GET /api/v1/my-progress/
    POST /api/v1/my-progress/
    """
    serializer_class = UserProgressSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return progress for the current user only."""
        return UserProgress.objects.filter(user=self.request.user).select_related(
            'step',
            'step__track',
            'step__track__topic',
            'step__track__topic__area',
        )

    def perform_create(self, serializer):
        """Automatically set the user to the current user."""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get user progress summary statistics.
        GET /api/v1/my-progress/summary/
        """
        user = request.user
        progress_queryset = UserProgress.objects.filter(user=user)

        total_steps_in_db = Passo.objects.count()
        total_progress = progress_queryset.count()
        completed = progress_queryset.filter(status=UserProgress.COMPLETED).count()
        in_progress = progress_queryset.filter(status=UserProgress.IN_PROGRESS).count()

        # Calculate completion percentage based on actual progress
        completion_percentage = (
            (completed / total_progress * 100) if total_progress > 0 else 0
        )

        # Get progress by area
        areas_progress = []
        for area in Area.objects.all():
            steps_in_area = Passo.objects.filter(
                track__topic__area=area
            ).count()

            completed_in_area = progress_queryset.filter(
                step__track__topic__area=area,
                status=UserProgress.COMPLETED
            ).count()

            in_progress_in_area = progress_queryset.filter(
                step__track__topic__area=area,
                status=UserProgress.IN_PROGRESS
            ).count()

            area_completion = (
                (completed_in_area / steps_in_area * 100) if steps_in_area > 0 else 0
            )

            areas_progress.append({
                'id': area.id,
                'title': area.title,
                'total_steps': steps_in_area,
                'completed_steps': completed_in_area,
                'in_progress_steps': in_progress_in_area,
                'completion_percentage': round(area_completion, 2),
            })

        summary_data = {
            'total_steps': total_progress,
            'completed_steps': completed,
            'in_progress_steps': in_progress,
            'completion_percentage': round(completion_percentage, 2),
            'areas': areas_progress,
        }

        serializer = UserProgressSummarySerializer(summary_data)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_step(request, step_id):
    """
    Mark a step as completed for the current user.
    POST /api/v1/steps/<step_id>/complete/
    """
    user = request.user
    step = get_object_or_404(Passo, id=step_id)

    # Get or create progress for this step
    progress, created = UserProgress.objects.get_or_create(
        user=user,
        step=step,
        defaults={'status': UserProgress.IN_PROGRESS}
    )

    # Mark as completed
    progress.mark_as_completed()

    serializer = UserProgressSerializer(progress)
    return Response({
        'detail': 'Step marked as completed.',
        'progress': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_progress(request):
    """
    Get all progress for the current user.
    GET /api/v1/my-progress/
    """
    progress = UserProgress.objects.filter(
        user=request.user
    ).select_related(
        'step',
        'step__track',
        'step__track__topic',
        'step__track__topic__area',
    ).order_by('-updated_at')

    serializer = UserProgressDetailSerializer(progress, many=True)
    return Response(serializer.data)
