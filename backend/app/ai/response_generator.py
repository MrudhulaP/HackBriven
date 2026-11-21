from decimal import Decimal
from typing import List, Dict, Any, Optional

class ResponseGenerator:
    @staticmethod
    def generate_transaction_confirmation_response(
        customer_name: str,
        new_balance: Decimal,
        events_summary: List[Dict[str, Any]],
        language: str = "hi"
    ) -> Dict[str, str]:
        """
        Generate spoken and text responses across English, Hindi, Kannada, Telugu, and Tamil.
        Preserves exact prompt acceptance test requirement:
        'Ramesh ka ₹140 baaki hai. ₹340 ka udhaar aur kal ₹200 ka payment record kar diya.'
        """
        bal_str = f"₹{new_balance}"
        
        hi_parts = []
        kn_parts = []
        te_parts = []
        ta_parts = []
        en_parts = []

        for ev in events_summary:
            amt = f"₹{ev.get('amount')}"
            date_lbl = str(ev.get('date_label', 'Today')).lower()
            tx_type = ev.get('type')

            if tx_type == "CREDIT":
                d_hi = "kal " if date_lbl == "yesterday" else ""
                d_kn = "ninne " if date_lbl == "yesterday" else ""
                d_te = "ninna " if date_lbl == "yesterday" else ""
                d_ta = "nerru " if date_lbl == "yesterday" else ""
                d_en = "yesterday's " if date_lbl == "yesterday" else ""

                hi_parts.append(f"{d_hi}{amt} ka udhaar")
                kn_parts.append(f"{d_kn}{amt} saala")
                te_parts.append(f"{d_te}{amt} appu")
                ta_parts.append(f"{d_ta}{amt} kadan")
                en_parts.append(f"{d_en}{amt} credit")
            else:
                d_hi = "kal " if date_lbl == "yesterday" else ""
                d_kn = "ninne " if date_lbl == "yesterday" else ""
                d_te = "ninna " if date_lbl == "yesterday" else ""
                d_ta = "nerru " if date_lbl == "yesterday" else ""
                d_en = "yesterday's " if date_lbl == "yesterday" else ""

                hi_parts.append(f"{d_hi}{amt} ka payment")
                kn_parts.append(f"{d_kn}{amt} payment")
                te_parts.append(f"{d_te}{amt} chellimpu")
                ta_parts.append(f"{d_ta}{amt} varavu")
                en_parts.append(f"{d_en}{amt} payment")

        hi_ev_str = " aur ".join(hi_parts)
        kn_ev_str = " mattu ".join(kn_parts)
        te_ev_str = " mariyu ".join(te_parts)
        ta_ev_str = " matrum ".join(ta_parts)
        en_ev_str = " and ".join(en_parts)

        # Handle advance / negative balance
        if new_balance < Decimal("0"):
            abs_bal = f"₹{abs(new_balance)}"
            spoken_hi = f"{customer_name} ka {abs_bal} advance jama hai. {hi_ev_str} record kar diya."
            spoken_kn = f"{customer_name} avara {abs_bal} advance ide. {kn_ev_str} record maadalaagide."
            spoken_te = f"{customer_name} gari {abs_bal} advance undi. {te_ev_str} record chesamu."
            spoken_ta = f"{customer_name} avargalukku {abs_bal} advance ullathu. {ta_ev_str} pathivu seithu vittom."
            spoken_en = f"{customer_name} has an advance credit balance of {abs_bal}. Recorded {en_ev_str}."
        else:
            spoken_hi = f"{customer_name} ka {bal_str} baaki hai. {hi_ev_str} record kar diya."
            spoken_kn = f"{customer_name} ge {bal_str} baaki ide. {kn_ev_str} record maadalaagide."
            spoken_te = f"{customer_name} gari baaki {bal_str} undi. {te_ev_str} record chesamu."
            spoken_ta = f"{customer_name} avargalukku {bal_str} baki ullathu. {ta_ev_str} pathivu seithu vittom."
            spoken_en = f"{customer_name}'s outstanding balance is {bal_str}. Recorded {en_ev_str}."

        if language == "kn":
            return {"spoken": spoken_kn, "text": spoken_kn}
        elif language == "te":
            return {"spoken": spoken_te, "text": spoken_te}
        elif language == "ta":
            return {"spoken": spoken_ta, "text": spoken_ta}
        elif language == "en":
            return {"spoken": spoken_en, "text": spoken_en}
        else:
            return {"spoken": spoken_hi, "text": spoken_hi}

    @staticmethod
    def generate_balance_response(customer_name: str, balance: Decimal, language: str = "hi") -> Dict[str, str]:
        bal_str = f"₹{balance}"
        if balance < Decimal("0"):
            abs_bal = f"₹{abs(balance)}"
            hi = f"{customer_name} ka {abs_bal} advance jama hai."
            kn = f"{customer_name} avara {abs_bal} advance ide."
            te = f"{customer_name} gari {abs_bal} advance undi."
            ta = f"{customer_name} avargalukku {abs_bal} advance ullathu."
            en = f"{customer_name} has an advance payment of {abs_bal}."
        elif balance == Decimal("0"):
            hi = f"{customer_name} ka koi hisaab baaki nahi hai (₹0 balance)."
            kn = f"{customer_name} avara yavude baaki illa (₹0 balance)."
            te = f"{customer_name} gariki emi baaki ledu (₹0 balance)."
            ta = f"{customer_name} avargalukku entha bakiyum illai (₹0 balance)."
            en = f"{customer_name} has no pending balance (₹0)."
        else:
            hi = f"{customer_name} ka {bal_str} baaki hai."
            kn = f"{customer_name} ge {bal_str} baaki ide."
            te = f"{customer_name} gariki {bal_str} baaki undi."
            ta = f"{customer_name} avargalukku {bal_str} baki ullathu."
            en = f"{customer_name} owes {bal_str}."

        if language == "kn":
            return {"spoken": kn, "text": kn}
        elif language == "te":
            return {"spoken": te, "text": te}
        elif language == "ta":
            return {"spoken": ta, "text": ta}
        elif language == "en":
            return {"spoken": en, "text": en}
        return {"spoken": hi, "text": hi}

    @staticmethod
    def generate_daily_summary_response(
        total_credit: Decimal,
        total_payment: Decimal,
        tx_count: int,
        language: str = "hi"
    ) -> Dict[str, str]:
        hi = f"Aaj aapne ₹{total_payment} jama kiye aur ₹{total_credit} ka udhaar diya. Kul {tx_count} transactions huye."
        kn = f"Ivattu neevu ₹{total_payment} collection maadirikri mattu ₹{total_credit} saala kottiri. Otu {tx_count} transactions aagive."
        te = f"Eroju meeru ₹{total_payment} vasoolu chesaru mariyu ₹{total_credit} appu icharu. Motham {tx_count} transactions jarigayi."
        ta = f"Inru neengal ₹{total_payment} vasool seithirgal matrum ₹{total_credit} kadan kodutheergal. Moththam {tx_count} parivarthanaigal."
        en = f"Today you collected ₹{total_payment} and gave ₹{total_credit} in credit across {tx_count} transactions."

        if language == "kn":
            return {"spoken": kn, "text": kn}
        elif language == "te":
            return {"spoken": te, "text": te}
        elif language == "ta":
            return {"spoken": ta, "text": ta}
        elif language == "en":
            return {"spoken": en, "text": en}
        return {"spoken": hi, "text": hi}

    @staticmethod
    def generate_weekly_summary_response(
        total_payment: Decimal,
        total_credit: Decimal,
        tx_count: int,
        language: str = "hi"
    ) -> Dict[str, str]:
        hi = f"Iss hafte aapne kul ₹{total_payment} ki vasooli ki aur ₹{total_credit} ka udhaar diya. Kul {tx_count} transactions huye."
        kn = f"Ee vaara neevu otu ₹{total_payment} collection maadirikri mattu ₹{total_credit} saala kottiri. Otu {tx_count} transactions aagive."
        te = f"Ee varamlo meeru motham ₹{total_payment} vasoolu chesaru mariyu ₹{total_credit} appu icharu. Motham {tx_count} transactions."
        ta = f"Intha vaaram neengal moththam ₹{total_payment} vasool seithirgal matrum ₹{total_credit} kadan kodutheergal. Moththam {tx_count} parivarthanaigal."
        en = f"This week you collected ₹{total_payment} and gave ₹{total_credit} in credit across {tx_count} transactions."

        if language == "kn":
            return {"spoken": kn, "text": kn}
        elif language == "te":
            return {"spoken": te, "text": te}
        elif language == "ta":
            return {"spoken": ta, "text": ta}
        elif language == "en":
            return {"spoken": en, "text": en}
        return {"spoken": hi, "text": hi}

    @staticmethod
    def generate_top_debtor_response(
        customer_name: str,
        balance: Decimal,
        language: str = "hi"
    ) -> Dict[str, str]:
        hi = f"Sabse zyada udhaar {customer_name} ka hai, kul ₹{balance} baaki hai."
        kn = f"Ati hecchu saala {customer_name} avardagi ide, otu ₹{balance} baaki ide."
        te = f"Andarikante ekkuva baaki {customer_name} gari daggara undi, motham ₹{balance} baaki."
        ta = f"Ellarilum athiga baki {customer_name} avargaludaiyathu, moththam ₹{balance} baki ullathu."
        en = f"{customer_name} owes the most money, with an outstanding balance of ₹{balance}."

        if language == "kn":
            return {"spoken": kn, "text": kn}
        elif language == "te":
            return {"spoken": te, "text": te}
        elif language == "ta":
            return {"spoken": ta, "text": ta}
        elif language == "en":
            return {"spoken": en, "text": en}
        return {"spoken": hi, "text": hi}

    @staticmethod
    def generate_clarification_prompt(
        kind: str,
        customer_name: Optional[str] = None,
        amount: Optional[Decimal] = None,
        language: str = "hi"
    ) -> str:
        name = customer_name or "customer"
        amt_str = f"₹{amount}" if amount else "amount"

        if kind == "AMBIGUOUS_TYPE":
            if language == "kn":
                return f"{name} ge {amt_str} saala kottira athava payment bantha?"
            elif language == "te":
                return f"{name} gariki {amt_str} appu ichara leka payment vachinda?"
            elif language == "ta":
                return f"{name} avargalukku {amt_str} kadan kodutheergala allathu varavu vanthutha?"
            elif language == "en":
                return f"Is {amt_str} credit given to {name} or a payment received from {name}?"
            else:
                return f"Kya {amt_str} {name} ko udhaar diya hai ya unse payment mila hai?"

        elif kind == "MISSING_AMOUNT":
            if language == "kn":
                return f"{name} eshtu roopaayi kottaru athava thagondaru?"
            elif language == "te":
                return f"{name} entha mottham icharu leka theesukunnaru?"
            elif language == "ta":
                return f"{name} evalavu thogai koduthar allathu vanginar?"
            elif language == "en":
                return f"How much did {name} pay or take?"
            else:
                return f"{name} ne kitne rupaye diye ya liye?"

        return f"Please clarify the transaction details for {name}."
