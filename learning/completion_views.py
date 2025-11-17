"""
Views for handling track and topic completions with new XP system.

New XP Structure:
- Step completion: Variable XP (default 10)
- Track completion: 100 XP
- Topic completion: 1000 XP bonus
"""

import logging
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    Trilha, Topico, Passo, UserProgress,
    UserProfile
)

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_track(request, track_id):
    """
    Mark a track as completed and award 100 XP.

    Automatically checks if user completed all steps in track.
    Awards 100 XP on first completion.
    Checks if this completes a topic for bonus 1000 XP.

    POST /api/v1/tracks/{track_id}/complete/

    Returns:
        {
            "track_completed": true,
            "xp_awarded": 100,
            "total_xp": 1500,
            "new_rank": "Bronze II",
            "topic_completed": false,  // or true with topic_bonus_xp
            "topic_bonus_xp": 1000,     // if topic completed
            "celebration": "track"|"topic"  // which celebration to show
        }
    """
    user = request.user

    try:
        # Get track
        track = get_object_or_404(Trilha, id=track_id)

        # Check if all steps completed
        total_steps = track.steps.count()
        completed_steps = UserProgress.objects.filter(
            user=user,
            step__track=track,
            status=UserProgress.COMPLETED
        ).count()

        if completed_steps < total_steps:
            return Response({
                'detail': f'Complete all {total_steps} steps first. You have completed {completed_steps}.',
                'completed_steps': completed_steps,
                'total_steps': total_steps,
                'remaining_steps': total_steps - completed_steps
            }, status=status.HTTP_400_BAD_REQUEST)

        # Use transaction to ensure atomicity
        with transaction.atomic():
            # Check if already completed
            from .models import UserTrackCompletion
            completion, created = UserTrackCompletion.objects.get_or_create(
                user=user,
                track=track,
                defaults={'xp_awarded': track.xp_reward or 100}
            )

            if not created:
                return Response({
                    'detail': 'Track already completed',
                    'completed_at': completion.completed_at,
                    'xp_awarded': 0,
                    'total_xp': user.profile.xp_points
                }, status=status.HTTP_200_OK)

            # Award track XP
            track_xp = track.xp_reward or 100
            xp_info = user.profile.add_xp(track_xp)

            # Update completion count
            user.profile.tracks_completed_count += 1
            user.profile.save()

            # Check if this completes the topic
            topic = track.topic
            topic_completed = False
            topic_bonus_xp = 0
            celebration_type = 'track'

            # Get all tracks in topic
            total_tracks_in_topic = topic.tracks.count()
            completed_tracks_in_topic = UserTrackCompletion.objects.filter(
                user=user,
                track__topic=topic
            ).count()

            # Topic is complete if all tracks are done
            if completed_tracks_in_topic == total_tracks_in_topic:
                # Check if topic already marked complete
                from .models import UserTopicCompletion
                topic_completion, topic_created = UserTopicCompletion.objects.get_or_create(
                    user=user,
                    topic=topic,
                    defaults={
                        'xp_awarded': topic.bonus_xp_reward or 1000,
                        'tracks_completed': completed_tracks_in_topic,
                        'completion_percentage': 100.0
                    }
                )

                if topic_created:
                    # Award bonus XP for completing topic!
                    topic_bonus_xp = topic.bonus_xp_reward or 1000
                    topic_xp_info = user.profile.add_xp(topic_bonus_xp)

                    # Update totals
                    user.profile.topics_completed_count += 1
                    user.profile.total_bonus_xp += topic_bonus_xp
                    user.profile.save()

                    topic_completed = True
                    celebration_type = 'topic'  # Show bigger celebration!

                    # Invalidate cache
                    cache.delete(f'progress_summary_{user.id}')

                    logger.info(
                        f"🎉 TOPIC COMPLETED! {user.username} finished '{topic.title}' "
                        f"and earned {topic_bonus_xp} bonus XP!"
                    )

        # Build response
        response_data = {
            'track_completed': True,
            'track_title': track.title,
            'xp_awarded': track_xp,
            'total_xp': user.profile.xp_points,
            'current_rank': user.profile.rank_data['current']['name'],
            'rank_tier': user.profile.rank_data['current']['tier'],
            'leveled_up': xp_info.get('leveled_up', False),
            'celebration': celebration_type
        }

        # Add topic completion data if applicable
        if topic_completed:
            response_data.update({
                'topic_completed': True,
                'topic_title': topic.title,
                'topic_bonus_xp': topic_bonus_xp,
                'topics_completed_total': user.profile.topics_completed_count,
                'confetti_level': 'max'  # Trigger maximum celebration!
            })
        else:
            response_data.update({
                'topic_completed': False,
                'topic_progress': {
                    'completed_tracks': completed_tracks_in_topic,
                    'total_tracks': total_tracks_in_topic,
                    'percentage': round((completed_tracks_in_topic / total_tracks_in_topic) * 100, 1)
                }
            })

        logger.info(
            f"Track completed: {user.username} finished '{track.title}' "
            f"and earned {track_xp} XP"
        )

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error completing track: {str(e)}")
        return Response({
            'detail': 'Failed to complete track. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def track_progress(request, track_id):
    """
    Get user's progress on a specific track.

    GET /api/v1/tracks/{track_id}/progress/

    Returns:
        {
            "track_id": 1,
            "track_title": "Python Basics",
            "total_steps": 10,
            "completed_steps": 7,
            "percentage": 70.0,
            "is_completed": false,
            "xp_reward": 100,
            "time_spent_seconds": 1800,
            "steps": [
                {
                    "step_id": 1,
                    "title": "Variables",
                    "completed": true,
                    "completed_at": "2025-01-15T10:30:00Z"
                }
            ]
        }
    """
    user = request.user

    try:
        track = get_object_or_404(Trilha, id=track_id)

        # Get all steps in track
        steps = track.steps.all().order_by('order')

        # Get user's progress on these steps
        progress_records = UserProgress.objects.filter(
            user=user,
            step__in=steps
        ).select_related('step')

        # Build progress map
        progress_map = {p.step_id: p for p in progress_records}

        # Calculate stats
        total_steps = steps.count()
        completed_steps = sum(
            1 for p in progress_records
            if p.status == UserProgress.COMPLETED
        )
        percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0

        # Check if track completed
        from .models import UserTrackCompletion
        track_completion = UserTrackCompletion.objects.filter(
            user=user,
            track=track
        ).first()

        # Build step details
        step_details = []
        for step in steps:
            progress = progress_map.get(step.id)
            step_details.append({
                'step_id': step.id,
                'title': step.title,
                'order': step.order,
                'content_type': step.content_type,
                'completed': progress.status == UserProgress.COMPLETED if progress else False,
                'completed_at': progress.completed_at if progress else None,
                'attempts': progress.attempts if progress else 0
            })

        return Response({
            'track_id': track.id,
            'track_title': track.title,
            'track_description': track.description,
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'percentage': round(percentage, 1),
            'is_completed': track_completion is not None,
            'completed_at': track_completion.completed_at if track_completion else None,
            'xp_reward': track.xp_reward or 100,
            'steps': step_details
        })

    except Exception as e:
        logger.error(f"Error getting track progress: {str(e)}")
        return Response({
            'detail': 'Failed to fetch track progress.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def topic_progress(request, topic_id):
    """
    Get user's progress on entire topic.

    GET /api/v1/topics/{topic_id}/progress/

    Returns:
        {
            "topic_id": 1,
            "topic_title": "Python Fundamentals",
            "total_tracks": 5,
            "completed_tracks": 3,
            "percentage": 60.0,
            "is_completed": false,
            "bonus_xp_reward": 1000,
            "tracks": [
                {
                    "track_id": 1,
                    "title": "Variables",
                    "completed": true,
                    "percentage": 100
                }
            ]
        }
    """
    user = request.user

    try:
        topic = get_object_or_404(Topico, id=topic_id)

        # Get all tracks in topic
        tracks = topic.tracks.all().order_by('order')

        # Get completed tracks
        from .models import UserTrackCompletion
        completed_track_ids = set(
            UserTrackCompletion.objects.filter(
                user=user,
                track__in=tracks
            ).values_list('track_id', flat=True)
        )

        # Calculate stats
        total_tracks = tracks.count()
        completed_tracks = len(completed_track_ids)
        percentage = (completed_tracks / total_tracks * 100) if total_tracks > 0 else 0

        # Check if topic completed
        from .models import UserTopicCompletion
        topic_completion = UserTopicCompletion.objects.filter(
            user=user,
            topic=topic
        ).first()

        # Build track details
        track_details = []
        for track in tracks:
            # Get track progress
            total_steps = track.steps.count()
            completed_steps = UserProgress.objects.filter(
                user=user,
                step__track=track,
                status=UserProgress.COMPLETED
            ).count()

            track_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0

            track_details.append({
                'track_id': track.id,
                'title': track.title,
                'order': track.order,
                'total_steps': total_steps,
                'completed_steps': completed_steps,
                'percentage': round(track_percentage, 1),
                'completed': track.id in completed_track_ids,
                'xp_reward': track.xp_reward or 100
            })

        return Response({
            'topic_id': topic.id,
            'topic_title': topic.title,
            'topic_description': topic.description,
            'total_tracks': total_tracks,
            'completed_tracks': completed_tracks,
            'percentage': round(percentage, 1),
            'is_completed': topic_completion is not None,
            'completed_at': topic_completion.completed_at if topic_completion else None,
            'bonus_xp_reward': topic.bonus_xp_reward or 1000,
            'tracks': track_details
        })

    except Exception as e:
        logger.error(f"Error getting topic progress: {str(e)}")
        return Response({
            'detail': 'Failed to fetch topic progress.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_completion_stats(request):
    """
    Get comprehensive completion statistics for user.

    GET /api/v1/my-completions/stats/

    Returns:
        {
            "tracks_completed": 15,
            "topics_completed": 3,
            "total_xp": 5500,
            "total_bonus_xp": 3000,
            "average_track_time_minutes": 45,
            "completion_rate": 75.5,
            "recent_completions": [...]
        }
    """
    user = request.user
    profile = user.profile

    try:
        from .models import UserTrackCompletion, UserTopicCompletion

        # Get recent completions
        recent_tracks = UserTrackCompletion.objects.filter(
            user=user
        ).select_related('track', 'track__topic').order_by('-completed_at')[:10]

        recent_topics = UserTopicCompletion.objects.filter(
            user=user
        ).select_related('topic').order_by('-completed_at')[:5]

        # Calculate average time
        track_times = UserTrackCompletion.objects.filter(
            user=user,
            completion_time_seconds__isnull=False
        ).values_list('completion_time_seconds', flat=True)

        avg_time_seconds = sum(track_times) / len(track_times) if track_times else 0
        avg_time_minutes = round(avg_time_seconds / 60, 1)

        # Total possible tracks
        total_tracks = Trilha.objects.count()
        completion_rate = (profile.tracks_completed_count / total_tracks * 100) if total_tracks > 0 else 0

        return Response({
            'tracks_completed': profile.tracks_completed_count,
            'topics_completed': profile.topics_completed_count,
            'total_xp': profile.xp_points,
            'total_bonus_xp': profile.total_bonus_xp,
            'average_track_time_minutes': avg_time_minutes,
            'completion_rate': round(completion_rate, 1),
            'current_rank': profile.rank_data['current']['name'],
            'rank_tier': profile.rank_data['current']['tier'],
            'recent_track_completions': [
                {
                    'track_id': c.track.id,
                    'track_title': c.track.title,
                    'topic_title': c.track.topic.title,
                    'xp_awarded': c.xp_awarded,
                    'completed_at': c.completed_at
                }
                for c in recent_tracks
            ],
            'recent_topic_completions': [
                {
                    'topic_id': c.topic.id,
                    'topic_title': c.topic.title,
                    'xp_awarded': c.xp_awarded,
                    'tracks_completed': c.tracks_completed,
                    'completed_at': c.completed_at
                }
                for c in recent_topics
            ]
        })

    except Exception as e:
        logger.error(f"Error getting completion stats: {str(e)}")
        return Response({
            'detail': 'Failed to fetch completion statistics.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
