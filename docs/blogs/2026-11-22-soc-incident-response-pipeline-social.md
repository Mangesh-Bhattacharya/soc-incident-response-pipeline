# Social copy for the 2026-11-22 post

Replace `[MEDIUM_URL]` after publishing. Attach `docs/blogs/images/2026-11-22-hero.png`.

## LinkedIn

No human touched soc-incident-response-pipeline's main branch this week. What did happen: Dependabot opened ten pull requests, and four of the five it opened last week were closed today and replaced by a newer version of the same dependency before anyone had merged them.

That's not neglect. It's the update cadence working as designed, so instead of forcing a weekly feature update I went and checked what actually stands between one of those PRs and main:

- The exact same CI gate a human's PR has to clear: ruff, 33 tests across Python 3.10/3.11/3.12, a dashboard build, and a job that boots the real docker-compose stack and curls the published port
- This week's ten PRs touched 3 of the 5 ecosystems Dependabot watches here (pip, npm, a docker base image) -- no GitHub Actions bump needed this time
- ruff and pytest run just now against main: "All checks passed!" and "33 passed, 1 warning in 0.95s" -- real output, not a claim
- A separate monthly schedule: trigger in CI runs the full suite with zero commits required, specifically to catch drift nothing in this repo would ever trigger a test for, and auto-files a GitHub issue if that scheduled run fails

If you maintain a project with Dependabot turned on, worth asking yourself the same question I asked: do you actually know what happens to one of those PRs between open and merge, or are you just trusting the green checkmark?

Full writeup: [MEDIUM_URL]
Repo: https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline

#cybersecurity #devsecops #python #cicd #opensource

## X / Bluesky thread

1/ Zero human commits on my SOC triage pipeline this week. Ten Dependabot PRs instead, and four of last week's five were closed today and replaced by a newer version of the same dependency before anyone merged them. Thread on what that machinery actually does:

2/ The replacements, all today: ruff (#74 -> #80), fastapi (#75 -> #82), framer-motion (#76 -> #83), oxlint (#77 -> #81). The fifth, @vitejs/plugin-react, is still open untouched -- simply because no newer release has shipped for it yet.

3/ Every one of those PRs has to clear the same CI gate a human's would: ruff check ., 33 tests across three Python versions, a dashboard build, and a job that actually boots docker compose and curls the running port. Ran it just now against main: "All checks passed!" / "33 passed... in 0.95s".

4/ Separate from push/PR, ci.yml also has a schedule: trigger that runs the full suite monthly with zero commits required -- for drift nothing in this repo's own diffs would ever trigger a test for (an upstream API shape change, a floating base image tag). On failure it auto-files a GitHub issue, because nobody watches a cron job by default.

5/ The honest limitation: Dependabot's open-pull-requests-limit is 10 per ecosystem here. Hasn't been hit yet, but it's a real ceiling if a dependency updates often enough or review lags long enough.

6/ If you run Dependabot on your own repo, I'd check the same thing I checked here: what's actually between "PR opened" and "PR merged" for you? A green checkmark is only worth trusting if you've looked at what it's checking.

Repo: https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline
Full post: [MEDIUM_URL]

#cybersecurity #devsecops #python #opensource
