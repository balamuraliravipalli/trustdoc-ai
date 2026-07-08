from openai import OpenAI, RateLimitError, APIError, AuthenticationError
from fastapi import HTTPException
from app.core.config import get_settings


class OpenAIService:
    def __init__(self):
        self.settings = get_settings()
        if not self.settings.openai_api_key or self.settings.openai_api_key == "replace_me":
            raise HTTPException(status_code=400, detail="OPENAI_API_KEY is missing. Add it to your .env file.")
        self.client = OpenAI(api_key=self.settings.openai_api_key)

    def _friendly_error(self, exc: Exception) -> HTTPException:
        if isinstance(exc, AuthenticationError):
            return HTTPException(status_code=401, detail="OpenAI API key is invalid. Check OPENAI_API_KEY in .env.")
        if isinstance(exc, RateLimitError):
            return HTTPException(status_code=402, detail="OpenAI API quota/billing issue. Add funds or check usage limits, then restart Docker.")
        if isinstance(exc, APIError):
            return HTTPException(status_code=502, detail=f"OpenAI API error: {exc}")
        return HTTPException(status_code=500, detail=str(exc))

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            response = self.client.embeddings.create(
                model=self.settings.openai_embedding_model,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception as exc:  # noqa: BLE001
            raise self._friendly_error(exc) from exc

    def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self.client.responses.create(
                model=self.settings.openai_chat_model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.output_text
        except Exception as exc:  # noqa: BLE001
            raise self._friendly_error(exc) from exc
