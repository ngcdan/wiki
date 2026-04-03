"""Module 1 demo: embed sentences and compute cosine similarity."""

import sys
sys.path.insert(0, ".")

from src.embedder import embed


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    return dot / (norm_a * norm_b)


def main():
    sentences = [
        "Con mèo ngồi trên thảm",
        "Chú mèo nằm trên tấm thảm",
        "Thời tiết hôm nay đẹp quá",
    ]

    print("Embedding sentences...")
    vectors = [embed(s) for s in sentences]

    print("\nCosine similarity:")
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            sim = cosine_similarity(vectors[i], vectors[j])
            print(f"  [{i}] vs [{j}]: {sim:.4f}")
            print(f"    \"{sentences[i]}\"")
            print(f"    \"{sentences[j]}\"")
            print()


if __name__ == "__main__":
    main()
