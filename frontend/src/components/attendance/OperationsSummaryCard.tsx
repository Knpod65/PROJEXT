import { Icon } from "@/components/ui/Icon";

interface OperationsSummaryCardProps {
  icon: string;
  label: string;
  value: string;
  note: string;
  tone?: "accent" | "success" | "danger" | "neutral";
}

export function OperationsSummaryCard({
  icon,
  label,
  note,
  tone = "accent",
  value,
}: OperationsSummaryCardProps) {
  return (
    <article className={`operations-summary-card operations-summary-card--${tone}`}>
      <div className="operations-summary-card__icon">
        <Icon name={icon} />
      </div>
      <div>
        <p className="operations-summary-card__label">{label}</p>
        <strong className="operations-summary-card__value">{value}</strong>
        <span className="operations-summary-card__note">{note}</span>
      </div>
    </article>
  );
}
