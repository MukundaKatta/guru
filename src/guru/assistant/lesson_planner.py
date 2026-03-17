"""LessonPlanner -- generate lesson plans from curriculum standards using an LLM."""

from __future__ import annotations

import json
import os

import anthropic

from guru.curriculum import (
    CourseStandard,
    LessonActivity,
    LessonObjective,
    LessonPlan,
    LessonTemplate,
    BloomLevel,
    get_template,
)


_SYSTEM_PROMPT = """\
You are GURU, an expert instructional designer and curriculum specialist.
Your job is to produce detailed, standards-aligned lesson plans that any
teacher can pick up and teach effectively.

Guidelines:
- Every activity must have clear teacher actions AND student actions.
- Include differentiation strategies for diverse learners.
- Ensure the plan addresses the stated curriculum standard(s).
- Be specific: avoid vague instructions like "discuss the topic".
- Respond ONLY with valid JSON matching the requested schema.
"""


class LessonPlanner:
    """Generate lesson plans from curriculum standards, optionally using a template."""

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
        standard: CourseStandard,
        duration_minutes: int = 50,
        template_name: str | None = None,
        additional_context: str = "",
    ) -> LessonPlan:
        """Generate a complete lesson plan for the given standard.

        Args:
            standard: The curriculum standard to address.
            duration_minutes: Total class time in minutes.
            template_name: Optional template key (e.g. "socratic_seminar").
            additional_context: Extra instructions or context for the LLM.

        Returns:
            A fully populated ``LessonPlan``.
        """
        template_section = ""
        if template_name:
            tpl = get_template(template_name)
            template_section = self._format_template(tpl, duration_minutes)

        user_prompt = self._build_prompt(
            standard, duration_minutes, template_section, additional_context
        )

        message = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        return self._parse_response(message.content[0].text, standard, duration_minutes)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_template(tpl: LessonTemplate, duration: int) -> str:
        lines = [
            f"Use the '{tpl.name}' lesson structure ({tpl.pedagogy}).",
            "Phases:",
        ]
        for phase in tpl.structure:
            mins = round(phase["duration_pct"] / 100 * duration)
            lines.append(f"  - {phase['phase']} (~{mins} min): {phase['details']}")
        if tpl.tips:
            lines.append("Tips:")
            for tip in tpl.tips:
                lines.append(f"  - {tip}")
        return "\n".join(lines)

    @staticmethod
    def _build_prompt(
        standard: CourseStandard,
        duration: int,
        template_section: str,
        extra: str,
    ) -> str:
        parts = [
            "Create a detailed lesson plan with the following parameters:",
            f"Subject: {standard.subject}",
            f"Grade level: {standard.grade_level}",
            f"Standard: {standard.code} -- {standard.description}",
            f"Duration: {duration} minutes",
        ]
        if standard.bloom_levels:
            parts.append(
                "Bloom's levels to target: "
                + ", ".join(b.value for b in standard.bloom_levels)
            )
        if template_section:
            parts.append(f"\nTemplate:\n{template_section}")
        if extra:
            parts.append(f"\nAdditional context:\n{extra}")

        parts.append(
            "\nRespond with a JSON object containing these keys: "
            "title, essential_question, materials (list of strings), "
            "warm_up, objectives (list of {text, bloom_level, assessment_method}), "
            "activities (list of {title, description, duration_minutes, materials, "
            "teacher_actions, student_actions}), closure, assessment, "
            "differentiation, homework, teacher_notes."
        )
        return "\n".join(parts)

    @staticmethod
    def _parse_response(
        raw: str, standard: CourseStandard, duration: int
    ) -> LessonPlan:
        """Parse LLM JSON response into a LessonPlan model."""
        # Strip markdown fences if present
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()

        data = json.loads(text)

        objectives = [
            LessonObjective(
                text=o.get("text", ""),
                bloom_level=BloomLevel(o.get("bloom_level", "understand")),
                assessment_method=o.get("assessment_method", ""),
            )
            for o in data.get("objectives", [])
        ]

        activities = [
            LessonActivity(
                title=a.get("title", ""),
                description=a.get("description", ""),
                duration_minutes=a.get("duration_minutes", 10),
                materials=a.get("materials", []),
                teacher_actions=a.get("teacher_actions", []),
                student_actions=a.get("student_actions", []),
            )
            for a in data.get("activities", [])
        ]

        return LessonPlan(
            title=data.get("title", f"{standard.subject} Lesson"),
            subject=standard.subject,
            grade_level=standard.grade_level,
            duration_minutes=duration,
            standards=[standard],
            objectives=objectives,
            essential_question=data.get("essential_question", ""),
            materials=data.get("materials", []),
            warm_up=data.get("warm_up", ""),
            activities=activities,
            closure=data.get("closure", ""),
            assessment=data.get("assessment", ""),
            differentiation=data.get("differentiation", ""),
            homework=data.get("homework", ""),
            teacher_notes=data.get("teacher_notes", ""),
        )
