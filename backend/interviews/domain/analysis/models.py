from dataclasses import dataclass


@dataclass
class Analysis:
    id: int
    score: float
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    recommendation: str  # "hire" | "consider" | "reject"
    answer_id: int
