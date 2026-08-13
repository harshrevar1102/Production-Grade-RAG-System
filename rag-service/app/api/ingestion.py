import os
import tempfile
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.pdf_service import extract_text_from_pdf
from app.services.chunking_service import create_chunks
from app.services.embedding_service import generate_embeddings
from app.services.vector_service import store_chunks
from app.services.bm25_service import save_index

router = APIRouter(
    prefix="/api/ingestion",
    tags=["Ingestion"]
)


@router.post("/process")
async def process_document(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is required."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are currently supported."
        )

    temp_path = None

    try:
        file_bytes = await file.read()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_file.write(file_bytes)
            temp_path = temp_file.name

        # ==========================================
        # 1. EXTRACT TEXT
        # ==========================================

        pages = extract_text_from_pdf(temp_path)

        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in PDF."
            )

        # ==========================================
        # 2. CREATE CHUNKS
        # ==========================================

        
        
        save_index(
            document_id=document_id,
            chunks=chunks
        )

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No chunks were created from document."
            )

        # ==========================================
        # 3. GENERATE DOCUMENT ID
        # ==========================================

        document_id = str(uuid.uuid4())

        # ==========================================
        # 4. GENERATE EMBEDDINGS
        # ==========================================

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = generate_embeddings(texts)

        # ==========================================
        # 5. STORE IN VECTOR DATABASE
        # ==========================================

        vector_result = store_chunks(
            document_id=document_id,
            chunks=chunks,
            embeddings=embeddings
        )

        return {
            "success": True,
            "document_id": document_id,
            "filename": file.filename,
            "total_pages": len(pages),
            "total_chunks": len(chunks),
            "embedding_dimensions": len(embeddings[0]),
            "vector_database": "ChromaDB",
            "collection": vector_result["collection"],
            "stored_chunks": vector_result["stored_chunks"]
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(error)}"
        )

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)