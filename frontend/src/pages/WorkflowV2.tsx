import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Skeleton } from "@/components/ui/Skeleton";
import { useI18n } from "@/i18n";
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
import { canManageExamPeriods, canSignWorkflow } from "@/utils/permissions";
import { getEffectiveRole } from "@/utils/roles";

const ISSUE_TYPES: WorkflowIssueType[] = [
  "no_invigilator_assigned",
  "room_capacity_exceeded",
  "high_student_invigilator_ratio",
  "external_staff_shortage",
];

const STAGE_KEYS = [
  { key: "no_session", labelKey: "workflowV2.stage.notStarted" },
  { key: "draft", labelKey: "workflowV2.stage.round1" },
  { key: "confirming", labelKey: "workflowV2.stage.confirming" },
  { key: "confirmed", labelKey: "workflowV2.stage.confirmed" },
  { key: "swap_open", labelKey: "workflowV2.stage.swapWindow" },
  { key: "locked", labelKey: "workflowV2.stage.locked" },
] as const;

function getIssueLabel(t: ReturnType<typeof useI18n>["t"], type: WorkflowIssueType) {
  return t(`workflowV2.issueType.${type}`);
}

function StageTimeline({ status }: { status: string }) {
  const { t } = useI18n();
  const index = STAGE_KEYS.findIndex((stage) => stage.key === status);

  return (
    <div className="wf-stage-timeline">
      {STAGE_KEYS.filter((stage) => stage.key !== "no_session").map((stage, stageIndex) => {
        const currentIndex = stageIndex + 1;
        const done = index >= currentIndex;
        const active = index === currentIndex;
        return (
          <div key={stage.key} className={`wf-stage${done ? " done" : ""}${active ? " active" : ""}`}>
            <div className="wf-stage__dot">
              {done ? <Icon name="check" /> : <span>{stageIndex + 1}</span>}
            </div>
            <span className="wf-stage__label">{t(stage.labelKey)}</span>
            {stageIndex < STAGE_KEYS.length - 2 && <div className="wf-stage__line" />}
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
  sig: { order: number; user?: string | null; signed_at?: string | null };
  isNext: boolean;
  onSign: () => void;
  busy: boolean;
  canSign: boolean;
}) {
  const { t } = useI18n();

  return (
    <div className={`wf-signer${sig.signed_at ? " signed" : ""}${isNext ? " next" : ""}`}>
      <Icon name={sig.signed_at ? "check_circle" : isNext ? "radio_button_checked" : "radio_button_unchecked"} />
      <div className="wf-signer__info">
        <strong>{sig.user ?? t("workflowV2.signers.unknown")}</strong>
        {sig.signed_at ? (
          <small>{new Date(sig.signed_at).toLocaleString()}</small>
        ) : isNext ? (
          <small className="text-muted">{t("workflowV2.signers.awaitingSignature")}</small>
        ) : null}
      </div>
      {isNext && canSign ? (
        <Button type="button" size="sm" loading={busy} onClick={onSign}>
          {t("workflowV2.actions.sign")}
        </Button>
      ) : null}
    </div>
  );
}

function computeInternalIssues(
  schedules: ScheduleWithSection[],
  t: ReturnType<typeof useI18n>["t"],
): WorkflowIssueItem[] {
  const issues: WorkflowIssueItem[] = [];

  for (const schedule of schedules) {
    const students = schedule.section?.num_students ?? 0;
    const capacity = schedule.room?.capacity ?? 0;
    const invigilators = schedule.supervisions.length;
    const courseCode = schedule.section?.course?.course_id ?? "-";
    const sectionNo = schedule.section?.section_no ?? "-";
    const reference = t("workflowV2.issue.reference", { course: courseCode, section: sectionNo });

    if (capacity > 0 && students > capacity) {
      issues.push({
        id: `capacity-${schedule.id}`,
        type: "room_capacity_exceeded",
        severity: "error",
        scope: "internal",
        title: getIssueLabel(t, "room_capacity_exceeded"),
        message: t("workflowV2.issue.message.roomCapacityExceeded", {
          room: schedule.room?.room_name ?? t("workflowV2.issue.unassignedRoom"),
          capacity,
          students,
        }),
        reference,
      });
    }

    if (invigilators === 0) {
      issues.push({
        id: `invig-${schedule.id}`,
        type: "no_invigilator_assigned",
        severity: "error",
        scope: "internal",
        title: getIssueLabel(t, "no_invigilator_assigned"),
        message: t("workflowV2.issue.message.noInvigilatorAssigned", {
          reference,
          date: schedule.exam_date,
          time: schedule.exam_time,
        }),
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
          title: getIssueLabel(t, "high_student_invigilator_ratio"),
          message: t("workflowV2.issue.message.highRatio", {
            reference,
            ratio: Math.round(ratio),
          }),
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
  const { t } = useI18n();

  const groups = useMemo(() => {
    return ISSUE_TYPES
      .map((type) => ({
        type,
        label: getIssueLabel(t, type),
        count: issues.filter((issue) => issue.type === type).length,
      }))
      .filter((group) => group.count > 0);
  }, [issues, t]);

  if (loading) {
    return <Skeleton className="dashboard-skeleton" />;
  }

  if (issues.length === 0) {
    return (
      <div className="wf-validation wf-validation--ok">
        <Icon name="check_circle" />
        <span>{t("workflowV2.issue.noneDetected")}</span>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <div className="stitch-metric-grid">
        <article className="dashboard-metric dashboard-metric--danger">
          <div className="dashboard-metric__icon"><Icon name="error" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("common.errors")}</p>
            <strong className="dashboard-metric__value">{issues.filter((issue) => issue.severity === "error").length}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--warning">
          <div className="dashboard-metric__icon"><Icon name="warning" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("common.warnings")}</p>
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
          {t("workflowV2.filters.allIssues")}
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
  const { t } = useI18n();
  const { toast } = useUi();
  const { user } = useAuth();
  const { activePeriod } = usePeriod();
  const role = getEffectiveRole(user);
  const isAdmin = canManageExamPeriods(user);
  const canSign = canSignWorkflow(user);

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

  const internalIssues = useMemo(() => computeInternalIssues(schedules, t), [schedules, t]);
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
      toast(err instanceof Error ? err.message : t("workflowV2.toast.actionFailed"), "error");
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
  const activeExamTypeLabel =
    activePeriod?.exam_type === "midterm"
      ? t("optimizer.form.midterm")
      : activePeriod?.exam_type === "final"
        ? t("optimizer.form.final")
        : activePeriod?.exam_type ?? "";

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
          <span className="page-hero__eyebrow">{t("workflowV2.heroEyebrow")}</span>
          <h1 className="page-hero__title">{t("workflowV2.heroTitle")}</h1>
          <p className="page-hero__description">{t("workflowV2.heroDescription")}</p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => { void loadSession(); void loadSchedules(); void loadExternalIssues(); }}>
            {t("common.refresh")}
          </Button>
          {isAdmin && status === "no_session" ? (
            <Button
              type="button"
              disabled={errorCount > 0}
              loading={sessionBusy}
              onClick={() => void doAction(async () => { await initWorkflowSession(); }, t("workflowV2.toast.sessionInitialized"))}
            >
              {t("workflowV2.actions.initializeSession")}
            </Button>
          ) : null}
          {isAdmin && status === "confirmed" ? (
            <Button
              type="button"
              variant="outline"
              loading={sessionBusy}
              onClick={() => void doAction(async () => { await openSwapWindow(); }, t("workflowV2.toast.swapWindowOpened"))}
            >
              {t("workflowV2.actions.openSwapWindow")}
            </Button>
          ) : null}
        </div>
      </section>

      {activePeriod ? (
        <div className="wf-period-bar">
          <Icon name="calendar_month" />
          <span>{t("workflowV2.activePeriod", { label: activePeriod.label })}</span>
          <span className="wf-period-bar__status">
            {t("workflowV2.activePeriodStatus", {
              examType: activeExamTypeLabel,
              semester: activePeriod.semester,
            })}
          </span>
        </div>
      ) : null}

      <Card title={t("workflowV2.status.title")} subtitle={t("workflowV2.status.subtitle")}>
        {sessionLoading ? (
          <Skeleton className="dashboard-skeleton" />
        ) : (
          <>
            <StageTimeline status={status} />
            {status === "no_session" ? (
              <p className="text-muted" style={{ marginTop: "12px" }}>
                {t("workflowV2.status.noSessionNote")}
              </p>
            ) : null}
          </>
        )}
      </Card>

      <div className="stitch-metric-grid">
        <article className="dashboard-metric dashboard-metric--accent">
          <div className="dashboard-metric__icon"><Icon name="event_note" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("workflowV2.metrics.schedules")}</p>
            <strong className="dashboard-metric__value">{scheduleStats.total}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--neutral">
          <div className="dashboard-metric__icon"><Icon name="meeting_room" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("workflowV2.metrics.withRoom")}</p>
            <strong className="dashboard-metric__value">{scheduleStats.withRoom}</strong>
          </div>
        </article>
        <article className={`dashboard-metric ${scheduleStats.withInvigilator < scheduleStats.total ? "dashboard-metric--warning" : "dashboard-metric--success"}`}>
          <div className="dashboard-metric__icon"><Icon name="groups" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("workflowV2.metrics.withInvigilators")}</p>
            <strong className="dashboard-metric__value">{scheduleStats.withInvigilator} / {scheduleStats.total}</strong>
          </div>
        </article>
        <article className={`dashboard-metric ${issues.length > 0 ? "dashboard-metric--warning" : "dashboard-metric--success"}`}>
          <div className="dashboard-metric__icon"><Icon name={issues.length > 0 ? "warning" : "check_circle"} /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("workflowV2.metrics.visibleIssues")}</p>
            <strong className="dashboard-metric__value">{issues.length}</strong>
          </div>
        </article>
      </div>

      <Card title={t("workflowV2.issues.title")} subtitle={t("workflowV2.issues.subtitle")}>
        <IssueSummary
          issues={issues}
          filter={issueFilter}
          onFilterChange={setIssueFilter}
          loading={schedulesLoading || externalLoading}
        />
        {issues.length > 0 ? (
          <DataTable<WorkflowIssueItem>
            columns={[
              {
                key: "title",
                label: t("workflowV2.table.issue"),
                width: "22%",
                render: (row) => (
                  <div className="data-table__content data-table__content--clamp">
                    <strong>{row.title}</strong>
                    <p>{row.scope === "external" ? t("workflowV2.scope.external") : t("workflowV2.scope.internal")}</p>
                  </div>
                ),
              },
              {
                key: "severity",
                label: t("workflowV2.table.severity"),
                width: "12%",
                render: (row) => (
                  <span className={`wf-issue-chip wf-issue-chip--${row.severity}`}>
                    <Icon name={row.severity === "error" ? "error" : "warning"} /> {t(`workflowV2.severity.${row.severity}`)}
                  </span>
                ),
              },
              {
                key: "reference",
                label: t("workflowV2.table.reference"),
                width: "18%",
              },
              {
                key: "message",
                label: t("workflowV2.table.details"),
                width: "48%",
              },
            ]}
            emptyTitle={t("workflowV2.issues.emptyTitle")}
            rowKey={(row) => row.id}
            rows={filteredIssues}
            scrollThreshold={5}
            tableLayout="fixed"
          />
        ) : null}
        {errorCount > 0 && isAdmin && status === "no_session" ? (
          <p className="text-muted" style={{ marginTop: "10px", fontSize: "0.85rem" }}>
            {t("workflowV2.issues.blockingNote")}
          </p>
        ) : null}
      </Card>

      {session && status !== "no_session" && round1 ? (
        <Card
          title={t("workflowV2.round1.title")}
          subtitle={t("workflowV2.roundProgress", {
            done: round1.done,
            total: round1.total,
            status: round1.complete ? t("workflowV2.roundStatus.complete") : "",
          }).trim()}
        >
          <div className="wf-signers">
            {round1.signatures.map((signature, index) => (
              <SignerRow
                key={signature.order}
                sig={signature}
                isNext={index === round1.done && !round1.complete}
                onSign={() => void doAction(async () => { await signWorkflow(1); }, t("workflowV2.toast.round1Signed"))}
                busy={sessionBusy}
                canSign={canSign && isNextRound1}
              />
            ))}
          </div>
          {round1.complete ? (
            <div className="wf-round-complete">
              <Icon name="verified" /> {t("workflowV2.round1.completeMessage")}
            </div>
          ) : null}
        </Card>
      ) : null}

      {session && round1?.complete && round2 ? (
        <Card
          title={t("workflowV2.round2.title")}
          subtitle={t("workflowV2.roundProgress", {
            done: round2.done,
            total: round2.total,
            status: round2.complete ? t("workflowV2.roundStatus.locked") : "",
          }).trim()}
        >
          <div className="wf-signers">
            {round2.signatures.map((signature, index) => (
              <SignerRow
                key={signature.order}
                sig={signature}
                isNext={index === round2.done && !round2.complete}
                onSign={() => void doAction(async () => { await signWorkflow(2); }, t("workflowV2.toast.round2Signed"))}
                busy={sessionBusy}
                canSign={canSign && isNextRound2}
              />
            ))}
          </div>
          {round2.complete ? (
            <div className="wf-round-complete">
              <Icon name="lock" /> {t("workflowV2.round2.completeMessage")}
            </div>
          ) : null}
        </Card>
      ) : null}

      {!schedulesLoading && schedules.length === 0 ? (
        <Card title={t("workflowV2.noScheduleCardTitle")}>
          <EmptyState
            icon={<Icon name="event_busy" />}
            title={t("workflowV2.noScheduleTitle")}
            description={t("workflowV2.noScheduleDescription")}
          />
        </Card>
      ) : null}
    </div>
  );
}
