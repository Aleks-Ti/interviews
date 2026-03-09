from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class QuestionAnalysis:
    score: int  # 0-10
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    recommendation: str  # "hire" | "consider" | "reject"


@dataclass
class GeneratedQuestion:
    text: str
    type: str           # "technical" | "behavioral" | "custom"
    criteria: list[str]


@dataclass
class GeneratedPlan:
    name: str
    description: str
    questions: list[GeneratedQuestion]


class AIProvider(ABC):
    """Abstract AI provider. Implement this to plug in any AI backend."""

    @abstractmethod
    async def transcribe(self, audio: bytes, filename: str = "audio.webm") -> str:
        """Convert audio recording to text."""
        ...

    @abstractmethod
    async def analyze_answer(
        self,
        question: str,
        answer: str,
        criteria: list[str],
    ) -> QuestionAnalysis:
        """Analyze a candidate's answer against the given criteria."""
        ...

    @abstractmethod
    async def suggest_question(self, context: str, question_type: str = "technical") -> GeneratedQuestion:
        """Generate a single well-crafted interview question for the given context."""
        ...

    @abstractmethod
    async def get_expected_answer(self, question: str, criteria: list[str], context: str) -> str:
        """Generate an expected answer to help interviewers evaluate responses."""
        ...

    @abstractmethod
    async def generate_plan(self, prompt: str, question_count: int = 10) -> GeneratedPlan:
        """Generate a complete interview plan with questions from a free-text prompt."""
        ...
