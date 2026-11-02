# rag-eval-harness

A **stdlib-only RAG retrieval evaluation harness**. Load a labeled mini corpus,
run a TF-IDF cosine baseline, and report Hit@K / MRR / nDCG — the same metrics
AI eng interviews expect you to discuss.

## Problem

“We added RAG” is not evidence. Without a labeled set and ranking metrics, you
cannot tell whether chunking or retrieval actually improved answerability.

## Solution

`rageval` provides:

- JSON eval set format (`documents` + `cases` with `relevant_ids`)
- Offline TF-IDF retriever (no embeddings API, no GPU)
- Aggregate + per-query Hit@1/3/5, MRR, nDCG@5
- Human table and JSON for notebooks / CI

Swap in your own corpus JSON to measure a real pipeline later; this demo proves
you can instrument eval before calling a vendor model.

## How to run

```bash
cd docs/portfolio/rag-eval-harness
python3 -m rageval
python3 -m rageval testdata/mini_corpus.json -k 5
python3 -m rageval -j
./smoke.sh
```

## Sample output

```
rag-eval — docs=8 cases=6 k=5
Aggregate:
  hit@1      0.833
  hit@3      1.000
  hit@5      1.000
  mrr        0.917
  ndcg@1     0.833
  ndcg@3     0.943
  ndcg@5     0.943

Per case:
  q1       hit@1=1 mrr=1.00  q='How do phishing sites steal bank passwo…'  top=[d1,d2,…]
  q2       hit@1=1 mrr=1.00  q='What metrics evaluate RAG retrieval…'     top=[d4,…]
```

## License

MIT
