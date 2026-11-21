import json
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, PendingSync
from app.models.customer import Customer
from app.schemas.sync import SyncItem, SyncResultItem
from app.services.ledger_service import LedgerService, quantize_inr

class SyncService:
    @staticmethod
    def process_sync_batch(db: Session, shop_id: str, items: List[SyncItem]) -> List[SyncResultItem]:
        results = []

        for item in items:
            op_id = item.operation_id
            op_type = item.operation_type
            payload = item.payload

            # Check if this operation_id was already processed
            existing_sync = db.query(PendingSync).filter(
                PendingSync.operation_id == op_id,
                PendingSync.shop_id == shop_id
            ).first()

            if existing_sync and existing_sync.sync_status == "SYNCED":
                results.append(SyncResultItem(
                    operation_id=op_id,
                    status="DUPLICATE",
                    server_id=existing_sync.id,
                    error=None
                ))
                continue

            try:
                server_id = None
                if op_type == "CREATE_TRANSACTION":
                    # Extract payload details
                    customer_id = payload.get("customer_id")
                    tx_type = payload.get("type")
                    amount = Decimal(str(payload.get("amount", "0")))
                    tx_date_raw = payload.get("transaction_date")
                    tx_date = date.fromisoformat(tx_date_raw) if tx_date_raw else date.today()
                    desc = payload.get("description", "Offline sync transaction")
                    idempotency_key = payload.get("idempotency_key") or op_id

                    tx = LedgerService.create_transaction(
                        db=db,
                        shop_id=shop_id,
                        customer_id=customer_id,
                        type=tx_type,
                        amount=amount,
                        transaction_date=tx_date,
                        description=desc,
                        input_method="OFFLINE_SYNC",
                        idempotency_key=idempotency_key
                    )
                    server_id = tx.id

                elif op_type == "CREATE_CUSTOMER":
                    cust_name = payload.get("name", "").strip()
                    mobile = payload.get("mobile")
                    address = payload.get("address")
                    notes = payload.get("notes")

                    cust = Customer(
                        id=str(uuid.uuid4()),
                        shop_id=shop_id,
                        name=cust_name,
                        mobile=mobile,
                        address=address,
                        notes=notes,
                        created_at=datetime.utcnow()
                    )
                    db.add(cust)
                    db.commit()
                    db.refresh(cust)
                    server_id = cust.id
                else:
                    raise ValueError(f"Unsupported operation type: {op_type}")

                # Record sync success
                if not existing_sync:
                    sync_record = PendingSync(
                        id=str(uuid.uuid4()),
                        shop_id=shop_id,
                        operation_id=op_id,
                        operation_type=op_type,
                        payload=json.dumps(payload),
                        sync_status="SYNCED",
                        created_at=datetime.utcnow()
                    )
                    db.add(sync_record)
                else:
                    existing_sync.sync_status = "SYNCED"

                db.commit()

                results.append(SyncResultItem(
                    operation_id=op_id,
                    status="SYNCED",
                    server_id=server_id,
                    error=None
                ))

            except Exception as e:
                db.rollback()
                results.append(SyncResultItem(
                    operation_id=op_id,
                    status="FAILED",
                    server_id=None,
                    error=str(e)
                ))

        return results
