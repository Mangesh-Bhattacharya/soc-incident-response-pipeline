"""AbuseIPDB IP-reputation lookups (API v2)."""
from __future__ import annotations

import os
from dataclasses import dataclass

import requests

ABUSEIPDB_URL = "https://api.abuseipdb.com/api/v2/check"
REQUEST_TIMEOUT = 15


@dataclass
class AbuseIPDBResult:
    ip_address: str
    found: bool
    abuse_confidence_score: int = 0
    total_reports: int = 0
    country_code: str | None = None
    isp: str | None = None
    is_tor: bool = False
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "ip_address": self.ip_address,
            "found": self.found,
            "abuse_confidence_score": self.abuse_confidence_score,
            "total_reports": self.total_reports,
            "country_code": self.country_code,
            "isp": self.isp,
            "is_tor": self.is_tor,
            "error": self.error,
        }


def check_ip(ip_address: str, api_key: str | None = None, max_age_days: int = 90) -> AbuseIPDBResult:
    """Look up an IPv4/IPv6 address on AbuseIPDB.

    Requires the `ABUSEIPDB_API_KEY` environment variable, or pass `api_key` explicitly.
    """
    api_key = api_key or os.environ.get("ABUSEIPDB_API_KEY")
    if not api_key:
        return AbuseIPDBResult(ip_address=ip_address, found=False, error="ABUSEIPDB_API_KEY not configured")

    try:
        response = requests.get(
            ABUSEIPDB_URL,
            headers={"Key": api_key, "Accept": "application/json"},
            params={"ipAddress": ip_address, "maxAgeInDays": max_age_days, "verbose": "true"},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        return AbuseIPDBResult(ip_address=ip_address, found=False, error=str(exc))

    if response.status_code != 200:
        return AbuseIPDBResult(
            ip_address=ip_address, found=False, error=f"AbuseIPDB returned HTTP {response.status_code}"
        )

    data = response.json().get("data", {})
    return AbuseIPDBResult(
        ip_address=ip_address,
        found=True,
        abuse_confidence_score=data.get("abuseConfidenceScore", 0),
        total_reports=data.get("totalReports", 0),
        country_code=data.get("countryCode"),
        isp=data.get("isp"),
        is_tor=data.get("isTor", False),
    )
