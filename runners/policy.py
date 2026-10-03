"""Enforce the researcher's no-account, no-spend execution choice."""
import json
from pathlib import Path

POLICY = Path(__file__).resolve().parents[1] / 'research-policy.json'


def require_model_access():
    policy = json.loads(POLICY.read_text(encoding='utf-8'))
    if policy.get('allow_model_calls') is not True:
        raise RuntimeError('Model calls are disabled by research-policy.json. Use runners.run_client_tests; no login or paid access is required.')
