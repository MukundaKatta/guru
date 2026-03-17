"""Curriculum models: standards, lesson plans, assignments, and built-in templates."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Core curriculum models
# ---------------------------------------------------------------------------

class BloomLevel(str, Enum):
    """Bloom's taxonomy levels."""

    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


class CourseStandard(BaseModel):
    """A curriculum standard that a lesson or assignment should address."""

    code: str = Field(description="Standard identifier, e.g. CCSS.MATH.8.EE.1")
    subject: str
    grade_level: int = Field(ge=1, le=16)
    description: str
    bloom_levels: list[BloomLevel] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


class LessonObjective(BaseModel):
    """A single measurable learning objective."""

    text: str
    bloom_level: BloomLevel = BloomLevel.UNDERSTAND
    assessment_method: str = ""


class LessonActivity(BaseModel):
    """A timed activity within a lesson plan."""

    title: str
    description: str
    duration_minutes: int = Field(ge=1)
    materials: list[str] = Field(default_factory=list)
    teacher_actions: list[str] = Field(default_factory=list)
    student_actions: list[str] = Field(default_factory=list)


class LessonPlan(BaseModel):
    """A complete lesson plan."""

    title: str
    subject: str
    grade_level: int = Field(ge=1, le=16)
    duration_minutes: int = Field(ge=1)
    standards: list[CourseStandard] = Field(default_factory=list)
    objectives: list[LessonObjective] = Field(default_factory=list)
    essential_question: str = ""
    materials: list[str] = Field(default_factory=list)
    warm_up: str = ""
    activities: list[LessonActivity] = Field(default_factory=list)
    closure: str = ""
    assessment: str = ""
    differentiation: str = ""
    homework: str = ""
    teacher_notes: str = ""

    @property
    def total_activity_minutes(self) -> int:
        return sum(a.duration_minutes for a in self.activities)


class AssignmentType(str, Enum):
    """Types of assignments."""

    ESSAY = "essay"
    PROBLEM_SET = "problem_set"
    LAB_REPORT = "lab_report"
    PROJECT = "project"
    PRESENTATION = "presentation"
    QUIZ = "quiz"
    DISCUSSION = "discussion"
    OTHER = "other"


class Assignment(BaseModel):
    """An assignment definition."""

    title: str
    subject: str
    grade_level: int = Field(ge=1, le=16)
    assignment_type: AssignmentType = AssignmentType.OTHER
    description: str = ""
    instructions: str = ""
    standards: list[CourseStandard] = Field(default_factory=list)
    due_date: str = ""
    max_score: float = Field(default=100.0, ge=0.0)
    rubric_criteria: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Built-in lesson plan templates
# ---------------------------------------------------------------------------

class LessonTemplate(BaseModel):
    """A reusable lesson plan template with placeholders."""

    name: str
    description: str
    pedagogy: str
    structure: list[dict[str, Any]]
    recommended_subjects: list[str] = Field(default_factory=list)
    recommended_grades: str = ""
    tips: list[str] = Field(default_factory=list)


LESSON_TEMPLATES: dict[str, LessonTemplate] = {
    "socratic_seminar": LessonTemplate(
        name="Socratic Seminar",
        description=(
            "A discussion-based lesson where students explore complex questions "
            "through dialogue, developing critical thinking and communication skills."
        ),
        pedagogy="inquiry-based learning",
        recommended_subjects=["English", "History", "Philosophy", "Science"],
        recommended_grades="6-16",
        structure=[
            {
                "phase": "Preparation",
                "duration_pct": 15,
                "details": (
                    "Distribute the anchor text or prompt. Students annotate and "
                    "prepare 2-3 open-ended questions."
                ),
            },
            {
                "phase": "Inner Circle Discussion",
                "duration_pct": 35,
                "details": (
                    "Half the class sits in the inner circle and discusses the "
                    "essential question. Participants must reference the text."
                ),
            },
            {
                "phase": "Outer Circle Observation",
                "duration_pct": 15,
                "details": (
                    "Outer circle students take notes on argumentation quality, "
                    "evidence use, and new insights."
                ),
            },
            {
                "phase": "Switch & Discuss",
                "duration_pct": 25,
                "details": "Circles swap roles and continue the discussion.",
            },
            {
                "phase": "Debrief & Reflect",
                "duration_pct": 10,
                "details": (
                    "Whole-class reflection: What changed your mind? What "
                    "question remains unanswered?"
                ),
            },
        ],
        tips=[
            "Establish norms: listen actively, build on others' ideas, cite evidence.",
            "Use sentence stems for reluctant speakers.",
            "Grade participation with a discussion tracker, not a hand-raise count.",
        ],
    ),
    "lab_investigation": LessonTemplate(
        name="Lab Investigation",
        description=(
            "A hands-on scientific inquiry lesson where students form hypotheses, "
            "design or follow procedures, collect data, and draw conclusions."
        ),
        pedagogy="inquiry-based / experiential learning",
        recommended_subjects=["Science", "Computer Science"],
        recommended_grades="5-16",
        structure=[
            {
                "phase": "Engage & Hypothesize",
                "duration_pct": 15,
                "details": (
                    "Present a driving phenomenon or demonstration. Students "
                    "generate initial hypotheses and predictions."
                ),
            },
            {
                "phase": "Procedure Review",
                "duration_pct": 10,
                "details": (
                    "Walk through safety protocols and step-by-step procedure. "
                    "Clarify data collection requirements."
                ),
            },
            {
                "phase": "Investigation",
                "duration_pct": 40,
                "details": (
                    "Students conduct the lab in groups, recording observations "
                    "and quantitative data in lab notebooks."
                ),
            },
            {
                "phase": "Data Analysis",
                "duration_pct": 20,
                "details": (
                    "Groups organize data into tables/graphs, identify patterns, "
                    "and compare results to hypotheses."
                ),
            },
            {
                "phase": "Conclusion & Share-Out",
                "duration_pct": 15,
                "details": (
                    "Each group presents findings. Class discusses sources of "
                    "error and real-world connections."
                ),
            },
        ],
        tips=[
            "Prepare materials stations in advance to maximize investigation time.",
            "Provide a structured lab report template for younger students.",
            "Include an extension question for groups that finish early.",
        ],
    ),
    "project_based_learning": LessonTemplate(
        name="Project-Based Learning (PBL)",
        description=(
            "An extended multi-day lesson framework where students tackle a "
            "real-world problem, producing a tangible product or presentation."
        ),
        pedagogy="constructivist / project-based learning",
        recommended_subjects=["All subjects"],
        recommended_grades="3-16",
        structure=[
            {
                "phase": "Entry Event & Driving Question",
                "duration_pct": 10,
                "details": (
                    "Launch with a compelling scenario (video, guest speaker, "
                    "news article). Reveal the driving question."
                ),
            },
            {
                "phase": "Need-to-Know List",
                "duration_pct": 10,
                "details": (
                    "Students brainstorm what they need to learn and what "
                    "resources they require. Teacher maps to standards."
                ),
            },
            {
                "phase": "Research & Skill-Building",
                "duration_pct": 25,
                "details": (
                    "Mini-lessons, readings, and skill workshops to fill "
                    "knowledge gaps. Checkpoints ensure progress."
                ),
            },
            {
                "phase": "Create & Iterate",
                "duration_pct": 35,
                "details": (
                    "Students build their product with structured feedback "
                    "loops (peer critique, teacher conferences)."
                ),
            },
            {
                "phase": "Present & Reflect",
                "duration_pct": 20,
                "details": (
                    "Public presentation to an authentic audience. Individual "
                    "reflection on learning and process."
                ),
            },
        ],
        tips=[
            "Define clear milestones with due dates to prevent last-minute rushes.",
            "Build in at least two rounds of structured peer feedback.",
            "Connect to a community partner or real audience for authenticity.",
        ],
    ),
    "flipped_classroom": LessonTemplate(
        name="Flipped Classroom",
        description=(
            "Students engage with instructional content before class (video, "
            "reading) so that class time is devoted to application, practice, "
            "and deeper exploration."
        ),
        pedagogy="blended learning / flipped instruction",
        recommended_subjects=["Math", "Science", "Foreign Language", "Computer Science"],
        recommended_grades="6-16",
        structure=[
            {
                "phase": "Pre-Class Content",
                "duration_pct": 0,
                "details": (
                    "Assign a short video or reading with guided notes and "
                    "2-3 comprehension check questions (completed before class)."
                ),
            },
            {
                "phase": "Warm-Up Review",
                "duration_pct": 10,
                "details": (
                    "Quick poll or quiz to surface misconceptions from the "
                    "pre-class material. Address common errors."
                ),
            },
            {
                "phase": "Guided Practice",
                "duration_pct": 30,
                "details": (
                    "Teacher models a complex example, then students work "
                    "through similar problems in pairs."
                ),
            },
            {
                "phase": "Independent / Group Application",
                "duration_pct": 45,
                "details": (
                    "Students apply concepts to challenging problems, case "
                    "studies, or creative tasks. Teacher circulates."
                ),
            },
            {
                "phase": "Exit Ticket & Preview",
                "duration_pct": 15,
                "details": (
                    "Students complete a brief formative assessment. Teacher "
                    "previews the next pre-class assignment."
                ),
            },
        ],
        tips=[
            "Keep pre-class videos under 10 minutes with embedded questions.",
            "Provide a paper alternative for students without reliable internet.",
            "Use class time data to form flexible small groups for re-teaching.",
        ],
    ),
    "differentiated_instruction": LessonTemplate(
        name="Differentiated Instruction",
        description=(
            "A lesson structure that provides multiple pathways to content, "
            "process, and product so every learner can access grade-level material."
        ),
        pedagogy="differentiated instruction / UDL",
        recommended_subjects=["All subjects"],
        recommended_grades="1-16",
        structure=[
            {
                "phase": "Whole-Group Mini-Lesson",
                "duration_pct": 15,
                "details": (
                    "Brief direct instruction on the core concept. Use visuals, "
                    "manipulatives, and verbal explanation (multi-modal)."
                ),
            },
            {
                "phase": "Tiered Activity Stations",
                "duration_pct": 45,
                "details": (
                    "Three stations at approaching / on-level / advanced tiers. "
                    "Each addresses the same standard at different complexity. "
                    "Students rotate or are assigned based on readiness."
                ),
            },
            {
                "phase": "Choice Board Work",
                "duration_pct": 25,
                "details": (
                    "Students select a product option (written, visual, oral, "
                    "digital) to demonstrate mastery of the objective."
                ),
            },
            {
                "phase": "Share & Synthesize",
                "duration_pct": 15,
                "details": (
                    "Gallery walk or lightning presentations. Class synthesizes "
                    "key takeaways collaboratively."
                ),
            },
        ],
        tips=[
            "Pre-assess to assign tiers -- never let students self-select into the easiest path.",
            "Ensure all tiers lead to the same essential understanding.",
            "Rotate groupings regularly so labels don't become fixed identities.",
        ],
    ),
    "collaborative_workshop": LessonTemplate(
        name="Collaborative Workshop",
        description=(
            "A group-based lesson where students build skills together through "
            "structured collaboration protocols."
        ),
        pedagogy="cooperative learning",
        recommended_subjects=["All subjects"],
        recommended_grades="3-16",
        structure=[
            {
                "phase": "Skill Introduction",
                "duration_pct": 15,
                "details": (
                    "Teacher models the target skill with a think-aloud. "
                    "Students take notes using a graphic organizer."
                ),
            },
            {
                "phase": "Structured Group Task",
                "duration_pct": 40,
                "details": (
                    "Groups of 3-4 work on a challenge problem. Each member "
                    "has an assigned role (facilitator, recorder, reporter, "
                    "timekeeper)."
                ),
            },
            {
                "phase": "Gallery Walk & Feedback",
                "duration_pct": 20,
                "details": (
                    "Groups post their work. Students circulate and leave "
                    "constructive feedback on sticky notes."
                ),
            },
            {
                "phase": "Revision & Reflection",
                "duration_pct": 15,
                "details": (
                    "Groups revise based on feedback. Individuals write a "
                    "brief reflection on what they learned from peers."
                ),
            },
            {
                "phase": "Closing Circle",
                "duration_pct": 10,
                "details": (
                    "Each group shares one insight. Teacher highlights "
                    "connections and previews next steps."
                ),
            },
        ],
        tips=[
            "Assign roles explicitly -- do not let groups self-organize every time.",
            "Use a visible timer to keep transitions crisp.",
            "Teach feedback norms (stars and wishes) before the gallery walk.",
        ],
    ),
}


def get_template(name: str) -> LessonTemplate:
    """Retrieve a lesson plan template by key name.

    Raises:
        KeyError: If the template name is not found.
    """
    key = name.lower().replace(" ", "_").replace("-", "_")
    if key not in LESSON_TEMPLATES:
        available = ", ".join(sorted(LESSON_TEMPLATES.keys()))
        raise KeyError(
            f"Unknown template '{name}'. Available templates: {available}"
        )
    return LESSON_TEMPLATES[key]


def list_templates() -> list[LessonTemplate]:
    """Return all built-in lesson plan templates."""
    return list(LESSON_TEMPLATES.values())
