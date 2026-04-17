import { Icon } from "@/components/ui/Icon";

interface SubmissionSummaryCardProps {
  icon: string;
  label: string;
  value: string;
  note: string;
  tone?: "accent" | "success" | "warning" | "danger";
}

export function SubmissionSummaryCard({
  icon,
  label,
  note,
  tone = "accent",
  value,
}: SubmissionSummaryCardProps) {
  return (
    <article className={`submission-summary-card submission-summary-card--${tone}`}>
      <div className="submission-summary-card__icon">
        <Icon name={icon} />
      </div>
      <p className="submission-summary-card__label">{label}</p>
      <strong className="submission-summary-card__value">{value}</strong>
      <span className="submission-summary-card__note">{note}</span>
    </article>
  );
}
