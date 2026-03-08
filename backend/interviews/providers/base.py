from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class QuestionAnalysis:
    score: int  # 0-10
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    recommendation: str  # "hire" | "consider" | "reject"


@dataclass
class GeneratedQuestions:
    questions: list[str]


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
    async def generate_questions(self, job_description: str, count: int = 5) -> list[str]:
        """Generate interview questions from a job description."""
        ...
