import json
from pathlib import Path

from rank_bm25 import BM25Okapi


BM25_PATH = Path("./bm25_indexes")
BM25_PATH.mkdir(exist_ok=True)


def tokenize(text: str) -> list[str]:
    return text.lower().split()


def save_index(document_id: str, chunks: list[dict]):
    path = BM25_PATH / f"{document_id}.json"

    data = {
        "chunks": chunks
    }

    path.write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8"
    )


def load_chunks(document_id: str) -> list[dict]:
    path = BM25_PATH / f"{document_id}.json"

    if not path.exists():
        return []

    data = json.loads(
        path.read_text(encoding="utf-8")
    )

    return data["chunks"]


def search_bm25(
    document_id: str,
    query: str,
    top_k: int = 20
) -> list[dict]:

    chunks = load_chunks(document_id)

    if not chunks:
        return []

    corpus = [
        tokenize(chunk["text"])
        for chunk in chunks
    ]

    bm25 = BM25Okapi(corpus)

    scores = bm25.get_scores(
        tokenize(query)
    )

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:top_k]

    return [
        {
            "chunk": chunks[index],
            "score": float(scores[index])
        }
        for index in ranked_indices
    ]