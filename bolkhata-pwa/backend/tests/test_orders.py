"""Judges' additions: auto-add customers, same-name new customer, back-orders, evening reminder."""
import pytest
from fastapi.testclient import TestClient

from app import main
from app.dialogue import Conversation
from app.nlu import parse


@pytest.mark.parametrize("text,name,items", [
    ("Ramesh ke liye 5 kilo cheeni order karo", "Ramesh", "5 kilo cheeni"),
    ("Sita ko 2 packet Maggi baad mein deni hai", "Sita", "2 packet maggi"),
    ("रमेश के लिए 5 किलो चीनी ऑर्डर", "रमेश", "5 किलो चीनी"),
    ("Ramesh needs 5 kg sugar, order it", "Ramesh", "5 kg sugar"),
    ("5 kg sugar for Ramesh, pending", "Ramesh", "5 kg sugar"),
    ("ರಮೇಶ್ ಅವರಿಗೆ 5 ಕೆಜಿ ಸಕ್ಕರೆ ಆರ್ಡರ್", "ರಮೇಶ್", "5 ಕೆಜಿ ಸಕ್ಕರೆ"),
])
def test_parse_order(text, name, items):
    p = parse(text)
    assert (p.order, p.name, p.items, p.amount, p.txn_type) == (True, name, items, None, None)


@pytest.mark.parametrize("text,name", [
    ("Ramesh ka saamaan aa gaya", "Ramesh"),
    ("रमेश का सामान आ गया", "रमेश"),
    ("Lakshmi's sugar arrived", "Lakshmi"),
])
def test_parse_arrival(text, name):
    p = parse(text)
    assert p.arrival and p.name == name and not p.order and p.txn_type is None


def test_order_flow_new_customer_auto_added(store):
    c = Conversation(store)
    r = c.handle("Sita ko 2 packet Maggi baad mein deni hai")
    assert r["key"] == "confirmOrder" and r["card"]["type"] == "order" and r["card"]["isNew"]
    assert not store.find("Sita") and not store.orders()  # nothing saved before confirm
    r = c.handle("haan")
    assert r["saved"] and r["key"] == "orderSaved"
    sita = store.find("Sita")
    assert len(sita) == 1 and sita[0]["phone"] is None and sita[0]["last_visit"] is not None
    o = store.orders("pending")
    assert len(o) == 1 and o[0]["items"] == "2 packet maggi"


def test_order_ask_items(store):
    c = Conversation(store)
    r = c.handle("Lakshmi ke liye order likho")
    assert r["key"] == "askItems"
    r = c.handle("5 kilo cheeni")
    assert r["key"] == "confirmOrder" and r["card"]["items"] == "5 kilo cheeni"
    c.handle("haan")
    r = c.handle("Lakshmi ka order")  # something pending now: list it
    assert r["key"] == "pendingList" and "5 kilo cheeni" in r["text"]


def test_pending_list_and_arrival_flow(store):
    c = Conversation(store)
    c.handle("Lakshmi ke liye 5 kilo cheeni order karo")
    c.handle("haan")
    assert "Lakshmi: 5 kilo cheeni" in c.handle("pending orders")["text"]
    r = c.handle("Lakshmi ka saamaan aa gaya")
    assert r["key"] == "confirmArrived" and "5 kilo cheeni" in r["card"]["items"]
    assert store.orders("pending")  # not marked before confirm
    r = c.handle("haan")
    assert r["key"] == "arrivedSaved" and r["notify"] == store.find("Lakshmi")[0]["id"]
    assert not store.orders("pending") and len(store.orders("arrived")) == 1
    assert c.handle("pending orders")["key"] == "noPendingOrders"


def test_arrival_without_order(store):
    assert Conversation(store).handle("Lakshmi ka saamaan aa gaya")["key"] == "noPendingOrder"


def test_arrival_without_phone(store):
    c = Conversation(store)
    c.handle("Sita ko 2 packet Maggi baad mein deni hai")
    c.handle("haan")
    c.handle("Sita ka saamaan aa gaya")
    assert c.handle("haan")["key"] == "arrivedNoPhone"


def test_new_ramesh_with_area(store):
    c = Conversation(store)
    r = c.handle("Ramesh ne 80 udhaar liya")
    assert r["options"][-1] == "नया ग्राहक" and len(r["options"]) == 3
    r = c.handle("naya")
    assert r["key"] == "askNote"
    r = c.handle("Bus Stand")
    assert r["card"]["isNew"] and r["card"]["note"] == "Bus Stand"
    c.handle("haan")
    rs = store.find("Ramesh")
    assert len(rs) == 3 and any(x["note"] == "Bus Stand" and x["balance"] == 80 for x in rs)


def test_new_customer_chip_tap_and_skip(store):
    c = Conversation(store)
    c.handle("Ramesh ne 80 udhaar liya")
    assert c.tap_choose(2)["key"] == "askNote"
    r = c.handle("skip")
    assert r["card"]["isNew"] and r["card"]["note"] == ""


def test_known_customer_updates_not_duplicates(store):
    c = Conversation(store)
    c.handle("Lakshmi ne 30 udhaar liya")
    c.handle("haan")
    assert len(store.find("Lakshmi")) == 1 and store.find("Lakshmi")[0]["balance"] == 150


@pytest.fixture
def client(db):
    with TestClient(main.create_app(db)) as c:
        yield c


def test_orders_api_and_whatsapp(client):
    app_store = client.app.state.store
    lak = app_store.find("Lakshmi")[0]
    oid = app_store.add_order(lak["id"], "5 kilo cheeni", "test", "hi")
    assert client.get("/api/orders").json()[0]["items"] == "5 kilo cheeni"
    assert client.get(f"/api/customers/{lak['id']}/arrived-message").status_code == 422  # still pending
    assert client.put(f"/api/orders/{oid}", json={"status": "arrived"}).json()["ok"]
    url = client.get(f"/api/customers/{lak['id']}/arrived-message?lang=en").json()["url"]
    assert url.startswith("https://wa.me/919000000003?text=") and "5%20kilo%20cheeni" in url
    client.put(f"/api/orders/{oid}", json={"status": "closed"})
    assert client.get("/api/orders").json() == []
    assert client.put(f"/api/orders/{oid}", json={"status": "lost"}).status_code == 422


def test_evening_summary(client):
    app_store = client.app.state.store
    sita = app_store.add_customer("Sita")
    app_store.add_order(sita["id"], "2 packet maggi", "test", "hi")
    e = client.get("/api/evening?lang=en").json()
    assert [m["name"] for m in e["missing"]] == ["Sita"]
    assert "Sita" in e["text"] and "2 packet maggi" in e["text"]


def test_customer_edit_and_closing_time(client):
    cid = client.get("/api/customers").json()[2]["id"]
    c = client.put(f"/api/customers/{cid}", json={"phone": "98765 43210", "note": "Market"}).json()
    assert c["phone"] == "9876543210" and c["note"] == "Market"
    assert client.put(f"/api/customers/{cid}", json={"phone": "123"}).status_code == 422
    assert client.put("/api/settings", json={"closing_time": "21:30"}).json()["closing_time"] == "21:30"
    assert client.put("/api/settings", json={"closing_time": "9pm"}).status_code == 422


# Real Gnani transcripts of spoken order commands.
@pytest.mark.parametrize("text,order,name,items", [
    ("पेंडिंग ऑर्डर्स बताओ।", True, None, ""),
    ("सीता को तो पैकेट माँ के बाद में देनी है।", True, "सीता", "तो पैकेट माँ"),
    ("लक्ष्मी के लिए पाँच किलो चीनी ऑर्डर करो।", True, "लक्ष्मी", "पाँच किलो चीनी"),
])
def test_real_order_transcripts(text, order, name, items):
    p = parse(text)
    assert (p.order, p.name, p.items) == (order, name, items)


def test_pending_orders_spoken_lists_them(store):
    c = Conversation(store)
    c.handle("Lakshmi ke liye 5 kilo cheeni order karo")
    c.handle("haan")
    assert c.handle("पेंडिंग ऑर्डर्स बताओ।")["key"] == "pendingList"


def test_english_order_replies_in_english(store):
    r = Conversation(store).handle("Ravi made two kg rice, order it.")
    assert r["lang"] == "en" and r["key"] == "confirmOrder"
