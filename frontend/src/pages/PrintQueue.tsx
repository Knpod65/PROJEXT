import { PrintQueueSummaryCards } from "@/components/printing/PrintQueueSummaryCards";
import { PrintQueueTable } from "@/components/printing/PrintQueueTable";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { getPrintJobActionLabel, usePrintQueueData } from "@/hooks/usePrintQueueData";
import type { PrintQueueJob } from "@/types/api";
import { useUi } from "@/store/ui.store";

function getActionToast(status: PrintQueueJob["status"]) {
  switch (status) {
    case "queued":
      return "Print job started.";
    case "processing":
      return "Print job completed and ready for dispatch.";
    case "completed":
      return "Print job dispatched to delivery.";
    case "dispatched":
      return "Print job marked as delivered.";
    default:
      return "Print queue updated.";
  }
}

export function PrintQueuePage() {
  const { toast } = useUi();
  const { advanceJob, error, jobs, loading, metrics, reload, supplyAlerts } = usePrintQueueData();

  const handlePreview = (job: PrintQueueJob) => {
    const summary = [job.subject_name, `Section ${job.section}`, job.notes || job.delivery_note || "No operator notes yet."]
      .filter(Boolean)
      .join(" | ");
    toast(summary, "info");
  };

  const handleAdvanceJob = async (job: PrintQueueJob) => {
    try {
      await advanceJob(job);
      toast(getActionToast(job.status), "success");
    } catch (error) {
      toast(error instanceof Error ? error.message : "Unable to update the print job.", "error");
    }
  };

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">ExamPrint Authority</span>
          <h1 className="page-hero__title">Print queue and dispatch control</h1>
          <p className="page-hero__description">
            The print queue now tracks released submissions through a dedicated printing workflow. Copy-count totals
            remain visible as supplemental volume metrics for the active period.
          </p>
          {error ? <p className="page-hero__description">Queue data warning: {error}</p> : null}
        </div>
        <div className="page-hero__actions">
          <Button
            type="button"
            variant="outline"
            onClick={() => toast("Manifest export is the next printing enhancement after the live queue actions.", "info")}
          >
            Export Manifest
          </Button>
          <Button loading={loading} type="button" onClick={() => void reload()}>
            Refresh Queue
          </Button>
        </div>
      </section>

      <PrintQueueSummaryCards metrics={metrics} />

      <div className="dashboard-shell-grid">
        <Card title="Supply watch" subtitle="Supplies are still manually monitored for now.">
          <div className="dashboard-list">
            {supplyAlerts.map((alert) => (
              <div key={alert.id} className="dashboard-list__item">
                <strong>{alert.label}</strong>
                <p>{alert.note}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Dispatch readiness" subtitle="Operator workflow follows the queue state transitions.">
          <div className="dashboard-list">
            <div className="dashboard-list__item">
              <strong>Start and complete</strong>
              <p>Queued jobs move into processing and completion directly from the table.</p>
            </div>
            <div className="dashboard-list__item">
              <strong>Dispatch and delivery</strong>
              <p>Completed jobs advance into dispatch, then final delivered status for audit visibility.</p>
            </div>
            <div className="dashboard-list__item">
              <strong>Queue sequencing</strong>
              <p>Priority is captured at release time and carried through the real printing workflow.</p>
            </div>
          </div>
        </Card>
      </div>

      <Card title="Active print queue" subtitle="Persisted print jobs created from released submissions.">
        <PrintQueueTable
          jobs={jobs}
          loading={loading}
          onPreview={handlePreview}
          onAdvanceJob={handleAdvanceJob}
        />
      </Card>
    </div>
  );
}
