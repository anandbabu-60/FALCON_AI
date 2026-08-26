from app.services.gap_analyzer import analyze_research_gaps


research_topic = "Fake news detection on social media"

paper_analyses = [
    """
    The paper discusses the rapid spread of fake news on social media
    and the impact of misinformation on users. It highlights the need
    for accurate fake news detection and discusses existing detection
    approaches and evaluation metrics.
    """
]

theme_analysis = """
Major themes include fake news detection, social media misinformation,
user confusion, decision-making, and the challenges of detecting false
information accurately.
"""


result = analyze_research_gaps(
    research_topic=research_topic,
    paper_analyses=paper_analyses,
    theme_analysis=theme_analysis
)


print("\n===== RESEARCH GAPS =====\n")

for gap in result.gaps:

    print("Gap:", gap.gap_title)
    print("Observation:", gap.observation)
    print("Evidence:", gap.evidence)
    print("Potential Direction:", gap.potential_direction)
    print("Confidence:", gap.confidence)
    print()

print("===== OVERALL DIRECTION =====")
print(result.overall_research_direction) 