# Migration for new XP system

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0010_expanded_question_types'),
    ]

    operations = [
        # Track completed tracks per user
        migrations.CreateModel(
            name='UserTrackCompletion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='completed_tracks',
                    to='auth.user',
                    verbose_name='User'
                )),
                ('track', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='user_completions',
                    to='learning.trilha',
                    verbose_name='Track'
                )),
                ('completed_at', models.DateTimeField(auto_now_add=True, verbose_name='Completed At')),
                ('xp_awarded', models.PositiveIntegerField(default=100, verbose_name='XP Awarded')),
                ('completion_time_seconds', models.PositiveIntegerField(
                    null=True,
                    blank=True,
                    help_text='Time taken to complete track in seconds',
                    verbose_name='Completion Time'
                )),
            ],
            options={
                'verbose_name': 'User Track Completion',
                'verbose_name_plural': 'User Track Completions',
                'ordering': ['-completed_at'],
                'unique_together': [['user', 'track']],
                'indexes': [
                    models.Index(fields=['user', '-completed_at'], name='learning_ut_user_completed_idx'),
                    models.Index(fields=['track'], name='learning_ut_track_idx'),
                ],
            },
        ),

        # Track completed topics per user
        migrations.CreateModel(
            name='UserTopicCompletion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='completed_topics',
                    to='auth.user',
                    verbose_name='User'
                )),
                ('topic', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='user_completions',
                    to='learning.topico',
                    verbose_name='Topic'
                )),
                ('completed_at', models.DateTimeField(auto_now_add=True, verbose_name='Completed At')),
                ('xp_awarded', models.PositiveIntegerField(default=1000, verbose_name='XP Awarded')),
                ('completion_percentage', models.FloatField(
                    default=100.0,
                    help_text='Percentage of topic completed',
                    verbose_name='Completion %'
                )),
                ('tracks_completed', models.PositiveIntegerField(
                    default=0,
                    help_text='Number of tracks completed in this topic',
                    verbose_name='Tracks Completed'
                )),
            ],
            options={
                'verbose_name': 'User Topic Completion',
                'verbose_name_plural': 'User Topic Completions',
                'ordering': ['-completed_at'],
                'unique_together': [['user', 'topic']],
                'indexes': [
                    models.Index(fields=['user', '-completed_at'], name='learning_uto_user_completed_idx'),
                    models.Index(fields=['topic'], name='learning_uto_topic_idx'),
                ],
            },
        ),

        # Add XP reward fields to Track and Topic
        migrations.AddField(
            model_name='trilha',
            name='xp_reward',
            field=models.PositiveIntegerField(
                default=100,
                help_text='XP awarded for completing this track',
                verbose_name='XP Reward'
            ),
        ),

        migrations.AddField(
            model_name='topico',
            name='bonus_xp_reward',
            field=models.PositiveIntegerField(
                default=1000,
                help_text='Bonus XP awarded for completing entire topic',
                verbose_name='Bonus XP Reward'
            ),
        ),

        # Add progress tracking fields to UserProfile
        migrations.AddField(
            model_name='userprofile',
            name='tracks_completed_count',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Total number of tracks completed',
                verbose_name='Tracks Completed'
            ),
        ),

        migrations.AddField(
            model_name='userprofile',
            name='topics_completed_count',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Total number of topics completed',
                verbose_name='Topics Completed'
            ),
        ),

        migrations.AddField(
            model_name='userprofile',
            name='total_bonus_xp',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Total bonus XP earned from topic completions',
                verbose_name='Total Bonus XP'
            ),
        ),
    ]
