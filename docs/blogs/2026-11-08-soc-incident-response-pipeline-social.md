# Social copy for the 2026-11-08 post

## LinkedIn

Ten of seventy VirusTotal engines flagging a file hash, and ten of twelve flagging it, score the exact same 60 points in my SOC triage pipeline's rubric.

That's not a bug I found by reading the code. I found it by building a calibration harness that scores the rubric against labelled alerts and prints a confusion matrix, the same way you'd evaluate a classifier, except there's no model here — it's forty lines of arithmetic, on purpose, because an alert payload contains attacker-controlled strings and I don't want a model deciding escalation on text an attacker chose.

This week, nothing substantive shipped on the repo (just dependency bumps), so instead of a weekly update I wrote up how the harness works:

- 9 of 11 labelled cases scored exactly right, 0 under-triaged (the direction that actually matters), 1 over-triaged on purpose
- The two misses are documented gaps, not surprises: a brute-force burst from Tor scores the same as one failed login (no behavioural axis), and a 10-of-70-engine hit saturates to the same score as a 60-of-70-engine hit
- Real terminal output included: a redacted, fail-closed run with no API keys configured, showing the pipeline still tickets rather than scoring a clean pass on missing evidence

If you're building or evaluating SOC automation, or you've got a labelled alert corpus and want to see how this rubric holds up against it, the repo's open: github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline

#cybersecurity #SOC #Python

## X / Bluesky thread

1/ Ten of seventy VirusTotal engines flagging a hash and ten of twelve flagging it score the exact same in my SOC triage pipeline. Found that by building a calibration harness, not by reading the code.

2/ No new commits on the repo this week, so instead of a weekly update: here's how the harness that grades a deterministic 40-line scorer actually works, with real numbers.

3/ python cli.py --calibrate examples/calibration_corpus.json → 9/11 exact, 0 under-triaged, 1 over-triaged. Under-triage is the number that matters: that's a real threat scored too low.

4/ The 2 misses are deliberate known gaps baked into the test corpus: no behavioural axis (40 failed Tor logins = 1 failed login), and VirusTotal saturates at 10 engines (10/70 and 60/70 score the same).

5/ Also ran it fail-closed with no API keys: a 0/100 "clean" score still tickets, because missing evidence isn't the same as evidence of nothing. Redacted output in the post, real pseudonymised tokens, no invented numbers.

6/ If you've got a labelled alert corpus and want to see how a rule-based scorer holds up against it (or want to add the behavioural axis / ratio-based VT scoring yourself), the repo's open: github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline

7/ Full writeup: [MEDIUM_URL]

#SOC #cybersecurity #infosec #Python
