"""
API views for AI content generation.

Provides endpoints for generating educational content using AI providers.
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import AIProvider, ContentTemplate, GeneratedContent
from .ai_services import generate_content

logger = logging.getLogger(__name__)


# ============================================================================
# AI Provider Management
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_ai_providers(request):
    """
    Get list of available AI providers.

    Returns:
        200: List of active AI providers
    """
    providers = AIProvider.objects.filter(is_active=True)

    providers_data = [{
        'id': p.id,
        'name': p.name,
        'provider_type': p.provider_type,
        'provider_type_display': p.get_provider_type_display(),
        'model_name': p.model_name,
        'max_tokens': p.max_tokens,
        'temperature': p.temperature,
    } for p in providers]

    return Response({
        'count': len(providers_data),
        'providers': providers_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_content_templates(request):
    """
    Get list of available content templates.

    Query params:
        content_type: Filter by content type (optional)

    Returns:
        200: List of active templates
    """
    templates = ContentTemplate.objects.filter(is_active=True)

    # Filter by content type if provided
    content_type = request.query_params.get('content_type')
    if content_type:
        templates = templates.filter(content_type=content_type)

    templates_data = [{
        'id': t.id,
        'name': t.name,
        'content_type': t.content_type,
        'content_type_display': t.get_content_type_display(),
        'system_prompt': t.system_prompt,
        'user_prompt_template': t.user_prompt_template,
    } for t in templates]

    return Response({
        'count': len(templates_data),
        'templates': templates_data
    })


# ============================================================================
# Content Generation
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_step_lesson(request):
    """
    Generate a lesson step using AI.

    Request body:
        provider_id: int - AI provider ID
        template_id: int - Content template ID (optional, uses default)
        topic: str - Topic for the lesson
        difficulty: str - Difficulty level (beginner/intermediate/advanced)
        language: str - Language (default: Portuguese)
        additional_context: str - Additional context (optional)

    Returns:
        200: Generated content
        400: Validation error
        500: Generation error
    """
    provider_id = request.data.get('provider_id')
    template_id = request.data.get('template_id')
    topic = request.data.get('topic')
    difficulty = request.data.get('difficulty', 'intermediate')
    language = request.data.get('language', 'Portuguese')
    additional_context = request.data.get('additional_context', '')

    # Validation
    if not provider_id:
        return Response(
            {'error': 'provider_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if not topic:
        return Response(
            {'error': 'topic is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get default template if not provided
    if not template_id:
        try:
            template = ContentTemplate.objects.get(
                content_type=ContentTemplate.STEP_LESSON,
                is_active=True
            )
            template_id = template.id
        except ContentTemplate.DoesNotExist:
            return Response(
                {'error': 'No default template found for lesson steps'},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Generate content
    result = generate_content(
        provider_id=provider_id,
        template_id=template_id,
        user=request.user,
        topic=topic,
        difficulty=difficulty,
        language=language,
        additional_context=additional_context
    )

    if result['success']:
        return Response({
            'success': True,
            'generated_text': result['text'],
            'parsed_content': result['parsed_content'],
            'tokens_used': result['tokens'],
            'generation_time': result['time'],
            'generation_id': result['generated_content_id']
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'error': result['error']
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_quiz_questions(request):
    """
    Generate quiz questions using AI.

    Request body:
        provider_id: int - AI provider ID
        template_id: int - Content template ID (optional)
        topic: str - Topic for the quiz
        num_questions: int - Number of questions (default: 5)
        difficulty: str - Difficulty level
        language: str - Language (default: Portuguese)

    Returns:
        200: Generated questions
        400: Validation error
        500: Generation error
    """
    provider_id = request.data.get('provider_id')
    template_id = request.data.get('template_id')
    topic = request.data.get('topic')
    num_questions = request.data.get('num_questions', 5)
    difficulty = request.data.get('difficulty', 'intermediate')
    language = request.data.get('language', 'Portuguese')

    # Validation
    if not provider_id:
        return Response(
            {'error': 'provider_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if not topic:
        return Response(
            {'error': 'topic is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get default template if not provided
    if not template_id:
        try:
            template = ContentTemplate.objects.get(
                content_type=ContentTemplate.QUIZ_QUESTIONS,
                is_active=True
            )
            template_id = template.id
        except ContentTemplate.DoesNotExist:
            return Response(
                {'error': 'No default template found for quiz questions'},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Generate content
    result = generate_content(
        provider_id=provider_id,
        template_id=template_id,
        user=request.user,
        topic=topic,
        num_questions=num_questions,
        difficulty=difficulty,
        language=language
    )

    if result['success']:
        return Response({
            'success': True,
            'generated_text': result['text'],
            'parsed_content': result['parsed_content'],
            'tokens_used': result['tokens'],
            'generation_time': result['time'],
            'generation_id': result['generated_content_id']
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'error': result['error']
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generation_history(request):
    """
    Get user's content generation history.

    Query params:
        limit: int - Number of records to return (default: 20)

    Returns:
        200: List of generation records
    """
    limit = int(request.query_params.get('limit', 20))

    generations = GeneratedContent.objects.filter(
        user=request.user
    ).select_related('provider', 'template')[:limit]

    history_data = [{
        'id': g.id,
        'provider': g.provider.name if g.provider else None,
        'template': g.template.name if g.template else None,
        'content_type': g.template.get_content_type_display() if g.template else None,
        'was_successful': g.was_successful,
        'tokens_used': g.tokens_used,
        'generation_time': g.generation_time,
        'created_at': g.created_at.isoformat(),
        'preview': g.generated_text[:200] if g.was_successful else g.error_message[:200],
    } for g in generations]

    return Response({
        'count': len(history_data),
        'history': history_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generation_detail(request, generation_id):
    """
    Get full details of a generated content.

    Args:
        generation_id: ID of generated content

    Returns:
        200: Full generation details
        404: Not found
    """
    generation = get_object_or_404(
        GeneratedContent,
        id=generation_id,
        user=request.user
    )

    return Response({
        'id': generation.id,
        'provider': {
            'name': generation.provider.name if generation.provider else None,
            'type': generation.provider.provider_type if generation.provider else None,
        },
        'template': {
            'name': generation.template.name if generation.template else None,
            'type': generation.template.content_type if generation.template else None,
        },
        'prompt': generation.prompt,
        'generated_text': generation.generated_text,
        'parsed_content': generation.parsed_content,
        'tokens_used': generation.tokens_used,
        'generation_time': generation.generation_time,
        'was_successful': generation.was_successful,
        'error_message': generation.error_message,
        'created_at': generation.created_at.isoformat(),
    })
