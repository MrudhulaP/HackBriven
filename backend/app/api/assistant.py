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

    # 1. "Who owes me the most money?" / "Sabse zyada udhaar kiska hai?"
    if any(p in query_low for p in ["who owes", "most money", "highest", "sabse zyada", "sabse bada", "tumba saala"]):
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
            text = "Kisi grahak ka koi udhaar baaki nahi hai." if lang == "hi" else (
                "Yavude grahakara baaki illa." if lang == "kn" else "No customer currently owes money."
            )
            return AssistantQueryResponse(query=query_raw, answer=text, spoken_answer=text, data={"ranked": []})
        top_name, top_bal = ranked[0]
        text_hi = f"Sabse zyada udhaar {top_name} ka hai, kul ₹{top_bal} baaki hai."
        text_kn = f"Ati hecchu saala {top_name} avardagi ide, otu ₹{top_bal} baaki ide."
        text_en = f"{top_name} owes the most money, with an outstanding balance of ₹{top_bal}."

        answer = text_kn if lang == "kn" else (text_en if lang == "en" else text_hi)
        return AssistantQueryResponse(
            query=query_raw,
            answer=answer,
            spoken_answer=answer,
            data={"customer": top_name, "amount": str(top_bal)}
        )

    # 2. "How much did I collect today?" / "Aaj kitna collection hua?"
    if any(p in query_low for p in ["collect", "collection", "jama", "aaj kitna aaya", "ivattina collection"]):
        daily = ReportService.get_daily_report(db, shop.id, today)
        tot_pay = daily["total_payment"]
        text_hi = f"Aaj kul ₹{tot_pay} jama huye hain."
        text_kn = f"Ivattu otu ₹{tot_pay} collection aagide."
        text_en = f"You have collected ₹{tot_pay} today."

        answer = text_kn if lang == "kn" else (text_en if lang == "en" else text_hi)
        return AssistantQueryResponse(
            query=query_raw,
            answer=answer,
            spoken_answer=answer,
            data={"today_collection": str(tot_pay)}
        )

    # 3. "How much credit did I give today?" / "Aaj kitna udhaar diya?"
    if any(p in query_low for p in ["credit gave", "give today", "udhaar diya", "saala kotte", "aaj kitna udhaar"]):
        daily = ReportService.get_daily_report(db, shop.id, today)
        tot_cred = daily["total_credit"]
        text_hi = f"Aaj aapne ₹{tot_cred} ka udhaar diya hai."
        text_kn = f"Ivattu neevu ₹{tot_cred} saala kottiri."
        text_en = f"You gave ₹{tot_cred} in credit today."

        answer = text_kn if lang == "kn" else (text_en if lang == "en" else text_hi)
        return AssistantQueryResponse(
            query=query_raw,
            answer=answer,
            spoken_answer=answer,
            data={"today_credit": str(tot_cred)}
        )

    # 4. Customer balance inquiry: "Ramesh ka kitna baaki hai?" / "How much does Ramesh owe?"
    cust_name = EntityExtractor.extract_customer_name(query_raw)
    if cust_name:
        cust = db.query(Customer).filter(
            Customer.shop_id == shop.id,
            Customer.archived_at == None,
            Customer.name.ilike(f"%{cust_name}%")
        ).first()

        if cust:
            bal, cred, pay = LedgerService.get_customer_balance(db, shop.id, cust.id)
            if bal > Decimal("0"):
                t_hi = f"{cust.name} ka ₹{bal} baaki hai."
                t_kn = f"{cust.name} ge ₹{bal} baaki ide."
                t_en = f"{cust.name} owes ₹{bal}."
            elif bal < Decimal("0"):
                t_hi = f"{cust.name} ka ₹{abs(bal)} advance jama hai."
                t_kn = f"{cust.name} avara ₹{abs(bal)} advance ide."
                t_en = f"{cust.name} has an advance credit of ₹{abs(bal)}."
            else:
                t_hi = f"{cust.name} ka pura hisaab barabar hai (₹0 baaki)."
                t_kn = f"{cust.name} avara sampoorna hisaab chukti aagide (₹0 baaki)."
                t_en = f"{cust.name}'s balance is settled at ₹0."

            ans = t_kn if lang == "kn" else (t_en if lang == "en" else t_hi)
            return AssistantQueryResponse(
                query=query_raw,
                answer=ans,
                spoken_answer=ans,
                data={"customer_name": cust.name, "balance": str(bal)}
            )

    # Default general shop summary
    summary = ReportService.get_dashboard_summary(db, shop.id)
    def_hi = f"Aapka kul baaki udhaar ₹{summary['total_outstanding']} hai, aur dukaan mein {summary['total_customers']} grahak hain."
    def_kn = f"Nimma dukaanada otu baaki ₹{summary['total_outstanding']} ide, mattu {summary['total_customers']} grahakariddare."
    def_en = f"Total outstanding across your shop is ₹{summary['total_outstanding']}, with {summary['total_customers']} customers registered."

    ans = def_kn if lang == "kn" else (def_en if lang == "en" else def_hi)
    return AssistantQueryResponse(
        query=query_raw,
        answer=ans,
        spoken_answer=ans,
        data={"summary": {k: str(v) for k, v in summary.items()}}
    )
