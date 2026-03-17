"""Rich-powered report rendering for GURU outputs."""

from __future__ import annotations

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from guru.curriculum import LessonPlan, LessonTemplate
from guru.models import FeedbackReport, GradingResult, QuestionAnswer


console = Console()


def render_lesson_plan(plan: LessonPlan) -> None:
    """Print a lesson plan to the terminal with rich formatting."""
    console.print()
    console.print(
        Panel(
            Text(plan.title, style="bold cyan", justify="center"),
            subtitle=f"{plan.subject} | Grade {plan.grade_level} | {plan.duration_minutes} min",
        )
    )

    if plan.essential_question:
        console.print(f"\n[bold]Essential Question:[/bold] {plan.essential_question}")

    if plan.objectives:
        console.print("\n[bold]Learning Objectives:[/bold]")
        for obj in plan.objectives:
            console.print(f"  - {obj.text} [dim]({obj.bloom_level.value})[/dim]")

    if plan.materials:
        console.print("\n[bold]Materials:[/bold]")
        for mat in plan.materials:
            console.print(f"  - {mat}")

    if plan.warm_up:
        console.print(f"\n[bold]Warm-Up:[/bold] {plan.warm_up}")

    if plan.activities:
        console.print("\n[bold]Activities:[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Activity", style="cyan")
        table.add_column("Duration", justify="right")
        table.add_column("Description")
        for act in plan.activities:
            table.add_row(act.title, f"{act.duration_minutes} min", act.description)
        console.print(table)

    if plan.closure:
        console.print(f"\n[bold]Closure:[/bold] {plan.closure}")

    if plan.assessment:
        console.print(f"\n[bold]Assessment:[/bold] {plan.assessment}")

    if plan.differentiation:
        console.print(f"\n[bold]Differentiation:[/bold] {plan.differentiation}")

    if plan.homework:
        console.print(f"\n[bold]Homework:[/bold] {plan.homework}")

    console.print()


def render_grading_result(result: GradingResult) -> None:
    """Print a grading result to the terminal."""
    console.print()
    grade_color = "green" if result.percentage >= 70 else "yellow" if result.percentage >= 50 else "red"
    console.print(
        Panel(
            Text(
                f"{result.assignment_title} -- {result.student_name}",
                style="bold",
                justify="center",
            ),
            subtitle=f"Score: [{grade_color}]{result.total_score}/{result.max_score} "
            f"({result.percentage}%) {result.letter_grade}[/{grade_color}]",
        )
    )

    if result.criterion_scores:
        table = Table(title="Criterion Scores", show_header=True, header_style="bold")
        table.add_column("Criterion")
        table.add_column("Score", justify="right")
        for criterion, score in result.criterion_scores.items():
            table.add_row(criterion, str(score))
        console.print(table)

    if result.strengths:
        console.print("\n[bold green]Strengths:[/bold green]")
        for s in result.strengths:
            console.print(f"  + {s}")

    if result.areas_for_improvement:
        console.print("\n[bold yellow]Areas for Improvement:[/bold yellow]")
        for a in result.areas_for_improvement:
            console.print(f"  - {a}")

    if result.detailed_feedback:
        console.print("\n[bold]Detailed Feedback:[/bold]")
        console.print(Markdown(result.detailed_feedback))

    if result.suggestions:
        console.print("\n[bold]Suggestions for Next Steps:[/bold]")
        for s in result.suggestions:
            console.print(f"  -> {s}")

    console.print()


def render_question_answer(qa: QuestionAnswer) -> None:
    """Print a Q&A response to the terminal."""
    console.print()
    console.print(Panel(f"[bold]Q:[/bold] {qa.question}", style="cyan"))
    console.print(Markdown(qa.answer))

    if qa.sources:
        console.print("\n[dim]Sources:[/dim]")
        for src in qa.sources:
            console.print(f"  - {src}")

    if qa.follow_up_questions:
        console.print("\n[bold]Follow-up questions you might explore:[/bold]")
        for fq in qa.follow_up_questions:
            console.print(f"  ? {fq}")

    console.print()


def render_feedback_report(report: FeedbackReport) -> None:
    """Print a personalized feedback report to the terminal."""
    console.print()
    console.print(
        Panel(
            Text(
                f"Feedback Report: {report.student.name}",
                style="bold cyan",
                justify="center",
            ),
            subtitle=report.period or "Current Period",
        )
    )

    if report.overall_summary:
        console.print(f"\n[bold]Summary:[/bold] {report.overall_summary}")

    if report.strengths_observed:
        console.print("\n[bold green]Strengths:[/bold green]")
        for s in report.strengths_observed:
            console.print(f"  + {s}")

    if report.growth_areas:
        console.print("\n[bold yellow]Areas for Growth:[/bold yellow]")
        for g in report.growth_areas:
            console.print(f"  - {g}")

    if report.action_items:
        console.print("\n[bold]Action Items:[/bold]")
        for i, item in enumerate(report.action_items, 1):
            console.print(f"  {i}. {item}")

    if report.encouragement:
        console.print(f"\n[italic]{report.encouragement}[/italic]")

    if report.parent_note:
        console.print(f"\n[bold]Note for Parents/Guardians:[/bold] {report.parent_note}")

    console.print()


def render_template_summary(template: LessonTemplate) -> None:
    """Print a concise summary of a lesson plan template."""
    console.print()
    console.print(Panel(f"[bold]{template.name}[/bold]\n{template.description}"))
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Phase")
    table.add_column("%", justify="right")
    table.add_column("Details")
    for phase in template.structure:
        table.add_row(
            phase["phase"],
            str(phase["duration_pct"]),
            phase["details"],
        )
    console.print(table)
    if template.tips:
        console.print("\n[bold]Tips:[/bold]")
        for tip in template.tips:
            console.print(f"  * {tip}")
    console.print()
