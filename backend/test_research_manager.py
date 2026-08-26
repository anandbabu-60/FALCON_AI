from app.agents.research_manager import ResearchManager


manager = ResearchManager()

result = manager.analyze_paper(
    title="Fake News Detection",
    abstract="""
    This research studies the detection of fake news on social media.
    The paper discusses the spread of false information and the need
    for accurate detection methods.
    """
)

print("\n===== RESEARCH MANAGER TEST =====\n")

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