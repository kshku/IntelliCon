from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.auth import get_current_user
from app.models.user import User
from app.tools.pdf_export import PDF_OUTPUT_DIR

router = APIRouter(prefix="/api/pdf", tags=["pdf"])


@router.get("/{filename}")
async def download_pdf(
    filename: str,
    _user: User = Depends(get_current_user),
):
    safe_name = os.path.basename(filename)
    if safe_name != filename or not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid filename")

    pdf_path = os.path.join(PDF_OUTPUT_DIR, safe_name)

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found or expired")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
    )
