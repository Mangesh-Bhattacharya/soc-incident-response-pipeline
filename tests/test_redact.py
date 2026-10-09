import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from socpipeline.pipeline import process_alert
from socpipeline.redact import redact_alert, redact_result

SALT = b"test-salt"
SAMPLE = json.loads(
    (Path(__file__).parent.parent / "examples" / "sample_splunk_alert.json").read_text(encoding="utf-8")
)


def test_identifiers_are_replaced_and_indicators_kept():
    redacted, _ = redact_alert(SAMPLE, SALT)
    assert redacted["user"].startswith("user-") and "alvarez" not in json.dumps(redacted)
    assert redacted["host"].startswith("host-")
    assert redacted["dest_ip"].startswith("ip-")  # private
    assert redacted["src_ip"] == SAMPLE["src_ip"]  # public indicator
    assert redacted["file_hash"] == SAMPLE["file_hash"]
    assert redacted["file_path"].endswith("\\AppData\\Local\\Temp\\update_svc.exe")


def test_unknown_fields_are_dropped_by_default():
    alert = {**SAMPLE, "command_line": "curl -u admin:hunter2 http://x", "extra": "secret"}
    redacted, _ = redact_alert(alert, SALT)
    assert "command_line" not in redacted and "extra" not in redacted
    assert "hunter2" not in json.dumps(redacted)


def test_tokens_are_stable_per_salt_and_differ_across_salts():
    a, _ = redact_alert(SAMPLE, SALT)
    b, _ = redact_alert(SAMPLE, SALT)
    c, _ = redact_alert(SAMPLE, b"other-salt")
    assert a == b
    assert a["user"] != c["user"]


def test_user_and_profile_path_share_one_token():
    redacted, _ = redact_alert(SAMPLE, SALT)
    assert redacted["user"] in redacted["file_path"]


def test_empty_salt_is_rejected():
    with pytest.raises(ValueError):
        redact_alert(SAMPLE, b"")


def test_result_scrubs_ticket_text(monkeypatch):
    monkeypatch.delenv("VT_API_KEY", raising=False)
    monkeypatch.delenv("ABUSEIPDB_API_KEY", raising=False)
    result = process_alert(SAMPLE, dry_run=True)
    assert "WKS-FIN-0231" in json.dumps(result)

    dumped = json.dumps(redact_result(result, SALT))
    assert "WKS-FIN-0231" not in dumped
    assert "j.alvarez" not in dumped
