#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from doc_reader import read_any_file

if len(sys.argv) < 2:
    print("Usage: python3 test_office.py <file.pdf|.docx|.xlsx>")
    sys.exit(1)

path = sys.argv[1]
print(f"📄 Reading: {path}\n")
print("="*60)
print(read_any_file(path)[:2000])  # First 2000 chars
print("\n" + "="*60)
print("✅ Extraction complete")
