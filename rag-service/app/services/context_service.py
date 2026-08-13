def build_context(chunks: list[dict]) -> str:
    """
    Build grounded context from retrieved chunks.
    """

    if not chunks:
        return ""

    context_parts = []

    for index, chunk in enumerate(chunks, start=1):

        metadata = chunk.get("metadata", {})

        document_id = metadata.get(
            "document_id",
            "unknown"
        )

        page_number = metadata.get(
            "page_number",
            "unknown"
        )

        chunk_index = metadata.get(
            "chunk_index",
            "unknown"
        )

        text = chunk.get("text", "").strip()

        context_parts.append(
            f"SOURCE {index}\n"
            f"Document ID: {document_id}\n"
            f"Page: {page_number}\n"
            f"Chunk: {chunk_index}\n"
            f"Content:\n{text}"
        )

    return "\n\n---\n\n".join(context_parts)