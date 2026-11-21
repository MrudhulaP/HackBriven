from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class SyncItem(BaseModel):
    operation_id: str
    operation_type: str  # 'CREATE_TRANSACTION', 'CREATE_CUSTOMER'
    payload: Dict[str, Any]
    client_timestamp: datetime

class SyncPushRequest(BaseModel):
    items: List[SyncItem]

class SyncResultItem(BaseModel):
    operation_id: str
    status: str  # 'SYNCED', 'DUPLICATE', 'FAILED'
    server_id: Optional[str] = None
    error: Optional[str] = None

class SyncPushResponse(BaseModel):
    processed_count: int
    results: List[SyncResultItem]
