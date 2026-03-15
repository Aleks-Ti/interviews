import json
import logging
import re

import anthropic

from interviews.providers.base import AIProvider, GeneratedPlan, GeneratedQuestion, QuestionAnalysis


def _parse_json(text: str) -> dict:
    text = text.strip()
    # Strip markdown code block if present: ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        text = match.group(1).strip()
    if not text:
        raise ValueError("Empty response from AI provider")
    return json.loads(text)

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


_SYSTEM_PROMPT = "Ты — помощник интервьюера. Все текстовые поля в ответах (названия, описания, вопросы, критерии, итоги, сильные и слабые стороны) пиши на русском языке. JSON-ключи и enum-значения (hire, consider, reject, technical, behavioral, custom) оставляй как есть."


class AnthropicProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001") -> None:
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def _complete(self, prompt: str, max_tokens: int = 1024) -> str:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text if response.content else ""
        logging.debug("AI raw response (stop_reason=%s): %r", response.stop_reason, text[:200])
        return text

    async def transcribe(self, audio: bytes, filename: str = "audio.webm") -> str:
        raise NotImplementedError(
            "Anthropic does not support audio transcription. "
            "Set AI_PROVIDER=openai or add a dedicated transcription service."
        )

    async def analyze_answer(self, question: str, answer: str, criteria: list[str]) -> QuestionAnalysis:
        prompt = _ANALYZE_PROMPT.format(question=question, answer=answer, criteria=", ".join(criteria))
        data = _parse_json(await self._complete(prompt))
        return QuestionAnalysis(**data)

    async def suggest_question(self, context: str, question_type: str = "technical") -> GeneratedQuestion:
        prompt = _SUGGEST_QUESTION_PROMPT.format(context=context, question_type=question_type)
        data = _parse_json(await self._complete(prompt))
        return GeneratedQuestion(**data)

    async def get_expected_answer(self, question: str, criteria: list[str], context: str) -> str:
        prompt = _EXPECTED_ANSWER_PROMPT.format(
            context=context, question=question, criteria=", ".join(criteria)
        )
        data = _parse_json(await self._complete(prompt, max_tokens=2048))
        return data["answer"]

    async def generate_plan(self, prompt: str, question_count: int = 10) -> GeneratedPlan:
        full_prompt = _GENERATE_PLAN_PROMPT.format(prompt=prompt, question_count=question_count)
        data = _parse_json(await self._complete(full_prompt, max_tokens=4096))
        return GeneratedPlan(
            name=data["name"],
            description=data["description"],
            questions=[GeneratedQuestion(**q) for q in data["questions"]],
        )
