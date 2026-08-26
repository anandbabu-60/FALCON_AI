from app.services.theme_analyzer import analyze_research_themes


paper_analyses = [
    """
    Research problem: Detecting fake news on social media.

    Methodology: Review and discussion of fake news detection approaches.

    Models or techniques: Not specified.

    Datasets: Not specified.

    Evaluation metrics: Not specified.

    Key findings:
    The research discusses fake news detection approaches and
    challenges related to detecting false information.

    Limitations: Not specified.
    """,

    """
    Research problem: Identifying false information on social media.

    Methodology: Machine-learning-based fake news detection.

    Models or techniques: Machine learning classification techniques.

    Datasets: Social media news dataset.

    Evaluation metrics: Accuracy and F1-score.

    Key findings:
    Machine learning techniques can help identify misleading
    information.

    Limitations:
    Dataset limitations may affect generalization.
    """
]


result = analyze_research_themes(
    papers=paper_analyses
)


print("\n===== THEME ANALYSIS =====\n")

print("Common Research Themes:")
for item in result.common_research_themes:
    print("-", item)

print("\nCommon Methods:")
for item in result.common_methods:
    print("-", item)

print("\nCommon Datasets:")
for item in result.common_datasets:
    print("-", item)

print("\nCommon Techniques:")
for item in result.common_techniques:
    print("-", item)

print("\nEmerging Directions:")
for item in result.emerging_directions:
    print("-", item)

print("\nMajor Differences:")
for item in result.major_differences:
    print("-", item)