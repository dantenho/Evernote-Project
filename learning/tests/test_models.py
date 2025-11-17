"""
Comprehensive unit tests for learning app models.
"""
import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from learning.models import Area, Topico, Trilha, Passo, Questao, Alternativa
from .factories import (
    AreaFactory,
    TopicoFactory,
    TrilhaFactory,
    PassoFactory,
    LessonFactory,
    QuizFactory,
    QuestaoFactory,
    AlternativaFactory,
    CorrectAlternativaFactory,
)


@pytest.mark.django_db
@pytest.mark.unit
class TestAreaModel:
    """Test cases for Area model."""

    def test_create_area(self):
        """Test creating an Area instance."""
        area = AreaFactory(title="Python Programming")
        assert area.title == "Python Programming"
        assert area.order >= 0
        assert area.pk is not None

    def test_area_str_representation(self):
        """Test Area __str__ method returns title."""
        area = AreaFactory(title="Data Science")
        assert str(area) == "Data Science"

    def test_area_default_order(self):
        """Test Area default order is 0."""
        area = AreaFactory(order=0)
        assert area.order == 0

    def test_area_ordering(self):
        """Test Areas are ordered by order field."""
        area1 = AreaFactory(order=2)
        area2 = AreaFactory(order=1)
        area3 = AreaFactory(order=3)

        areas = Area.objects.all()
        assert list(areas) == [area2, area1, area3]

    def test_area_verbose_name(self):
        """Test Area meta verbose names."""
        assert Area._meta.verbose_name == "Área"
        assert Area._meta.verbose_name_plural == "Áreas"

    def test_area_title_max_length(self):
        """Test Area title has max_length of 150."""
        field = Area._meta.get_field('title')
        assert field.max_length == 150

    def test_create_multiple_areas(self):
        """Test creating multiple Areas with different orders."""
        areas = AreaFactory.create_batch(5)
        assert Area.objects.count() == 5
        assert len(areas) == 5


@pytest.mark.django_db
@pytest.mark.unit
class TestTopicoModel:
    """Test cases for Topico model."""

    def test_create_topico(self):
        """Test creating a Topico instance."""
        area = AreaFactory()
        topico = TopicoFactory(title="Web Development", area=area)
        assert topico.title == "Web Development"
        assert topico.area == area
        assert topico.pk is not None

    def test_topico_str_representation(self):
        """Test Topico __str__ method returns title."""
        topico = TopicoFactory(title="Django Basics")
        assert str(topico) == "Django Basics"

    def test_topico_area_relationship(self):
        """Test Topico foreign key relationship with Area."""
        area = AreaFactory()
        topico1 = TopicoFactory(area=area)
        topico2 = TopicoFactory(area=area)

        assert topico1.area == area
        assert topico2.area == area
        assert area.topics.count() == 2
        assert list(area.topics.all()) == [topico1, topico2]

    def test_topico_cascade_delete(self):
        """Test deleting an Area cascades to its Topicos."""
        area = AreaFactory()
        topico1 = TopicoFactory(area=area)
        topico2 = TopicoFactory(area=area)

        area_pk = area.pk
        area.delete()

        assert Area.objects.filter(pk=area_pk).count() == 0
        assert Topico.objects.filter(area_id=area_pk).count() == 0

    def test_topico_ordering(self):
        """Test Topicos are ordered by order field."""
        area = AreaFactory()
        topico1 = TopicoFactory(area=area, order=2)
        topico2 = TopicoFactory(area=area, order=1)
        topico3 = TopicoFactory(area=area, order=3)

        topicos = Topico.objects.all()
        assert list(topicos) == [topico2, topico1, topico3]

    def test_topico_verbose_name(self):
        """Test Topico meta verbose names."""
        assert Topico._meta.verbose_name == "Tópico"
        assert Topico._meta.verbose_name_plural == "Tópicos"


@pytest.mark.django_db
@pytest.mark.unit
class TestTrilhaModel:
    """Test cases for Trilha model."""

    def test_create_trilha(self):
        """Test creating a Trilha instance."""
        topico = TopicoFactory()
        trilha = TrilhaFactory(title="Beginner Track", topic=topico)
        assert trilha.title == "Beginner Track"
        assert trilha.topic == topico
        assert trilha.pk is not None

    def test_trilha_str_representation(self):
        """Test Trilha __str__ method returns title."""
        trilha = TrilhaFactory(title="Advanced Track")
        assert str(trilha) == "Advanced Track"

    def test_trilha_topic_relationship(self):
        """Test Trilha foreign key relationship with Topico."""
        topico = TopicoFactory()
        trilha1 = TrilhaFactory(topic=topico)
        trilha2 = TrilhaFactory(topic=topico)

        assert trilha1.topic == topico
        assert trilha2.topic == topico
        assert topico.tracks.count() == 2
        assert list(topico.tracks.all()) == [trilha1, trilha2]

    def test_trilha_cascade_delete_from_topico(self):
        """Test deleting a Topico cascades to its Trilhas."""
        topico = TopicoFactory()
        trilha1 = TrilhaFactory(topic=topico)
        trilha2 = TrilhaFactory(topic=topico)

        topico_pk = topico.pk
        topico.delete()

        assert Topico.objects.filter(pk=topico_pk).count() == 0
        assert Trilha.objects.filter(topic_id=topico_pk).count() == 0

    def test_trilha_cascade_delete_from_area(self):
        """Test deleting an Area cascades through Topico to Trilhas."""
        area = AreaFactory()
        topico = TopicoFactory(area=area)
        trilha = TrilhaFactory(topic=topico)

        area.delete()

        assert Trilha.objects.filter(pk=trilha.pk).count() == 0

    def test_trilha_ordering(self):
        """Test Trilhas are ordered by order field."""
        topico = TopicoFactory()
        trilha1 = TrilhaFactory(topic=topico, order=2)
        trilha2 = TrilhaFactory(topic=topico, order=1)
        trilha3 = TrilhaFactory(topic=topico, order=3)

        trilhas = Trilha.objects.all()
        assert list(trilhas) == [trilha2, trilha1, trilha3]

    def test_trilha_verbose_name(self):
        """Test Trilha meta verbose names."""
        assert Trilha._meta.verbose_name == "Trilha"
        assert Trilha._meta.verbose_name_plural == "Trilhas"


@pytest.mark.django_db
@pytest.mark.unit
class TestPassoModel:
    """Test cases for Passo model."""

    def test_create_lesson_passo(self):
        """Test creating a lesson-type Passo."""
        trilha = TrilhaFactory()
        passo = LessonFactory(
            title="Introduction to Django",
            track=trilha,
            text_content="Django is a web framework"
        )
        assert passo.title == "Introduction to Django"
        assert passo.content_type == Passo.LESSON
        assert passo.text_content == "Django is a web framework"
        assert passo.track == trilha

    def test_create_quiz_passo(self):
        """Test creating a quiz-type Passo."""
        trilha = TrilhaFactory()
        passo = QuizFactory(
            title="Django Quiz",
            track=trilha
        )
        assert passo.title == "Django Quiz"
        assert passo.content_type == Passo.QUIZ
        assert passo.track == trilha

    def test_passo_str_representation(self):
        """Test Passo __str__ method returns title."""
        passo = PassoFactory(title="Step 1")
        assert str(passo) == "Step 1"

    def test_passo_content_type_choices(self):
        """Test Passo content_type has correct choices."""
        assert Passo.LESSON == 'lesson'
        assert Passo.QUIZ == 'quiz'
        assert Passo.CONTENT_CHOICES == (
            ('lesson', 'Lição'),
            ('quiz', 'Quiz'),
        )

    def test_passo_default_content_type(self):
        """Test Passo defaults to LESSON content type."""
        passo = PassoFactory()
        assert passo.content_type == Passo.LESSON

    def test_passo_track_relationship(self):
        """Test Passo foreign key relationship with Trilha."""
        trilha = TrilhaFactory()
        passo1 = PassoFactory(track=trilha)
        passo2 = PassoFactory(track=trilha)

        assert passo1.track == trilha
        assert passo2.track == trilha
        assert trilha.steps.count() == 2
        assert list(trilha.steps.all()) == [passo1, passo2]

    def test_passo_optional_fields(self):
        """Test Passo text_content and video_url can be null/blank."""
        passo = PassoFactory(text_content=None, video_url=None)
        assert passo.text_content is None
        assert passo.video_url is None

    def test_passo_cascade_delete(self):
        """Test deleting a Trilha cascades to its Passos."""
        trilha = TrilhaFactory()
        passo1 = PassoFactory(track=trilha)
        passo2 = PassoFactory(track=trilha)

        trilha_pk = trilha.pk
        trilha.delete()

        assert Trilha.objects.filter(pk=trilha_pk).count() == 0
        assert Passo.objects.filter(track_id=trilha_pk).count() == 0

    def test_passo_ordering(self):
        """Test Passos are ordered by order field."""
        trilha = TrilhaFactory()
        passo1 = PassoFactory(track=trilha, order=2)
        passo2 = PassoFactory(track=trilha, order=1)
        passo3 = PassoFactory(track=trilha, order=3)

        passos = Passo.objects.all()
        assert list(passos) == [passo2, passo1, passo3]

    def test_passo_verbose_name(self):
        """Test Passo meta verbose names."""
        assert Passo._meta.verbose_name == "Passo"
        assert Passo._meta.verbose_name_plural == "Passos"


@pytest.mark.django_db
@pytest.mark.unit
class TestQuestaoModel:
    """Test cases for Questao model."""

    def test_create_questao(self):
        """Test creating a Questao instance."""
        passo = QuizFactory()
        questao = QuestaoFactory(
            step=passo,
            text="What is Django?"
        )
        assert questao.text == "What is Django?"
        assert questao.step == passo
        assert questao.pk is not None

    def test_questao_str_representation(self):
        """Test Questao __str__ method returns text."""
        questao = QuestaoFactory(text="What is Python?")
        assert str(questao) == "What is Python?"

    def test_questao_step_relationship(self):
        """Test Questao foreign key relationship with Passo."""
        passo = QuizFactory()
        questao1 = QuestaoFactory(step=passo)
        questao2 = QuestaoFactory(step=passo)

        assert questao1.step == passo
        assert questao2.step == passo
        assert passo.questions.count() == 2
        assert list(passo.questions.all()) == [questao1, questao2]

    def test_questao_cascade_delete(self):
        """Test deleting a Passo cascades to its Questoes."""
        passo = QuizFactory()
        questao1 = QuestaoFactory(step=passo)
        questao2 = QuestaoFactory(step=passo)

        passo_pk = passo.pk
        passo.delete()

        assert Passo.objects.filter(pk=passo_pk).count() == 0
        assert Questao.objects.filter(step_id=passo_pk).count() == 0

    def test_questao_verbose_name(self):
        """Test Questao meta verbose names."""
        assert Questao._meta.verbose_name == "Questão"
        assert Questao._meta.verbose_name_plural == "Questões"

    def test_multiple_questoes_per_quiz(self):
        """Test a quiz can have multiple questions."""
        passo = QuizFactory()
        questoes = QuestaoFactory.create_batch(5, step=passo)

        assert passo.questions.count() == 5
        assert len(questoes) == 5


@pytest.mark.django_db
@pytest.mark.unit
class TestAlternativaModel:
    """Test cases for Alternativa model."""

    def test_create_alternativa(self):
        """Test creating an Alternativa instance."""
        questao = QuestaoFactory()
        alternativa = AlternativaFactory(
            question=questao,
            text="A web framework",
            is_correct=True
        )
        assert alternativa.text == "A web framework"
        assert alternativa.question == questao
        assert alternativa.is_correct is True
        assert alternativa.pk is not None

    def test_alternativa_str_representation(self):
        """Test Alternativa __str__ method returns text."""
        alternativa = AlternativaFactory(text="Option A")
        assert str(alternativa) == "Option A"

    def test_alternativa_default_is_correct(self):
        """Test Alternativa defaults to is_correct=False."""
        alternativa = AlternativaFactory()
        assert alternativa.is_correct is False

    def test_alternativa_question_relationship(self):
        """Test Alternativa foreign key relationship with Questao."""
        questao = QuestaoFactory()
        alt1 = AlternativaFactory(question=questao, is_correct=True)
        alt2 = AlternativaFactory(question=questao, is_correct=False)
        alt3 = AlternativaFactory(question=questao, is_correct=False)

        assert alt1.question == questao
        assert alt2.question == questao
        assert alt3.question == questao
        assert questao.choices.count() == 3
        assert list(questao.choices.all()) == [alt1, alt2, alt3]

    def test_alternativa_cascade_delete(self):
        """Test deleting a Questao cascades to its Alternativas."""
        questao = QuestaoFactory()
        alt1 = AlternativaFactory(question=questao)
        alt2 = AlternativaFactory(question=questao)

        questao_pk = questao.pk
        questao.delete()

        assert Questao.objects.filter(pk=questao_pk).count() == 0
        assert Alternativa.objects.filter(question_id=questao_pk).count() == 0

    def test_alternativa_verbose_name(self):
        """Test Alternativa meta verbose names."""
        assert Alternativa._meta.verbose_name == "Alternativa"
        assert Alternativa._meta.verbose_name_plural == "Alternativas"

    def test_create_correct_and_incorrect_alternatives(self):
        """Test creating both correct and incorrect alternatives."""
        questao = QuestaoFactory()
        correct = CorrectAlternativaFactory(question=questao)
        incorrect1 = AlternativaFactory(question=questao)
        incorrect2 = AlternativaFactory(question=questao)

        assert correct.is_correct is True
        assert incorrect1.is_correct is False
        assert incorrect2.is_correct is False

    def test_filter_correct_alternatives(self):
        """Test filtering for correct alternatives."""
        questao = QuestaoFactory()
        correct = CorrectAlternativaFactory(question=questao)
        AlternativaFactory(question=questao)
        AlternativaFactory(question=questao)

        correct_choices = questao.choices.filter(is_correct=True)
        assert correct_choices.count() == 1
        assert list(correct_choices) == [correct]


@pytest.mark.django_db
@pytest.mark.unit
class TestModelRelationships:
    """Test complex relationships between models."""

    def test_full_cascade_delete_chain(self):
        """Test deleting Area cascades through all related models."""
        # Create full hierarchy
        area = AreaFactory()
        topico = TopicoFactory(area=area)
        trilha = TrilhaFactory(topic=topico)
        passo = QuizFactory(track=trilha)
        questao = QuestaoFactory(step=passo)
        alternativa = AlternativaFactory(question=questao)

        # Store PKs
        area_pk = area.pk
        topico_pk = topico.pk
        trilha_pk = trilha.pk
        passo_pk = passo.pk
        questao_pk = questao.pk
        alternativa_pk = alternativa.pk

        # Delete area
        area.delete()

        # Verify all related objects are deleted
        assert Area.objects.filter(pk=area_pk).count() == 0
        assert Topico.objects.filter(pk=topico_pk).count() == 0
        assert Trilha.objects.filter(pk=trilha_pk).count() == 0
        assert Passo.objects.filter(pk=passo_pk).count() == 0
        assert Questao.objects.filter(pk=questao_pk).count() == 0
        assert Alternativa.objects.filter(pk=alternativa_pk).count() == 0

    def test_related_name_access(self):
        """Test all related_name attributes work correctly."""
        area = AreaFactory()
        topico = TopicoFactory(area=area)
        trilha = TrilhaFactory(topic=topico)
        passo = QuizFactory(track=trilha)
        questao = QuestaoFactory(step=passo)
        alternativa = AlternativaFactory(question=questao)

        # Test related_name access
        assert area.topics.first() == topico
        assert topico.tracks.first() == trilha
        assert trilha.steps.first() == passo
        assert passo.questions.first() == questao
        assert questao.choices.first() == alternativa

    def test_complex_hierarchy_ordering(self):
        """Test ordering works correctly in a complex hierarchy."""
        area = AreaFactory(order=1)
        topico1 = TopicoFactory(area=area, order=2)
        topico2 = TopicoFactory(area=area, order=1)
        trilha1 = TrilhaFactory(topic=topico1, order=2)
        trilha2 = TrilhaFactory(topic=topico1, order=1)

        # Verify ordering
        assert list(area.topics.all()) == [topico2, topico1]
        assert list(topico1.tracks.all()) == [trilha2, trilha1]


@pytest.mark.django_db
@pytest.mark.unit
class TestAlternativaValidation:
    """Test validation logic for the Alternativa model."""

    def test_prevent_multiple_correct_answers_on_create(self):
        """Test validation prevents creating multiple correct answers."""
        questao = QuestaoFactory()
        CorrectAlternativaFactory(question=questao)

        # Try to create another correct answer
        with pytest.raises(ValidationError, match="This question already has a correct answer."):
            CorrectAlternativaFactory(question=questao).full_clean()

    def test_prevent_multiple_correct_answers_on_update(self):
        """Test validation prevents updating to multiple correct answers."""
        questao = QuestaoFactory()
        CorrectAlternativaFactory(question=questao)
        incorrect_choice = AlternativaFactory(question=questao, is_correct=False)

        # Try to mark the incorrect answer as correct
        incorrect_choice.is_correct = True
        with pytest.raises(ValidationError, match="This question already has a correct answer."):
            incorrect_choice.full_clean()

    def test_prevent_removing_last_correct_answer(self):
        """Test validation prevents removing the last correct answer."""
        questao = QuestaoFactory()
        correct_choice = CorrectAlternativaFactory(question=questao)
        AlternativaFactory(question=questao, is_correct=False)

        # Try to unmark the only correct answer
        correct_choice.is_correct = False
        with pytest.raises(ValidationError, match="A question must have at least one correct answer."):
            correct_choice.full_clean()

    def test_allow_saving_correct_answer(self):
        """Test that saving an existing correct answer is allowed."""
        correct_choice = CorrectAlternativaFactory()
        correct_choice.text = "Updated text"
        try:
            correct_choice.full_clean()
        except ValidationError:
            pytest.fail("Saving a correct answer raised a ValidationError unexpectedly.")
