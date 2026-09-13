import { motion } from "framer-motion";
import type { Stage } from "../types";
import { STAGE_ORDER } from "../types";

interface FlowNodeDef {
  stage: Stage;
  icon: string;
  label: string;
}

const NODES: FlowNodeDef[] = [
  { stage: "normalizing", icon: "📡", label: "Splunk Alert" },
  { stage: "virustotal", icon: "🦠", label: "VirusTotal" },
  { stage: "abuseipdb", icon: "🌐", label: "AbuseIPDB" },
  { stage: "scoring", icon: "🎯", label: "Score Alert" },
  { stage: "ticketing", icon: "🎫", label: "Jira Ticket" },
];

function nodeState(nodeStage: Stage, currentStage: Stage): "pending" | "active" | "done" {
  const currentIndex = STAGE_ORDER.indexOf(currentStage);
  const nodeIndex = STAGE_ORDER.indexOf(nodeStage);
  if (currentStage === "idle") return "pending";
  if (nodeIndex < currentIndex) return "done";
  if (nodeIndex === currentIndex) return "active";
  return "pending";
}

export default function PipelineFlow({ stage }: { stage: Stage }) {
  return (
    <div className="panel">
      <p className="panel-title">
        <span>Pipeline</span>
        <span>{stage === "idle" ? "Idle" : stage === "done" ? "Complete" : "Running…"}</span>
      </p>
      <div className="pipeline-flow">
        {NODES.map((node, i) => {
          const state = nodeState(node.stage, stage);
          return (
            <div key={node.stage} style={{ display: "flex", alignItems: "center", flex: i === NODES.length - 1 ? "0 0 auto" : "1 1 auto" }}>
              <div className="flow-node">
                <motion.div
                  className="flow-node-icon"
                  animate={{
                    borderColor: state === "pending" ? "var(--border)" : "var(--accent)",
                    boxShadow:
                      state === "active"
                        ? "0 0 0 4px var(--accent-soft)"
                        : state === "done"
                          ? "0 0 0 1px var(--accent)"
                          : "none",
                    scale: state === "active" ? 1.08 : 1,
                    opacity: state === "pending" ? 0.45 : 1,
                  }}
                  transition={{ duration: 0.35 }}
                >
                  {state === "done" ? "✅" : node.icon}
                </motion.div>
                <span className="flow-node-label">{node.label}</span>
              </div>
              {i < NODES.length - 1 && (
                <div className="flow-connector">
                  <motion.div
                    style={{ position: "absolute", inset: 0, background: "var(--accent)", transformOrigin: "left" }}
                    animate={{ scaleX: state === "done" ? 1 : 0 }}
                    transition={{ duration: 0.35 }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
