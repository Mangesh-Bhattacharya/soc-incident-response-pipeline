import type { Scenario } from "../types";

// Every number here was computed with the exact same rubric as
// src/socpipeline/scoring.py (malicious x6 capped 60, suspicious x2 capped 10,
// abuse-confidence x0.5, +10 flat for a Tor exit node) so this demo data
// stays truthful to what the real backend would return for the same inputs.
export const SCENARIOS: Scenario[] = [
  {
    id: "critical-malware-c2",
    label: "Malware Drop + C2 Beacon",
    result: {
      alert: {
        rule_name: "Suspicious Outbound Connection Following Malicious File Write",
        search_name: "SOC - Malware Drop + C2 Beacon Correlation",
        _time: "2026-09-14T03:41:07Z",
        host: "WKS-FIN-0231",
        user: "j.alvarez",
        src_ip: "185.220.101.45",
        file_hash: "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0",
      },
      enrichment: {
        virustotal: {
          file_hash: "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0",
          found: true,
          malicious: 58,
          suspicious: 4,
          harmless: 8,
          undetected: 4,
          reputation: -61,
          type_description: "Win32 EXE",
        },
        abuseipdb: {
          ip_address: "185.220.101.45",
          found: true,
          abuse_confidence_score: 97,
          total_reports: 412,
          country_code: "RO",
          isp: "M247 Europe SRL",
          is_tor: true,
        },
      },
      score: {
        score: 100,
        severity: "CRITICAL",
        reasons: [
          "VirusTotal: 58/74 engines flagged 275a021b...51fd0 as malicious",
          "VirusTotal: 4 engines flagged the hash as suspicious",
          "AbuseIPDB: 185.220.101.45 has a 97% abuse confidence score across 412 reports",
          "AbuseIPDB: 185.220.101.45 is a known Tor exit node",
        ],
        should_create_ticket: true,
        jira_priority: "Highest",
      },
      ticket: {
        created: true,
        issue_key: "SOC-142",
        issue_url: "https://your-domain.atlassian.net/browse/SOC-142",
      },
    },
  },
  {
    id: "high-brute-force-tor",
    label: "Brute Force from Tor Exit",
    result: {
      alert: {
        rule_name: "Brute Force Authentication Attempt",
        search_name: "SOC - Repeated Auth Failures",
        _time: "2026-09-14T01:12:44Z",
        host: "vpn-gateway-02",
        user: "svc-remote",
        src_ip: "91.243.44.10",
      },
      enrichment: {
        abuseipdb: {
          ip_address: "91.243.44.10",
          found: true,
          abuse_confidence_score: 100,
          total_reports: 650,
          country_code: "SC",
          isp: "FlokiNET Ehf",
          is_tor: true,
        },
      },
      score: {
        score: 60,
        severity: "HIGH",
        reasons: [
          "AbuseIPDB: 91.243.44.10 has a 100% abuse confidence score across 650 reports",
          "AbuseIPDB: 91.243.44.10 is a known Tor exit node",
        ],
        should_create_ticket: true,
        jira_priority: "High",
      },
      ticket: {
        created: true,
        issue_key: "SOC-138",
        issue_url: "https://your-domain.atlassian.net/browse/SOC-138",
      },
    },
  },
  {
    id: "medium-watchlist-egress",
    label: "Egress to Watchlisted IP",
    result: {
      alert: {
        rule_name: "Outbound Connection to Watchlisted IP",
        search_name: "SOC - Watchlist IP Egress",
        _time: "2026-09-13T22:05:19Z",
        host: "WKS-ENG-0110",
        user: "d.osei",
        src_ip: "45.133.1.22",
      },
      enrichment: {
        abuseipdb: {
          ip_address: "45.133.1.22",
          found: true,
          abuse_confidence_score: 85,
          total_reports: 120,
          country_code: "NL",
          isp: "WorldStream B.V.",
          is_tor: false,
        },
      },
      score: {
        score: 43,
        severity: "MEDIUM",
        reasons: ["AbuseIPDB: 45.133.1.22 has a 85% abuse confidence score across 120 reports"],
        should_create_ticket: true,
        jira_priority: "Medium",
      },
      ticket: {
        created: true,
        issue_key: "SOC-133",
        issue_url: "https://your-domain.atlassian.net/browse/SOC-133",
      },
    },
  },
  {
    id: "low-suspicious-hash",
    label: "Unrecognized Script, Low Confidence",
    result: {
      alert: {
        rule_name: "Suspicious File Write",
        search_name: "SOC - Malware Drop + C2 Beacon Correlation",
        _time: "2026-09-13T18:47:02Z",
        host: "WKS-HR-0087",
        user: "l.nguyen",
        file_hash: "9f2c9a6e1b7d4c3a8e0f5b2d6c1a4e7b9d3f6c0a2e5b8d1f4a7c0e3b6d9f2c5a",
      },
      enrichment: {
        virustotal: {
          file_hash: "9f2c9a6e1b7d4c3a8e0f5b2d6c1a4e7b9d3f6c0a2e5b8d1f4a7c0e3b6d9f2c5a",
          found: true,
          malicious: 0,
          suspicious: 2,
          harmless: 60,
          undetected: 3,
          reputation: 4,
          type_description: "PowerShell Script",
        },
      },
      score: {
        score: 4,
        severity: "LOW",
        reasons: ["VirusTotal: 2 engines flagged the hash as suspicious"],
        should_create_ticket: false,
        jira_priority: "Low",
      },
      ticket: {
        created: false,
        reason: "Below ticket-creation threshold",
      },
    },
  },
  {
    id: "info-benign-login",
    label: "Off-Hours Login, No Indicators",
    result: {
      alert: {
        rule_name: "Off-Hours Login Anomaly",
        search_name: "SOC - Anomalous Login Time",
        _time: "2026-09-13T05:58:31Z",
        host: "WKS-SALES-0044",
        user: "r.kapoor",
        src_ip: "203.0.113.19",
      },
      enrichment: {
        abuseipdb: {
          ip_address: "203.0.113.19",
          found: true,
          abuse_confidence_score: 0,
          total_reports: 0,
          country_code: "IN",
          isp: "Corporate ISP Ltd.",
          is_tor: false,
        },
      },
      score: {
        score: 0,
        severity: "INFO",
        reasons: ["No indicators returned a hit from either enrichment source"],
        should_create_ticket: false,
        jira_priority: "Lowest",
      },
      ticket: {
        created: false,
        reason: "Below ticket-creation threshold",
      },
    },
  },
];
