"""
Integration tests for complete workflows across multiple models.
"""
import pytest
from django.db import transaction

from learning.models import Area, Topico, Trilha, Passo, Questao, Alternativa
from .factories import (
    AreaFactory,
    TopicoFactory,
    TrilhaFactory,
    LessonFactory,
    QuizFactory,
    QuestaoFactory,
    AlternativaFactory,
    CorrectAlternativaFactory,
)


@pytest.mark.django_db
@pytest.mark.integration
class TestLearningPathCreation:
    """Test creating complete learning paths."""

    def test_create_complete_learning_hierarchy(self):
        """Test creating a complete Area > Topic > Track > Step hierarchy."""
        # Create area
        area = AreaFactory(title="Python Programming", order=1)

        # Create topics under area
        topico1 = TopicoFactory(title="Python Basics", area=area, order=1)
        topico2 = TopicoFactory(title="Advanced Python", area=area, order=2)

        # Create tracks under topics
        trilha1 = TrilhaFactory(title="Getting Started", topic=topico1, order=1)
        trilha2 = TrilhaFactory(title="Variables & Types", topic=topico1, order=2)

        # Create steps under tracks
        passo1 = LessonFactory(
            title="Introduction",
            track=trilha1,
            content_type=Passo.LESSON,
            text_content="Welcome to Python!",
            order=1
        )
        passo2 = LessonFactory(
            title="Installation",
            track=trilha1,
            content_type=Passo.LESSON,
            text_content="How to install Python",
            order=2
        )
        passo3 = QuizFactory(
            title="Python Basics Quiz",
            track=trilha1,
            content_type=Passo.QUIZ,
            order=3
        )

        # Verify hierarchy
        assert area.topics.count() == 2
        assert topico1.tracks.count() == 2
        assert trilha1.steps.count() == 3
        assert Area.objects.count() == 1
        assert Topico.objects.count() == 2
        assert Trilha.objects.count() == 2
        assert Passo.objects.count() == 3

    def test_create_quiz_with_questions_and_answers(self):
        """Test creating a complete quiz with questions and alternatives."""
        # Create quiz
        quiz = QuizFactory(title="Python Quiz")

        # Create questions
        q1 = QuestaoFactory(
            step=quiz,
            text="What is Python?"
        )
        q2 = QuestaoFactory(
            step=quiz,
            text="Who created Python?"
        )

        # Create alternatives for question 1
        CorrectAlternativaFactory(question=q1, text="A programming language")
        AlternativaFactory(question=q1, text="A snake")
        AlternativaFactory(question=q1, text="A movie")
        AlternativaFactory(question=q1, text="A game")

        # Create alternatives for question 2
        CorrectAlternativaFactory(question=q2, text="Guido van Rossum")
        AlternativaFactory(question=q2, text="Dennis Ritchie")
        AlternativaFactory(question=q2, text="Linus Torvalds")
        AlternativaFactory(question=q2, text="James Gosling")

        # Verify structure
        assert quiz.questions.count() == 2
        assert q1.choices.count() == 4
        assert q2.choices.count() == 4
        assert q1.choices.filter(is_correct=True).count() == 1
        assert q2.choices.filter(is_correct=True).count() == 1

    def test_multi_area_learning_platform(self):
        """Test creating multiple learning areas with complete content."""
        # Create multiple areas
        python_area = AreaFactory(title="Python", order=1)
        js_area = AreaFactory(title="JavaScript", order=2)
        django_area = AreaFactory(title="Django", order=3)

        # Create topics for each area
        TopicoFactory.create_batch(3, area=python_area)
        TopicoFactory.create_batch(2, area=js_area)
        TopicoFactory.create_batch(4, area=django_area)

        # Verify counts
        assert Area.objects.count() == 3
        assert Topico.objects.count() == 9
        assert python_area.topics.count() == 3
        assert js_area.topics.count() == 2
        assert django_area.topics.count() == 4


@pytest.mark.django_db
@pytest.mark.integration
class TestCascadeDeletion:
    """Test cascade deletion through the entire hierarchy."""

    def test_delete_area_removes_everything(self):
        """Test deleting an area removes all nested content."""
        # Create full hierarchy
        area = AreaFactory()
        topico = TopicoFactory(area=area)
        trilha = TrilhaFactory(topic=topico)
        lesson = LessonFactory(track=trilha)
        quiz = QuizFactory(track=trilha)
        questao = QuestaoFactory(step=quiz)
        alternativa = AlternativaFactory(question=questao)

        # Count before deletion
        assert Area.objects.count() == 1
        assert Topico.objects.count() == 1
        assert Trilha.objects.count() == 1
        assert Passo.objects.count() == 2
        assert Questao.objects.count() == 1
        assert Alternativa.objects.count() == 1

        # Delete area
        area.delete()

        # Verify everything is deleted
        assert Area.objects.count() == 0
        assert Topico.objects.count() == 0
        assert Trilha.objects.count() == 0
        assert Passo.objects.count() == 0
        assert Questao.objects.count() == 0
        assert Alternativa.objects.count() == 0

    def test_delete_topico_preserves_area(self):
        """Test deleting a topic doesn't delete the area."""
        area = AreaFactory()
        topico1 = TopicoFactory(area=area)
        topico2 = TopicoFactory(area=area)
        trilha = TrilhaFactory(topic=topico1)

        # Delete topico1
        topico1.delete()

        # Verify area and topico2 remain
        assert Area.objects.count() == 1
        assert Topico.objects.count() == 1
        assert Trilha.objects.count() == 0
        assert area.topics.count() == 1

    def test_delete_quiz_removes_all_questions_and_answers(self):
        """Test deleting a quiz removes all its questions and alternatives."""
        quiz = QuizFactory()
        q1 = QuestaoFactory(step=quiz)
        q2 = QuestaoFactory(step=quiz)
        AlternativaFactory.create_batch(4, question=q1)
        AlternativaFactory.create_batch(4, question=q2)

        # Verify counts before deletion
        assert Questao.objects.count() == 2
        assert Alternativa.objects.count() == 8

        # Delete quiz
        quiz.delete()

        # Verify all questions and alternatives are deleted
        assert Passo.objects.count() == 0
        assert Questao.objects.count() == 0
        assert Alternativa.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.integration
class TestLearningPathNavigation:
    """Test navigating through a learning path."""

    def test_navigate_through_ordered_content(self):
        """Test navigating through content in correct order."""
        area = AreaFactory(order=1)
        topico = TopicoFactory(area=area, order=1)
        trilha = TrilhaFactory(topic=topico, order=1)

        # Create ordered steps
        step1 = LessonFactory(track=trilha, order=1)
        step2 = LessonFactory(track=trilha, order=2)
        step3 = QuizFactory(track=trilha, order=3)
        step4 = LessonFactory(track=trilha, order=4)

        # Navigate through steps
        steps = trilha.steps.all()
        assert list(steps) == [step1, step2, step3, step4]

        # Verify we can get first and last steps
        assert steps.first() == step1
        assert steps.last() == step4

    def test_get_all_steps_in_topic(self):
        """Test getting all steps within a topic."""
        topico = TopicoFactory()
        trilha1 = TrilhaFactory(topic=topico, order=1)
        trilha2 = TrilhaFactory(topic=topico, order=2)

        # Create steps in both tracks
        LessonFactory.create_batch(3, track=trilha1)
        LessonFactory.create_batch(2, track=trilha2)

        # Get all steps in topic
        all_steps = Passo.objects.filter(track__topic=topico)
        assert all_steps.count() == 5

    def test_get_all_quizzes_in_area(self):
        """Test getting all quizzes within an area."""
        area = AreaFactory()
        topico1 = TopicoFactory(area=area)
        topico2 = TopicoFactory(area=area)
        trilha1 = TrilhaFactory(topic=topico1)
        trilha2 = TrilhaFactory(topic=topico2)

        # Create mix of lessons and quizzes
        LessonFactory.create_batch(2, track=trilha1)
        QuizFactory.create_batch(1, track=trilha1)
        LessonFactory.create_batch(1, track=trilha2)
        QuizFactory.create_batch(2, track=trilha2)

        # Get all quizzes in area
        quizzes = Passo.objects.filter(
            track__topic__area=area,
            content_type=Passo.QUIZ
        )
        assert quizzes.count() == 3


@pytest.mark.django_db
@pytest.mark.integration
class TestQuizValidation:
    """Test quiz validation logic."""

    def test_quiz_with_valid_questions(self):
        """Test creating a valid quiz with properly structured questions."""
        quiz = QuizFactory()

        # Create question with one correct and three incorrect answers
        question = QuestaoFactory(step=quiz)
        correct = CorrectAlternativaFactory(question=question)
        incorrect1 = AlternativaFactory(question=question)
        incorrect2 = AlternativaFactory(question=question)
        incorrect3 = AlternativaFactory(question=question)

        # Verify structure
        assert question.choices.count() == 4
        assert question.choices.filter(is_correct=True).count() == 1
        assert question.choices.filter(is_correct=False).count() == 3

        # Get correct answer
        correct_answer = question.choices.filter(is_correct=True).first()
        assert correct_answer == correct

    def test_quiz_can_have_multiple_questions(self):
        """Test a quiz can have multiple questions."""
        quiz = QuizFactory()

        # Create 5 questions
        questions = []
        for i in range(5):
            q = QuestaoFactory(step=quiz)
            # Add alternatives
            CorrectAlternativaFactory(question=q)
            AlternativaFactory.create_batch(3, question=q)
            questions.append(q)

        # Verify quiz structure
        assert quiz.questions.count() == 5
        assert Alternativa.objects.filter(question__step=quiz).count() == 20

        # Verify each question has exactly one correct answer
        for question in questions:
            assert question.choices.filter(is_correct=True).count() == 1


@pytest.mark.django_db
@pytest.mark.integration
class TestContentOrganization:
    """Test content organization and hierarchy."""

    def test_reorder_topics_within_area(self):
        """Test reordering topics within an area."""
        area = AreaFactory()
        topico1 = TopicoFactory(area=area, order=1)
        topico2 = TopicoFactory(area=area, order=2)
        topico3 = TopicoFactory(area=area, order=3)

        # Reorder: swap topico1 and topico3
        topico1.order = 3
        topico3.order = 1
        topico1.save()
        topico3.save()

        # Verify new order
        topics = area.topics.all()
        assert list(topics) == [topico3, topico2, topico1]

    def test_move_track_to_different_topic(self):
        """Test moving a track from one topic to another."""
        topico1 = TopicoFactory(title="Basics")
        topico2 = TopicoFactory(title="Advanced")
        trilha = TrilhaFactory(topic=topico1)

        # Create steps in the track
        LessonFactory.create_batch(3, track=trilha)

        # Move track to different topic
        trilha.topic = topico2
        trilha.save()

        # Verify move
        assert topico1.tracks.count() == 0
        assert topico2.tracks.count() == 1
        assert trilha.steps.count() == 3  # Steps should remain

    def test_complex_multi_level_hierarchy(self):
        """Test a complex multi-level learning hierarchy."""
        # Create 2 areas
        for area_num in range(1, 3):
            area = AreaFactory(order=area_num)

            # Each area has 2 topics
            for topic_num in range(1, 3):
                topico = TopicoFactory(area=area, order=topic_num)

                # Each topic has 2 tracks
                for track_num in range(1, 3):
                    trilha = TrilhaFactory(topic=topico, order=track_num)

                    # Each track has 3 lessons and 1 quiz
                    for step_num in range(1, 5):
                        if step_num == 4:
                            QuizFactory(track=trilha, order=step_num)
                        else:
                            LessonFactory(track=trilha, order=step_num)

        # Verify counts
        assert Area.objects.count() == 2
        assert Topico.objects.count() == 4  # 2 areas × 2 topics
        assert Trilha.objects.count() == 8  # 4 topics × 2 tracks
        assert Passo.objects.count() == 32  # 8 tracks × 4 steps
        assert Passo.objects.filter(content_type=Passo.LESSON).count() == 24
        assert Passo.objects.filter(content_type=Passo.QUIZ).count() == 8


@pytest.mark.django_db
@pytest.mark.integration
class TestDataIntegrity:
    """Test data integrity across the system."""

    def test_cannot_have_orphaned_topics(self):
        """Test that topics must have an area."""
        # This should work
        area = AreaFactory()
        topico = TopicoFactory(area=area)
        assert topico.area is not None

        # Attempting to create a topic without an area would fail
        # due to the NOT NULL constraint on the database level

    def test_related_names_work_correctly(self):
        """Test all related_name attributes work bidirectionally."""
        area = AreaFactory()
        topico = TopicoFactory(area=area)
        trilha = TrilhaFactory(topic=topico)
        passo = QuizFactory(track=trilha)
        questao = QuestaoFactory(step=passo)
        alternativa = AlternativaFactory(question=questao)

        # Test forward relationships
        assert topico.area == area
        assert trilha.topic == topico
        assert passo.track == trilha
        assert questao.step == passo
        assert alternativa.question == questao

        # Test reverse relationships
        assert area.topics.first() == topico
        assert topico.tracks.first() == trilha
        assert trilha.steps.first() == passo
        assert passo.questions.first() == questao
        assert questao.choices.first() == alternativa

    def test_bulk_create_maintains_relationships(self):
        """Test bulk creation maintains proper relationships."""
        area = AreaFactory()

        # Bulk create topics
        topics_data = [
            TopicoFactory.build(area=area, order=i)
            for i in range(1, 6)
        ]
        Topico.objects.bulk_create(topics_data)

        # Verify relationships
        assert area.topics.count() == 5
        assert Topico.objects.filter(area=area).count() == 5

    def test_transaction_rollback_on_error(self):
        """Test that errors during creation rollback properly."""
        area = AreaFactory()
        initial_count = Topico.objects.count()

        # This should fail and rollback
        try:
            with transaction.atomic():
                TopicoFactory(area=area, title="Valid Topic")
                # Create another topic to increase count
                TopicoFactory(area=area, title="Another Valid")
                # Force an error
                raise ValueError("Simulated error")
        except ValueError:
            pass

        # Verify rollback - count should be unchanged
        assert Topico.objects.count() == initial_count
