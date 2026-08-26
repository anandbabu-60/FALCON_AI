from app.services.roadmap_generator import generate_roadmap


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

experiment_plan = """
Research question:
How do advanced deep learning architectures using textual
and social media features compare with traditional machine
learning baselines in cross-domain fake news detection?

Datasets:
FakeNewsNet, PHEME, LIAR.

Baseline models:
Traditional machine learning models using scikit-learn.

Proposed models:
Advanced deep learning architectures using PyTorch.

Experiments:
In-domain evaluation, cross-domain evaluation, and
ablation studies comparing textual and social media features.

Evaluation:
Accuracy, Precision, Recall, and F1-score.
"""


result = generate_roadmap(
    research_topic=research_topic,
    research_gaps=research_gaps,
    methodology=methodology,
    experiment_plan=experiment_plan
)


print("\n===== RESEARCH ROADMAP =====\n")

print("Research Goal:")
print(result.research_goal)

for i, phase in enumerate(result.phases, start=1):

    print(f"\n===== PHASE {i}: {phase.phase} =====")

    print("\nObjective:")
    print(phase.objective)

    print("\nTasks:")
    for item in phase.tasks:
        print("-", item)

    print("\nDeliverables:")
    for item in phase.deliverables:
        print("-", item)

    print("\nMilestones:")
    for item in phase.milestones:
        print("-", item)


print("\n===== FINAL DELIVERABLES =====")

for item in result.final_deliverables:
    print("-", item)