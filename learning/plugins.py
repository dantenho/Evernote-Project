"""
Plugin system for extending LearnHub functionality.

Allows adding custom step types, AI providers, gamification rules, and more
through a plugin architecture.
"""

import importlib
import logging
from typing import Any, Dict, List, Optional, Callable
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class PluginRegistry:
    """
    Central registry for all plugins.

    Manages plugin registration, loading, and execution.
    """

    def __init__(self):
        self._plugins: Dict[str, Dict[str, 'BasePlugin']] = {
            'step_types': {},
            'ai_providers': {},
            'gamification_rules': {},
            'content_generators': {},
            'validators': {},
            'webhooks': {},
        }
        self._hooks: Dict[str, List[Callable]] = {}

    def register_plugin(self, plugin_type: str, plugin_name: str, plugin_instance: 'BasePlugin'):
        """
        Register a plugin in the registry.

        Args:
            plugin_type: Type of plugin (step_types, ai_providers, etc.)
            plugin_name: Unique name for the plugin
            plugin_instance: Instance of the plugin class

        Raises:
            ValueError: If plugin type is unknown or plugin name already exists
        """
        if plugin_type not in self._plugins:
            raise ValueError(f"Unknown plugin type: {plugin_type}")

        if plugin_name in self._plugins[plugin_type]:
            logger.warning(f"Plugin {plugin_name} already registered, replacing...")

        self._plugins[plugin_type][plugin_name] = plugin_instance
        logger.info(f"Registered plugin: {plugin_name} (type: {plugin_type})")

    def get_plugin(self, plugin_type: str, plugin_name: str) -> Optional['BasePlugin']:
        """
        Get a registered plugin.

        Args:
            plugin_type: Type of plugin
            plugin_name: Name of plugin

        Returns:
            BasePlugin: Plugin instance or None if not found
        """
        return self._plugins.get(plugin_type, {}).get(plugin_name)

    def get_all_plugins(self, plugin_type: str) -> Dict[str, 'BasePlugin']:
        """
        Get all plugins of a specific type.

        Args:
            plugin_type: Type of plugins to retrieve

        Returns:
            dict: Dictionary of plugin_name -> plugin_instance
        """
        return self._plugins.get(plugin_type, {}).copy()

    def register_hook(self, hook_name: str, callback: Callable):
        """
        Register a callback function for a hook.

        Args:
            hook_name: Name of the hook (e.g., 'before_step_complete', 'after_xp_award')
            callback: Function to call when hook is triggered
        """
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []

        self._hooks[hook_name].append(callback)
        logger.info(f"Registered hook callback for: {hook_name}")

    def trigger_hook(self, hook_name: str, **kwargs) -> Dict[str, Any]:
        """
        Trigger all callbacks registered for a hook.

        Args:
            hook_name: Name of the hook to trigger
            **kwargs: Arguments to pass to callbacks

        Returns:
            dict: Aggregated results from all callbacks
        """
        results = {}
        callbacks = self._hooks.get(hook_name, [])

        for i, callback in enumerate(callbacks):
            try:
                result = callback(**kwargs)
                results[f'callback_{i}'] = result
            except Exception as e:
                logger.error(f"Hook callback failed ({hook_name}): {str(e)}")
                results[f'callback_{i}'] = {'error': str(e)}

        return results

    def load_plugins_from_module(self, module_path: str):
        """
        Load all plugins from a Python module.

        Args:
            module_path: Import path to module (e.g., 'myapp.plugins')
        """
        try:
            module = importlib.import_module(module_path)

            # Look for plugin classes in module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                # Check if it's a plugin class (not abstract, subclass of BasePlugin)
                if (isinstance(attr, type) and
                    issubclass(attr, BasePlugin) and
                    attr is not BasePlugin and
                    not getattr(attr, '__abstractmethods__', None)):

                    # Instantiate and register
                    try:
                        plugin_instance = attr()
                        self.register_plugin(
                            plugin_instance.plugin_type,
                            plugin_instance.name,
                            plugin_instance
                        )
                    except Exception as e:
                        logger.error(f"Failed to instantiate plugin {attr_name}: {str(e)}")

            logger.info(f"Loaded plugins from module: {module_path}")

        except ImportError as e:
            logger.error(f"Failed to load plugin module {module_path}: {str(e)}")


# Global plugin registry instance
registry = PluginRegistry()


class BasePlugin(ABC):
    """
    Base class for all plugins.

    Subclass this to create custom plugins.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for the plugin."""
        pass

    @property
    @abstractmethod
    def plugin_type(self) -> str:
        """Type of plugin (step_types, ai_providers, etc.)."""
        pass

    @property
    def version(self) -> str:
        """Plugin version."""
        return "1.0.0"

    @property
    def description(self) -> str:
        """Human-readable description."""
        return ""

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Main execution method for the plugin.

        Override this to implement plugin functionality.
        """
        pass


class StepTypePlugin(BasePlugin):
    """
    Plugin for adding custom step types.

    Allows creating new types of learning content beyond lesson/quiz/code_challenge.
    """

    plugin_type = 'step_types'

    @abstractmethod
    def render_step(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render custom step type.

        Args:
            step_data: Step data from database

        Returns:
            dict: Rendered step data for frontend
        """
        pass

    @abstractmethod
    def validate_step(self, step_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate step data.

        Args:
            step_data: Step data to validate

        Returns:
            tuple: (is_valid, error_message)
        """
        pass


class AIProviderPlugin(BasePlugin):
    """
    Plugin for adding custom AI providers.

    Allows integration with new AI services beyond Claude, Gemini, etc.
    """

    plugin_type = 'ai_providers'

    @abstractmethod
    def generate_content(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Generate content using AI provider.

        Args:
            system_prompt: System instructions
            user_prompt: User request

        Returns:
            dict: Generated content with metadata
        """
        pass


class GamificationRulePlugin(BasePlugin):
    """
    Plugin for custom gamification rules.

    Allows adding custom XP calculations, achievement criteria, etc.
    """

    plugin_type = 'gamification_rules'

    @abstractmethod
    def calculate_xp(self, action: str, context: Dict[str, Any]) -> int:
        """
        Calculate XP for an action.

        Args:
            action: Action type (e.g., 'complete_step', 'daily_streak')
            context: Additional context data

        Returns:
            int: XP amount to award
        """
        pass


class WebhookPlugin(BasePlugin):
    """
    Plugin for webhook integrations.

    Allows sending events to external services.
    """

    plugin_type = 'webhooks'

    @abstractmethod
    def send_webhook(self, event: str, data: Dict[str, Any]) -> bool:
        """
        Send webhook notification.

        Args:
            event: Event name (e.g., 'user.registered', 'step.completed')
            data: Event data

        Returns:
            bool: True if webhook sent successfully
        """
        pass


# Example plugin implementations

class InteractiveVideoStepPlugin(StepTypePlugin):
    """
    Example: Interactive video step type with embedded quizzes.
    """

    name = "interactive_video"
    description = "Video content with embedded interactive questions"

    def execute(self, *args, **kwargs):
        return self.render_step(kwargs.get('step_data', {}))

    def render_step(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render interactive video step."""
        return {
            'type': 'interactive_video',
            'video_url': step_data.get('video_url'),
            'checkpoints': step_data.get('checkpoints', []),
            'questions': step_data.get('questions', [])
        }

    def validate_step(self, step_data: Dict[str, Any]) -> tuple[bool, str]:
        """Validate interactive video data."""
        if not step_data.get('video_url'):
            return False, "Video URL is required"

        if not step_data.get('checkpoints'):
            return False, "At least one checkpoint is required"

        return True, ""


class StreakBonusPlugin(GamificationRulePlugin):
    """
    Example: Bonus XP for maintaining daily streaks.
    """

    name = "streak_bonus"
    description = "Award bonus XP based on current streak"

    def execute(self, *args, **kwargs):
        return self.calculate_xp(kwargs.get('action'), kwargs.get('context', {}))

    def calculate_xp(self, action: str, context: Dict[str, Any]) -> int:
        """Calculate streak bonus XP."""
        if action != 'daily_login':
            return 0

        streak = context.get('current_streak', 0)

        # Award bonus XP based on streak milestones
        if streak >= 30:
            return 50  # 1 month streak
        elif streak >= 7:
            return 20  # 1 week streak
        elif streak >= 3:
            return 10  # 3 day streak

        return 5  # Base daily login XP


# Auto-register example plugins
registry.register_plugin('step_types', 'interactive_video', InteractiveVideoStepPlugin())
registry.register_plugin('gamification_rules', 'streak_bonus', StreakBonusPlugin())
