"""
Signal handlers for gamification features.

This module handles automatic creation of user profiles and
achievement checking when users complete learning activities.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import Count, Q
import logging

from .models import (
    UserProfile,
    UserProgress,
    Achievement,
    UserAchievement,
    Passo,
    Trilha,
    Area,
)

logger = logging.getLogger(__name__)


# ============================================================================
# User Profile Creation
# ============================================================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create UserProfile when a new User is created.

    Args:
        sender: User model class
        instance: User instance that was saved
        created: Boolean indicating if this is a new user
        **kwargs: Additional keyword arguments
    """
    if created:
        UserProfile.objects.create(user=instance)
        logger.info(f"Created profile for new user: {instance.username}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save UserProfile whenever User is saved.

    Ensures profile exists even if it was deleted.

    Args:
        sender: User model class
        instance: User instance that was saved
        **kwargs: Additional keyword arguments
    """
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()


# ============================================================================
# Achievement Checking
# ============================================================================

@receiver(post_save, sender=UserProgress)
def check_achievements_on_progress(sender, instance, created, **kwargs):
    """
    Check and award achievements when user progress is updated.

    Triggered when:
    - First step is completed
    - A track is completed
    - An area is completed

    Args:
        sender: UserProgress model class
        instance: UserProgress instance that was saved
        created: Boolean indicating if this is new progress
        **kwargs: Additional keyword arguments
    """
    # Only check when step is completed
    if instance.status != UserProgress.COMPLETED:
        return

    user = instance.user
    step = instance.step

    try:
        # Check for "First Step" achievement
        check_first_step_achievement(user)

        # Check for track completion
        check_track_completion_achievement(user, step.track)

        # Check for area completion
        check_area_completion_achievement(user, step.track.topic.area)

    except Exception as e:
        logger.error(f"Error checking achievements for user {user.username}: {str(e)}")


def check_first_step_achievement(user):
    """
    Award "First Step" achievement if this is user's first completed step.

    Args:
        user: User instance to check
    """
    # Check if this is the first completed step
    completed_count = UserProgress.objects.filter(
        user=user,
        status=UserProgress.COMPLETED
    ).count()

    if completed_count == 1:
        # Try to find and award the "First Step" achievement
        try:
            achievement = Achievement.objects.get(achievement_type=Achievement.FIRST_STEP)
            award_achievement(user, achievement)
        except Achievement.DoesNotExist:
            logger.warning("First Step achievement not found in database")
        except Achievement.MultipleObjectsReturned:
            logger.error("Multiple First Step achievements found - database inconsistency")


def check_track_completion_achievement(user, track):
    """
    Award track completion achievement if all steps in track are completed.

    Args:
        user: User instance to check
        track: Trilha instance to check completion for
    """
    # Count total steps in track
    total_steps = track.steps.count()
    if total_steps == 0:
        return

    # Count completed steps
    completed_steps = UserProgress.objects.filter(
        user=user,
        step__track=track,
        status=UserProgress.COMPLETED
    ).count()

    # Check if track is fully completed
    if completed_steps == total_steps:
        # Try to find track-specific achievement
        try:
            achievement = Achievement.objects.get(
                achievement_type=Achievement.TRACK_COMPLETE,
                related_track=track
            )
            award_achievement(user, achievement)
        except Achievement.DoesNotExist:
            logger.debug(f"No achievement found for completing track: {track.title}")
        except Achievement.MultipleObjectsReturned:
            logger.error(f"Multiple achievements found for track {track.id}")


def check_area_completion_achievement(user, area):
    """
    Award area completion achievement if all steps in area are completed.

    Args:
        user: User instance to check
        area: Area instance to check completion for
    """
    # Count total steps in area
    total_steps = Passo.objects.filter(track__topic__area=area).count()
    if total_steps == 0:
        return

    # Count completed steps
    completed_steps = UserProgress.objects.filter(
        user=user,
        step__track__topic__area=area,
        status=UserProgress.COMPLETED
    ).count()

    # Check if area is fully completed
    if completed_steps == total_steps:
        # Try to find area-specific achievement
        try:
            achievement = Achievement.objects.get(
                achievement_type=Achievement.AREA_COMPLETE,
                related_area=area
            )
            award_achievement(user, achievement)
        except Achievement.DoesNotExist:
            logger.debug(f"No achievement found for completing area: {area.title}")
        except Achievement.MultipleObjectsReturned:
            logger.error(f"Multiple achievements found for area {area.id}")


@receiver(post_save, sender=UserProfile)
def check_rank_achievements(sender, instance, **kwargs):
    """
    Check and award rank milestone achievements when profile is updated.

    Args:
        sender: UserProfile model class
        instance: UserProfile instance that was saved
        **kwargs: Additional keyword arguments
    """
    user = instance.user
    rank_tier = instance.rank_tier

    try:
        # Find all rank milestone achievements user qualifies for
        rank_achievements = Achievement.objects.filter(
            achievement_type=Achievement.RANK_MILESTONE,
            required_value__lte=rank_tier
        )

        for achievement in rank_achievements:
            award_achievement(user, achievement)

    except Exception as e:
        logger.error(f"Error checking rank achievements for user {user.username}: {str(e)}")


@receiver(post_save, sender=UserProfile)
def check_streak_achievements(sender, instance, **kwargs):
    """
    Check and award streak milestone achievements when profile is updated.

    Args:
        sender: UserProfile model class
        instance: UserProfile instance that was saved
        **kwargs: Additional keyword arguments
    """
    user = instance.user
    current_streak = instance.current_streak

    try:
        # Find all streak milestone achievements user qualifies for
        streak_achievements = Achievement.objects.filter(
            achievement_type=Achievement.STREAK_MILESTONE,
            required_value=current_streak  # Exact match for streak milestones
        )

        for achievement in streak_achievements:
            award_achievement(user, achievement)

    except Exception as e:
        logger.error(f"Error checking streak achievements for user {user.username}: {str(e)}")


@receiver(post_save, sender=UserProfile)
def check_xp_achievements(sender, instance, **kwargs):
    """
    Check and award XP milestone achievements when profile is updated.

    Args:
        sender: UserProfile model class
        instance: UserProfile instance that was saved
        **kwargs: Additional keyword arguments
    """
    user = instance.user
    xp_points = instance.xp_points

    try:
        # Find all XP milestone achievements user qualifies for
        xp_achievements = Achievement.objects.filter(
            achievement_type=Achievement.XP_MILESTONE,
            required_value__lte=xp_points
        )

        for achievement in xp_achievements:
            award_achievement(user, achievement)

    except Exception as e:
        logger.error(f"Error checking XP achievements for user {user.username}: {str(e)}")


# ============================================================================
# Achievement Awarding
# ============================================================================

def award_achievement(user, achievement):
    """
    Award an achievement to a user if they don't already have it.

    Also awards bonus XP if the achievement provides it.

    Args:
        user: User instance to award achievement to
        achievement: Achievement instance to award

    Returns:
        tuple: (UserAchievement instance or None, bool indicating if newly awarded)
    """
    # Check if user already has this achievement
    user_achievement, created = UserAchievement.objects.get_or_create(
        user=user,
        achievement=achievement,
        defaults={'xp_awarded': achievement.xp_reward}
    )

    if created:
        logger.info(
            f"Achievement earned: {user.username} earned '{achievement.name}' "
            f"(+{achievement.xp_reward} XP)"
        )

        # Award bonus XP if achievement provides it
        if achievement.xp_reward > 0:
            profile = user.profile
            profile.add_xp(achievement.xp_reward)

            logger.info(
                f"Bonus XP awarded: {user.username} received {achievement.xp_reward} XP "
                f"for '{achievement.name}'"
            )

        return user_achievement, True

    return user_achievement, False
