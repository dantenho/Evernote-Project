"""
Webhook system for external integrations.

Allows sending event notifications to external services (Slack, Discord, custom endpoints, etc.)
"""

import json
import hashlib
import hmac
import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class WebhookEvent:
    """
    Represents a webhook event to be sent.
    """

    # Event types
    USER_REGISTERED = 'user.registered'
    USER_LEVELED_UP = 'user.leveled_up'
    STEP_COMPLETED = 'step.completed'
    TRACK_COMPLETED = 'track.completed'
    ACHIEVEMENT_EARNED = 'achievement.earned'
    DAILY_STREAK = 'daily_streak.milestone'
    AI_GENERATION = 'ai.generation_complete'

    def __init__(self, event_type: str, data: Dict[str, Any], user_id: Optional[int] = None):
        """
        Initialize webhook event.

        Args:
            event_type: Type of event (use constants above)
            data: Event payload data
            user_id: ID of user related to event (if applicable)
        """
        self.event_type = event_type
        self.data = data
        self.user_id = user_id
        self.timestamp = datetime.utcnow().isoformat()
        self.event_id = self._generate_event_id()

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        content = f"{self.event_type}:{self.timestamp}:{self.user_id}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_payload(self) -> Dict[str, Any]:
        """Convert event to webhook payload."""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp,
            'user_id': self.user_id,
            'data': self.data
        }


class WebhookDelivery:
    """
    Handles delivery of webhooks to endpoints.
    """

    def __init__(self, url: str, secret: Optional[str] = None):
        """
        Initialize webhook delivery.

        Args:
            url: Webhook endpoint URL
            secret: Secret for signing webhook payload (optional)
        """
        self.url = url
        self.secret = secret
        self.timeout = 10  # seconds

    def _generate_signature(self, payload: str) -> str:
        """
        Generate HMAC signature for payload.

        Args:
            payload: JSON string payload

        Returns:
            str: HMAC signature
        """
        if not self.secret:
            return ""

        signature = hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"sha256={signature}"

    def send(self, event: WebhookEvent, retry: bool = True) -> bool:
        """
        Send webhook event to endpoint.

        Args:
            event: WebhookEvent to send
            retry: Whether to retry on failure

        Returns:
            bool: True if delivery successful
        """
        payload = event.to_payload()
        payload_json = json.dumps(payload)

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'LearnHub-Webhooks/1.0',
            'X-Webhook-Event': event.event_type,
            'X-Webhook-ID': event.event_id,
        }

        # Add signature if secret is set
        if self.secret:
            headers['X-Webhook-Signature'] = self._generate_signature(payload_json)

        try:
            response = requests.post(
                self.url,
                data=payload_json,
                headers=headers,
                timeout=self.timeout
            )

            response.raise_for_status()

            logger.info(
                f"Webhook delivered successfully: {event.event_type} to {self.url} "
                f"(status: {response.status_code})"
            )

            return True

        except requests.exceptions.Timeout:
            logger.error(f"Webhook timeout: {event.event_type} to {self.url}")
            if retry:
                return self._retry_send(event)
            return False

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Webhook HTTP error: {event.event_type} to {self.url} "
                f"(status: {e.response.status_code})"
            )
            if retry and e.response.status_code >= 500:
                return self._retry_send(event)
            return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Webhook delivery failed: {event.event_type} to {self.url} - {str(e)}")
            if retry:
                return self._retry_send(event)
            return False

    def _retry_send(self, event: WebhookEvent, max_retries: int = 3) -> bool:
        """
        Retry sending webhook with exponential backoff.

        Args:
            event: WebhookEvent to send
            max_retries: Maximum number of retries

        Returns:
            bool: True if eventually successful
        """
        import time

        for attempt in range(max_retries):
            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            time.sleep(wait_time)

            logger.info(f"Retrying webhook delivery (attempt {attempt + 1}/{max_retries})")

            if self.send(event, retry=False):
                return True

        logger.error(f"Webhook delivery failed after {max_retries} retries")
        return False


class WebhookManager:
    """
    Manages webhook subscriptions and delivery.
    """

    def __init__(self):
        self.subscriptions: Dict[str, List[WebhookDelivery]] = {}

    def subscribe(self, event_type: str, url: str, secret: Optional[str] = None):
        """
        Subscribe to webhook events.

        Args:
            event_type: Event type to subscribe to (or '*' for all events)
            url: Webhook endpoint URL
            secret: Optional secret for signing payloads
        """
        if event_type not in self.subscriptions:
            self.subscriptions[event_type] = []

        delivery = WebhookDelivery(url, secret)
        self.subscriptions[event_type].append(delivery)

        logger.info(f"Webhook subscription added: {event_type} -> {url}")

    def unsubscribe(self, event_type: str, url: str):
        """
        Unsubscribe from webhook events.

        Args:
            event_type: Event type
            url: Webhook endpoint URL
        """
        if event_type in self.subscriptions:
            self.subscriptions[event_type] = [
                delivery for delivery in self.subscriptions[event_type]
                if delivery.url != url
            ]

            logger.info(f"Webhook subscription removed: {event_type} -> {url}")

    def trigger(self, event: WebhookEvent, async_delivery: bool = True):
        """
        Trigger webhook event delivery to all subscribers.

        Args:
            event: WebhookEvent to deliver
            async_delivery: Whether to deliver asynchronously (recommended)
        """
        # Get subscribers for this specific event type
        subscribers = self.subscriptions.get(event.event_type, [])

        # Also get subscribers for all events
        subscribers += self.subscriptions.get('*', [])

        if not subscribers:
            logger.debug(f"No subscribers for event: {event.event_type}")
            return

        logger.info(f"Triggering webhook: {event.event_type} to {len(subscribers)} subscribers")

        if async_delivery:
            # Use Django's cache to queue webhooks for async delivery
            # In production, use Celery or similar task queue
            self._queue_for_async_delivery(event, subscribers)
        else:
            # Synchronous delivery (blocks request)
            for delivery in subscribers:
                delivery.send(event)

    def _queue_for_async_delivery(self, event: WebhookEvent, subscribers: List[WebhookDelivery]):
        """
        Queue webhooks for async delivery.

        In production, replace this with Celery tasks or similar.
        """
        # For now, we'll just send synchronously in a try-except to avoid blocking
        # TODO: Integrate with Celery for true async delivery
        import threading

        def send_webhooks():
            for delivery in subscribers:
                try:
                    delivery.send(event)
                except Exception as e:
                    logger.error(f"Async webhook delivery error: {str(e)}")

        thread = threading.Thread(target=send_webhooks, daemon=True)
        thread.start()


# Global webhook manager instance
manager = WebhookManager()


# Convenience functions for common events

def trigger_user_registered(user):
    """Trigger webhook when user registers."""
    event = WebhookEvent(
        WebhookEvent.USER_REGISTERED,
        {
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined.isoformat()
        },
        user_id=user.id
    )
    manager.trigger(event)


def trigger_user_leveled_up(user, old_level: int, new_level: int, new_rank: str):
    """Trigger webhook when user levels up."""
    event = WebhookEvent(
        WebhookEvent.USER_LEVELED_UP,
        {
            'username': user.username,
            'old_level': old_level,
            'new_level': new_level,
            'new_rank': new_rank,
            'total_xp': user.profile.xp_points
        },
        user_id=user.id
    )
    manager.trigger(event)


def trigger_step_completed(user, step, track):
    """Trigger webhook when step is completed."""
    event = WebhookEvent(
        WebhookEvent.STEP_COMPLETED,
        {
            'username': user.username,
            'step_id': step.id,
            'step_title': step.title,
            'track_id': track.id,
            'track_title': track.title,
            'xp_earned': 10  # Base XP for step completion
        },
        user_id=user.id
    )
    manager.trigger(event)


def trigger_achievement_earned(user, achievement, xp_awarded: int):
    """Trigger webhook when achievement is earned."""
    event = WebhookEvent(
        WebhookEvent.ACHIEVEMENT_EARNED,
        {
            'username': user.username,
            'achievement_name': achievement.name,
            'achievement_icon': achievement.icon,
            'xp_awarded': xp_awarded
        },
        user_id=user.id
    )
    manager.trigger(event)


def trigger_daily_streak_milestone(user, streak_days: int):
    """Trigger webhook when daily streak milestone is reached."""
    event = WebhookEvent(
        WebhookEvent.DAILY_STREAK,
        {
            'username': user.username,
            'streak_days': streak_days,
            'milestone': streak_days in [7, 30, 100, 365]
        },
        user_id=user.id
    )
    manager.trigger(event)


# Integration helpers

def setup_slack_webhook(webhook_url: str, events: List[str] = None):
    """
    Setup Slack webhook integration.

    Args:
        webhook_url: Slack incoming webhook URL
        events: List of events to subscribe to (default: all major events)
    """
    if events is None:
        events = [
            WebhookEvent.USER_REGISTERED,
            WebhookEvent.USER_LEVELED_UP,
            WebhookEvent.ACHIEVEMENT_EARNED,
            WebhookEvent.DAILY_STREAK
        ]

    for event in events:
        manager.subscribe(event, webhook_url)

    logger.info(f"Slack webhook configured for {len(events)} event types")


def setup_discord_webhook(webhook_url: str, events: List[str] = None):
    """
    Setup Discord webhook integration.

    Args:
        webhook_url: Discord webhook URL
        events: List of events to subscribe to (default: all major events)
    """
    if events is None:
        events = [
            WebhookEvent.USER_REGISTERED,
            WebhookEvent.USER_LEVELED_UP,
            WebhookEvent.ACHIEVEMENT_EARNED
        ]

    for event in events:
        manager.subscribe(event, webhook_url)

    logger.info(f"Discord webhook configured for {len(events)} event types")
