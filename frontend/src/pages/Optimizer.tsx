import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs } from "@/components/ui/Tabs";
import { useI18n } from "@/i18n";
import {
  addUnavailability,
  deleteUnavailability,
  getSession,
  getUnavailability,
  initSession,
  runOptimizer,
  signSession,
  type OptimizeSessionData,
  type OptimizerResult,
  type UnavailabilityRecord,
} from "@/services/optimizer.service";
import { listSchedules } from "@/services/schedule.service";
import { useAuth } from "@/store/auth.store";
import { usePeriod } from "@/store/period.store";
import { useUi } from "@/store/ui.store";
import type { ScheduleWithSection } from "@/types/api";
import { formatDate } from "@/utils/format";
import { canManageExamPeriods } from "@/utils/permissions";

function UnavailabilityPanel({
  rows,
  loading,
  onAdd,
  onDelete,
}: {
  rows: UnavailabilityRecord[];
  loading: boolean;
  onAdd: (userId: number, date: string, time?: string, reason?: string) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}) {
  const { t } = useI18n();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ user_id: "", block_date: "", block_time: "", reason: "" });
  const [saving, setSaving] = useState(false);

  const handleAdd = async () => {
    if (!form.user_id || !form.block_date) return;
    setSaving(true);
    try {
      await onAdd(Number(form.user_id), form.block_date, form.block_time || undefined, form.reason || undefined);
      setForm({ user_id: "", block_date: "", block_time: "", reason: "" });
      setShowForm(false);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="optimizer-section">
      <div className="optimizer-section__header">
        <div>
          <h3>{t("optimizer.unavailability.title")}</h3>
          <p className="text-muted">{t("optimizer.unavailability.subtitle")}</p>
        </div>
        <Button type="button" size="sm" variant="outline" onClick={() => setShowForm(true)}>
          {t("optimizer.unavailability.addBlock")}
        </Button>
      </div>

      {loading ? (
        <Skeleton className="dashboard-skeleton" />
      ) : rows.length === 0 ? (
        <p className="text-muted">{t("optimizer.unavailability.empty")}</p>
      ) : (
        <div className="table-wrap">
          <table className="data-table data-table--compact">
            <thead>
              <tr>
                <th>{t("common.staff")}</th>
                <th>{t("common.date")}</th>
                <th>{t("common.time")}</th>
                <th>{t("common.reason")}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id}>
                  <td><strong>{row.full_name ?? t("optimizer.unavailability.userFallback", { id: row.user_id })}</strong></td>
                  <td>{row.block_date}</td>
                  <td>{row.all_day ? t("optimizer.block.allDay") : (row.block_time ?? "-")}</td>
                  <td className="text-muted">{row.reason ?? "-"}</td>
                  <td>
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      onClick={() => void onDelete(row.id)}
                    >
                      {t("common.remove")}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        open={showForm}
        title={t("optimizer.unavailability.modalTitle")}
        onClose={() => setShowForm(false)}
        footer={
          <div className="inline-actions">
            <Button type="button" variant="outline" onClick={() => setShowForm(false)}>{t("common.cancel")}</Button>
            <Button type="button" loading={saving} disabled={!form.user_id || !form.block_date} onClick={() => void handleAdd()}>
              {t("optimizer.unavailability.addBlock")}
            </Button>
          </div>
        }
      >
        <div className="optimizer-block-form">
          <div className="form-field">
            <label htmlFor="block-uid">{t("optimizer.unavailability.form.userId")}</label>
            <input id="block-uid" type="number" placeholder={t("optimizer.unavailability.form.userIdPlaceholder")} value={form.user_id} onChange={(e) => setForm((f) => ({ ...f, user_id: e.target.value }))} />
            <span className="form-hint">{t("optimizer.unavailability.form.userIdHint")}</span>
          </div>
          <div className="form-field">
            <label htmlFor="block-date">{t("common.date")}</label>
            <input id="block-date" type="date" value={form.block_date} onChange={(e) => setForm((f) => ({ ...f, block_date: e.target.value }))} />
          </div>
          <div className="form-field">
            <label htmlFor="block-time">{t("optimizer.unavailability.form.timeSlot")}</label>
            <input id="block-time" type="text" placeholder={t("optimizer.unavailability.form.timeSlotPlaceholder")} value={form.block_time} onChange={(e) => setForm((f) => ({ ...f, block_time: e.target.value }))} />
          </div>
          <div className="form-field">
            <label htmlFor="block-reason">{t("common.reason")}</label>
            <input id="block-reason" type="text" placeholder={t("optimizer.unavailability.form.reasonPlaceholder")} value={form.reason} onChange={(e) => setForm((f) => ({ ...f, reason: e.target.value }))} />
          </div>
        </div>
      </Modal>
    </div>
  );
}

function SessionPanel({
  session,
  onInit,
  onSign,
  busy,
}: {
  session: OptimizeSessionData | null;
  onInit: () => Promise<void>;
  onSign: (round: 1 | 2) => Promise<void>;
  busy: boolean;
}) {
  const { t } = useI18n();

  if (!session || session.status === "no_session") {
    return (
      <div className="optimizer-section">
        <p className="text-muted">{t("optimizer.session.empty")}</p>
        <Button type="button" variant="outline" loading={busy} onClick={() => void onInit()}>
          {t("optimizer.session.initialize")}
        </Button>
      </div>
    );
  }

  const r1 = session.round1;
  const r2 = session.round2;

  return (
    <div className="optimizer-section">
      <div className="optimizer-session-status">
        <span className={`session-badge session-badge--${session.status}`}>{t(`optimizer.session.status.${session.status}`)}</span>
        {session.baseline_saved ? <span className="session-badge session-badge--success">{t("optimizer.session.baselineSaved")}</span> : null}
      </div>

      {r1 ? (
        <div className="optimizer-round">
          <h4>{t("optimizer.session.round1Title", { done: r1.done, total: r1.total })}</h4>
          <div className="optimizer-signers">
            {r1.signatures.map((sig) => (
              <div key={sig.order} className={`optimizer-signer${sig.signed_at ? " signed" : ""}`}>
                <Icon name={sig.signed_at ? "check_circle" : "radio_button_unchecked"} />
                <span>{sig.username}</span>
                {sig.signed_at ? <small>{formatDate(sig.signed_at)}</small> : null}
              </div>
            ))}
          </div>
          {!r1.complete && session.status === "draft" ? (
            <Button type="button" size="sm" loading={busy} onClick={() => void onSign(1)}>
              {t("optimizer.session.signRound1", { signer: session.next_signer_r1 ?? t("optimizer.session.nextSigner") })}
            </Button>
          ) : null}
        </div>
      ) : null}

      {r2 && r1?.complete ? (
        <div className="optimizer-round">
          <h4>{t("optimizer.session.round2Title", { done: r2.done, total: r2.total })}</h4>
          <div className="optimizer-signers">
            {r2.signatures.map((sig) => (
              <div key={sig.order} className={`optimizer-signer${sig.signed_at ? " signed" : ""}`}>
                <Icon name={sig.signed_at ? "check_circle" : "radio_button_unchecked"} />
                <span>{sig.username}</span>
                {sig.signed_at ? <small>{formatDate(sig.signed_at)}</small> : null}
              </div>
            ))}
          </div>
          {!r2.complete && session.status === "swap_open" ? (
            <Button type="button" size="sm" loading={busy} onClick={() => void onSign(2)}>
              {t("optimizer.session.signRound2", { signer: session.next_signer_r2 ?? t("optimizer.session.nextSigner") })}
            </Button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

function RoomAssignmentTable({ schedules }: { schedules: ScheduleWithSection[] }) {
  const { t } = useI18n();

  if (schedules.length === 0) {
    return <EmptyState icon={<Icon name="event_note" />} title={t("optimizer.rooms.emptyTitle")} description={t("optimizer.rooms.emptyDescription")} />;
  }

  return (
    <div className="table-wrap">
      <table className="data-table data-table--compact">
        <thead>
          <tr>
            <th>{t("common.date")}</th>
            <th>{t("common.time")}</th>
            <th>{t("optimizer.rooms.examRoom")}</th>
            <th>{t("common.course")}</th>
            <th>{t("common.section")}</th>
            <th>{t("common.students")}</th>
            <th>{t("common.capacity")}</th>
            <th>{t("optimizer.rooms.invigilators")}</th>
          </tr>
        </thead>
        <tbody>
          {schedules.map((sch) => (
            <tr key={sch.id}>
              <td>{sch.exam_date}</td>
              <td>{sch.exam_time}</td>
              <td>
                <strong>{sch.room?.room_name ?? t("optimizer.rooms.roomPending")}</strong>
                {sch.room?.building ? <small className="text-muted"> {sch.room.building}</small> : null}
                {!sch.room?.building && sch.section?.teaching_room?.room_name ? (
                  <small className="text-muted"> {t("optimizer.rooms.teachingRoom", { room: sch.section.teaching_room.room_name })}</small>
                ) : null}
              </td>
              <td>{sch.section?.course?.course_id ?? "-"}</td>
              <td>{sch.section?.section_no ?? "?"}</td>
              <td>{sch.section?.num_students ?? "-"}</td>
              <td className={sch.room && sch.section && sch.room.capacity < sch.section.num_students ? "text-danger" : ""}>
                {sch.room?.capacity ?? "-"}
              </td>
              <td>
                {sch.supervisions.length === 0 ? (
                  <span className="text-muted">{t("common.none")}</span>
                ) : (
                  <span>{sch.supervisions.map((s) => s.user?.full_name ?? `#${s.id}`).join(", ")}</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function StaffAssignmentTable({ schedules }: { schedules: ScheduleWithSection[] }) {
  const { t } = useI18n();
  const staffMap = new Map<number, { name: string; slots: ScheduleWithSection[] }>();
  for (const sch of schedules) {
    for (const sup of sch.supervisions) {
      if (!sup.user) continue;
      const id = sup.user.id;
      if (!staffMap.has(id)) {
        staffMap.set(id, { name: sup.user.full_name ?? sup.user.username, slots: [] });
      }
      staffMap.get(id)!.slots.push(sch);
    }
  }

  const staffList = [...staffMap.entries()].sort((a, b) => a[1].name.localeCompare(b[1].name));

  if (staffList.length === 0) {
    return <EmptyState icon={<Icon name="groups" />} title={t("optimizer.staff.emptyTitle")} description={t("optimizer.staff.emptyDescription")} />;
  }

  return (
    <div className="table-wrap">
      <table className="data-table data-table--compact">
        <thead>
          <tr>
            <th>{t("common.staff")}</th>
            <th>{t("optimizer.staff.slots")}</th>
            <th>{t("optimizer.staff.assignments")}</th>
          </tr>
        </thead>
        <tbody>
          {staffList.map(([id, staff]) => (
            <tr key={id}>
              <td><strong>{staff.name}</strong></td>
              <td>{staff.slots.length}</td>
              <td>
                <div className="staff-slots">
                  {staff.slots.map((sch) => (
                    <span key={sch.id} className="staff-slot-tag">
                      {t("optimizer.staff.assignmentTag", {
                        date: sch.exam_date,
                        time: sch.exam_time,
                        room: sch.room?.room_name ?? t("optimizer.rooms.roomPendingShort"),
                      })}
                    </span>
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function OptimizerPage() {
  const { t } = useI18n();
  const { toast } = useUi();
  const { activePeriod } = usePeriod();
  const { user } = useAuth();
  const isAdmin = canManageExamPeriods(user);

  const [form, setForm] = useState({
    semester: activePeriod?.semester ?? "2",
    academic_year: activePeriod?.academic_year ?? "2568",
    exam_type: activePeriod?.exam_type ?? "final",
  });

  const [runResult, setRunResult] = useState<OptimizerResult | null>(null);
  const [running, setRunning] = useState(false);

  const [schedules, setSchedules] = useState<ScheduleWithSection[]>([]);
  const [schedulesLoading, setSchedulesLoading] = useState(false);

  const [unavailability, setUnavailability] = useState<UnavailabilityRecord[]>([]);
  const [unavailLoading, setUnavailLoading] = useState(false);

  const [session, setSession] = useState<OptimizeSessionData | null>(null);
  const [sessionBusy, setSessionBusy] = useState(false);

  const [resultsTab, setResultsTab] = useState("rooms");

  const loadUnavailability = useCallback(async () => {
    if (!isAdmin) return;
    setUnavailLoading(true);
    try {
      const rows = await getUnavailability();
      setUnavailability(rows);
    } catch {
      // non-critical
    } finally {
      setUnavailLoading(false);
    }
  }, [isAdmin]);

  const loadSession = useCallback(async () => {
    if (!isAdmin) return;
    try {
      const s = await getSession();
      setSession(s);
    } catch {
      // non-critical
    }
  }, [isAdmin]);

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
    void loadUnavailability();
    void loadSession();
    void loadSchedules();
  }, [loadUnavailability, loadSession, loadSchedules]);

  useEffect(() => {
    if (activePeriod) {
      setForm({
        semester: activePeriod.semester,
        academic_year: activePeriod.academic_year,
        exam_type: activePeriod.exam_type ?? "final",
      });
    }
  }, [activePeriod]);

  const handleRun = async () => {
    setRunning(true);
    try {
      const result = await runOptimizer(form);
      setRunResult(result);
      await loadSchedules();
      await loadSession();
      toast(t("optimizer.toast.completed", {
        assigned: result.sections_assigned,
        total: result.sections_total,
      }), "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : t("optimizer.toast.failed"), "error");
    } finally {
      setRunning(false);
    }
  };

  const handleAddBlock = async (userId: number, date: string, time?: string, reason?: string) => {
    await addUnavailability({ user_id: userId, block_date: date, block_time: time, reason });
    await loadUnavailability();
    toast(t("optimizer.toast.blockAdded"), "success");
  };

  const handleDeleteBlock = async (id: number) => {
    await deleteUnavailability(id);
    await loadUnavailability();
    toast(t("optimizer.toast.blockRemoved"), "warning");
  };

  const handleInitSession = async () => {
    setSessionBusy(true);
    try {
      const s = await initSession();
      setSession(s);
      toast(t("optimizer.toast.sessionInitialized"), "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : t("optimizer.toast.initFailed"), "error");
    } finally {
      setSessionBusy(false);
    }
  };

  const handleSign = async (round: 1 | 2) => {
    setSessionBusy(true);
    try {
      const s = await signSession(round);
      setSession(s);
      toast(t("optimizer.toast.roundSigned", { round }), "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : t("optimizer.toast.signFailed"), "error");
    } finally {
      setSessionBusy(false);
    }
  };

  const violationCount = runResult?.violations?.length ?? 0;

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">{t("optimizer.heroEyebrow")}</span>
          <h1 className="page-hero__title">{t("optimizer.heroTitle")}</h1>
          <p className="page-hero__description">{t("optimizer.heroDescription")}</p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => void loadSchedules()} disabled={schedulesLoading}>
            {t("optimizer.actions.refreshResults")}
          </Button>
        </div>
      </section>

      {isAdmin ? (
        <Card title={t("optimizer.setup.title")} subtitle={t("optimizer.setup.subtitle")}>
          <UnavailabilityPanel
            rows={unavailability}
            loading={unavailLoading}
            onAdd={handleAddBlock}
            onDelete={handleDeleteBlock}
          />
        </Card>
      ) : null}

      <Card title={t("optimizer.run.title")} subtitle={t("optimizer.run.subtitle")}>
        <div className="optimizer-run-row">
          <div className="form-field">
            <label htmlFor="opt-ay">{t("common.academicYear")}</label>
            <input
              id="opt-ay"
              type="text"
              value={form.academic_year}
              onChange={(e) => setForm((f) => ({ ...f, academic_year: e.target.value }))}
            />
          </div>
          <div className="form-field">
            <label htmlFor="opt-sem">{t("common.semester")}</label>
            <select
              id="opt-sem"
              value={form.semester}
              onChange={(e) => setForm((f) => ({ ...f, semester: e.target.value }))}
            >
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="summer">{t("optimizer.form.summer")}</option>
            </select>
          </div>
          <div className="form-field">
            <label htmlFor="opt-type">{t("common.examType")}</label>
            <select
              id="opt-type"
              value={form.exam_type}
              onChange={(e) => setForm((f) => ({ ...f, exam_type: e.target.value }))}
            >
              <option value="midterm">{t("optimizer.form.midterm")}</option>
              <option value="final">{t("optimizer.form.final")}</option>
            </select>
          </div>
          {isAdmin ? (
            <Button type="button" loading={running} onClick={() => void handleRun()}>
              {t("optimizer.actions.run")}
            </Button>
          ) : null}
        </div>

        {runResult ? (
          <div className="optimizer-result-bar">
            <div className="summary-grid">
              <div className="summary-box">
                <span>{t("optimizer.result.assigned")}</span>
                <strong>{runResult.sections_assigned} / {runResult.sections_total}</strong>
              </div>
              <div className="summary-box">
                <span>{t("optimizer.result.fairnessScore")}</span>
                <strong>{runResult.fairness_score}</strong>
              </div>
              <div className={`summary-box${violationCount > 0 ? " summary-box--warning" : ""}`}>
                <span>{t("optimizer.result.violations")}</span>
                <strong>{violationCount}</strong>
              </div>
              <div className={`summary-box${(runResult.paper_distribution_unfilled ?? 0) > 0 ? " summary-box--warning" : ""}`}>
                <span>{t("optimizer.result.paperDistribution")}</span>
                <strong>{runResult.paper_distribution_assigned ?? 0} / {runResult.paper_distribution_slots ?? 0}</strong>
              </div>
            </div>
            {violationCount > 0 ? (
              <ul className="plain-list optimizer-violations">
                {runResult.violations.map((v) => <li key={v}>{v}</li>)}
              </ul>
            ) : null}
            {(runResult.paper_distribution_warnings?.length ?? 0) > 0 ? (
              <ul className="plain-list optimizer-violations">
                {runResult.paper_distribution_warnings?.map((warning) => <li key={warning}>{warning}</li>)}
              </ul>
            ) : null}
          </div>
        ) : null}
      </Card>

      <Card title={t("optimizer.assignments.title")} subtitle={t("optimizer.assignments.subtitle")}>
        <Tabs
          activeKey={resultsTab}
          items={[
            { key: "rooms", label: t("optimizer.tabs.rooms"), badge: schedules.length || undefined },
            { key: "staff", label: t("optimizer.tabs.staff") },
          ]}
          onChange={setResultsTab}
        />

        {schedulesLoading ? (
          <div className="page-stack">
            {[0, 1, 2].map((i) => <Skeleton key={i} className="dashboard-skeleton" />)}
          </div>
        ) : resultsTab === "rooms" ? (
          <RoomAssignmentTable schedules={schedules} />
        ) : (
          <StaffAssignmentTable schedules={schedules} />
        )}
      </Card>

      {isAdmin ? (
        <Card title={t("optimizer.workflow.title")} subtitle={t("optimizer.workflow.subtitle")}>
          <SessionPanel
            session={session}
            onInit={handleInitSession}
            onSign={handleSign}
            busy={sessionBusy}
          />
        </Card>
      ) : null}
    </div>
  );
}
