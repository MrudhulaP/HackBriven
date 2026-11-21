from typing import Optional, List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import Shop, User
from app.models.customer import Customer
from app.schemas.voice import (
    VoiceInterpretRequest, VoiceInterpretResponse, VoiceConfirmRequest, VoiceConfirmResponse, VoiceSpeakRequest
)
from app.ai.ai_provider import AIProvider
from app.ai.speech_to_text import SpeechToTextService
from app.ai.text_to_speech import TextToSpeechService
from app.services.ledger_service import LedgerService, quantize_inr
from app.api.deps import get_current_shop, get_current_user

router = APIRouter(prefix="/voice", tags=["Voice AI"])

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    shop: Shop = Depends(get_current_shop)
):
    audio_bytes = await file.read()
    result = await SpeechToTextService.transcribe_audio(
        audio_data=audio_bytes,
        language=language,
        content_type=file.content_type or "audio/webm"
    )
    return result

@router.post("/interpret", response_model=VoiceInterpretResponse)
def interpret_transcript(
    data: VoiceInterpretRequest,
    shop: Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    return AIProvider.interpret_text(
        text=data.text,
        db=db,
        shop_id=shop.id,
        language=data.language
    )

@router.post("/confirm", response_model=VoiceConfirmResponse)
def confirm_voice_transactions(
    data: VoiceConfirmRequest,
    shop: Shop = Depends(get_current_shop),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not data.items:
        raise HTTPException(status_code=400, detail="No transaction items provided for confirmation")

    created_txs = []
    events_summary = []
    customer_id = data.items[0].customer_id
    customer_name = data.items[0].customer_name

    # Atomic write of all confirmed events
    for item in data.items:
        tx = LedgerService.create_transaction(
            db=db,
            shop_id=shop.id,
            customer_id=item.customer_id,
            type=item.type,
            amount=item.amount,
            transaction_date=item.transaction_date,
            description=item.description or f"Voice ledger: {item.type} of ₹{item.amount}",
            input_method="VOICE",
            user_id=user.id
        )
        created_txs.append({
            "id": tx.id,
            "type": tx.type,
            "amount": str(tx.amount),
            "date": tx.transaction_date.isoformat(),
            "customer_id": tx.customer_id
        })
        events_summary.append({
            "type": item.type,
            "amount": str(item.amount),
            "date_label": "Yesterday" if (tx.transaction_date < tx.created_at.date()) else "Today"
        })

    # Exact live balance calculation from DB
    new_balance, _, _ = LedgerService.get_customer_balance(db, shop.id, customer_id)
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if cust:
        customer_name = cust.name

    # Generate spoken and text response
    resp = AIProvider.format_confirmation_response(
        customer_name=customer_name,
        new_balance=new_balance,
        events=events_summary,
        language=data.language
    )

    return VoiceConfirmResponse(
        success=True,
        created_transactions=created_txs,
        customer_id=customer_id,
        customer_name=customer_name,
        new_outstanding_balance=new_balance,
        formatted_balance=f"₹{new_balance}",
        spoken_response=resp["spoken"],
        text_response=resp["text"]
    )

@router.post("/speak")
async def speak_text(data: VoiceSpeakRequest):
    return await TextToSpeechService.synthesize_speech(text=data.text, language=data.language)
