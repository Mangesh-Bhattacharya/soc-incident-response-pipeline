"""Optional FastAPI backend for the dashboard's "live" mode.

Wraps socpipeline.process_alert() behind two endpoints so the dashboard (or
any other client) can hit the real, tested pipeline instead of canned demo
data. This is a public-facing demo surface, so /api/process always runs in
dry-run mode -- it can never file a real Jira ticket, only report what it
would have done.

Run it with:
    pip install -r requirements-api.txt
    uvicorn api.main:app --reload --port 8000
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from socpipeline import process_alert

app = FastAPI(
    title="SOC Pipeline API",
    description="Demo backend for the SOC Triage Console dashboard. Always runs dry-run.",
)

# Wide open on purpose: this exists to let a locally-run dashboard (or a demo
# deployment) call it from the browser. Tighten allow_origins before putting
# this anywhere that isn't a personal demo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/process")
def process(alert: dict) -> dict:
    """Run a Splunk-alert-shaped payload through the real pipeline (dry-run only)."""
    return process_alert(alert, dry_run=True)
