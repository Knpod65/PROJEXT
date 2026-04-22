import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Skeleton } from "@/components/ui/Skeleton";
import {
  getWorkflowSession,
  initWorkflowSession,
  openSwapWindow,
  signWorkflow,
} from "@/services/workflow.service";
import { listSchedules } from "@/services/schedule.service";
import { useAuth } from "@/store/auth.store";
import { usePeriod } from "@/store/period.store";
import { useUi } from "@/store/ui.store";
import type { ScheduleWithSection, WorkflowSession } from "@/types/api";
import { getEffectiveRole } from "@/utils/roles";

// ── Stage indicator ────────────────────────────────────────────

const STAGES = [
  { key: "no_session", label: "Not started" },
  { key: "draft", label: "Round 1 signing" },
  { key: "confirming", label: "Confirming" },
  { key: "confirmed", label: "Confirmed" },
  { key: "swap_open", label: "Swap window" },
  { key: "locked", label: "Locked" },
];

function StageTimeline({ status }: { status: string }) {
  const idx = STAGES.findIndex((s) => s.key === status);
  return (
    <div className="wf-stage-timeline">
      {STAGES.filter((s) => s.key !== "no_session").map((stage, i) => {
        const stageIdx = i + 1;
        const done = idx >= stageIdx;
        const active = idx === stageIdx;
        return (
          <div key={stage.key} className={`wf-stage${done ? " done" : ""}${active ? " active" : ""}`}>
            <div className="wf-stage__dot">
              {done ? <Icon name="check" /> : <span>{i + 1}</span>}
            </div>
            <span className="wf-stage__label">{stage.label}</span>
            {i < STAGES.length - 2 && <div className="wf-stage__line" />}
          </div>
        );
      })}
    </div>
  );
}

// ── Validation summary ─────────────────────────────────────────

interface ValidationIssue {
  type: "overcapacity" | "no_invigilator" | "underratio";
  severity: "error" | "warning";
  message: string;
  scheduleId: number;
}

function computeIssues(schedules: ScheduleWithSection[]): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  for (const sch of schedules) {
    const students = sch.section?.num_students ?? 0;
    const capacity = sch.room?.capacity ?? 0;
    const invigs = sch.supervisions.length;

    if (capacity > 0 && students > capacity) {
      issues.push({
        type: "overcapacity",
        severity: "error",
        message: `${sch.room?.room_name ?? "Room"} — ${students} students, capacity ${capacity} (${sch.section?.course?.course_id ?? ""} §${sch.section?.section_no ?? ""})`,
        scheduleId: sch.id,
      });
    }

    if (invigs === 0) {
      issues.push({
        type: "no_invigilator",
        severity: "error",
        message: `No invigilator assigned — ${sch.section?.course?.course_id ?? ""} §${sch.section?.section_no ?? ""} on ${sch.exam_date} ${sch.exam_time}`,
        scheduleId: sch.id,
      });
    } else if (students > 0 && invigs > 0) {
      const ratio = students / invigs;
      if (ratio > 50) {
        issues.push({
          type: "underratio",
          severity: "warning",
          message: `High student/invigilator ratio (${Math.round(ratio)}:1) — ${sch.section?.course?.course_id ?? ""} §${sch.section?.section_no ?? ""}`,
          scheduleId: sch.id,
        });
      }
    }
  }
  return issues;
}

function ValidationPanel({ issues, loading }: { issues: ValidationIssue[]; loading: boolean }) {
  const [expanded, setExpanded] = useState(false);
  const errors = issues.filter((i) => i.severity === "error");
  const warnings = issues.filter((i) => i.severity === "warning");

  if (loading) return <Skeleton className="dashboard-skeleton" />;
  if (issues.length === 0) {
    return (
      <div className="wf-validation wf-validation--ok">
        <Icon name="check_circle" />
        <span>No scheduling issues detected. Room assignments and invigilator ratios are within bounds.</span>
      </div>
    );
  }

  return (
    <div className="wf-validation">
      <div className="wf-validation__summary" onClick={() => setExpanded((p) => !p)} style={{ cursor: "pointer" }}>
        <div className="wf-validation__counts">
          {errors.length > 0 && (
            <span className="wf-issue-chip wf-issue-chip--error">
              <Icon name="error" /> {errors.length} error{errors.length !== 1 ? "s" : ""}
            </span>
          )}
          {warnings.length > 0 && (
            <span className="wf-issue-chip wf-issue-chip--warning">
              <Icon name="warning" /> {warnings.length} warning{warnings.length !== 1 ? "s" : ""}
            </span>
          )}
        </div>
        <Icon name={expanded ? "expand_less" : "expand_more"} />
      </div>
      {expanded && (
        <ul className="wf-issue-list">
          {issues.map((issue, i) => (
            <li key={i} className={`wf-issue wf-issue--${issue.severity}`}>
              <Icon name={issue.severity === "error" ? "error" : "warning"} />
              <span>{issue.message}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ── Signer row ─────────────────────────────────────────────────

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

// ── Main page ──────────────────────────────────────────────────

export function WorkflowV2Page() {
  const { toast } = useUi();
  const { user } = useAuth();
  const { activePeriod } = usePeriod();
  const role = getEffectiveRole(user);
  const isAdmin = role === "admin";
  const isEsq = role === "esq_head";
  const isSecretary = role === "secretary";
  const canSign = isAdmin || isEsq || isSecretary;

  const [session, setSession] = useState<WorkflowSession | null>(null);
  const [sessionLoading, setSessionLoading] = useState(true);
  const [sessionBusy, setSessionBusy] = useState(false);

  const [schedules, setSchedules] = useState<ScheduleWithSection[]>([]);
  const [schedulesLoading, setSchedulesLoading] = useState(true);

  const loadSession = useCallback(async () => {
    setSessionLoading(true);
    try {
      const s = await getWorkflowSession();
      setSession(s);
    } catch {
      setSession(null);
    } finally {
      setSessionLoading(false);
    }
  }, []);

  const loadSchedules = useCallback(async () => {
    setSchedulesLoading(true);
    try {
      const data = await listSchedules();
      setSchedules(data);
    } catch {
      setSchedules([]);
    } finally {
      setSchedulesLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadSession();
    void loadSchedules();
  }, [loadSession, loadSchedules]);

  const issues = useMemo(() => computeIssues(schedules), [schedules]);
  const errorCount = issues.filter((i) => i.severity === "error").length;

  const doAction = async (fn: () => Promise<void>, successMsg: string) => {
    setSessionBusy(true);
    try {
      await fn();
      toast(successMsg, "success");
      await loadSession();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Action failed.", "error");
    } finally {
      setSessionBusy(false);
    }
  };

  const status = session?.status ?? "no_session";
  const r1 = session?.round1;
  const r2 = session?.round2;

  // Check if current user's username matches the next signer
  const myUsername = user?.username ?? "";
  const isNextR1 = session?.next_signer_r1 === myUsername;
  const isNextR2 = session?.next_signer_r2 === myUsername;

  const schedStats = useMemo(() => {
    const total = schedules.length;
    const withRoom = schedules.filter((s) => s.room).length;
    const withInvig = schedules.filter((s) => s.supervisions.length > 0).length;
    const students = schedules.reduce((acc, s) => acc + (s.section?.num_students ?? 0), 0);
    return { total, withRoom, withInvig, students };
  }, [schedules]);

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">Approval workflow</span>
          <h1 className="page-hero__title">Schedule review & sign-off</h1>
          <p className="page-hero__description">
            4-signature confirmation process. Admin and ESQ sign round 1 before swaps open; ESQ and Secretary sign round 2 to lock.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => { void loadSession(); void loadSchedules(); }}>
            Refresh
          </Button>
          {isAdmin && status === "no_session" && (
            <Button
              type="button"
              disabled={errorCount > 0}
              loading={sessionBusy}
              onClick={() => void doAction(async () => { await initWorkflowSession(); }, "Session initialized.")}
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

      {/* Period context */}
      {activePeriod && (
        <div className="wf-period-bar">
          <Icon name="calendar_month" />
          <span>Active period: <strong>{activePeriod.label}</strong></span>
          <span className="wf-period-bar__status">{activePeriod.exam_type} · {activePeriod.semester}</span>
        </div>
      )}

      {/* Stage timeline */}
      <Card title="Workflow status" subtitle="Current position in the approval process">
        {sessionLoading ? (
          <Skeleton className="dashboard-skeleton" />
        ) : (
          <>
            <StageTimeline status={status} />
            {status === "no_session" && (
              <p className="text-muted" style={{ marginTop: "12px" }}>
                Run the optimizer first, then initialize a session to begin the approval process.
              </p>
            )}
          </>
        )}
      </Card>

      {/* Scheduling summary stats */}
      <div className="stitch-metric-grid">
        <article className="dashboard-metric dashboard-metric--accent">
          <div className="dashboard-metric__icon"><Icon name="event_note" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Total schedules</p>
            <strong className="dashboard-metric__value">{schedStats.total}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--neutral">
          <div className="dashboard-metric__icon"><Icon name="meeting_room" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">With room assigned</p>
            <strong className="dashboard-metric__value">{schedStats.withRoom}</strong>
          </div>
        </article>
        <article className={`dashboard-metric ${schedStats.withInvig < schedStats.total ? "dashboard-metric--warning" : "dashboard-metric--success"}`}>
          <div className="dashboard-metric__icon"><Icon name="groups" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">With invigilators</p>
            <strong className="dashboard-metric__value">{schedStats.withInvig} / {schedStats.total}</strong>
          </div>
        </article>
        <article className={`dashboard-metric ${errorCount > 0 ? "dashboard-metric--danger" : "dashboard-metric--success"}`}>
          <div className="dashboard-metric__icon"><Icon name={errorCount > 0 ? "error" : "check_circle"} /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Validation issues</p>
            <strong className="dashboard-metric__value">{issues.length}</strong>
          </div>
        </article>
      </div>

      {/* Validation summary */}
      <Card title="Schedule validation" subtitle="Room capacity, invigilator coverage, and ratio checks">
        <ValidationPanel issues={issues} loading={schedulesLoading} />
        {errorCount > 0 && isAdmin && status === "no_session" && (
          <p className="text-muted" style={{ marginTop: "10px", fontSize: "0.85rem" }}>
            Resolve all errors before initializing the session.
          </p>
        )}
      </Card>

      {/* Round 1 */}
      {session && session.status !== "no_session" && r1 && (
        <Card
          title="Round 1 — Pre-swap signatures"
          subtitle={`${r1.done} of ${r1.total} signed${r1.complete ? " · Complete" : ""}`}
        >
          <div className="wf-signers">
            {r1.signatures.map((sig, idx) => (
              <SignerRow
                key={sig.order}
                sig={sig as { order: number; username: string; signed_at: string | null }}
                isNext={idx === r1.done && !r1.complete}
                onSign={() => void doAction(async () => { await signWorkflow(1); }, "Round 1 signature recorded.")}
                busy={sessionBusy}
                canSign={canSign && isNextR1}
              />
            ))}
          </div>
          {r1.complete && (
            <div className="wf-round-complete">
              <Icon name="verified" /> Round 1 complete — swaps can now be opened.
            </div>
          )}
        </Card>
      )}

      {/* Round 2 */}
      {session && r1?.complete && r2 && (
        <Card
          title="Round 2 — Post-swap lock"
          subtitle={`${r2.done} of ${r2.total} signed${r2.complete ? " · Locked" : ""}`}
        >
          <div className="wf-signers">
            {r2.signatures.map((sig, idx) => (
              <SignerRow
                key={sig.order}
                sig={sig as { order: number; username: string; signed_at: string | null }}
                isNext={idx === r2.done && !r2.complete}
                onSign={() => void doAction(async () => { await signWorkflow(2); }, "Round 2 signature recorded.")}
                busy={sessionBusy}
                canSign={canSign && isNextR2}
              />
            ))}
          </div>
          {r2.complete && (
            <div className="wf-round-complete">
              <Icon name="lock" /> Schedule locked. Ready for print preparation.
            </div>
          )}
        </Card>
      )}

      {/* No schedules yet */}
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
