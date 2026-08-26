import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors
from fastapi import HTTPException


# ============================================================
# Environment
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")


# ============================================================
# Gemini Configuration
# ============================================================

MODEL_NAME = "gemini-3.6-flash"

client = genai.Client(
    api_key=api_key
)


# ============================================================
# Generate Structured / Normal Content
# ============================================================

def generate_content(
    prompt: str,
    response_schema=None
):
    try:

        config = None

        if response_schema:

            config = {
                "response_mime_type": "application/json",
                "response_schema": response_schema,
            }

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config,
        )

        # ----------------------------------------------------
        # Structured response
        # ----------------------------------------------------

        if response_schema:

            if response.parsed is None:

                raise HTTPException(
                    status_code=502,
                    detail={
                        "error": "Invalid AI response",
                        "message": (
                            "Gemini returned a response that "
                            "could not be parsed into the "
                            "requested research schema."
                        ),
                        "retryable": True,
                    },
                )

            return response.parsed

        # ----------------------------------------------------
        # Normal text response
        # ----------------------------------------------------

        if not response.text:

            raise HTTPException(
                status_code=502,
                detail={
                    "error": "Empty AI response",
                    "message": (
                        "Gemini returned an empty response."
                    ),
                    "retryable": True,
                },
            )

        return response.text

    except HTTPException:
        raise

    except errors.ClientError as e:

        # ----------------------------------------------------
        # Gemini quota / rate limit
        # ----------------------------------------------------

        if e.code == 429:

            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Gemini API quota exceeded",
                    "message": (
                        "The Gemini API quota has been "
                        "exhausted. Please wait for the "
                        "quota to reset or check the "
                        "Gemini API plan."
                    ),
                    "retryable": True,
                },
            )

        # ----------------------------------------------------
        # Other Gemini client errors
        # ----------------------------------------------------

        raise HTTPException(
            status_code=502,
            detail={
                "error": "Gemini API error",
                "message": str(e),
                "retryable": False,
            },
        )

    except errors.ServerError as e:

        # ----------------------------------------------------
        # Temporary Gemini server failure
        # ----------------------------------------------------

        raise HTTPException(
            status_code=503,
            detail={
                "error": "Gemini API temporarily unavailable",
                "message": (
                    "The Gemini service is temporarily "
                    "unavailable. Please try again later."
                ),
                "retryable": True,
            },
        )

    except Exception as e:

        # ----------------------------------------------------
        # Unexpected error
        # ----------------------------------------------------

        raise HTTPException(
            status_code=502,
            detail={
                "error": "AI service error",
                "message": str(e),
                "retryable": False,
            },
        )


# ============================================================
# RAG Answer Generation
# ============================================================

def generate_answer(
    prompt: str
):
    """
    Generate a plain-text answer for the RAG pipeline.
    """

    return generate_content(
        prompt=prompt
    )