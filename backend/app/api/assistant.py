import re
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database.session import get_db
from app.models.user import Shop
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.schemas.voice import AssistantQueryRequest, AssistantQueryResponse
from app.services.ledger_service import LedgerService, quantize_inr
from app.services.report_service import ReportService
from app.ai.language_detector import IndicLanguageDetector
from app.ai.entity_extractor import EntityExtractor
from app.ai.response_generator import ResponseGenerator
from app.api.deps import get_current_shop

router = APIRouter(prefix="/assistant", tags=["Financial Assistant"])

@router.post("/query", response_model=AssistantQueryResponse)
def query_financial_assistant(
    data: AssistantQueryRequest,
    shop: Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    query_raw = data.query.strip()
    query_low = query_raw.lower()
    lang = data.language or IndicLanguageDetector.detect(query_raw)
    today = date.today()

    # 1. Weekly Report Query: "How much money did I make this week?" / "Iss hafte kitna collection hua?"
    if any(p in query_low for p in ["this week", "made this week", "iss hafte", "is hafte", "ee varam", "ee vaaram", "inda vaaram", "indha vaaram", "week collection", "hafte"]):
        weekly = ReportService.get_weekly_report(db, shop.id, today)
        resp = ResponseGenerator.generate_weekly_summary_response(
            total_payment=weekly["total_payment"],
            total_credit=weekly["total_credit"],
            tx_count=weekly["transaction_count"],
            language=lang
        )
        return AssistantQueryResponse(
            query=query_raw,
            answer=resp["text"],
            spoken_answer=resp["spoken"],
            data={"weekly": {k: str(v) for k, v in weekly.items()}}
        )

    # 2. "Who owes me the most money?" / "Sabse zyada udhaar kiska hai?"
    if any(p in query_low for p in ["who owes", "most money", "highest", "sabse zyada", "sabse bada", "tumba saala", "ati hecchu", "ekkuva appu", "athigam kadan"]):
        customers = db.query(Customer).filter(
            Customer.shop_id == shop.id,
            Customer.archived_at == None
        ).all()
        ranked = []
        for c in customers:
            bal, _, _ = LedgerService.get_customer_balance(db, shop.id, c.id)
            if bal > Decimal("0"):
                ranked.append((c.name, bal))
        ranked.sort(key=lambda x: x[1], reverse=True)

        if not ranked:
            empty_texts = {
                "hi": "Kisi grahak ka koi udhaar baaki nahi hai.",
                "kn": "Yavude grahakara baaki illa.",
                "te": "Evariki baaki ledu.",
                "ta": "Yaarukkum baki illai.",
                "en": "No customer currently owes money."
            }
            text = empty_texts.get(lang, empty_texts["hi"])
            return AssistantQueryResponse(query=query_raw, answer=text, spoken_answer=text, data={"ranked": []})

        top_name, top_bal = ranked[0]
        resp = ResponseGenerator.generate_top_debtor_response(top_name, top_bal, language=lang)
        return AssistantQueryResponse(
            query=query_raw,
            answer=resp["text"],
            spoken_answer=resp["spoken"],
            data={"customer": top_name, "amount": str(top_bal)}
        )

    # 3. "How much did I collect today?" / "Aaj kitna collection hua?"
    if any(p in query_low for p in ["collect", "collection", "jama", "aaj kitna aaya", "ivattina collection", "eroju enta vachindi"]):
        daily = ReportService.get_daily_report(db, shop.id, today)
        tot_pay = daily["total_payment"]
        text_hi = f"Aaj kul ₹{tot_pay} jama huye hain."
        text_kn = f"Ivattu otu ₹{tot_pay} collection aagide."
        text_te = f"Eroju motham ₹{tot_pay} vasoolu aindi."
        text_ta = f"Inru moththam ₹{tot_pay} vasool aagirukku."
        text_en = f"You have collected ₹{tot_pay} today."

        mapping = {"kn": text_kn, "te": text_te, "ta": text_ta, "en": text_en, "hi": text_hi}
        answer = mapping.get(lang, text_hi)
        return AssistantQueryResponse(
            query=query_raw,
            answer=answer,
            spoken_answer=answer,
            data={"today_collection": str(tot_pay)}
        )

    # 4. "How much credit did I give today?" / "Aaj kitna udhaar diya?"
    if any(p in query_low for p in ["credit gave", "give today", "udhaar diya", "saala kotte", "aaj kitna udhaar", "appu ichanu"]):
        daily = ReportService.get_daily_report(db, shop.id, today)
        tot_cred = daily["total_credit"]
        text_hi = f"Aaj aapne ₹{tot_cred} ka udhaar diya hai."
        text_kn = f"Ivattu neevu ₹{tot_cred} saala kottiri."
        text_te = f"Eroju meeru ₹{tot_cred} appu icharu."
        text_ta = f"Inru neengal ₹{tot_cred} kadan kodutheergal."
        text_en = f"You gave ₹{tot_cred} in credit today."

        mapping = {"kn": text_kn, "te": text_te, "ta": text_ta, "en": text_en, "hi": text_hi}
        answer = mapping.get(lang, text_hi)
        return AssistantQueryResponse(
            query=query_raw,
            answer=answer,
            spoken_answer=answer,
            data={"today_credit": str(tot_cred)}
        )

    # 5. Customer balance inquiry: "Ramesh ka kitna baaki hai?" / "How much does Ramesh owe?"
    cust_name = EntityExtractor.extract_customer_name(query_raw)
    if cust_name:
        cust = db.query(Customer).filter(
            Customer.shop_id == shop.id,
            Customer.archived_at == None,
            Customer.name.ilike(f"%{cust_name}%")
        ).first()

        if cust:
            bal, cred, pay = LedgerService.get_customer_balance(db, shop.id, cust.id)
            resp = ResponseGenerator.generate_balance_response(cust.name, bal, language=lang)
            return AssistantQueryResponse(
                query=query_raw,
                answer=resp["text"],
                spoken_answer=resp["spoken"],
                data={"customer_name": cust.name, "balance": str(bal)}
            )

    # Default general shop summary
    summary = ReportService.get_dashboard_summary(db, shop.id)
    def_hi = f"Aapka kul baaki udhaar ₹{summary['total_outstanding']} hai, aur dukaan mein {summary['total_customers']} grahak hain."
    def_kn = f"Nimma dukaanada otu baaki ₹{summary['total_outstanding']} ide, mattu {summary['total_customers']} grahakariddare."
    def_te = f"Mee dukaanam motham baaki ₹{summary['total_outstanding']} undi, mariyu {summary['total_customers']} mandi grahakulunnaru."
    def_ta = f"Ungal kadaiyin moththa baki ₹{summary['total_outstanding']}, matrum {summary['total_customers']} vaadikkaiyaalargal ullaargal."
    def_en = f"Total outstanding across your shop is ₹{summary['total_outstanding']}, with {summary['total_customers']} customers registered."

    mapping = {"kn": def_kn, "te": def_te, "ta": def_ta, "en": def_en, "hi": def_hi}
    ans = mapping.get(lang, def_hi)
    return AssistantQueryResponse(
        query=query_raw,
        answer=ans,
        spoken_answer=ans,
        data={"summary": {k: str(v) for k, v in summary.items()}}
    )
