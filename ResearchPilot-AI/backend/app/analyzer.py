import os
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from typing import List

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=api_key)


class ResearchAnalysis(BaseModel):
    research_area: str
    research_problem: str
    research_task: str
    technologies: List[str]
    objectives: List[str]
    keywords: List[str]


def analyze_research_idea(research_idea: str) -> ResearchAnalysis:

    prompt = f"""
You are an expert academic research advisor.

Analyze the following research idea.

Research idea:
{research_idea}

Identify:

1. Research area
2. Research problem
3. Research task
4. Technologies involved
5. Main research objectives
6. Important research keywords

Return only structured information matching the requested schema.

Do not invent specific research papers, datasets, statistics,
or research results.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ResearchAnalysis,
        },
    )

    return response.parsed
