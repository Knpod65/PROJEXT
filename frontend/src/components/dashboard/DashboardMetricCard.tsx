import { Icon } from "@/components/ui/Icon";

interface DashboardMetricCardProps {
  icon: string;
  label: string;
  value: string;
  hint: string;
  tone?: "accent" | "success" | "warning" | "neutral";
  onClick?: () => void;
}

export function DashboardMetricCard({
  hint,
  icon,
  label,
  onClick,
  tone = "accent",
  value,
}: DashboardMetricCardProps) {
  const cls = `dashboard-metric dashboard-metric--${tone}${onClick ? " dashboard-metric--clickable" : ""}`;

  if (onClick) {
    return (
      <button type="button" className={cls} onClick={onClick}>
        <div className="dashboard-metric__icon">
          <Icon name={icon} />
        </div>
        <div className="dashboard-metric__body">
          <p className="dashboard-metric__label">{label}</p>
          <strong className="dashboard-metric__value">{value}</strong>
          <span className="dashboard-metric__hint">{hint}</span>
        </div>
        <Icon className="dashboard-metric__arrow" name="arrow_forward" />
      </button>
    );
  }

  return (
    <article className={cls}>
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
