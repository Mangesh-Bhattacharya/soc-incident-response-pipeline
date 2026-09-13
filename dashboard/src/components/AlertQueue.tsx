import { motion } from "framer-motion";
import type { CSSProperties } from "react";
import type { Scenario, Severity } from "../types";
import { SEVERITY_COLOR } from "../types";

interface AlertQueueProps {
  scenarios: Scenario[];
  activeId: string | null;
  runningId: string | null;
  onRun: (scenario: Scenario) => void;
}

function timeAgo(iso: string) {
  const diffMs = Date.now() - new Date(iso).getTime();
  const hours = Math.max(1, Math.round(diffMs / 3_600_000));
  return hours < 24 ? `${hours}h ago` : `${Math.round(hours / 24)}d ago`;
}

export default function AlertQueue({ scenarios, activeId, runningId, onRun }: AlertQueueProps) {
  return (
    <div className="panel">
      <p className="panel-title">
        <span>Splunk Alert Queue</span>
        <span>{scenarios.length} alerts</span>
      </p>
      <div className="alert-list">
        {scenarios.map((scenario) => {
          const severity: Severity = scenario.result.score.severity;
          const isRunning = runningId === scenario.id;
          return (
            <motion.button
              key={scenario.id}
              className={`alert-item${activeId === scenario.id ? " active" : ""}`}
              style={{ "--severity-color": SEVERITY_COLOR[severity] } as CSSProperties}
              onClick={() => onRun(scenario)}
              whileTap={{ scale: 0.98 }}
              disabled={runningId !== null}
            >
              <div className="alert-item-top">
                <span className="alert-rule">{scenario.label}</span>
                <span
                  className="severity-chip"
                  style={{
                    color: SEVERITY_COLOR[severity],
                    background: `${SEVERITY_COLOR[severity]}22`,
                  }}
                >
                  {isRunning ? "Processing…" : severity}
                </span>
              </div>
              <span className="alert-meta">
                {scenario.result.alert.host} · {scenario.result.alert.user} ·{" "}
                {timeAgo(scenario.result.alert._time)}
              </span>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
