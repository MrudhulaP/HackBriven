"""Code checks every LLM result before the app acts on it. The LLM never decides money or customers on its own."""
import re
from dataclasses import replace

from ..lang import SCRIPTS, edit_distance, name_key
from ..nlu import amounts, extract_phone, tokenize
from ..prompts import BANNED
from .types import TALK, BrainAction, BrainResult

LEDGER = {BrainAction.addCredit, BrainAction.recordPayment, BrainAction.correction}
_EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]")


def sanitize_reply(text, lang):
    """Plain spoken text, max 200 chars; None if empty or it pressures anyone about money."""
    if not text:
        return None
    t = re.sub(r"[*_`#>\[\]|~]", "", text)
    t = re.sub(r"\(https?://\S+\)|https?://\S+", "", t)
    t = _EMOJI.sub("", t)
    t = re.sub(r"\s+", " ", t).strip()
    own = SCRIPTS.get(lang)
    if own is not None and any(b != own and b <= ord(ch) < b + 0x80 for ch in t for b in SCRIPTS.values()):
        return None  # mixed scripts ("உधார்"): use the fixed template instead
    low = t.lower()
    if any(w in low for words in (BANNED.get(lang, []), BANNED["en"]) for w in words):
        return None
    if len(t) > 200:
        cut = t[:200]
        t = cut[:cut.rfind(" ")] if " " in cut else cut
    return t or None


def validate(r: BrainResult, transcript: str, n_options: int, find_customers, lang: str):
    """Returns a checked result, downgraded where the LLM went beyond what was said."""
    phone, rest = extract_phone(transcript)
    tokens = tokenize(rest)
    spoken_numbers = set(amounts(tokens))
    spoken_keys = {name_key(t) for t in tokens}

    amount = r.amount if r.amount is not None and r.amount > 0 and r.amount in spoken_numbers else None
    customer, area = r.customer, None
    m = re.fullmatch(r"(.+?)\s*\((.+)\)\s*", customer or "")
    if m:  # the LLM copied "Ramesh (Gandhi Nagar)" from the customer list
        customer, area = m.group(1).strip(), m.group(2).strip()
    ck = name_key(customer or "")
    said_it = any(ck == k or (min(len(ck), len(k)) >= 4 and edit_distance(ck, k) <= 1) for k in spoken_keys)
    if customer and not find_customers(customer) and not said_it:  # "Suresh" vs spoken சுரேஷ் (romanizes as 'churesh')
        customer = None  # neither an existing customer nor a name that was actually said
    choice = r.choiceIndex if r.choiceIndex is not None and 0 <= r.choiceIndex < n_options else None
    entry = r.entryType or {BrainAction.addCredit: "credit", BrainAction.recordPayment: "payment"}.get(r.action)
    item = r.item if r.item and set(map(name_key, tokenize(r.item))) & spoken_keys else None
    qty = r.quantity if r.quantity and (not re.search(r"\d", r.quantity) or
                                         set(amounts(tokenize(r.quantity))) <= spoken_numbers) else None
    action = r.action
    if action in LEDGER and r.confidence is not None and r.confidence < 0.4:
        action = BrainAction.unclear
    if action == BrainAction.chooseCustomer and choice is None:
        action = BrainAction.unclear
    reply = sanitize_reply(r.reply, lang) if action in TALK else None
    return replace(r, action=action, customer=customer, amount=amount, choiceIndex=choice, entryType=entry,
                   item=item, quantity=qty, phone=phone if r.phone and r.phone == phone else None, reply=reply,
                   area=area if customer else None)
