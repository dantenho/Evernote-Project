"""
Tests for Django admin interface configuration.
"""
import pytest
from django.contrib import admin
from django.contrib.auth.models import User
from django.test import RequestFactory

from learning.models import Area, Topico, Trilha, Passo, Questao, Alternativa
from learning.admin import (
    AreaAdmin,
    TopicoAdmin,
    TrilhaAdmin,
    PassoAdmin,
    QuestaoAdmin,
    AlternativaAdmin,
    TopicoInline,
    TrilhaInline,
    PassoInline,
    QuestaoInline,
    AlternativaInline,
)
from .factories import (
    AreaFactory,
    TopicoFactory,
    TrilhaFactory,
    LessonFactory,
    QuizFactory,
    QuestaoFactory,
    AlternativaFactory,
)


@pytest.mark.django_db
@pytest.mark.unit
class TestAdminRegistration:
    """Test that all models are registered in admin."""

    def test_area_is_registered(self):
        """Test Area model is registered in admin."""
        assert admin.site.is_registered(Area)

    def test_topico_is_registered(self):
        """Test Topico model is registered in admin."""
        assert admin.site.is_registered(Topico)

    def test_trilha_is_registered(self):
        """Test Trilha model is registered in admin."""
        assert admin.site.is_registered(Trilha)

    def test_passo_is_registered(self):
        """Test Passo model is registered in admin."""
        assert admin.site.is_registered(Passo)

    def test_questao_is_registered(self):
        """Test Questao model is registered in admin."""
        assert admin.site.is_registered(Questao)

    def test_alternativa_is_registered(self):
        """Test Alternativa model is registered in admin."""
        assert admin.site.is_registered(Alternativa)

    def test_correct_admin_classes(self):
        """Test correct admin classes are used."""
        assert isinstance(admin.site._registry[Area], AreaAdmin)
        assert isinstance(admin.site._registry[Topico], TopicoAdmin)
        assert isinstance(admin.site._registry[Trilha], TrilhaAdmin)
        assert isinstance(admin.site._registry[Passo], PassoAdmin)
        assert isinstance(admin.site._registry[Questao], QuestaoAdmin)
        assert isinstance(admin.site._registry[Alternativa], AlternativaAdmin)


@pytest.mark.django_db
@pytest.mark.unit
class TestAreaAdmin:
    """Test AreaAdmin configuration."""

    def test_area_list_display(self):
        """Test Area admin list_display configuration."""
        assert AreaAdmin.list_display == ('title', 'order')

    def test_area_has_topico_inline(self):
        """Test Area admin has TopicoInline."""
        assert TopicoInline in AreaAdmin.inlines

    def test_topico_inline_configuration(self):
        """Test TopicoInline configuration."""
        assert TopicoInline.model == Topico
        assert TopicoInline.extra == 1
        assert TopicoInline.ordering == ('order',)

    def test_area_admin_display_in_list(self):
        """Test Area displays correctly in admin list."""
        area = AreaFactory(title="Test Area", order=1)
        area_admin = AreaAdmin(Area, admin.site)

        # Get list display values
        title_display = area_admin.list_display[0]
        order_display = area_admin.list_display[1]

        # Verify they match
        assert getattr(area, title_display) == "Test Area"
        assert getattr(area, order_display) == 1


@pytest.mark.django_db
@pytest.mark.unit
class TestTopicoAdmin:
    """Test TopicoAdmin configuration."""

    def test_topico_list_display(self):
        """Test Topico admin list_display configuration."""
        assert TopicoAdmin.list_display == ('title', 'area', 'order')

    def test_topico_list_filter(self):
        """Test Topico admin list_filter configuration."""
        assert TopicoAdmin.list_filter == ('area',)

    def test_topico_has_trilha_inline(self):
        """Test Topico admin has TrilhaInline."""
        assert TrilhaInline in TopicoAdmin.inlines

    def test_trilha_inline_configuration(self):
        """Test TrilhaInline configuration."""
        assert TrilhaInline.model == Trilha
        assert TrilhaInline.extra == 1
        assert TrilhaInline.ordering == ('order',)


@pytest.mark.django_db
@pytest.mark.unit
class TestTrilhaAdmin:
    """Test TrilhaAdmin configuration."""

    def test_trilha_list_display(self):
        """Test Trilha admin list_display configuration."""
        assert TrilhaAdmin.list_display == ('title', 'topic', 'order')

    def test_trilha_list_filter(self):
        """Test Trilha admin list_filter configuration."""
        assert TrilhaAdmin.list_filter == ('topic__area', 'topic')

    def test_trilha_has_passo_inline(self):
        """Test Trilha admin has PassoInline."""
        assert PassoInline in TrilhaAdmin.inlines

    def test_passo_inline_configuration(self):
        """Test PassoInline configuration."""
        assert PassoInline.model == Passo
        assert PassoInline.extra == 1
        assert PassoInline.ordering == ('order',)

    def test_trilha_filtering_by_area(self):
        """Test TrilhaAdmin can filter by topic__area."""
        area1 = AreaFactory(title="Area 1")
        area2 = AreaFactory(title="Area 2")
        topico1 = TopicoFactory(area=area1)
        topico2 = TopicoFactory(area=area2)
        trilha1 = TrilhaFactory(topic=topico1)
        trilha2 = TrilhaFactory(topic=topico2)

        # Verify we can filter by area through topic
        trilhas_area1 = Trilha.objects.filter(topic__area=area1)
        trilhas_area2 = Trilha.objects.filter(topic__area=area2)

        assert list(trilhas_area1) == [trilha1]
        assert list(trilhas_area2) == [trilha2]


@pytest.mark.django_db
@pytest.mark.unit
class TestPassoAdmin:
    """Test PassoAdmin configuration."""

    def test_passo_list_display(self):
        """Test Passo admin list_display configuration."""
        assert PassoAdmin.list_display == ('title', 'track', 'content_type', 'order')

    def test_passo_list_filter(self):
        """Test Passo admin list_filter configuration."""
        expected_filters = ('track__topic__area', 'track__topic', 'track', 'content_type')
        assert PassoAdmin.list_filter == expected_filters

    def test_passo_quiz_has_questao_inline(self):
        """Test quiz-type Passo shows QuestaoInline."""
        quiz = QuizFactory()
        passo_admin = PassoAdmin(Passo, admin.site)
        factory = RequestFactory()
        request = factory.get('/')

        inlines = passo_admin.get_inlines(request, quiz)
        assert QuestaoInline in inlines

    def test_passo_lesson_no_questao_inline(self):
        """Test lesson-type Passo doesn't show QuestaoInline."""
        lesson = LessonFactory()
        passo_admin = PassoAdmin(Passo, admin.site)
        factory = RequestFactory()
        request = factory.get('/')

        inlines = passo_admin.get_inlines(request, lesson)
        assert QuestaoInline not in inlines
        assert inlines == []

    def test_passo_new_object_no_inline(self):
        """Test new Passo (obj=None) has no inlines."""
        passo_admin = PassoAdmin(Passo, admin.site)
        factory = RequestFactory()
        request = factory.get('/')

        inlines = passo_admin.get_inlines(request, obj=None)
        assert inlines == []

    def test_questao_inline_configuration(self):
        """Test QuestaoInline configuration."""
        assert QuestaoInline.model == Questao
        assert QuestaoInline.extra == 1


@pytest.mark.django_db
@pytest.mark.unit
class TestQuestaoAdmin:
    """Test QuestaoAdmin configuration."""

    def test_questao_list_display(self):
        """Test Questao admin list_display configuration."""
        assert QuestaoAdmin.list_display == ('text', 'step')

    def test_questao_has_alternativa_inline(self):
        """Test Questao admin has AlternativaInline."""
        assert AlternativaInline in QuestaoAdmin.inlines

    def test_alternativa_inline_configuration(self):
        """Test AlternativaInline configuration."""
        assert AlternativaInline.model == Alternativa
        assert AlternativaInline.extra == 4


@pytest.mark.django_db
@pytest.mark.unit
class TestAlternativaAdmin:
    """Test AlternativaAdmin configuration."""

    def test_alternativa_list_display(self):
        """Test Alternativa admin list_display configuration."""
        assert AlternativaAdmin.list_display == ('text', 'question', 'is_correct')

    def test_alternativa_list_filter(self):
        """Test Alternativa admin list_filter configuration."""
        assert AlternativaAdmin.list_filter == ('question',)


@pytest.mark.django_db
@pytest.mark.unit
class TestAdminInlineRelationships:
    """Test admin inline relationships work correctly."""

    def test_area_displays_topics_inline(self):
        """Test Area admin can display Topics inline."""
        area = AreaFactory()
        topico1 = TopicoFactory(area=area)
        topico2 = TopicoFactory(area=area)

        # Verify the inline can access related topics
        assert area.topics.count() == 2
        assert set(area.topics.all()) == {topico1, topico2}

    def test_topico_displays_trilhas_inline(self):
        """Test Topico admin can display Trilhas inline."""
        topico = TopicoFactory()
        trilha1 = TrilhaFactory(topic=topico)
        trilha2 = TrilhaFactory(topic=topico)

        assert topico.tracks.count() == 2
        assert set(topico.tracks.all()) == {trilha1, trilha2}

    def test_trilha_displays_passos_inline(self):
        """Test Trilha admin can display Passos inline."""
        trilha = TrilhaFactory()
        passo1 = LessonFactory(track=trilha)
        passo2 = QuizFactory(track=trilha)

        assert trilha.steps.count() == 2
        assert set(trilha.steps.all()) == {passo1, passo2}

    def test_quiz_passo_displays_questoes_inline(self):
        """Test quiz Passo admin can display Questoes inline."""
        quiz = QuizFactory()
        questao1 = QuestaoFactory(step=quiz)
        questao2 = QuestaoFactory(step=quiz)

        assert quiz.questions.count() == 2
        assert set(quiz.questions.all()) == {questao1, questao2}

    def test_questao_displays_alternativas_inline(self):
        """Test Questao admin can display Alternativas inline."""
        questao = QuestaoFactory()
        alt1 = AlternativaFactory(question=questao)
        alt2 = AlternativaFactory(question=questao)
        alt3 = AlternativaFactory(question=questao)
        alt4 = AlternativaFactory(question=questao)

        assert questao.choices.count() == 4
        assert set(questao.choices.all()) == {alt1, alt2, alt3, alt4}


@pytest.mark.django_db
@pytest.mark.unit
class TestAdminFiltering:
    """Test admin filtering capabilities."""

    def test_filter_topicos_by_area(self):
        """Test filtering Topicos by Area in admin."""
        area1 = AreaFactory(title="Python")
        area2 = AreaFactory(title="JavaScript")
        topico1 = TopicoFactory(area=area1)
        topico2 = TopicoFactory(area=area2)
        topico3 = TopicoFactory(area=area1)

        # Filter by area1
        topicos_area1 = Topico.objects.filter(area=area1)
        assert topicos_area1.count() == 2
        assert set(topicos_area1) == {topico1, topico3}

    def test_filter_trilhas_by_topic(self):
        """Test filtering Trilhas by Topic in admin."""
        topico1 = TopicoFactory()
        topico2 = TopicoFactory()
        trilha1 = TrilhaFactory(topic=topico1)
        trilha2 = TrilhaFactory(topic=topico2)

        trilhas_topico1 = Trilha.objects.filter(topic=topico1)
        assert list(trilhas_topico1) == [trilha1]

    def test_filter_passos_by_content_type(self):
        """Test filtering Passos by content_type in admin."""
        trilha = TrilhaFactory()
        lesson1 = LessonFactory(track=trilha)
        lesson2 = LessonFactory(track=trilha)
        quiz1 = QuizFactory(track=trilha)

        lessons = Passo.objects.filter(content_type=Passo.LESSON)
        quizzes = Passo.objects.filter(content_type=Passo.QUIZ)

        assert lessons.count() == 2
        assert quizzes.count() == 1
        assert set(lessons) == {lesson1, lesson2}
        assert list(quizzes) == [quiz1]

    def test_filter_alternativas_by_question(self):
        """Test filtering Alternativas by Question in admin."""
        questao1 = QuestaoFactory()
        questao2 = QuestaoFactory()
        alt1 = AlternativaFactory(question=questao1)
        alt2 = AlternativaFactory(question=questao1)
        alt3 = AlternativaFactory(question=questao2)

        alts_q1 = Alternativa.objects.filter(question=questao1)
        alts_q2 = Alternativa.objects.filter(question=questao2)

        assert alts_q1.count() == 2
        assert alts_q2.count() == 1
        assert set(alts_q1) == {alt1, alt2}
        assert list(alts_q2) == [alt3]


@pytest.mark.django_db
@pytest.mark.unit
class TestAdminOrdering:
    """Test admin ordering of inlines."""

    def test_topico_inline_ordered_by_order(self):
        """Test TopicoInline displays topics in order."""
        area = AreaFactory()
        topico1 = TopicoFactory(area=area, order=3)
        topico2 = TopicoFactory(area=area, order=1)
        topico3 = TopicoFactory(area=area, order=2)

        # Inlines should respect ordering
        ordered_topics = area.topics.order_by('order')
        assert list(ordered_topics) == [topico2, topico3, topico1]

    def test_trilha_inline_ordered_by_order(self):
        """Test TrilhaInline displays trilhas in order."""
        topico = TopicoFactory()
        trilha1 = TrilhaFactory(topic=topico, order=3)
        trilha2 = TrilhaFactory(topic=topico, order=1)
        trilha3 = TrilhaFactory(topic=topico, order=2)

        ordered_trilhas = topico.tracks.order_by('order')
        assert list(ordered_trilhas) == [trilha2, trilha3, trilha1]

    def test_passo_inline_ordered_by_order(self):
        """Test PassoInline displays passos in order."""
        trilha = TrilhaFactory()
        passo1 = LessonFactory(track=trilha, order=3)
        passo2 = LessonFactory(track=trilha, order=1)
        passo3 = QuizFactory(track=trilha, order=2)

        ordered_passos = trilha.steps.order_by('order')
        assert list(ordered_passos) == [passo2, passo3, passo1]
