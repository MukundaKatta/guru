"""Core domain models for the GURU teaching assistant."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class GradeLevel(str, Enum):
    """Supported grade level bands."""

    ELEMENTARY = "elementary"  # K-5
    MIDDLE = "middle"  # 6-8
    HIGH = "high"  # 9-12
    COLLEGE = "college"


class Subject(str, Enum):
    """Common academic subjects."""

    MATH = "math"
    SCIENCE = "science"
    ENGLISH = "english"
    HISTORY = "history"
    COMPUTER_SCIENCE = "computer_science"
    ART = "art"
    MUSIC = "music"
    FOREIGN_LANGUAGE = "foreign_language"
    OTHER = "other"


class Student(BaseModel):
    """Represents a student."""

    name: str
    student_id: str = ""
    grade_level: int = Field(ge=1, le=16)
    strengths: list[str] = Field(default_factory=list)
    areas_for_growth: list[str] = Field(default_factory=list)
    accommodations: list[str] = Field(default_factory=list)


class PerformanceRecord(BaseModel):
    """A single assessment score for a student."""

    student: Student
    assessment_name: str
    score: float = Field(ge=0.0, le=100.0)
    max_score: float = Field(default=100.0, ge=0.0)
    date: datetime = Field(default_factory=datetime.now)
    notes: str = ""

    @property
    def percentage(self) -> float:
        if self.max_score == 0:
            return 0.0
        return round((self.score / self.max_score) * 100, 2)


class RubricCriterion(BaseModel):
    """A single criterion within a grading rubric."""

    name: str
    description: str
    max_points: float = Field(ge=0.0)
    weight: float = Field(default=1.0, ge=0.0)


class Rubric(BaseModel):
    """A grading rubric composed of multiple criteria."""

    title: str
    criteria: list[RubricCriterion] = Field(min_length=1)
    total_points: float = Field(default=0.0)

    def model_post_init(self, __context: Any) -> None:
        if self.total_points == 0.0:
            self.total_points = sum(c.max_points * c.weight for c in self.criteria)


class GradingResult(BaseModel):
    """Result of grading an assignment."""

    student_name: str
    assignment_title: str
    criterion_scores: dict[str, float] = Field(default_factory=dict)
    total_score: float = Field(ge=0.0)
    max_score: float = Field(ge=0.0)
    letter_grade: str = ""
    strengths: list[str] = Field(default_factory=list)
    areas_for_improvement: list[str] = Field(default_factory=list)
    detailed_feedback: str = ""
    suggestions: list[str] = Field(default_factory=list)

    @property
    def percentage(self) -> float:
        if self.max_score == 0:
            return 0.0
        return round((self.total_score / self.max_score) * 100, 2)


class QuestionAnswer(BaseModel):
    """A question-answer pair from the Q&A engine."""

    question: str
    answer: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    sources: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)


class FeedbackReport(BaseModel):
    """Personalized feedback report for a student."""

    student: Student
    period: str = ""
    overall_summary: str = ""
    strengths_observed: list[str] = Field(default_factory=list)
    growth_areas: list[str] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)
    encouragement: str = ""
    parent_note: str = ""
    generated_at: datetime = Field(default_factory=datetime.now)
