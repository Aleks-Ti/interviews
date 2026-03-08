import json

import httpx

from interviews.providers.base import AIProvider, QuestionAnalysis

_ANALYZE_PROMPT = """
You are an experienced interviewer. Analyze the candidate's answer.

Question: {question}
Answer: {answer}
Evaluation criteria: {criteria}

Respond ONLY with valid JSON in this exact format:
{{
  "score": <integer 0-10>,
  "summary": "<one sentence summary>",
  "strengths": ["<strength>", ...],
  "weaknesses": ["<weakness>", ...],
  "recommendation": "<hire | consider | reject>"
}}
""".strip()

_QUESTIONS_PROMPT = """
You are an experienced technical recruiter. Generate {count} interview questions for the following job description.

Respond ONLY with valid JSON in this exact format:
{{"questions": ["<question>", ...]}}

Job description:
{job_description}
""".strip()


class OllamaProvider(AIProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3") -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def transcribe(self, audio: bytes, filename: str = "audio.webm") -> str:
        raise NotImplementedError(
            "Ollama does not support audio transcription natively. "
            "Run whisper.cpp with an HTTP server and handle transcription separately."
        )

    async def _chat(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self._base_url}/api/generate",
                json={"model": self._model, "prompt": prompt, "stream": False, "format": "json"},
            )
            response.raise_for_status()
            return response.json()["response"]

    async def analyze_answer(
        self,
        question: str,
        answer: str,
        criteria: list[str],
    ) -> QuestionAnalysis:
        prompt = _ANALYZE_PROMPT.format(
            question=question,
            answer=answer,
            criteria=", ".join(criteria),
        )
        data = json.loads(await self._chat(prompt))
        return QuestionAnalysis(**data)

    async def generate_questions(self, job_description: str, count: int = 5) -> list[str]:
        prompt = _QUESTIONS_PROMPT.format(count=count, job_description=job_description)
        data = json.loads(await self._chat(prompt))
        return data["questions"]
