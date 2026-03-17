#!/usr/bin/env python3
"""Example usage of the GURU AI Teaching Assistant.

This script demonstrates how to use GURU's Python API for:
1. Listing built-in lesson plan templates
2. Generating a lesson plan
3. Grading an assignment
4. Answering a student question
5. Generating personalized feedback

Set the ANTHROPIC_API_KEY environment variable before running examples
that call the LLM (2-5).
"""

from __future__ import annotations

import os
import sys

from rich.console import Console

# Ensure the src directory is importable when running the example directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from guru.curriculum import CourseStandard, BloomLevel, get_template, list_templates
from guru.models import Rubric, RubricCriterion, Student, PerformanceRecord
from guru.report import render_lesson_plan, render_grading_result, render_question_answer, render_feedback_report, render_template_summary

console = Console()


def demo_templates() -> None:
    """List all built-in lesson plan templates."""
    console.rule("[bold cyan]Built-in Lesson Plan Templates[/bold cyan]")
    for tpl in list_templates():
        render_template_summary(tpl)


def demo_lesson_plan() -> None:
    """Generate a lesson plan using the LLM."""
    from guru.assistant.lesson_planner import LessonPlanner

    console.rule("[bold cyan]Lesson Plan Generation[/bold cyan]")

    standard = CourseStandard(
        code="NGSS-HS-LS1-5",
        subject="Biology",
        grade_level=10,
        description="Use a model to illustrate how photosynthesis transforms light energy into stored chemical energy.",
        bloom_levels=[BloomLevel.UNDERSTAND, BloomLevel.APPLY, BloomLevel.ANALYZE],
        keywords=["photosynthesis", "chloroplast", "ATP", "glucose"],
    )

    planner = LessonPlanner()
    plan = planner.generate(
        standard,
        duration_minutes=50,
        template_name="lab_investigation",
        additional_context="Students have already learned about cell organelles.",
    )
    render_lesson_plan(plan)


def demo_grading() -> None:
    """Grade a sample essay submission."""
    from guru.assistant.grader import AssignmentGrader

    console.rule("[bold cyan]Assignment Grading[/bold cyan]")

    rubric = Rubric(
        title="Persuasive Essay Rubric",
        criteria=[
            RubricCriterion(
                name="Thesis & Argument",
                description="Clear thesis with well-developed arguments supported by evidence.",
                max_points=30,
            ),
            RubricCriterion(
                name="Evidence & Analysis",
                description="Uses relevant evidence and provides insightful analysis.",
                max_points=30,
            ),
            RubricCriterion(
                name="Organization",
                description="Logical structure with smooth transitions.",
                max_points=20,
            ),
            RubricCriterion(
                name="Language & Mechanics",
                description="Proper grammar, spelling, and academic tone.",
                max_points=20,
            ),
        ],
    )

    sample_essay = """\
    Social media has transformed how we communicate, but not all changes are positive.
    While platforms like Instagram and TikTok connect people across the globe, they also
    contribute to rising anxiety among teenagers. According to a 2023 study by the American
    Psychological Association, teens who spend more than three hours daily on social media
    are twice as likely to report symptoms of depression.

    However, social media is not inherently harmful. It provides a voice to marginalized
    communities and enables rapid information sharing during crises. The key is teaching
    digital literacy so young people can navigate these platforms responsibly.

    In conclusion, rather than banning social media, schools should integrate media literacy
    into their curriculum to help students develop critical thinking about online content.
    """

    grader = AssignmentGrader()
    result = grader.grade(
        student_name="Jordan",
        assignment_title="Persuasive Essay: Social Media in Schools",
        submission_text=sample_essay,
        rubric=rubric,
    )
    render_grading_result(result)


def demo_qa() -> None:
    """Answer a student question."""
    from guru.assistant.qa_engine import QAEngine

    console.rule("[bold cyan]Q&A Engine[/bold cyan]")

    engine = QAEngine()
    result = engine.ask(
        question="Why does the moon appear to change shape throughout the month?",
        grade_level=6,
        subject="Earth Science",
        course_materials=[
            "The Moon orbits Earth approximately once every 27.3 days. As it orbits, "
            "different portions of the Moon's surface are illuminated by the Sun. "
            "These changing illumination patterns are called lunar phases. The eight "
            "primary phases are: new moon, waxing crescent, first quarter, waxing "
            "gibbous, full moon, waning gibbous, third quarter, and waning crescent.",
        ],
    )
    render_question_answer(result)


def demo_feedback() -> None:
    """Generate personalized student feedback."""
    from guru.assistant.feedback import FeedbackGenerator

    console.rule("[bold cyan]Personalized Feedback[/bold cyan]")

    student = Student(
        name="Priya Sharma",
        student_id="S-2024-047",
        grade_level=9,
        strengths=["analytical thinking", "class participation"],
        areas_for_growth=["written expression", "time management"],
    )

    records = [
        PerformanceRecord(student=student, assessment_name="Unit 1 Test", score=88, max_score=100),
        PerformanceRecord(student=student, assessment_name="Lab Report 1", score=72, max_score=100),
        PerformanceRecord(student=student, assessment_name="Homework Average", score=95, max_score=100),
        PerformanceRecord(student=student, assessment_name="Midterm Exam", score=81, max_score=100),
    ]

    generator = FeedbackGenerator()
    report = generator.generate(
        student=student,
        records=records,
        period="Q1 2026",
        additional_observations="Priya asks thoughtful questions during class discussions.",
    )
    render_feedback_report(report)


if __name__ == "__main__":
    # Template listing works without an API key.
    demo_templates()

    # The following require ANTHROPIC_API_KEY to be set.
    if os.environ.get("ANTHROPIC_API_KEY"):
        demo_lesson_plan()
        demo_grading()
        demo_qa()
        demo_feedback()
    else:
        console.print(
            "\n[yellow]Set ANTHROPIC_API_KEY to run LLM-powered demos "
            "(lesson plan, grading, Q&A, feedback).[/yellow]\n"
        )
