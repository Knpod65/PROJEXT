import { Icon } from "@/components/ui/Icon";
import { formatCurrency, formatNumber } from "@/utils/format";

interface PrintQueueSummaryCardsProps {
  metrics: {
    pendingJobs: number;
    urgentJobs: number;
    totalSheets: number;
    totalCost: number;
    sections: number;
  };
}

export function PrintQueueSummaryCards({ metrics }: PrintQueueSummaryCardsProps) {
  return (
    <div className="operations-summary-grid">
      <article className="operations-summary-card">
        <div className="operations-summary-card__icon">
          <Icon filled name="pending_actions" />
        </div>
        <p className="operations-summary-card__label">Pending Jobs</p>
        <strong className="operations-summary-card__value">{formatNumber(metrics.pendingJobs)}</strong>
        <p className="operations-summary-card__note">Open print batches awaiting operator action.</p>
      </article>

      <article className="operations-summary-card operations-summary-card--danger">
        <div className="operations-summary-card__icon">
          <Icon filled name="priority_high" />
        </div>
        <p className="operations-summary-card__label">Urgent Queue</p>
        <strong className="operations-summary-card__value">{formatNumber(metrics.urgentJobs)}</strong>
        <p className="operations-summary-card__note">High-volume or same-day batches requiring close oversight.</p>
      </article>

      <article className="operations-summary-card operations-summary-card--success">
        <div className="operations-summary-card__icon">
          <Icon filled name="description" />
        </div>
        <p className="operations-summary-card__label">Total Sheets</p>
        <strong className="operations-summary-card__value">{formatNumber(metrics.totalSheets)}</strong>
        <p className="operations-summary-card__note">Derived from the live copy workload for the active period.</p>
      </article>

      <article className="operations-summary-card operations-summary-card--neutral">
        <div className="operations-summary-card__icon">
          <Icon filled name="payments" />
        </div>
        <p className="operations-summary-card__label">Estimated Cost</p>
        <strong className="operations-summary-card__value">{formatCurrency(metrics.totalCost)}</strong>
        <p className="operations-summary-card__note">{formatNumber(metrics.sections)} sections currently mapped into the queue.</p>
      </article>
    </div>
  );
}
