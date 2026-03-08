import json

import anthropic

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


class AnthropicProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001") -> None:
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def transcribe(self, audio: bytes, filename: str = "audio.webm") -> str:
        raise NotImplementedError(
            "Anthropic does not support audio transcription. Set AI_PROVIDER=openai or add a dedicated transcription service."
        )

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
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        data = json.loads(response.content[0].text)
        return QuestionAnalysis(**data)

    async def generate_questions(self, job_description: str, count: int = 5) -> list[str]:
        prompt = _QUESTIONS_PROMPT.format(count=count, job_description=job_description)
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        data = json.loads(response.content[0].text)
        return data["questions"]
