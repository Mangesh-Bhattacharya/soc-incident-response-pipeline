"""Measure a scorer against a labelled alert corpus.

Turns "is this score right?" from opinion into a number. The scorer is any
callable with `score_alert`'s signature, so a model-based replacement can be
evaluated over identical inputs.
"""
from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from .abuseipdb import AbuseIPDBResult
from .scoring import ScoreResult, Severity, score_alert
from .virustotal import VirusTotalResult

Scorer = Callable[[VirusTotalResult | None, AbuseIPDBResult | None], ScoreResult]

SEVERITY_ORDER = [s.value for s in (Severity.INFO, Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL)]
TICKET_FLOOR = SEVERITY_ORDER.index(Severity.MEDIUM.value)


@dataclass
class CalibrationCase:
    case_id: str
    expected: str
    vt: VirusTotalResult | None
    abuse: AbuseIPDBResult | None
    # Whether an analyst should see this alert. Defaults to expected >= MEDIUM, but a
    # case can override it: a failed lookup scores INFO yet must still reach a human.
    expect_ticket: bool = False
    note: str = ""


@dataclass
class CalibrationReport:
    total: int
    correct: int
    # (expected, predicted) -> count
    matrix: Counter[tuple[str, str]] = field(default_factory=Counter)
    # Ticket-worthy alerts (expected MEDIUM+) that the scorer did not ticket.
    under_triaged: list[str] = field(default_factory=list)
    # Alerts expected below MEDIUM that the scorer did ticket.
    over_triaged: list[str] = field(default_factory=list)
    misclassified: list[tuple[str, str, str]] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    def render(self) -> str:
        width = max(len(s) for s in SEVERITY_ORDER) + 1
        lines = ["Confusion matrix (rows = expected, columns = predicted)", ""]
        lines.append(" " * width + "".join(f"{s:>{width}}" for s in SEVERITY_ORDER))
        for expected in SEVERITY_ORDER:
            row = "".join(f"{self.matrix[(expected, p)]:>{width}}" for p in SEVERITY_ORDER)
            lines.append(f"{expected:<{width}}{row}")
        lines += [
            "",
            f"Exact severity accuracy: {self.correct}/{self.total} ({self.accuracy:.0%})",
            f"Under-triaged (should ticket, did not): {len(self.under_triaged)}  {self.under_triaged}",
            f"Over-triaged  (should not ticket, did): {len(self.over_triaged)}  {self.over_triaged}",
        ]
        if self.misclassified:
            lines += ["", "Misclassified:"]
            lines += [f"  {cid}: expected {exp}, got {got}" for cid, exp, got in self.misclassified]
        return "\n".join(lines)


def _parse_case(raw: dict) -> CalibrationCase:
    expected = raw["expected"].upper()
    if expected not in SEVERITY_ORDER:
        raise ValueError(f"case {raw.get('id')!r}: unknown expected severity {raw['expected']!r}")
    case_id = raw["id"]
    vt = abuse = None
    if vt_raw := raw.get("virustotal"):
        vt = VirusTotalResult(file_hash=f"corpus:{case_id}", found=vt_raw.get("found", True), **{
            k: vt_raw[k] for k in ("malicious", "suspicious", "harmless", "undetected", "error") if k in vt_raw
        })
    if abuse_raw := raw.get("abuseipdb"):
        abuse = AbuseIPDBResult(ip_address=f"corpus:{case_id}", found=abuse_raw.get("found", True), **{
            k: abuse_raw[k]
            for k in ("abuse_confidence_score", "total_reports", "is_tor", "error")
            if k in abuse_raw
        })
    expect_ticket = raw.get("expect_ticket", SEVERITY_ORDER.index(expected) >= TICKET_FLOOR)
    return CalibrationCase(
        case_id=case_id, expected=expected, vt=vt, abuse=abuse, expect_ticket=expect_ticket, note=raw.get("note", "")
    )


def load_corpus(path: str | Path) -> list[CalibrationCase]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [_parse_case(item) for item in raw["cases"]]


def evaluate(cases: list[CalibrationCase], scorer: Scorer = score_alert) -> CalibrationReport:
    report = CalibrationReport(total=len(cases), correct=0)
    for case in cases:
        result = scorer(case.vt, case.abuse)
        predicted = result.severity.value
        report.matrix[(case.expected, predicted)] += 1
        if predicted == case.expected:
            report.correct += 1
        else:
            report.misclassified.append((case.case_id, case.expected, predicted))
        if case.expect_ticket and not result.should_create_ticket:
            report.under_triaged.append(case.case_id)
        elif not case.expect_ticket and result.should_create_ticket:
            report.over_triaged.append(case.case_id)
    return report
