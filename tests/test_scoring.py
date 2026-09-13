import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from socpipeline.abuseipdb import AbuseIPDBResult
from socpipeline.scoring import Severity, TICKET_THRESHOLD_SCORE, score_alert
from socpipeline.virustotal import VirusTotalResult


def test_no_enrichment_yields_info_severity():
    result = score_alert()
    assert result.score == 0
    assert result.severity == Severity.INFO
    assert result.should_create_ticket is False


def test_hash_not_found_and_ip_not_found_yields_info():
    vt = VirusTotalResult(file_hash="deadbeef", found=False)
    abuse = AbuseIPDBResult(ip_address="1.2.3.4", found=False)
    result = score_alert(vt, abuse)
    assert result.score == 0
    assert result.severity == Severity.INFO


def test_vt_only_alert_caps_at_high_not_critical():
    # A single source (VirusTotal alone) tops out at 60 malicious-points +
    # 10 suspicious-points = 70, which is HIGH, not CRITICAL — CRITICAL
    # requires corroboration from a second signal (e.g. AbuseIPDB too).
    vt = VirusTotalResult(file_hash="abc123", found=True, malicious=20, suspicious=10, harmless=10)
    result = score_alert(vt_result=vt)
    assert result.score == 70
    assert result.severity == Severity.HIGH
    assert result.should_create_ticket is True


def test_combined_signals_reach_critical():
    vt = VirusTotalResult(file_hash="abc123", found=True, malicious=20, harmless=10)
    abuse = AbuseIPDBResult(ip_address="185.220.101.45", found=True, abuse_confidence_score=100, is_tor=True)
    result = score_alert(vt_result=vt, abuse_result=abuse)
    assert result.score == 100  # 60 (VT capped) + 50 (abuse) + 10 (tor), capped at 100
    assert result.severity == Severity.CRITICAL


def test_abuseipdb_score_weighted_at_half():
    abuse = AbuseIPDBResult(ip_address="185.220.101.45", found=True, abuse_confidence_score=80, total_reports=200)
    result = score_alert(abuse_result=abuse)
    assert result.score == 40
    assert result.severity == Severity.MEDIUM


def test_tor_exit_node_adds_ten_points():
    abuse = AbuseIPDBResult(ip_address="185.220.101.45", found=True, abuse_confidence_score=0, is_tor=True)
    result = score_alert(abuse_result=abuse)
    assert result.score == 10
    assert any("Tor" in reason for reason in result.reasons)


def test_ticket_threshold_boundary():
    abuse = AbuseIPDBResult(
        ip_address="1.2.3.4", found=True, abuse_confidence_score=round(TICKET_THRESHOLD_SCORE / 0.5)
    )
    result = score_alert(abuse_result=abuse)
    assert result.score == TICKET_THRESHOLD_SCORE
    assert result.should_create_ticket is True
