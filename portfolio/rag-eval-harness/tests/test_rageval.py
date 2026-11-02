#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rageval.dataset import load_evalset  # noqa: E402
from rageval.evaluate import run_eval  # noqa: E402
from rageval.metrics import hit_at_k, mrr, ndcg_at_k  # noqa: E402


class RagEvalTests(unittest.TestCase):
    def test_metrics_unit(self) -> None:
        ranked = ["a", "b", "c"]
        rel = {"b"}
        self.assertEqual(hit_at_k(ranked, rel, 1), 0.0)
        self.assertEqual(hit_at_k(ranked, rel, 2), 1.0)
        self.assertAlmostEqual(mrr(ranked, rel), 0.5)
        self.assertGreater(ndcg_at_k(ranked, rel, 3), 0.0)

    def test_mini_corpus_quality(self) -> None:
        result = run_eval(load_evalset(ROOT / "testdata" / "mini_corpus.json"), k=5)
        self.assertGreaterEqual(result["aggregate"]["mrr"], 0.5)
        self.assertGreaterEqual(result["aggregate"]["hit@3"], 0.6)


if __name__ == "__main__":
    unittest.main()
