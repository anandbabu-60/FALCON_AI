from functools import lru_cache
from typing import Any

from fastapi import HTTPException

from app.core.config import get_settings


def health_status() -> dict[str, object]:
    settings = get_settings()
    try:
        from google import genai  # noqa: F401
        sdk_installed = True
    except ImportError:
        sdk_installed = False
    return {
        "configured": bool(settings.gemini_api_key),
        "sdk_installed": sdk_installed,
        "model": settings.gemini_model,
    }


@lru_cache
def _client():
    settings = get_settings()
    if not settings.gemini_api_key:
        raise HTTPException(status_code=503, detail={"error": "AI service is not configured", "message": "Set GEMINI_API_KEY on the backend server.", "retryable": False})
    try:
        from google import genai
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="The Gemini SDK is not installed") from exc
    return genai.Client(api_key=settings.gemini_api_key)


def generate_content(prompt: str, response_schema: Any = None):
    try:
        config = None
        if response_schema is not None:
            config = {"response_mime_type": "application/json", "response_schema": response_schema}
        response = _client().models.generate_content(model=get_settings().gemini_model, contents=prompt, config=config)
        if response_schema is not None:
            if response.parsed is None:
                raise HTTPException(status_code=502, detail={"error": "Invalid AI response", "message": "Gemini could not produce the requested research schema.", "retryable": True})
            return response.parsed
        if not response.text:
            raise HTTPException(status_code=502, detail={"error": "Empty AI response", "message": "Gemini returned an empty response.", "retryable": True})
        return response.text
    except HTTPException:
        raise
    except Exception as exc:
        code = getattr(exc, "code", None)
        error_text = str(exc)
        if code == 401 or "UNAUTHENTICATED" in error_text.upper() or " 401 " in error_text:
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "Gemini API key rejected",
                    "message": "The GEMINI_API_KEY was rejected by Google. Create a new key and restart the API container.",
                    "retryable": False,
                },
            ) from exc
        if code == 429:
            raise HTTPException(status_code=429, detail={"error": "Gemini API quota exceeded", "message": "Wait for the quota to reset or use a different Gemini plan.", "retryable": True}) from exc
        if code is not None and code >= 500:
            raise HTTPException(status_code=503, detail={"error": "Gemini API temporarily unavailable", "message": str(exc), "retryable": True}) from exc
        raise HTTPException(status_code=502, detail={"error": "Gemini API error", "message": str(exc), "retryable": False}) from exc


def generate_answer(prompt: str) -> str:
    return generate_content(prompt)
