from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.tools.pdf_export import PDF_OUTPUT_DIR

router = APIRouter(prefix="/api/pdf", tags=["pdf"])


@router.get("/{filename}")
async def download_pdf(filename: str):
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    pdf_path = os.path.join(PDF_OUTPUT_DIR, filename)

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found or expired")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
    )
