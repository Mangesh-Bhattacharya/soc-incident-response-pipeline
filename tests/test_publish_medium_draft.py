import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).parent.parent
spec = importlib.util.spec_from_file_location("publish_medium_draft", ROOT / "scripts" / "publish_medium_draft.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["publish_medium_draft"] = mod
spec.loader.exec_module(mod)

POST = ROOT / "docs" / "blogs" / "2026-10-09-soc-incident-response-pipeline.md"


def test_prepare_lifts_title_and_strips_internal_notes():
    title, body = mod.prepare(POST.read_text(encoding="utf-8"), POST, ROOT)
    assert title.startswith("Your SOC Pipeline Should Fail Closed")
    assert not body.startswith("# ")
    assert "Draft for Medium" not in body
    assert "<!--" not in body


def test_relative_links_become_github_urls():
    _, body = mod.prepare(POST.read_text(encoding="utf-8"), POST, ROOT)
    assert "](../../src/socpipeline/scoring.py)" not in body
    assert f"]({mod.REPO_BLOB}/src/socpipeline/scoring.py)" in body


def test_link_escaping_the_repo_is_dropped_but_text_kept(tmp_path):
    src = tmp_path / "docs" / "p.md"
    src.parent.mkdir()
    _, body = mod.prepare("# T\n\nsee [secret](../../../etc/passwd) here", src, tmp_path / "repo")
    assert "passwd" not in body and "secret" in body


def test_create_draft_always_requests_draft_status():
    me = MagicMock(json=lambda: {"data": {"id": "u1"}})
    post = MagicMock(json=lambda: {"data": {"url": "https://medium.com/p/x"}})
    with patch.object(mod.requests, "get", return_value=me), patch.object(mod.requests, "post", return_value=post) as p:
        url = mod.create_draft("tok", "T", "body", ["a", "b", "c", "d", "e", "f"])
    payload = p.call_args.kwargs["json"]
    assert url == "https://medium.com/p/x"
    assert payload["publishStatus"] == "draft"
    assert len(payload["tags"]) == 5
