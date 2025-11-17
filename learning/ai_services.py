"""
AI Content Generation Services

This module provides integration with multiple AI providers for
content generation: Claude (Anthropic), Gemini (Google), Ollama (local),
and custom OpenAI-compatible endpoints.
"""

import json
import time
import logging
import requests
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Base exception for AI service errors."""
    pass


class BaseAIService:
    """Base class for AI service integrations."""

    def __init__(self, provider):
        """
        Initialize AI service with provider configuration.

        Args:
            provider: AIProvider model instance
        """
        self.provider = provider
        self.api_key = provider.api_key
        self.api_endpoint = provider.api_endpoint
        self.model_name = provider.model_name
        self.max_tokens = provider.max_tokens
        self.temperature = provider.temperature

    def generate(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Generate content using AI provider.

        Args:
            system_prompt: System instructions for AI
            user_prompt: User request/question

        Returns:
            dict: Generated content with metadata
                - text: Generated text
                - tokens: Number of tokens used
                - time: Generation time in seconds
        """
        raise NotImplementedError("Subclasses must implement generate()")

    def _make_request(self, url: str, headers: dict, payload: dict) -> requests.Response:
        """Make HTTP request with error handling."""
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            raise AIServiceError("Request timed out")
        except requests.exceptions.RequestException as e:
            raise AIServiceError(f"Request failed: {str(e)}")


class ClaudeService(BaseAIService):
    """Service for Claude (Anthropic) API integration."""

    DEFAULT_ENDPOINT = "https://api.anthropic.com/v1/messages"
    ANTHROPIC_VERSION = "2023-06-01"

    def generate(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate content using Claude API."""
        start_time = time.time()

        # Prepare request
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.ANTHROPIC_VERSION,
            "content-type": "application/json",
        }

        payload = {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        }

        # Make request
        endpoint = self.api_endpoint or self.DEFAULT_ENDPOINT
        response = self._make_request(endpoint, headers, payload)
        data = response.json()

        # Extract response
        generated_text = data.get("content", [{}])[0].get("text", "")
        tokens_used = data.get("usage", {}).get("output_tokens", 0)

        generation_time = time.time() - start_time

        logger.info(
            f"Claude generation successful: {tokens_used} tokens in {generation_time:.2f}s"
        )

        return {
            "text": generated_text,
            "tokens": tokens_used,
            "time": generation_time,
            "raw_response": data
        }


class GeminiService(BaseAIService):
    """Service for Google Gemini API integration."""

    DEFAULT_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"

    def generate(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate content using Gemini API."""
        start_time = time.time()

        # Build endpoint with API key
        endpoint = self.api_endpoint or f"{self.DEFAULT_ENDPOINT}/{self.model_name}:generateContent"
        endpoint = f"{endpoint}?key={self.api_key}"

        # Combine system and user prompts
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"

        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": combined_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens,
            }
        }

        # Make request
        response = self._make_request(endpoint, headers, payload)
        data = response.json()

        # Extract response
        candidates = data.get("candidates", [])
        if not candidates:
            raise AIServiceError("No response from Gemini")

        generated_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        tokens_used = data.get("usageMetadata", {}).get("candidatesTokenCount", 0)

        generation_time = time.time() - start_time

        logger.info(
            f"Gemini generation successful: {tokens_used} tokens in {generation_time:.2f}s"
        )

        return {
            "text": generated_text,
            "tokens": tokens_used,
            "time": generation_time,
            "raw_response": data
        }


class OllamaService(BaseAIService):
    """Service for Ollama (local) API integration."""

    DEFAULT_ENDPOINT = "http://localhost:11434"

    def generate(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate content using Ollama API."""
        start_time = time.time()

        # Build endpoint
        endpoint = f"{self.api_endpoint or self.DEFAULT_ENDPOINT}/api/generate"

        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            }
        }

        # Make request
        response = self._make_request(endpoint, headers, payload)
        data = response.json()

        # Extract response
        generated_text = data.get("response", "")
        tokens_used = data.get("eval_count", 0)

        generation_time = time.time() - start_time

        logger.info(
            f"Ollama generation successful: {tokens_used} tokens in {generation_time:.2f}s"
        )

        return {
            "text": generated_text,
            "tokens": tokens_used,
            "time": generation_time,
            "raw_response": data
        }


class CustomModelService(BaseAIService):
    """Service for custom OpenAI-compatible API integration."""

    def generate(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate content using custom OpenAI-compatible API."""
        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        # Make request
        response = self._make_request(self.api_endpoint, headers, payload)
        data = response.json()

        # Extract response (OpenAI format)
        choices = data.get("choices", [])
        if not choices:
            raise AIServiceError("No response from custom model")

        generated_text = choices[0].get("message", {}).get("content", "")
        tokens_used = data.get("usage", {}).get("completion_tokens", 0)

        generation_time = time.time() - start_time

        logger.info(
            f"Custom model generation successful: {tokens_used} tokens in {generation_time:.2f}s"
        )

        return {
            "text": generated_text,
            "tokens": tokens_used,
            "time": generation_time,
            "raw_response": data
        }


def get_ai_service(provider) -> BaseAIService:
    """
    Get appropriate AI service for provider.

    Args:
        provider: AIProvider model instance

    Returns:
        BaseAIService: Appropriate service instance

    Raises:
        ValueError: If provider type is not supported
    """
    service_map = {
        'claude': ClaudeService,
        'gemini': GeminiService,
        'ollama': OllamaService,
        'custom': CustomModelService,
    }

    service_class = service_map.get(provider.provider_type)
    if not service_class:
        raise ValueError(f"Unsupported provider type: {provider.provider_type}")

    return service_class(provider)


def generate_content(
    provider_id: int,
    template_id: int,
    user: Any,
    **template_variables
) -> Dict[str, Any]:
    """
    Generate content using specified provider and template.

    Args:
        provider_id: AIProvider ID
        template_id: ContentTemplate ID
        user: User requesting generation
        **template_variables: Variables for template rendering

    Returns:
        dict: Generation result
            - success: bool
            - text: str (if successful)
            - parsed_content: dict (if successful)
            - error: str (if failed)
            - generated_content_id: int (database record ID)
    """
    from .models import AIProvider, ContentTemplate, GeneratedContent

    try:
        # Get provider and template
        provider = AIProvider.objects.get(id=provider_id, is_active=True)
        template = ContentTemplate.objects.get(id=template_id, is_active=True)

        # Render prompts
        system_prompt = template.system_prompt
        user_prompt = template.render_prompt(**template_variables)

        # Generate content
        service = get_ai_service(provider)
        result = service.generate(system_prompt, user_prompt)

        # Parse JSON if possible
        try:
            parsed_content = json.loads(result['text'])
        except json.JSONDecodeError:
            parsed_content = {"raw_text": result['text']}

        # Save to database
        generated = GeneratedContent.objects.create(
            provider=provider,
            template=template,
            user=user,
            prompt=f"System: {system_prompt}\n\nUser: {user_prompt}",
            generated_text=result['text'],
            parsed_content=parsed_content,
            tokens_used=result['tokens'],
            generation_time=result['time'],
            was_successful=True
        )

        return {
            "success": True,
            "text": result['text'],
            "parsed_content": parsed_content,
            "tokens": result['tokens'],
            "time": result['time'],
            "generated_content_id": generated.id
        }

    except Exception as e:
        logger.error(f"Content generation failed: {str(e)}")

        # Save error to database
        try:
            generated = GeneratedContent.objects.create(
                provider_id=provider_id if 'provider' in locals() else None,
                template_id=template_id if 'template' in locals() else None,
                user=user,
                prompt="Error before generation",
                generated_text="",
                was_successful=False,
                error_message=str(e)
            )
        except:
            pass

        return {
            "success": False,
            "error": str(e)
        }
