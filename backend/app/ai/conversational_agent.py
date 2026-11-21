import uuid
from decimal import Decimal
from datetime import date
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.ai.language_detector import IndicLanguageDetector
from app.ai.intent_classifier import IntentClassifier
from app.ai.entity_extractor import EntityExtractor
from app.ai.transaction_parser import TransactionParser
from app.ai.response_generator import ResponseGenerator
from app.services.ledger_service import LedgerService, quantize_inr
from app.services.report_service import ReportService
from app.models.customer import Customer

class ConversationalAgent:
    """
    Maintains one-to-one ongoing conversation loop across turns for Indian Kirana retailers.
    Handles auto-language detection, context memory, clarifier follow-ups, and voice triggers.
    """
    _sessions: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_or_create_session(cls, session_id: str) -> Dict[str, Any]:
        if session_id not in cls._sessions:
            cls._sessions[session_id] = {
                "awaiting": None,  # "TYPE", "AMOUNT", "CUSTOMER", "CONFIRM"
                "pending_customer_name": None,
                "pending_customer_id": None,
                "pending_amount": None,
                "pending_date": None,
                "pending_intent": None,
                "language": "hi",
                "history": []
            }
        return cls._sessions[session_id]

    @classmethod
    def reset_session(cls, session_id: str):
        if session_id in cls._sessions:
            cls._sessions[session_id]["awaiting"] = None
            cls._sessions[session_id]["pending_customer_name"] = None
            cls._sessions[session_id]["pending_customer_id"] = None
            cls._sessions[session_id]["pending_amount"] = None
            cls._sessions[session_id]["pending_date"] = None
            cls._sessions[session_id]["pending_intent"] = None

    @classmethod
    def process_turn(
        cls,
        session_id: str,
        user_text: str,
        shop_id: str,
        db: Session,
        explicit_language: Optional[str] = None
    ) -> Dict[str, Any]:
        session = cls.get_or_create_session(session_id)
        raw_text = user_text.strip()

        # 1. Automatic Language Detection on each turn (Voice-First Adaptability)
        detected_lang = explicit_language or IndicLanguageDetector.detect(raw_text)
        session["language"] = detected_lang

        clean_text = IntentClassifier.clean_fillers(raw_text)
        clean_low = clean_text.lower()

        # Check for cancellation
        if any(w in clean_low for w in ["cancel", "radd", "chhod do", "vaddu", "vendaam", "stop"]):
            cls.reset_session(session_id)
            cancel_msgs = {
                "hi": "Theek hai, radd kar diya. Aur kya hisaab likhna hai?",
                "kn": "Sari, raddumaadalaagide. Bere yavudannu baredkolli?",
                "te": "Sare, raddu chesamu. Inkemaina sahayam kavala?",
                "ta": "Sari, rathu seithu vittom. Vera enna ezhutha vendum?",
                "en": "Cancelled. What else would you like to record?"
            }
            msg = cancel_msgs.get(detected_lang, cancel_msgs["hi"])
            return {
                "action": "CANCELLED",
                "text_response": msg,
                "spoken_response": msg,
                "language": detected_lang,
                "events": [],
                "requires_clarification": False
            }

        # 2. Check if we are waiting for a follow-up answer (One-to-One Clarification Loop)
        if session.get("awaiting") == "TYPE":
            # User is replying whether it's Credit or Payment
            is_credit = any(w in clean_low for w in [
                "udhaar", "udhar", "credit", "saala", "appu", "kadan", "dena hai", "liya"
            ])
            is_payment = any(w in clean_low for w in [
                "jama", "payment", "diya", "paid", "ichadu", "ichanu", "koduthen", "bandide", "vachindi"
            ])

            if is_credit or is_payment:
                cust_name = session["pending_customer_name"]
                cust_id = session["pending_customer_id"]
                amount = session["pending_amount"]
                tx_date = session["pending_date"] or date.today()
                tx_type = "CREDIT" if is_credit else "PAYMENT"
                intent = "ADD_CREDIT" if is_credit else "RECORD_PAYMENT"

                cls.reset_session(session_id)

                event = {
                    "event_id": str(uuid.uuid4()),
                    "intent": intent,
                    "customer_id": cust_id,
                    "customer_name": cust_name,
                    "matched_customers": [],
                    "amount": float(amount),
                    "currency": "INR",
                    "transaction_date": tx_date.isoformat(),
                    "date_label": "Today",
                    "description": f"{tx_type} of ₹{amount}",
                    "confidence": 0.98,
                    "is_ambiguous": False,
                    "clarification_question": None,
                    "missing_fields": []
                }

                confirm_prompts = {
                    "hi": f"{cust_name} ka ₹{amount} {'udhaar' if is_credit else 'jama'} samajh aaya. Kya darj karein?",
                    "kn": f"{cust_name} avara ₹{amount} {'saala' if is_credit else 'payment'}. Khatege serisala?",
                    "te": f"{cust_name} gari ₹{amount} {'appu' if is_credit else 'payment'}. Khathaalo rayala?",
                    "ta": f"{cust_name} avargalukku ₹{amount} {'kadan' if is_credit else 'varavu'}. Kanakkil serkkava?",
                    "en": f"Understood: ₹{amount} {'credit' if is_credit else 'payment'} for {cust_name}. Confirm to save?"
                }
                spoken = confirm_prompts.get(detected_lang, confirm_prompts["hi"])

                return {
                    "session_id": session_id,
                    "primary_intent": intent,
                    "action": "SHOW_CONFIRMATION",
                    "text_response": spoken,
                    "spoken_response": spoken,
                    "language": detected_lang,
                    "events": [event],
                    "requires_clarification": False
                }

        elif session.get("awaiting") == "AMOUNT":
            amt = EntityExtractor.extract_amount(raw_text)
            if amt:
                cust_name = session["pending_customer_name"]
                cust_id = session["pending_customer_id"]
                intent = session.get("pending_intent") or "ADD_CREDIT"
                tx_type = "CREDIT" if intent == "ADD_CREDIT" else "PAYMENT"

                cls.reset_session(session_id)

                event = {
                    "event_id": str(uuid.uuid4()),
                    "intent": intent,
                    "customer_id": cust_id,
                    "customer_name": cust_name,
                    "matched_customers": [],
                    "amount": float(amt),
                    "currency": "INR",
                    "transaction_date": date.today().isoformat(),
                    "date_label": "Today",
                    "description": f"{tx_type} of ₹{amt}",
                    "confidence": 0.98,
                    "is_ambiguous": False,
                    "clarification_question": None,
                    "missing_fields": []
                }

                confirm_prompts = {
                    "hi": f"Theek hai, {cust_name} ka ₹{amt} {'udhaar' if tx_type == 'CREDIT' else 'jama'}. Kya confirm karein?",
                    "kn": f"Sari, {cust_name} avara ₹{amt} {'saala' if tx_type == 'CREDIT' else 'payment'}. Confirm maadala?",
                    "te": f"Sare, {cust_name} gari ₹{amt} {'appu' if tx_type == 'CREDIT' else 'payment'}. Confirm cheyala?",
                    "ta": f"Sari, {cust_name} avargalukku ₹{amt} {'kadan' if tx_type == 'CREDIT' else 'varavu'}. Confirm seiyalaama?",
                    "en": f"Got it: ₹{amt} {'credit' if tx_type == 'CREDIT' else 'payment'} for {cust_name}. Confirm?"
                }
                spoken = confirm_prompts.get(detected_lang, confirm_prompts["hi"])

                return {
                    "session_id": session_id,
                    "primary_intent": intent,
                    "action": "SHOW_CONFIRMATION",
                    "text_response": spoken,
                    "spoken_response": spoken,
                    "language": detected_lang,
                    "events": [event],
                    "requires_clarification": False
                }

        # 3. Check Voice-Activated Receipt / Bill Scanning Trigger
        classified_intent, conf = IntentClassifier.classify(raw_text)
        if classified_intent == IntentClassifier.INTENT_SCAN_RECEIPT:
            scan_prompts = {
                "hi": "Theek hai, parcha scan karne ke liye camera khol raha hoon. Bill saaf dikhayiye.",
                "kn": "Sari, bill scan maadalu camera theriyuttiddene. Bill annu spastavagi thorisi.",
                "te": "Sare, billu scan cheyadaniki camera open chestunnanu. Bill spashtamga chupinchandi.",
                "ta": "Sari, receipt scan seiya camera thirakkiren. Bill-ai thelivaga kaattavum.",
                "en": "Opening camera to scan your receipt. Please show the paper bill clearly."
            }
            resp_txt = scan_prompts.get(detected_lang, scan_prompts["hi"])
            return {
                "session_id": session_id,
                "primary_intent": IntentClassifier.INTENT_SCAN_RECEIPT,
                "action": "TRIGGER_CAMERA_SCAN",
                "text_response": resp_txt,
                "spoken_response": resp_txt,
                "language": detected_lang,
                "events": [],
                "requires_clarification": False
            }

        # 4. Check Business Reports Triggers
        # A) Weekly Business Report: "How much money did I make this week?"
        if classified_intent == IntentClassifier.INTENT_WEEKLY_REPORT:
            weekly = ReportService.get_weekly_report(db, shop_id)
            resp = ResponseGenerator.generate_weekly_summary_response(
                total_payment=weekly["total_payment"],
                total_credit=weekly["total_credit"],
                tx_count=weekly["transaction_count"],
                language=detected_lang
            )
            return {
                "session_id": session_id,
                "primary_intent": IntentClassifier.INTENT_WEEKLY_REPORT,
                "action": "SHOW_REPORT",
                "text_response": resp["text"],
                "spoken_response": resp["spoken"],
                "language": detected_lang,
                "report_data": weekly,
                "events": [],
                "requires_clarification": False
            }

        # B) Top Debtors: "Who owes me the most money?"
        if classified_intent == IntentClassifier.INTENT_TOP_DEBTORS:
            customers = db.query(Customer).filter(
                Customer.shop_id == shop_id,
                Customer.archived_at == None
            ).all()
            debtors = []
            for c in customers:
                bal, _, _ = LedgerService.get_customer_balance(db, shop_id, c.id)
                if bal > Decimal("0"):
                    debtors.append((c.name, bal))
            debtors.sort(key=lambda x: x[1], reverse=True)

            if debtors:
                top_name, top_bal = debtors[0]
                resp = ResponseGenerator.generate_top_debtor_response(top_name, top_bal, language=detected_lang)
            else:
                empty_msgs = {
                    "hi": "Aapki dukaan mein kisi grahak ka koi udhaar baaki nahi hai.",
                    "kn": "Nimma dukaanadalli yavude grahakara baaki illa.",
                    "te": "Mee dukaanamlo evariki baaki ledu.",
                    "ta": "Ungal kadaiyil yaarukkum baki illai.",
                    "en": "No customer currently owes money in your shop."
                }
                msg = empty_msgs.get(detected_lang, empty_msgs["hi"])
                resp = {"text": msg, "spoken": msg}

            return {
                "session_id": session_id,
                "primary_intent": IntentClassifier.INTENT_TOP_DEBTORS,
                "action": "SHOW_REPORT",
                "text_response": resp["text"],
                "spoken_response": resp["spoken"],
                "language": detected_lang,
                "events": [],
                "requires_clarification": False
            }

        # C) Balance Inquiry for a Customer
        if classified_intent == IntentClassifier.INTENT_CHECK_BALANCE:
            cust_name = EntityExtractor.extract_customer_name(raw_text)
            if cust_name:
                cust = db.query(Customer).filter(
                    Customer.shop_id == shop_id,
                    Customer.archived_at == None,
                    Customer.name.ilike(f"%{cust_name}%")
                ).first()
                if cust:
                    bal, _, _ = LedgerService.get_customer_balance(db, shop_id, cust.id)
                    resp = ResponseGenerator.generate_balance_response(cust.name, bal, language=detected_lang)
                    return {
                        "session_id": session_id,
                        "primary_intent": IntentClassifier.INTENT_CHECK_BALANCE,
                        "action": "SHOW_BALANCE",
                        "text_response": resp["text"],
                        "spoken_response": resp["spoken"],
                        "language": detected_lang,
                        "customer": {"name": cust.name, "balance": float(bal)},
                        "events": [],
                        "requires_clarification": False
                    }

        # 5. Standard Financial Entry / Multi-Event Parsing
        interpret_res = TransactionParser.parse(raw_text, db=db, shop_id=shop_id, language=detected_lang)

        # Check Ambiguity (Save context for next turn in conversational loop!)
        if interpret_res.requires_clarification and interpret_res.events:
            first_ev = interpret_res.events[0]
            if first_ev.intent == IntentClassifier.INTENT_AMBIGUOUS_TRANSACTION and first_ev.amount:
                session["awaiting"] = "TYPE"
                session["pending_customer_name"] = first_ev.customer_name
                session["pending_customer_id"] = first_ev.customer_id
                session["pending_amount"] = first_ev.amount
                session["pending_date"] = first_ev.transaction_date

                clar_q = ResponseGenerator.generate_clarification_prompt(
                    "AMBIGUOUS_TYPE",
                    customer_name=first_ev.customer_name,
                    amount=first_ev.amount,
                    language=detected_lang
                )
                return {
                    "session_id": session_id,
                    "primary_intent": first_ev.intent,
                    "action": "AWAITING_CLARIFICATION",
                    "text_response": clar_q,
                    "spoken_response": clar_q,
                    "language": detected_lang,
                    "events": [first_ev.model_dump()],
                    "requires_clarification": True
                }

            if "amount" in first_ev.missing_fields:
                session["awaiting"] = "AMOUNT"
                session["pending_customer_name"] = first_ev.customer_name
                session["pending_customer_id"] = first_ev.customer_id
                session["pending_intent"] = first_ev.intent

                clar_q = ResponseGenerator.generate_clarification_prompt(
                    "MISSING_AMOUNT",
                    customer_name=first_ev.customer_name,
                    language=detected_lang
                )
                return {
                    "session_id": session_id,
                    "primary_intent": first_ev.intent,
                    "action": "AWAITING_CLARIFICATION",
                    "text_response": clar_q,
                    "spoken_response": clar_q,
                    "language": detected_lang,
                    "events": [first_ev.model_dump()],
                    "requires_clarification": True
                }

        # Ready for confirmation card
        serialized_events = [e.model_dump() for e in interpret_res.events]
        spoken_clar = interpret_res.clarification_prompt or "Please review and confirm these ledger entries."
        return {
            "session_id": session_id,
            "primary_intent": interpret_res.primary_intent,
            "action": "SHOW_CONFIRMATION" if not interpret_res.requires_clarification else "AWAITING_CLARIFICATION",
            "text_response": spoken_clar,
            "spoken_response": spoken_clar,
            "language": detected_lang,
            "events": serialized_events,
            "requires_clarification": interpret_res.requires_clarification
        }
