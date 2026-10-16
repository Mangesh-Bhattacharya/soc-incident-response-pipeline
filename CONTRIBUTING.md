# Contributing

This is a collaborative project, not a template to fork and forget. The most useful contributions are the ones that make the triage decision more correct, and every one of them can be measured.

## Fastest ways to help (no setup)

1. **Send a misjudged alert.** An alert that scored LOW and should have been CRITICAL, or the reverse, with the enrichment values. Redact it first: `python cli.py --alert a.json --json --redact`. Use the "Misjudged alert" issue form.
2. **Run `python launch.py --doctor` on your OS** and report anything it got wrong. Windows, macOS, Linux and WSL variants are all welcome.
3. **Add labelled cases** to `examples/calibration_corpus.json`. This turns arguments about scoring into numbers.

## Code contributions

```bash
git clone https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline.git
cd soc-incident-response-pipeline
pip install -r requirements-dev.txt
pytest tests/ -v && ruff check .
```

- Open an issue or Discussion before anything larger than a small fix, so effort is not wasted.
- Keep PRs small and include a test. External API calls are always mocked.
- Changes to scoring must include calibration corpus cases showing the effect. Under-triage (a ticket-worthy alert that gets suppressed) is the number that must not get worse.
- No containment or auto-remediation features. Enrich, score, ticket is a deliberate boundary.
- Never route alert fields into a model that decides escalation. They are attacker-controlled.

Open items are listed under "Contributing" in the README, in rough order of value.

## Expectations

Be direct and kind. Critique the code, not the person. Corrections are as welcome as features. Security issues go through [SECURITY.md](SECURITY.md), not public issues.
