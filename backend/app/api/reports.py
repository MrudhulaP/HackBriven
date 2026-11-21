from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import Shop
from app.schemas.report import DailyReportResponse, MonthlyReportResponse, OutstandingSummaryResponse
from app.services.report_service import ReportService
from app.api.deps import get_current_shop

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])

@router.get("/daily", response_model=DailyReportResponse)
def get_daily_report(
    target_date: Optional[date] = Query(None),
    shop: Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    return ReportService.get_daily_report(db, shop.id, target_date)

@router.get("/monthly", response_model=MonthlyReportResponse)
def get_monthly_report(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    shop: Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    return ReportService.get_monthly_report(db, shop.id, year, month)

@router.get("/outstanding", response_model=OutstandingSummaryResponse)
def get_outstanding_summary(
    shop: Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    daily = ReportService.get_daily_report(db, shop.id)
    summary = ReportService.get_dashboard_summary(db, shop.id)
    return OutstandingSummaryResponse(
        total_outstanding=summary["total_outstanding"],
        total_customers_with_balance=0,  # can calculate if needed
        total_credit_today=daily["total_credit"],
        total_payment_today=daily["total_payment"],
        total_customers_count=summary["total_customers"]
    )
