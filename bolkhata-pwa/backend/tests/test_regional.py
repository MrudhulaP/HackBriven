"""Fixes from the Kannada/Telugu/Tamil spoken-conversation run (real Gnani transcripts)."""
import asyncio
import json

import httpx
import pytest

from app.ai.llm_brain import LlmBrain
from app.ai.llm_client import LlmClient
from app.brain.validator import sanitize_reply
from app.dialogue import Conversation
from app.gnani import stt_language
from app.lang import detect_language
from app.nlu import parse


@pytest.mark.parametrize("text,amount", [
    ("ಇಲ್ಲ, ನಾನೂರ ಐವತ್ತು.", 450),
    ("இல்லை, நானூற்று ஐம்பது.", 450),
    ("కాదు, నాలుగు వందల యాభై.", 450),
    ("ನೂರೈವತ್ತು ರೂಪಾಯಿ ಸಾಮಾನು", 150),
    ("నూట యాభై రూపాయల సామాను", 150),
    ("நூற்றம்பது ரூபாய் சாமான்", 150),
    ("சுரேஷ் ஐந்நூறு ரூபாய் கடன் வாங்கினார்.", 500),
    ("அண்ணா, முந்நூறு ரூபாய்க்கு சாமான் வேணும்", 300),
    ("ಮುನ್ನೂರ ಐವತ್ತು", 350),
])
def test_regional_number_forms(text, amount):
    assert parse(text).amount == amount


def test_tamil_450_correction_is_not_a_new_customer(store):
    c = Conversation(store)
    c.handle("சுரேஷ் ஐந்நூறு ரூபாய் கடன் வாங்கினார்.")
    r = c.handle("இல்லை, நானூற்று ஐம்பது.")
    assert r["card"]["amount"] == 450 and r["card"]["name"] == "சுரேஷ்"
    assert c.handle("ஆமாம்")["saved"] and not store.find("நானூற்று")


@pytest.mark.parametrize("word", ["ಲಕ್ಷ್ಮಿಗೆ", "లక్ష్మికి", "லக்ஷ்மிக்கு"])
def test_case_endings_find_existing_customer(store, word):
    assert [c["name"] for c in store.find(word)] == ["Lakshmi"]


def test_order_to_lakshmi_with_case_ending_rules_only(store):
    r = Conversation(store).handle("ಲಕ್ಷ್ಮಿಗೆ ಎರಡು ಕೆಜಿ ಸಕ್ಕರೆ ಆರ್ಡರ್ ಮಾಡಿ.")
    assert r["key"] == "confirmOrder" and r["card"]["name"] == "Lakshmi" and not r["card"]["isNew"]


@pytest.mark.parametrize("text", ["அண்ணா, இன்றைக்கு காசு இல்லை, நாளைக்கு தரேன்.",
                                  "ಅಣ್ಣಾ, ಇವತ್ತು ದುಡ್ಡಿಲ್ಲ, ನಾಳೆ ಕೊಡ್ತೀನಿ.", "అన్నా, ఈరోజు డబ్బులు లేవు, రేపు ఇస్తాను."])
def test_address_words_are_not_names(text):
    assert parse(text).name not in ("அண்ணா", "ಅಣ್ಣಾ", "అన్నా")


@pytest.mark.parametrize("text,yes,no", [("ஆமாம்", True, False), ("சரி", True, False), ("ಸರಿ", True, False),
                                         ("సరే", True, False), ("ಬೇಡ, ಕ್ಯಾನ್ಸಲ್ ಮಾಡಿ.", False, True),
                                         ("వద్దు, క్యాన్సిల్ చేయండి.", False, True), ("வேண்டாம், கேன்சல் பண்ணுங்கள்.", False, True)])
def test_regional_yes_no(text, yes, no):
    p = parse(text)
    assert (p.yes, p.no) == (yes, no)


def test_one_native_script_word_switches_language():
    assert detect_language("ஆமாம்", "te") == "ta" and detect_language("ಹೌದು", "te") == "kn"
    assert detect_language("हाँ", "en") == "en" and detect_language("haan", "kn") == "kn"  # Hindi/Latin "yes" keeps


def test_mixed_script_llm_reply_rejected():
    assert sanitize_reply("நான் உங்களுக்கு உधார் பதிவு செய்ய உதவுகிறேன்.", "ta") is None
    assert sanitize_reply("நான் Lakshmi கணக்கை பார்க்கிறேன்.", "ta") is not None


@pytest.mark.parametrize("mode,regional,code", [("auto", "", "indic-auto"), ("auto", "kn", "hi-IN,en-IN,kn-IN"),
                                                ("ta", "kn", "ta-IN"), ("auto", "xx", "indic-auto")])
def test_auto_language_with_regional_setting(mode, regional, code):
    assert stt_language(mode, regional) == code


def test_regional_setting_validated(store):
    assert store.save_settings({"regional_language": "te"})["regional_language"] == "te"
    with pytest.raises(ValueError):
        store.save_settings({"regional_language": "fr"})


class OneAnswer(LlmClient):
    name = "groq"

    def __init__(self, answer):
        super().__init__("k", "m", client=httpx.AsyncClient())
        self.answer = answer

    async def complete_json(self, system, user, timeout):
        return json.dumps(self.answer, ensure_ascii=False)


def smart(c, text, answer):
    return asyncio.run(c.handle_smart(text, brain=LlmBrain([OneAnswer(answer)])))


def test_llm_name_with_area_picks_that_customer(store):
    text = "ಅಯ್ಯೋ, ಆ ರಮೇಶ್ ಗಾಂಧಿನಗರದವರು ಬಂದಿದ್ದರು, ನೂರೈವತ್ತು ರೂಪಾಯಿ ಸಾಮಾನು ತಗೊಂಡು ಹೋದರು, ಬರ್ಕೊಳ್ಳಿ."
    r, source, _ = smart(Conversation(store), text, {"action": "addCredit", "customer": "Ramesh (Gandhi Nagar)",
                                                     "amount": 150, "entryType": "credit", "confidence": 0.9})
    assert r["state"] == "confirming"  # rules or LLM, either way the right customer and amount
    assert r["card"]["note"] == "Gandhi Nagar" and r["card"]["amount"] == 150


def test_llm_missing_amount_filled_from_sentence(store):
    text = "ಸುರೇಶ್ ಐನೂರು ರೂಪಾಯಿ ಸಾಲ ತಗೊಂಡ್ರು."
    r, source, _ = smart(Conversation(store), text, {"action": "addCredit", "customer": "ಸುರೇಶ್", "amount": None,
                                                     "entryType": "credit", "confidence": 0.9})
    assert r["card"]["amount"] == 500


def test_order_items_keep_spoken_words_and_units(store):
    text = "ಲಕ್ಷ್ಮಿಗೆ ಎರಡು ಕೆಜಿ ಸಕ್ಕರೆ ಆರ್ಡರ್ ಮಾಡಿ."
    r, _, _ = smart(Conversation(store), "ಆ " + text, {"action": "addOrder", "customer": "Lakshmi", "item": "sugar",
                                                       "quantity": "2 kg", "confidence": 0.9})
    assert r["card"]["items"] == "ಎರಡು ಕೆಜಿ ಸಕ್ಕರೆ" and r["card"]["name"] == "Lakshmi"


@pytest.mark.parametrize("text,amount", [("ಇಲ್ಲ, ನಾನ್ನೂರ ಐವತ್ತು.", 450), ("ನಾನ್ನೂರು", 400), ("இருநூறு", 200)])
def test_number_spelling_variants(text, amount):
    assert parse(text).amount == amount


def test_garbled_area_does_not_pick_wrong_customer(store):
    c = Conversation(store)
    c.handle("ರಮೇಶ್ ಮುನ್ನೂರು ರೂಪಾಯಿ ಸಾಲ ತಗೊಂಡ್ರು.")
    assert c.handle("ತೇಜ್ ನೂರ್ ಅವರು.")["state"] == "chooseCustomer"  # was wrongly Gandhi Nagar


@pytest.mark.parametrize("text,note", [
    ("ಅಯ್ಯೋ, ಆ ರಮೇಶ್ ಗಾಂಧಿನಗರದವರು ಬಂದಿದ್ದರು, ನೂರೈವತ್ತು ರೂಪಾಯಿ ಸಾಲ ತಗೊಂಡ್ರು", "Gandhi Nagar"),
    ("గాంధీనగర్ రమేష్ నూట యాభై రూపాయలు అప్పు తీసుకున్నారు", "Gandhi Nagar"),
    ("காந்தி நகர் ரமேஷ் நூற்றம்பது ரூபாய் கடன் வாங்கினார்", "Gandhi Nagar"),
])
def test_area_in_same_sentence_picks_customer(store, text, note):
    r = Conversation(store).handle(text)
    assert r["state"] == "confirming" and r["card"]["note"] == note and r["card"]["amount"] == 150


def test_customer_chatter_never_asks_about_invented_name(store):
    for text in ["அண்ணா, இன்னைக்கு காசு இல்லை, நாளைக்கு தரேன்.", "అన్నా, ఈరోజు డబ్బులు లేవు, రేపు ఇస్తాను."]:
        r, _, _ = smart(Conversation(store), text, {"action": "unclear", "reply": None, "confidence": 0.3})
        assert r["key"] == "notUnderstood"
    assert Conversation(store).handle("అన్నా, ఈరోజు డబ్బులు లేవు, రేపు ఇస్తాను.")["key"] == "notUnderstood"


def test_llm_latin_name_matches_tamil_spoken_name(store):
    text = "சுரேஷ் ஐந்நூறு ரூபாய் கடன் வாங்கினார்."
    r, source, _ = smart(Conversation(store), text, {"action": "addCredit", "customer": "Suresh", "amount": 200,
                                                     "entryType": "credit", "confidence": 0.9})
    assert source == "groq" and r["card"]["name"] == "Suresh" and r["card"]["amount"] == 500  # LLM's 200 rejected


@pytest.mark.parametrize("text,amount", [("இல்லை நானூற்றி ஐம்பது", 450), ("நூற்றி ஐம்பது ரூபாய்", 150),
                                         ("ಮುನ್ನೂರು", 300), ("ఐదు వందల", 500), ("ಎರಡು", 2), ("இரண்டு கிலோ", 2),
                                         ("రమేష్ బాకీ ఎంత", None)])  # 'how much' is not 8
def test_number_words_ignore_final_vowel(text, amount):
    assert parse(text).amount == amount


def test_noisy_shop_makes_gnani_vad_stricter(store):
    from app.gnani import stt_headers
    assert "x-vad-threshold" not in stt_headers("k", "auto")
    h = stt_headers("k", "auto", noisy=True)
    assert h["x-vad-threshold"] == "0.85" and h["x-min-speech-ms"] == "250" and h["x-min-silence-ms"] == "400"
    assert store.save_settings({"noisy_shop": "on"})["noisy_shop"] == "on"
    with pytest.raises(ValueError):
        store.save_settings({"noisy_shop": "loud"})
