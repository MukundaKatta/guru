"""FeedbackGenerator -- produce personalized student feedback using an LLM."""

from __future__ import annotations

import json
import os

import anthropic

from guru.models import FeedbackReport, PerformanceRecord, Student


_SYSTEM_PROMPT = """\
You are GURU, a compassionate and insightful teaching assistant generating
personalized student feedback.

Guidelines:
- Start with genuine, specific praise before addressing areas for growth.
- Be encouraging but honest -- students benefit from truthful feedback.
- Provide concrete, actionable next steps the student can take.
- Include a brief note for parents/guardians when appropriate.
- Tailor language to the student's grade level.
- Respond ONLY with valid JSON matching the requested schema.
"""


class FeedbackGenerator:
    """Generate personalized feedback reports for students."""

    def __init__(
        self,
        *,
        model: str = "claude-sonnet-4-20250514",
        api_key: str | None = None,
    ) -> None:
        self._model = model
        self._client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY", ""),
        )

    def generate(
        self,
        student: Student,
        records: list[PerformanceRecord],
        period: str = "",
        additional_observations: str = "",
    ) -> FeedbackReport:
        """Generate a personalized feedback report.

        Args:
            student: The student to write feedback for.
            records: Recent performance records / assessment scores.
            period: Reporting period label (e.g. "Q2 2026").
            additional_observations: Teacher notes or behavioral observations.

        Returns:
            A ``FeedbackReport`` with structured feedback.
        """
        user_prompt = self._build_prompt(
            student, records, period, additional_observations
        )

        message = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        return self._parse_response(message.content[0].text, student, period)

    def generate_from_scores(
        self,
        student_name: str,
        grade_level: int,
        scores: dict[str, float],
        period: str = "",
    ) -> FeedbackReport:
        """Convenience method to generate feedback from a simple scores dict.

        Args:
            student_name: Name of the student.
            grade_level: Grade level (1-16).
            scores: Mapping of assessment name to score (0-100).
            period: Reporting period label.

        Returns:
            A ``FeedbackReport``.
        """
        student = Student(name=student_name, grade_level=grade_level)
        records = [
            PerformanceRecord(student=student, assessment_name=name, score=score)
            for name, score in scores.items()
        ]
        return self.generate(student, records, period=period)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_prompt(
        student: Student,
        records: list[PerformanceRecord],
        period: str,
        observations: str,
    ) -> str:
        parts = [
            f"Student: {student.name} (Grade {student.grade_level})",
        ]
        if student.strengths:
            parts.append(f"Known strengths: {', '.join(student.strengths)}")
        if student.areas_for_growth:
            parts.append(f"Known growth areas: {', '.join(student.areas_for_growth)}")
        if student.accommodations:
            parts.append(f"Accommodations: {', '.join(student.accommodations)}")
        if period:
            parts.append(f"Reporting period: {period}")

        if records:
            parts.append("\nAssessment Scores:")
            for r in records:
                parts.append(f"  - {r.assessment_name}: {r.score}/{r.max_score} ({r.percentage}%)")

            avg = sum(r.percentage for r in records) / len(records)
            parts.append(f"  Average: {avg:.1f}%")

        if observations:
            parts.append(f"\nTeacher observations:\n{observations}")

        parts.append(
            "\nRespond with a JSON object containing: "
            "overall_summary, strengths_observed (list), "
            "growth_areas (list), action_items (list of specific steps), "
            "encouragement (a warm closing sentence), "
            "parent_note (brief note for parents/guardians)."
        )
        return "\n".join(parts)

    @staticmethod
    def _parse_response(
        raw: str, student: Student, period: str
    ) -> FeedbackReport:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()

        data = json.loads(text)

        return FeedbackReport(
            student=student,
            period=period,
            overall_summary=data.get("overall_summary", ""),
            strengths_observed=data.get("strengths_observed", []),
            growth_areas=data.get("growth_areas", []),
            action_items=data.get("action_items", []),
            encouragement=data.get("encouragement", ""),
            parent_note=data.get("parent_note", ""),
        )
