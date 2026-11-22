"""Customer messages when an order arrives.

The order status and the message are tracked separately: marking an order arrived always succeeds; the message has
its own record (one per order and event, so repeated clicks never send twice) with status sent / failed / no_phone /
not_configured, and failed sends can be retried.

No messaging provider is configured by default. WhatsApp Business (Cloud API) or an SMS gateway needs a business
account, a sender number and, for WhatsApp, a pre-approved message template, so automatic sending stays off until
those are set up (see README). Until then the shopkeeper sends the prepared message with one tap (wa.me link).
"""
import logging
import os
import uuid
from datetime import datetime, timezone

log = logging.getLogger("bolkhata.notify")


class Sender:
    """Interface for a real provider. send() returns (ok, reason)."""
    name = "none"

    async def send(self, phone: str, text: str):
        raise NotImplementedError


def build_sender():
    provider = os.environ.get("MESSAGING_PROVIDER", "").strip().lower()
    if not provider:
        return None
    log.warning("MESSAGING_PROVIDER=%s is not implemented yet; automatic messages stay off", provider)
    return None


async def notify_arrival(store, order_ids, sender, text_for):
    """After the orders are marked arrived. Returns what happened, for the shopkeeper's screen."""
    orders = [o for o in store.orders("arrived") if o["id"] in set(order_ids)]
    if not orders:
        return None
    c = store.customer(orders[0]["customer_id"])
    ref = ", ".join(o["items"] for o in orders)
    key = "arrived:" + ",".join(sorted(order_ids))
    rec = store.notifications_c.find_one({"key": key}, {"_id": 0})
    if rec and rec["status"] == "sent":
        return {"status": "already_sent", "customer_id": c["id"], "name": c["name"], "orders": ref, "order_ids": order_ids}
    if not c["phone"]:
        status, reason = "no_phone", None
    elif sender is None:
        status, reason = "not_configured", None
    else:
        try:
            ok, reason = await sender.send(c["phone"], text_for(c, ref))
            status = "sent" if ok else "failed"
        except Exception as e:  # noqa: BLE001 - the order stays arrived; only the message failed
            status, reason = "failed", type(e).__name__
    now = datetime.now(timezone.utc)
    store.notifications_c.update_one({"key": key}, {
        "$set": {"status": status, "reason": reason, "channel": getattr(sender, "name", "none"), "updated_at": now,
                 "customer_id": c["id"], "order_ids": order_ids},
        "$setOnInsert": {"id": str(uuid.uuid4()), "created_at": now},
        "$inc": {"attempts": 1}}, upsert=True)
    return {"status": status, "reason": reason, "customer_id": c["id"], "name": c["name"], "orders": ref,
            "order_ids": order_ids}
