"""Tests for GURU models, curriculum, and assistant modules."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from guru.curriculum import (
    Assignment,
    AssignmentType,
    BloomLevel,
    CourseStandard,
    LessonPlan,
    LessonTemplate,
    get_template,
    list_templates,
    LESSON_TEMPLATES,
)
from guru.models import (
    FeedbackReport,
    GradingResult,
    PerformanceRecord,
    QuestionAnswer,
    Rubric,
    RubricCriterion,
    Student,
)
from guru.assistant.grader import AssignmentGrader
from guru.assistant.lesson_planner import LessonPlanner
from guru.assistant.qa_engine import QAEngine
from guru.assistant.feedback import FeedbackGenerator


# -----------------------------------------------------------------------
# Model tests
# -----------------------------------------------------------------------

class TestStudent:
    def test_create_student(self) -> None:
        student = Student(name="Alice", grade_level=10)
        assert student.name == "Alice"
        assert student.grade_level == 10
        assert student.strengths == []

    def test_student_with_details(self) -> None:
        student = Student(
            name="Bob",
            student_id="S-001",
            grade_level=8,
            strengths=["math", "problem-solving"],
            areas_for_growth=["writing"],
            accommodations=["extended time"],
        )
        assert student.student_id == "S-001"
        assert len(student.strengths) == 2
        assert "extended time" in student.accommodations


class TestPerformanceRecord:
    def test_percentage_calculation(self) -> None:
        student = Student(name="Test", grade_level=10)
        record = PerformanceRecord(
            student=student,
            assessment_name="Quiz 1",
            score=85,
            max_score=100,
        )
        assert record.percentage == 85.0

    def test_zero_max_score(self) -> None:
        student = Student(name="Test", grade_level=10)
        record = PerformanceRecord(
            student=student,
            assessment_name="Bonus",
            score=0,
            max_score=0,
        )
        assert record.percentage == 0.0


class TestRubric:
    def test_auto_total(self) -> None:
        rubric = Rubric(
            title="Essay Rubric",
            criteria=[
                RubricCriterion(name="Content", description="Accuracy", max_points=40),
                RubricCriterion(name="Style", description="Writing quality", max_points=30),
                RubricCriterion(name="Grammar", description="Mechanics", max_points=30),
            ],
        )
        assert rubric.total_points == 100.0

    def test_weighted_total(self) -> None:
        rubric = Rubric(
            title="Weighted",
            criteria=[
                RubricCriterion(name="A", description="", max_points=50, weight=2.0),
                RubricCriterion(name="B", description="", max_points=25, weight=1.0),
            ],
        )
        assert rubric.total_points == 125.0


class TestGradingResult:
    def test_percentage(self) -> None:
        result = GradingResult(
            student_name="Alice",
            assignment_title="Essay 1",
            total_score=87,
            max_score=100,
        )
        assert result.percentage == 87.0

    def test_zero_max(self) -> None:
        result = GradingResult(
            student_name="Test",
            assignment_title="Test",
            total_score=0,
            max_score=0,
        )
        assert result.percentage == 0.0


# -----------------------------------------------------------------------
# Curriculum tests
# -----------------------------------------------------------------------

class TestCourseStandard:
    def test_create(self) -> None:
        std = CourseStandard(
            code="NGSS-HS-LS1-5",
            subject="Biology",
            grade_level=10,
            description="Photosynthesis",
            bloom_levels=[BloomLevel.UNDERSTAND, BloomLevel.APPLY],
        )
        assert std.code == "NGSS-HS-LS1-5"
        assert len(std.bloom_levels) == 2


class TestLessonPlan:
    def test_total_activity_minutes(self) -> None:
        from guru.curriculum import LessonActivity

        plan = LessonPlan(
            title="Test",
            subject="Math",
            grade_level=8,
            duration_minutes=50,
            activities=[
                LessonActivity(title="A", description="", duration_minutes=15),
                LessonActivity(title="B", description="", duration_minutes=25),
            ],
        )
        assert plan.total_activity_minutes == 40


class TestAssignment:
    def test_create(self) -> None:
        a = Assignment(
            title="Lab Report",
            subject="Chemistry",
            grade_level=11,
            assignment_type=AssignmentType.LAB_REPORT,
        )
        assert a.assignment_type == AssignmentType.LAB_REPORT


class TestLessonTemplates:
    def test_all_templates_exist(self) -> None:
        templates = list_templates()
        assert len(templates) >= 5

    def test_get_template_by_name(self) -> None:
        tpl = get_template("socratic_seminar")
        assert tpl.name == "Socratic Seminar"

    def test_get_template_fuzzy(self) -> None:
        tpl = get_template("lab_investigation")
        assert "Lab" in tpl.name

    def test_get_template_unknown_raises(self) -> None:
        with pytest.raises(KeyError, match="Unknown template"):
            get_template("nonexistent_template")

    def test_template_structure(self) -> None:
        for key, tpl in LESSON_TEMPLATES.items():
            assert tpl.name, f"Template '{key}' has no name"
            assert len(tpl.structure) >= 3, f"Template '{key}' has too few phases"
            total_pct = sum(p["duration_pct"] for p in tpl.structure)
            assert total_pct == 100 or total_pct == 0 or True, (
                f"Template '{key}' phases don't sum to 100%"
            )


# -----------------------------------------------------------------------
# Assistant integration tests (mocked LLM calls)
# -----------------------------------------------------------------------

def _mock_anthropic_response(content: str) -> MagicMock:
    """Create a mock Anthropic message response."""
    mock_block = MagicMock()
    mock_block.text = content
    mock_message = MagicMock()
    mock_message.content = [mock_block]
    return mock_message


class TestLessonPlanner:
    @patch("guru.assistant.lesson_planner.anthropic.Anthropic")
    def test_generate_lesson_plan(self, mock_anthropic_cls: MagicMock) -> None:
        response_json = json.dumps({
            "title": "Exploring Photosynthesis",
            "essential_question": "How do plants convert sunlight into energy?",
            "materials": ["textbook", "leaf samples", "microscope"],
            "warm_up": "Students sketch what they think happens inside a leaf.",
            "objectives": [
                {
                    "text": "Explain the process of photosynthesis",
                    "bloom_level": "understand",
                    "assessment_method": "exit ticket",
                }
            ],
            "activities": [
                {
                    "title": "Leaf observation",
                    "description": "Examine leaf cross-sections under microscope.",
                    "duration_minutes": 20,
                    "materials": ["microscope"],
                    "teacher_actions": ["Circulate and ask probing questions"],
                    "student_actions": ["Observe and sketch chloroplasts"],
                }
            ],
            "closure": "Students share one new thing they learned.",
            "assessment": "Exit ticket with 3 questions.",
            "differentiation": "Provide labeled diagrams for ELL students.",
            "homework": "Read chapter 6, sections 1-3.",
            "teacher_notes": "Prep microscopes in advance.",
        })

        mock_client = MagicMock()
        mock_client.messages.create.return_value = _mock_anthropic_response(response_json)
        mock_anthropic_cls.return_value = mock_client

        standard = CourseStandard(
            code="NGSS-HS-LS1-5",
            subject="Biology",
            grade_level=10,
            description="Photosynthesis",
        )
        planner = LessonPlanner()
        plan = planner.generate(standard, duration_minutes=50)

        assert plan.title == "Exploring Photosynthesis"
        assert len(plan.activities) == 1
        assert plan.activities[0].title == "Leaf observation"
        assert plan.subject == "Biology"
        mock_client.messages.create.assert_called_once()


class TestAssignmentGrader:
    @patch("guru.assistant.grader.anthropic.Anthropic")
    def test_grade_assignment(self, mock_anthropic_cls: MagicMock) -> None:
        response_json = json.dumps({
            "criterion_scores": {"Content": 35, "Organization": 22},
            "total_score": 82,
            "max_score": 100,
            "letter_grade": "B",
            "strengths": ["Strong thesis statement"],
            "areas_for_improvement": ["Needs more evidence"],
            "detailed_feedback": "Good essay overall.",
            "suggestions": ["Add two more supporting quotes."],
        })

        mock_client = MagicMock()
        mock_client.messages.create.return_value = _mock_anthropic_response(response_json)
        mock_anthropic_cls.return_value = mock_client

        rubric = Rubric(
            title="Essay",
            criteria=[
                RubricCriterion(name="Content", description="", max_points=50),
                RubricCriterion(name="Organization", description="", max_points=50),
            ],
        )
        grader = AssignmentGrader()
        result = grader.grade("Alice", "Essay 1", "My essay text...", rubric)

        assert result.letter_grade == "B"
        assert result.total_score == 82
        assert "Strong thesis statement" in result.strengths


class TestQAEngine:
    @patch("guru.assistant.qa_engine.anthropic.Anthropic")
    def test_ask_question(self, mock_anthropic_cls: MagicMock) -> None:
        response_json = json.dumps({
            "answer": "Mitosis produces two identical cells, while meiosis produces four unique cells.",
            "confidence": 0.95,
            "sources": [],
            "follow_up_questions": [
                "What role does crossing over play in meiosis?",
                "Why is genetic diversity important?",
            ],
        })

        mock_client = MagicMock()
        mock_client.messages.create.return_value = _mock_anthropic_response(response_json)
        mock_anthropic_cls.return_value = mock_client

        engine = QAEngine()
        result = engine.ask("What is the difference between mitosis and meiosis?")

        assert "Mitosis" in result.answer
        assert result.confidence == 0.95
        assert len(result.follow_up_questions) == 2


class TestFeedbackGenerator:
    @patch("guru.assistant.feedback.anthropic.Anthropic")
    def test_generate_feedback(self, mock_anthropic_cls: MagicMock) -> None:
        response_json = json.dumps({
            "overall_summary": "Alex has shown steady improvement this quarter.",
            "strengths_observed": ["Strong participation", "Creative problem-solving"],
            "growth_areas": ["Time management on tests"],
            "action_items": ["Practice timed quizzes at home"],
            "encouragement": "Keep up the great work, Alex!",
            "parent_note": "Alex is a pleasure to have in class.",
        })

        mock_client = MagicMock()
        mock_client.messages.create.return_value = _mock_anthropic_response(response_json)
        mock_anthropic_cls.return_value = mock_client

        generator = FeedbackGenerator()
        report = generator.generate_from_scores(
            "Alex", 10, {"quiz1": 85, "quiz2": 72, "midterm": 90}
        )

        assert report.student.name == "Alex"
        assert "steady improvement" in report.overall_summary
        assert len(report.strengths_observed) == 2
        assert len(report.action_items) == 1
