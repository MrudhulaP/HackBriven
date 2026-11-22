"""Score the English/Hindi/Hinglish cases through the rules (no LLM). Used by the test suite and for reporting."""
import base64
import os
import re
import sys

import mongomock

sys.path.insert(0, os.path.dirname(__file__))
from en_hi_cases import CASES, NUMBERS  # noqa: E402

from app.dialogue import Conversation  # noqa: E402
from app.nlu import parse  # noqa: E402
from app.store import Crypto, Store  # noqa: E402

KEY = {"confirmCredit": "credit", "confirmCreditNew": "credit", "confirmPayment": "payment", "confirmOrder": "order",
       "balanceIs": "balance", "balanceMulti": "balance_multi", "totalDue": "total", "topDebtor": "top",
       "collectionsToday": "collect_today", "collectionsWeek": "collect_week", "confirmPhone": "contact",
       "confirmPhoneNew": "contact", "phoneTaken": "contact", "confirmAddCustomer": "add_customer", "recentList": "recent",
       "noEntriesYet": "recent", "pendingList": "orders_list", "noPendingOrders": "orders_list"}


def run_case(text):
    store = Store(mongomock.MongoClient().db, Crypto(base64.urlsafe_b64encode(b"k" * 32).decode()))
    store.seed_demo()
    return Conversation(store, "auto", "en").handle(text)


def check(case):
    text, _lang, intent, exp = case
    r = run_case(text)
    card = r.get("card") or {}
    got = KEY.get(r["key"], r["key"])
    problems = [] if got == intent else [f"intent {got}"]
    for k, v in exp.items():
        have = card.get(k)
        if k == "phone" and have:
            have = re.sub(r"\D", "", have)
        if k in ("amount", "items", "phone", "name") and k in card and have != v:
            problems.append(f"{k}={have!r}")
    return problems, r


if __name__ == "__main__":
    by = {}
    for case in CASES:
        problems, r = check(case)
        by.setdefault(case[1], [0, 0])
        by[case[1]][1] += 1
        if problems:
            print(f"FAIL [{case[1]}] {case[0]!r}: {problems} | {r['text'][:60]}")
        else:
            by[case[1]][0] += 1
    nums_ok = sum(parse(t).amount == v for t, v in NUMBERS)
    for lang, (ok, n) in by.items():
        print(f"{lang:9} intent+entities: {ok}/{n}")
    print(f"numbers: {nums_ok}/{len(NUMBERS)}")
    for t, v in NUMBERS:
        if parse(t).amount != v:
            print("  number FAIL", t, "->", parse(t).amount, "want", v)
