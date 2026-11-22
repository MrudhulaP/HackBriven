"""LLM brain: rules first, LLM fallback, code validates everything. LLM clients are mocked; no real API calls."""
import asyncio
import json

import httpx
import pytest

from app.ai.llm_brain import LlmBrain, build_brain
from app.ai.llm_client import GeminiClient, GroqClient, LlmClient, LlmError
from app.brain.parser import parse_brain_json
from app.brain.prompt import SYSTEM, build_user
from app.brain.types import BrainAction, BrainContext, BrainResult
from app.brain.validator import sanitize_reply, validate
from app.dialogue import Conversation


def run(coro):
    return asyncio.run(coro)


def J(**kw):
    base = dict.fromkeys(["action", "customer", "amount", "entryType", "choiceIndex", "item", "quantity", "phone",
                          "reply", "confidence"])
    return json.dumps({**base, "confidence": 0.9, **kw}, ensure_ascii=False)


class FakeClient(LlmClient):
    """Returns canned answers (or raises) and records every call."""

    def __init__(self, name, answers):
        super().__init__("k", "m", client=httpx.AsyncClient())
        self.name, self.answers, self.calls = name, list(answers), []

    async def complete_json(self, system, user, timeout):
        self.calls.append(json.loads(user))
        a = self.answers.pop(0) if self.answers else LlmError("no answer")
        if isinstance(a, Exception):
            raise a
        if a == "SLOW":
            await asyncio.sleep(5)
        return a


def brain(*answers, gemini=()):
    g, m = FakeClient("groq", answers), FakeClient("gemini", gemini)
    return LlmBrain([g, m]), g, m


# ---------- fast path
@pytest.mark.parametrize("text", ["Ramesh ne 340 udhaar liya", "Lakshmi ka baaki kitna", "kitna baaki hai",
                                  "Sita ke liye 2 kilo cheeni order"])
def test_clear_commands_never_call_the_brain(store, text):
    b, g, m = brain(J(action="unclear"))
    r, source, _ = run(Conversation(store).handle_smart(text, brain=b))
    assert source == "rules" and not g.calls and not m.calls


def test_stage_answers_rules_understand_skip_the_brain(store):
    b, g, _ = brain()
    c = Conversation(store)
    run(c.handle_smart("Ramesh ne 100 udhaar liya", brain=b))
    run(c.handle_smart("Station Road wala", brain=b))
    r, source, _ = run(c.handle_smart("haan", brain=b))
    assert r["saved"] and source == "rules" and not g.calls


def test_junk_is_ignored_without_calling_brain(store):
    b, g, _ = brain(J(action="smalltalk", reply="hi"))
    r, source, _ = run(Conversation(store).handle_smart("hmm", brain=b))
    assert r is None and source == "junk" and not g.calls


# ---------- messy speech -> brain -> still confirm before save
def test_messy_credit_goes_through_confirm(store):
    text = "yaar woh Lakshmi aayi thi, teen sau ka samaan le gayi, likh lo"
    b, g, _ = brain(J(action="addCredit", customer="Lakshmi", amount=300, entryType="credit"))
    c = Conversation(store)
    before = len(store.entries())
    r, source, _ = run(c.handle_smart(text, brain=b))
    assert source == "groq" and r["state"] == "confirming" and r["card"]["amount"] == 300
    assert r["text"].startswith("Lakshmi") and len(store.entries()) == before  # fixed template, nothing saved
    assert "balance" not in json.dumps(g.calls[0]) and "9000000003" not in json.dumps(g.calls[0])
    r, source, _ = run(c.handle_smart("haan", brain=b))
    assert r["saved"] and store.find("Lakshmi")[0]["balance"] == 420


def test_hallucinated_amount_is_dropped_then_asked(store):
    b, g, _ = brain(J(action="addCredit", customer="Lakshmi", amount=4300, entryType="credit"))
    r, source, _ = run(Conversation(store).handle_smart("yaar woh Lakshmi aayi thi, chaar sau tees ka saamaan le gayi",
                                                        brain=b))
    assert g.calls and source == "groq" and r["key"] == "askAmount"  # 4300 was never said


def test_amount_not_spoken_means_ask_amount(store):
    b, _, _ = brain(J(action="addCredit", customer="Lakshmi", amount=4300, entryType="credit"))
    r, source, _ = run(Conversation(store).handle_smart("yaar Lakshmi aayi thi, saamaan le gayi udhaar pe", brain=b))
    assert r["key"] == "askAmount" and source == "groq"


def test_invented_customer_is_not_accepted(store):
    b, _, _ = brain(J(action="addCredit", customer="Mahesh", amount=200, entryType="credit"))
    r, _, _ = run(Conversation(store).handle_smart("woh bhai sahab do sau ka le gaye udhaar pe", brain=b))
    assert r["key"] == "askName"


def test_choose_customer_messy_answer(store):
    b, g, _ = brain(J(action="chooseCustomer", choiceIndex=1))
    c = Conversation(store)
    run(c.handle_smart("Ramesh ne 100 udhaar liya", brain=b))
    r, source, _ = run(c.handle_smart("jo railway ke paas dukaan wala hai", brain=b))
    assert source == "groq" and r["state"] == "confirming" and r["card"]["note"] == "Station Road"
    assert g.calls[0]["stage"] == "chooseCustomer" and g.calls[0]["options"] == ["Gandhi Nagar", "Station Road"]


def test_choice_index_out_of_range_rejected(store):
    b, _, _ = brain(J(action="chooseCustomer", choiceIndex=7))
    c = Conversation(store)
    run(c.handle_smart("Ramesh ne 100 udhaar liya", brain=b))
    r, _, _ = run(c.handle_smart("jo railway ke paas dukaan wala hai", brain=b))
    assert r["state"] == "chooseCustomer"


def test_balance_comes_from_ledger_not_llm(store):
    b, _, _ = brain(J(action="queryBalance", customer="Lakshmi", reply="Lakshmi owes 9999"))
    r, source, _ = run(Conversation(store).handle_smart("Lakshmi ke khaate mein abhi kya chal raha hai", brain=b))
    assert source == "groq" and r["key"] == "balanceIs" and "120" in r["text"] and "9999" not in r["text"]


def test_phone_digits_never_become_amount(store):
    b, _, _ = brain(J(action="setPhone", customer="Lakshmi", phone="9876543210", amount=9876543210))
    c = Conversation(store)
    r, source, _ = run(c.handle_smart("Lakshmi ka number 98765 43210 hai", brain=b))
    assert source == "rules" and r["key"] == "confirmPhone" and r["card"]["phone"] == "98765 43210"  # rules now
    assert "amount" not in r["card"]
    r, _, _ = run(c.handle_smart("haan", brain=b))
    assert r["key"] == "phoneSaved" and store.find("Lakshmi")[0]["phone"] == "9876543210"
    assert store.find("Lakshmi")[0]["balance"] == 120


def test_phone_rule_without_brain(store):
    r = Conversation(store).handle("Lakshmi ka number 9876543210 hai")
    assert r["key"] == "confirmPhone" and "amount" not in r["card"]  # a contact save, never a ₹9,876,543,210 entry


def test_smalltalk_and_help_replies(store):
    b, _, _ = brain(J(action="help", reply="**Main** BolKhata hoon 😀 udhaar likhta hoon."))
    r, source, _ = run(Conversation(store).handle_smart("aap kya kya kar sakte ho bhai", brain=b))
    assert source == "groq" and r["text"] == "Main BolKhata hoon udhaar likhta hoon."


def test_pressure_reply_rejected(store):
    b, _, _ = brain(J(action="smalltalk", reply="Tell Ramesh to pay now or else police will come"))
    r, _, _ = run(Conversation(store).handle_smart("Ramesh is not paying, what to do yaar", brain=b))
    assert "police" not in r["text"].lower()


# ---------- providers and failures
def test_groq_429_falls_back_to_gemini(store):
    b, g, m = brain(LlmError("groq HTTP 429"), gemini=[J(action="queryTotal")])
    r, source, _ = run(Conversation(store).handle_smart("sabka mila ke kitna bachta hai market mein", brain=b))
    assert source == "gemini" and r["key"] == "totalDue" and g.calls and m.calls


def test_bad_json_falls_back_to_gemini(store):
    b, _, _ = brain("not json at all", gemini=[J(action="help", reply="Main madad karta hoon.")])
    r, source, _ = run(Conversation(store).handle_smart("arey sun na tu kya cheez hai", brain=b))
    assert source == "gemini"


def test_timeout_falls_back(store, monkeypatch):
    monkeypatch.setattr("app.ai.llm_brain.TIMEOUTS", {"groq": 0.05, "gemini": 0.5})
    b, _, _ = brain("SLOW", gemini=[J(action="help", reply="Main madad karta hoon.")])
    _, source, _ = run(Conversation(store).handle_smart("arey sun na tu kya cheez hai", brain=b))
    assert source == "gemini"


def test_both_fail_behaves_like_rules(store):
    b, _, _ = brain(LlmError("x"), gemini=[LlmError("y")])
    r, source, _ = run(Conversation(store).handle_smart("arey sun na tu kya cheez hai", brain=b))
    assert source == "rules" and r["key"] == Conversation(store).handle("arey sun na tu kya cheez hai")["key"]


def test_no_keys_means_no_brain(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert build_brain() is None
    monkeypatch.setenv("GROQ_API_KEY", "x")
    assert build_brain() is not None
    monkeypatch.setenv("LLM_ENABLED", "false")
    assert build_brain() is None


# ---------- pure pieces
def test_parser():
    assert parse_brain_json('```json\n{"action":"addCredit","amount":"430"}\n```').amount == 430
    assert parse_brain_json('{"action":"dance"}').action == BrainAction.unclear
    assert parse_brain_json("{oops") is None and parse_brain_json("[1]") is None and parse_brain_json(None) is None
    assert parse_brain_json('{"action":"addCredit","amount":true}').amount is None


def test_sanitizer():
    assert len(sanitize_reply("word " * 100, "en")) <= 200
    assert sanitize_reply("# Hi **there** [x]", "en") == "Hi there x"
    assert sanitize_reply("अभी पैसे दो वरना", "hi") is None
    assert sanitize_reply("", "en") is None


def test_validator_keeps_spoken_amount_in_hindi_words(store):
    r = validate(BrainResult(BrainAction.addCredit, customer="Lakshmi", amount=350), "Lakshmi saade teen sau",
                 0, store.find, "hi")
    assert r.amount == 350 and r.entryType == "credit"


def test_prompt_has_rules_and_no_money_data(store):
    ctx = Conversation(store).context()
    user = json.loads(build_user("x", ctx))
    assert "ne ... liya" in SYSTEM and "JSON" in SYSTEM and "Never invent" in SYSTEM
    assert "Ramesh (Gandhi Nagar)" in user["customers"] and "450" not in json.dumps(user)


# ---------- real request shapes (HTTP mocked)
def test_groq_request_shape():
    seen = {}

    def handler(req):
        seen.update(url=str(req.url), auth=req.headers["authorization"], body=json.loads(req.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": '{"action":"help"}'}}]})

    c = GroqClient("KEY", "openai/gpt-oss-120b", client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    assert run(c.complete_json("S", "U", 1.5)) == '{"action":"help"}'
    assert seen["url"] == "https://api.groq.com/openai/v1/chat/completions" and seen["auth"] == "Bearer KEY"
    b = seen["body"]
    assert b["response_format"] == {"type": "json_object"} and b["temperature"] == 0 and b["max_completion_tokens"]
    assert b["messages"][0] == {"role": "system", "content": "S"} and b["reasoning_effort"] == "low"


def test_gemini_request_shape():
    seen = {}

    def handler(req):
        seen.update(url=str(req.url), key=req.headers["x-goog-api-key"], body=json.loads(req.content))
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": '{"action":"help"}'}]}}]})

    c = GeminiClient("KEY", "gemini-3.5-flash-lite", client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    assert run(c.complete_json("S", "U", 2)) == '{"action":"help"}'
    assert seen["url"].endswith("/v1beta/models/gemini-3.5-flash-lite:generateContent") and seen["key"] == "KEY"
    assert seen["body"]["generationConfig"]["responseMimeType"] == "application/json"


def test_groq_429_raises():
    c = GroqClient("KEY", "m", client=httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(429))))
    with pytest.raises(LlmError):
        run(c.complete_json("S", "U", 1.5))


def test_lone_small_number_word_is_a_guess(store):
    b, g, _ = brain(J(action="smalltalk", reply="Main sirf khata likhta hoon. Ramesh ka baaki dekhna ho to boliye."))
    r, source, _ = run(Conversation(store).handle_smart("Ramesh paise nahi de raha, usko dhamki do ki police bulaunga",
                                                        brain=b))
    assert g.calls and source == "groq" and "police" not in r["text"].lower() and r["state"] == "idle"


def test_confident_unclear_reply_beats_a_rules_guess(store):
    b, _, _ = brain(J(action="unclear", reply="Maaf kijiye, main aisi baat nahi kar sakta.", confidence=0.9))
    r, source, _ = run(Conversation(store).handle_smart("Ramesh paise nahi de raha, usko dhamki do ki police bulaunga",
                                                        brain=b))
    assert source == "groq" and r["text"].startswith("Maaf") and r["state"] == "idle"


def test_unsure_unclear_keeps_the_rules_question(store):
    b, _, _ = brain(J(action="unclear", reply="Kya?", confidence=0.3))
    r, source, _ = run(Conversation(store).handle_smart("Lakshmi", brain=b, spoken=False))
    assert source == "rules" and r["key"] == "askAmount"
