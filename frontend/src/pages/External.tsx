import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import {
  createExternalExam,
  deleteExternalExam,
  listExternalExams,
  updateExternalExam,
} from "@/services/external.service";
import { post } from "@/services/api";
import { useAuth } from "@/store/auth.store";
import { useUi } from "@/store/ui.store";
import type { ExternalExam } from "@/types/api";
import { getEffectiveRole } from "@/utils/roles";

// ── Status badge ───────────────────────────────────────────────

function ExamStatusBadge({ status }: { status: string | undefined }) {
  const s = status ?? "draft";
  const map: Record<string, string> = {
    draft: "ext-badge ext-badge--draft",
    confirmed: "ext-badge ext-badge--confirmed",
    completed: "ext-badge ext-badge--completed",
    cancelled: "ext-badge ext-badge--cancelled",
  };
  return <span className={map[s] ?? "ext-badge"}>{s}</span>;
}

// ── Exam form ──────────────────────────────────────────────────

interface ExamFormData {
  title: string;
  organizer: string;
  exam_date: string;
  exam_time: string;
  room_name: string;
  num_students: number | "";
  invigilators_needed: number | "";
  notes: string;
}

function emptyForm(): ExamFormData {
  return {
    title: "",
    organizer: "",
    exam_date: "",
    exam_time: "",
    room_name: "",
    num_students: "",
    invigilators_needed: 1,
    notes: "",
  };
}

function ExamFormModal({
  exam,
  open,
  busy,
  onClose,
  onSave,
}: {
  exam: ExternalExam | null;
  open: boolean;
  busy: boolean;
  onClose: () => void;
  onSave: (data: ExamFormData) => Promise<void>;
}) {
  const [form, setForm] = useState<ExamFormData>(emptyForm);

  useEffect(() => {
    if (exam) {
      setForm({
        title: exam.title ?? "",
        organizer: exam.organizer ?? "",
        exam_date: exam.exam_date ?? "",
        exam_time: exam.exam_time ?? "",
        room_name: exam.room_name ?? "",
        num_students: exam.num_students ?? "",
        invigilators_needed: exam.invigilators_needed ?? 1,
        notes: exam.notes ?? "",
      });
    } else {
      setForm(emptyForm());
    }
  }, [exam, open]);

  const set = (k: keyof ExamFormData, v: string | number | "") =>
    setForm((f) => ({ ...f, [k]: v }));

  const canSave = form.title.trim() !== "" && form.exam_date !== "";

  return (
    <Modal
      open={open}
      title={exam ? "Edit external exam" : "Create external exam"}
      onClose={onClose}
      footer={
        <div className="inline-actions">
          <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="button" disabled={!canSave} loading={busy} onClick={() => void onSave(form)}>
            {exam ? "Save changes" : "Create exam"}
          </Button>
        </div>
      }
    >
      <div className="ext-form">
        <div className="form-field">
          <label htmlFor="ext-title">Exam / activity name</label>
          <input id="ext-title" type="text" value={form.title} placeholder="e.g. TOEFL Mock Test" onChange={(e) => set("title", e.target.value)} />
        </div>
        <div className="import-upload-grid">
          <div className="form-field">
            <label htmlFor="ext-organizer">Organizer (optional)</label>
            <input id="ext-organizer" type="text" value={form.organizer} placeholder="e.g. Faculty of Arts" onChange={(e) => set("organizer", e.target.value)} />
          </div>
          <div className="form-field">
            <label htmlFor="ext-room">Room / venue (optional)</label>
            <input id="ext-room" type="text" value={form.room_name} placeholder="e.g. Hall A" onChange={(e) => set("room_name", e.target.value)} />
          </div>
          <div className="form-field">
            <label htmlFor="ext-date">Date</label>
            <input id="ext-date" type="date" value={form.exam_date} onChange={(e) => set("exam_date", e.target.value)} />
          </div>
          <div className="form-field">
            <label htmlFor="ext-time">Time</label>
            <input id="ext-time" type="text" placeholder="e.g. 09:00-12:00" value={form.exam_time} onChange={(e) => set("exam_time", e.target.value)} />
          </div>
          <div className="form-field">
            <label htmlFor="ext-students">Expected attendees</label>
            <input id="ext-students" type="number" min={0} value={form.num_students} onChange={(e) => set("num_students", e.target.value === "" ? "" : Number(e.target.value))} />
          </div>
          <div className="form-field">
            <label htmlFor="ext-invigs">Staff required</label>
            <input id="ext-invigs" type="number" min={1} value={form.invigilators_needed} onChange={(e) => set("invigilators_needed", e.target.value === "" ? "" : Number(e.target.value))} />
            <span className="form-hint">Number of invigilators needed</span>
          </div>
        </div>
        <div className="form-field">
          <label htmlFor="ext-notes">Notes (optional)</label>
          <textarea id="ext-notes" rows={2} value={form.notes} placeholder="Any special instructions…" onChange={(e) => set("notes", e.target.value)} />
        </div>
      </div>
    </Modal>
  );
}

// ── Exam card ──────────────────────────────────────────────────

function ExamCard({
  exam,
  isAdmin,
  onEdit,
  onAssign,
  onDelete,
}: {
  exam: ExternalExam;
  isAdmin: boolean;
  onEdit: () => void;
  onAssign: () => void;
  onDelete: () => void;
}) {
  const assigned = exam.supervisions?.length ?? 0;
  const needed = exam.invigilators_needed ?? 0;
  const staffReady = assigned >= needed;

  return (
    <article className="ext-exam-card">
      <div className="ext-exam-card__header">
        <div>
          <strong className="ext-exam-card__title">{exam.title ?? "External Exam"}</strong>
          {exam.organizer && <span className="text-muted ext-exam-card__organizer">{exam.organizer}</span>}
        </div>
        <ExamStatusBadge status={exam.status} />
      </div>

      <div className="ext-exam-card__meta">
        <span><Icon name="event" /> {exam.exam_date ?? "—"} {exam.exam_time ?? ""}</span>
        <span><Icon name="meeting_room" /> {exam.room_name ?? "No room set"}</span>
        <span><Icon name="groups" /> {exam.num_students ?? 0} attendees</span>
        <span className={staffReady ? "ext-staff-ok" : "ext-staff-missing"}>
          <Icon name={staffReady ? "check_circle" : "warning"} />
          {assigned}/{needed} staff assigned
        </span>
      </div>

      {exam.supervisions && exam.supervisions.length > 0 && (
        <div className="ext-invig-list">
          {exam.supervisions.map((s) => (
            <span key={s.id} className="staff-slot-tag">
              {s.user_name ?? `User #${s.id}`}
              {s.confirmed && <Icon name="check" />}
            </span>
          ))}
        </div>
      )}

      {exam.notes && <p className="ext-exam-card__notes text-muted">{exam.notes}</p>}

      {isAdmin && (
        <div className="inline-actions ext-exam-card__actions">
          <Button type="button" size="sm" variant="outline" onClick={onEdit}>Edit</Button>
          {!staffReady && (
            <Button type="button" size="sm" onClick={onAssign}>
              Auto-assign staff
            </Button>
          )}
          <Button type="button" size="sm" variant="ghost" onClick={onDelete}>
            Delete
          </Button>
        </div>
      )}
    </article>
  );
}

// ── Main page ──────────────────────────────────────────────────

export function ExternalPage() {
  const { toast } = useUi();
  const { user } = useAuth();
  const role = getEffectiveRole(user);
  const isAdmin = role === "admin";

  const [exams, setExams] = useState<ExternalExam[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editTarget, setEditTarget] = useState<ExternalExam | null>(null);
  const [formBusy, setFormBusy] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listExternalExams();
      setExams(data);
    } catch {
      setExams([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void load(); }, [load]);

  const handleSave = async (data: ExamFormData) => {
    setFormBusy(true);
    try {
      if (editTarget) {
        await updateExternalExam(editTarget.id, data as unknown as Record<string, unknown>);
        toast("Exam updated.", "success");
      } else {
        await createExternalExam(data as unknown as Record<string, unknown>);
        toast("Exam created.", "success");
      }
      setShowForm(false);
      setEditTarget(null);
      await load();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to save.", "error");
    } finally {
      setFormBusy(false);
    }
  };

  const handleDelete = async (exam: ExternalExam) => {
    try {
      await deleteExternalExam(exam.id);
      toast("Exam deleted.", "warning");
      await load();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to delete.", "error");
    }
  };

  const handleAutoAssign = async (examId: number) => {
    try {
      await post<unknown>(`/external/${examId}/assign`);
      toast("Staff auto-assigned using fairness algorithm.", "success");
      await load();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Auto-assign failed.", "error");
    }
  };

  const totalStaff = exams.reduce((acc, e) => acc + (e.supervisions?.length ?? 0), 0);
  const pendingAssign = exams.filter((e) => (e.supervisions?.length ?? 0) < (e.invigilators_needed ?? 1)).length;

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">Special events</span>
          <h1 className="page-hero__title">External exams</h1>
          <p className="page-hero__description">
            Manage special exam sessions outside the standard timetable. Staff are assigned using the same fairness algorithm as the optimizer.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => void load()} disabled={loading}>
            Refresh
          </Button>
          {isAdmin && (
            <Button type="button" onClick={() => { setEditTarget(null); setShowForm(true); }}>
              Create exam
            </Button>
          )}
        </div>
      </section>

      <div className="stitch-metric-grid">
        <article className="dashboard-metric dashboard-metric--accent">
          <div className="dashboard-metric__icon"><Icon name="language" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Total exams</p>
            <strong className="dashboard-metric__value">{exams.length}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--neutral">
          <div className="dashboard-metric__icon"><Icon name="groups" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Staff assigned</p>
            <strong className="dashboard-metric__value">{totalStaff}</strong>
          </div>
        </article>
        <article className={`dashboard-metric ${pendingAssign > 0 ? "dashboard-metric--warning" : "dashboard-metric--success"}`}>
          <div className="dashboard-metric__icon"><Icon name={pendingAssign > 0 ? "warning" : "check_circle"} /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Needs staff</p>
            <strong className="dashboard-metric__value">{pendingAssign}</strong>
          </div>
        </article>
      </div>

      {loading ? (
        <div className="page-stack">
          {[0, 1, 2].map((i) => <Skeleton key={i} className="dashboard-skeleton" />)}
        </div>
      ) : exams.length === 0 ? (
        <Card title="External exams">
          <EmptyState
            icon={<Icon name="language" />}
            title="No external exams scheduled"
            description={isAdmin ? "Create an exam using the button above." : "No special exams are scheduled for the current period."}
          />
        </Card>
      ) : (
        <Card title="Scheduled exams" subtitle={`${exams.length} exam${exams.length !== 1 ? "s" : ""} for the active period`}>
          <div className="page-stack">
            {exams.map((exam) => (
              <ExamCard
                key={exam.id}
                exam={exam}
                isAdmin={isAdmin}
                onEdit={() => { setEditTarget(exam); setShowForm(true); }}
                onAssign={() => void handleAutoAssign(exam.id)}
                onDelete={() => void handleDelete(exam)}
              />
            ))}
          </div>
        </Card>
      )}

      <ExamFormModal
        open={showForm}
        exam={editTarget}
        busy={formBusy}
        onClose={() => { setShowForm(false); setEditTarget(null); }}
        onSave={handleSave}
      />
    </div>
  );
}
