from django.apps import AppConfig


class LearningConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "learning"

    def ready(self):
        """
        Import signals when the app is ready.

        # # Claude: This is the standard Django practice for registering signals.
        # By importing the signals module here, we ensure that the signal
        # handlers are connected when the application starts, making the
        # cache invalidation system active.
        """
        import learning.signals
