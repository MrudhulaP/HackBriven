"""MongoDB storage. raw_text and phone are AES-GCM encrypted at rest."""
import base64
import os
import re
import uuid
from datetime import datetime, timezone

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .lang import edit_distance, name_key, romanize


class Crypto:
    def __init__(self, key_b64: str):
        key = base64.urlsafe_b64decode(key_b64 + "=" * (-len(key_b64) % 4))
        if len(key) != 32:
            raise ValueError("ENCRYPTION_KEY must be 32 bytes, base64-encoded")
        self.aes = AESGCM(key)

    def enc(self, text):
        if not text:
            return text
        nonce = os.urandom(12)
        return base64.b64encode(nonce + self.aes.encrypt(nonce, text.encode(), None)).decode()

    def dec(self, blob):
        if not blob:
            return blob
        raw = base64.b64decode(blob)
        return self.aes.decrypt(raw[:12], raw[12:], None).decode()


_CASE_SUFFIXES = ("avarige", "ukku", "uku", "ige", "nige", "kke", "ge", "ke", "ki", "ku", "ni", "na")


def _aware(d):
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def now():
    return datetime.now(timezone.utc)


class Store:
    def __init__(self, db, crypto: Crypto):
        self.customers_c, self.entries_c, self.settings_c = db.customers, db.entries, db.settings
        self.orders_c = db.orders
        self.notifications_c = db.notifications
        self.crypto = crypto

    # ---- customers
    def _customer_out(self, c, balances, visits):
        return {"id": c["id"], "name": c["name"], "note": c.get("note", ""), "phone": self.crypto.dec(c.get("phone")),
                "balance": balances.get(c["id"], 0), "demo": c.get("demo", False), "created_at": c["created_at"],
                "last_visit": visits.get(c["id"])}

    def _last_visits(self):
        v = {}
        for coll in (self.entries_c, self.orders_c):
            for e in coll.find({}, {"_id": 0, "customer_id": 1, "created_at": 1}):
                if e["created_at"] > v.get(e["customer_id"], e["created_at"].replace(year=1)):
                    v[e["customer_id"]] = e["created_at"]
        return v

    def customers(self):
        bal, visits = self.balances(), self._last_visits()
        return [self._customer_out(c, bal, visits) for c in self.customers_c.find({}, {"_id": 0}).sort("created_at", 1)]

    def customer(self, cid):
        c = self.customers_c.find_one({"id": cid}, {"_id": 0})
        return c and self._customer_out(c, self.balances(), self._last_visits())

    def add_customer(self, name, note="", phone=None, demo=False):  # phone stays a string
        c = {"id": str(uuid.uuid4()), "name": name, "name_roman": romanize(name), "note": note,
             "phone": self.crypto.enc(phone), "demo": demo, "created_at": now()}
        self.customers_c.insert_one(dict(c))
        return self.customer(c["id"])

    def update_customer(self, cid, phone=None, note=None):
        changes = {}
        if phone is not None:
            changes["phone"] = self.crypto.enc(phone or None)
        if note is not None:
            changes["note"] = note
        if changes:
            self.customers_c.update_one({"id": cid}, {"$set": changes})

    def find(self, name):
        """Same customer across scripts (रमेश = Ramesh); edit distance 1 only if nothing matches exactly."""
        key = name_key(name)
        all_c = self.customers()
        exact = [c for c in all_c if name_key(c["name"]) == key]
        if exact or len(key) < 4:
            return exact
        close = [c for c in all_c if edit_distance(name_key(c["name"]), key) <= 1]
        if close:
            return close
        for suf in _CASE_SUFFIXES:  # ಲಕ್ಷ್ಮಿಗೆ / లక్ష్మికి / லக்ஷ்மிக்கு = "to Lakshmi"
            if key.endswith(suf) and len(key) - len(suf) >= 3:
                base = key[:-len(suf)]
                hit = [c for c in all_c if edit_distance(name_key(c["name"]), base) <= 1]
                if hit:
                    return hit
        return []

    # ---- entries
    def add_entry(self, cid, type_, amount, raw_text, language, created_at=None):
        if type_ not in ("credit", "payment") or not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            raise ValueError("bad entry")
        e = {"id": str(uuid.uuid4()), "customer_id": cid, "type": type_, "amount": amount,
             "raw_text": self.crypto.enc(raw_text), "language": language, "created_at": created_at or now()}
        self.entries_c.insert_one(dict(e))
        return e["id"]

    def entries(self, customer_id=None):
        q = {"customer_id": customer_id} if customer_id else {}
        out = []
        for e in self.entries_c.find(q, {"_id": 0}).sort("created_at", 1):
            e["raw_text"] = self.crypto.dec(e.get("raw_text"))
            out.append(e)
        return out

    def balances(self):
        bal = {}
        for e in self.entries_c.find({}, {"_id": 0, "customer_id": 1, "type": 1, "amount": 1}):
            bal[e["customer_id"]] = bal.get(e["customer_id"], 0) + (e["amount"] if e["type"] == "credit" else -e["amount"])
        return bal

    def balance(self, cid):
        return self.balances().get(cid, 0)

    def customer_with_phone(self, phone):
        return next((c for c in self.customers() if c["phone"] == phone), None)

    def payments_since(self, since):
        """Sum of payments received since a datetime (one source of truth: the entries)."""
        return sum(e["amount"] for e in self.entries_c.find({"type": "payment"}, {"_id": 0, "amount": 1, "created_at": 1})
                   if _aware(e["created_at"]) >= since)

    # ---- undo support (removes only what one confirmed action created)
    def delete_entry(self, eid):
        self.entries_c.delete_one({"id": eid})

    def delete_order(self, oid):
        self.orders_c.delete_one({"id": oid})

    def delete_customer_if_unused(self, cid):
        if not self.entries_c.count_documents({"customer_id": cid}) and not self.orders_c.count_documents({"customer_id": cid}):
            self.customers_c.delete_one({"id": cid})

    # ---- back-orders: pending -> arrived -> closed
    def add_order(self, cid, items, raw_text, language):
        o = {"id": str(uuid.uuid4()), "customer_id": cid, "items": items, "status": "pending",
             "raw_text": self.crypto.enc(raw_text), "language": language, "created_at": now()}
        self.orders_c.insert_one(dict(o))
        return o["id"]

    def orders(self, status=None, customer_id=None):
        q = {k: v for k, v in (("status", status), ("customer_id", customer_id)) if v}
        names = {c["id"]: c for c in self.customers()}
        out = []
        for o in self.orders_c.find(q, {"_id": 0}).sort("created_at", 1):
            c = names.get(o["customer_id"], {})
            out.append({**o, "raw_text": self.crypto.dec(o.get("raw_text")), "customer": c.get("name", "?"),
                        "note": c.get("note", ""), "phone": c.get("phone")})
        return out

    def set_order_status(self, oid, status):
        if status not in ("pending", "arrived", "closed"):
            raise ValueError("bad status")
        r = self.orders_c.update_one({"id": oid}, {"$set": {"status": status, status + "_at": now()}})
        return r.matched_count == 1

    # ---- settings
    DEFAULT_SETTINGS = {"shop_name": "Meri Dukaan", "upi_vpa": "", "default_language": "auto", "closing_time": "20:00",
                        "regional_language": "", "noisy_shop": "off"}

    def settings(self):
        s = self.settings_c.find_one({"_id": "shop"}, {"_id": 0}) or {}
        return {**self.DEFAULT_SETTINGS, **s}

    def save_settings(self, s):
        clean = {k: str(s[k])[:100] for k in self.DEFAULT_SETTINGS if k in s}
        if "closing_time" in clean and not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", clean["closing_time"]):
            raise ValueError("closing_time must be HH:MM")
        if clean.get("regional_language", "") not in ("", "kn", "te", "ta"):
            raise ValueError("regional_language must be kn, te, ta or empty")
        if clean.get("noisy_shop", "off") not in ("on", "off"):
            raise ValueError("noisy_shop must be on or off")
        self.settings_c.update_one({"_id": "shop"}, {"$set": clean}, upsert=True)
        return self.settings()

    # ---- synthetic demo data
    def seed_demo(self):
        if self.customers_c.count_documents({}):
            return
        for name, note, phone, rows in [
            ("Ramesh", "Gandhi Nagar", "9000000001", [("credit", 600, "Ramesh ne 600 udhaar liya"), ("payment", 150, "Ramesh se 150 mile")]),
            ("Ramesh", "Station Road", "9000000002", [("credit", 200, "Station Road wale Ramesh ne 200 liya")]),
            ("Lakshmi", "", "9000000003", [("credit", 120, "Lakshmi ne 120 udhaar liya")]),
        ]:
            c = self.add_customer(name, note, phone, demo=True)
            for t, a, raw in rows:
                self.add_entry(c["id"], t, a, raw, "hi")
