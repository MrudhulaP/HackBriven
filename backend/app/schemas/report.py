from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from decimal import Decimal

class DailyReportResponse(BaseModel):
    report_date: date
    total_credit: Decimal
    total_payment: Decimal
    net_change: Decimal
    transaction_count: int
    customers_served: int

class TopCustomerReport(BaseModel):
    customer_id: str
    customer_name: str
    outstanding_balance: Decimal
    last_transaction_date: Optional[str] = None

class DailyTrendPoint(BaseModel):
    date: str
    credit: Decimal
    payment: Decimal

class MonthlyReportResponse(BaseModel):
    month_name: str
    year: int
    total_credit: Decimal
    total_payment: Decimal
    net_credit_given: Decimal
    current_total_outstanding: Decimal
    active_customers_count: int
    top_debtors: List[TopCustomerReport]
    daily_trends: List[DailyTrendPoint]

class OutstandingSummaryResponse(BaseModel):
    total_outstanding: Decimal
    total_customers_with_balance: int
    total_credit_today: Decimal
    total_payment_today: Decimal
    total_customers: int
    total_customers_count: int
