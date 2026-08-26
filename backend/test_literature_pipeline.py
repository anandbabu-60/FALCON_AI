from app.services.paper_analyzer import analyze_paper
from app.services.theme_analyzer import analyze_research_themes
from app.services.gap_analyzer import analyze_research_gaps


papers = [
    {
        "title": "Fake News Detection",
        "abstract": """
        The rise of social media produces inconsistent online news,
        leaving readers perplexed and unsure. Fake news frequently
        surfaces and grows daily, influencing and deceiving societies.
        Research projects attempt to distinguish genuine news from
        fake news on social media platforms. The research discusses
        fake news detection approaches and related challenges.
        """
    },
    {
        "title": "Machine Learning for Fake News Detection",
        "abstract": """
        This study investigates machine learning techniques for
        identifying fake news on social media. A social media news
        dataset is used to evaluate classification performance using
        accuracy and F1-score. The study discusses challenges in
        generalizing fake news detection models.
        """
    }
]


# --------------------------------------------------
# 1. Analyze individual papers
# --------------------------------------------------

paper_analyses = []

for paper in papers:

    analysis = analyze_paper(
        title=paper["title"],
        abstract=paper["abstract"]
    )

    paper_analyses.append(analysis)

print("\n===== PAPER ANALYSES COMPLETE =====")


# --------------------------------------------------
# 2. Convert analyses into text for theme analysis
# --------------------------------------------------

paper_analysis_text = []

for i, analysis in enumerate(paper_analyses, start=1):

    text = f"""
Paper {i}

Research Problem:
{analysis.research_problem}

Methodology:
{analysis.methodology}

Models or Techniques:
{analysis.models_or_techniques}

Datasets:
{analysis.datasets}

Evaluation Metrics:
{analysis.evaluation_metrics}

Key Findings:
{analysis.key_findings}

Limitations:
{analysis.limitations}
"""

    paper_analysis_text.append(text)


# --------------------------------------------------
# 3. Analyze common themes
# --------------------------------------------------

theme_analysis = analyze_research_themes(
    papers=paper_analysis_text
)

print("\n===== THEME ANALYSIS =====")

print("Common Themes:")
for item in theme_analysis.common_research_themes:
    print("-", item)

print("\nEmerging Directions:")
for item in theme_analysis.emerging_directions:
    print("-", item)


# --------------------------------------------------
# 4. Prepare information for gap analyzer
# --------------------------------------------------

gap_paper_analyses = paper_analysis_text

theme_text = f"""
Common Research Themes:
{theme_analysis.common_research_themes}

Common Methods:
{theme_analysis.common_methods}

Common Datasets:
{theme_analysis.common_datasets}

Common Techniques:
{theme_analysis.common_techniques}

Emerging Directions:
{theme_analysis.emerging_directions}

Major Differences:
{theme_analysis.major_differences}
"""


# --------------------------------------------------
# 5. Detect research gaps
# --------------------------------------------------

gap_analysis = analyze_research_gaps(
    research_topic="Fake news detection on social media",
    paper_analyses=gap_paper_analyses,
    theme_analysis=theme_text
)

print("\n===== RESEARCH GAPS =====")

for gap in gap_analysis.gaps:

    print("\nGap:", gap.gap_title)
    print("Observation:", gap.observation)
    print("Evidence:", gap.evidence)
    print("Potential Direction:", gap.potential_direction)
    print("Confidence:", gap.confidence)


print("\n===== OVERALL RESEARCH DIRECTION =====")
print(gap_analysis.overall_research_direction)