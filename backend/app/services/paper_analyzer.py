import os
from typing import List

from dotenv import load_dotenv
from google import genai
from google.genai import errors
from fastapi import HTTPException
from pydantic import BaseModel


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=api_key)


class PaperAnalysis(BaseModel):
    research_problem: str
    methodology: str
    models_or_techniques: List[str]
    datasets: List[str]
    evaluation_metrics: List[str]
    key_findings: List[str]
    limitations: List[str]


def analyze_paper(
    title: str,
    abstract: str
) -> PaperAnalysis:

    prompt = f"""
You are an expert academic research assistant.

Analyze the following research paper based ONLY on the
information available in its title and abstract.

Paper title:
{title}

Abstract:
{abstract}

Extract the following:

1. Research problem
2. Methodology
3. Models or techniques used
4. Datasets mentioned
5. Evaluation metrics mentioned
6. Key findings
7. Limitations

Important rules:

- Do not invent information.
- If something is not mentioned, say "Not specified".
- Do not claim that a research gap is proven.
- Base your analysis only on the provided title and abstract.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": PaperAnalysis,
            },
        )

        return response.parsed

    except errors.ClientError as e:

        if e.code == 429:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Gemini API quota exceeded",
                    "message": (
                        "The Gemini API free-tier quota has been "
                        "exhausted. Please wait for the quota to reset "
                        "or check your Gemini API plan."
                    )
                }
            )

        raise HTTPException(
            status_code=502,
            detail={
                "error": "Gemini API error",
                "message": str(e)
            }
        )