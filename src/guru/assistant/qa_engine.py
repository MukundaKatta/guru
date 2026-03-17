"""QAEngine -- answer student questions with context from course materials."""

from __future__ import annotations

import json
import os

import anthropic

from guru.models import QuestionAnswer


_SYSTEM_PROMPT = """\
You are GURU, a knowledgeable and patient teaching assistant.

Guidelines:
- Answer questions clearly and at the appropriate level for the student.
- When course materials are provided, ground your answer in those materials.
- If you are unsure, say so honestly rather than guessing.
- Suggest follow-up questions to deepen understanding.
- Use analogies and examples to make abstract concepts concrete.
- Respond ONLY with valid JSON matching the requested schema.
"""


class QAEngine:
    """Answer student questions, optionally grounded in course materials."""

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

    def ask(
        self,
        question: str,
        course_materials: list[str] | None = None,
        grade_level: int | None = None,
        subject: str = "",
    ) -> QuestionAnswer:
        """Answer a student question.

        Args:
            question: The student's question.
            course_materials: Optional list of text excerpts to use as context.
            grade_level: Student's grade level for appropriate language.
            subject: The subject area for context.

        Returns:
            A ``QuestionAnswer`` with the response and follow-ups.
        """
        user_prompt = self._build_prompt(
            question, course_materials, grade_level, subject
        )

        message = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        return self._parse_response(message.content[0].text, question)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_prompt(
        question: str,
        materials: list[str] | None,
        grade_level: int | None,
        subject: str,
    ) -> str:
        parts: list[str] = []

        if subject:
            parts.append(f"Subject: {subject}")
        if grade_level is not None:
            parts.append(f"Student grade level: {grade_level}")

        if materials:
            parts.append("\n--- Course Materials ---")
            for i, mat in enumerate(materials, 1):
                parts.append(f"[Source {i}]\n{mat}")
            parts.append("--- End Materials ---\n")

        parts.append(f"Student question: {question}")

        parts.append(
            "\nRespond with a JSON object containing: "
            "answer (markdown string), confidence (float 0-1), "
            "sources (list of source references used, if any), "
            "follow_up_questions (list of 2-3 questions the student could explore next)."
        )
        return "\n".join(parts)

    @staticmethod
    def _parse_response(raw: str, question: str) -> QuestionAnswer:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()

        data = json.loads(text)

        return QuestionAnswer(
            question=question,
            answer=data.get("answer", ""),
            confidence=data.get("confidence", 0.0),
            sources=data.get("sources", []),
            follow_up_questions=data.get("follow_up_questions", []),
        )
