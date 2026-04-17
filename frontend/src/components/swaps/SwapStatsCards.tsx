import { Card } from "@/components/ui/Card";

import type { SwapsViewRole } from "@/hooks/useSwapsData";

interface SwapStatsCardsProps {
  mode: SwapsViewRole;
  stats: {
    total: number;
    pending: number;
    escalated: number;
    approvedToday: number;
    highPriority: number;
  };
}

export function SwapStatsCards({ mode, stats }: SwapStatsCardsProps) {
  const firstLabel = mode === "teacher" ? "My Requests" : "Total Requests";
  const firstHint = mode === "teacher" ? "Submitted by your account" : "System-wide records";
  const thirdLabel = mode === "teacher" ? "Approved" : "Escalated Cases";
  const thirdValue = mode === "teacher" ? stats.approvedToday : stats.escalated;
  const thirdHint =
    mode === "teacher" ? "Requests that already passed review" : "Needs admin follow-up";

  return (
    <section className="stats-grid" aria-label="Swap statistics">
      <Card>
        <article className="stat-card__row">
          <div className="stat-card__meta">
            <p className="stat-card__label">{firstLabel}</p>
            <h3 className="stat-card__value">{stats.total}</h3>
            <p className="stat-card__sub">{firstHint}</p>
          </div>
        </article>
      </Card>

      <Card>
        <article className="stat-card__row">
          <div className="stat-card__meta">
            <p className="stat-card__label">Pending Queue</p>
            <h3 className="stat-card__value">{stats.pending}</h3>
            <p className="stat-card__sub">Awaiting decision</p>
          </div>
        </article>
      </Card>

      <Card>
        <article className="stat-card__row">
          <div className="stat-card__meta">
            <p className="stat-card__label">{thirdLabel}</p>
            <h3 className="stat-card__value">{thirdValue}</h3>
            <p className="stat-card__sub">{thirdHint}</p>
          </div>
        </article>
      </Card>

      <Card>
        <article className="stat-card__row">
          <div className="stat-card__meta">
            <p className="stat-card__label">High Priority</p>
            <h3 className="stat-card__value">{stats.highPriority}</h3>
            <p className="stat-card__sub">Critical staffing impact</p>
          </div>
        </article>
      </Card>
    </section>
  );
}
