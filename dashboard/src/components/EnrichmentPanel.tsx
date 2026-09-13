import { motion, AnimatePresence } from "framer-motion";
import type { AbuseIPDBResult, VirusTotalResult } from "../types";

interface EnrichmentPanelProps {
  virustotal?: VirusTotalResult;
  abuseipdb?: AbuseIPDBResult;
  showVt: boolean;
  showAbuse: boolean;
}

export default function EnrichmentPanel({ virustotal, abuseipdb, showVt, showAbuse }: EnrichmentPanelProps) {
  return (
    <div className="results-grid">
      <AnimatePresence>
        {showVt && virustotal ? (
          <motion.div
            key="vt-card"
            className="enrichment-card"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h3>🦠 VirusTotal</h3>
            {virustotal.found ? (
              <>
                <div className="stat-row">
                  <span className="stat-label">Malicious</span>
                  <span className="stat-value" style={{ color: virustotal.malicious ? "var(--critical)" : undefined }}>
                    {virustotal.malicious}
                  </span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">Suspicious</span>
                  <span className="stat-value">{virustotal.suspicious}</span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">Clean / Undetected</span>
                  <span className="stat-value">
                    {virustotal.harmless} / {virustotal.undetected}
                  </span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">File type</span>
                  <span className="stat-value">{virustotal.type_description ?? "Unknown"}</span>
                </div>
              </>
            ) : (
              <p className="stat-row" style={{ border: "none" }}>
                Hash not seen by VirusTotal before.
              </p>
            )}
          </motion.div>
        ) : showVt ? (
          <motion.div
            key="vt-skipped"
            className="empty-card"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <span className="empty-icon">🦠</span>
            No file hash on this alert — VirusTotal skipped
          </motion.div>
        ) : null}
      </AnimatePresence>

      <AnimatePresence>
        {showAbuse && abuseipdb ? (
          <motion.div
            key="abuse-card"
            className="enrichment-card"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h3>🌐 AbuseIPDB</h3>
            <div className="stat-row">
              <span className="stat-label">Abuse confidence</span>
              <span className="stat-value">{abuseipdb.abuse_confidence_score}%</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Total reports</span>
              <span className="stat-value">{abuseipdb.total_reports}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Location / ISP</span>
              <span className="stat-value">
                {abuseipdb.country_code ?? "—"} · {abuseipdb.isp ?? "Unknown"}
              </span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Tor exit node</span>
              <span className="stat-value" style={{ color: abuseipdb.is_tor ? "var(--high)" : undefined }}>
                {abuseipdb.is_tor ? "Yes" : "No"}
              </span>
            </div>
          </motion.div>
        ) : showAbuse ? (
          <motion.div
            key="abuse-skipped"
            className="empty-card"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <span className="empty-icon">🌐</span>
            No source IP on this alert — AbuseIPDB skipped
          </motion.div>
        ) : null}
      </AnimatePresence>
    </div>
  );
}
