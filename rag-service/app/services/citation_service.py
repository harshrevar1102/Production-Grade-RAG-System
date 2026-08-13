def build_sources(chunks: list[dict]) -> list[dict]:

    sources = []
    seen = set()

    for chunk in chunks:

        metadata = chunk.get("metadata", {})

        document_id = metadata.get("document_id")
        page_number = metadata.get("page_number")
        chunk_index = metadata.get("chunk_index")

        key = (
            document_id,
            page_number,
            chunk_index
        )

        if key in seen:
            continue

        seen.add(key)

        sources.append({
            "document_id": document_id,
            "page_number": page_number,
            "chunk_index": chunk_index,
            "chunk_id": chunk.get("chunk_id"),
            "rerank_score": chunk.get("rerank_score")
        })

    return sources