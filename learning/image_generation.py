"""
Image generation services using Stable Diffusion and other AI models.

Supports multiple backends:
- Stability AI API (official Stable Diffusion API)
- Replicate API (cloud-hosted models)
- Local Stable Diffusion (via diffusers library)
- DALL-E (OpenAI)
- Midjourney (via unofficial API)
"""

import os
import base64
import logging
import requests
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from django.conf import settings
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


class ImageGenerationError(Exception):
    """Base exception for image generation errors."""
    pass


class BaseImageGenerator:
    """Base class for image generation services."""

    def __init__(self, api_key: Optional[str] = None, model_path: Optional[str] = None):
        """
        Initialize image generator.

        Args:
            api_key: API key for cloud services
            model_path: Local model path for self-hosted
        """
        self.api_key = api_key
        self.model_path = model_path

    def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image from text prompt.

        Args:
            prompt: Text description of desired image
            negative_prompt: What to avoid in the image
            width: Image width in pixels
            height: Image height in pixels
            num_inference_steps: Number of denoising steps (higher = better quality)
            guidance_scale: How closely to follow prompt (7-15 recommended)
            seed: Random seed for reproducibility
            **kwargs: Additional model-specific parameters

        Returns:
            dict: Generated image data
                - image_data: Base64 encoded image or bytes
                - format: Image format (png, jpg)
                - width: Image width
                - height: Image height
                - seed: Seed used
                - time: Generation time
        """
        raise NotImplementedError("Subclasses must implement generate()")

    def validate_prompt(self, prompt: str) -> tuple[bool, str]:
        """
        Validate image generation prompt.

        Args:
            prompt: Prompt to validate

        Returns:
            tuple: (is_valid, error_message)
        """
        if not prompt or not isinstance(prompt, str):
            return False, "Prompt must be a non-empty string"

        if len(prompt) > 2000:
            return False, "Prompt is too long (max 2000 characters)"

        # Check for NSFW/inappropriate content patterns
        inappropriate_patterns = [
            'nsfw', 'nude', 'naked', 'explicit', 'porn', 'sexual',
            'gore', 'violence', 'blood', 'death', 'suicide'
        ]

        prompt_lower = prompt.lower()
        for pattern in inappropriate_patterns:
            if pattern in prompt_lower:
                return False, f"Prompt contains inappropriate content: {pattern}"

        return True, ""


class StabilityAIGenerator(BaseImageGenerator):
    """
    Stability AI API integration.

    Official Stable Diffusion API service.
    """

    API_HOST = "https://api.stability.ai"
    DEFAULT_MODEL = "stable-diffusion-xl-1024-v1-0"

    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key=api_key)
        self.model = model or self.DEFAULT_MODEL

    def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        style_preset: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate image using Stability AI API."""

        # Validate prompt
        is_valid, error = self.validate_prompt(prompt)
        if not is_valid:
            raise ImageGenerationError(error)

        start_time = time.time()

        # Prepare request
        url = f"{self.API_HOST}/v1/generation/{self.model}/text-to-image"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Build text prompts
        text_prompts = [{"text": prompt, "weight": 1}]
        if negative_prompt:
            text_prompts.append({"text": negative_prompt, "weight": -1})

        payload = {
            "text_prompts": text_prompts,
            "cfg_scale": guidance_scale,
            "height": height,
            "width": width,
            "steps": num_inference_steps,
            "samples": 1,
        }

        if seed is not None:
            payload["seed"] = seed

        if style_preset:
            payload["style_preset"] = style_preset

        # Make request
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()

            # Extract image
            if not data.get("artifacts"):
                raise ImageGenerationError("No image generated")

            image_data = data["artifacts"][0]["base64"]
            seed_used = data["artifacts"][0].get("seed", seed)

            generation_time = time.time() - start_time

            logger.info(f"Stability AI image generated: {width}x{height} in {generation_time:.2f}s")

            return {
                "image_data": image_data,
                "format": "png",
                "width": width,
                "height": height,
                "seed": seed_used,
                "time": generation_time,
                "provider": "stability_ai",
                "model": self.model
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Stability AI API error: {str(e)}")
            raise ImageGenerationError(f"API request failed: {str(e)}")


class ReplicateGenerator(BaseImageGenerator):
    """
    Replicate API integration.

    Cloud-hosted AI models including Stable Diffusion variants.
    """

    API_HOST = "https://api.replicate.com/v1"

    # Popular Stable Diffusion models on Replicate
    MODELS = {
        "sdxl": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
        "sd-1.5": "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
        "playground-v2": "playgroundai/playground-v2-1024px-aesthetic:42fe626e41cc811eaf02c94b892774839268ce1994ea778eba97103fe1ef51b8"
    }

    def __init__(self, api_key: str, model: str = "sdxl"):
        super().__init__(api_key=api_key)
        self.model_version = self.MODELS.get(model, self.MODELS["sdxl"])

    def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate image using Replicate API."""

        # Validate prompt
        is_valid, error = self.validate_prompt(prompt)
        if not is_valid:
            raise ImageGenerationError(error)

        start_time = time.time()

        # Prepare request
        url = f"{self.API_HOST}/predictions"

        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "version": self.model_version,
            "input": {
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
            }
        }

        if negative_prompt:
            payload["input"]["negative_prompt"] = negative_prompt

        if seed is not None:
            payload["input"]["seed"] = seed

        try:
            # Start prediction
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            prediction = response.json()

            # Poll for completion
            prediction_url = prediction["urls"]["get"]
            max_attempts = 60  # 60 attempts * 2 seconds = 2 minutes max

            for _ in range(max_attempts):
                time.sleep(2)

                response = requests.get(prediction_url, headers=headers, timeout=30)
                response.raise_for_status()
                prediction = response.json()

                if prediction["status"] == "succeeded":
                    break
                elif prediction["status"] == "failed":
                    raise ImageGenerationError(f"Generation failed: {prediction.get('error')}")

            if prediction["status"] != "succeeded":
                raise ImageGenerationError("Generation timed out")

            # Get image URL
            image_url = prediction["output"][0] if isinstance(prediction["output"], list) else prediction["output"]

            # Download image
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()
            image_data = base64.b64encode(image_response.content).decode()

            generation_time = time.time() - start_time

            logger.info(f"Replicate image generated: {width}x{height} in {generation_time:.2f}s")

            return {
                "image_data": image_data,
                "format": "png",
                "width": width,
                "height": height,
                "seed": seed,
                "time": generation_time,
                "provider": "replicate",
                "model": self.model_version
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Replicate API error: {str(e)}")
            raise ImageGenerationError(f"API request failed: {str(e)}")


class LocalStableDiffusionGenerator(BaseImageGenerator):
    """
    Local Stable Diffusion using Hugging Face diffusers.

    Runs models locally for privacy and cost savings.
    """

    def __init__(self, model_path: str = "stabilityai/stable-diffusion-xl-base-1.0"):
        super().__init__(model_path=model_path)
        self.pipeline = None
        self.device = None

    def _load_pipeline(self):
        """Load Stable Diffusion pipeline (lazy loading)."""
        if self.pipeline is not None:
            return

        try:
            from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
            import torch

            logger.info(f"Loading Stable Diffusion model: {self.model_path}")

            # Determine device
            if torch.cuda.is_available():
                self.device = "cuda"
                torch_dtype = torch.float16
            elif torch.backends.mps.is_available():
                self.device = "mps"
                torch_dtype = torch.float32
            else:
                self.device = "cpu"
                torch_dtype = torch.float32

            # Load pipeline
            self.pipeline = StableDiffusionXLPipeline.from_pretrained(
                self.model_path,
                torch_dtype=torch_dtype,
                use_safetensors=True,
                variant="fp16" if torch_dtype == torch.float16 else None
            )

            # Use efficient scheduler
            self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipeline.scheduler.config
            )

            # Move to device
            self.pipeline = self.pipeline.to(self.device)

            # Enable memory optimizations
            if self.device == "cuda":
                self.pipeline.enable_model_cpu_offload()
                self.pipeline.enable_vae_slicing()

            logger.info(f"Model loaded successfully on {self.device}")

        except ImportError:
            raise ImageGenerationError(
                "diffusers library not installed. "
                "Install with: pip install diffusers transformers accelerate"
            )

    def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate image using local Stable Diffusion."""

        # Validate prompt
        is_valid, error = self.validate_prompt(prompt)
        if not is_valid:
            raise ImageGenerationError(error)

        # Load pipeline if needed
        self._load_pipeline()

        start_time = time.time()

        try:
            import torch
            from PIL import Image
            import io

            # Set seed for reproducibility
            generator = None
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)

            # Generate image
            result = self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator
            )

            image = result.images[0]

            # Convert to base64
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            image_data = base64.b64encode(buffer.getvalue()).decode()

            generation_time = time.time() - start_time

            logger.info(f"Local SD image generated: {width}x{height} in {generation_time:.2f}s")

            return {
                "image_data": image_data,
                "format": "png",
                "width": width,
                "height": height,
                "seed": seed,
                "time": generation_time,
                "provider": "local_sd",
                "model": self.model_path
            }

        except Exception as e:
            logger.error(f"Local SD generation failed: {str(e)}")
            raise ImageGenerationError(f"Generation failed: {str(e)}")


class DALLEGenerator(BaseImageGenerator):
    """
    DALL-E integration (OpenAI).

    High-quality image generation from OpenAI.
    """

    API_HOST = "https://api.openai.com/v1"

    def __init__(self, api_key: str, model: str = "dall-e-3"):
        super().__init__(api_key=api_key)
        self.model = model

    def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate image using DALL-E API."""

        # Validate prompt
        is_valid, error = self.validate_prompt(prompt)
        if not is_valid:
            raise ImageGenerationError(error)

        start_time = time.time()

        url = f"{self.API_HOST}/images/generations"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "style": style,
            "response_format": "b64_json",
            "n": 1
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()

            image_data = data["data"][0]["b64_json"]
            revised_prompt = data["data"][0].get("revised_prompt")

            width, height = map(int, size.split("x"))

            generation_time = time.time() - start_time

            logger.info(f"DALL-E image generated: {size} in {generation_time:.2f}s")

            return {
                "image_data": image_data,
                "format": "png",
                "width": width,
                "height": height,
                "seed": None,
                "time": generation_time,
                "provider": "dalle",
                "model": self.model,
                "revised_prompt": revised_prompt
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"DALL-E API error: {str(e)}")
            raise ImageGenerationError(f"API request failed: {str(e)}")


def get_image_generator(provider: str, **config) -> BaseImageGenerator:
    """
    Factory function to get image generator.

    Args:
        provider: Provider name (stability_ai, replicate, local_sd, dalle)
        **config: Provider-specific configuration

    Returns:
        BaseImageGenerator: Appropriate generator instance
    """
    generators = {
        "stability_ai": StabilityAIGenerator,
        "replicate": ReplicateGenerator,
        "local_sd": LocalStableDiffusionGenerator,
        "dalle": DALLEGenerator
    }

    generator_class = generators.get(provider)
    if not generator_class:
        raise ValueError(f"Unknown provider: {provider}")

    return generator_class(**config)


def save_generated_image(
    image_data: str,
    filename: str,
    format: str = "png",
    upload_to: str = "generated_images"
) -> str:
    """
    Save base64 image to Django media storage.

    Args:
        image_data: Base64 encoded image
        filename: Desired filename (without extension)
        format: Image format (png, jpg)
        upload_to: Directory within MEDIA_ROOT

    Returns:
        str: Path to saved image
    """
    from django.core.files.storage import default_storage

    # Decode base64
    image_bytes = base64.b64decode(image_data)

    # Create file path
    file_path = f"{upload_to}/{filename}.{format}"

    # Save file
    saved_path = default_storage.save(file_path, ContentFile(image_bytes))

    logger.info(f"Image saved: {saved_path}")

    return saved_path
