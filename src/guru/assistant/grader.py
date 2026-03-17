"""AssignmentGrader -- grade assignments with constructive feedback using an LLM."""

from __future__ import annotations

import json
import os

import anthropic

from guru.models import GradingResult, Rubric


_SYSTEM_PROMPT = """\
You are GURU, an experienced and fair assignment grader.

Guidelines:
- Evaluate student work against the provided rubric criteria.
- Be constructive: highlight what the student did well before noting weaknesses.
- Give specific, actionable suggestions for improvement.
- Assign a numeric score for each rubric criterion.
- Determine an overall letter grade (A, A-, B+, B, B-, C+, C, C-, D, F).
- Respond ONLY with valid JSON matching the requested schema.
"""


class AssignmentGrader:
    """Grade student assignments using an LLM with rubric-based evaluation."""

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

    def grade(
        self,
        student_name: str,
        assignment_title: str,
        submission_text: str,
        rubric: Rubric,
        additional_instructions: str = "",
    ) -> GradingResult:
        """Grade a student submission against a rubric.

        Args:
            student_name: Name of the student.
            assignment_title: Title of the assignment.
            submission_text: The student's submitted work.
            rubric: The grading rubric to apply.
            additional_instructions: Extra grading guidance.

        Returns:
            A ``GradingResult`` with scores and feedback.
        """
        user_prompt = self._build_prompt(
            student_name,
            assignment_title,
            submission_text,
            rubric,
            additional_instructions,
        )

        message = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        return self._parse_response(
            message.content[0].text, student_name, assignment_title, rubric
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_prompt(
        student_name: str,
        assignment_title: str,
        submission: str,
        rubric: Rubric,
        extra: str,
    ) -> str:
        rubric_lines = [f"Rubric: {rubric.title} (Total: {rubric.total_points} pts)"]
        for c in rubric.criteria:
            rubric_lines.append(
                f"  - {c.name} ({c.max_points} pts, weight {c.weight}): {c.description}"
            )

        parts = [
            f"Student: {student_name}",
            f"Assignment: {assignment_title}",
            "\n".join(rubric_lines),
            f"\n--- Student Submission ---\n{submission}\n--- End Submission ---",
        ]
        if extra:
            parts.append(f"\nAdditional grading instructions:\n{extra}")

        parts.append(
            "\nRespond with a JSON object containing: "
            "criterion_scores (dict of criterion name -> score), "
            "total_score, max_score, letter_grade, "
            "strengths (list), areas_for_improvement (list), "
            "detailed_feedback (markdown string), suggestions (list)."
        )
        return "\n".join(parts)

    @staticmethod
    def _parse_response(
        raw: str,
        student_name: str,
        assignment_title: str,
        rubric: Rubric,
    ) -> GradingResult:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()

        data = json.loads(text)

        return GradingResult(
            student_name=student_name,
            assignment_title=assignment_title,
            criterion_scores=data.get("criterion_scores", {}),
            total_score=data.get("total_score", 0),
            max_score=data.get("max_score", rubric.total_points),
            letter_grade=data.get("letter_grade", ""),
            strengths=data.get("strengths", []),
            areas_for_improvement=data.get("areas_for_improvement", []),
            detailed_feedback=data.get("detailed_feedback", ""),
            suggestions=data.get("suggestions", []),
        )
