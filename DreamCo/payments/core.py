from dataclasses import dataclass

@dataclass
class PaymentResult:
    success: bool
    transaction_id: str = ""
    error: str = ""

class PaymentProcessor:
    def charge(self, amount, currency="USD"):
        raise NotImplementedError