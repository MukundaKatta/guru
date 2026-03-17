# GURU - AI Teaching Assistant

An AI-powered teaching assistant that helps educators with lesson planning, assignment grading, student Q&A, and personalized feedback generation.

## Features

- **Lesson Planning** -- Generate standards-aligned lesson plans from curriculum standards
- **Assignment Grading** -- Grade assignments with detailed, constructive feedback using LLM
- **Q&A Engine** -- Answer student questions with context from course materials
- **Feedback Generation** -- Produce personalized student feedback based on performance data

## Installation

```bash
pip install -e .
```

## Configuration

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

## Usage

### CLI

```bash
# Generate a lesson plan
guru plan --subject "Biology" --topic "Photosynthesis" --grade 10

# Grade an assignment
guru grade --assignment path/to/assignment.txt --rubric path/to/rubric.txt

# Ask a question
guru ask "What is the difference between mitosis and meiosis?"

# Generate student feedback
guru feedback --student "Alex" --scores '{"quiz1": 85, "quiz2": 72, "midterm": 90}'
```

### Python API

```python
from guru.assistant.lesson_planner import LessonPlanner
from guru.curriculum import CourseStandard

standard = CourseStandard(
    code="NGSS-HS-LS1-5",
    subject="Biology",
    grade_level=10,
    description="Photosynthesis and cellular respiration",
)
planner = LessonPlanner()
plan = planner.generate(standard, duration_minutes=50)
```

## Built-in Lesson Plan Templates

GURU ships with templates for common subjects:

1. **Socratic Seminar** -- Discussion-based critical thinking
2. **Lab Investigation** -- Hands-on scientific inquiry
3. **Project-Based Learning** -- Extended real-world projects
4. **Flipped Classroom** -- Pre-class content, in-class application
5. **Differentiated Instruction** -- Multi-level scaffolded lessons
6. **Collaborative Workshop** -- Group-based skill building

## Author

Mukunda Katta
