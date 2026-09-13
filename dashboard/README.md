# SOC Triage Console (dashboard)

An animated React + TypeScript front end for the SOC pipeline — click a
queued Splunk alert and watch it move through the same detect → enrich →
score → ticket stages as the real backend, with the pipeline nodes lighting
up, a risk gauge counting up, enrichment cards animating in, and a Jira
ticket (or "logged only") outcome at the end.

Built separately from [`src/socpipeline/`](../src/socpipeline/) on purpose —
Python runs the pipeline, this is a different language/runtime (Vite + React
+ TypeScript, animated with [Framer Motion](https://www.framer.com/motion/))
purely for the UI layer.

## Two modes

- **Demo mode** (default, no setup): five canned scenarios spanning
  `CRITICAL` → `INFO`, with every VirusTotal/AbuseIPDB stat and risk score
  computed by hand using the *exact same rubric* as
  [`scoring.py`](../src/socpipeline/scoring.py) — see
  [`src/data/scenarios.ts`](src/data/scenarios.ts). Nothing here is invented;
  it's what the real pipeline would return for those inputs.
- **Live mode**: point it at the optional FastAPI backend in
  [`../api/`](../api/main.py), and clicking a scenario sends its alert to the
  real `socpipeline.process_alert()` (always `dry_run=True` — this endpoint
  can never file an actual Jira ticket) and animates the real response
  instead of the canned one.

## Run it

```bash
npm install
npm run dev
```

Opens at `http://localhost:5173`.

> **Cloning into a cloud-synced folder (Google Drive, OneDrive, Dropbox)?**
> `npm install` writes tens of thousands of small files for `node_modules`,
> and cloud-sync virtual filesystems can choke on that (`TAR_ENTRY_ERROR`,
> `EBADF`). If you hit that, run `npm install`/`npm run dev` from a plain
> local path instead (e.g. clone the repo outside the synced folder, or into
> a temp directory) rather than inside the synced one.

For live mode, also run the API (from the repo root) and set
`VITE_API_BASE_URL`:

```bash
# repo root
pip install -r requirements-api.txt
uvicorn api.main:app --reload --port 8000

# dashboard/
cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

The header pill flips from "Demo mode" to "Live backend connected" once it
detects the API. If a live request fails mid-animation, it silently falls
back to that scenario's canned result rather than leaving the UI stuck.

## Build

```bash
npm run build   # outputs to dist/
```

## Structure

```
src/
  types.ts            Mirrors the Python dataclasses (PipelineResult, ScoreResult, ...)
  data/scenarios.ts    Five canned demo alerts + their precomputed pipeline results
  api.ts                Live-mode fetch helpers
  components/
    PipelineFlow.tsx    The animated node chain (Splunk -> VT -> AbuseIPDB -> Score -> Jira)
    ScoreGauge.tsx       Animated 0-100 radial risk gauge
    EnrichmentPanel.tsx  VirusTotal / AbuseIPDB result cards
    TicketPanel.tsx      Jira ticket outcome card
    AlertQueue.tsx       The clickable alert list
    StatsStrip.tsx       Session KPI tiles
  App.tsx               State machine driving the stage-by-stage reveal animation
```
