from app.services.experiment_planner import plan_experiments


research_topic = "Fake news detection on social media"

research_gaps = [
    "Model generalization across diverse social media contexts",
    "Specific feature representation and advanced architecture comparisons"
]

methodology = """
Cross-domain empirical deep learning framework comparing
traditional machine learning baselines with advanced
deep learning architectures using textual and social
media features.
"""

datasets = [
    "FakeNewsNet",
    "PHEME",
    "LIAR"
]

tools = [
    "Python",
    "scikit-learn",
    "PyTorch"
]


result = plan_experiments(
    research_topic=research_topic,
    research_gaps=research_gaps,
    methodology=methodology,
    datasets=datasets,
    tools=tools
)


print("\n===== EXPERIMENT PLAN =====\n")

for i, plan in enumerate(result.plans, start=1):

    print(f"--- Experiment Plan {i} ---")

    print("\nResearch Question:")
    print(plan.research_question)

    print("\nHypothesis:")
    print(plan.hypothesis)

    print("\nDatasets:")
    for item in plan.datasets:
        print("-", item)

    print("\nPreprocessing Steps:")
    for item in plan.preprocessing_steps:
        print("-", item)

    print("\nBaseline Models:")
    for item in plan.baseline_models:
        print("-", item)

    print("\nProposed Models:")
    for item in plan.proposed_models:
        print("-", item)

    print("\nExperiments:")
    for item in plan.experiments:
        print("-", item)

    print("\nEvaluation Metrics:")
    for item in plan.evaluation_metrics:
        print("-", item)

    print("\nAblation Studies:")
    for item in plan.ablation_studies:
        print("-", item)

    print("\nExpected Outputs:")
    for item in plan.expected_outputs:
        print("-", item)

    print()