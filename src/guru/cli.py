"""GURU command-line interface powered by Click and Rich."""

from __future__ import annotations

import json
import sys

import click
from rich.console import Console

from guru.assistant.feedback import FeedbackGenerator
from guru.assistant.grader import AssignmentGrader
from guru.assistant.lesson_planner import LessonPlanner
from guru.assistant.qa_engine import QAEngine
from guru.curriculum import CourseStandard, BloomLevel, list_templates
from guru.models import Rubric, RubricCriterion, Student
from guru.report import (
    render_feedback_report,
    render_grading_result,
    render_lesson_plan,
    render_question_answer,
    render_template_summary,
)

console = Console()


@click.group()
@click.version_option(package_name="guru")
def cli() -> None:
    """GURU -- AI Teaching Assistant.

    Generate lesson plans, grade assignments, answer student questions,
    and produce personalized feedback reports.
    """


# -----------------------------------------------------------------------
# guru plan
# -----------------------------------------------------------------------

@cli.command()
@click.option("--subject", required=True, help="Subject area (e.g. Biology).")
@click.option("--topic", required=True, help="Topic or standard description.")
@click.option("--grade", required=True, type=int, help="Grade level (1-16).")
@click.option("--duration", default=50, type=int, help="Class duration in minutes.")
@click.option("--standard-code", default="", help="Curriculum standard code.")
@click.option("--template", default=None, help="Lesson template name.")
@click.option("--context", default="", help="Additional context for the planner.")
def plan(
    subject: str,
    topic: str,
    grade: int,
    duration: int,
    standard_code: str,
    template: str | None,
    context: str,
) -> None:
    """Generate a lesson plan from a curriculum standard."""
    standard = CourseStandard(
        code=standard_code or f"{subject.upper()}-{grade}",
        subject=subject,
        grade_level=grade,
        description=topic,
    )

    console.print("[dim]Generating lesson plan...[/dim]")
    planner = LessonPlanner()
    lesson = planner.generate(
        standard,
        duration_minutes=duration,
        template_name=template,
        additional_context=context,
    )
    render_lesson_plan(lesson)


# -----------------------------------------------------------------------
# guru grade
# -----------------------------------------------------------------------

@cli.command()
@click.option("--assignment", required=True, type=click.Path(exists=True), help="Path to student submission.")
@click.option("--rubric", default=None, type=click.Path(exists=True), help="Path to rubric JSON file.")
@click.option("--student", default="Student", help="Student name.")
@click.option("--title", default="Assignment", help="Assignment title.")
@click.option("--instructions", default="", help="Additional grading instructions.")
def grade(
    assignment: str,
    rubric: str | None,
    student: str,
    title: str,
    instructions: str,
) -> None:
    """Grade an assignment with rubric-based feedback."""
    with open(assignment, "r") as f:
        submission_text = f.read()

    if rubric:
        with open(rubric, "r") as f:
            rubric_data = json.load(f)
        grading_rubric = Rubric(
            title=rubric_data.get("title", "Rubric"),
            criteria=[
                RubricCriterion(**c) for c in rubric_data.get("criteria", [])
            ],
        )
    else:
        grading_rubric = Rubric(
            title="General Assessment",
            criteria=[
                RubricCriterion(name="Content", description="Accuracy and depth of content", max_points=40),
                RubricCriterion(name="Organization", description="Structure and flow", max_points=25),
                RubricCriterion(name="Analysis", description="Critical thinking and analysis", max_points=25),
                RubricCriterion(name="Mechanics", description="Grammar, spelling, and formatting", max_points=10),
            ],
        )

    console.print("[dim]Grading assignment...[/dim]")
    grader = AssignmentGrader()
    result = grader.grade(student, title, submission_text, grading_rubric, instructions)
    render_grading_result(result)


# -----------------------------------------------------------------------
# guru ask
# -----------------------------------------------------------------------

@cli.command()
@click.argument("question")
@click.option("--subject", default="", help="Subject area for context.")
@click.option("--grade", default=None, type=int, help="Student grade level.")
@click.option("--materials", default=None, type=click.Path(exists=True), help="Path to course materials file.")
def ask(
    question: str,
    subject: str,
    grade: int | None,
    materials: str | None,
) -> None:
    """Ask a question and get an AI-powered answer."""
    course_materials = None
    if materials:
        with open(materials, "r") as f:
            course_materials = [f.read()]

    console.print("[dim]Thinking...[/dim]")
    engine = QAEngine()
    result = engine.ask(
        question,
        course_materials=course_materials,
        grade_level=grade,
        subject=subject,
    )
    render_question_answer(result)


# -----------------------------------------------------------------------
# guru feedback
# -----------------------------------------------------------------------

@cli.command()
@click.option("--student", required=True, help="Student name.")
@click.option("--scores", required=True, help='JSON dict of assessment scores, e.g. \'{"quiz1": 85}\'.')
@click.option("--grade", default=10, type=int, help="Student grade level.")
@click.option("--period", default="", help="Reporting period label.")
@click.option("--observations", default="", help="Additional teacher observations.")
def feedback(
    student: str,
    scores: str,
    grade: int,
    period: str,
    observations: str,
) -> None:
    """Generate a personalized student feedback report."""
    try:
        scores_dict = json.loads(scores)
    except json.JSONDecodeError:
        console.print("[red]Error: --scores must be valid JSON.[/red]")
        sys.exit(1)

    console.print("[dim]Generating feedback...[/dim]")
    generator = FeedbackGenerator()
    report = generator.generate_from_scores(student, grade, scores_dict, period=period)
    render_feedback_report(report)


# -----------------------------------------------------------------------
# guru templates
# -----------------------------------------------------------------------

@cli.command()
@click.argument("name", required=False, default=None)
def templates(name: str | None) -> None:
    """List available lesson plan templates, or show details for one."""
    if name:
        from guru.curriculum import get_template

        try:
            tpl = get_template(name)
        except KeyError as exc:
            console.print(f"[red]{exc}[/red]")
            sys.exit(1)
        render_template_summary(tpl)
    else:
        all_templates = list_templates()
        console.print(f"\n[bold]Available Lesson Plan Templates ({len(all_templates)}):[/bold]\n")
        for tpl in all_templates:
            console.print(f"  [cyan]{tpl.name}[/cyan] -- {tpl.description[:80]}...")
        console.print("\n[dim]Use 'guru templates <name>' for details.[/dim]\n")


if __name__ == "__main__":
    cli()
