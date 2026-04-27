import re, yaml
from pathlib import Path

VAULT_ROOT = Path.home() / "Desktop" / "00_Kyoto_Core" / "vault"

def parse_md(content: str):
    """Extract YAML frontmatter + body from Markdown"""
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if match:
        return yaml.safe_load(match.group(1)), match.group(2)
    return {}, content

def save_note(title: str, content: str, meta: dict, folder: str = "notes"):
    """Save Markdown note with frontmatter to vault"""
    target = VAULT_ROOT / folder
    target.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower().strip())
    path = target / f"{slug}.md"
    frontmatter = yaml.dump(meta, sort_keys=False, allow_unicode=True)
    path.write_text(f"---\n{frontmatter}---\n{content}", encoding='utf-8')
    return str(path)
