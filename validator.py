from decimal import Decimal, InvalidOperation
from typing import Any

def to_decimal(value: Any):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None

def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())

def verify_invoice(invoice: dict, purchase_order: dict) -> dict:
    checks = {}
    issues = []

    # Basic document and supplier checks
    checks["supplier"] = (
        "MATCH" if normalize_text(invoice.get("supplier")) == normalize_text(purchase_order.get("supplier"))
        else "MISMATCH"
    )
    if checks["supplier"] == "MISMATCH":
        issues.append("Supplier name differs between invoice and purchase order.")

    invoice_po = normalize_text(invoice.get("purchase_order_number"))
    po_number = normalize_text(purchase_order.get("purchase_order_number"))
    checks["purchase_order_number"] = "MATCH" if invoice_po and invoice_po == po_number else "MISMATCH"
    if checks["purchase_order_number"] == "MISMATCH":
        issues.append("Purchase order reference is missing or does not match.")

    inv_items = invoice.get("items", [])
    po_items = purchase_order.get("items", [])

    if len(inv_items) != len(po_items):
        checks["item_count"] = "MISMATCH"
        issues.append(f"Invoice has {len(inv_items)} line items; PO has {len(po_items)}.")
    else:
        checks["item_count"] = "MATCH"

    # Simple MVP line matching by normalized description and position.
    line_results = []
    for index, inv_item in enumerate(inv_items):
        if index >= len(po_items):
            line_results.append({"line": index + 1, "status": "UNMATCHED", "issues": ["No corresponding PO line."]})
            continue

        po_item = po_items[index]
        line_issues = []
        description_match = normalize_text(inv_item.get("description")) == normalize_text(po_item.get("description"))
        qty_inv = to_decimal(inv_item.get("quantity"))
        qty_po = to_decimal(po_item.get("quantity"))
        price_inv = to_decimal(inv_item.get("unit_price"))
        price_po = to_decimal(po_item.get("unit_price"))

        if not description_match:
            line_issues.append("Item description differs.")
        if qty_inv is None or qty_po is None or qty_inv != qty_po:
            line_issues.append("Quantity missing or differs.")
        if price_inv is None or price_po is None or price_inv != price_po:
            line_issues.append("Unit price missing or differs.")

        line_results.append({
            "line": index + 1,
            "invoice_description": inv_item.get("description"),
            "po_description": po_item.get("description"),
            "status": "MATCH" if not line_issues else "MISMATCH",
            "issues": line_issues
        })

    checks["line_items"] = "MATCH" if all(x["status"] == "MATCH" for x in line_results) and len(inv_items) == len(po_items) else "MISMATCH"
    for line in line_results:
        issues.extend([f"Line {line['line']}: {issue}" for issue in line["issues"]])

    # Verify invoice line arithmetic and compare declared totals.
    computed_invoice_total = Decimal("0")
    arithmetic_valid = True
    for item in inv_items:
        qty = to_decimal(item.get("quantity"))
        price = to_decimal(item.get("unit_price"))
        if qty is None or price is None:
            arithmetic_valid = False
            break
        computed_invoice_total += qty * price

    declared_total = to_decimal(invoice.get("total"))
    if not arithmetic_valid or declared_total is None:
        checks["invoice_total_arithmetic"] = "NEEDS_REVIEW"
        issues.append("Invoice total cannot be checked because a numeric field is missing or invalid.")
    elif computed_invoice_total == declared_total:
        checks["invoice_total_arithmetic"] = "MATCH"
    else:
        checks["invoice_total_arithmetic"] = "MISMATCH"
        issues.append(f"Invoice line sum ({computed_invoice_total}) differs from declared total ({declared_total}).")

    po_total = Decimal("0")
    po_arithmetic_valid = True
    for item in po_items:
        qty = to_decimal(item.get("quantity"))
        price = to_decimal(item.get("unit_price"))
        if qty is None or price is None:
            po_arithmetic_valid = False
            break
        po_total += qty * price

    if not po_arithmetic_valid:
        checks["po_total_arithmetic"] = "NEEDS_REVIEW"
        issues.append("Purchase order total cannot be checked due to missing or invalid numeric fields.")
    elif declared_total is not None and po_total == declared_total:
        checks["po_total_vs_invoice"] = "MATCH"
    else:
        checks["po_total_vs_invoice"] = "MISMATCH"
        issues.append(f"PO line sum ({po_total}) differs from invoice total ({declared_total}).")

    status = "MATCH" if all(v == "MATCH" for v in checks.values()) else "NEEDS_REVIEW"
    return {
        "invoice_number": invoice.get("invoice_number"),
        "purchase_order_number": purchase_order.get("purchase_order_number"),
        "status": status,
        "checks": checks,
        "line_results": line_results,
        "issues": issues,
        "requires_human_review": status != "MATCH",
        "note": "This prototype flags discrepancies; it does not approve or reject payment."
    }
