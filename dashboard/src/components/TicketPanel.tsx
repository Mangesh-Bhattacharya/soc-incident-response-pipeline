import { motion, AnimatePresence } from "framer-motion";
import type { ScoreResult, TicketResult } from "../types";
import { SEVERITY_COLOR } from "../types";

interface TicketPanelProps {
  ticket?: TicketResult;
  score?: ScoreResult;
  visible: boolean;
}

export default function TicketPanel({ ticket, score, visible }: TicketPanelProps) {
  return (
    <div className="panel">
      <p className="panel-title">
        <span>Outcome</span>
      </p>
      <AnimatePresence mode="wait">
        {visible && ticket && score ? (
          <motion.div
            key={ticket.created ? "created" : "skipped"}
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.35, ease: "easeOut" }}
            className="ticket-card"
          >
            <div
              className="ticket-icon"
              style={{
                background: ticket.created ? "rgba(79, 209, 197, 0.15)" : "rgba(138, 147, 166, 0.15)",
                color: ticket.created ? "var(--accent)" : "var(--text-dim)",
              }}
            >
              {ticket.created ? "🎫" : "📝"}
            </div>
            <div>
              <p className="ticket-title">
                {ticket.created
                  ? `Jira ticket ${ticket.issue_key} created`
                  : "No ticket created — logged only"}
              </p>
              <p className="ticket-body">
                {ticket.created ? (
                  <>
                    Priority <strong style={{ color: SEVERITY_COLOR[score.severity] }}>{score.jira_priority}</strong>
                    {" · "}
                    <a href={ticket.issue_url ?? "#"} target="_blank" rel="noreferrer">
                      view issue
                    </a>
                  </>
                ) : (
                  `Score ${score.score}/100 stayed below the ticket-creation threshold (40) — still recorded in the audit log for review.`
                )}
              </p>
            </div>
          </motion.div>
        ) : (
          <div className="empty-card">Run an alert through the pipeline to see the outcome</div>
        )}
      </AnimatePresence>
    </div>
  );
}
