from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.hybrid_retrieval_service import hybrid_retrieve
from app.services.context_service import build_context
from app.services.llm_service import generate_answer
from app.services.citation_service import build_sources


router = APIRouter(
    prefix="/api/rag",
    tags=["RAG"]
)


class RAGRequest(BaseModel):
    document_id: str
    query: str
    top_k: int = 5


@router.post("/ask")
def ask_document(request: RAGRequest):

    try:

        # ==========================================
        # 1. RETRIEVAL
        # ==========================================

        retrieved_chunks = hybrid_retrieve(
            document_id=request.document_id,
            query=request.query,
            top_k=request.top_k,
            candidate_k=20
        )

        # ==========================================
        # 2. HANDLE NO RESULTS
        # ==========================================

        if not retrieved_chunks:
            return {
                "success": True,
                "query": request.query,
                "answer": (
                    "I don't have enough information "
                    "in the provided documents."
                ),
                "sources": []
            }

        # ==========================================
        # 3. CONTEXT CONSTRUCTION
        # ==========================================

        context = build_context(
            retrieved_chunks
        )

        # ==========================================
        # 4. LLM GENERATION
        # ==========================================

        answer = generate_answer(
            query=request.query,
            context=context
        )

        # ==========================================
        # 5. BUILD DETERMINISTIC SOURCES
        # ==========================================

        sources = build_sources(
            retrieved_chunks
        )

        # ==========================================
        # 6. FINAL RESPONSE
        # ==========================================

        return {
            "success": True,
            "query": request.query,
            "answer": answer,
            "sources": sources
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"RAG generation failed: {str(error)}"
        )