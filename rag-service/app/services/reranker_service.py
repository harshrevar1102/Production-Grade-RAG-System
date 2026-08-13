from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_model = None


def get_reranker():

    global _model

    if _model is None:
        _model = CrossEncoder(MODEL_NAME)

    return _model


def rerank(
    query: str,
    chunks: list[dict],
    top_k: int = 5
) -> list[dict]:

    if not chunks:
        return []

    model = get_reranker()

    pairs = [
        [query, chunk["text"]]
        for chunk in chunks
    ]

    scores = model.predict(pairs)

    ranked = sorted(
        zip(chunks, scores),
        key=lambda item: float(item[1]),
        reverse=True
    )

    results = []

    for chunk, score in ranked[:top_k]:

        results.append({
            **chunk,
            "rerank_score": float(score)
        })

    return results