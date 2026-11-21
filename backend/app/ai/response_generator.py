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
        Generate spoken and text responses in the chosen language.
        Matches exact prompt requirement:
        'Ramesh ka ₹140 baaki hai. ₹340 ka udhaar aur kal ₹200 ka payment record kar diya.'
        """
        bal_str = f"₹{new_balance}"
        
        # Build event details
        # e.g. "₹340 ka udhaar" and "kal ₹200 ka payment"
        hi_parts = []
        kn_parts = []
        en_parts = []

        for ev in events_summary:
            amt = f"₹{ev.get('amount')}"
            date_lbl = ev.get('date_label', 'Today').lower()
            tx_type = ev.get('type')

            if tx_type == "CREDIT":
                date_prefix_hi = "kal " if date_lbl == "yesterday" else ""
                date_prefix_kn = "ninne " if date_lbl == "yesterday" else ""
                date_prefix_en = "yesterday's " if date_lbl == "yesterday" else ""
                hi_parts.append(f"{date_prefix_hi}{amt} ka udhaar")
                kn_parts.append(f"{date_prefix_kn}{amt} saala")
                en_parts.append(f"{date_prefix_en}{amt} credit")
            else:
                date_prefix_hi = "kal " if date_lbl == "yesterday" else ""
                date_prefix_kn = "ninne " if date_lbl == "yesterday" else ""
                date_prefix_en = "yesterday's " if date_lbl == "yesterday" else ""
                hi_parts.append(f"{date_prefix_hi}{amt} ka payment")
                kn_parts.append(f"{date_prefix_kn}{amt} payment")
                en_parts.append(f"{date_prefix_en}{amt} payment")

        hi_ev_str = " aur ".join(hi_parts)
        kn_ev_str = " mattu ".join(kn_parts)
        en_ev_str = " and ".join(en_parts)

        # Handle advance / negative balance
        if new_balance < Decimal("0"):
            abs_bal = f"₹{abs(new_balance)}"
            spoken_hi = f"{customer_name} ka {abs_bal} advance jama hai. {hi_ev_str} record kar diya."
            spoken_kn = f"{customer_name} avara {abs_bal} advance ide. {kn_ev_str} record maadalaagide."
            spoken_en = f"{customer_name} has an advance credit balance of {abs_bal}. Recorded {en_ev_str}."
        else:
            spoken_hi = f"{customer_name} ka {bal_str} baaki hai. {hi_ev_str} record kar diya."
            spoken_kn = f"{customer_name} ge {bal_str} baaki ide. {kn_ev_str} record maadalaagide."
            spoken_en = f"{customer_name}'s outstanding balance is {bal_str}. Recorded {en_ev_str}."

        if language == "kn":
            return {"spoken": spoken_kn, "text": spoken_kn}
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
            en = f"{customer_name} has an advance payment of {abs_bal}."
        elif balance == Decimal("0"):
            hi = f"{customer_name} ka koi hisaab baaki nahi hai (₹0 balance)."
            kn = f"{customer_name} avara yavude baaki illa (₹0 balance)."
            en = f"{customer_name} has no pending balance (₹0)."
        else:
            hi = f"{customer_name} ka {bal_str} baaki hai."
            kn = f"{customer_name} ge {bal_str} baaki ide."
            en = f"{customer_name} owes {bal_str}."

        if language == "kn":
            return {"spoken": kn, "text": kn}
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
        en = f"Today you collected ₹{total_payment} and gave ₹{total_credit} in credit across {tx_count} transactions."

        if language == "kn":
            return {"spoken": kn, "text": kn}
        elif language == "en":
            return {"spoken": en, "text": en}
        return {"spoken": hi, "text": hi}
