from app.services.paper_analyzer import analyze_paper


title = "Fake News Detection"

abstract = """
The rise of social media produces inconsistent online news, which
leaves readers perplexed and unsure. Fake news frequently surfaces
and grows daily, influencing and deceiving societies. Numerous
research projects attempt to distinguish genuine news from fake news
on social media platforms. The spread of false information can be
stopped through quick and accurate identification. The research
discusses fake news detection approaches and related challenges.
"""


result = analyze_paper(
    title=title,
    abstract=abstract
)


print("\n===== PAPER ANALYSIS =====\n")

print("Research Problem:")
print(result.research_problem)

print("\nMethodology:")
print(result.methodology)

print("\nModels / Techniques:")
for item in result.models_or_techniques:
    print("-", item)

print("\nDatasets:")
for item in result.datasets:
    print("-", item)

print("\nEvaluation Metrics:")
for item in result.evaluation_metrics:
    print("-", item)

print("\nKey Findings:")
for item in result.key_findings:
    print("-", item)

print("\nLimitations:")
for item in result.limitations:
    print("-", item)