"""Module 6: RAG evaluation — precision@k and keyword match."""

import json
import sys
sys.path.insert(0, ".")

from src.rag import RAG


def precision_at_k(results: list[dict], expected_source: str) -> float:
    """Fraction of retrieved chunks from expected source."""
    if not results:
        return 0.0
    matches = sum(1 for r in results if expected_source in r.get("metadata", {}).get("source", ""))
    return matches / len(results)


def keyword_match(answer: str, expected: str) -> float:
    """Fraction of expected answer keywords present in actual answer."""
    expected_words = set(expected.lower().split())
    answer_words = set(answer.lower().split())
    if not expected_words:
        return 0.0
    return len(expected_words & answer_words) / len(expected_words)


def main():
    with open("scripts/eval_dataset.json") as f:
        dataset = json.load(f)

    if not dataset or dataset[0].get("question") == "Example question about the documents?":
        print("Please populate scripts/eval_dataset.json with real test cases first.")
        return

    rag = RAG()
    total_precision = 0.0
    total_keyword = 0.0

    for i, item in enumerate(dataset):
        q = item["question"]
        expected = item["expected_answer"]
        source = item["source_doc"]

        results = rag._retriever.retrieve(q, top_k=5)
        answer = rag.ask(q)

        prec = precision_at_k(results, source)
        kw = keyword_match(answer, expected)
        total_precision += prec
        total_keyword += kw

        print(f"[{i+1}] Q: {q}")
        print(f"     precision@5={prec:.2f}  keyword_match={kw:.2f}")
        print(f"     Answer: {answer[:100]}...")
        print()

    n = len(dataset)
    print(f"--- Summary ({n} questions) ---")
    print(f"Avg precision@5: {total_precision/n:.2f}")
    print(f"Avg keyword match: {total_keyword/n:.2f}")


if __name__ == "__main__":
    main()
