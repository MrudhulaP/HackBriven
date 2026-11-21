from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import Shop
from app.schemas.sync import SyncPushRequest, SyncPushResponse
from app.services.sync_service import SyncService
from app.api.deps import get_current_shop

router = APIRouter(prefix="/sync", tags=["Offline Sync"])

@router.post("/push", response_model=SyncPushResponse)
def push_offline_items(
    data: SyncPushRequest,
    shop: Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    results = SyncService.process_sync_batch(db, shop.id, data.items)
    return SyncPushResponse(
        processed_count=len(results),
        results=results
    )

@router.get("/status")
def sync_status(shop: Shop = Depends(get_current_shop)):
    return {
        "status": "online",
        "shop_id": shop.id,
        "message": "BolKhata cloud synchronization service is active."
    }
