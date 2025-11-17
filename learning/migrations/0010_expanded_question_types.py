# Generated migration for expanded question types

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0009_add_avatar_fields'),
    ]

    operations = [
        # Add question_type field to Questao
        migrations.AddField(
            model_name='questao',
            name='question_type',
            field=models.CharField(
                choices=[
                    ('multiple_choice', 'Multiple Choice'),
                    ('reorder', 'Reorder Items'),
                    ('fill_blank', 'Fill in the Blank'),
                    ('short_answer', 'Short Answer'),
                    ('long_answer', 'Long Answer (Essay)'),
                    ('true_false', 'True/False'),
                    ('matching', 'Matching'),
                ],
                default='multiple_choice',
                help_text='Type of question',
                max_length=20,
                verbose_name='Question Type'
            ),
        ),

        # Add correct_answer field for text-based answers
        migrations.AddField(
            model_name='questao',
            name='correct_answer',
            field=models.TextField(
                blank=True,
                null=True,
                help_text='Correct answer for fill-in-blank and short answer questions',
                verbose_name='Correct Answer'
            ),
        ),

        # Add correct_order field for reorder questions
        migrations.AddField(
            model_name='questao',
            name='correct_order',
            field=models.JSONField(
                blank=True,
                null=True,
                help_text='Correct order of items for reorder questions (array of choice IDs)',
                verbose_name='Correct Order'
            ),
        ),

        # Add validation_type for short answers
        migrations.AddField(
            model_name='questao',
            name='validation_type',
            field=models.CharField(
                choices=[
                    ('exact', 'Exact Match'),
                    ('case_insensitive', 'Case Insensitive'),
                    ('contains', 'Contains Keyword'),
                    ('regex', 'Regular Expression'),
                ],
                default='case_insensitive',
                help_text='How to validate short answer responses',
                max_length=20,
                verbose_name='Validation Type'
            ),
        ),

        # Add blank_position for fill-in-blank questions
        migrations.AddField(
            model_name='questao',
            name='blank_position',
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                help_text='Position of the blank in the text (for fill-in-blank)',
                verbose_name='Blank Position'
            ),
        ),

        # Add max_length for text answers
        migrations.AddField(
            model_name='questao',
            name='max_answer_length',
            field=models.PositiveIntegerField(
                default=500,
                validators=[django.core.validators.MinValueValidator(10)],
                help_text='Maximum character length for text answers',
                verbose_name='Max Answer Length'
            ),
        ),

        # Add points field
        migrations.AddField(
            model_name='questao',
            name='points',
            field=models.PositiveSmallIntegerField(
                default=10,
                validators=[django.core.validators.MinValueValidator(1)],
                help_text='Points awarded for correct answer',
                verbose_name='Points'
            ),
        ),

        # Add hint field
        migrations.AddField(
            model_name='questao',
            name='hint',
            field=models.TextField(
                blank=True,
                null=True,
                help_text='Optional hint shown to user',
                verbose_name='Hint'
            ),
        ),

        # Model for generated images
        migrations.CreateModel(
            name='GeneratedImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt', models.TextField(help_text='Text prompt used to generate image', verbose_name='Prompt')),
                ('negative_prompt', models.TextField(blank=True, help_text='Negative prompt (what to avoid)', null=True, verbose_name='Negative Prompt')),
                ('provider', models.CharField(choices=[('stability_ai', 'Stability AI'), ('replicate', 'Replicate'), ('local_sd', 'Local Stable Diffusion'), ('dalle', 'DALL-E')], help_text='AI provider used', max_length=50, verbose_name='Provider')),
                ('model', models.CharField(help_text='Specific model used', max_length=200, verbose_name='Model')),
                ('image', models.ImageField(help_text='Generated image file', upload_to='generated_images/', verbose_name='Image')),
                ('width', models.PositiveIntegerField(help_text='Image width in pixels', verbose_name='Width')),
                ('height', models.PositiveIntegerField(help_text='Image height in pixels', verbose_name='Height')),
                ('seed', models.BigIntegerField(blank=True, help_text='Random seed used', null=True, verbose_name='Seed')),
                ('guidance_scale', models.FloatField(default=7.5, help_text='Guidance scale parameter', verbose_name='Guidance Scale')),
                ('num_inference_steps', models.PositiveIntegerField(default=50, help_text='Number of inference steps', verbose_name='Inference Steps')),
                ('generation_time', models.FloatField(help_text='Time taken to generate (seconds)', verbose_name='Generation Time')),
                ('user', models.ForeignKey(help_text='User who generated the image', on_delete=models.deletion.CASCADE, related_name='generated_images', to='auth.user', verbose_name='User')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('is_public', models.BooleanField(default=False, help_text='Whether image is publicly visible', verbose_name='Public')),
                ('tags', models.JSONField(blank=True, default=list, help_text='Tags for categorization', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'Generated Image',
                'verbose_name_plural': 'Generated Images',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['user', '-created_at'], name='learning_ge_user_id_created_idx'),
                    models.Index(fields=['provider'], name='learning_ge_provider_idx'),
                ],
            },
        ),

        # Index for question_type
        migrations.AddIndex(
            model_name='questao',
            index=models.Index(fields=['question_type'], name='learning_qu_quest_type_idx'),
        ),
    ]
