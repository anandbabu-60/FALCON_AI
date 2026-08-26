from app.services.methodology_planner import recommend_methodology


research_topic = "Fake news detection on social media"

research_gaps = [
    "Model generalization across diverse social media contexts",
    "Specific feature representation and advanced architecture comparisons"
]

available_datasets = [
    "FakeNewsNet",
    "PHEME",
    "LIAR"
]

available_tools = [
    "Python",
    "scikit-learn",
    "PyTorch"
]


result = recommend_methodology(
    research_topic=research_topic,
    research_gaps=research_gaps,
    available_datasets=available_datasets,
    available_tools=available_tools
)


print("\n===== METHODOLOGY RECOMMENDATIONS =====\n")

for i, methodology in enumerate(result.recommendations, start=1):

    print(f"--- Methodology {i} ---")

    print("Name:", methodology.methodology_name)
    print("Research Design:", methodology.research_design)

    print("\nRecommended Methods:")
    for item in methodology.recommended_methods:
        print("-", item)

    print("\nData Requirements:")
    for item in methodology.data_requirements:
        print("-", item)

    print("\nEvaluation Strategy:")
    for item in methodology.evaluation_strategy:
        print("-", item)

    print("\nStrengths:")
    for item in methodology.strengths:
        print("-", item)

    print("\nLimitations:")
    for item in methodology.limitations:
        print("-", item)

    print("\nSuitability:")
    print(methodology.suitability)

    print()