"""CLI for rag-eval-harness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .dataset import load_evalset
from .evaluate import run_eval


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="rageval",
        description=(
            "Offline RAG retrieval eval harness (TF-IDF baseline). "
            "Measures Hit@K / MRR / nDCG on a labeled mini corpus — no API keys required."
        ),
    )
    p.add_argument(
        "dataset",
        nargs="?",
        default=None,
        help="Path to eval JSON (default: bundled testdata/mini_corpus.json)",
    )
    p.add_argument("-k", type=int, default=5, help="Retrieve top-k (default 5)")
    p.add_argument("-j", "--json", action="store_true", help="Full JSON report")
    p.add_argument("-V", "--version", action="version", version=f"rageval {__version__}")
    return p


def _default_dataset() -> Path:
    return Path(__file__).resolve().parents[1] / "testdata" / "mini_corpus.json"


def print_human(result: dict) -> None:
    agg = result["aggregate"]
    print(f"rag-eval — docs={result['n_docs']} cases={result['n_cases']} k={result['k']}")
    print("Aggregate:")
    for key in sorted(agg):
        print(f"  {key:<10} {agg[key]:.3f}")
    print("\nPer case:")
    for row in result["cases"]:
        top = ",".join(row["ranked_ids"][:3]) or "-"
        print(
            f"  {row['case_id']:<8} hit@1={row['hit@1']:.0f} mrr={row['mrr']:.2f}  "
            f"q={row['query'][:40]!r}  top=[{top}]"
        )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.dataset) if args.dataset else _default_dataset()
    if not path.is_file():
        print(f"dataset not found: {path}", file=sys.stderr)
        return 2
    result = run_eval(load_evalset(path), k=args.k)
    if args.json:
        json.dump(result, sys.stdout, indent=2)
        print()
    else:
        print_human(result)
    # Soft quality gate for the demo corpus
    if result["aggregate"].get("mrr", 0) < 0.3:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
