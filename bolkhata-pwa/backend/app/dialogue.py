"""Dialogue state machine: idle, askName, askAmount, askType, askItems, chooseCustomer, askNote, confirming.
Three intents: txn (credit/payment), order (back-order to deliver later), arrival (ordered goods came in).
Nothing is written to the store until the shopkeeper confirms."""
import copy
from collections import deque

from .brain.types import TALK, BrainAction, BrainContext
from .brain.validator import validate
from .lang import detect_language
from .lang import name_key
from .nlu import KEYWORDS, choose_index, display_name, extract_items, extract_phone, is_name_word, parse, tokenize
from .prompts import UI, say


class Conversation:
    def __init__(self, store, lang_mode="auto", default_lang="hi"):
        self.store = store
        self.mode = lang_mode
        self.lang = default_lang if lang_mode == "auto" else lang_mode
        self.state = "idle"
        self.p = {}
        self.history = deque(maxlen=3)  # (shopkeeper, app) for the LLM's context
        self.miss = False  # rules could not understand this turn
        self.soft_miss = False  # rules only guessed (e.g. a name that is just the first unknown word)
        self.weak_name = False  # the guessed name matches no customer

    def set_mode(self, mode):
        self.mode = mode
        if mode != "auto":
            self.lang = mode

    # ---- replies
    def _r(self, key, card=None, chips=None, saved=False, **kw):
        return {"type": "reply", "key": key, "text": say(self.lang, key, **kw), "lang": self.lang, "state": self.state,
                "card": card, "options": chips or [], "saved": saved}

    def greeting(self):
        return self._r("greeting")

    def _reset(self, key, **kw):
        self.state, self.p = "idle", {}
        return self._r(key, **kw)

    def _add_raw(self, text):
        self.p["raw"] += " | " + text

    # ---- entry points
    def handle(self, text, detected=None):
        """Rules only (the fast path)."""
        if self.mode == "auto":
            self.lang = detect_language(text, self.lang, detected)
        return self._rules(text)

    async def handle_smart(self, text, detected=None, brain=None, spoken=True):
        """Rules first; the LLM brain only when rules missed or guessed. Returns (reply or None, source, brain_ms).
        Without a brain, or if it fails, the result is exactly the rules result."""
        if self.mode == "auto":
            self.lang = detect_language(text, self.lang, detected)
        if spoken and self._is_junk(text):
            return None, "junk", None
        before = self._snapshot()
        r = self._rules(text)
        if brain is None or not (self.miss or self.soft_miss):
            self._remember(text, r)
            return r, "rules", None
        after = self._snapshot()
        self._restore(before)
        outcome = await brain.interpret(text, self.context())
        if outcome:
            checked = validate(outcome.result, text, len(self.p.get("candidates", [])), self.store.find, self.lang)
            rr = self.apply_brain(checked, text, hard=after[2] or after[4])
            if rr is not None:
                self._remember(text, rr)
                return rr, outcome.provider, outcome.ms
        self._restore(after)
        self._remember(text, r)
        return r, "rules", None

    # ---- brain support
    def _snapshot(self):
        return self.state, copy.deepcopy(self.p), self.miss, self.soft_miss, self.weak_name

    def _restore(self, snap):
        self.state, self.p, self.miss, self.soft_miss, self.weak_name = \
            snap[0], copy.deepcopy(snap[1]), snap[2], snap[3], snap[4]

    def _remember(self, text, reply):
        self.history.append((text, reply["text"]))

    def _is_junk(self, text):
        """Empty, or one meaningless word while idle ('hmm', 'acha'): ignore, never call the LLM."""
        tokens = tokenize(text)
        if not tokens:
            return True
        t = tokens[0]
        return (len(tokens) == 1 and self.state == "idle" and t not in KEYWORDS and not t.isdigit()
                and not self.store.find(t))

    def context(self):
        p = self.p
        pending = {k: p.get(k) for k in ("intent", "name", "amount", "type", "items") if p.get(k)}
        cands = p.get("candidates", []) if self.state == "chooseCustomer" else []
        names = [c["name"] + (f" ({c['note']})" if c["note"] else "") for c in self.store.customers()][:50]
        return BrainContext(stage=self.state, pending=pending, options=[c["note"] or c["name"] for c in cands],
                            customers=names, lang=self.lang, history=list(self.history))

    def apply_brain(self, b, text, hard=True):
        """Feed a validated brain result into the same state machine. None = nothing usable, keep the rules reply."""
        A, st = b.action, self.state
        if A == BrainAction.unclear:
            if not (hard or (b.reply and (b.confidence or 0) >= 0.7)):
                return None  # keep the rules' own question
            return {**self._r("notUnderstood"), **({"text": b.reply} if b.reply else {})}  # never ask about an invented name
        if A in TALK:
            reply = self._r("help" if A == BrainAction.help else "smalltalkFallback")
            if b.reply:
                reply["text"] = b.reply  # sanitized free text, only ever for help / small talk / unclear
            return reply
        if A == BrainAction.confirm:
            return self.tap_confirm(True) if st == "confirming" else None
        if A == BrainAction.cancel:
            return self._reset("cancelled") if st != "idle" else None
        if A == BrainAction.correction:
            return self.tap_amount(b.amount) if st == "confirming" and b.amount else None
        if A == BrainAction.chooseCustomer:
            return self.tap_choose(b.choiceIndex) if st == "chooseCustomer" else None
        if A == BrainAction.queryBalance:
            return self._query(b.customer) if b.customer else None  # balance always comes from the ledger
        if A == BrainAction.queryTotal:
            return self._query(None)
        if A == BrainAction.listOrders:
            return self._pending_list(b.customer)
        if A == BrainAction.setPhone:
            matches = self.store.find(b.customer) if b.customer else []
            if not b.phone or len(matches) != 1:
                return None
            self.p = {"intent": "phone", "name": matches[0]["name"], "customer": matches[0], "phone": b.phone,
                      "raw": text, "type": None, "amount": None, "items": ""}
            return self._confirm()
        name = display_name(b.customer) if b.customer and " " not in b.customer else b.customer
        said = parse(text)  # code-read facts from the same sentence fill what the LLM left out
        amount = b.amount if b.amount is not None else said.amount
        if A in (BrainAction.addCredit, BrainAction.recordPayment):
            if st in ("askName", "askAmount", "askType") and self.p.get("intent") == "txn":
                self.p["name"] = self.p["name"] or name
                self.p["amount"] = self.p["amount"] if self.p["amount"] is not None else amount
                self.p["type"] = self.p["type"] or b.entryType
                self._add_raw(text)
            else:
                self.state = "idle"
                self.p = {"intent": "txn", "name": name, "amount": amount, "type": b.entryType, "items": "", "raw": text}
            self._pick_area(b.area)
            return self._advance()
        if A == BrainAction.addOrder:
            items = self._spoken_items(text, name) or " ".join(x for x in (b.quantity, b.item) if x)
            if st == "askItems" and self.p.get("intent") == "order":
                self.p["items"] = items
                self._add_raw(text)
            else:
                self.state = "idle"
                self.p = {"intent": "order", "name": name, "amount": None, "type": None, "items": items, "raw": text}
                self._pick_area(b.area)
            return self._advance()
        if A == BrainAction.markArrived:
            self.state = "idle"
            self.p = {"intent": "arrival", "name": name, "amount": None, "type": None, "items": b.item or "", "raw": text}
            return self._advance()
        return None

    def _pick_area(self, area):
        """LLM said 'Ramesh (Gandhi Nagar)': go straight to that customer instead of asking which one."""
        if not area or not self.p.get("name"):
            return
        hit = [c for c in self.store.find(self.p["name"]) if name_key(c["note"]) == name_key(area)]
        if len(hit) == 1:
            self.p["customer"] = hit[0]

    def _spoken_items(self, text, name):
        """Goods exactly as spoken, units kept ('ಎರಡು ಕೆಜಿ ಸಕ್ಕರೆ'), without the customer's name (any case ending)."""
        key = name_key(name or "")
        tokens = [t for t in tokenize(extract_phone(text)[1]) if not (key and name_key(t).startswith(key[:max(3, len(key) - 1)]))]
        return extract_items(tokens, None)

    def _rules(self, text):
        self.miss = self.soft_miss = self.weak_name = False
        p = parse(text)
        complete = (p.is_query or (p.name and p.amount and p.txn_type) or (p.order and p.name and p.items)
                    or (p.arrival and p.name))
        if self.state != "idle" and complete:
            self.state, self.p = "idle", {}  # a complete new command replaces the unsaved one
        return getattr(self, "_on_" + self.state)(p, text)

    def tap_confirm(self, yes: bool):
        if self.state != "confirming":
            return self._r("notUnderstood")
        return self._save() if yes else self._reset("cancelled")

    def tap_choose(self, index: int):
        """index == len(candidates) is the 'new customer' chip."""
        cands = self.p.get("candidates", [])
        if self.state != "chooseCustomer" or not 0 <= index <= len(cands) or (index == len(cands) and not self._allow_new()):
            return self._r("notUnderstood")
        if index == len(cands):
            self.state = "askNote"
            return self._r("askNote", name=self.p["name"])
        self.p["customer"] = cands[index]
        return self._advance()

    def tap_amount(self, amount: int):
        if self.state != "confirming" or self.p["intent"] != "txn" or not isinstance(amount, int) or amount <= 0:
            return self._r("notUnderstood")
        self.p["amount"] = amount
        return self._confirm()

    # ---- states
    def _on_idle(self, p, text):
        if p.name and not p.name_strong and not self.store.find(p.name):
            known = next((t for t in p.tokens if is_name_word(t) and self.store.find(t)), None)
            if known:  # "Gandhinagar Ramesh ..." -> the known customer, not the first unknown word
                p.name = display_name(known)
        base = {"name": p.name, "amount": p.amount, "type": p.txn_type, "items": p.items, "raw": text}
        if p.name and not p.name_strong and not self.store.find(p.name):
            self.soft_miss = self.weak_name = True  # name is only a guess (first unknown word) and matches nobody
        if p.amount is not None and p.amount < 10 and not any(t.isdigit() for t in p.tokens):
            self.soft_miss = True  # "dhamki do" -> 'do' (give) is not ₹2
        if p.arrival:
            self.p = {**base, "intent": "arrival"}
            return self._advance()
        if p.order:
            if not p.items and not (p.name and not self._pending_for(p.name)):
                return self._pending_list(p.name)
            self.p = {**base, "intent": "order"}
            return self._advance()
        if p.is_query:
            return self._query(p.name)
        if p.amount is None and p.name is None and p.txn_type is None:
            self.miss = True
            return self._r("notUnderstood")
        if p.phone or p.txn_type is None:  # credit or payment unclear: let the LLM decide before asking
            self.soft_miss = True  # e.g. "Ramesh ka number 98…" or just a name: the LLM may know better
        self.p = {**base, "intent": "txn"}
        return self._advance()

    def _on_askName(self, p, text):
        if p.no and not p.name:
            return self._reset("cancelled")
        if not p.name:
            self.miss = True
            return self._r("askName")
        self.p["name"] = p.name
        self.p["amount"] = self.p["amount"] or p.amount
        self.p["type"] = self.p["type"] or p.txn_type
        self._add_raw(text)
        return self._advance()

    def _on_askAmount(self, p, text):
        if p.amount is None:
            if p.no:
                return self._reset("cancelled")
            self.miss = True
            return self._r("askAmount", name=self.p["name"])
        self.p["amount"] = p.amount
        self.p["type"] = self.p["type"] or p.txn_type
        self._add_raw(text)
        return self._advance()

    def _on_askType(self, p, text):
        if p.txn_type is None:
            if p.no:
                return self._reset("cancelled")
            self.miss = True
            return self._r("askType", name=self.p["name"], amount=self.p["amount"])
        self.p["type"] = p.txn_type
        self._add_raw(text)
        return self._advance()

    def _on_askItems(self, p, text):
        items = p.items or extract_items(p.tokens, None)
        if not items:
            if p.no:
                return self._reset("cancelled")
            self.miss = True
            return self._r("askItems", name=self.p["name"])
        self.p["items"] = items
        self._add_raw(text)
        return self._advance()

    def _on_chooseCustomer(self, p, text):
        cands = self.p["candidates"]
        if p.new and self._allow_new():
            self._add_raw(text)
            return self.tap_choose(len(cands))
        idx = choose_index(text, [c["note"] for c in cands])
        if idx is None:
            if p.no:
                return self._reset("cancelled")
            self.miss = True
            return self._choose_prompt()
        self._add_raw(text)
        return self.tap_choose(idx)

    def _on_askNote(self, p, text):
        """Area for a new customer who shares a name, e.g. 'Gandhi Nagar'. 'skip' leaves it empty."""
        words = [] if p.skip else [w for w in p.tokens if w not in KEYWORDS and not w.isdigit()]
        self.p["note"] = " ".join(display_name(w) for w in words)
        self.p["customer"] = None
        self._add_raw(text)
        return self._advance()

    def _on_confirming(self, p, text):
        if p.correction and self.p["intent"] == "txn":
            self.p["amount"] = p.amount
            self._add_raw(text)
            return self._confirm()
        if p.yes:
            return self._save()
        if p.no:
            return self._reset("cancelled")
        self.miss = True
        return self._confirm()

    # ---- helpers
    def _allow_new(self):
        return self.p.get("intent") != "arrival"

    def _advance(self):
        p = self.p
        if not p["name"]:
            self.state = "askName"
            return self._r("askName")
        if p["intent"] == "txn":
            if p["amount"] is None:
                self.state = "askAmount"
                return self._r("askAmount", name=p["name"])
            if p["type"] is None:
                self.state = "askType"
                return self._r("askType", name=p["name"], amount=p["amount"])
        if p["intent"] == "order" and not p["items"]:
            self.state = "askItems"
            return self._r("askItems", name=p["name"])
        if "customer" not in p:
            matches = self.store.find(p["name"])
            if p["intent"] == "arrival":
                matches = [c for c in matches if self.store.orders("pending", c["id"])]
                if not matches:
                    self.soft_miss = True  # "Lakshmi aayi thi" may just mean she came by, not goods arriving
                    return self._reset("noPendingOrder", name=p["name"])
            if len(matches) >= 2:
                p["candidates"] = matches
                idx = choose_index(p["raw"], [c["note"] for c in matches])
                if idx is None:  # area not said in the sentence: ask which one
                    return self._choose_prompt()
                p["customer"] = matches[idx]
                return self._advance()
            p["customer"] = matches[0] if matches else None
        if p["intent"] == "arrival" and "orders" not in p:
            pending = self.store.orders("pending", p["customer"]["id"])
            words = set(p["items"].split())
            hit = [o for o in pending if words & set(o["items"].lower().split())]
            p["orders"] = hit or pending
        return self._confirm()

    def _choose_prompt(self):
        self.state = "chooseCustomer"
        c = self.p["candidates"]
        notes = [x["note"] or f"#{i + 1}" for i, x in enumerate(c)]
        chips = notes + ([UI[self.lang]["newCustomer"]] if self._allow_new() else [])
        return self._r("chooseCustomer", chips=chips, name=c[0]["name"], count=len(c), options=", ".join(notes))

    def _confirm(self):
        self.state = "confirming"
        p, c = self.p, self.p["customer"]
        name = c["name"] if c else p["name"]
        card = {"name": name, "note": c["note"] if c else p.get("note", ""), "type": p["type"], "isNew": c is None}
        if p["intent"] == "phone":
            return self._r("confirmPhone", card={**card, "type": "phone", "phone": p["phone"]}, name=name, phone=p["phone"])
        if p["intent"] == "order":
            return self._r("confirmOrder", card={**card, "type": "order", "items": p["items"]}, name=name, items=p["items"])
        if p["intent"] == "arrival":
            items = "; ".join(o["items"] for o in p["orders"])
            return self._r("confirmArrived", card={**card, "type": "arrival", "items": items}, name=name, items=items)
        key = "confirmPayment" if p["type"] == "payment" else ("confirmCredit" if c else "confirmCreditNew")
        return self._r(key, card={**card, "amount": p["amount"]}, name=name, amount=p["amount"])

    def _save(self):
        p = self.p
        c = p["customer"] or self.store.add_customer(p["name"], p.get("note", ""))
        self.state, self.p = "idle", {}
        if p["intent"] == "phone":
            self.store.update_customer(c["id"], phone=p["phone"])
            return self._r("phoneSaved", saved=True, name=c["name"])
        if p["intent"] == "order":
            self.store.add_order(c["id"], p["items"], p["raw"], self.lang)
            return self._r("orderSaved", saved=True, name=c["name"], items=p["items"])
        if p["intent"] == "arrival":
            for o in p["orders"]:
                self.store.set_order_status(o["id"], "arrived")
            if not c["phone"]:
                return self._r("arrivedNoPhone", saved=True, name=c["name"])
            return {**self._r("arrivedSaved", saved=True, name=c["name"]), "notify": c["id"]}
        self.store.add_entry(c["id"], p["type"], p["amount"], p["raw"], self.lang)
        return self._r("saved", saved=True, name=c["name"], balance=self.store.balance(c["id"]))

    def _query(self, name):
        if not name:
            total = sum(b for b in self.store.balances().values() if b > 0)
            return self._r("totalDue", amount=total)
        matches = self.store.find(name)
        if not matches:
            self.soft_miss = True  # 'Lakshmi didi ka hisaab' -> rules took 'didi' as the name
            return self._r("customerNotFound", name=name)
        if len(matches) == 1:
            return self._r("balanceIs", name=matches[0]["name"], balance=matches[0]["balance"])
        lst = ", ".join(f'{c["note"] or c["name"]} {c["balance"]}' for c in matches)
        return self._r("balanceMulti", name=matches[0]["name"], list=lst)

    def _pending_for(self, name):
        ids = {c["id"] for c in self.store.find(name)}
        return [o for o in self.store.orders("pending") if o["customer_id"] in ids]

    def _pending_list(self, name=None):
        ids = {c["id"] for c in self.store.find(name)} if name else None
        orders = [o for o in self.store.orders("pending") if ids is None or o["customer_id"] in ids]
        if not orders:
            return self._r("noPendingOrder", name=name) if name else self._r("noPendingOrders")
        return self._r("pendingList", list=pending_text(orders))


def pending_text(orders):
    return "; ".join(f'{o["customer"]}{" (" + o["note"] + ")" if o["note"] else ""}: {o["items"]}' for o in orders)
