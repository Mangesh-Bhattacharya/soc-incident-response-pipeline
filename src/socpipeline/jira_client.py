"""Create SOC incident tickets in Jira via the REST API v3."""
from __future__ import annotations

import os
from dataclasses import dataclass

import requests

REQUEST_TIMEOUT = 15


@dataclass
class JiraTicketResult:
    created: bool
    issue_key: str | None = None
    issue_url: str | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "created": self.created,
            "issue_key": self.issue_key,
            "issue_url": self.issue_url,
            "error": self.error,
        }


def _adf_description(summary_lines: list[str]) -> dict:
    """Build an Atlassian Document Format description from plain text lines."""
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": line}]} for line in summary_lines
        ],
    }


def create_incident_ticket(
    summary: str,
    description_lines: list[str],
    priority: str,
    labels: list[str] | None = None,
    base_url: str | None = None,
    email: str | None = None,
    api_token: str | None = None,
    project_key: str | None = None,
    issue_type: str = "Incident",
) -> JiraTicketResult:
    """Create a Jira issue for a triaged SOC alert.

    Reads `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY` from
    the environment unless overridden. Uses Jira Cloud's REST API v3 with basic
    auth (email + API token), per Atlassian's documented auth scheme.
    """
    base_url = base_url or os.environ.get("JIRA_BASE_URL")
    email = email or os.environ.get("JIRA_EMAIL")
    api_token = api_token or os.environ.get("JIRA_API_TOKEN")
    project_key = project_key or os.environ.get("JIRA_PROJECT_KEY")

    missing = [
        name
        for name, value in [
            ("JIRA_BASE_URL", base_url),
            ("JIRA_EMAIL", email),
            ("JIRA_API_TOKEN", api_token),
            ("JIRA_PROJECT_KEY", project_key),
        ]
        if not value
    ]
    if missing:
        return JiraTicketResult(created=False, error=f"Missing Jira configuration: {', '.join(missing)}")

    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "description": _adf_description(description_lines),
            "issuetype": {"name": issue_type},
            "priority": {"name": priority},
            "labels": labels or ["soc-automation"],
        }
    }

    try:
        response = requests.post(
            f"{base_url.rstrip('/')}/rest/api/3/issue",
            json=payload,
            auth=(email, api_token),
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        return JiraTicketResult(created=False, error=str(exc))

    if response.status_code not in (200, 201):
        return JiraTicketResult(created=False, error=f"Jira returned HTTP {response.status_code}: {response.text}")

    data = response.json()
    issue_key = data.get("key")
    return JiraTicketResult(
        created=True,
        issue_key=issue_key,
        issue_url=f"{base_url.rstrip('/')}/browse/{issue_key}" if issue_key else None,
    )
