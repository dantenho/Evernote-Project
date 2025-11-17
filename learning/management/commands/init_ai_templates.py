"""
Management command to initialize default AI content templates.

Usage:
    python manage.py init_ai_templates
"""

from django.core.management.base import BaseCommand
from learning.models import ContentTemplate


class Command(BaseCommand):
    help = 'Initialize default AI content generation templates'

    def handle(self, *args, **options):
        """Create default content templates if they don't exist."""

        templates_created = 0
        templates_updated = 0

        # ====================================================================
        # Step Lesson Template
        # ====================================================================

        lesson_template, created = ContentTemplate.objects.update_or_create(
            name='Default Step Lesson',
            defaults={
                'content_type': ContentTemplate.STEP_LESSON,
                'is_active': True,
                'system_prompt': """You are an expert educational content creator. Your task is to generate engaging, comprehensive lesson content for online learning platforms.

Your lessons should:
- Be clear, well-structured, and easy to understand
- Include practical examples and real-world applications
- Use a friendly, encouraging tone
- Break down complex concepts into digestible parts
- Include clear learning objectives

Return your response as valid JSON with the following structure:
{
    "title": "Lesson title",
    "content": "Full lesson content in markdown format",
    "learning_objectives": ["objective 1", "objective 2"],
    "key_concepts": ["concept 1", "concept 2"],
    "examples": [{"title": "Example 1", "description": "..."}],
    "summary": "Brief summary of the lesson"
}""",
                'user_prompt_template': """Create a comprehensive lesson on the following topic:

Topic: {{topic}}
Difficulty Level: {{difficulty}}
Language: {{language}}

Additional Context: {{additional_context}}

Please generate a complete lesson that covers the fundamentals and practical applications of this topic. The lesson should be appropriate for {{difficulty}} level learners and written in {{language}}."""
            }
        )

        if created:
            templates_created += 1
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {lesson_template.name}'))
        else:
            templates_updated += 1
            self.stdout.write(self.style.WARNING(f'↻ Updated: {lesson_template.name}'))

        # ====================================================================
        # Quiz Questions Template
        # ====================================================================

        quiz_template, created = ContentTemplate.objects.update_or_create(
            name='Default Quiz Questions',
            defaults={
                'content_type': ContentTemplate.QUIZ_QUESTIONS,
                'is_active': True,
                'system_prompt': """You are an expert at creating educational quiz questions. Your questions should:
- Test understanding, not just memorization
- Be clear and unambiguous
- Have one clearly correct answer
- Include plausible distractors (wrong answers)
- Cover a range of difficulty within the topic
- Use positive language (avoid double negatives)

Return your response as valid JSON with the following structure:
{
    "questions": [
        {
            "question_text": "The question text",
            "options": [
                {"text": "Option A", "is_correct": false, "explanation": "Why this is wrong"},
                {"text": "Option B", "is_correct": true, "explanation": "Why this is correct"},
                {"text": "Option C", "is_correct": false, "explanation": "Why this is wrong"},
                {"text": "Option D", "is_correct": false, "explanation": "Why this is wrong"}
            ],
            "difficulty": "easy|medium|hard",
            "topic_area": "Specific aspect of the topic"
        }
    ]
}""",
                'user_prompt_template': """Create {{num_questions}} multiple-choice quiz questions on the following topic:

Topic: {{topic}}
Difficulty Level: {{difficulty}}
Language: {{language}}

Each question should have 4 options with only one correct answer. Include explanations for why each answer is correct or incorrect. Ensure the questions are appropriate for {{difficulty}} level learners and written in {{language}}."""
            }
        )

        if created:
            templates_created += 1
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {quiz_template.name}'))
        else:
            templates_updated += 1
            self.stdout.write(self.style.WARNING(f'↻ Updated: {quiz_template.name}'))

        # ====================================================================
        # Step Quiz Template (for generating quiz-type steps)
        # ====================================================================

        step_quiz_template, created = ContentTemplate.objects.update_or_create(
            name='Default Step Quiz',
            defaults={
                'content_type': ContentTemplate.STEP_QUIZ,
                'is_active': True,
                'system_prompt': """You are an expert at creating concise quiz questions for learning steps. Each quiz should:
- Have 3-5 questions
- Test key concepts from the step
- Be quick to complete (2-3 minutes)
- Provide immediate learning value

Return your response as valid JSON with the following structure:
{
    "title": "Quiz title",
    "description": "Brief description of what this quiz tests",
    "questions": [
        {
            "question_text": "The question text",
            "options": [
                {"text": "Option A", "is_correct": false},
                {"text": "Option B", "is_correct": true},
                {"text": "Option C", "is_correct": false}
            ],
            "explanation": "Explanation of the correct answer"
        }
    ]
}""",
                'user_prompt_template': """Create a short quiz to test understanding of:

Topic: {{topic}}
Difficulty Level: {{difficulty}}
Language: {{language}}

Generate 3-5 multiple-choice questions. Keep it concise and focused on the core concepts. Questions should be in {{language}} and appropriate for {{difficulty}} level learners."""
            }
        )

        if created:
            templates_created += 1
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {step_quiz_template.name}'))
        else:
            templates_updated += 1
            self.stdout.write(self.style.WARNING(f'↻ Updated: {step_quiz_template.name}'))

        # ====================================================================
        # Summary
        # ====================================================================

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS(f'Templates Created: {templates_created}'))
        self.stdout.write(self.style.WARNING(f'Templates Updated: {templates_updated}'))
        self.stdout.write(self.style.SUCCESS(f'Total Templates: {templates_created + templates_updated}'))
        self.stdout.write(self.style.SUCCESS('='*60))

        if templates_created > 0:
            self.stdout.write('')
            self.stdout.write('Next steps:')
            self.stdout.write('1. Configure AI providers in Django admin')
            self.stdout.write('2. Add API keys for your chosen providers')
            self.stdout.write('3. Test content generation via API or admin interface')
