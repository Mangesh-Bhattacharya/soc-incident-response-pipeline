import type { PipelineResult, SplunkAlert } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL as string | undefined;

export const hasLiveBackend = Boolean(API_BASE);

export async function checkBackendHealth(timeoutMs = 1500): Promise<boolean> {
  if (!API_BASE) return false;
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
  if (!API_BASE) throw new Error("VITE_API_BASE_URL is not configured");
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
