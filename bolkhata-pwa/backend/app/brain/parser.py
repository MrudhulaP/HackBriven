"""LLM JSON text -> BrainResult. Never throws: anything malformed gives None (or unclear for an unknown action)."""
import json
import re

from .types import BrainAction, BrainResult


def _int(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, str) and re.fullmatch(r"\s*\d+\s*", v):
        return int(v)
    return None


def _str(v, limit=80):
    return v.strip()[:limit] if isinstance(v, str) and v.strip() else None


def parse_brain_json(raw: str):
    try:
        text = re.sub(r"^\s*```(?:json)?|```\s*$", "", raw or "").strip()
        d = json.loads(text)
        if not isinstance(d, dict):
            return None
        try:
            action = BrainAction(d.get("action"))
        except ValueError:
            action = BrainAction.unclear
        conf = d.get("confidence")
        return BrainResult(
            action=action,
            customer=_str(d.get("customer"), 40),
            amount=_int(d.get("amount")),
            entryType=d.get("entryType") if d.get("entryType") in ("credit", "payment") else None,
            choiceIndex=_int(d.get("choiceIndex")),
            item=_str(d.get("item")),
            quantity=_str(d.get("quantity") if not isinstance(d.get("quantity"), (int, float)) else str(d["quantity"]), 30),
            phone=re.sub(r"\D", "", str(d["phone"])) if d.get("phone") is not None else None,
            reply=_str(d.get("reply"), 1000),
            confidence=float(conf) if isinstance(conf, (int, float)) and not isinstance(conf, bool) else None,
        )
    except Exception:  # noqa: BLE001 - bad model output must never crash the voice loop
        return None
