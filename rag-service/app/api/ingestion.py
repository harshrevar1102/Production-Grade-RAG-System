import os
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.pdf_service import extract_text_from_pdf
from app.services.chunking_service import create_chunks


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

        pages = extract_text_from_pdf(temp_path)

        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in PDF."
            )

        chunks = create_chunks(pages)

        return {
            "success": True,
            "filename": file.filename,
            "total_pages": len(pages),
            "total_chunks": len(chunks),
            "chunks": chunks
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