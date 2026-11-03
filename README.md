# AI Invoice Verification Assistant

A small prototype for comparing supplier invoices against purchase orders.

## Current prototype
- Uses synthetic JSON examples.
- Performs deterministic checks for supplier, PO reference, line items, quantities, prices, and totals.
- Flags uncertain or mismatched cases for human review.
- Does not approve payments or provide tax/legal advice.

## Setup
Python 3.10+ recommended.

```bash
python -m venv .venv
```

Windows:
```powershell
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Run:
```bash
python app.py
```

Run tests:
```bash
pytest -q
```

## AI integration
The first version intentionally isolates deterministic validation from AI extraction.
The next stage will add an LLM extraction adapter (for example, using an OpenRouter-compatible API).
Never use real customer or confidential financial documents in this prototype.


## Optional LLM extraction setup

1. Copy `.env.example` to `.env`.
2. Add your OpenRouter API key and a model identifier available to your account.
3. Do not share or commit `.env`.
4. The `extractor.py` module calls an OpenRouter-compatible chat completion endpoint and requests JSON.
5. API calls can cost money or be rate-limited depending on the selected model/account. Check the model's current terms before use.

Example:
```python
from document_reader import read_document
from extractor import extract_document

text = read_document("sample_invoice.pdf")
invoice_data = extract_document(text, "invoice")
print(invoice_data)
```

The LLM may make extraction mistakes. Always run the extracted data through `validator.py` and require human review for uncertain cases. PDF text extraction does not include OCR for scanned documents yet.


## Run the AI end-to-end demo

After configuring `.env` with your OpenRouter key and model:

```bash
python run_ai_verification.py
```

This demo reads two synthetic text documents, asks the model to extract invoice and PO fields, runs the extracted data through the Python validator, and saves `ai_verification_result.json`.

Review the output carefully. The model's extraction is not guaranteed to be correct, and a `MATCH` means the fields matched under this prototype's checks—not that a payment is approved or that a transaction is fraud-free.


## Latest run evidence (reported by developer)

- Automated tests: `python -m pytest -v` → **15 passed** (3 parser, 10 synthetic scenarios, 2 validator tests).
- Live AI smoke test: the OpenRouter free router (`openrouter/free`) successfully extracted one synthetic invoice/PO pair. The validator returned `MATCH` for INV-101 / PO-101 and saved `ai_verification_result.json`.
- This is one live example, not a model accuracy benchmark. The 10 scenario tests are deterministic validation tests and do not each invoke the LLM.
- The specific model chosen by OpenRouter's free router can change; the exact underlying model was not recorded.

## API key security

- Keep your actual API key only in your local `.env` file.
- **Never include `.env` in the submission ZIP, upload it to GitHub, or paste the key into chat.**
- The package includes only `.env.example` with placeholder values.
- If a key is ever exposed, revoke it in OpenRouter and create a replacement.
