import json
from pathlib import Path
from validator import verify_invoice

def main():
    data_dir = Path(__file__).parent / "sample_data"
    invoice = json.loads((data_dir / "invoice_01.json").read_text(encoding="utf-8"))
    po = json.loads((data_dir / "purchase_order_01.json").read_text(encoding="utf-8"))

    result = verify_invoice(invoice, po)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
