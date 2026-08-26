from app.agents.research_manager import ResearchManager


manager = ResearchManager()


papers = [
    {
        "title": "Fake News Detection",
        "abstract": """
        This research discusses the problem of fake news spreading
        through social media platforms. False information can confuse
        users and influence decision-making. The study discusses
        approaches for detecting fake news and the challenges involved
        in identifying false information.
        """
    },
    {
        "title": "Machine Learning for Fake News Detection",
        "abstract": """
        This study investigates machine learning approaches for fake
        news detection on social media. The research evaluates
        classification approaches and discusses challenges in
        generalizing detection models across different datasets and
        social media contexts.
        """
    }
]


print("\nStarting full research workflow...\n")

result = manager.run_research_workflow(
    research_topic="Fake news detection on social media",
    papers=papers
)


print("\n===== FULL RESEARCH WORKFLOW =====")


print("\n===== PAPER ANALYSES =====")

for i, analysis in enumerate(
    result["paper_analyses"],
    start=1
):
    print(f"\n--- Paper {i} ---")
    print("Research Problem:")
    print(analysis.research_problem)

    print("Methodology:")
    print(analysis.methodology)


print("\n===== THEME ANALYSIS =====")

theme = result["theme_analysis"]

for item in theme.common_research_themes:
    print("-", item)


print("\n===== RESEARCH GAPS =====")

gaps = result["gap_analysis"]

for gap in gaps.gaps:
    print("\nGap:", gap.gap_title)
    print("Observation:", gap.observation)
    print("Direction:", gap.potential_direction)
    print("Confidence:", gap.confidence)


print("\n===== DATASET RECOMMENDATIONS =====")

datasets = result["dataset_recommendations"]

for dataset in datasets.recommendations:
    print("-", dataset.name)
    print("  Suitability:", dataset.suitability)


print("\n===== TOOL RECOMMENDATIONS =====")

tools = result["tool_recommendations"]

for tool in tools.recommendations:
    print("-", tool.name)
    print("  Suitability:", tool.suitability)


print("\n===== METHODOLOGY =====")

methodology = result["methodology_recommendations"]

for item in methodology.recommendations:
    print("-", item.methodology_name)
    print("  Design:", item.research_design)
    print("  Suitability:", item.suitability)


print("\n===== EXPERIMENT PLAN =====")

experiments = result["experiment_plan"]

for plan in experiments.plans:
    print("Research Question:")
    print(plan.research_question)

    print("\nHypothesis:")
    print(plan.hypothesis)

    print("\nExperiments:")
    for experiment in plan.experiments:
        print("-", experiment)


print("\n===== ROADMAP =====")

roadmap = result["roadmap"]

print("Research Goal:")
print(roadmap.research_goal)

for phase in roadmap.phases:
    print(f"\n{phase.phase}")
    print("Objective:", phase.objective)

    print("Milestones:")
    for milestone in phase.milestones:
        print("-", milestone)


print("\n===== WORKFLOW COMPLETE =====")
