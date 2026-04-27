#!/usr/bin/env python3
import sys, os
from pathlib import Path
from datetime import datetime

# Ensure src/ imports work regardless of CWD
sys.path.insert(0, str(Path(__file__).parent))
from doc_reader import read_any_file
from vault_tools import save_note

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 process_attachment.py <file.pdf|.docx|.xlsx> [--client NAME] [--tags tag1,tag2]")
        sys.exit(1)

    file_path = sys.argv[1]
    client = next((sys.argv[i+1] for i, a in enumerate(sys.argv) if a == "--client"), "internal")
    tags_str = next((sys.argv[i+1] for i, a in enumerate(sys.argv) if a == "--tags"), "attachment")
    tags = [t.strip() for t in tags_str.split(",")]

    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {path}")
        sys.exit(1)

    print(f"📥 Processing: {path.name}")
    text = read_any_file(str(path))
    if not text.strip():
        text = "[No text extracted - file may be image/scanned]"

    meta = {
        "type": "Document",
        "status": "Processed",
        "tags": tags,
        "client": client,
        "source_file": path.name,
        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    slug = path.stem.lower().replace(" ", "-")
    vault_path = save_note(slug, text, meta, folder="documents")
    print(f"✅ Saved to vault: {vault_path}")

if __name__ == "__main__":
    main()
