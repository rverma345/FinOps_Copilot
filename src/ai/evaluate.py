# src/analytics/eval_rag.py
import pandas as pd
from src.ai.rag_engine import get_answer
from typing import List


#10-15 Q&A pairs
test_set = [
    {"question": "What is FinOps?", "answer": "FinOps is a set of practices to manage cloud costs."},
    {"question": "How can we optimize AWS EC2 usage?", "answer": "Use rightsizing, reserved instances, and spot instances."},
    {"question": "What is a common FinOps KPI?", "answer": "Cost per workload, cost savings, utilization rate."},
    {"question": "How do you track cloud spend?", "answer": "By using tagging, reporting, and dashboards."},
    {"question": "Best way to reduce S3 costs?", "answer": "Use lifecycle policies and storage class optimization."},
    {"question": "What is a reserved instance?", "answer": "A reserved instance is a pre-paid compute resource offering discount over on-demand pricing."},
    {"question": "How to monitor cost anomalies?", "answer": "Use cloud provider alerts and anomaly detection dashboards."},
    {"question": "What is the role of a FinOps team?", "answer": "To manage cloud cost, efficiency, and governance."},
    {"question": "How to estimate future cloud spend?", "answer": "Use historical trends, forecasting, and predictive analytics."},
    {"question": "Why is tagging important?", "answer": "Tagging helps allocate costs and manage resources effectively."},
]


# 2. Evaluation metrics

def recall_at_k(retrieved_docs: List, ground_truth: str, k: int = 3) -> int:
    """
    Returns 1 if any of top-k retrieved documents contain keywords from the ground truth.
    """
    for doc in retrieved_docs[:k]:
        if any(word.lower() in doc.page_content.lower() for word in ground_truth.split()):
            return 1
    return 0

def subjective_score(answer: str, ground_truth: str) -> int:
    """
    Simple subjective scoring 1-5 based on correctness and relevance.
    5 = perfect match, 1 = irrelevant/wrong
    """
    answer_lower = answer.lower()
    gt_lower = ground_truth.lower()
    if gt_lower in answer_lower:
        return 5
    elif any(word in answer_lower for word in gt_lower.split()):
        return 3
    else:
        return 1


# 3. Run evaluation

results = []

for item in test_set:
    question = item["question"]
    ground_truth = item["answer"]

    # Call RAG engine
    answer, retrieved_docs = get_answer(question)

    # Metrics
    r3 = recall_at_k(retrieved_docs, ground_truth, k=3)
    s_score = subjective_score(answer, ground_truth)

    results.append({
        "question": question,
        "ground_truth": ground_truth,
        "generated_answer": answer,
        "retrieved_docs_count": len(retrieved_docs),
        "Recall@3": r3,
        "SubjectiveScore": s_score
    })

# 4. saving results
df = pd.DataFrame(results)
df.to_csv("src/ai/evaluation_results.csv", index=False)
print("Evaluation completed. Results saved to evaluation_results.csv")

# Print summary
print("Average Recall@3:", df["Recall@3"].mean())
print("Average Subjective Score:", df["SubjectiveScore"].mean())
