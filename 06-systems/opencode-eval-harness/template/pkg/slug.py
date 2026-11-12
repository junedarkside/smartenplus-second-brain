import re


def slugify(text: str) -> str:
    """Lowercase, replace runs of non-alphanumerics with one dash, strip dashes."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]", "-", text)
    return text.strip("-")
