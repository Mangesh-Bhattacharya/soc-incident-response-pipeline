import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_process_returns_pipeline_shape_without_live_keys():
    # No VT_API_KEY/ABUSEIPDB_API_KEY configured in CI, and this alert carries
    # no file_hash/src_ip anyway -- exercises the endpoint end-to-end without
    # any network call or live credentials.
    alert = {"rule_name": "API Smoke Test", "host": "ci-runner", "user": "ci"}
    response = client.post("/api/process", json=alert)
    assert response.status_code == 200

    body = response.json()
    assert body["score"]["severity"] == "INFO"
    assert body["ticket"]["created"] is False


def test_process_never_creates_a_real_ticket():
    # /api/process always runs dry_run=True regardless of what's posted --
    # this is a public demo endpoint and must never be able to file Jira
    # tickets even if scored CRITICAL.
    alert = {
        "rule_name": "API Smoke Test - High Score",
        "host": "ci-runner",
        "user": "ci",
        "file_hash": "0" * 64,
    }
    response = client.post("/api/process", json=alert)
    body = response.json()
    assert body["ticket"].get("created") is not True
