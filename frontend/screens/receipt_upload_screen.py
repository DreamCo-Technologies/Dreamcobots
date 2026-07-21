"""
DreamCo Money OS — Receipt Upload Screen

FlutterFlow-style screen for uploading receipts, OCR scanning, and
automatically stacking cashback across all supported apps.
"""

from datetime import datetime


class ReceiptUploadScreen:
    """
    Receipt upload with OCR scanning and multi-app cashback stacking.

    Fields
    ------
    receipt_image_url : URL / path of the uploaded receipt image.
    store             : Detected or manually selected store.
    purchase_amount   : Detected or manually entered purchase total.
    cashback_results  : Stacked cashback breakdown from receiptBot.
    total_cashback    : Combined cashback from all apps.
    scan_status       : 'idle' | 'scanning' | 'complete' | 'error'.
    supported_apps    : List of supported cashback apps.
    last_updated      : ISO timestamp.
    """

    SCREEN_NAME = "ReceiptUploadScreen"
    ROUTE = "/receipt/upload"

    SUPPORTED_APPS = ["coinout", "ibotta", "fetch_rewards", "checkout51", "rakuten"]

    def __init__(
        self,
        receipt_image_url: str = "",
        store: str = "",
        purchase_amount: float = 0.0,
        cashback_results: list = None,
        total_cashback: float = 0.0,
        scan_status: str = "idle",
    ):
        self.receipt_image_url = receipt_image_url
        self.store = store
        self.purchase_amount = purchase_amount
        self.cashback_results = cashback_results or []
        self.total_cashback = total_cashback
        self.scan_status = scan_status
        self.last_updated = datetime.utcnow().isoformat() + "Z"

    def render(self) -> dict:
        return {
            "screen": self.SCREEN_NAME,
            "route": self.ROUTE,
            "widgets": {
                "upload_area": {
                    "label": "Tap to upload or take a photo of your receipt",
                    "image_url": self.receipt_image_url,
                    "status": self.scan_status,
                },
                "ocr_result": {
                    "store": self.store or "Detecting...",
                    "purchase_amount": f"${self.purchase_amount:.2f}" if self.purchase_amount else "Detecting...",
                },
                "cashback_stack": {
                    "apps": self.SUPPORTED_APPS,
                    "results": self.cashback_results,
                    "total_cashback": f"${self.total_cashback:.2f}",
                    "highlight_color": "green",
                },
                "submit_button": {
                    "label": "Stack Cashback Now",
                    "enabled": self.scan_status == "complete",
                },
            },
            "last_updated": self.last_updated,
        }

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_NAME,
            "receipt_image_url": self.receipt_image_url,
            "store": self.store,
            "purchase_amount": self.purchase_amount,
            "cashback_results": self.cashback_results,
            "total_cashback": self.total_cashback,
            "scan_status": self.scan_status,
            "supported_apps": self.SUPPORTED_APPS,
            "last_updated": self.last_updated,
        }

    @classmethod
    def demo(cls) -> "ReceiptUploadScreen":
        return cls(
            receipt_image_url="https://example.com/receipts/sample.jpg",
            store="walmart",
            purchase_amount=87.43,
            cashback_results=[
                {"app": "coinout", "cashback_amount": 4.37, "cashback_pct": 5.0, "status": "pending"},
                {"app": "ibotta", "cashback_amount": 6.99, "cashback_pct": 8.0, "status": "pending"},
                {"app": "fetch_rewards", "cashback_amount": 2.62, "cashback_pct": 3.0, "status": "pending"},
                {"app": "checkout51", "cashback_amount": 5.25, "cashback_pct": 6.0, "status": "pending"},
                {"app": "rakuten", "cashback_amount": 8.74, "cashback_pct": 10.0, "status": "pending"},
            ],
            total_cashback=27.97,
            scan_status="complete",
        )
