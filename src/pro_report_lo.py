#!/usr/bin/env python3
import sys, os, subprocess, tempfile
from pathlib import Path
from datetime import datetime
import jinja2

BASE = Path.home() / "Desktop" / "00_Kyoto_Core"
TEMPLATES = BASE / "templates"
VAULT_INVOICES = BASE / "vault" / "invoices"

def generate_pdf_libre(data: dict):
    # Calculations
    subtotal = sum(i['qty'] * i['price'] for i in data['items'])
    tva = subtotal * 0.19
    total = subtotal + tva

    # Render HTML
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(TEMPLATES)))
    template = env.get_template("simple_invoice.html")
    html_content = template.render(**data, subtotal=subtotal, tva=tva, total=total)

    # Write temp HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        temp_html = f.name

    # Output paths
    pdf_name = f"{data['doc_type'].lower()}_{data['doc_number']}.pdf"
    pdf_path = VAULT_INVOICES / pdf_name
    VAULT_INVOICES.mkdir(parents=True, exist_ok=True)

    # Convert via LibreOffice headless
    lo_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    subprocess.run([
        lo_path, '--headless', '--convert-to', 'pdf',
        '--outdir', str(VAULT_INVOICES), temp_html
    ], check=True, capture_output=True)

    # Rename output (LibreOffice uses original filename)
    temp_pdf = VAULT_INVOICES / Path(temp_html).with_suffix('.pdf').name
    if temp_pdf.exists() and temp_pdf != pdf_path:
        temp_pdf.rename(pdf_path)

    # Cleanup
    os.unlink(temp_html)

    # Save companion markdown to vault
    sys.path.insert(0, str(BASE / "src"))
    from vault_tools import save_note
    meta = {
        "type": "Invoice",
        "status": "Generated",
        "tags": ["professional", "client-ready", "libreoffice"],
        "client": data.get("client_name", "unknown"),
        "amount_tnd": round(total, 2),
        "date": data["date"]
    }
    md_content = f"# {data['doc_type']} #{data['doc_number']}\n\nClient: {data['client_name']}\nTotal: {total:.2f} TND\nPDF: `{pdf_name}`\n\n📄 [View PDF](vault/invoices/{pdf_name})"
    save_note(f"{data['doc_type'].lower()}-{data['doc_number']}", md_content, meta, folder="invoices")

    return str(pdf_path)

if __name__ == "__main__":
    test_data = {
        "company_name": "Kyoto Digital Solutions",
        "company_address": "Tunis, Tunisia",
        "company_contact": "contact@kyoto.tn | +216 XX XXX XXX",
        "doc_type": "Facture",
        "doc_number": "INV-2026-001",
        "date": datetime.now().strftime("%d/%m/%Y"),
        "client_name": "ABC Corp Tunisia",
        "reference": "PROJ-042",
        "items": [
            {"desc": "Intégration Workflow IA", "qty": 1, "price": 3500},
            {"desc": "Maintenance Mensuelle", "qty": 3, "price": 450},
            {"desc": "Formation Équipe (2h)", "qty": 2, "price": 300}
        ]
    }
    pdf = generate_pdf_libre(test_data)
    print(f"✅ Professional PDF generated via LibreOffice: {pdf}")
