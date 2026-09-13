import { useEffect, useRef, useState } from "react";
import Header from "./components/Header";
import Hero from "./components/Hero";
import AlertQueue from "./components/AlertQueue";
import PipelineFlow from "./components/PipelineFlow";
import ScoreGauge from "./components/ScoreGauge";
import EnrichmentPanel from "./components/EnrichmentPanel";
import TicketPanel from "./components/TicketPanel";
import StatsStrip from "./components/StatsStrip";
import { SCENARIOS } from "./data/scenarios";
import { checkBackendHealth, processAlertLive } from "./api";
import type { PipelineResult, Scenario, Stage } from "./types";
import { STAGE_ORDER } from "./types";

const STAGE_DELAYS_MS: Record<Stage, number> = {
  idle: 0,
  normalizing: 350,
  virustotal: 750,
  abuseipdb: 750,
  scoring: 550,
  ticketing: 650,
  done: 0,
};

export default function App() {
  const [scenarios] = useState<Scenario[]>(SCENARIOS);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [runningId, setRunningId] = useState<string | null>(null);
  const [stage, setStage] = useState<Stage>("idle");
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [live, setLive] = useState(false);
  const [history, setHistory] = useState<PipelineResult[]>([]);
  const [autoPlaying, setAutoPlaying] = useState(false);
  const timers = useRef<number[]>([]);
  const interactedRef = useRef(false);

  useEffect(() => {
    // Always probe -- in the Docker Compose deployment the API is reachable
    // same-origin behind nginx with zero configuration, so this is how the
    // dashboard discovers it rather than requiring an env var.
    checkBackendHealth().then(setLive);
  }, []);

  useEffect(() => {
    return () => timers.current.forEach((t) => window.clearTimeout(t));
  }, []);

  // First-time visitors from a blog link won't know to click anything —
  // auto-play the most dramatic scenario shortly after load so the pipeline
  // is already shown working. Cancelled the instant a real user interacts.
  useEffect(() => {
    const autoplayTimer = window.setTimeout(() => {
      if (interactedRef.current) return;
      setAutoPlaying(true);
      runScenario(scenarios[0]).finally(() => setAutoPlaying(false));
    }, 1600);
    return () => window.clearTimeout(autoplayTimer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleRun(scenario: Scenario) {
    interactedRef.current = true;
    setAutoPlaying(false);
    runScenario(scenario);
  }

  async function runScenario(scenario: Scenario) {
    if (runningId) return;
    timers.current.forEach((t) => window.clearTimeout(t));
    timers.current = [];

    setRunningId(scenario.id);
    setActiveId(scenario.id);
    setResult(null);
    setStage("idle");

    let finalResult = scenario.result;
    if (live) {
      try {
        finalResult = await processAlertLive(scenario.result.alert);
      } catch {
        // Live backend hiccuped mid-demo — fall back to the canned result
        // rather than leaving the UI stuck.
        finalResult = scenario.result;
      }
    }

    // Populate the result right away — the `stage` gates below control when
    // each panel is allowed to *reveal* it, so the enrichment/score data is
    // already there the instant its stage arrives instead of racing it.
    setResult(finalResult);

    let elapsed = 0;
    STAGE_ORDER.forEach((s) => {
      elapsed += STAGE_DELAYS_MS[s];
      const timer = window.setTimeout(() => {
        setStage(s);
        if (s === "done") {
          setHistory((h) => [...h, finalResult]);
          setRunningId(null);
        }
      }, elapsed);
      timers.current.push(timer);
    });
  }

  const stageIndex = STAGE_ORDER.indexOf(stage);
  const showVt = stageIndex >= STAGE_ORDER.indexOf("virustotal");
  const showAbuse = stageIndex >= STAGE_ORDER.indexOf("abuseipdb");
  const showScore = stageIndex >= STAGE_ORDER.indexOf("scoring");
  const showTicket = stage === "done";

  const processed = history.length;
  const ticketsCreated = history.filter((r) => r.ticket.created).length;
  const avgScore = processed ? Math.round(history.reduce((sum, r) => sum + r.score.score, 0) / processed) : 0;
  const severityRank: Record<string, number> = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1, INFO: 0 };
  const highestSeverity = processed
    ? history.reduce((worst, r) => (severityRank[r.score.severity] > severityRank[worst] ? r.score.severity : worst), "INFO")
    : "—";

  const heroTarget = scenarios.find((s) => s.id === activeId) ?? scenarios[0];

  return (
    <div className="app-shell">
      <Header live={live} />
      <Hero
        onWatch={() => handleRun(heroTarget)}
        hasRun={processed > 0}
        isRunning={Boolean(runningId)}
        autoPlaying={autoPlaying}
      />

      <div className="layout-grid">
        <AlertQueue scenarios={scenarios} activeId={activeId} runningId={runningId} onRun={handleRun} />

        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <PipelineFlow stage={stage} />

          <div className="panel">
            <p className="panel-title">
              <span>Risk Score</span>
              {result && <span>{result.alert.rule_name}</span>}
            </p>
            <ScoreGauge
              targetScore={result?.score.score ?? 0}
              severity={result?.score.severity ?? "INFO"}
              active={showScore && Boolean(result)}
            />
            {result && showScore && (
              <ul className="reasons-list">
                {result.score.reasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
            )}
          </div>

          <div className="panel">
            <p className="panel-title">
              <span>Enrichment</span>
            </p>
            <EnrichmentPanel
              virustotal={result?.enrichment.virustotal}
              abuseipdb={result?.enrichment.abuseipdb}
              showVt={showVt}
              showAbuse={showAbuse}
            />
          </div>

          <TicketPanel ticket={result?.ticket} score={result?.score} visible={showTicket} />
        </div>
      </div>

      <StatsStrip
        processed={processed}
        ticketsCreated={ticketsCreated}
        avgScore={avgScore}
        highestSeverity={highestSeverity}
      />

      <footer className="cta-footer">
        <div>
          <p className="cta-footer-title">Want this running against your own Splunk, Jira, and threat feeds?</p>
          <p className="footer-note" style={{ margin: 0 }}>
            Every number above follows the same scoring rules as{" "}
            <a href="https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline" target="_blank" rel="noreferrer">
              the real pipeline
            </a>
            {live
              ? " — currently running against the live Python backend."
              : ". Demo mode: canned scenarios, no backend required."}
          </p>
        </div>
        <a
          className="btn-primary"
          href="https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline"
          target="_blank"
          rel="noreferrer"
        >
          Explore the repo →
        </a>
      </footer>
    </div>
  );
}
