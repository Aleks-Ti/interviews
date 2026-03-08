from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class QuestionType(StrEnum):
    technical = "technical"
    behavioral = "behavioral"
    custom = "custom"


@dataclass
class Question:
    id: int
    text: str
    type: str
    criteria: list[str]
    plan_id: int
    date_create: datetime
    date_update: datetime


@dataclass
class Plan:
    id: int
    name: str
    description: str
    created_by_user_id: UUID
    date_create: datetime
    date_update: datetime
    questions: list[Question]
