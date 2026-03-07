import json
from io import BytesIO

from openai import AsyncOpenAI

from interwiews.providers.base import AIProvider, QuestionAnalysis

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


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def transcribe(self, audio: bytes, filename: str = "audio.webm") -> str:
        response = await self._client.audio.transcriptions.create(
            model="whisper-1",
            file=(filename, BytesIO(audio)),
        )
        return response.text

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
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        return QuestionAnalysis(**data)

    async def generate_questions(self, job_description: str, count: int = 5) -> list[str]:
        prompt = _QUESTIONS_PROMPT.format(count=count, job_description=job_description)
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        return data["questions"]
