"""Retrieval metrics: Hit@K, MRR, nDCG@K."""

from __future__ import annotations

import math


def hit_at_k(ranked_ids: list[str], relevant: set[str], k: int) -> float:
    return 1.0 if any(doc_id in relevant for doc_id in ranked_ids[:k]) else 0.0


def mrr(ranked_ids: list[str], relevant: set[str]) -> float:
    for i, doc_id in enumerate(ranked_ids, start=1):
        if doc_id in relevant:
            return 1.0 / i
    return 0.0


def dcg_at_k(ranked_ids: list[str], relevant: set[str], k: int) -> float:
    score = 0.0
    for i, doc_id in enumerate(ranked_ids[:k], start=1):
        rel = 1.0 if doc_id in relevant else 0.0
        score += rel / math.log2(i + 1)
    return score


def ndcg_at_k(ranked_ids: list[str], relevant: set[str], k: int) -> float:
    ideal_hits = min(k, len(relevant))
    if ideal_hits == 0:
        return 0.0
    ideal = [f"__ideal_{i}" for i in range(ideal_hits)]
    ideal_rel = set(ideal)
    ideal_dcg = dcg_at_k(ideal, ideal_rel, k)
    if ideal_dcg == 0:
        return 0.0
    return dcg_at_k(ranked_ids, relevant, k) / ideal_dcg


def aggregate(rows: list[dict], ks: tuple[int, ...] = (1, 3, 5)) -> dict[str, float]:
    out: dict[str, float] = {"mrr": 0.0}
    for k in ks:
        out[f"hit@{k}"] = 0.0
        out[f"ndcg@{k}"] = 0.0
    if not rows:
        return out
    n = len(rows)
    for row in rows:
        ranked = row["ranked_ids"]
        rel = set(row["relevant_ids"])
        out["mrr"] += mrr(ranked, rel)
        for k in ks:
            out[f"hit@{k}"] += hit_at_k(ranked, rel, k)
            out[f"ndcg@{k}"] += ndcg_at_k(ranked, rel, k)
    return {k: v / n for k, v in out.items()}
