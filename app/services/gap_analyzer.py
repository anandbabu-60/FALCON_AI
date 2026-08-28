from typing import List, Optional

from pydantic import BaseModel

from app.integrations.gemini import generate_content


class ResearchGap(BaseModel):
    gap_title: str
    observation: str
    evidence: List[str]
    potential_direction: str
    confidence: str


class GapAnalysis(BaseModel):
    gaps: List[ResearchGap]
    overall_research_direction: str


def analyze_research_gaps(research_topic: str, paper_analyses: List[str], theme_analysis: str, evidence: Optional[List[dict]] = None) -> GapAnalysis:
    papers_text = "\n\n".join(f"Paper Analysis {i + 1}:\n{paper}" for i, paper in enumerate(paper_analyses))
    evidence_text = "\n\n".join(f"[Evidence {item.get('id', 'Unknown')}] {item.get('source', 'Unknown')} p.{item.get('page', 'Unknown')}\n{item.get('text', '')}" for item in (evidence or [])) or "No additional retrieved research evidence was provided."
    prompt = f"""
You are an expert academic research advisor. Identify POTENTIAL research gaps from only the supplied information.
Use cautious academic language and do not claim novelty or invent evidence. Return JSON with gaps and
overall_research_direction. Each gap requires gap_title, observation, evidence, potential_direction, and
confidence (Low, Moderate, or High).

Research topic: {research_topic}
Research themes: {theme_analysis}
Paper analyses: {papers_text}
Retrieved evidence: {evidence_text}
"""
    return generate_content(prompt, response_schema=GapAnalysis)
