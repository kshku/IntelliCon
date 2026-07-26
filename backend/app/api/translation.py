from deep_translator import GoogleTranslator
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import get_current_user
from app.models.user import User

router = APIRouter()


class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "kn"  # Kannada default
    target_lang: str = "en"  # English default


class TranslationResponse(BaseModel):
    translated_text: str
    source_lang: str
    target_lang: str


@router.post("/translate", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    _user: User = Depends(get_current_user),
):
    """Translate text between Kannada and English for LLM processing."""
    try:
        translator = GoogleTranslator(
            source=request.source_lang,
            target=request.target_lang,
        )
        translated = translator.translate(request.text)
        return TranslationResponse(
            translated_text=translated,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Translation service unavailable: {type(exc).__name__}",
        )


@router.post("/translate/batch", response_model=list[TranslationResponse])
async def translate_batch(
    requests: list[TranslationRequest],
    _user: User = Depends(get_current_user),
):
    """Translate multiple texts in batch."""
    results = []
    for req in requests:
        try:
            translator = GoogleTranslator(
                source=req.source_lang,
                target=req.target_lang,
            )
            translated = translator.translate(req.text)
            results.append(
                TranslationResponse(
                    translated_text=translated,
                    source_lang=req.source_lang,
                    target_lang=req.target_lang,
                )
            )
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Translation service unavailable: {type(exc).__name__}",
            )
    return results
