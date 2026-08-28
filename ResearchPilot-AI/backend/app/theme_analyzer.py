from typing import List

from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
import os


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=api_key)


class ThemeAnalysis(BaseModel):
    common_research_themes: List[str]
    common_methods: List[str]
    common_datasets: List[str]
    common_techniques: List[str]
    emerging_directions: List[str]
    major_differences: List[str]


def analyze_research_themes(papers: List[str]) -> ThemeAnalysis:

    papers_text = "\n\n".join(
        f"Paper {i + 1}:\n{paper}"
        for i, paper in enumerate(papers)
    )

    prompt = f"""
You are an expert academic research analyst.

Analyze the following collection of research papers.

{papers_text}

Identify:

1. Common research themes
2. Common methodologies or methods
3. Common datasets
4. Common techniques or models
5. Emerging research directions
6. Major differences between the papers

Rules:

- Base your analysis ONLY on the information provided.
- Do not invent papers, datasets, methods, or results.
- If information is unavailable, say "Not specified".
- Do not claim that an identified direction is definitely a research gap.
- Return concise but useful academic analysis.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ThemeAnalysis,
        },
    )

    return response.parsed
