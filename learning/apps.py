"""
Learning app configuration.

Registers signal handlers for gamification features.
"""

from django.apps import AppConfig


class LearningConfig(AppConfig):
    """
    Configuration for the learning application.

    Handles initialization of signal handlers for:
    - Automatic user profile creation
    - XP and achievement awarding
    - Progress tracking
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "learning"

    def ready(self):
        """
        Import signal handlers when app is ready.

        This ensures signals are registered before any models are used.
        """
        import learning.signals  # noqa: F401
