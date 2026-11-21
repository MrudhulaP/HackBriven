from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal

class ParsedEvent(BaseModel):
    event_id: str
    intent: str  # ADD_CREDIT, RECORD_PAYMENT, CHECK_BALANCE, etc.
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    matched_customers: List[Dict[str, Any]] = []
    amount: Optional[Decimal] = None
    currency: str = "INR"
    transaction_date: date = Field(default_factory=date.today)
    date_label: str = "Today"  # "Today", "Yesterday", or formatted date
    description: Optional[str] = None
    confidence: float = 0.95
    is_ambiguous: bool = False
    clarification_question: Optional[str] = None
    missing_fields: List[str] = []

class VoiceInterpretRequest(BaseModel):
    text: str
    language: Optional[str] = None  # 'hi', 'kn', 'en' or None (auto-detect)
    input_source: str = "VOICE"     # "VOICE" or "TEXT"

class VoiceInterpretResponse(BaseModel):
    raw_transcript: str
    detected_language: str
    primary_intent: str
    events: List[ParsedEvent]
    requires_clarification: bool = False
    clarification_prompt: Optional[str] = None
    spoken_clarification: Optional[str] = None
    spoken_summary: Optional[str] = None
    can_execute_directly: bool = False

class VoiceConfirmItem(BaseModel):
    customer_id: str
    customer_name: str
    type: str  # CREDIT or PAYMENT
    amount: Decimal
    transaction_date: date
    description: Optional[str] = None

class VoiceConfirmRequest(BaseModel):
    items: List[VoiceConfirmItem]
    language: str = "hi"

class VoiceConfirmResponse(BaseModel):
    success: bool
    created_transactions: List[Dict[str, Any]]
    customer_id: str
    customer_name: str
    new_outstanding_balance: Decimal
    formatted_balance: str
    spoken_response: str
    text_response: str

class VoiceSpeakRequest(BaseModel):
    text: str
    language: str = "hi"

class AssistantQueryRequest(BaseModel):
    query: str
    language: Optional[str] = "hi"

class AssistantQueryResponse(BaseModel):
    query: str
    answer: str
    spoken_answer: str
    data: Optional[Dict[str, Any]] = None
