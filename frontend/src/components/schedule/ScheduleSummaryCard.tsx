import { Icon } from "@/components/ui/Icon";

interface ScheduleSummaryCardProps {
  icon: string;
  label: string;
  value: string;
  hint: string;
}

export function ScheduleSummaryCard({ hint, icon, label, value }: ScheduleSummaryCardProps) {
  return (
    <article className="schedule-summary-card">
      <div className="schedule-summary-card__icon">
        <Icon name={icon} />
      </div>
      <div>
        <p className="schedule-summary-card__label">{label}</p>
        <strong className="schedule-summary-card__value">{value}</strong>
        <span className="schedule-summary-card__hint">{hint}</span>
      </div>
    </article>
  );
}
