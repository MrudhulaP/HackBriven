"""Shapes shared by the LLM brain. No network code here."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class BrainAction(str, Enum):
    addCredit = "addCredit"
    recordPayment = "recordPayment"
    queryBalance = "queryBalance"
    queryTotal = "queryTotal"
    correction = "correction"
    confirm = "confirm"
    cancel = "cancel"
    undo = "undo"
    queryCollections = "queryCollections"
    topDebtor = "topDebtor"
    chooseCustomer = "chooseCustomer"
    addOrder = "addOrder"
    markArrived = "markArrived"
    listOrders = "listOrders"
    setPhone = "setPhone"
    smalltalk = "smalltalk"
    help = "help"
    unclear = "unclear"


TALK = {BrainAction.smalltalk, BrainAction.help, BrainAction.unclear}


@dataclass
class BrainContext:
    """What the LLM may see. Never balances or phone numbers."""
    stage: str
    pending: dict
    options: list[str]
    customers: list[str]  # names (+ area), at most 50
    lang: str
    history: list[tuple[str, str]] = field(default_factory=list)  # last 3 (shopkeeper, app)


@dataclass
class BrainResult:
    action: BrainAction
    customer: str | None = None
    amount: int | None = None
    entryType: str | None = None
    choiceIndex: int | None = None
    item: str | None = None
    quantity: str | None = None
    phone: str | None = None
    reply: str | None = None
    confidence: float | None = None
    area: str | None = None  # from "Ramesh (Gandhi Nagar)": picks that exact customer


@dataclass
class BrainOutcome:
    result: BrainResult
    provider: str  # "groq" | "gemini"
    ms: int


class Brain(Protocol):
    async def interpret(self, transcript: str, ctx: BrainContext) -> BrainOutcome | None: ...
