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

    MAX_PROMPT_LENGTH = 50000  # Maximum prompt length to prevent abuse

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
        # Reuse HTTP session for connection pooling
        self.session = requests.Session()

    def _validate_prompts(self, system_prompt: str, user_prompt: str):
        """
        Validate prompt inputs before sending to AI service.

        Args:
            system_prompt: System instructions for AI
            user_prompt: User request/question

        Raises:
            AIServiceError: If prompts are invalid
        """
        if not system_prompt or not isinstance(system_prompt, str):
            raise AIServiceError("System prompt must be a non-empty string")

        if not user_prompt or not isinstance(user_prompt, str):
            raise AIServiceError("User prompt must be a non-empty string")

        if len(system_prompt) > self.MAX_PROMPT_LENGTH:
            raise AIServiceError(
                f"System prompt exceeds maximum length of {self.MAX_PROMPT_LENGTH} characters"
            )

        if len(user_prompt) > self.MAX_PROMPT_LENGTH:
            raise AIServiceError(
                f"User prompt exceeds maximum length of {self.MAX_PROMPT_LENGTH} characters"
            )

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
        # Validate inputs before generation
        self._validate_prompts(system_prompt, user_prompt)
        raise NotImplementedError("Subclasses must implement generate()")

    def _make_request(self, url: str, headers: dict, payload: dict) -> requests.Response:
        """Make HTTP request with error handling and connection pooling."""
        try:
            response = self.session.post(
                url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            raise AIServiceError("Request timed out")
        except requests.exceptions.HTTPError as e:
            # Log the response for debugging
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text[:500]}")
            raise AIServiceError(f"HTTP error: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
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
        # Validate inputs first
        self._validate_prompts(system_prompt, user_prompt)

        start_time = time.time()

        # Build endpoint WITHOUT API key (security fix)
        endpoint = self.api_endpoint or f"{self.DEFAULT_ENDPOINT}/{self.model_name}:generateContent"
        # Note: Gemini requires API key in URL, but we'll use POST parameter to avoid logging
        # Alternative: Use x-goog-api-key header if supported

        # Combine system and user prompts
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,  # Use header instead of URL parameter
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


class TransformersService(BaseAIService):
    """
    Service for Hugging Face Transformers (local models).

    Supports running models locally using the transformers library.
    Good for privacy and offline usage.
    """

    def generate(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate content using local Transformers model."""
        # Validate inputs first
        self._validate_prompts(system_prompt, user_prompt)

        start_time = time.time()

        try:
            # Import transformers here to make it optional
            from transformers import pipeline, AutoTokenizer
            import torch

            # Check for GPU availability
            device = 0 if torch.cuda.is_available() else -1

            logger.info(f"Loading Transformers model: {self.model_name}")

            # Initialize text generation pipeline
            generator = pipeline(
                "text-generation",
                model=self.model_name,
                tokenizer=self.model_name,
                device=device,
                torch_dtype=torch.float16 if device == 0 else torch.float32,
            )

            # Combine prompts
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"

            # Generate
            outputs = generator(
                combined_prompt,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                do_sample=True,
                top_p=0.95,
                num_return_sequences=1,
            )

            generated_text = outputs[0]["generated_text"]

            # Remove the prompt from generated text
            if generated_text.startswith(combined_prompt):
                generated_text = generated_text[len(combined_prompt):].strip()

            # Estimate tokens (rough approximation)
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            tokens_used = len(tokenizer.encode(generated_text))

            generation_time = time.time() - start_time

            logger.info(
                f"Transformers generation successful: ~{tokens_used} tokens in {generation_time:.2f}s"
            )

            return {
                "text": generated_text,
                "tokens": tokens_used,
                "time": generation_time,
                "raw_response": outputs
            }

        except ImportError:
            raise AIServiceError(
                "Transformers library not installed. "
                "Install with: pip install transformers torch"
            )
        except Exception as e:
            logger.error(f"Transformers generation failed: {str(e)}")
            raise AIServiceError(f"Transformers generation failed: {str(e)}")


class LangChainService(BaseAIService):
    """
    Service for LangChain integration.

    Supports multiple LLM backends through LangChain framework.
    Enables advanced features like chains, agents, and memory.
    """

    def generate(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate content using LangChain."""
        # Validate inputs first
        self._validate_prompts(system_prompt, user_prompt)

        start_time = time.time()

        try:
            # Import LangChain here to make it optional
            from langchain.llms import OpenAI, HuggingFaceHub
            from langchain.chat_models import ChatOpenAI
            from langchain.prompts import ChatPromptTemplate
            from langchain.schema import SystemMessage, HumanMessage

            logger.info(f"Using LangChain with model: {self.model_name}")

            # Determine which LangChain LLM to use based on api_endpoint
            if "openai" in self.api_endpoint.lower() or not self.api_endpoint:
                # Use OpenAI-compatible endpoint
                llm = ChatOpenAI(
                    model_name=self.model_name,
                    openai_api_key=self.api_key,
                    openai_api_base=self.api_endpoint if self.api_endpoint else None,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
            elif "huggingface" in self.api_endpoint.lower():
                # Use Hugging Face Hub
                llm = HuggingFaceHub(
                    repo_id=self.model_name,
                    huggingfacehub_api_token=self.api_key,
                    model_kwargs={
                        "temperature": self.temperature,
                        "max_length": self.max_tokens,
                    }
                )
            else:
                # Default to generic OpenAI-compatible
                llm = ChatOpenAI(
                    model_name=self.model_name,
                    openai_api_key=self.api_key,
                    openai_api_base=self.api_endpoint,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )

            # Create messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            # Generate
            response = llm(messages)

            # Extract text from response
            if hasattr(response, 'content'):
                generated_text = response.content
            else:
                generated_text = str(response)

            # Estimate tokens (rough approximation)
            tokens_used = len(generated_text.split()) * 1.3  # Rough estimate

            generation_time = time.time() - start_time

            logger.info(
                f"LangChain generation successful: ~{int(tokens_used)} tokens in {generation_time:.2f}s"
            )

            return {
                "text": generated_text,
                "tokens": int(tokens_used),
                "time": generation_time,
                "raw_response": {"content": generated_text}
            }

        except ImportError:
            raise AIServiceError(
                "LangChain library not installed. "
                "Install with: pip install langchain openai"
            )
        except Exception as e:
            logger.error(f"LangChain generation failed: {str(e)}")
            raise AIServiceError(f"LangChain generation failed: {str(e)}")


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
        'transformers': TransformersService,
        'langchain': LangChainService,
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
