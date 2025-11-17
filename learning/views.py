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
    UserProfile,
    Achievement,
    UserAchievement,
)
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    AreaSerializer,
    UserProgressSerializer,
    UserProgressDetailSerializer,
    CompleteStepSerializer,
    UserProgressSummarySerializer,
    UserProfileSerializer,
    AchievementSerializer,
    UserAchievementSerializer,
    UserAchievementSummarySerializer,
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
        # Check cache first
        cache_key = 'learning_paths_full'
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        # Build optimized queryset
        queryset = Area.objects.all().prefetch_related(
            # Prefetch topics with their tracks
            Prefetch(
                'topics',
                queryset=Topico.objects.select_related('area').prefetch_related(
                    # Prefetch tracks with their steps
                    Prefetch(
                        'tracks',
                        queryset=Trilha.objects.select_related('topic', 'prerequisite').prefetch_related(
                            # Prefetch steps with questions and choices
                            Prefetch(
                                'steps',
                                queryset=Passo.objects.select_related('track').prefetch_related(
                                    Prefetch('questions__choices')
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

    GET /api/v1/my-progress/ - List user's progress
    POST /api/v1/my-progress/ - Create progress record
    GET /api/v1/my-progress/{id}/ - Retrieve specific progress
    PUT/PATCH /api/v1/my-progress/{id}/ - Update progress
    DELETE /api/v1/my-progress/{id}/ - Delete progress
    GET /api/v1/my-progress/summary/ - Get progress statistics

    All operations are scoped to the authenticated user.
    """

    serializer_class = UserProgressSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Return progress records for the current user only.

        Optimizes queries with select_related to prevent N+1 issues.

        Returns:
            QuerySet: User's progress records
        """
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
        Get comprehensive progress summary statistics.

        GET /api/v1/my-progress/summary/

        Returns:
            Response: Progress statistics including:
                - Total steps attempted
                - Completed steps
                - In-progress steps
                - Completion percentage
                - Progress breakdown by area

        Optimizations:
        - Uses aggregated queries to minimize database hits
        - Caches results per user
        """
        user = request.user
        cache_key = f'progress_summary_{user.id}'

        # Check cache first
        cached_summary = cache.get(cache_key)
        if cached_summary:
            return Response(cached_summary)

        try:
            # Get user's progress queryset
            progress_queryset = UserProgress.objects.filter(user=user)

            # Calculate overall statistics
            total_progress = progress_queryset.count()
            completed = progress_queryset.filter(
                status=UserProgress.COMPLETED
            ).count()
            in_progress = progress_queryset.filter(
                status=UserProgress.IN_PROGRESS
            ).count()

            # Calculate completion percentage based on progress records
            completion_percentage = (
                (completed / total_progress * 100) if total_progress > 0 else 0
            )

            # Get progress by area
            areas_progress = []
            for area in Area.objects.all():
                # Count steps in this area
                steps_in_area = Passo.objects.filter(
                    track__topic__area=area
                ).count()

                # Count completed and in-progress steps
                completed_in_area = progress_queryset.filter(
                    step__track__topic__area=area,
                    status=UserProgress.COMPLETED
                ).count()

                in_progress_in_area = progress_queryset.filter(
                    step__track__topic__area=area,
                    status=UserProgress.IN_PROGRESS
                ).count()

                # Calculate area completion percentage
                area_completion = (
                    (completed_in_area / steps_in_area * 100)
                    if steps_in_area > 0 else 0
                )

                areas_progress.append({
                    'id': area.id,
                    'title': area.title,
                    'total_steps': steps_in_area,
                    'completed_steps': completed_in_area,
                    'in_progress_steps': in_progress_in_area,
                    'completion_percentage': round(area_completion, 2),
                })

            # Build summary response
            summary_data = {
                'total_steps': total_progress,
                'completed_steps': completed,
                'in_progress_steps': in_progress,
                'completion_percentage': round(completion_percentage, 2),
                'areas': areas_progress,
            }

            # Validate with serializer
            serializer = UserProgressSummarySerializer(summary_data)

            # Cache for 2 minutes
            cache.set(cache_key, serializer.data, 120)

            logger.info(f"Progress summary generated for user {user.username}")

            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error generating progress summary: {str(e)}")
            return Response(
                {'detail': 'Failed to generate progress summary.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_step(request, step_id):
    """
    Mark a step as completed for the current user.

    POST /api/v1/steps/<step_id>/complete/

    Args:
        request: HTTP request
        step_id: ID of the step to complete

    Returns:
        Response: Success message with progress data

    Raises:
        NotFound: If step doesn't exist
        ValidationError: If completion fails

    Notes:
    - Creates progress record if it doesn't exist
    - Idempotent: calling multiple times won't duplicate completion
    - Invalidates progress summary cache
    """
    user = request.user

    try:
        # Validate step exists
        step = get_object_or_404(Passo, id=step_id)

        # Track if this is the first completion for XP calculation
        was_already_completed = False

        # Get or create progress record
        with transaction.atomic():
            progress, created = UserProgress.objects.get_or_create(
                user=user,
                step=step,
                defaults={'status': UserProgress.IN_PROGRESS}
            )

            # Check if already completed before marking
            was_already_completed = progress.status == UserProgress.COMPLETED

            # Mark as completed (idempotent)
            progress.mark_as_completed()

            # Award XP only if this is the first completion (not re-completing)
            xp_info = None
            if not was_already_completed:
                XP_PER_STEP = 10  # Base XP reward for completing a step
                xp_info = user.profile.add_xp(XP_PER_STEP)

                logger.info(
                    f"XP awarded: {user.username} earned {XP_PER_STEP} XP for completing step {step_id}. "
                    f"Total XP: {xp_info['new_xp']}, Level: {xp_info['new_level']}"
                )

                # Check if user leveled up
                if xp_info['leveled_up']:
                    logger.info(
                        f"LEVEL UP! {user.username} reached level {xp_info['new_level']}"
                    )

        # Invalidate progress summary cache
        cache_key = f'progress_summary_{user.id}'
        cache.delete(cache_key)

        # Serialize response
        serializer = UserProgressSerializer(progress, context={'request': request})

        logger.info(
            f"Step {step_id} {'initially ' if created else ''}completed "
            f"by user {user.username}"
        )

        # Build response with XP information
        response_data = {
            'detail': 'Step marked as completed.',
            'progress': serializer.data,
            'created': created,
        }

        # Add XP information if awarded
        if xp_info:
            response_data['xp_earned'] = xp_info['xp_gained']
            response_data['total_xp'] = xp_info['new_xp']
            response_data['level'] = xp_info['new_level']
            response_data['leveled_up'] = xp_info['leveled_up']

        return Response(response_data, status=status.HTTP_200_OK)

    except Passo.DoesNotExist:
        logger.warning(f"User {user.username} attempted to complete non-existent step {step_id}")
        raise NotFound('Step does not exist.')
    except Exception as e:
        logger.error(f"Error completing step {step_id} for user {user.username}: {str(e)}")
        return Response(
            {'detail': 'Failed to mark step as completed.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_progress(request):
    """
    Get all progress records for the current user.

    GET /api/v1/my-progress/

    Returns:
        Response: List of progress records with full step details

    Optimizations:
    - Uses select_related to prevent N+1 queries
    - Orders by most recently updated
    - Includes full step data for frontend display
    """
    try:
        # Get progress with optimized queries
        progress = UserProgress.objects.filter(
            user=request.user
        ).select_related(
            'step',
            'step__track',
            'step__track__topic',
            'step__track__topic__area',
        ).order_by('-updated_at')

        # Serialize with detailed step information
        serializer = UserProgressDetailSerializer(
            progress,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Error fetching progress for user {request.user.username}: {str(e)}")
        return Response(
            {'detail': 'Failed to fetch progress data.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# Gamification Views
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_achievements(request):
    """
    Get all achievements earned by the current user.

    GET /api/v1/my-achievements/

    Returns:
        Response: User's earned achievements with summary statistics

    Response format:
        {
            "total_achievements": int,      # Total achievements available
            "earned_achievements": int,     # Number earned by user
            "completion_percentage": float, # Percentage earned
            "recent_achievements": [        # List of earned achievements
                {
                    "id": int,
                    "achievement": {...},   # Achievement details
                    "earned_at": datetime,
                    "xp_awarded": int
                }
            ]
        }
    """
    try:
        user = request.user

        # Get user's earned achievements
        user_achievements = UserAchievement.objects.filter(
            user=user
        ).select_related(
            'achievement',
            'achievement__related_track',
            'achievement__related_area'
        ).order_by('-earned_at')

        # Get total achievements count
        total_achievements = Achievement.objects.count()
        earned_count = user_achievements.count()

        # Calculate completion percentage
        completion_percentage = (
            round((earned_count / total_achievements) * 100, 2)
            if total_achievements > 0 else 0.0
        )

        # Build summary response
        summary_data = {
            'total_achievements': total_achievements,
            'earned_achievements': earned_count,
            'completion_percentage': completion_percentage,
            'recent_achievements': UserAchievementSerializer(
                user_achievements,
                many=True,
                context={'request': request}
            ).data
        }

        logger.info(f"Achievement list fetched for user {user.username}")

        return Response(summary_data)

    except Exception as e:
        logger.error(f"Error fetching achievements for user {request.user.username}: {str(e)}")
        return Response(
            {'detail': 'Failed to fetch achievements data.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def available_achievements(request):
    """
    Get list of all available achievements in the system.

    GET /api/v1/achievements/

    Returns:
        Response: List of all achievements with details

    Note: This is a public endpoint to show users what achievements they can earn
    """
    try:
        # Get all achievements ordered by order field
        achievements = Achievement.objects.all().select_related(
            'related_track',
            'related_area'
        ).order_by('order', 'name')

        serializer = AchievementSerializer(
            achievements,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Error fetching available achievements: {str(e)}")
        return Response(
            {'detail': 'Failed to fetch achievements.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_gamification(request):
    """
    Get current user's gamification profile.

    GET /api/v1/profile/gamification/

    Returns:
        Response: User profile with XP, level, and progress data

    Response format:
        {
            "id": int,
            "xp_points": int,
            "level": int,
            "xp_for_current_level": int,
            "xp_for_next_level": int,
            "progress_to_next_level": float,
            "created_at": datetime,
            "updated_at": datetime
        }
    """
    try:
        user = request.user
        profile = user.profile

        serializer = UserProfileSerializer(profile, context={'request': request})

        return Response(serializer.data)

    except UserProfile.DoesNotExist:
        logger.error(f"Profile not found for user {user.username}")
        return Response(
            {'detail': 'User profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error fetching gamification profile for user {request.user.username}: {str(e)}")
        return Response(
            {'detail': 'Failed to fetch profile data.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
