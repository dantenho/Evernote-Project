"""
Specialized AI agents for educational content generation.

Uses multi-agent approach for high-quality quiz and lesson generation.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ContentAnalysis:
    """Analysis result from content analyzer agent."""
    topic: str
    difficulty_level: str
    key_concepts: List[str]
    learning_objectives: List[str]
    prerequisite_knowledge: List[str]
    estimated_time_minutes: int
    recommended_question_count: int


@dataclass
class GeneratedQuestion:
    """Single generated question."""
    question_type: str  # multiple_choice, fill_blank, etc.
    text: str
    correct_answer: str
    choices: Optional[List[Dict[str, Any]]] = None
    explanation: str = ""
    hint: str = ""
    points: int = 10
    difficulty: str = "medium"


@dataclass
class QuizGeneration:
    """Complete quiz generation result."""
    title: str
    description: str
    questions: List[GeneratedQuestion]
    total_points: int
    estimated_time_minutes: int
    difficulty_distribution: Dict[str, int]
    quality_score: float


class ContentAnalyzerAgent:
    """
    Analyzes educational content to extract key information.

    First step in multi-agent pipeline.
    """

    def __init__(self, ai_service):
        """
        Initialize content analyzer.

        Args:
            ai_service: AI service instance (Claude, GPT-4, etc.)
        """
        self.ai_service = ai_service

    def analyze(self, content: str, topic: str = None) -> ContentAnalysis:
        """
        Analyze educational content.

        Args:
            content: Raw educational content (text, code, etc.)
            topic: Optional topic hint

        Returns:
            ContentAnalysis: Structured analysis
        """
        system_prompt = """You are an expert educational content analyzer.

Analyze the provided content and extract:
1. Main topic and subtopics
2. Difficulty level (beginner/intermediate/advanced)
3. Key concepts that should be tested
4. Learning objectives
5. Required prerequisite knowledge
6. Estimated study time
7. Recommended number of questions

Output as JSON with this structure:
{
    "topic": "string",
    "difficulty_level": "beginner|intermediate|advanced",
    "key_concepts": ["concept1", "concept2"],
    "learning_objectives": ["objective1", "objective2"],
    "prerequisite_knowledge": ["prereq1", "prereq2"],
    "estimated_time_minutes": 30,
    "recommended_question_count": 10
}"""

        user_prompt = f"""Analyze this educational content:

{f"Topic hint: {topic}" if topic else ""}

Content:
{content[:3000]}  # Limit to 3000 chars

Provide detailed analysis as JSON."""

        try:
            result = self.ai_service.generate(system_prompt, user_prompt)
            data = json.loads(result['text'])

            return ContentAnalysis(
                topic=data['topic'],
                difficulty_level=data['difficulty_level'],
                key_concepts=data['key_concepts'],
                learning_objectives=data['learning_objectives'],
                prerequisite_knowledge=data['prerequisite_knowledge'],
                estimated_time_minutes=data['estimated_time_minutes'],
                recommended_question_count=data['recommended_question_count']
            )

        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            # Return default analysis
            return ContentAnalysis(
                topic=topic or "Unknown",
                difficulty_level="intermediate",
                key_concepts=[],
                learning_objectives=[],
                prerequisite_knowledge=[],
                estimated_time_minutes=30,
                recommended_question_count=10
            )


class QuestionGeneratorAgent:
    """
    Generates high-quality educational questions.

    Second step in multi-agent pipeline.
    """

    def __init__(self, ai_service):
        self.ai_service = ai_service

    def generate_questions(
        self,
        analysis: ContentAnalysis,
        content: str,
        count: int = 10,
        question_types: List[str] = None
    ) -> List[GeneratedQuestion]:
        """
        Generate questions based on content analysis.

        Args:
            analysis: ContentAnalysis from analyzer agent
            content: Original educational content
            count: Number of questions to generate
            question_types: List of question types to include

        Returns:
            List[GeneratedQuestion]: Generated questions
        """
        if question_types is None:
            question_types = ['multiple_choice', 'fill_blank', 'short_answer']

        system_prompt = f"""You are an expert question writer for educational assessments.

Create {count} high-quality questions based on the provided content and analysis.

Guidelines:
1. Use diverse question types: {', '.join(question_types)}
2. Cover all key concepts from analysis
3. Match difficulty level: {analysis.difficulty_level}
4. Include clear explanations
5. Provide helpful hints
6. Assign appropriate point values (5-20 points)

For multiple choice:
- 4 options minimum
- Only one correct answer
- Plausible distractors
- No "all of the above" or "none of the above"

For fill-in-blank:
- Clear sentence structure
- One blank per question
- Unambiguous answer

For short answer:
- Open-ended but specific
- Clear grading criteria

Output as JSON array:
[{{
    "question_type": "multiple_choice|fill_blank|short_answer",
    "text": "Question text here",
    "correct_answer": "Answer",
    "choices": [{{"text": "Option", "is_correct": false}}],  // for multiple_choice
    "explanation": "Why this is the answer",
    "hint": "Helpful hint",
    "points": 10,
    "difficulty": "easy|medium|hard"
}}]"""

        user_prompt = f"""Topic: {analysis.topic}
Difficulty: {analysis.difficulty_level}

Key Concepts to Cover:
{chr(10).join(f'- {c}' for c in analysis.key_concepts)}

Learning Objectives:
{chr(10).join(f'- {o}' for o in analysis.learning_objectives)}

Content:
{content[:2000]}

Generate {count} questions as JSON array."""

        try:
            result = self.ai_service.generate(system_prompt, user_prompt)

            # Extract JSON from response
            text = result['text']
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]

            data = json.loads(text.strip())

            questions = []
            for q in data:
                questions.append(GeneratedQuestion(
                    question_type=q['question_type'],
                    text=q['text'],
                    correct_answer=q['correct_answer'],
                    choices=q.get('choices'),
                    explanation=q.get('explanation', ''),
                    hint=q.get('hint', ''),
                    points=q.get('points', 10),
                    difficulty=q.get('difficulty', 'medium')
                ))

            return questions

        except Exception as e:
            logger.error(f"Question generation failed: {str(e)}")
            return []


class QualityReviewAgent:
    """
    Reviews generated questions for quality and accuracy.

    Third step in multi-agent pipeline.
    """

    def __init__(self, ai_service):
        self.ai_service = ai_service

    def review_questions(
        self,
        questions: List[GeneratedQuestion],
        content: str
    ) -> Dict[str, Any]:
        """
        Review questions for quality.

        Args:
            questions: Generated questions to review
            content: Original content for fact-checking

        Returns:
            dict: Review results with scores and suggestions
        """
        system_prompt = """You are an expert educational content reviewer.

Review the provided questions for:
1. Accuracy (factually correct based on content)
2. Clarity (unambiguous wording)
3. Difficulty balance (good mix of easy/medium/hard)
4. Coverage (tests all important concepts)
5. Quality of explanations and hints

Provide:
- Overall quality score (0-100)
- Issues found (if any)
- Suggestions for improvement
- Flag any incorrect or ambiguous questions

Output as JSON:
{
    "overall_score": 85,
    "issues": [
        {"question_index": 0, "issue": "description", "severity": "high|medium|low"}
    ],
    "suggestions": ["suggestion1", "suggestion2"],
    "difficulty_distribution": {"easy": 3, "medium": 5, "hard": 2},
    "coverage_gaps": ["concept not covered"],
    "flagged_questions": [0, 3]  // indices of problematic questions
}"""

        questions_json = [
            {
                'index': i,
                'type': q.question_type,
                'text': q.text,
                'answer': q.correct_answer,
                'difficulty': q.difficulty
            }
            for i, q in enumerate(questions)
        ]

        user_prompt = f"""Review these {len(questions)} questions:

{json.dumps(questions_json, indent=2)}

Original Content:
{content[:1500]}

Provide detailed review as JSON."""

        try:
            result = self.ai_service.generate(system_prompt, user_prompt)

            # Extract JSON
            text = result['text']
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]

            return json.loads(text.strip())

        except Exception as e:
            logger.error(f"Quality review failed: {str(e)}")
            return {
                'overall_score': 70,
                'issues': [],
                'suggestions': [],
                'difficulty_distribution': {'easy': 0, 'medium': len(questions), 'hard': 0},
                'coverage_gaps': [],
                'flagged_questions': []
            }


class DifficultyBalancerAgent:
    """
    Balances question difficulty distribution.

    Fourth step in multi-agent pipeline.
    """

    def __init__(self, ai_service):
        self.ai_service = ai_service

    def balance_difficulty(
        self,
        questions: List[GeneratedQuestion],
        target_distribution: Dict[str, int] = None
    ) -> List[GeneratedQuestion]:
        """
        Adjust questions to match target difficulty distribution.

        Args:
            questions: Questions to balance
            target_distribution: Desired distribution (e.g., {'easy': 3, 'medium': 5, 'hard': 2})

        Returns:
            List[GeneratedQuestion]: Balanced questions
        """
        if target_distribution is None:
            # Default: 30% easy, 50% medium, 20% hard
            total = len(questions)
            target_distribution = {
                'easy': int(total * 0.3),
                'medium': int(total * 0.5),
                'hard': int(total * 0.2)
            }

        # Count current distribution
        current = {'easy': 0, 'medium': 0, 'hard': 0}
        for q in questions:
            current[q.difficulty] = current.get(q.difficulty, 0) + 1

        logger.info(f"Current difficulty distribution: {current}")
        logger.info(f"Target difficulty distribution: {target_distribution}")

        # Simple balancing: adjust difficulty labels
        # In production, you might regenerate questions
        balanced = questions.copy()

        # Sort by difficulty
        easy_questions = [q for q in balanced if q.difficulty == 'easy']
        medium_questions = [q for q in balanced if q.difficulty == 'medium']
        hard_questions = [q for q in balanced if q.difficulty == 'hard']

        # Adjust if needed
        needed_easy = target_distribution['easy'] - len(easy_questions)
        needed_hard = target_distribution['hard'] - len(hard_questions)

        # Promote medium to hard if needed
        if needed_hard > 0 and len(medium_questions) > needed_hard:
            for i in range(needed_hard):
                medium_questions[i].difficulty = 'hard'
                medium_questions[i].points += 5

        # Demote medium to easy if needed
        if needed_easy > 0 and len(medium_questions) > needed_easy:
            for i in range(needed_easy):
                medium_questions[-(i+1)].difficulty = 'easy'
                medium_questions[-(i+1)].points = max(5, medium_questions[-(i+1)].points - 5)

        return balanced


class QuizOrchestrator:
    """
    Orchestrates the multi-agent quiz generation pipeline.

    Main interface for generating high-quality quizzes.
    """

    def __init__(self, ai_service):
        """
        Initialize quiz orchestrator with all agents.

        Args:
            ai_service: AI service instance
        """
        self.analyzer = ContentAnalyzerAgent(ai_service)
        self.generator = QuestionGeneratorAgent(ai_service)
        self.reviewer = QualityReviewAgent(ai_service)
        self.balancer = DifficultyBalancerAgent(ai_service)

    def generate_quiz(
        self,
        content: str,
        topic: str = None,
        question_count: int = 10,
        difficulty_distribution: Dict[str, int] = None,
        min_quality_score: float = 70.0
    ) -> QuizGeneration:
        """
        Generate complete quiz using multi-agent pipeline.

        Pipeline:
        1. Analyzer: Understand content
        2. Generator: Create questions
        3. Reviewer: Check quality
        4. Balancer: Adjust difficulty

        Args:
            content: Educational content to create quiz from
            topic: Optional topic hint
            question_count: Number of questions
            difficulty_distribution: Target difficulty mix
            min_quality_score: Minimum acceptable quality (0-100)

        Returns:
            QuizGeneration: Complete quiz with metadata
        """
        logger.info(f"Starting quiz generation: {question_count} questions on '{topic}'")

        # Step 1: Analyze content
        logger.info("Step 1: Analyzing content...")
        analysis = self.analyzer.analyze(content, topic)
        logger.info(f"Analysis complete: {analysis.topic} ({analysis.difficulty_level})")

        # Step 2: Generate questions
        logger.info("Step 2: Generating questions...")
        questions = self.generator.generate_questions(
            analysis,
            content,
            count=question_count
        )
        logger.info(f"Generated {len(questions)} questions")

        if not questions:
            raise ValueError("Failed to generate any questions")

        # Step 3: Review quality
        logger.info("Step 3: Reviewing quality...")
        review = self.reviewer.review_questions(questions, content)
        quality_score = review['overall_score']
        logger.info(f"Quality score: {quality_score}/100")

        # Check if quality meets threshold
        if quality_score < min_quality_score:
            logger.warning(f"Quality score {quality_score} below threshold {min_quality_score}")
            # In production, might retry generation here

        # Remove flagged questions
        if review.get('flagged_questions'):
            logger.warning(f"Removing {len(review['flagged_questions'])} flagged questions")
            questions = [
                q for i, q in enumerate(questions)
                if i not in review['flagged_questions']
            ]

        # Step 4: Balance difficulty
        logger.info("Step 4: Balancing difficulty...")
        questions = self.balancer.balance_difficulty(questions, difficulty_distribution)

        # Calculate total points
        total_points = sum(q.points for q in questions)

        # Build final quiz
        quiz = QuizGeneration(
            title=f"{analysis.topic} - Assessment",
            description=f"Test your knowledge of {analysis.topic}",
            questions=questions,
            total_points=total_points,
            estimated_time_minutes=analysis.estimated_time_minutes,
            difficulty_distribution=review['difficulty_distribution'],
            quality_score=quality_score
        )

        logger.info(f"Quiz generation complete: {len(questions)} questions, {total_points} points")

        return quiz


# Convenience function
def generate_quiz_from_content(
    content: str,
    ai_service,
    topic: str = None,
    question_count: int = 10
) -> QuizGeneration:
    """
    Quick quiz generation from content.

    Args:
        content: Educational content
        ai_service: AI service instance
        topic: Optional topic
        question_count: Number of questions

    Returns:
        QuizGeneration: Complete quiz
    """
    orchestrator = QuizOrchestrator(ai_service)
    return orchestrator.generate_quiz(content, topic, question_count)
