interface HeroProps {
  onWatch: () => void;
  hasRun: boolean;
  isRunning: boolean;
  autoPlaying: boolean;
}

export default function Hero({ onWatch, hasRun, isRunning, autoPlaying }: HeroProps) {
  return (
    <section className="hero">
      <div className="hero-copy">
        <h2>Alert triage, automated end to end</h2>
        <p>
          Splunk detects it, this pipeline enriches it against VirusTotal and AbuseIPDB, scores it,
          and — only when it's actually worth an analyst's time — opens a Jira ticket. This console
          animates that exact pipeline so you can see it work before wiring it into your own stack.
        </p>
        <div className="hero-actions">
          <button className="btn-primary" onClick={onWatch} disabled={isRunning}>
            {isRunning ? "Running…" : hasRun ? "↺ Replay the demo" : "▶ Watch it work"}
          </button>
          <a
            className="btn-ghost"
            href="https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline"
            target="_blank"
            rel="noreferrer"
          >
            View the source →
          </a>
        </div>
        <p className="hero-hint" style={{ visibility: autoPlaying ? "visible" : "hidden" }}>
          Auto-playing a CRITICAL alert — click any alert in the queue to try your own.
        </p>
      </div>
      <div className="hero-badges">
        <div className="hero-badge">
          <strong>5</strong>
          <span>live scenarios</span>
        </div>
        <div className="hero-badge">
          <strong>19</strong>
          <span>tests passing</span>
        </div>
        <div className="hero-badge">
          <strong>MIT</strong>
          <span>open source</span>
        </div>
      </div>
    </section>
  );
}
