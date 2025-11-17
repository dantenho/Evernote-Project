"""
Factory Boy factories for creating test data.
"""
import factory
from factory.django import DjangoModelFactory
from faker import Faker

from learning.models import Area, Topico, Trilha, Passo, Questao, Alternativa

fake = Faker('pt_BR')


class AreaFactory(DjangoModelFactory):
    """Factory for creating Area instances."""

    class Meta:
        model = Area

    title = factory.Sequence(lambda n: f"Área {n}")
    order = factory.Sequence(lambda n: n)


class TopicoFactory(DjangoModelFactory):
    """Factory for creating Topico instances."""

    class Meta:
        model = Topico

    title = factory.Sequence(lambda n: f"Tópico {n}")
    area = factory.SubFactory(AreaFactory)
    order = factory.Sequence(lambda n: n)


class TrilhaFactory(DjangoModelFactory):
    """Factory for creating Trilha instances."""

    class Meta:
        model = Trilha

    title = factory.Sequence(lambda n: f"Trilha {n}")
    topic = factory.SubFactory(TopicoFactory)
    order = factory.Sequence(lambda n: n)


class PassoFactory(DjangoModelFactory):
    """Factory for creating Passo instances."""

    class Meta:
        model = Passo

    title = factory.Sequence(lambda n: f"Passo {n}")
    track = factory.SubFactory(TrilhaFactory)
    content_type = Passo.LESSON
    text_content = factory.Faker('paragraph', locale='pt_BR')
    video_url = factory.Faker('url')
    order = factory.Sequence(lambda n: n)


class LessonFactory(PassoFactory):
    """Factory for creating lesson-type Passo instances."""

    content_type = Passo.LESSON
    text_content = factory.Faker('paragraph', locale='pt_BR')
    video_url = factory.Faker('url')


class QuizFactory(PassoFactory):
    """Factory for creating quiz-type Passo instances."""

    content_type = Passo.QUIZ
    text_content = factory.Faker('paragraph', locale='pt_BR')
    video_url = None


class QuestaoFactory(DjangoModelFactory):
    """Factory for creating Questao instances."""

    class Meta:
        model = Questao

    step = factory.SubFactory(QuizFactory)
    text = factory.Faker('sentence', locale='pt_BR')


class AlternativaFactory(DjangoModelFactory):
    """Factory for creating Alternativa instances."""

    class Meta:
        model = Alternativa

    question = factory.SubFactory(QuestaoFactory)
    text = factory.Faker('sentence', locale='pt_BR')
    is_correct = False


class CorrectAlternativaFactory(AlternativaFactory):
    """Factory for creating correct Alternativa instances."""

    is_correct = True
