from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.hybrid_retrieval_service import hybrid_retrieve


router = APIRouter(
    prefix="/api/retrieval",
    tags=["Retrieval"]
)


class RetrievalRequest(BaseModel):
    document_id: str
    query: str
    top_k: int = 5


@router.post("/search")
def search_document(request: RetrievalRequest):

    try:

        results = hybrid_retrieve(
            document_id=request.document_id,
            query=request.query,
            top_k=request.top_k,
            candidate_k=20
        )

        return {
            "success": True,
            "query": request.query,
            "results": results
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Retrieval failed: {str(error)}"
        )