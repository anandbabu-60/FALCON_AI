from app.services.tool_recommender import recommend_tools


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


result = recommend_tools(
    research_topic=research_topic,
    research_gaps=research_gaps,
    methodology=methodology
)


print("\n===== TOOL RECOMMENDATIONS =====\n")

for i, tool in enumerate(result.recommendations, start=1):

    print(f"--- Tool {i} ---")

    print("Name:", tool.name)
    print("Purpose:", tool.purpose)
    print("Relevance:", tool.relevance)

    print("\nStrengths:")
    for item in tool.strengths:
        print("-", item)

    print("\nLimitations:")
    for item in tool.limitations:
        print("-", item)

    print("\nSuitability:")
    print(tool.suitability)

    print()