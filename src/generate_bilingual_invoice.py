#!/usr/bin/env python3
import sys, os, subprocess, tempfile
from pathlib import Path
from datetime import datetime
import jinja2

BASE = Path.home() / "Desktop" / "00_Kyoto_Core"
TEMPLATES = BASE / "templates"
VAULT_INVOICES = BASE / "vault" / "invoices"

# Bilingual Labels
LABELS = {
    'ar': {
        'doc_type': 'فاتورة',
        'label_date': 'التاريخ',
        'label_client': 'العميل',
        'label_ref': 'المرجع',
        'label_desc': 'البيان',
        'label_qty': 'الكمية',
        'label_price': 'سعر الوحدة',
        'label_total': 'المجموع',
        'label_subtotal': 'المجموع الجزئي',
        'label_tva': 'الضريبة على القيمة المضافة',
        'label_total_ttc': 'المجموع العام',
        'label_notes': 'ملاحظات',
        'label_payment_terms': 'الدفع خلال 30 يوم',
        'label_penalty': 'تأخير: 2%/شهر',
        'footer_generated': 'تم الإنشاء آلياً بواسطة Kyoto v2.0',
        'direction': 'rtl',
        'lang': 'ar',
    },
    'fr': {
        'doc_type': 'Facture',
        'label_date': 'Date',
        'label_client': 'Client',
        'label_ref': 'Référence',
        'label_desc': 'Désignation',
        'label_qty': 'Qté',
        'label_price': 'Prix Unit.',
        'label_total': 'Total',
        'label_subtotal': 'Sous-total',
        'label_tva': 'TVA',
        'label_total_ttc': 'Total TTC',
        'label_notes': 'Notes',
        'label_payment_terms': 'Paiement 30 jours',
        'label_penalty': 'Pénalité 2%/mois',
        'footer_generated': 'Généré automatiquement par Kyoto v2.0',
        'direction': 'ltr',
        'lang': 'fr',
    }
}

def generate_invoice(data: dict, lang: str = 'ar'):
    labels = LABELS[lang]
    
    # Calculations
    subtotal = sum(i['qty'] * i['price'] for i in data['items'])
    tva_rate = 19
    tva = subtotal * (tva_rate / 100)
    total = subtotal + tva

    # Render HTML
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(TEMPLATES)))
    template = env.get_template("invoice_ar_fr.html")
    
    html_content = template.render(
        **data, 
        **labels,
        subtotal=subtotal, 
        tva=tva, 
        tva_rate=tva_rate,
        total=total,
        currency="TND"
    )

    # Write temp HTML
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        temp_html = f.name

    # Output path
    pdf_name = f"{labels['doc_type']}_{data['doc_number']}.pdf"
    pdf_path = VAULT_INVOICES / pdf_name
    VAULT_INVOICES.mkdir(parents=True, exist_ok=True)

    # Convert via LibreOffice
    lo_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    subprocess.run([
        lo_path, '--headless', '--convert-to', 'pdf',
        '--outdir', str(VAULT_INVOICES), temp_html
    ], check=True, capture_output=True)

    # Rename
    temp_pdf = VAULT_INVOICES / Path(temp_html).with_suffix('.pdf').name
    if temp_pdf.exists() and temp_pdf != pdf_path:
        temp_pdf.rename(pdf_path)

    os.unlink(temp_html)

    # Save to vault
    sys.path.insert(0, str(BASE / "src"))
    from vault_tools import save_note
    meta = {
        "type": "Invoice",
        "status": "Generated",
        "tags": ["bilingual", "tunisia", lang],
        "client": data.get("client_name", "unknown"),
        "amount_tnd": round(total, 3),
        "date": data["date"],
        "language": lang
    }
    md_content = f"# {labels['doc_type']} #{data['doc_number']}\n\n**Client:** {data['client_name']}\n**Total:** {total:.3f} TND\n**Language:** {lang.upper()}\n\n📄 [View PDF](vault/invoices/{pdf_name})"
    save_note(f"{labels['doc_type'].lower()}-{data['doc_number']}", md_content, meta, folder="invoices")

    return str(pdf_path)

if __name__ == "__main__":
    test_data = {
        "company_name": "Kyoto Digital Solutions",
        "company_address": "Tunis, Tunisia",
        "company_contact": "contact@kyoto.tn | +216 XX XXX XXX",
        "doc_number": "INV-2026-002",
        "date": datetime.now().strftime("%d/%m/%Y"),
        "client_name": "شركة ABC Tunisia / ABC Corp Tunisia",
        "reference": "PROJ-043",
        "items": [
            {"desc": "تطوير نظام الذكاء الاصطناعي / AI System Development", "qty": 1, "price": 4500},
            {"desc": "الدعم الفني الشهري / Monthly Support", "qty": 3, "price": 500},
            {"desc": "تدريب الفريق (4 ساعات) / Team Training (4h)", "qty": 1, "price": 800}
        ],
        "notes": "شكراً لثقتكم بنا / Merci pour votre confiance"
    }

    # Generate Arabic version
    pdf_ar = generate_invoice(test_data, lang='ar')
    print(f"✅ Arabic invoice: {pdf_ar}")

    # Generate French version
    pdf_fr = generate_invoice(test_data, lang='fr')
    print(f"✅ French invoice: {pdf_fr}")
