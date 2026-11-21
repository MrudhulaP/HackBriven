from typing import Optional, Dict, Any, List
from decimal import Decimal
from sqlalchemy.orm import Session

from app.ai.language_detector import IndicLanguageDetector
from app.ai.intent_classifier import IntentClassifier
from app.ai.entity_extractor import EntityExtractor
from app.ai.transaction_parser import TransactionParser
from app.ai.response_generator import ResponseGenerator
from app.ai.speech_to_text import SpeechToTextService
from app.ai.text_to_speech import TextToSpeechService
from app.schemas.voice import VoiceInterpretResponse

class AIProvider:
    """Unified provider-independent AI layer for BolKhata."""

    @classmethod
    async def process_speech_audio(
        cls,
        audio_bytes: bytes,
        language: Optional[str] = None,
        db: Optional[Session] = None,
        shop_id: Optional[str] = None
    ) -> VoiceInterpretResponse:
        stt_result = await SpeechToTextService.transcribe_audio(audio_bytes, language=language)
        transcript = stt_result.get("transcript", "")
        return cls.interpret_text(transcript, db=db, shop_id=shop_id, language=language)

    @classmethod
    def interpret_text(
        cls,
        text: str,
        db: Optional[Session] = None,
        shop_id: Optional[str] = None,
        language: Optional[str] = None
    ) -> VoiceInterpretResponse:
        return TransactionParser.parse(text, db=db, shop_id=shop_id, language=language)

    @classmethod
    def format_confirmation_response(
        cls,
        customer_name: str,
        new_balance: Decimal,
        events: List[Dict[str, Any]],
        language: str = "hi"
    ) -> Dict[str, str]:
        return ResponseGenerator.generate_transaction_confirmation_response(
            customer_name=customer_name,
            new_balance=new_balance,
            events_summary=events,
            language=language
        )
