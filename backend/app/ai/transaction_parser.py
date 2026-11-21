import re
import uuid
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from app.ai.language_detector import IndicLanguageDetector
from app.ai.intent_classifier import IntentClassifier
from app.ai.entity_extractor import EntityExtractor
from app.models.customer import Customer
from app.schemas.voice import ParsedEvent, VoiceInterpretResponse

class TransactionParser:
    CLAUSE_DELIMITERS = [
        r',', r';', r'\baur\b', r'\band\b', r'\bmattu\b', r'\blekin\b', r'\bbut\b'
    ]

    @classmethod
    def split_into_clauses(cls, text: str) -> List[str]:
        """
        Split a compound or multi-intent statement into sub-clauses.
        E.g. 'Ramesh ka 340 udhaar, kal 200 diya tha' ->
        ['Ramesh ka 340 udhaar', 'kal 200 diya tha']
        """
        # Split on comma, semicolon, 'aur', 'and', 'mattu'
        pattern = r'[,;]|\b(?:aur|and|mattu)\b'
        raw_clauses = re.split(pattern, text, flags=re.IGNORECASE)
        clauses = [c.strip() for c in raw_clauses if c and c.strip()]
        return clauses if clauses else [text.strip()]

    @classmethod
    def parse(
        cls,
        text: str,
        db: Optional[Session] = None,
        shop_id: Optional[str] = None,
        language: Optional[str] = None
    ) -> VoiceInterpretResponse:
        """
        Full NLU parsing pipeline:
        1. Detect language.
        2. Check for multi-event clauses (e.g. Credit + Payment in one breath).
        3. Extract entities (customer, amount, date) for each event.
        4. Match customer against shop database.
        5. Flag ambiguities (missing amount, ambiguous credit/payment, multiple customer matches).
        6. Return structured VoiceInterpretResponse.
        """
        detected_lang = language or IndicLanguageDetector.detect(text)
        clauses = cls.split_into_clauses(text)

        # Get known customers from DB if available
        known_customers_map: Dict[str, Customer] = {}
        known_names: List[str] = []
        if db and shop_id:
            db_customers = db.query(Customer).filter(
                Customer.shop_id == shop_id,
                Customer.archived_at == None
            ).all()
            for c in db_customers:
                known_customers_map[c.name.lower()] = c
                known_names.append(c.name)

        events: List[ParsedEvent] = []
        active_customer_name: Optional[str] = None
        active_customer_id: Optional[str] = None
        primary_intent = IntentClassifier.INTENT_UNKNOWN

        for i, clause in enumerate(clauses):
            intent, confidence = IntentClassifier.classify(clause)
            if i == 0:
                primary_intent = intent

            amount = EntityExtractor.extract_amount(clause)
            tx_date, date_label = EntityExtractor.extract_date(clause)

            # Customer extraction
            cust_name = EntityExtractor.extract_customer_name(clause, known_names)
            if cust_name:
                active_customer_name = cust_name
            else:
                # Inherit from preceding clause if missing (e.g. second clause "kal 200 diya tha")
                cust_name = active_customer_name

            # Match customer in DB
            matched_customers = []
            cust_id = None
            if cust_name and db and shop_id:
                matches = db.query(Customer).filter(
                    Customer.shop_id == shop_id,
                    Customer.archived_at == None,
                    Customer.name.ilike(f"%{cust_name}%")
                ).all()
                matched_customers = [{"id": m.id, "name": m.name, "mobile": m.mobile} for m in matches]
                if len(matches) == 1:
                    cust_id = matches[0].id
                    active_customer_id = cust_id
                elif active_customer_id and not matches:
                    cust_id = active_customer_id

            # Check Ambiguity
            is_ambiguous = False
            clarification_q = None
            missing_fields = []

            if intent in (IntentClassifier.INTENT_ADD_CREDIT, IntentClassifier.INTENT_RECORD_PAYMENT):
                if amount is None:
                    is_ambiguous = True
                    missing_fields.append("amount")
                    action_word = "pay" if intent == IntentClassifier.INTENT_RECORD_PAYMENT else "take as credit"
                    name_display = cust_name or "the customer"
                    clarification_q = f"How much did {name_display} {action_word}?"
            elif intent == IntentClassifier.INTENT_AMBIGUOUS_TRANSACTION:
                is_ambiguous = True
                name_display = cust_name or "the customer"
                amt_str = f"₹{amount}" if amount else "the amount"
                clarification_q = f"Is {amt_str} credit given to {name_display} or a payment received from {name_display}?"
            elif intent == IntentClassifier.INTENT_CHECK_BALANCE:
                if not cust_name:
                    is_ambiguous = True
                    missing_fields.append("customer_name")
                    clarification_q = "Whose balance would you like to check?"

            # Multiple customer name matches ambiguity
            if len(matched_customers) > 1 and not is_ambiguous:
                is_ambiguous = True
                names_str = ", ".join(m["name"] for m in matched_customers)
                clarification_q = f"I found {len(matched_customers)} customers matching '{cust_name}': {names_str}. Which one do you mean?"

            # Map intent to transaction type
            tx_type = "CREDIT" if intent == IntentClassifier.INTENT_ADD_CREDIT else (
                "PAYMENT" if intent == IntentClassifier.INTENT_RECORD_PAYMENT else "UNKNOWN"
            )

            event = ParsedEvent(
                event_id=str(uuid.uuid4()),
                intent=intent,
                customer_id=cust_id,
                customer_name=cust_name,
                matched_customers=matched_customers,
                amount=amount,
                currency="INR",
                transaction_date=tx_date,
                date_label=date_label,
                description=f"{tx_type} of ₹{amount} on {date_label}" if amount else None,
                confidence=confidence,
                is_ambiguous=is_ambiguous,
                clarification_question=clarification_q,
                missing_fields=missing_fields
            )
            events.append(event)

        # Global clarification check
        any_clarification = any(e.is_ambiguous for e in events)
        first_clarification = next((e.clarification_question for e in events if e.is_ambiguous and e.clarification_question), None)
        can_execute = not any_clarification and all(
            e.intent in (IntentClassifier.INTENT_ADD_CREDIT, IntentClassifier.INTENT_RECORD_PAYMENT) and e.amount and e.customer_name
            for e in events
        )

        return VoiceInterpretResponse(
            raw_transcript=text,
            detected_language=detected_lang,
            primary_intent=primary_intent,
            events=events,
            requires_clarification=any_clarification,
            clarification_prompt=first_clarification,
            spoken_clarification=first_clarification,
            can_execute_directly=can_execute
        )
