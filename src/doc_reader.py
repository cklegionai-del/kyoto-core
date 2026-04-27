import os, subprocess
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd

def read_pdf(path):
    """Extract text from PDF using pdftotext (poppler) with PyPDF2 fallback."""
    if not os.path.exists(path):
        return {"success": False, "error": f"File not found: {path}"}
    
    # Try pdftotext first (more reliable for complex layouts)
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", path, "-"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return {"success": True, "data": result.stdout.strip(), "source": "pdftotext"}
    except Exception as e:
        pass  # Fallback to PyPDF2
    
    # Fallback: PyPDF2
    try:
        with open(path, 'rb') as file:
            reader = PdfReader(file)
            text = ''.join(page.extract_text() or '' for page in reader.pages)
        if text.strip():
            return {"success": True, "data": text.strip(), "source": "PyPDF2"}
        return {"success": False, "error": "No text extracted (PDF may be scanned/image-based)"}
    except Exception as e:
        return {"success": False, "error": f"PyPDF2 error: {str(e)}"}

def read_docx(path):
    """Extract text from Word document."""
    if not os.path.exists(path):
        return {"success": False, "error": f"File not found: {path}"}
    try:
        document = Document(path)
        text = '\n'.join([para.text for para in document.paragraphs if para.text.strip()])
        return {"success": True, "data": text.strip(), "source": "python-docx"}
    except Exception as e:
        return {"success": False, "error": f"docx error: {str(e)}"}

def read_excel(path):
    """Extract data from Excel as formatted string."""
    if not os.path.exists(path):
        return {"success": False, "error": f"File not found: {path}"}
    try:
        df = pd.read_excel(path)
        return {"success": True, "data": df.to_string(), "source": "pandas"}
    except Exception as e:
        return {"success": False, "error": f"excel error: {str(e)}"}

if __name__ == "__main__":
    print("📚 Testing doc_reader.py...\n")
    
    # Find any PDF on Desktop to test
    desktop = os.path.expanduser("~/Desktop")
    test_pdf = None
    for f in os.listdir(desktop):
        if f.lower().endswith(".pdf"):
            test_pdf = os.path.join(desktop, f)
            break
    
    if test_pdf:
        print(f"📄 Testing with: {os.path.basename(test_pdf)}")
        result = read_pdf(test_pdf)
        if result["success"]:
            print(f"✅ Success! Source: {result['source']}")
            print(f"📝 Preview ({len(result['data'])} chars):\n{result['data'][:300]}...")
        else:
            print(f"❌ {result['error']}")
    else:
        print("⚠️ No PDF found on Desktop — create one or skip test")
    
    print("\n✅ Tests complete!")
