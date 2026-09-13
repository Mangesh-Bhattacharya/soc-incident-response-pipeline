"""VirusTotal file-hash reputation lookups (API v3)."""
from __future__ import annotations

import os
from dataclasses import dataclass

import requests

VT_BASE_URL = "https://www.virustotal.com/api/v3/files"
REQUEST_TIMEOUT = 15


@dataclass
class VirusTotalResult:
    file_hash: str
    found: bool
    malicious: int = 0
    suspicious: int = 0
    harmless: int = 0
    undetected: int = 0
    reputation: int = 0
    type_description: str | None = None
    error: str | None = None

    @property
    def total_engines(self) -> int:
        return self.malicious + self.suspicious + self.harmless + self.undetected

    def to_dict(self) -> dict:
        return {
            "file_hash": self.file_hash,
            "found": self.found,
            "malicious": self.malicious,
            "suspicious": self.suspicious,
            "harmless": self.harmless,
            "undetected": self.undetected,
            "reputation": self.reputation,
            "type_description": self.type_description,
            "error": self.error,
        }


def check_file_hash(file_hash: str, api_key: str | None = None) -> VirusTotalResult:
    """Look up a file hash (MD5/SHA1/SHA256) on VirusTotal.

    Requires the `VT_API_KEY` environment variable, or pass `api_key` explicitly.
    A hash VirusTotal has never seen returns `found=False` rather than raising.
    """
    api_key = api_key or os.environ.get("VT_API_KEY")
    if not api_key:
        return VirusTotalResult(file_hash=file_hash, found=False, error="VT_API_KEY not configured")

    try:
        response = requests.get(
            f"{VT_BASE_URL}/{file_hash}",
            headers={"x-apikey": api_key},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        return VirusTotalResult(file_hash=file_hash, found=False, error=str(exc))

    if response.status_code == 404:
        return VirusTotalResult(file_hash=file_hash, found=False)
    if response.status_code != 200:
        return VirusTotalResult(
            file_hash=file_hash, found=False, error=f"VirusTotal returned HTTP {response.status_code}"
        )

    payload = response.json().get("data", {}).get("attributes", {})
    stats = payload.get("last_analysis_stats", {})
    return VirusTotalResult(
        file_hash=file_hash,
        found=True,
        malicious=stats.get("malicious", 0),
        suspicious=stats.get("suspicious", 0),
        harmless=stats.get("harmless", 0),
        undetected=stats.get("undetected", 0),
        reputation=payload.get("reputation", 0),
        type_description=payload.get("type_description"),
    )
