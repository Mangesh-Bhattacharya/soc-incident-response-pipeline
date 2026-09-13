export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";

export interface SplunkAlert {
  rule_name: string;
  search_name?: string;
  _time: string;
  host: string;
  user: string;
  src_ip?: string;
  file_hash?: string;
}

export interface VirusTotalResult {
  file_hash: string;
  found: boolean;
  malicious: number;
  suspicious: number;
  harmless: number;
  undetected: number;
  reputation: number;
  type_description?: string | null;
  error?: string | null;
}

export interface AbuseIPDBResult {
  ip_address: string;
  found: boolean;
  abuse_confidence_score: number;
  total_reports: number;
  country_code?: string | null;
  isp?: string | null;
  is_tor: boolean;
  error?: string | null;
}

export interface ScoreResult {
  score: number;
  severity: Severity;
  reasons: string[];
  should_create_ticket: boolean;
  jira_priority: string;
}

export interface TicketResult {
  created: boolean;
  issue_key?: string | null;
  issue_url?: string | null;
  dry_run?: boolean;
  reason?: string;
  error?: string | null;
  would_create?: { summary: string; description: string[]; priority: string };
}

export interface PipelineResult {
  alert: SplunkAlert;
  enrichment: {
    virustotal?: VirusTotalResult;
    abuseipdb?: AbuseIPDBResult;
  };
  score: ScoreResult;
  ticket: TicketResult;
}

export interface Scenario {
  id: string;
  label: string;
  result: PipelineResult;
}

export type Stage =
  | "idle"
  | "normalizing"
  | "virustotal"
  | "abuseipdb"
  | "scoring"
  | "ticketing"
  | "done";

export const STAGE_ORDER: Stage[] = [
  "normalizing",
  "virustotal",
  "abuseipdb",
  "scoring",
  "ticketing",
  "done",
];

export const SEVERITY_COLOR: Record<Severity, string> = {
  CRITICAL: "#ff4d5e",
  HIGH: "#ff9f43",
  MEDIUM: "#ffd43b",
  LOW: "#5dd6a8",
  INFO: "#6c8eff",
};
