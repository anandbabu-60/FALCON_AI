from typing import List

from pydantic import BaseModel

from app.integrations.gemini import generate_content


class PaperAnalysis(BaseModel):
    research_problem: str
    methodology: str
    models_or_techniques: List[str]
    datasets: List[str]
    evaluation_metrics: List[str]
    key_findings: List[str]
    limitations: List[str]


def analyze_paper(title: str, abstract: str) -> PaperAnalysis:
    prompt = f"""
You are an expert academic research assistant. Analyze this paper using ONLY its title and abstract.
Return JSON with research_problem, methodology, models_or_techniques, datasets, evaluation_metrics,
key_findings, and limitations. Do not invent information; use \"Not specified\" when unavailable.

Paper title: {title}
Abstract: {abstract}
"""
    return generate_content(prompt, response_schema=PaperAnalysis)
