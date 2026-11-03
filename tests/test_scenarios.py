"""Ten synthetic invoice/PO scenarios for regression testing."""
from copy import deepcopy
from validator import verify_invoice

BASE_INVOICE = {
    "supplier": "ABC Electronics",
    "invoice_number": "INV-100",
    "purchase_order_number": "PO-100",
    "currency": "INR",
    "items": [{"description": "Microcontroller", "quantity": 10, "unit_price": 500}],
    "total": 5000
}
BASE_PO = {
    "supplier": "ABC Electronics",
    "purchase_order_number": "PO-100",
    "currency": "INR",
    "items": [{"description": "Microcontroller", "quantity": 10, "unit_price": 500}]
}

def verify_with_changes(invoice_changes=None, po_changes=None):
    invoice = deepcopy(BASE_INVOICE)
    po = deepcopy(BASE_PO)
    for key, value in (invoice_changes or {}).items():
        invoice[key] = value
    for key, value in (po_changes or {}).items():
        po[key] = value
    return verify_invoice(invoice, po)

def test_01_perfect_match():
    assert verify_with_changes()["status"] == "MATCH"

def test_02_quantity_mismatch():
    result = verify_with_changes({"items": [{"description": "Microcontroller", "quantity": 12, "unit_price": 500}], "total": 6000})
    assert result["checks"]["line_items"] == "MISMATCH"

def test_03_unit_price_mismatch():
    result = verify_with_changes({"items": [{"description": "Microcontroller", "quantity": 10, "unit_price": 550}], "total": 5500})
    assert result["checks"]["line_items"] == "MISMATCH"

def test_04_invoice_total_arithmetic_mismatch():
    result = verify_with_changes({"total": 4999})
    assert result["checks"]["invoice_total_arithmetic"] == "MISMATCH"

def test_05_supplier_mismatch():
    result = verify_with_changes({"supplier": "Other Supplier"})
    assert result["checks"]["supplier"] == "MISMATCH"

def test_06_purchase_order_reference_mismatch():
    result = verify_with_changes({"purchase_order_number": "PO-999"})
    assert result["checks"]["purchase_order_number"] == "MISMATCH"

def test_07_missing_quantity_needs_review():
    result = verify_with_changes({"items": [{"description": "Microcontroller", "quantity": None, "unit_price": 500}]})
    assert result["checks"]["line_items"] == "MISMATCH"
    assert result["requires_human_review"] is True

def test_08_description_mismatch():
    result = verify_with_changes({"items": [{"description": "Microcontroller Board", "quantity": 10, "unit_price": 500}]})
    assert result["checks"]["line_items"] == "MISMATCH"

def test_09_invoice_has_extra_line():
    invoice = deepcopy(BASE_INVOICE)
    invoice["items"].append({"description": "Cable", "quantity": 1, "unit_price": 100})
    invoice["total"] = 5100
    result = verify_invoice(invoice, BASE_PO)
    assert result["checks"]["item_count"] == "MISMATCH"

def test_10_two_lines_with_one_mismatch():
    invoice = deepcopy(BASE_INVOICE)
    po = deepcopy(BASE_PO)
    invoice["items"].append({"description": "Cable", "quantity": 2, "unit_price": 100})
    po["items"].append({"description": "Cable", "quantity": 1, "unit_price": 100})
    invoice["total"] = 5200
    result = verify_invoice(invoice, po)
    assert result["checks"]["line_items"] == "MISMATCH"
