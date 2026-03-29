import json
from typing import Any

from groq import Groq

from config import settings


class AIServiceError(RuntimeError):
    """Raised when the Groq API cannot fulfill a request."""


class GroqService:
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None

    @property
    def available(self) -> bool:
        return self.client is not None

    def generate_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 700,
    ) -> str:
        if not self.client:
            raise AIServiceError("GROQ_API_KEY is missing.")

        try:
            completion = self.client.chat.completions.create(
                model=settings.groq_model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except Exception as exc:
            raise AIServiceError(f"Groq request failed: {exc}") from exc

        content = completion.choices[0].message.content
        if not content:
            raise AIServiceError("Groq returned an empty response.")
        return content.strip()

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> Any:
        content = self.generate_text(
            system_prompt=system_prompt,
            user_prompt=f"{user_prompt}\n\nReturn valid JSON only.",
            temperature=temperature,
            max_tokens=max_tokens,
        )
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(cleaned)
