"""Run the complete document-text -> LLM extraction -> Python validation flow."""
import json
from pathlib import Path

from document_reader import read_document
from extractor import extract_document
from validator import verify_invoice

ROOT = Path(__file__).parent

def main():
    invoice_text = read_document(str(ROOT / "sample_data" / "invoice_sample.txt"))
    po_text = read_document(str(ROOT / "sample_data" / "purchase_order_sample.txt"))

    print("Extracting invoice fields with LLM...")
    invoice = extract_document(invoice_text, "invoice")
    print("Extracting purchase-order fields with LLM...")
    purchase_order = extract_document(po_text, "purchase_order")

    result = verify_invoice(invoice, purchase_order)
    output_path = ROOT / "ai_verification_result.json"
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"Saved result to: {output_path}")

if __name__ == "__main__":
    main()
