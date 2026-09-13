interface HeaderProps {
  live: boolean;
}

export default function Header({ live }: HeaderProps) {
  return (
    <header className="header">
      <div className="header-title">
        <span className="logo-dot" />
        <div>
          <h1>SOC Triage Console</h1>
          <div className="subtitle">Detect → Enrich → Score → Ticket, animated</div>
        </div>
      </div>
      <div className="mode-pill">
        <span className="pulse" />
        {live ? "Live backend connected" : "Demo mode — canned scenarios, real scoring rules"}
      </div>
    </header>
  );
}
