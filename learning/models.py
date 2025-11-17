from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Area(models.Model):
    title = models.CharField(max_length=150, verbose_name="Título")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Ordem")

    class Meta:
        ordering = ['order']
        verbose_name = "Área"
        verbose_name_plural = "Áreas"

    def __str__(self):
        return self.title

class Topico(models.Model):
    title = models.CharField(max_length=150, verbose_name="Título")
    area = models.ForeignKey(Area, related_name='topics', on_delete=models.CASCADE, verbose_name="Área")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Ordem")

    class Meta:
        ordering = ['order']
        verbose_name = "Tópico"
        verbose_name_plural = "Tópicos"

    def __str__(self):
        return self.title

class Trilha(models.Model):
    title = models.CharField(max_length=150, verbose_name="Título")
    topic = models.ForeignKey(Topico, related_name='tracks', on_delete=models.CASCADE, verbose_name="Tópico")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Ordem")
    # TODO: Implementar a lógica para pré-requisitos entre trilhas.

    class Meta:
        ordering = ['order']
        verbose_name = "Trilha"
        verbose_name_plural = "Trilhas"

    def __str__(self):
        return self.title

class Passo(models.Model):
    LESSON = 'lesson'
    QUIZ = 'quiz'
    CONTENT_CHOICES = (
        (LESSON, 'Lição'),
        (QUIZ, 'Quiz'),
    )

    title = models.CharField(max_length=150, verbose_name="Título")
    track = models.ForeignKey(Trilha, related_name='steps', on_delete=models.CASCADE, verbose_name="Trilha")
    content_type = models.CharField(max_length=10, choices=CONTENT_CHOICES, default=LESSON, verbose_name="Tipo de Conteúdo")
    text_content = models.TextField(blank=True, null=True, verbose_name="Conteúdo em Texto")
    video_url = models.URLField(blank=True, null=True, verbose_name="URL do Vídeo")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Ordem")

    class Meta:
        ordering = ['order']
        verbose_name = "Passo"
        verbose_name_plural = "Passos"

    def __str__(self):
        return self.title

class Questao(models.Model):
    step = models.ForeignKey(Passo, related_name='questions', on_delete=models.CASCADE, verbose_name="Passo (Quiz)")
    text = models.TextField(verbose_name="Texto da Questão")

    class Meta:
        verbose_name = "Questão"
        verbose_name_plural = "Questões"

    def __str__(self):
        return self.text

class Alternativa(models.Model):
    question = models.ForeignKey(Questao, related_name='choices', on_delete=models.CASCADE, verbose_name="Questão")
    text = models.CharField(max_length=255, verbose_name="Texto da Alternativa")
    is_correct = models.BooleanField(default=False, verbose_name="É a correta?")

    class Meta:
        verbose_name = "Alternativa"
        verbose_name_plural = "Alternativas"

    def __str__(self):
        return self.text


class UserProgress(models.Model):
    """Track user progress through learning steps."""

    COMPLETED = 'completed'
    IN_PROGRESS = 'in_progress'
    STATUS_CHOICES = (
        (COMPLETED, 'Completed'),
        (IN_PROGRESS, 'In Progress'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name="Usuário"
    )
    step = models.ForeignKey(
        Passo,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name="Passo"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=IN_PROGRESS,
        verbose_name="Status"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Completado em"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Progresso do Usuário"
        verbose_name_plural = "Progressos dos Usuários"
        ordering = ['-updated_at']
        unique_together = ('user', 'step')
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['step', 'status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.step.title} ({self.status})"

    def mark_as_completed(self):
        """Mark this step as completed."""
        self.status = self.COMPLETED
        self.completed_at = timezone.now()
        self.save()
