import { Card } from "./Card";

interface StatCardProps {
  icon: string;
  iconBackground?: string;
  label: string;
  value: string;
  subLabel?: string;
  progress?: number;
}

export function StatCard({ icon, iconBackground, label, progress, subLabel, value }: StatCardProps) {
  return (
    <Card className="stat-card">
      <div className="stat-card__row">
        <div className="stat-card__icon" style={iconBackground ? { background: iconBackground } : undefined}>
          {icon}
        </div>
        <div className="stat-card__meta">
          <p className="stat-card__label">{label}</p>
          <p className="stat-card__value">{value}</p>
        </div>
      </div>
      {subLabel ? <p className="stat-card__sub">{subLabel}</p> : null}
      {progress !== undefined ? (
        <div className="stat-card__progress" aria-hidden="true">
          <span style={{ width: `${Math.max(0, Math.min(100, progress))}%` }} />
        </div>
      ) : null}
    </Card>
  );
}
