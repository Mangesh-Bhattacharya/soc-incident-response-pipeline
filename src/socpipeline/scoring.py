"""Combine VirusTotal + AbuseIPDB enrichment into a single severity verdict.

The scoring model is deliberately simple and transparent — every SOC tunes
its own thresholds, so this favors an easy-to-read rubric over a black-box
weighted formula. Adjust the thresholds below to match your environment.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .abuseipdb import AbuseIPDBResult
from .virustotal import VirusTotalResult

# Jira priority mapping and ticket-creation threshold live here so the whole
# scoring policy is defined in one place.
JIRA_PRIORITY = {
    "CRITICAL": "Highest",
    "HIGH": "High",
    "MEDIUM": "Medium",
    "LOW": "Low",
    "INFO": "Lowest",
}
TICKET_THRESHOLD_SCORE = 40  # alerts scoring below this are logged only, no Jira ticket
# Priority for an alert whose enrichment failed and scored below the threshold:
# the score is not evidence of safety, so it goes to a human at a neutral priority.
ENRICHMENT_FAILED_PRIORITY = "Medium"


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class ScoreResult:
    score: int
    severity: Severity
    reasons: list[str] = field(default_factory=list)
    # One entry per enrichment lookup that errored (rate limit, timeout, missing key).
    # Non-empty means the score was computed on incomplete evidence.
    enrichment_errors: list[str] = field(default_factory=list)

    @property
    def enrichment_failed(self) -> bool:
        return bool(self.enrichment_errors)

    @property
    def should_create_ticket(self) -> bool:
        # Fail closed: a lookup that errored is not a clean verdict, so the alert
        # reaches a human rather than being suppressed on partial evidence.
        return self.score >= TICKET_THRESHOLD_SCORE or self.enrichment_failed

    @property
    def jira_priority(self) -> str:
        if self.enrichment_failed and self.score < TICKET_THRESHOLD_SCORE:
            return ENRICHMENT_FAILED_PRIORITY
        return JIRA_PRIORITY[self.severity.value]

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "severity": self.severity.value,
            "reasons": self.reasons,
            "enrichment_failed": self.enrichment_failed,
            "enrichment_errors": self.enrichment_errors,
            "should_create_ticket": self.should_create_ticket,
            "jira_priority": self.jira_priority,
        }


def _score_from_severity(score: int) -> Severity:
    if score >= 80:
        return Severity.CRITICAL
    if score >= 60:
        return Severity.HIGH
    if score >= TICKET_THRESHOLD_SCORE:
        return Severity.MEDIUM
    if score > 0:
        return Severity.LOW
    return Severity.INFO


def score_alert(
    vt_result: VirusTotalResult | None = None,
    abuse_result: AbuseIPDBResult | None = None,
) -> ScoreResult:
    """Score a Splunk alert from its enrichment results.

    - VirusTotal: each engine flagging the hash malicious contributes 6 points
      (capped at 60); any "suspicious" verdicts add 2 points each (capped at 10).
    - AbuseIPDB: its 0-100 abuse-confidence score is weighted at 50%.
    - The two signals are additive and capped at 100.
    - A lookup that returned an error (as opposed to "not found") marks the result
      `enrichment_failed`, which forces a ticket regardless of score.
    """
    score = 0
    reasons: list[str] = []
    enrichment_errors: list[str] = []

    if vt_result and vt_result.error:
        enrichment_errors.append(f"VirusTotal: {vt_result.error}")
    if abuse_result and abuse_result.error:
        enrichment_errors.append(f"AbuseIPDB: {abuse_result.error}")

    if vt_result and vt_result.found:
        malicious_points = min(vt_result.malicious * 6, 60)
        suspicious_points = min(vt_result.suspicious * 2, 10)
        if malicious_points:
            score += malicious_points
            reasons.append(
                f"VirusTotal: {vt_result.malicious}/{vt_result.total_engines} engines flagged "
                f"{vt_result.file_hash} as malicious"
            )
        if suspicious_points:
            score += suspicious_points
            reasons.append(f"VirusTotal: {vt_result.suspicious} engines flagged the hash as suspicious")

    if abuse_result and abuse_result.found:
        abuse_points = round(abuse_result.abuse_confidence_score * 0.5)
        if abuse_points:
            score += abuse_points
            reasons.append(
                f"AbuseIPDB: {abuse_result.ip_address} has a {abuse_result.abuse_confidence_score}% "
                f"abuse confidence score across {abuse_result.total_reports} reports"
            )
        if abuse_result.is_tor:
            score += 10
            reasons.append(f"AbuseIPDB: {abuse_result.ip_address} is a known Tor exit node")

    score = min(score, 100)
    if enrichment_errors:
        reasons.append(
            "Enrichment incomplete, score reflects partial evidence and needs analyst review: "
            + "; ".join(enrichment_errors)
        )
    elif not reasons:
        reasons.append("No indicators returned a hit from either enrichment source")

    return ScoreResult(
        score=score,
        severity=_score_from_severity(score),
        reasons=reasons,
        enrichment_errors=enrichment_errors,
    )
