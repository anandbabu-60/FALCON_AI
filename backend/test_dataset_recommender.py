from app.services.resource_recommender import recommend_datasets


research_topic = "Fake news detection on social media"

research_gaps = [
    "Model generalization across diverse social media contexts",
    "Specific feature representation and advanced architecture comparisons"
]

methodology = """
Machine learning based fake news detection using textual and
social media features, with evaluation across multiple datasets
and platforms.
"""


result = recommend_datasets(
    research_topic=research_topic,
    research_gaps=research_gaps,
    methodology=methodology
)


print("\n===== DATASET RECOMMENDATIONS =====\n")

for i, dataset in enumerate(result.recommendations, start=1):

    print(f"--- Dataset {i} ---")

    print("Name:", dataset.name)
    print("Purpose:", dataset.purpose)
    print("Relevance:", dataset.relevance)

    print("\nStrengths:")
    for item in dataset.strengths:
        print("-", item)

    print("\nLimitations:")
    for item in dataset.limitations:
        print("-", item)

    print("\nSuitability:")
    print(dataset.suitability)

    print()