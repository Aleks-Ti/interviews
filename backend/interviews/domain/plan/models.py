from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class QuestionType(StrEnum):
    technical = "technical"
    behavioral = "behavioral"
    custom = "custom"


class PlanStatus(StrEnum):
    draft = "draft"
    published = "published"


@dataclass
class Question:
    id: int
    text: str
    type: str
    criteria: list[str]
    plan_id: int
    date_create: datetime
    date_update: datetime
    position: int = 0
    expected_answer: str | None = None


@dataclass
class Plan:
    id: int
    name: str
    description: str
    status: str
    created_by_user_id: UUID
    date_create: datetime
    date_update: datetime
    questions: list[Question]
