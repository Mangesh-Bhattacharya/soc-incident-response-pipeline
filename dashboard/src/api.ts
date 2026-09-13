import type { PipelineResult, SplunkAlert } from "./types";

// Defaults to a same-origin relative path so this "just works" behind the
// nginx reverse proxy in docker-compose.yml (which serves the dashboard and
// proxies /api/* to the backend on the same origin -- no CORS, no second
// port to open). Set VITE_API_BASE_URL to point at a different host, e.g.
// when running `vite dev` against a backend on a different port.
const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "";

export async function checkBackendHealth(timeoutMs = 1500): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    const response = await fetch(`${API_BASE}/api/health`, { signal: controller.signal });
    clearTimeout(timer);
    return response.ok;
  } catch {
    return false;
  }
}

export async function processAlertLive(alert: SplunkAlert): Promise<PipelineResult> {
  const response = await fetch(`${API_BASE}/api/process`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(alert),
  });
  if (!response.ok) {
    throw new Error(`Backend returned HTTP ${response.status}`);
  }
  return response.json();
}
