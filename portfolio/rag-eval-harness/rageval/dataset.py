"""Load a mini RAG eval set from JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .retriever import Document


@dataclass
class EvalCase:
    id: str
    query: str
    relevant_ids: list[str]


@dataclass
class EvalSet:
    documents: list[Document]
    cases: list[EvalCase]


def load_evalset(path: Path) -> EvalSet:
    data = json.loads(path.read_text(encoding="utf-8"))
    docs = [Document(id=d["id"], text=d["text"]) for d in data["documents"]]
    cases = [
        EvalCase(id=c["id"], query=c["query"], relevant_ids=list(c["relevant_ids"]))
        for c in data["cases"]
    ]
    return EvalSet(documents=docs, cases=cases)
