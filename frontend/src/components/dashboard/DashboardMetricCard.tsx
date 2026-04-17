import { Icon } from "@/components/ui/Icon";

interface DashboardMetricCardProps {
  icon: string;
  label: string;
  value: string;
  hint: string;
  tone?: "accent" | "success" | "warning" | "neutral";
}

export function DashboardMetricCard({
  hint,
  icon,
  label,
  tone = "accent",
  value,
}: DashboardMetricCardProps) {
  return (
    <article className={`dashboard-metric dashboard-metric--${tone}`}>
      <div className="dashboard-metric__icon">
        <Icon name={icon} />
      </div>
      <div className="dashboard-metric__body">
        <p className="dashboard-metric__label">{label}</p>
        <strong className="dashboard-metric__value">{value}</strong>
        <span className="dashboard-metric__hint">{hint}</span>
      </div>
    </article>
  );
}
