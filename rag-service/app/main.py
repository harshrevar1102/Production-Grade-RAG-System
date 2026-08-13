from fastapi import FastAPI

from app.api.ingestion import router as ingestion_router
from app.api.retrieval import router as retrieval_router
from app.api.rag import router as rag_router


app = FastAPI(
    title="Production-Grade-RAG-System RAG Service",
    version="1.0.0"
)


app.include_router(ingestion_router)
app.include_router(retrieval_router)
app.include_router(rag_router)


@app.get("/")
def health_check():

    return {
        "status": "healthy",
        "service": "rag-service"
    }