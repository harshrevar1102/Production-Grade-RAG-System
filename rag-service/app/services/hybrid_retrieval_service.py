from app.services.retrieval_service import retrieve_chunks
from app.services.bm25_service import search_bm25
from app.services.reranker_service import rerank


def reciprocal_rank_fusion(
    semantic_results: list[dict],
    bm25_results: list[dict],
    k: int = 60
) -> list[dict]:
    """
    Combine semantic and BM25 rankings using
    Reciprocal Rank Fusion (RRF).
    """

    fused = {}

    # Semantic ranking
    for rank, result in enumerate(semantic_results, start=1):

        chunk_id = result["chunk_id"]

        if chunk_id not in fused:
            fused[chunk_id] = {
                "chunk_id": chunk_id,
                "text": result["text"],
                "metadata": result["metadata"],
                "rrf_score": 0.0
            }

        fused[chunk_id]["rrf_score"] += 1 / (k + rank)

    # BM25 ranking
    for rank, result in enumerate(bm25_results, start=1):

        chunk = result["chunk"]
        chunk_id = (
            f"{chunk['metadata']['document_id']}_chunk_"
            f"{chunk['chunk_index']}"
        )

        if chunk_id not in fused:
            fused[chunk_id] = {
                "chunk_id": chunk_id,
                "text": chunk["text"],
                "metadata": chunk["metadata"],
                "rrf_score": 0.0
            }

        fused[chunk_id]["rrf_score"] += 1 / (k + rank)

    return sorted(
        fused.values(),
        key=lambda x: x["rrf_score"],
        reverse=True
    )


def hybrid_retrieve(
    document_id: str,
    query: str,
    top_k: int = 5,
    candidate_k: int = 20
) -> list[dict]:

    # ==========================================
    # 1. SEMANTIC SEARCH
    # ==========================================

    semantic_results = retrieve_chunks(
        document_id=document_id,
        query=query,
        top_k=candidate_k
    )

    # ==========================================
    # 2. BM25 SEARCH
    # ==========================================

    bm25_results = search_bm25(
        document_id=document_id,
        query=query,
        top_k=candidate_k
    )

    # ==========================================
    # 3. RRF FUSION
    # ==========================================

    fused_results = reciprocal_rank_fusion(
        semantic_results,
        bm25_results
    )

    # ==========================================
    # 4. CROSS-ENCODER RERANKING
    # ==========================================

    reranked = rerank(
        query=query,
        chunks=fused_results[:candidate_k],
        top_k=top_k
    )

    return reranked