"""Pseudonymise alerts and pipeline results before they leave your environment.

Use it before attaching an alert to a public issue, adding it to a shared
calibration corpus, or feeding it to any external service. Secure defaults:

- Allowlist, not blocklist. Only fields known to be safe survive; unknown fields
  (command lines, URLs, registry keys) are dropped because they routinely carry
  credentials and usernames.
- Identifiers are replaced with a keyed HMAC, so the same user maps to the same
  token within a corpus, but the token cannot be reversed or brute-forced
  without the salt.
- Public IPs and file hashes are kept: they are the threat indicators and are
  already sent to VirusTotal / AbuseIPDB.
"""
from __future__ import annotations

import hashlib
import hmac
import ipaddress
import re
from typing import Any

# Pass through unchanged.
SAFE_FIELDS = frozenset({"rule_name", "search_name", "_time", "sourcetype", "index", "file_hash", "process_name"})
# Replaced with a stable token. IP fields are only replaced when not publicly routable.
PSEUDONYMISED_FIELDS = {"user": "user", "host": "host"}
IP_FIELDS = ("src_ip", "dest_ip")

_PROFILE_PATH = re.compile(r"(?i)(?P<prefix>(?:\\|/)(?:Users|home)(?:\\|/))(?P<name>[^\\/]+)")


def _token(kind: str, value: str, salt: bytes) -> str:
    digest = hmac.new(salt, f"{kind}:{value}".encode(), hashlib.sha256).hexdigest()
    return f"{kind}-{digest[:10]}"


def _is_public_ip(value: str) -> bool:
    try:
        return ipaddress.ip_address(value).is_global
    except ValueError:
        return False


def redact_alert(alert: dict, salt: bytes) -> tuple[dict, dict[str, str]]:
    """Return (redacted_alert, replacements). `replacements` maps each original
    sensitive value to its token so callers can scrub derived text."""
    if not salt:
        raise ValueError("salt must be non-empty; an unkeyed hash of a username is trivially reversible")

    redacted: dict[str, Any] = {}
    replacements: dict[str, str] = {}

    for key, value in alert.items():
        if not isinstance(value, str):
            continue
        if key in SAFE_FIELDS:
            redacted[key] = value
        elif key in PSEUDONYMISED_FIELDS:
            redacted[key] = replacements[value] = _token(PSEUDONYMISED_FIELDS[key], value, salt)
        elif key in IP_FIELDS:
            if _is_public_ip(value):
                redacted[key] = value
            else:
                redacted[key] = replacements[value] = _token("ip", value, salt)
        elif key == "file_path":
            def _swap(match: re.Match[str]) -> str:
                name = match.group("name")
                replacements[name] = _token("user", name, salt)
                return match.group("prefix") + replacements[name]

            redacted[key] = _PROFILE_PATH.sub(_swap, value)
    return redacted, replacements


def _scrub(node: Any, replacements: dict[str, str]) -> Any:
    if isinstance(node, str):
        # Longest first so a hostname is not partially replaced by a shorter substring.
        for original in sorted(replacements, key=len, reverse=True):
            node = node.replace(original, replacements[original])
        return node
    if isinstance(node, list):
        return [_scrub(item, replacements) for item in node]
    if isinstance(node, dict):
        return {key: _scrub(value, replacements) for key, value in node.items()}
    return node


def redact_result(result: dict, salt: bytes) -> dict:
    """Redact a `process_alert` result: the alert via the allowlist, everything
    else (reasons, ticket text) by substituting the values the alert redaction replaced."""
    redacted_alert, replacements = redact_alert(result["alert"], salt)
    rest = {key: value for key, value in result.items() if key != "alert"}
    return {"alert": redacted_alert, **_scrub(rest, replacements)}
