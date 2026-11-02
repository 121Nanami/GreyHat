"""Run retrieval eval and return per-case + aggregate metrics."""

from __future__ import annotations

from .dataset import EvalSet
from .metrics import aggregate, hit_at_k, mrr, ndcg_at_k
from .retriever import TfidfRetriever


def run_eval(evalset: EvalSet, *, k: int = 5) -> dict:
    retriever = TfidfRetriever(evalset.documents)
    rows = []
    for case in evalset.cases:
        ranked = retriever.search(case.query, k=k)
        ranked_ids = [doc_id for doc_id, _ in ranked]
        scores = {doc_id: score for doc_id, score in ranked}
        rel = set(case.relevant_ids)
        rows.append(
            {
                "case_id": case.id,
                "query": case.query,
                "relevant_ids": case.relevant_ids,
                "ranked_ids": ranked_ids,
                "scores": scores,
                "hit@1": hit_at_k(ranked_ids, rel, 1),
                "hit@3": hit_at_k(ranked_ids, rel, 3),
                "mrr": mrr(ranked_ids, rel),
                "ndcg@5": ndcg_at_k(ranked_ids, rel, 5),
            }
        )
    return {
        "k": k,
        "n_cases": len(rows),
        "n_docs": len(evalset.documents),
        "aggregate": aggregate(rows, ks=(1, 3, 5)),
        "cases": rows,
    }
