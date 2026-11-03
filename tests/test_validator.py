from validator import verify_invoice

def test_matching_invoice_and_po():
    invoice = {
        "supplier": "ABC Electronics",
        "invoice_number": "INV-101",
        "purchase_order_number": "PO-101",
        "items": [{"description": "Microcontroller", "quantity": 100, "unit_price": 500}],
        "total": 50000
    }
    po = {
        "supplier": "ABC Electronics",
        "purchase_order_number": "PO-101",
        "items": [{"description": "Microcontroller", "quantity": 100, "unit_price": 500}]
    }
    result = verify_invoice(invoice, po)
    assert result["status"] == "MATCH"
    assert result["requires_human_review"] is False

def test_quantity_mismatch_requires_review():
    invoice = {
        "supplier": "ABC Electronics",
        "invoice_number": "INV-102",
        "purchase_order_number": "PO-101",
        "items": [{"description": "Microcontroller", "quantity": 120, "unit_price": 500}],
        "total": 60000
    }
    po = {
        "supplier": "ABC Electronics",
        "purchase_order_number": "PO-101",
        "items": [{"description": "Microcontroller", "quantity": 100, "unit_price": 500}]
    }
    result = verify_invoice(invoice, po)
    assert result["status"] == "NEEDS_REVIEW"
    assert result["checks"]["line_items"] == "MISMATCH"
