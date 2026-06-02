"""Invoice generation helpers with optional PDF export via reportlab."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List


@dataclass
class InvoiceLine:
    description: str
    quantity: float
    unit_price: float

    @property
    def line_total(self) -> float:
        return round(self.quantity * self.unit_price, 2)


@dataclass
class Invoice:
    invoice_id: str
    customer: str
    issued_on: date
    lines: List[InvoiceLine] = field(default_factory=list)
    tax_rate: float = 0.0


class InvoiceGenerator:
    def totals(self, invoice: Invoice) -> Dict[str, float]:
        subtotal = round(sum(line.line_total for line in invoice.lines), 2)
        tax = round(subtotal * invoice.tax_rate, 2)
        total = round(subtotal + tax, 2)
        return {"subtotal": subtotal, "tax": tax, "total": total}

    def to_text(self, invoice: Invoice) -> str:
        totals = self.totals(invoice)
        body = [f"Invoice {invoice.invoice_id}", f"Customer: {invoice.customer}", f"Issued: {invoice.issued_on.isoformat()}", ""]
        for line in invoice.lines:
            body.append(f"- {line.description}: {line.quantity} x {line.unit_price:.2f} = {line.line_total:.2f}")
        body.extend(["", f"Subtotal: {totals['subtotal']:.2f}", f"Tax: {totals['tax']:.2f}", f"Total: {totals['total']:.2f}"])
        return "\n".join(body)

    def generate_invoice(self, invoice: Invoice, output_path: str | None = None) -> Dict[str, object]:
        text = self.to_text(invoice)
        result: Dict[str, object] = {"text": text, "totals": self.totals(invoice)}
        if output_path is None:
            return result
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() == '.pdf':
            try:
                from reportlab.lib.pagesizes import LETTER
                from reportlab.pdfgen import canvas
            except Exception:
                path.write_text(text, encoding='utf-8')
                result["output"] = str(path)
                result["format"] = "text-fallback"
                return result
            pdf = canvas.Canvas(str(path), pagesize=LETTER)
            y = 750
            for line in text.splitlines():
                pdf.drawString(72, y, line)
                y -= 18
                if y < 72:
                    pdf.showPage()
                    y = 750
            pdf.save()
            result["output"] = str(path)
            result["format"] = "pdf"
            return result
        path.write_text(text, encoding='utf-8')
        result["output"] = str(path)
        result["format"] = "text"
        return result


def sample_invoice() -> Invoice:
    return Invoice(
        invoice_id='INV-1001',
        customer='DreamCo Customer',
        issued_on=date.today(),
        lines=[InvoiceLine('Platform subscription', 1, 199.0), InvoiceLine('Support hours', 3, 75.0)],
        tax_rate=0.07,
    )
