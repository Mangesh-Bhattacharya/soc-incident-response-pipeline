import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from socpipeline.pipeline import process_alert

SAMPLE_ALERT = json.loads(
    (Path(__file__).parent.parent / "examples" / "sample_splunk_alert.json").read_text(encoding="utf-8")
)


def _mock_vt_response(malicious=55, suspicious=3, harmless=10, undetected=2):
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "data": {
            "attributes": {
                "last_analysis_stats": {
                    "malicious": malicious,
                    "suspicious": suspicious,
                    "harmless": harmless,
                    "undetected": undetected,
                },
                "reputation": -50,
                "type_description": "Win32 EXE",
            }
        }
    }
    return response


def _mock_abuse_response(score=90, reports=100, is_tor=True):
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "data": {
            "abuseConfidenceScore": score,
            "totalReports": reports,
            "countryCode": "RO",
            "isp": "Example",
            "isTor": is_tor,
        }
    }
    return response


def _dispatching_get(vt_response, abuse_response):
    """socpipeline.virustotal and socpipeline.abuseipdb both do a plain
    `import requests`, so they share the exact same `requests.get` attribute —
    patching it from two module paths at once means the second patch silently
    clobbers the first. A single dispatcher keyed on the request URL avoids
    that collision and mirrors how a real HTTP mocking layer would behave.
    """

    def _get(url, *_args, **_kwargs):
        if "virustotal.com" in url:
            return vt_response
        if "abuseipdb.com" in url:
            return abuse_response
        raise AssertionError(f"Unexpected GET to {url}")

    return _get


@patch("socpipeline.jira_client.requests.post")
@patch("socpipeline.virustotal.requests.get")
def test_high_severity_alert_creates_ticket(mock_get, mock_jira_post, monkeypatch):
    monkeypatch.setenv("VT_API_KEY", "fake")
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "fake")
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "soc@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "fake")
    monkeypatch.setenv("JIRA_PROJECT_KEY", "SOC")

    mock_get.side_effect = _dispatching_get(_mock_vt_response(), _mock_abuse_response())

    jira_response = MagicMock()
    jira_response.status_code = 201
    jira_response.json.return_value = {"key": "SOC-101"}
    mock_jira_post.return_value = jira_response

    result = process_alert(SAMPLE_ALERT)

    # VT: 55 malicious (capped 60) + 3 suspicious (capped 6) = 66
    # AbuseIPDB: 90 * 0.5 = 45, +10 tor = 55
    # Combined 66 + 55 = 121, capped at 100 -> CRITICAL
    assert result["score"]["severity"] == "CRITICAL"
    assert result["score"]["score"] == 100
    assert result["ticket"]["created"] is True
    assert result["ticket"]["issue_key"] == "SOC-101"


@patch("socpipeline.virustotal.requests.get")
def test_dry_run_never_calls_jira(mock_get, monkeypatch):
    monkeypatch.setenv("VT_API_KEY", "fake")
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "fake")
    mock_get.side_effect = _dispatching_get(_mock_vt_response(), _mock_abuse_response())

    with patch("socpipeline.jira_client.requests.post") as mock_jira_post:
        result = process_alert(SAMPLE_ALERT, dry_run=True)

        assert mock_jira_post.called is False
        assert result["ticket"]["dry_run"] is True
        assert "summary" in result["ticket"]["would_create"]


def test_low_score_alert_skips_ticket():
    alert = {"rule_name": "Benign login", "host": "WKS-1", "user": "svc-acct"}
    result = process_alert(alert)
    assert result["score"]["severity"] == "INFO"
    assert result["ticket"]["created"] is False
