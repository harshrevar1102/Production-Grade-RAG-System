from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.retrieval_service import retrieve_chunks


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

        chunks = retrieve_chunks(
            document_id=request.document_id,
            query=request.query,
            top_k=request.top_k
        )

        return {
            "success": True,
            "query": request.query,
            "results": chunks
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Retrieval failed: {str(error)}"
        )