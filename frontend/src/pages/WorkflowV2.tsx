import { WorkflowCalendarView } from "@/components/workflow/WorkflowCalendarView";
import { WorkflowFilters } from "@/components/workflow/WorkflowFilters";
import { WorkflowRegistryTable } from "@/components/workflow/WorkflowRegistryTable";
import { WorkflowReviewPanel } from "@/components/workflow/WorkflowReviewPanel";
import { WorkflowStatusCards } from "@/components/workflow/WorkflowStatusCards";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useWorkflowData } from "@/hooks/useWorkflowData";
import { useUi } from "@/store/ui.store";

export function WorkflowV2Page() {
  const { toast } = useUi();
  const {
    approvalState,
    calendarDays,
    getSlot,
    query,
    registryRows,
    resetFilters,
    reviewNotes,
    sessionLabel,
    setQuery,
    setStatusFilter,
    stats,
    statusFilter,
    timeSlots,
  } = useWorkflowData();

  const showReadOnlyToast = (label: string) => {
    toast(`${label} is disabled in Milestone 3 read-only mode.`, "info");
  };

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">Workflow and Approvals</span>
          <h1 className="page-hero__title">Institutional Master Schedule</h1>
          <p className="page-hero__description">
            Final verification of time-slot allocation and resource utilization across all departments.
          </p>
          <p className="page-hero__description">Session: {sessionLabel} • Status: {approvalState}</p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={resetFilters}>
            Reset View
          </Button>
          <Button type="button" onClick={() => showReadOnlyToast("Digital sign-off")}>
            Digitally Sign and Publish
          </Button>
        </div>
      </section>

      <WorkflowStatusCards stats={stats} />

      <Card title="Calendar Review View" subtitle="Base template: esq_schedule_review_feedback_calendar_view">
        <WorkflowCalendarView days={calendarDays} timeSlots={timeSlots} getSlot={getSlot} />
      </Card>

      <WorkflowReviewPanel
        notes={reviewNotes}
        onReturnForCorrection={() => showReadOnlyToast("Return for correction")}
        onFinalSignoff={() => showReadOnlyToast("Final authorization")}
      />

      <WorkflowFilters
        query={query}
        statusFilter={statusFilter}
        onQueryChange={setQuery}
        onStatusChange={setStatusFilter}
        onReset={resetFilters}
      />

      <Card title="Final Approval Registry" subtitle="Read-only registry queue for workflow oversight">
        <WorkflowRegistryTable rows={registryRows} />
      </Card>
    </div>
  );
}
