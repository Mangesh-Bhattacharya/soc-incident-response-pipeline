import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from socpipeline.calibration import evaluate, load_corpus
from socpipeline.scoring import ScoreResult, Severity

CORPUS = Path(__file__).parent.parent / "examples" / "calibration_corpus.json"


def test_bundled_corpus_loads_and_current_rubric_never_under_triages():
    report = evaluate(load_corpus(CORPUS))
    assert report.total == 11
    assert report.under_triaged == []


def test_known_gaps_are_reported_not_hidden():
    report = evaluate(load_corpus(CORPUS))
    missed = {cid for cid, _, _ in report.misclassified}
    assert {"packer-false-positive", "brute-force-burst-tor"} <= missed
    assert report.over_triaged == ["packer-false-positive"]


def test_suppress_everything_scorer_is_flagged_as_under_triaging():
    def never_ticket(_vt, _abuse):
        return ScoreResult(score=0, severity=Severity.INFO)

    report = evaluate(load_corpus(CORPUS), scorer=never_ticket)
    assert "eicar-tor-c2" in report.under_triaged
    assert "vt-rate-limited" in report.under_triaged
    assert report.matrix[("CRITICAL", "INFO")] == 1


def test_unknown_expected_severity_is_rejected(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"cases": [{"id": "x", "expected": "SEVERE"}]}', encoding="utf-8")
    with pytest.raises(ValueError, match="unknown expected severity"):
        load_corpus(bad)
