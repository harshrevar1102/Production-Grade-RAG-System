from app.services.embedding_service import generate_embeddings
from app.services.vector_service import get_collection


def retrieve_chunks(
    document_id: str,
    query: str,
    top_k: int = 5
) -> list[dict]:
    """
    Retrieve the most semantically relevant chunks
    for a query from ChromaDB.
    """

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    collection = get_collection(document_id)

    query_embedding = generate_embeddings([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    retrieved_chunks = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    for index in range(len(documents)):

        retrieved_chunks.append({
            "chunk_id": ids[index],
            "text": documents[index],
            "metadata": metadatas[index],
            "distance": distances[index]
        })

    return retrieved_chunks