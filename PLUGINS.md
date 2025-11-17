# Plugin System Documentation

LearnHub features a powerful plugin system that allows extending functionality without modifying core code.

## Overview

The plugin system enables:

- ✅ **Custom Step Types**: Create new types of learning content
- ✅ **AI Provider Integration**: Add support for new AI services
- ✅ **Gamification Rules**: Custom XP calculations and achievements
- ✅ **Content Generators**: Automated content creation
- ✅ **Validators**: Custom validation logic
- ✅ **Webhooks**: External integrations (Slack, Discord, etc.)

## Architecture

### Plugin Registry

Central registry that manages all plugins:

```python
from learning.plugins import registry

# Register a plugin
registry.register_plugin('step_types', 'my_plugin', MyPluginInstance())

# Get a plugin
plugin = registry.get_plugin('step_types', 'my_plugin')

# Get all plugins of a type
all_step_plugins = registry.get_all_plugins('step_types')
```

### Plugin Types

Six plugin categories:

1. **step_types**: Custom learning step types
2. **ai_providers**: AI service integrations
3. **gamification_rules**: XP and achievement logic
4. **content_generators**: Automated content creation
5. **validators**: Input validation
6. **webhooks**: External integrations

### Hook System

Register callbacks for events:

```python
# Register a hook
registry.register_hook('before_step_complete', my_callback)

# Trigger a hook
results = registry.trigger_hook('before_step_complete', user=user, step=step)
```

Available hooks:
- `before_step_complete`
- `after_step_complete`
- `before_xp_award`
- `after_xp_award`
- `before_level_up`
- `after_level_up`

## Creating Plugins

### Base Plugin Class

All plugins inherit from `BasePlugin`:

```python
from learning.plugins import BasePlugin

class MyPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "my_plugin"

    @property
    def plugin_type(self) -> str:
        return "step_types"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "My awesome plugin"

    def execute(self, *args, **kwargs):
        # Main plugin logic
        pass
```

### Example: Custom Step Type

Create interactive video steps with embedded quizzes:

```python
from learning.plugins import StepTypePlugin

class InteractiveVideoPlugin(StepTypePlugin):
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

# Register the plugin
from learning.plugins import registry
registry.register_plugin('step_types', 'interactive_video', InteractiveVideoPlugin())
```

### Example: AI Provider

Add support for a new AI service:

```python
from learning.plugins import AIProviderPlugin

class MyAIProvider(AIProviderPlugin):
    name = "my_ai_service"
    description = "Integration with My AI Service"

    def execute(self, *args, **kwargs):
        return self.generate_content(
            kwargs.get('system_prompt'),
            kwargs.get('user_prompt')
        )

    def generate_content(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate content using My AI Service."""
        import requests

        response = requests.post(
            'https://api.myaiservice.com/generate',
            json={
                'system': system_prompt,
                'user': user_prompt
            },
            headers={'Authorization': f'Bearer {self.api_key}'}
        )

        data = response.json()

        return {
            'text': data['generated_text'],
            'tokens': data['tokens_used'],
            'time': data['generation_time']
        }

# Register the plugin
registry.register_plugin('ai_providers', 'my_ai_service', MyAIProvider())
```

### Example: Gamification Rule

Custom XP calculation based on streak:

```python
from learning.plugins import GamificationRulePlugin

class StreakBonusPlugin(GamificationRulePlugin):
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

# Register the plugin
registry.register_plugin('gamification_rules', 'streak_bonus', StreakBonusPlugin())
```

## Using Plugins

### In Views

```python
from learning.plugins import registry

def custom_step_view(request, step_id):
    """Handle custom step types via plugins."""
    step = get_object_or_404(Passo, id=step_id)

    # Get the appropriate plugin for this step type
    plugin = registry.get_plugin('step_types', step.content_type)

    if plugin:
        # Use plugin to render the step
        rendered_data = plugin.execute(step_data=step.get_data())
        return Response(rendered_data)
    else:
        # Fall back to default handling
        return Response({'error': 'Unknown step type'})
```

### With Hooks

```python
from learning.plugins import registry

def complete_step_with_hooks(user, step):
    """Complete step with plugin hooks."""

    # Trigger before hook
    registry.trigger_hook('before_step_complete', user=user, step=step)

    # Complete the step
    progress = UserProgress.objects.get_or_create(user=user, step=step)
    progress.mark_as_completed()

    # Trigger after hook
    registry.trigger_hook('after_step_complete', user=user, step=step, progress=progress)
```

## Loading Plugins

### From Module

```python
# Load all plugins from a module
registry.load_plugins_from_module('myapp.plugins')
```

### From Package

Create a `plugins.py` file in your Django app:

```python
# myapp/plugins.py

from learning.plugins import StepTypePlugin, registry

class MyStepType(StepTypePlugin):
    name = "my_step"
    # ... implementation ...

# Auto-register
registry.register_plugin('step_types', 'my_step', MyStepType())
```

Then in your app's `apps.py`:

```python
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'myapp'

    def ready(self):
        # Import plugins to register them
        from . import plugins
```

## Webhook System

### Overview

Built-in webhook system for external integrations:

```python
from learning.webhooks import manager, WebhookEvent

# Subscribe to events
manager.subscribe(
    event_type=WebhookEvent.USER_REGISTERED,
    url='https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
    secret='your-webhook-secret'  # Optional
)

# Trigger events
from learning.webhooks import trigger_user_registered
trigger_user_registered(user)
```

### Available Events

- `user.registered` - New user registration
- `user.leveled_up` - User gains a level
- `step.completed` - Step completion
- `track.completed` - Track completion
- `achievement.earned` - Achievement unlocked
- `daily_streak.milestone` - Streak milestone reached
- `ai.generation_complete` - AI content generated

### Slack Integration

```python
from learning.webhooks import setup_slack_webhook

setup_slack_webhook(
    webhook_url='https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
    events=[
        WebhookEvent.USER_REGISTERED,
        WebhookEvent.USER_LEVELED_UP,
        WebhookEvent.ACHIEVEMENT_EARNED
    ]
)
```

### Discord Integration

```python
from learning.webhooks import setup_discord_webhook

setup_discord_webhook(
    webhook_url='https://discord.com/api/webhooks/YOUR/WEBHOOK/URL',
    events=[
        WebhookEvent.USER_REGISTERED,
        WebhookEvent.ACHIEVEMENT_EARNED
    ]
)
```

### Custom Webhooks

```python
from learning.webhooks import WebhookEvent, manager

# Create custom event
event = WebhookEvent(
    event_type='custom.event',
    data={
        'message': 'Something happened!',
        'value': 42
    },
    user_id=user.id
)

# Trigger delivery
manager.trigger(event)
```

### Webhook Security

Webhooks include HMAC signatures for verification:

```python
# Verify webhook signature (on receiving end)
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(f"sha256={expected}", signature)
```

## Best Practices

### Plugin Development

1. **Keep plugins focused**: One plugin = one feature
2. **Handle errors gracefully**: Don't crash if plugin fails
3. **Validate inputs**: Check data before processing
4. **Document thoroughly**: Explain what plugin does and how to use it
5. **Version carefully**: Use semantic versioning
6. **Test independently**: Unit test plugins in isolation

### Security

1. **Validate all inputs** in plugins
2. **Sanitize outputs** before displaying
3. **Use secrets safely**: Never hardcode API keys
4. **Implement rate limiting** for expensive operations
5. **Log security events**: Track plugin usage

### Performance

1. **Cache results** when possible
2. **Avoid N+1 queries**: Use select_related/prefetch_related
3. **Run heavy tasks async**: Use Celery for long-running operations
4. **Implement timeouts**: Don't let plugins hang
5. **Monitor resource usage**: Track CPU/memory consumption

## Plugin Marketplace (Future)

Plan for community plugin sharing:

1. **Plugin Registry Website**: Browse and install plugins
2. **Versioning**: Semantic versioning with compatibility checks
3. **Security Scanning**: Automated security review
4. **Ratings & Reviews**: Community feedback
5. **Installation**: One-click plugin installation

## Examples in Production

### Interactive Coding Challenges

```python
class LiveCodeEditorPlugin(StepTypePlugin):
    """Real-time code execution with WebSocket support."""
    name = "live_code_editor"

    def render_step(self, step_data):
        return {
            'type': 'live_code_editor',
            'language': step_data.get('language', 'python'),
            'starter_code': step_data.get('starter_code'),
            'test_cases': step_data.get('test_cases', []),
            'execution_environment': 'pyodide'  # Browser-based Python
        }
```

### Peer Review System

```python
class PeerReviewPlugin(StepTypePlugin):
    """Enable peer code review for projects."""
    name = "peer_review"

    def render_step(self, step_data):
        return {
            'type': 'peer_review',
            'project_id': step_data.get('project_id'),
            'review_criteria': step_data.get('criteria', []),
            'min_reviews': step_data.get('min_reviews', 2),
            'anonymous': step_data.get('anonymous', True)
        }
```

## API Reference

### PluginRegistry

```python
class PluginRegistry:
    def register_plugin(plugin_type: str, plugin_name: str, plugin_instance: BasePlugin)
    def get_plugin(plugin_type: str, plugin_name: str) -> BasePlugin
    def get_all_plugins(plugin_type: str) -> Dict[str, BasePlugin]
    def register_hook(hook_name: str, callback: Callable)
    def trigger_hook(hook_name: str, **kwargs) -> Dict[str, Any]
    def load_plugins_from_module(module_path: str)
```

### BasePlugin

```python
class BasePlugin(ABC):
    @property
    def name(self) -> str
    @property
    def plugin_type(self) -> str
    @property
    def version(self) -> str
    @property
    def description(self) -> str

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any
```

## Contributing Plugins

To contribute a plugin to the LearnHub ecosystem:

1. Fork the repository
2. Create plugin in `learning/contrib_plugins/`
3. Write tests in `learning/tests/test_plugins/`
4. Document in plugin docstring
5. Submit pull request

## Support

- **Documentation**: https://docs.learnhub.example.com/plugins
- **Examples**: `/learning/plugins.py`
- **Issues**: GitHub Issues
- **Community**: Discord #plugin-development

## Changelog

### 2025-01-XX - Plugin System v1.0

- ✅ Initial plugin system implementation
- ✅ Support for 6 plugin types
- ✅ Hook system for event callbacks
- ✅ Example plugins (Interactive Video, Streak Bonus)
- ✅ Webhook system for external integrations
- ✅ Slack and Discord webhook helpers
- ✅ Plugin registry with auto-loading
