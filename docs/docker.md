# Running with Docker

The whole console — dashboard + API — runs from two containers and one
command, on Linux, macOS, or Windows (Docker Desktop or Docker Engine +
Compose v2):

```bash
cp .env.example .env      # fill in VT_API_KEY / ABUSEIPDB_API_KEY / JIRA_* — or leave blank for demo mode
docker compose up --build
```

Open **http://localhost:8080**. That's it — no Python or Node.js install
required on the host, no manual wiring between the two services.

## Why you (probably) won't see a firewall prompt

Windows Defender Firewall, the macOS Application Firewall, and Linux's
`ufw`/`firewalld` all prompt (or silently block) when a program starts
listening for connections **from other machines**. This setup avoids that
by design, not by asking you to click "Allow":

- `docker-compose.yml` binds the dashboard's port to `127.0.0.1:8080`, not
  `0.0.0.0:8080` — it only accepts connections that originate from the same
  machine. Loopback-only traffic doesn't cross the firewall boundary those
  tools police, so nothing to approve.
- The API container publishes **no port at all**. It's reachable only from
  the dashboard container, over a private Docker network (`internal` in
  `docker-compose.yml`) that never touches the host's network stack. There's
  nothing for a firewall to see, let alone block.

If `docker compose up` doesn't work at all, that's almost always the Docker
Desktop application itself needing a one-time network permission on first
launch (separate from anything in this repo) — check Docker Desktop's own
prompts, not your OS firewall settings.

## Opting into LAN access

Want a teammate on the same network to open the dashboard too? Change the
port mapping in `docker-compose.yml`:

```yaml
    ports:
      - "8080:8080"   # was "127.0.0.1:8080:8080"
```

...then allow the port through your OS firewall:

**Windows (PowerShell, run as Administrator):**
```powershell
New-NetFirewallRule -DisplayName "SOC Triage Console" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

**macOS:** System Settings → Network → Firewall → Options → add the Docker
Desktop application (or, from Terminal): `sudo pfctl -e` after adding an
allow rule to `/etc/pf.conf` — most users will find the GUI path simpler.

**Linux (ufw):**
```bash
sudo ufw allow 8080/tcp
```

**Linux (firewalld):**
```bash
sudo firewall-cmd --add-port=8080/tcp --permanent && sudo firewall-cmd --reload
```

Only do this on a network you trust — the dashboard has no authentication,
by design, since it's a local analyst tool, not a public-facing app.

## What's actually hardened here

- **Non-root containers.** The API runs as a fixed non-root UID; the
  dashboard uses the `nginx-unprivileged` image (uid 101), not stock nginx.
- **Read-only root filesystems.** Both containers set `read_only: true` in
  `docker-compose.yml`, with `tmpfs` mounts only where the runtime genuinely
  needs to write (nginx's cache/pid dirs, `/tmp`).
- **All Linux capabilities dropped** (`cap_drop: [ALL]`) plus
  `no-new-privileges` — neither service needs any of the capabilities
  containers get by default.
- **Minimal images.** Multi-stage builds mean the dashboard's final image
  contains nginx and static files only — no Node.js, no source, no
  `node_modules`. The API image installs only `requirements-api.txt` (no
  `pytest`, no dev tooling).
- **No secrets baked into images.** API keys are injected at container
  *start* via `.env` (`env_file:` in `docker-compose.yml`), never `COPY`'d
  or `ARG`'d into a layer. `.dockerignore` also excludes `.env` from the
  build context as a second line of defense.
- **No CORS wildcard exposure.** The API container isn't reachable from a
  browser at all in this setup — the dashboard's nginx proxies `/api/*`
  same-origin, so the FastAPI app's permissive CORS middleware (meant for
  local `vite dev` against a separately-running API) never comes into play.

## Health checks

Both services define a `HEALTHCHECK`; `docker compose ps` shows `healthy`
once each is actually serving traffic, not just "container started":

```bash
docker compose ps
```

## Stopping / cleaning up

```bash
docker compose down          # stop and remove containers
docker compose down --rmi local   # also remove the images this repo built
```
