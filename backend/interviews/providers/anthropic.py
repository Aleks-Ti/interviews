import json

import anthropic

from interviews.providers.base import AIProvider, GeneratedPlan, GeneratedQuestion, QuestionAnalysis

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

_SUGGEST_QUESTION_PROMPT = """
You are an expert interviewer. Generate a single well-crafted interview question.

Context: {context}
Question type: {question_type}

Respond ONLY with valid JSON:
{{"text": "<question>", "type": "<technical|behavioral|custom>", "criteria": ["<evaluation criterion>", ...]}}
""".strip()

_EXPECTED_ANSWER_PROMPT = """
You are an expert in the following domain: {context}

Write an ideal expected answer to the interview question below.
This will help an interviewer (who may not know the topic) evaluate the candidate's response.

Question: {question}
Evaluation criteria: {criteria}

Respond ONLY with valid JSON:
{{"answer": "<expected answer covering all key points a strong candidate should mention>"}}
""".strip()

_GENERATE_PLAN_PROMPT = """
You are an expert recruiter. Create a complete structured interview plan.

Requirements: {prompt}
Number of questions: {question_count}

Respond ONLY with valid JSON:
{{
  "name": "<concise plan name>",
  "description": "<brief description of the plan>",
  "questions": [
    {{"text": "<question>", "type": "<technical|behavioral|custom>", "criteria": ["<evaluation criterion>", ...]}},
    ...
  ]
}}
""".strip()


class AnthropicProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001") -> None:
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def _complete(self, prompt: str, max_tokens: int = 1024) -> str:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    async def transcribe(self, audio: bytes, filename: str = "audio.webm") -> str:
        raise NotImplementedError(
            "Anthropic does not support audio transcription. "
            "Set AI_PROVIDER=openai or add a dedicated transcription service."
        )

    async def analyze_answer(self, question: str, answer: str, criteria: list[str]) -> QuestionAnalysis:
        prompt = _ANALYZE_PROMPT.format(question=question, answer=answer, criteria=", ".join(criteria))
        data = json.loads(await self._complete(prompt))
        return QuestionAnalysis(**data)

    async def suggest_question(self, context: str, question_type: str = "technical") -> GeneratedQuestion:
        prompt = _SUGGEST_QUESTION_PROMPT.format(context=context, question_type=question_type)
        data = json.loads(await self._complete(prompt))
        return GeneratedQuestion(**data)

    async def get_expected_answer(self, question: str, criteria: list[str], context: str) -> str:
        prompt = _EXPECTED_ANSWER_PROMPT.format(
            context=context, question=question, criteria=", ".join(criteria)
        )
        data = json.loads(await self._complete(prompt, max_tokens=2048))
        return data["answer"]

    async def generate_plan(self, prompt: str, question_count: int = 10) -> GeneratedPlan:
        full_prompt = _GENERATE_PLAN_PROMPT.format(prompt=prompt, question_count=question_count)
        data = json.loads(await self._complete(full_prompt, max_tokens=4096))
        return GeneratedPlan(
            name=data["name"],
            description=data["description"],
            questions=[GeneratedQuestion(**q) for q in data["questions"]],
        )
