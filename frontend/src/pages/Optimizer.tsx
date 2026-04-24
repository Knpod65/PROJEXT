import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs } from "@/components/ui/Tabs";
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
import { usePeriod } from "@/store/period.store";
import { useUi } from "@/store/ui.store";
import type { ScheduleWithSection } from "@/types/api";
import { formatDate } from "@/utils/format";
import { useAuth } from "@/store/auth.store";
import { getEffectiveRole } from "@/utils/roles";

// ── Pre-optimization: unavailability panel ─────────────────────

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
          <h3>Staff unavailability</h3>
          <p className="text-muted">Block staff from specific dates before running the optimizer.</p>
        </div>
        <Button type="button" size="sm" variant="outline" onClick={() => setShowForm(true)}>
          Add block
        </Button>
      </div>

      {loading ? (
        <Skeleton className="dashboard-skeleton" />
      ) : rows.length === 0 ? (
        <p className="text-muted">No unavailability blocks. All staff are currently available.</p>
      ) : (
        <div className="table-wrap">
          <table className="data-table data-table--compact">
            <thead>
              <tr>
                <th>Staff</th>
                <th>Date</th>
                <th>Time</th>
                <th>Reason</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id}>
                  <td><strong>{row.full_name ?? `User #${row.user_id}`}</strong></td>
                  <td>{row.block_date}</td>
                  <td>{row.all_day ? "All day" : (row.block_time ?? "—")}</td>
                  <td className="text-muted">{row.reason ?? "—"}</td>
                  <td>
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      onClick={() => void onDelete(row.id)}
                    >
                      Remove
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
        title="Block staff date"
        onClose={() => setShowForm(false)}
        footer={
          <div className="inline-actions">
            <Button type="button" variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
            <Button type="button" loading={saving} disabled={!form.user_id || !form.block_date} onClick={() => void handleAdd()}>
              Add block
            </Button>
          </div>
        }
      >
        <div className="optimizer-block-form">
          <div className="form-field">
            <label htmlFor="block-uid">User ID</label>
            <input id="block-uid" type="number" placeholder="Enter user ID" value={form.user_id} onChange={(e) => setForm((f) => ({ ...f, user_id: e.target.value }))} />
            <span className="form-hint">Enter the numeric user ID of the staff member.</span>
          </div>
          <div className="form-field">
            <label htmlFor="block-date">Date</label>
            <input id="block-date" type="date" value={form.block_date} onChange={(e) => setForm((f) => ({ ...f, block_date: e.target.value }))} />
          </div>
          <div className="form-field">
            <label htmlFor="block-time">Time slot (optional — leave blank for all-day)</label>
            <input id="block-time" type="text" placeholder="e.g. 09:00 or 09.00-12.00" value={form.block_time} onChange={(e) => setForm((f) => ({ ...f, block_time: e.target.value }))} />
          </div>
          <div className="form-field">
            <label htmlFor="block-reason">Reason (optional)</label>
            <input id="block-reason" type="text" placeholder="e.g. Medical leave" value={form.reason} onChange={(e) => setForm((f) => ({ ...f, reason: e.target.value }))} />
          </div>
        </div>
      </Modal>
    </div>
  );
}

// ── Session workflow panel ─────────────────────────────────────

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
  if (!session || session.status === "no_session") {
    return (
      <div className="optimizer-section">
        <p className="text-muted">No session. Run the optimizer first, then initialize a session.</p>
        <Button type="button" variant="outline" loading={busy} onClick={() => void onInit()}>
          Initialize session
        </Button>
      </div>
    );
  }

  const r1 = session.round1;
  const r2 = session.round2;

  return (
    <div className="optimizer-section">
      <div className="optimizer-session-status">
        <span className={`session-badge session-badge--${session.status}`}>{session.status.replace("_", " ")}</span>
        {session.baseline_saved && <span className="session-badge session-badge--success">Baseline saved</span>}
      </div>

      {r1 && (
        <div className="optimizer-round">
          <h4>Round 1 — Pre-swap confirmation ({r1.done}/{r1.total})</h4>
          <div className="optimizer-signers">
            {r1.signatures.map((sig) => (
              <div key={sig.order} className={`optimizer-signer${sig.signed_at ? " signed" : ""}`}>
                <Icon name={sig.signed_at ? "check_circle" : "radio_button_unchecked"} />
                <span>{sig.username}</span>
                {sig.signed_at && <small>{formatDate(sig.signed_at)}</small>}
              </div>
            ))}
          </div>
          {!r1.complete && session.status === "draft" && (
            <Button type="button" size="sm" loading={busy} onClick={() => void onSign(1)}>
              Sign round 1 (as {session.next_signer_r1 ?? "next signer"})
            </Button>
          )}
        </div>
      )}

      {r2 && r1?.complete && (
        <div className="optimizer-round">
          <h4>Round 2 — Post-swap lock ({r2.done}/{r2.total})</h4>
          <div className="optimizer-signers">
            {r2.signatures.map((sig) => (
              <div key={sig.order} className={`optimizer-signer${sig.signed_at ? " signed" : ""}`}>
                <Icon name={sig.signed_at ? "check_circle" : "radio_button_unchecked"} />
                <span>{sig.username}</span>
                {sig.signed_at && <small>{formatDate(sig.signed_at)}</small>}
              </div>
            ))}
          </div>
          {!r2.complete && session.status === "swap_open" && (
            <Button type="button" size="sm" loading={busy} onClick={() => void onSign(2)}>
              Sign round 2 (as {session.next_signer_r2 ?? "next signer"})
            </Button>
          )}
        </div>
      )}
    </div>
  );
}

// ── Results: room & staff assignment tables ─────────────────────

function RoomAssignmentTable({ schedules }: { schedules: ScheduleWithSection[] }) {
  if (schedules.length === 0) {
    return <EmptyState icon={<Icon name="event_note" />} title="No schedules available." description="Run the optimizer to generate assignments." />;
  }

  return (
    <div className="table-wrap">
      <table className="data-table data-table--compact">
        <thead>
          <tr>
            <th>Date</th>
            <th>Time</th>
            <th>Exam room</th>
            <th>Course</th>
            <th>Section</th>
            <th>Students</th>
            <th>Capacity</th>
            <th>Invigilators</th>
          </tr>
        </thead>
        <tbody>
          {schedules.map((sch) => (
            <tr key={sch.id}>
              <td>{sch.exam_date}</td>
              <td>{sch.exam_time}</td>
              <td>
                <strong>{sch.room?.room_name ?? "Exam room not assigned yet"}</strong>
                {sch.room?.building && <small className="text-muted"> {sch.room.building}</small>}
                {!sch.room?.building && sch.section?.teaching_room?.room_name && (
                  <small className="text-muted"> Teaching room: {sch.section.teaching_room.room_name}</small>
                )}
              </td>
              <td>{sch.section?.course?.course_id ?? "—"}</td>
              <td>§{sch.section?.section_no ?? "?"}</td>
              <td>{sch.section?.num_students ?? "—"}</td>
              <td className={sch.room && sch.section && sch.room.capacity < sch.section.num_students ? "text-danger" : ""}>
                {sch.room?.capacity ?? "—"}
              </td>
              <td>
                {sch.supervisions.length === 0 ? (
                  <span className="text-muted">None</span>
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
  // Flatten supervisions grouped by staff member
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

  const staffList = [...staffMap.entries()].sort((a, b) =>
    a[1].name.localeCompare(b[1].name),
  );

  if (staffList.length === 0) {
    return <EmptyState icon={<Icon name="groups" />} title="No staff assignments yet." description="Run the optimizer to generate assignments." />;
  }

  return (
    <div className="table-wrap">
      <table className="data-table data-table--compact">
        <thead>
          <tr>
            <th>Staff member</th>
            <th>Slots</th>
            <th>Assignments</th>
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
                      {sch.exam_date} {sch.exam_time} · Exam room: {sch.room?.room_name ?? "not assigned yet"}
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

// ── Main page ──────────────────────────────────────────────────

export function OptimizerPage() {
  const { toast } = useUi();
  const { activePeriod } = usePeriod();
  const { user } = useAuth();
  const role = getEffectiveRole(user);
  const isAdmin = role === "admin";

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

  // Sync form with active period when it loads
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
      toast(`Optimizer complete: ${result.sections_assigned}/${result.sections_total} sections assigned.`, "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Optimizer failed.", "error");
    } finally {
      setRunning(false);
    }
  };

  const handleAddBlock = async (userId: number, date: string, time?: string, reason?: string) => {
    await addUnavailability({ user_id: userId, block_date: date, block_time: time, reason });
    await loadUnavailability();
    toast("Unavailability block added.", "success");
  };

  const handleDeleteBlock = async (id: number) => {
    await deleteUnavailability(id);
    await loadUnavailability();
    toast("Block removed.", "warning");
  };

  const handleInitSession = async () => {
    setSessionBusy(true);
    try {
      const s = await initSession();
      setSession(s);
      toast("Session initialized.", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to init session.", "error");
    } finally {
      setSessionBusy(false);
    }
  };

  const handleSign = async (round: 1 | 2) => {
    setSessionBusy(true);
    try {
      const s = await signSession(round);
      setSession(s);
      toast(`Round ${round} signature recorded.`, "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to sign.", "error");
    } finally {
      setSessionBusy(false);
    }
  };

  const violationCount = runResult?.violations?.length ?? 0;

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">Exam optimization</span>
          <h1 className="page-hero__title">Schedule & invigilator assignment</h1>
          <p className="page-hero__description">
            Configure constraints, run the optimizer, then review exam-room and staff assignments before confirming.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => void loadSchedules()} disabled={schedulesLoading}>
            Refresh results
          </Button>
        </div>
      </section>

      {/* ── Pre-optimization: constraints ── */}
      {isAdmin && (
        <Card title="Pre-optimization setup" subtitle="Staff blocks are applied before the optimizer runs">
          <UnavailabilityPanel
            rows={unavailability}
            loading={unavailLoading}
            onAdd={handleAddBlock}
            onDelete={handleDeleteBlock}
          />
        </Card>
      )}

      {/* ── Run optimizer ── */}
      <Card title="Run optimizer" subtitle="Assign exam rooms and invigilators for the selected term">
        <div className="optimizer-run-row">
          <div className="form-field">
            <label htmlFor="opt-ay">Academic year</label>
            <input
              id="opt-ay"
              type="text"
              value={form.academic_year}
              onChange={(e) => setForm((f) => ({ ...f, academic_year: e.target.value }))}
            />
          </div>
          <div className="form-field">
            <label htmlFor="opt-sem">Semester</label>
            <select
              id="opt-sem"
              value={form.semester}
              onChange={(e) => setForm((f) => ({ ...f, semester: e.target.value }))}
            >
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="summer">Summer</option>
            </select>
          </div>
          <div className="form-field">
            <label htmlFor="opt-type">Exam type</label>
            <select
              id="opt-type"
              value={form.exam_type}
              onChange={(e) => setForm((f) => ({ ...f, exam_type: e.target.value }))}
            >
              <option value="midterm">Midterm</option>
              <option value="final">Final</option>
            </select>
          </div>
          {isAdmin && (
            <Button type="button" loading={running} onClick={() => void handleRun()}>
              Run optimizer
            </Button>
          )}
        </div>

        {runResult && (
          <div className="optimizer-result-bar">
            <div className="summary-grid">
              <div className="summary-box">
                <span>Assigned</span>
                <strong>{runResult.sections_assigned} / {runResult.sections_total}</strong>
              </div>
              <div className="summary-box">
                <span>Fairness score</span>
                <strong>{runResult.fairness_score}</strong>
              </div>
              <div className={`summary-box${violationCount > 0 ? " summary-box--warning" : ""}`}>
                <span>Violations</span>
                <strong>{violationCount}</strong>
              </div>
              <div className={`summary-box${(runResult.paper_distribution_unfilled ?? 0) > 0 ? " summary-box--warning" : ""}`}>
                <span>Paper distribution</span>
                <strong>{runResult.paper_distribution_assigned ?? 0} / {runResult.paper_distribution_slots ?? 0}</strong>
              </div>
            </div>
            {violationCount > 0 && (
              <ul className="plain-list optimizer-violations">
                {runResult.violations.map((v) => <li key={v}>{v}</li>)}
              </ul>
            )}
            {(runResult.paper_distribution_warnings?.length ?? 0) > 0 && (
              <ul className="plain-list optimizer-violations">
                {runResult.paper_distribution_warnings?.map((warning) => <li key={warning}>{warning}</li>)}
              </ul>
            )}
          </div>
        )}
      </Card>

      {/* ── Results: room & staff assignments ── */}
      <Card title="Assignment results" subtitle="Current exam-room and invigilator allocations for the active period">
        <Tabs
          activeKey={resultsTab}
          items={[
            { key: "rooms", label: "Exam room assignments", badge: schedules.length || undefined },
            { key: "staff", label: "Staff assignments" },
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

      {/* ── 4-signature workflow session ── */}
      {isAdmin && (
        <Card title="Approval workflow" subtitle="4-signature confirmation — round 1 before swap, round 2 to lock">
          <SessionPanel
            session={session}
            onInit={handleInitSession}
            onSign={handleSign}
            busy={sessionBusy}
          />
        </Card>
      )}
    </div>
  );
}
