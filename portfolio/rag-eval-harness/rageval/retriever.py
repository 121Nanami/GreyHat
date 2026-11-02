"""Simple TF-IDF cosine retriever for offline RAG eval demos."""

from __future__ import annotations

from dataclasses import dataclass

from .tokenize import build_idf, cosine, tfidf_vec, tokenize


@dataclass
class Document:
    id: str
    text: str


class TfidfRetriever:
    def __init__(self, documents: list[Document]) -> None:
        self.documents = documents
        self._toks = [tokenize(d.text) for d in documents]
        self._idf = build_idf(self._toks)
        self._vecs = [tfidf_vec(t, self._idf) for t in self._toks]

    def search(self, query: str, k: int = 5) -> list[tuple[str, float]]:
        qv = tfidf_vec(tokenize(query), self._idf)
        scored = [
            (doc.id, cosine(qv, vec))
            for doc, vec in zip(self.documents, self._vecs)
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]
