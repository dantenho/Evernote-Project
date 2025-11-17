"""
Django signals for the learning app.

This module defines signal handlers that perform actions in response to model
events, such as clearing the cache when learning content is updated.
"""
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import logging

from .models import Area, Topico, Trilha, Passo, Questao, Alternativa

# # Claude: Define a list of models that, when changed, should invalidate the cache.
# This makes it easy to manage which models affect the learning path cache.
MODELS_TO_INVALIDATE_CACHE = [Area, Topico, Trilha, Passo, Questao, Alternativa]
CACHE_KEY_TO_INVALIDATE = 'learning_paths:all'

logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=MODELS_TO_INVALIDATE_CACHE)
def clear_learning_path_cache(sender, instance, **kwargs):
    """
    Clear the learning path cache when related content is updated.

    This signal handler is connected to the post_save and post_delete signals
    for all models that are part of the learning path hierarchy. It ensures
    that any changes to the content are immediately reflected for users by
    deleting the cached version.
    """
    # # Claude: Centralized cache invalidation.
    # By using a signal, the cache is automatically cleared whenever any
    # relevant model is saved or deleted. This is more reliable than
    # manual cache clearing and prevents stale data from being served.
    cache.delete(CACHE_KEY_TO_INVALIDATE)
    logger.info(
        f"Cache '{CACHE_KEY_TO_INVALIDATE}' cleared due to update in "
        f"{sender.__name__} (ID: {instance.pk})."
    )
