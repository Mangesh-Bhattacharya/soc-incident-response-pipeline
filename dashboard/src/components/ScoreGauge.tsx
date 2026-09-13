import { useEffect, useState } from "react";
import { animate, motion } from "framer-motion";
import type { Severity } from "../types";
import { SEVERITY_COLOR } from "../types";

interface ScoreGaugeProps {
  targetScore: number;
  severity: Severity;
  active: boolean;
}

const RADIUS = 52;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export default function ScoreGauge({ targetScore, severity, active }: ScoreGaugeProps) {
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    if (!active) {
      setDisplayScore(0);
      return;
    }
    const controls = animate(0, targetScore, {
      duration: 0.9,
      ease: "easeOut",
      onUpdate: (value) => setDisplayScore(Math.round(value)),
    });
    return () => controls.stop();
  }, [active, targetScore]);

  const color = active ? SEVERITY_COLOR[severity] : "var(--border)";
  const offset = CIRCUMFERENCE - (displayScore / 100) * CIRCUMFERENCE;

  return (
    <div className="gauge-wrap">
      <div style={{ position: "relative", width: 132, height: 132 }}>
        <svg width="132" height="132" viewBox="0 0 132 132">
          <circle cx="66" cy="66" r={RADIUS} fill="none" stroke="var(--border)" strokeWidth="10" />
          <motion.circle
            cx="66"
            cy="66"
            r={RADIUS}
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={CIRCUMFERENCE}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 0.15 }}
            transform="rotate(-90 66 66)"
          />
        </svg>
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div className="gauge-score">
            {displayScore}
            <span style={{ fontSize: "0.9rem", color: "var(--text-dim)" }}>/100</span>
          </div>
        </div>
      </div>
      <div className="gauge-severity" style={{ color }}>
        {active ? severity : "—"}
      </div>
    </div>
  );
}
