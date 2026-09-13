# Wiring a Splunk alert to the n8n webhook

Splunk has no native "send to n8n" action, but its built-in **Webhook** alert
action does exactly what's needed: POST the search results as JSON to a URL
when the alert fires.

## 1. Save the search as an alert

1. Run one of the searches in [`detections.spl`](detections.spl).
2. **Save As > Alert**.
3. Set **Trigger Conditions** (e.g. "Number of Results > 0") and a
   **Cron Schedule** (e.g. `*/5 * * * *` for every 5 minutes).

## 2. Add the Webhook trigger action

1. Under **Trigger Actions**, click **Add Actions > Webhook**.
2. **URL**: your n8n instance's production webhook URL for the imported
   workflow, e.g. `https://n8n.example.com/webhook/splunk-alert`.
3. Splunk POSTs a JSON body shaped like:

```json
{
  "sid": "...",
  "search_name": "SOC - Malware Drop + C2 Beacon Correlation",
  "results_link": "https://splunk.example.com/...",
  "result": {
    "_time": "2026-09-12T03:41:07Z",
    "host": "WKS-FIN-0231",
    "user": "j.alvarez",
    "src_ip": "185.220.101.45",
    "file_hash": "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0",
    "rule_name": "Suspicious File Write"
  }
}
```

   Splunk nests the first matching event under `result` (or `results` — an
   array — if **Include search results** returns more than one row). The n8n
   workflow's first node normalizes both shapes into the flat alert object
   the rest of the pipeline expects; see [`n8n/README.md`](../n8n/README.md).

## 3. Restrict who can reach the webhook

Since this endpoint accepts unauthenticated POSTs by default, lock it down:

- In n8n, enable **Header Auth** on the webhook node and set Splunk's alert
  action to send a static `X-Splunk-Signature` (or similar) header — Splunk's
  webhook action supports custom headers via its REST API alert config even
  though the UI form doesn't expose one directly (use `splunk` CLI or the
  `saved/searches` REST endpoint to add `action.webhook.param.headers`).
- Alternatively, front the n8n webhook with a reverse proxy that allow-lists
  your Splunk search head's egress IP.

## Running the equivalent pipeline without n8n

If you'd rather skip n8n entirely, point the Splunk webhook at a small HTTP
listener that calls `socpipeline.process_alert()` directly — the Python
package in [`src/socpipeline/`](../src/socpipeline/) implements the identical
detect → enrich → score → ticket logic and can run as a standalone Flask/
FastAPI endpoint instead of an n8n workflow.
