from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.models.transaction import Transaction
from app.models.customer import Customer
from app.services.ledger_service import quantize_inr, LedgerService

class ReportService:
    @staticmethod
    def get_daily_report(db: Session, shop_id: str, target_date: Optional[date] = None) -> Dict[str, Any]:
        target = target_date or date.today()

        credit_today = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.shop_id == shop_id,
            Transaction.type == "CREDIT",
            Transaction.status == "CONFIRMED",
            Transaction.transaction_date == target
        ).scalar()

        payment_today = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.shop_id == shop_id,
            Transaction.type == "PAYMENT",
            Transaction.status == "CONFIRMED",
            Transaction.transaction_date == target
        ).scalar()

        tx_count = db.query(func.count(Transaction.id)).filter(
            Transaction.shop_id == shop_id,
            Transaction.status == "CONFIRMED",
            Transaction.transaction_date == target
        ).scalar() or 0

        customers_served = db.query(func.count(func.distinct(Transaction.customer_id))).filter(
            Transaction.shop_id == shop_id,
            Transaction.status == "CONFIRMED",
            Transaction.transaction_date == target
        ).scalar() or 0

        c_dec = quantize_inr(Decimal(str(credit_today)))
        p_dec = quantize_inr(Decimal(str(payment_today)))
        net_change = quantize_inr(c_dec - p_dec)

        return {
            "report_date": target,
            "total_credit": c_dec,
            "total_payment": p_dec,
            "net_change": net_change,
            "transaction_count": tx_count,
            "customers_served": customers_served
        }

    @staticmethod
    def get_monthly_report(db: Session, shop_id: str, year: Optional[int] = None, month: Optional[int] = None) -> Dict[str, Any]:
        today = date.today()
        target_year = year or today.year
        target_month = month or today.month

        # First and last day of month
        start_date = date(target_year, target_month, 1)
        if target_month == 12:
            end_date = date(target_year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(target_year, target_month + 1, 1) - timedelta(days=1)

        credit_month = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.shop_id == shop_id,
            Transaction.type == "CREDIT",
            Transaction.status == "CONFIRMED",
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).scalar()

        payment_month = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.shop_id == shop_id,
            Transaction.type == "PAYMENT",
            Transaction.status == "CONFIRMED",
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).scalar()

        c_dec = quantize_inr(Decimal(str(credit_month)))
        p_dec = quantize_inr(Decimal(str(payment_month)))
        net_credit = quantize_inr(c_dec - p_dec)

        # Active customers this month
        active_customers = db.query(func.count(func.distinct(Transaction.customer_id))).filter(
            Transaction.shop_id == shop_id,
            Transaction.status == "CONFIRMED",
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).scalar() or 0

        # Calculate total outstanding across all customers in the shop
        customers = db.query(Customer).filter(
            Customer.shop_id == shop_id,
            Customer.archived_at == None
        ).all()

        customer_balances = []
        total_outstanding = Decimal("0")
        for c in customers:
            bal, _, _ = LedgerService.get_customer_balance(db, shop_id, c.id)
            total_outstanding += bal
            if bal > Decimal("0"):
                customer_balances.append({
                    "customer_id": c.id,
                    "customer_name": c.name,
                    "outstanding_balance": bal
                })

        # Top debtors
        customer_balances.sort(key=lambda x: x["outstanding_balance"], reverse=True)
        top_debtors = customer_balances[:5]

        # Daily trends for the month
        daily_trends = []
        cur = start_date
        # Limit trend days up to today if in current month
        max_trend_date = min(end_date, today)
        while cur <= max_trend_date:
            day_credit = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
                Transaction.shop_id == shop_id,
                Transaction.type == "CREDIT",
                Transaction.status == "CONFIRMED",
                Transaction.transaction_date == cur
            ).scalar()
            day_payment = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
                Transaction.shop_id == shop_id,
                Transaction.type == "PAYMENT",
                Transaction.status == "CONFIRMED",
                Transaction.transaction_date == cur
            ).scalar()

            daily_trends.append({
                "date": cur.isoformat(),
                "credit": quantize_inr(Decimal(str(day_credit))),
                "payment": quantize_inr(Decimal(str(day_payment)))
            })
            cur += timedelta(days=1)

        month_names = ["January", "February", "March", "April", "May", "June", "July",
                       "August", "September", "October", "November", "December"]

        return {
            "month_name": month_names[target_month - 1],
            "year": target_year,
            "total_credit": c_dec,
            "total_payment": p_dec,
            "net_credit_given": net_credit,
            "current_total_outstanding": quantize_inr(total_outstanding),
            "active_customers_count": active_customers,
            "top_debtors": top_debtors,
            "daily_trends": daily_trends
        }

    @staticmethod
    def get_dashboard_summary(db: Session, shop_id: str) -> Dict[str, Any]:
        """Calculates real-time metrics for the 4 summary cards on the Dashboard."""
        today = date.today()

        # 1. Total Outstanding (all confirmed credits - all confirmed payments)
        total_credit = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.shop_id == shop_id,
            Transaction.type == "CREDIT",
            Transaction.status == "CONFIRMED"
        ).scalar()

        total_payment = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.shop_id == shop_id,
            Transaction.type == "PAYMENT",
            Transaction.status == "CONFIRMED"
        ).scalar()

        tot_cred_dec = quantize_inr(Decimal(str(total_credit)))
        tot_pay_dec = quantize_inr(Decimal(str(total_payment)))
        total_outstanding = quantize_inr(tot_cred_dec - tot_pay_dec)

        # 2. Today's Credit
        today_credit = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.shop_id == shop_id,
            Transaction.type == "CREDIT",
            Transaction.status == "CONFIRMED",
            Transaction.transaction_date == today
        ).scalar()

        # 3. Today's Collections (Payments)
        today_payment = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.shop_id == shop_id,
            Transaction.type == "PAYMENT",
            Transaction.status == "CONFIRMED",
            Transaction.transaction_date == today
        ).scalar()

        # 4. Total Customers
        customer_count = db.query(func.count(Customer.id)).filter(
            Customer.shop_id == shop_id,
            Customer.archived_at == None
        ).scalar() or 0

        return {
            "total_outstanding": total_outstanding,
            "today_credit": quantize_inr(Decimal(str(today_credit))),
            "today_payment": quantize_inr(Decimal(str(today_payment))),
            "total_customers": customer_count
        }
