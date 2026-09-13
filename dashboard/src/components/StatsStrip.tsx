interface StatsStripProps {
  processed: number;
  ticketsCreated: number;
  avgScore: number;
  highestSeverity: string;
}

export default function StatsStrip({ processed, ticketsCreated, avgScore, highestSeverity }: StatsStripProps) {
  const tiles = [
    { label: "Alerts processed this session", value: processed },
    { label: "Jira tickets created", value: ticketsCreated },
    { label: "Average risk score", value: processed ? `${avgScore}/100` : "—" },
    { label: "Highest severity seen", value: processed ? highestSeverity : "—" },
  ];
  return (
    <div className="stats-strip">
      {tiles.map((tile) => (
        <div className="stat-tile" key={tile.label}>
          <div className="stat-tile-value">{tile.value}</div>
          <div className="stat-tile-label">{tile.label}</div>
        </div>
      ))}
    </div>
  );
}
