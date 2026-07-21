"""ReceiptUploadScreen — receipt OCR scanning and cashback matching."""


class ReceiptUploadScreen:
    SCREEN_ID = "receipt_upload"

    def __init__(self, matched_items=None, total_cashback=0.0, status="idle"):
        self.matched_items = matched_items or []
        self.total_cashback = total_cashback
        self.status = status

    def render(self) -> str:
        lines = [
            "=== DreamCo — Receipt Upload & Cashback ===",
            f"Status: {self.status}",
            f"Items Matched: {len(self.matched_items)}",
            f"Total Cashback: ${self.total_cashback:.2f}",
        ]
        for item in self.matched_items[:3]:
            lines.append(f"  • {item.get('name', '?')} → ${item.get('cashback', 0):.2f}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_ID,
            "matched_items": self.matched_items,
            "total_cashback": self.total_cashback,
            "status": self.status,
        }

    @classmethod
    def demo(cls) -> "ReceiptUploadScreen":
        return cls(
            matched_items=[
                {"name": "Tide Pods", "cashback": 2.50},
                {"name": "Lay's Chips", "cashback": 1.00},
            ],
            total_cashback=3.50,
            status="processed",
        )
