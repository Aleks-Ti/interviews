from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from interviews.domain.analysis.models import Analysis


class InterviewType(StrEnum):
    technical = "technical"
    behavioral = "behavioral"
    custom = "custom"


class InterviewStatus(StrEnum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


@dataclass
class Answer:
    id: int
    answer: str
    audio_path: str | None
    transcript: str | None
    question_id: int
    interview_id: int
    date_create: datetime
    date_update: datetime
    analysis: Analysis | None = field(default=None)


@dataclass
class Interview:
    id: int
    candidate_name: str
    type: str
    status: str
    plan_id: int
    conducted_by: UUID
    date_create: datetime
    date_update: datetime
    answers: list[Answer]
