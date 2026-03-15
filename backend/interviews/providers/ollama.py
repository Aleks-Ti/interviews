import json

import httpx

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
You are an interview assistant. Be concise.

Context: {context}
Question: {question}
Criteria: {criteria}

- Technical question → give the correct answer directly, key points only (3-5 bullets max).
- Behavioral/abstract question → list 3-5 short bullet points of what the candidate should mention.

No preamble. No "the candidate should". Just the substance. Max 80 words.

Respond ONLY with valid JSON:
{{"answer": "<answer>"}}
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


class OllamaProvider(AIProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3") -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def _chat(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self._base_url}/api/generate",
                json={"model": self._model, "prompt": prompt, "stream": False, "format": "json"},
            )
            response.raise_for_status()
            return response.json()["response"]

    async def analyze_answer(self, question: str, answer: str, criteria: list[str]) -> QuestionAnalysis:
        prompt = _ANALYZE_PROMPT.format(question=question, answer=answer, criteria=", ".join(criteria))
        data = json.loads(await self._chat(prompt))
        return QuestionAnalysis(**data)

    async def suggest_question(self, context: str, question_type: str = "technical") -> GeneratedQuestion:
        prompt = _SUGGEST_QUESTION_PROMPT.format(context=context, question_type=question_type)
        data = json.loads(await self._chat(prompt))
        return GeneratedQuestion(**data)

    async def get_expected_answer(self, question: str, criteria: list[str], context: str) -> str:
        prompt = _EXPECTED_ANSWER_PROMPT.format(
            context=context, question=question, criteria=", ".join(criteria)
        )
        data = json.loads(await self._chat(prompt))
        return data["answer"]

    async def generate_plan(self, prompt: str, question_count: int = 10) -> GeneratedPlan:
        full_prompt = _GENERATE_PLAN_PROMPT.format(prompt=prompt, question_count=question_count)
        data = json.loads(await self._chat(full_prompt))
        return GeneratedPlan(
            name=data["name"],
            description=data["description"],
            questions=[GeneratedQuestion(**q) for q in data["questions"]],
        )
