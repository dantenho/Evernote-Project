from django.db import models

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
