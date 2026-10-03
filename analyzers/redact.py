"""Defense in depth for excerpts; raw transcripts must remain private."""
import re
from typing import Any

PATTERNS = [
    (r'(?i)[a-z]:[\\/]users[\\/][^\\/\s"<>]+', '<HOME>'),
    (r'/(?:home|Users)/[^/\s"<>]+', '<HOME>'),
    (r'(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', '<EMAIL>'),
    (r'\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-ant-[A-Za-z0-9_-]+)\b', '<TOKEN>'),
    (r'(?i)(?:authorization\s*[:=]\s*|bearer\s+)[^\s,;"<>]+', '<AUTH>'),
    (r'(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|cookie)\s*[:=]\s*["\']?[^\s,;"\'<>]+', '<SECRET>'),
    (r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b', '<JWT>'),
    (r'\b1[3-9][0-9]{9}\b', '<PHONE>'),
    (r'(?i)(?:https?://)[^\s/@]+:[^\s/@]+@', 'https://<CREDENTIALS>@'),
]

def redact(text: str, private_literals=()) -> str:
    for literal in sorted((s for s in private_literals if s), key=len, reverse=True):
        text = re.sub(re.escape(literal), '<PRIVATE>', text, flags=re.IGNORECASE)
    for pattern, replacement in PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text

def redact_tree(value: Any, private_literals=()):
    if isinstance(value, str): return redact(value, private_literals)
    if isinstance(value, list): return [redact_tree(v, private_literals) for v in value]
    if isinstance(value, dict): return {redact(k, private_literals): redact_tree(v, private_literals) for k, v in value.items()}
    return value

def has_obvious_private_data(text: str) -> bool:
    return any(re.search(p, text) for p, _ in PATTERNS)
