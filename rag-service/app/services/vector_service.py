import chromadb


CHROMA_PATH = "./chroma_db"

_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


def get_collection(document_id: str):
    """
    Get or create a dedicated collection for a document.
    """

    collection_name = f"document_{document_id}"

    return _client.get_or_create_collection(
        name=collection_name,
        metadata={
            "hnsw:space": "cosine"
        }
    )


def store_chunks(
    document_id: str,
    chunks: list[dict],
    embeddings: list[list[float]]
):
    """
    Store document chunks and their embeddings in ChromaDB.
    """

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks and embeddings must match."
        )

    collection = get_collection(document_id)

    ids = [
        f"{document_id}_chunk_{chunk['chunk_index']}"
        for chunk in chunks
    ]

    documents = [
        chunk["text"]
        for chunk in chunks
    ]

    metadatas = [
        {
            "document_id": document_id,
            "chunk_index": chunk["chunk_index"],
            "page_number": chunk["page_number"]
        }
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return {
        "collection": collection.name,
        "stored_chunks": len(chunks)
    }