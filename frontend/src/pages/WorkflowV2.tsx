import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Skeleton } from "@/components/ui/Skeleton";
import { listSchedules } from "@/services/schedule.service";
import {
  getWorkflowSession,
  initWorkflowSession,
  listWorkflowExternalIssues,
  openSwapWindow,
  signWorkflow,
} from "@/services/workflow.service";
import { useAuth } from "@/store/auth.store";
import { usePeriod } from "@/store/period.store";
import { useUi } from "@/store/ui.store";
import type { ScheduleWithSection, WorkflowIssueItem, WorkflowIssueType, WorkflowSession } from "@/types/api";
import { getEffectiveRole } from "@/utils/roles";

const ISSUE_LABELS: Record<WorkflowIssueType, string> = {
  no_invigilator_assigned: "No invigilator assigned",
  room_capacity_exceeded: "Room capacity exceeded",
  high_student_invigilator_ratio: "High student/invigilator ratio",
  external_staff_shortage: "External exam staff shortage",
};

const STAGES = [
  { key: "no_session", label: "Not started" },
  { key: "draft", label: "Round 1 signing" },
  { key: "confirming", label: "Confirming" },
  { key: "confirmed", label: "Confirmed" },
  { key: "swap_open", label: "Swap window" },
  { key: "locked", label: "Locked" },
];

function StageTimeline({ status }: { status: string }) {
  const index = STAGES.findIndex((stage) => stage.key === status);

  return (
    <div className="wf-stage-timeline">
      {STAGES.filter((stage) => stage.key !== "no_session").map((stage, stageIndex) => {
        const currentIndex = stageIndex + 1;
        const done = index >= currentIndex;
        const active = index === currentIndex;
        return (
          <div key={stage.key} className={`wf-stage${done ? " done" : ""}${active ? " active" : ""}`}>
            <div className="wf-stage__dot">
              {done ? <Icon name="check" /> : <span>{stageIndex + 1}</span>}
            </div>
            <span className="wf-stage__label">{stage.label}</span>
            {stageIndex < STAGES.length - 2 && <div className="wf-stage__line" />}
          </div>
        );
      })}
    </div>
  );
}

function SignerRow({
  sig,
  isNext,
  onSign,
  busy,
  canSign,
}: {
  sig: { order: number; username: string; signed_at: string | null };
  isNext: boolean;
  onSign: () => void;
  busy: boolean;
  canSign: boolean;
}) {
  return (
    <div className={`wf-signer${sig.signed_at ? " signed" : ""}${isNext ? " next" : ""}`}>
      <Icon name={sig.signed_at ? "check_circle" : isNext ? "radio_button_checked" : "radio_button_unchecked"} />
      <div className="wf-signer__info">
        <strong>{sig.username}</strong>
        {sig.signed_at ? (
          <small>{new Date(sig.signed_at).toLocaleString()}</small>
        ) : isNext ? (
          <small className="text-muted">Awaiting signature</small>
        ) : null}
      </div>
      {isNext && canSign && (
        <Button type="button" size="sm" loading={busy} onClick={onSign}>
          Sign
        </Button>
      )}
    </div>
  );
}

function computeInternalIssues(schedules: ScheduleWithSection[]): WorkflowIssueItem[] {
  const issues: WorkflowIssueItem[] = [];

  for (const schedule of schedules) {
    const students = schedule.section?.num_students ?? 0;
    const capacity = schedule.room?.capacity ?? 0;
    const invigilators = schedule.supervisions.length;
    const courseCode = schedule.section?.course?.course_id ?? "-";
    const sectionNo = schedule.section?.section_no ?? "-";
    const reference = `${courseCode} sec ${sectionNo}`;

    if (capacity > 0 && students > capacity) {
      issues.push({
        id: `capacity-${schedule.id}`,
        type: "room_capacity_exceeded",
        severity: "error",
        scope: "internal",
        title: ISSUE_LABELS.room_capacity_exceeded,
        message: `${schedule.room?.room_name ?? "Unassigned room"} has capacity ${capacity}, but ${students} students are scheduled.`,
        reference,
      });
    }

    if (invigilators === 0) {
      issues.push({
        id: `invig-${schedule.id}`,
        type: "no_invigilator_assigned",
        severity: "error",
        scope: "internal",
        title: ISSUE_LABELS.no_invigilator_assigned,
        message: `${reference} on ${schedule.exam_date} ${schedule.exam_time} has no invigilator assigned.`,
        reference,
      });
    } else if (students > 0) {
      const ratio = students / invigilators;
      if (ratio > 50) {
        issues.push({
          id: `ratio-${schedule.id}`,
          type: "high_student_invigilator_ratio",
          severity: "warning",
          scope: "internal",
          title: ISSUE_LABELS.high_student_invigilator_ratio,
          message: `${reference} is running at roughly ${Math.round(ratio)} students per invigilator.`,
          reference,
        });
      }
    }
  }

  return issues;
}

function IssueSummary({
  issues,
  filter,
  onFilterChange,
  loading,
}: {
  issues: WorkflowIssueItem[];
  filter: WorkflowIssueType | "all";
  onFilterChange: (value: WorkflowIssueType | "all") => void;
  loading: boolean;
}) {
  const groups = useMemo(() => {
    return (["no_invigilator_assigned", "room_capacity_exceeded", "high_student_invigilator_ratio", "external_staff_shortage"] as WorkflowIssueType[])
      .map((type) => ({
        type,
        label: ISSUE_LABELS[type],
        count: issues.filter((issue) => issue.type === type).length,
      }))
      .filter((group) => group.count > 0);
  }, [issues]);

  if (loading) {
    return <Skeleton className="dashboard-skeleton" />;
  }

  if (issues.length === 0) {
    return (
      <div className="wf-validation wf-validation--ok">
        <Icon name="check_circle" />
        <span>No workflow issues detected. The current schedules and external allocations look ready for review.</span>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <div className="stitch-metric-grid">
        <article className="dashboard-metric dashboard-metric--danger">
          <div className="dashboard-metric__icon"><Icon name="error" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Errors</p>
            <strong className="dashboard-metric__value">{issues.filter((issue) => issue.severity === "error").length}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--warning">
          <div className="dashboard-metric__icon"><Icon name="warning" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Warnings</p>
            <strong className="dashboard-metric__value">{issues.filter((issue) => issue.severity === "warning").length}</strong>
          </div>
        </article>
        {groups.map((group) => (
          <button
            key={group.type}
            type="button"
            className={`dashboard-metric dashboard-metric--clickable${filter === group.type ? " dashboard-metric--selected" : ""}`}
            onClick={() => onFilterChange(filter === group.type ? "all" : group.type)}
          >
            <div className="dashboard-metric__icon"><Icon name="rule" /></div>
            <div className="dashboard-metric__body">
              <p className="dashboard-metric__label">{group.label}</p>
              <strong className="dashboard-metric__value">{group.count}</strong>
            </div>
          </button>
        ))}
      </div>

      <div className="wf-filter-bar">
        <Button type="button" size="sm" variant={filter === "all" ? "primary" : "outline"} onClick={() => onFilterChange("all")}>
          All issues
        </Button>
        {groups.map((group) => (
          <Button
            key={group.type}
            type="button"
            size="sm"
            variant={filter === group.type ? "primary" : "outline"}
            onClick={() => onFilterChange(group.type)}
          >
            {group.label}
          </Button>
        ))}
      </div>
    </div>
  );
}

export function WorkflowV2Page() {
  const { toast } = useUi();
  const { user } = useAuth();
  const { activePeriod } = usePeriod();
  const role = getEffectiveRole(user);
  const isAdmin = role === "admin";
  const canSign = role === "admin" || role === "esq_head" || role === "secretary";

  const [session, setSession] = useState<WorkflowSession | null>(null);
  const [sessionLoading, setSessionLoading] = useState(true);
  const [sessionBusy, setSessionBusy] = useState(false);

  const [schedules, setSchedules] = useState<ScheduleWithSection[]>([]);
  const [schedulesLoading, setSchedulesLoading] = useState(true);
  const [externalIssues, setExternalIssues] = useState<WorkflowIssueItem[]>([]);
  const [externalLoading, setExternalLoading] = useState(false);

  const [issueFilter, setIssueFilter] = useState<WorkflowIssueType | "all">("all");

  const loadSession = useCallback(async () => {
    setSessionLoading(true);
    try {
      const nextSession = await getWorkflowSession();
      setSession(nextSession);
    } catch {
      setSession(null);
    } finally {
      setSessionLoading(false);
    }
  }, []);

  const loadSchedules = useCallback(async () => {
    setSchedulesLoading(true);
    try {
      const nextSchedules = await listSchedules();
      setSchedules(nextSchedules);
    } catch {
      setSchedules([]);
    } finally {
      setSchedulesLoading(false);
    }
  }, []);

  const loadExternalIssues = useCallback(async () => {
    if (!canSign) {
      setExternalIssues([]);
      return;
    }
    setExternalLoading(true);
    try {
      const nextIssues = await listWorkflowExternalIssues();
      setExternalIssues(nextIssues);
    } catch {
      setExternalIssues([]);
    } finally {
      setExternalLoading(false);
    }
  }, [canSign]);

  useEffect(() => {
    void loadSession();
    void loadSchedules();
    void loadExternalIssues();
  }, [loadExternalIssues, loadSchedules, loadSession]);

  const internalIssues = useMemo(() => computeInternalIssues(schedules), [schedules]);
  const issues = useMemo(() => [...internalIssues, ...externalIssues], [externalIssues, internalIssues]);
  const filteredIssues = useMemo(
    () => (issueFilter === "all" ? issues : issues.filter((issue) => issue.type === issueFilter)),
    [issueFilter, issues],
  );
  const errorCount = issues.filter((issue) => issue.severity === "error").length;

  const doAction = async (action: () => Promise<void>, successMessage: string) => {
    setSessionBusy(true);
    try {
      await action();
      toast(successMessage, "success");
      await loadSession();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Action failed.", "error");
    } finally {
      setSessionBusy(false);
    }
  };

  const status = session?.status ?? "no_session";
  const round1 = session?.round1;
  const round2 = session?.round2;
  const myUsername = user?.username ?? "";
  const isNextRound1 = session?.next_signer_r1 === myUsername;
  const isNextRound2 = session?.next_signer_r2 === myUsername;

  const scheduleStats = useMemo(() => {
    return {
      total: schedules.length,
      withRoom: schedules.filter((schedule) => schedule.room).length,
      withInvigilator: schedules.filter((schedule) => schedule.supervisions.length > 0).length,
      students: schedules.reduce((sum, schedule) => sum + (schedule.section?.num_students ?? 0), 0),
    };
  }, [schedules]);

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">Workflow review</span>
          <h1 className="page-hero__title">Schedule review & sign-off</h1>
          <p className="page-hero__description">
            Review operational issues, confirm readiness, and complete the two-round sign-off flow before release.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => { void loadSession(); void loadSchedules(); void loadExternalIssues(); }}>
            Refresh
          </Button>
          {isAdmin && status === "no_session" && (
            <Button
              type="button"
              disabled={errorCount > 0}
              loading={sessionBusy}
              onClick={() => void doAction(async () => { await initWorkflowSession(); }, "Workflow session initialized.")}
            >
              Initialize session
            </Button>
          )}
          {isAdmin && status === "confirmed" && (
            <Button
              type="button"
              variant="outline"
              loading={sessionBusy}
              onClick={() => void doAction(async () => { await openSwapWindow(); }, "Swap window opened.")}
            >
              Open swap window
            </Button>
          )}
        </div>
      </section>

      {activePeriod && (
        <div className="wf-period-bar">
          <Icon name="calendar_month" />
          <span>Active period: <strong>{activePeriod.label}</strong></span>
          <span className="wf-period-bar__status">{activePeriod.exam_type} · semester {activePeriod.semester}</span>
        </div>
      )}

      <Card title="Workflow status" subtitle="Current position in the approval pipeline">
        {sessionLoading ? (
          <Skeleton className="dashboard-skeleton" />
        ) : (
          <>
            <StageTimeline status={status} />
            {status === "no_session" && (
              <p className="text-muted" style={{ marginTop: "12px" }}>
                Generate schedules, resolve blocking issues, then initialize the workflow session to start sign-off.
              </p>
            )}
          </>
        )}
      </Card>

      <div className="stitch-metric-grid">
        <article className="dashboard-metric dashboard-metric--accent">
          <div className="dashboard-metric__icon"><Icon name="event_note" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Schedules</p>
            <strong className="dashboard-metric__value">{scheduleStats.total}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--neutral">
          <div className="dashboard-metric__icon"><Icon name="meeting_room" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">With room assigned</p>
            <strong className="dashboard-metric__value">{scheduleStats.withRoom}</strong>
          </div>
        </article>
        <article className={`dashboard-metric ${scheduleStats.withInvigilator < scheduleStats.total ? "dashboard-metric--warning" : "dashboard-metric--success"}`}>
          <div className="dashboard-metric__icon"><Icon name="groups" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">With invigilators</p>
            <strong className="dashboard-metric__value">{scheduleStats.withInvigilator} / {scheduleStats.total}</strong>
          </div>
        </article>
        <article className={`dashboard-metric ${issues.length > 0 ? "dashboard-metric--warning" : "dashboard-metric--success"}`}>
          <div className="dashboard-metric__icon"><Icon name={issues.length > 0 ? "warning" : "check_circle"} /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Visible issues</p>
            <strong className="dashboard-metric__value">{issues.length}</strong>
          </div>
        </article>
      </div>

      <Card title="Issue review checkpoint" subtitle="Grouped issues must be reviewed before the workflow moves forward">
        <IssueSummary
          issues={issues}
          filter={issueFilter}
          onFilterChange={setIssueFilter}
          loading={schedulesLoading || externalLoading}
        />
        {issues.length > 0 && (
          <DataTable<WorkflowIssueItem>
            columns={[
              {
                key: "title",
                label: "Issue",
                width: "22%",
                render: (row) => (
                  <div className="data-table__content data-table__content--clamp">
                    <strong>{row.title}</strong>
                    <p>{row.scope === "external" ? "External exam flow" : "Internal schedule flow"}</p>
                  </div>
                ),
              },
              {
                key: "severity",
                label: "Severity",
                width: "12%",
                render: (row) => (
                  <span className={`wf-issue-chip wf-issue-chip--${row.severity}`}>
                    <Icon name={row.severity === "error" ? "error" : "warning"} /> {row.severity}
                  </span>
                ),
              },
              {
                key: "reference",
                label: "Reference",
                width: "18%",
              },
              {
                key: "message",
                label: "Details",
                width: "48%",
              },
            ]}
            emptyTitle="No visible issues"
            rowKey={(row) => row.id}
            rows={filteredIssues}
            scrollThreshold={5}
            tableLayout="fixed"
          />
        )}
        {errorCount > 0 && isAdmin && status === "no_session" && (
          <p className="text-muted" style={{ marginTop: "10px", fontSize: "0.85rem" }}>
            Resolve the blocking errors above before initializing the workflow session.
          </p>
        )}
      </Card>

      {session && status !== "no_session" && round1 && (
        <Card
          title="Round 1 · Pre-swap signatures"
          subtitle={`${round1.done} of ${round1.total} signed${round1.complete ? " · Complete" : ""}`}
        >
          <div className="wf-signers">
            {round1.signatures.map((signature, index) => (
              <SignerRow
                key={signature.order}
                sig={signature as { order: number; username: string; signed_at: string | null }}
                isNext={index === round1.done && !round1.complete}
                onSign={() => void doAction(async () => { await signWorkflow(1); }, "Round 1 signature recorded.")}
                busy={sessionBusy}
                canSign={canSign && isNextRound1}
              />
            ))}
          </div>
          {round1.complete && (
            <div className="wf-round-complete">
              <Icon name="verified" /> Round 1 complete. Swaps can now be opened.
            </div>
          )}
        </Card>
      )}

      {session && round1?.complete && round2 && (
        <Card
          title="Round 2 · Post-swap lock"
          subtitle={`${round2.done} of ${round2.total} signed${round2.complete ? " · Locked" : ""}`}
        >
          <div className="wf-signers">
            {round2.signatures.map((signature, index) => (
              <SignerRow
                key={signature.order}
                sig={signature as { order: number; username: string; signed_at: string | null }}
                isNext={index === round2.done && !round2.complete}
                onSign={() => void doAction(async () => { await signWorkflow(2); }, "Round 2 signature recorded.")}
                busy={sessionBusy}
                canSign={canSign && isNextRound2}
              />
            ))}
          </div>
          {round2.complete && (
            <div className="wf-round-complete">
              <Icon name="lock" /> Schedule locked. Ready for print preparation and downstream operations.
            </div>
          )}
        </Card>
      )}

      {!schedulesLoading && schedules.length === 0 && (
        <Card title="No schedule data">
          <EmptyState
            icon={<Icon name="event_busy" />}
            title="No schedules found"
            description="Run the optimizer to generate room and invigilator assignments before starting the workflow."
          />
        </Card>
      )}
    </div>
  );
}
