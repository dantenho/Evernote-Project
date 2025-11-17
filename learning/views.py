"""
API views for the learning app.

This module provides REST API endpoints for:
- User authentication (registration, profile management)
- Learning content access (areas, topics, tracks, steps)
- Progress tracking (viewing and updating user progress)
"""

from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError, NotFound
from django.contrib.auth.models import User
from django.db.models import Count, Q, Prefetch
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.cache import cache
import logging

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
    PassoSerializer,
)

# Initialize logger for error tracking
logger = logging.getLogger(__name__)


# ============================================================================
# Authentication Views
# ============================================================================

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.

    POST /api/v1/auth/register/
    Body: {
        "username": str,
        "password": str,
        "password2": str,
        "email": str,
        "first_name": str,
        "last_name": str
    }
    Returns: User data + JWT tokens
    """

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        """
        Create new user account and return JWT tokens.

        Args:
            request: HTTP request with user data

        Returns:
            Response: User data with access and refresh tokens

        Raises:
            ValidationError: If registration data is invalid
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Create user within transaction to ensure atomicity
            with transaction.atomic():
                user = serializer.save()

            # Generate JWT tokens for immediate authentication
            refresh = RefreshToken.for_user(user)

            logger.info(f"New user registered: {user.username}")

            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            logger.warning(f"Registration failed: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during registration: {str(e)}")
            return Response(
                {'detail': 'Registration failed. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for viewing and updating user profile.

    GET /api/v1/auth/profile/ - Retrieve profile
    PUT/PATCH /api/v1/auth/profile/ - Update profile

    Returns: User profile data
    """

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """
        Return the current authenticated user.

        Returns:
            User: Current user instance
        """
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        Update user profile with validation.

        Args:
            request: HTTP request with update data

        Returns:
            Response: Updated user data

        Raises:
            ValidationError: If update data is invalid
        """
        try:
            response = super().update(request, *args, **kwargs)
            logger.info(f"Profile updated for user: {request.user.username}")
            return response
        except ValidationError as e:
            logger.warning(f"Profile update failed for {request.user.username}: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating profile: {str(e)}")
            return Response(
                {'detail': 'Profile update failed. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    API endpoint for user logout (blacklist refresh token).

    POST /api/v1/auth/logout/
    Body: {"refresh": str}

    Returns: Success message

    Note: Requires JWT token blacklisting to be enabled in settings.
    """
    try:
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'detail': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Blacklist the refresh token
        token = RefreshToken(refresh_token)
        token.blacklist()

        logger.info(f"User logged out: {request.user.username}")

        return Response(
            {'detail': 'Successfully logged out.'},
            status=status.HTTP_200_OK
        )

    except AttributeError:
        # Token blacklisting not enabled
        logger.warning("Token blacklisting attempted but not enabled in settings")
        return Response(
            {'detail': 'Logout successful (token blacklisting disabled).'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Logout error for {request.user.username}: {str(e)}")
        return Response(
            {'detail': f'Logout failed: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================================================
# Learning Content Views
# ============================================================================

class LearningPathViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing learning paths (read-only).

    GET /api/v1/learning-paths/ - List all learning areas
    GET /api/v1/learning-paths/{id}/ - Retrieve specific area

    Returns: Hierarchical learning content (Area → Topic → Track → Step)

    Optimizations:
    - Prefetch all related data to prevent N+1 queries
    - Cache results for improved performance
    """

    serializer_class = AreaSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """
        Return optimized queryset with prefetched relationships.
        Uses select_related and prefetch_related to minimize database queries.
        Returns:
            QuerySet: Optimized Area queryset
        """
        # # Claude: Use a more descriptive cache key.
        # This makes it easier to identify this specific cache entry when
        # debugging or performing manual cache operations.
        cache_key = 'learning_paths:all'
        cached_queryset = cache.get(cache_key)

        if cached_queryset is not None:
            return cached_queryset

        # # Claude: Dynamically prefetch user progress only for authenticated users.
        # This avoids unnecessary database lookups for anonymous users while
        # still solving the N+1 problem for authenticated ones.
        user = self.request.user
        prerequisite_progress_prefetch = None
        if user.is_authenticated:
            prerequisite_progress_prefetch = Prefetch(
                'prerequisite__steps__user_progress',
                queryset=UserProgress.objects.filter(
                    user=user, status=UserProgress.COMPLETED
                ),
                to_attr='completed_prerequisite_steps'
            )

        # Build optimized queryset
        queryset = Area.objects.all().prefetch_related(
            Prefetch(
                'topics',
                queryset=Topico.objects.prefetch_related(
                    Prefetch(
                        'tracks',
                        queryset=Trilha.objects.select_related(
                            'prerequisite'
                        ).prefetch_related(
                            prerequisite_progress_prefetch,
                            Prefetch(
                                'steps',
                                queryset=Passo.objects.prefetch_related(
                                    'questions__choices'
                                )
                            )
                        ) if prerequisite_progress_prefetch else Trilha.objects.select_related(
                            'prerequisite'
                        ).prefetch_related(
                            Prefetch(
                                'steps',
                                queryset=Passo.objects.prefetch_related(
                                    'questions__choices'
                                )
                            )
                        )
                    )
                )
            )
        ).order_by('order', 'title')

        # Cache for 5 minutes
        cache.set(cache_key, queryset, 300)

        return queryset

    def list(self, request, *args, **kwargs):
        """
        List all learning areas with nested content.

        Args:
            request: HTTP request

        Returns:
            Response: Paginated list of learning areas
        """
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error fetching learning paths: {str(e)}")
            return Response(
                {'detail': 'Failed to fetch learning content.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================================
# User Progress Views
# ============================================================================


class UserProgressViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user progress management.

    GET /api/v1/progress/ - List user's progress records.
    POST /api/v1/progress/ - Create a progress record.
    GET /api/v1/progress/{id}/ - Retrieve a specific progress record.
    PUT/PATCH /api/v1/progress/{id}/ - Update a progress record.
    DELETE /api/v1/progress/{id}/ - Delete a progress record.
    GET /api/v1/progress/summary/ - Get progress statistics.
    POST /api/v1/progress/{step_id}/complete/ - Mark a step as completed.

    All operations are scoped to the authenticated user.
    """

    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        # # Claude: Use a more detailed serializer for list and retrieve actions.
        # This provides richer information to the frontend without requiring
        # separate endpoints, simplifying the API design.
        if self.action in ['list', 'retrieve']:
            return UserProgressDetailSerializer
        return UserProgressSerializer

    def get_queryset(self):
        """
        Return progress records for the current user only.

        Optimizes queries with select_related to prevent N+1 issues.

        Returns:
            QuerySet: User's progress records
        """
        # # Claude: The original my_progress view is now consolidated here.
        # This queryset is used for all actions, ensuring data is always
        # scoped to the authenticated user.
        return UserProgress.objects.filter(
            user=self.request.user
        ).select_related(
            'step',
            'step__track',
            'step__track__topic',
            'step__track__topic__area',
        ).order_by('-updated_at')

    def perform_create(self, serializer):
        """
        Automatically set the user to the current authenticated user.

        Args:
            serializer: Validated serializer instance

        Raises:
            ValidationError: If progress already exists for step
        """
        try:
            # # Claude: Ensure the user is always set to the request user for security.
            serializer.save(user=self.request.user)
            logger.info(
                f"Progress created for user {self.request.user.username} "
                f"on step {serializer.instance.step.id}"
            )
        except Exception as e:
            logger.error(f"Error creating progress: {str(e)}")
            raise ValidationError({'detail': 'Failed to create progress record.'})

    def perform_update(self, serializer):
        """
        Update progress record with logging.

        Args:
            serializer: Validated serializer instance
        """
        try:
            serializer.save()
            logger.info(
                f"Progress updated for user {self.request.user.username} "
                f"on step {serializer.instance.step.id}"
            )
        except Exception as e:
            logger.error(f"Error updating progress: {str(e)}")
            raise ValidationError({'detail': 'Failed to update progress record.'})

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get comprehensive progress summary statistics for the authenticated user.
        GET /api/v1/progress/summary/
        """
        user = request.user
        cache_key = f'progress_summary_{user.id}'

        cached_summary = cache.get(cache_key)
        if cached_summary:
            return Response(cached_summary)

        try:
            # # Claude: Optimized overall statistics.
            # This single aggregation query replaces three separate .count() calls,
            # significantly reducing database load.
            overall_stats = UserProgress.objects.filter(user=user).aggregate(
                total_started=Count('id'),
                total_completed=Count('id', filter=Q(status=UserProgress.COMPLETED)),
            )

            # # Claude: Optimized per-area statistics.
            # This single, annotated query replaces a loop that made multiple
            # queries per area, fixing a major N+1 performance issue.
            areas_data = Area.objects.annotate(
                total_steps=Count('topics__tracks__steps', distinct=True),
                completed_steps=Count(
                    'topics__tracks__steps__user_progress',
                    filter=Q(
                        topics__tracks__steps__user_progress__user=user,
                        topics__tracks__steps__user_progress__status=UserProgress.COMPLETED
                    ),
                    distinct=True
                ),
                in_progress_steps=Count(
                    'topics__tracks__steps__user_progress',
                    filter=Q(
                        topics__tracks__steps__user_progress__user=user,
                        topics__tracks__steps__user_progress__status=UserProgress.IN_PROGRESS
                    ),
                    distinct=True
                )
            ).values(
                'id', 'title', 'total_steps', 'completed_steps', 'in_progress_steps'
            )

            areas_progress = [
                {
                    **area,
                    'completion_percentage': round(
                        (area['completed_steps'] / area['total_steps'] * 100), 2
                    ) if area['total_steps'] > 0 else 0.0,
                }
                for area in areas_data
            ]

            total_completed = overall_stats.get('total_completed', 0)
            total_available_steps = sum(area['total_steps'] for area in areas_progress)
            overall_percentage = (
                (total_completed / total_available_steps * 100)
                if total_available_steps > 0 else 0
            )

            summary_data = {
                'total_steps': total_available_steps,
                'completed_steps': total_completed,
                'in_progress_steps': overall_stats.get('total_started', 0) - total_completed,
                'completion_percentage': round(overall_percentage, 2),
                'areas': areas_progress,
            }

            serializer = UserProgressSummarySerializer(summary_data)
            cache.set(cache_key, serializer.data, 120)

            logger.info(f"Progress summary generated for user {user.username}")
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error generating progress summary for {user.username}: {str(e)}")
            return Response(
                {'detail': 'Failed to generate progress summary.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StepViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for interacting with Steps.
    """
    queryset = Passo.objects.all()
    serializer_class = PassoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark a step as completed for the current user.
        POST /api/v1/steps/{step_id}/complete/
        """
        user = request.user
        step = self.get_object()

        try:
            with transaction.atomic():
                progress, created = UserProgress.objects.get_or_create(
                    user=user,
                    step=step,
                    defaults={'status': UserProgress.IN_PROGRESS}
                )
                progress.mark_as_completed()

            cache.delete(f'progress_summary_{user.id}')

            serializer = UserProgressSerializer(progress)
            logger.info(f"Step {step.id} completed by user {user.username}")
            return Response({
                'detail': 'Step marked as completed.',
                'progress': serializer.data,
                'created': created
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error completing step {step.id} for {user.username}: {e}")
            return Response(
                {'detail': 'Failed to mark step as completed.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
