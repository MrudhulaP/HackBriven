"""English / Hindi / Hinglish suite (rules only, no network): intents, entities, numbers, and a 50-turn session."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "data"))
from en_hi_cases import CASES, NUMBERS  # noqa: E402
from run_probe import check  # noqa: E402

from app.dialogue import Conversation  # noqa: E402
from app.nlu import parse  # noqa: E402


@pytest.mark.parametrize("case", CASES, ids=[f"{c[1]}:{c[0][:40]}" for c in CASES])
def test_intent_and_entities(case):
    problems, r = check(case)
    assert not problems, (problems, r["text"])


@pytest.mark.parametrize("text,value", NUMBERS, ids=[t[:40] for t, _ in NUMBERS])
def test_number(text, value):
    assert parse(text).amount == value


@pytest.mark.parametrize("a,b", [
    ("Arjun needs 5 kg of sugar", "Arjun owes me 5 rupees"),                # order vs credit
    ("Lakshmi paid 200 rupees", "Lakshmi took 200 rupees on credit"),       # payment vs credit
    ("लक्ष्मी ने 200 रुपये दिए", "लक्ष्मी को 200 रुपये दिए"),                  # ne vs ko flips the meaning
    ("Lakshmi se 300 mile", "Lakshmi ko 300 diye"),
])
def test_near_identical_sentences_keep_different_meanings(a, b):
    pa, pb = parse(a), parse(b)
    assert (pa.order, pa.txn_type) != (pb.order, pb.txn_type)


def test_fifty_turn_session_mixed_languages(store):
    c = Conversation(store, "auto", "en")
    turns = [
        ("Lakshmi took 100 on credit", "confirmCredit", "en"), ("yes", "saved", "en"),
        ("लक्ष्मी ने 50 रुपये दिए", "confirmPayment", "hi"), ("हाँ", "saved", "hi"),
        ("Lakshmi ka baaki kitna", "balanceIs", "hi"), ("Show today's collections", "collectionsToday", "en"),
        ("Arjun needs 5 kg of sugar", "confirmOrder", "en"), ("yes", "orderSaved", "en"),
        ("अर्जुन का नंबर 999 9999999 है", "confirmPhone", "hi"), ("हाँ", "phoneSaved", "hi"),
        ("Who owes me the most money?", "topDebtor", "en"), ("Add Priya as a customer", "confirmAddCustomer", "en"),
        ("yes", "customerAdded", "en"), ("Priya ne 300 rupees udhaar liye", "confirmCredit", "hi"), ("haan", "saved", "hi"),
        ("Show recent transactions", "recentList", "en"), ("Arjun's sugar arrived", "confirmArrived", "en"),
        ("yes", "arrivedSaved", "en"), ("undo", "undone", "en"), ("pending orders batao", "pendingList", "en"),
        ("Priya paid 100", "confirmPayment", "en"), ("no", "cancelled", "en"), ("Priya paid 100", "confirmPayment", "en"),
        ("yes", "saved", "en"), ("कुल बकाया कितना है", "totalDue", "hi"), ("How much did I collect this week?", "collectionsWeek", "en"),
        ("Lakshmi ke khaate mein 40 likh do", "confirmCredit", "hi"), ("nahi 45", "confirmCredit", "hi"),
        ("haan", "saved", "hi"), ("What does Lakshmi owe me?", "balanceIs", "en"),
    ]
    for said, key, lang in turns:
        r = c.handle(said)
        assert r["key"] == key and r["lang"] == lang, (said, r["key"], r["lang"], r["text"])
    # 20 more turns with explicit language switching: the chosen language always wins
    for i in range(10):
        c.set_mode("hi" if i % 2 else "en")
        want = "hi" if i % 2 else "en"
        for said in ("Lakshmi ka baaki kitna", "What does Priya owe me?"):
            r = c.handle(said)
            assert r["key"] == "balanceIs" and r["lang"] == want, (i, said, r)
    assert len(turns) + 20 == 50
    assert store.find("Lakshmi")[0]["balance"] == 120 + 100 - 50 + 45
    assert store.find("Priya")[0]["balance"] == 300 - 100
    assert store.find("Arjun")[0]["phone"] == "9999999999"
    assert len(store.orders("pending")) == 1  # the arrival was undone
