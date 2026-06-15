import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { useI18n } from "@/i18n";
import {
  applyExternalExamAssignment,
  createExternalExam,
  deleteExternalExam,
  listExternalExams,
  previewExternalExamAssignment,
  updateExternalExam,
} from "@/services/external.service";
import { useAuth } from "@/store/auth.store";
import { useEffectiveRole } from "@/hooks/useEffectiveRole";
import { useUi } from "@/store/ui.store";
import type { ExternalExam, ExternalExamAssignmentPreview } from "@/types/api";
import { canManageExamPeriods, canAccessExternalExams } from "@/utils/permissions";

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

function ExamStatusBadge({ status }: { status: string | undefined }) {
  const { t } = useI18n();
  const normalized = status ?? "draft";
  const classMap: Record<string, string> = {
    draft: "ext-badge ext-badge--draft",
    confirmed: "ext-badge ext-badge--confirmed",
    completed: "ext-badge ext-badge--completed",
    cancelled: "ext-badge ext-badge--cancelled",
  };
  return <span className={classMap[normalized] ?? "ext-badge"}>{t(`legacy.external.status.${normalized}`)}</span>;
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
  const { t } = useI18n();
  const [form, setForm] = useState<ExamFormData>(emptyForm);

  useEffect(() => {
    if (!open) {
      return;
    }
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
      return;
    }
    setForm(emptyForm());
  }, [exam, open]);

  const setField = (key: keyof ExamFormData, value: string | number | "") => {
    setForm((previous) => ({ ...previous, [key]: value }));
  };

  const canSave = form.title.trim() !== "" && form.exam_date.trim() !== "" && form.exam_time.trim() !== "";

  return (
    <Modal
      open={open}
      title={exam ? t("legacy.external.form.editTitle") : t("legacy.external.form.createTitle")}
      onClose={onClose}
      footer={(
        <div className="inline-actions">
          <Button type="button" variant="outline" onClick={onClose}>{t("common.cancel")}</Button>
          <Button type="button" disabled={!canSave} loading={busy} onClick={() => void onSave(form)}>
            {exam ? t("common.saveChanges") : t("legacy.external.actions.create")}
          </Button>
        </div>
      )}
    >
      <div className="ext-form">
        <div className="form-field">
          <label htmlFor="external-title">{t("legacy.external.form.name")}</label>
          <input id="external-title" type="text" value={form.title} onChange={(event) => setField("title", event.target.value)} />
        </div>
        <div className="import-upload-grid">
          <div className="form-field">
            <label htmlFor="external-organizer">{t("legacy.external.form.organizer")}</label>
            <input id="external-organizer" type="text" value={form.organizer} onChange={(event) => setField("organizer", event.target.value)} />
          </div>
          <div className="form-field">
            <label htmlFor="external-room">{t("legacy.external.form.venue")}</label>
            <input id="external-room" type="text" value={form.room_name} onChange={(event) => setField("room_name", event.target.value)} />
            <span className="form-hint">{t("legacy.external.form.venueHint")}</span>
          </div>
          <div className="form-field">
            <label htmlFor="external-date">{t("common.date")}</label>
            <input id="external-date" type="date" value={form.exam_date} onChange={(event) => setField("exam_date", event.target.value)} />
          </div>
          <div className="form-field">
            <label htmlFor="external-time">{t("common.time")}</label>
            <input id="external-time" type="text" placeholder="09:00-12:00" value={form.exam_time} onChange={(event) => setField("exam_time", event.target.value)} />
          </div>
          <div className="form-field">
            <label htmlFor="external-students">{t("legacy.external.form.attendees")}</label>
            <input id="external-students" type="number" min={0} value={form.num_students} onChange={(event) => setField("num_students", event.target.value === "" ? "" : Number(event.target.value))} />
          </div>
          <div className="form-field">
            <label htmlFor="external-staff">{t("legacy.external.form.staffRequired")}</label>
            <input id="external-staff" type="number" min={1} value={form.invigilators_needed} onChange={(event) => setField("invigilators_needed", event.target.value === "" ? "" : Number(event.target.value))} />
          </div>
        </div>
        <div className="form-field">
          <label htmlFor="external-notes">{t("common.notes")}</label>
          <textarea id="external-notes" rows={2} value={form.notes} onChange={(event) => setField("notes", event.target.value)} />
        </div>
      </div>
    </Modal>
  );
}

function PreviewSection({
  title,
  subtitle,
  rows,
}: {
  title: string;
  subtitle?: string;
  rows: Array<{ user_id: number; full_name: string | null; division?: string | null; unit?: string | null; total_load: number; reason?: string }>;
}) {
  const { t } = useI18n();
  return (
    <Card title={title} subtitle={subtitle}>
      <DataTable
        columns={[
          {
            key: "full_name",
            label: t("legacy.external.preview.staff"),
            width: "38%",
            render: (row) => (
              <div className="data-table__content data-table__content--clamp">
                <strong>{row.full_name ?? t("legacy.external.preview.userFallback", { id: row.user_id })}</strong>
                <p>{row.division ?? row.unit ?? t("legacy.external.preview.noOrganization")}</p>
              </div>
            ),
          },
          {
            key: "total_load",
            label: t("legacy.external.preview.historicalLoad"),
            width: "18%",
            align: "right",
            render: (row) => row.total_load,
          },
          {
            key: "reason",
            label: t("legacy.external.preview.reason"),
            width: "44%",
            render: (row) => row.reason ?? t("legacy.external.preview.eligible"),
          },
        ]}
        emptyTitle={t("legacy.external.preview.noRows")}
        rowKey={(row) => row.user_id}
        rows={rows}
        scrollThreshold={5}
        tableLayout="fixed"
      />
    </Card>
  );
}

function AssignmentPreviewPanel({
  preview,
  busy,
  onClose,
  onConfirm,
}: {
  preview: ExternalExamAssignmentPreview;
  busy: boolean;
  onClose: () => void;
  onConfirm: () => void;
}) {
  const { t } = useI18n();
  const exam = preview.exam;

  return (
    <Card
      title={t("legacy.external.preview.title", { name: exam.title ?? t("legacy.external.preview.examFallback") })}
      subtitle={t("legacy.external.preview.subtitle")}
      actions={(
        <div className="inline-actions">
          <Button type="button" variant="outline" onClick={onClose}>{t("common.close")}</Button>
          <Button type="button" loading={busy} disabled={preview.shortage_count > 0 || preview.needed_count === 0} onClick={onConfirm}>
            {t("legacy.external.preview.confirm")}
          </Button>
        </div>
      )}
    >
      <div className="stitch-metric-grid">
        <article className="dashboard-metric dashboard-metric--accent">
          <div className="dashboard-metric__icon"><Icon name="groups" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("legacy.external.preview.needed")}</p>
            <strong className="dashboard-metric__value">{preview.needed_count}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--neutral">
          <div className="dashboard-metric__icon"><Icon name="person_search" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("legacy.external.preview.eligibleStaff")}</p>
            <strong className="dashboard-metric__value">{preview.eligible_candidates.length}</strong>
          </div>
        </article>
        <article className={`dashboard-metric ${preview.shortage_count > 0 ? "dashboard-metric--warning" : "dashboard-metric--success"}`}>
          <div className="dashboard-metric__icon"><Icon name={preview.shortage_count > 0 ? "warning" : "check_circle"} /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("legacy.external.preview.shortage")}</p>
            <strong className="dashboard-metric__value">{preview.shortage_count}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--neutral">
          <div className="dashboard-metric__icon"><Icon name="analytics" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("legacy.external.preview.fairness")}</p>
            <strong className="dashboard-metric__value">
              {preview.fairness.current_score} → {preview.fairness.projected_score}
            </strong>
          </div>
        </article>
      </div>

      {preview.warnings.length > 0 && (
        <div className="wf-validation">
          <div className="wf-validation__counts">
            {preview.warnings.map((warning) => (
              <span key={warning} className="wf-issue-chip wf-issue-chip--warning">
                <Icon name="warning" /> {warning}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="page-stack">
        <PreviewSection
          title={t("legacy.external.preview.recommended")}
          subtitle={t("legacy.external.preview.recommendedHint")}
          rows={preview.recommended_assignment}
        />
        <PreviewSection
          title={t("legacy.external.preview.reserve")}
          subtitle={t("legacy.external.preview.reserveHint")}
          rows={preview.eligible_candidates}
        />
        <PreviewSection
          title={t("legacy.external.preview.conflicted")}
          subtitle={t("legacy.external.preview.conflictedHint")}
          rows={preview.conflicted_staff}
        />
        <PreviewSection
          title={t("legacy.external.preview.excluded")}
          subtitle={t("legacy.external.preview.excludedHint")}
          rows={preview.excluded_staff}
        />
      </div>
    </Card>
  );
}

function ExamCard({
  exam,
  canManage,
  canOptimize,
  onEdit,
  onDelete,
  onPreview,
}: {
  exam: ExternalExam;
  canManage: boolean;
  canOptimize: boolean;
  onEdit: () => void;
  onDelete: () => void;
  onPreview: () => void;
}) {
  const { t } = useI18n();
  const assigned = exam.supervisions?.length ?? 0;
  const needed = exam.invigilators_needed ?? 0;
  const staffReady = assigned >= needed;

  return (
    <article className="ext-exam-card">
      <div className="ext-exam-card__header">
        <div>
          <strong className="ext-exam-card__title">{exam.title ?? t("legacy.external.preview.examFallback")}</strong>
          {exam.organizer && <span className="text-muted ext-exam-card__organizer">{exam.organizer}</span>}
        </div>
        <ExamStatusBadge status={exam.status} />
      </div>

      <div className="ext-exam-card__meta">
        <span><Icon name="event" /> {exam.exam_date ?? "-"} {exam.exam_time ?? ""}</span>
        <span><Icon name="location_on" /> {exam.room_name ?? t("legacy.external.card.noVenue")}</span>
        <span><Icon name="groups" /> {t("legacy.external.card.attendees", { count: exam.num_students ?? 0 })}</span>
        <span className={staffReady ? "ext-staff-ok" : "ext-staff-missing"}>
          <Icon name={staffReady ? "check_circle" : "warning"} />
          {t("legacy.external.card.staffAssigned", { assigned, needed })}
        </span>
      </div>

      <p className="text-muted ext-exam-card__notes">{t("legacy.external.form.venueHint")}</p>

      {exam.supervisions && exam.supervisions.length > 0 && (
        <div className="ext-invig-list">
          {exam.supervisions.map((supervision) => (
            <span key={supervision.id} className="staff-slot-tag">
              {supervision.full_name ?? supervision.user_name ?? t("legacy.external.preview.userFallback", { id: supervision.user_id ?? supervision.id })}
              {supervision.confirmed && <Icon name="check" />}
            </span>
          ))}
        </div>
      )}

      {exam.notes && <p className="ext-exam-card__notes text-muted">{exam.notes}</p>}

      {(canManage || canOptimize) && (
        <div className="inline-actions ext-exam-card__actions">
          {canManage && <Button type="button" size="sm" variant="outline" onClick={onEdit}>{t("common.edit")}</Button>}
          {canOptimize && (
            <Button type="button" size="sm" onClick={onPreview}>
              {t("legacy.external.actions.reviewAllocation")}
            </Button>
          )}
          {canManage && <Button type="button" size="sm" variant="ghost" onClick={onDelete}>{t("common.delete")}</Button>}
        </div>
      )}
    </article>
  );
}

export function ExternalPage() {
  const { t } = useI18n();
  const { toast } = useUi();
  const { user } = useAuth();
  const role = useEffectiveRole();
  const canManage = canManageExamPeriods(user);
  const canOptimize = canAccessExternalExams(user);

  const [exams, setExams] = useState<ExternalExam[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editTarget, setEditTarget] = useState<ExternalExam | null>(null);
  const [formBusy, setFormBusy] = useState(false);

  const [preview, setPreview] = useState<ExternalExamAssignmentPreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [assignBusy, setAssignBusy] = useState(false);

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

  useEffect(() => {
    void load();
  }, [load]);

  const handleSave = async (data: ExamFormData) => {
    setFormBusy(true);
    try {
      if (editTarget) {
        await updateExternalExam(editTarget.id, data as unknown as Record<string, unknown>);
        toast(t("legacy.external.toast.updated"), "success");
      } else {
        await createExternalExam(data as unknown as Record<string, unknown>);
        toast(t("legacy.external.toast.created"), "success");
      }
      setShowForm(false);
      setEditTarget(null);
      await load();
    } catch (err) {
      toast(err instanceof Error ? err.message : t("legacy.external.toast.saveFailed"), "error");
    } finally {
      setFormBusy(false);
    }
  };

  const handleDelete = async (exam: ExternalExam) => {
    try {
      await deleteExternalExam(exam.id);
      toast(t("legacy.external.toast.deleted"), "warning");
      await load();
    } catch (err) {
      toast(err instanceof Error ? err.message : t("legacy.external.toast.deleteFailed"), "error");
    }
  };

  const handlePreview = async (examId: number) => {
    setPreviewLoading(true);
    try {
      const nextPreview = await previewExternalExamAssignment(examId);
      setPreview(nextPreview);
    } catch (err) {
      toast(err instanceof Error ? err.message : t("legacy.external.toast.previewFailed"), "error");
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!preview) {
      return;
    }
    setAssignBusy(true);
    try {
      const response = await applyExternalExamAssignment(preview.exam.id);
      setPreview(response.preview);
      toast(t("legacy.external.toast.allocated"), "success");
      await load();
    } catch (err) {
      toast(err instanceof Error ? err.message : t("legacy.external.toast.allocateFailed"), "error");
    } finally {
      setAssignBusy(false);
    }
  };

  const totalAssigned = useMemo(
    () => exams.reduce((sum, exam) => sum + (exam.supervisions?.length ?? 0), 0),
    [exams],
  );
  const pendingCount = useMemo(
    () => exams.filter((exam) => (exam.supervisions?.length ?? 0) < (exam.invigilators_needed ?? 1)).length,
    [exams],
  );

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">{t("legacy.external.eyebrow")}</span>
          <h1 className="page-hero__title">{t("legacy.external.title")}</h1>
          <p className="page-hero__description">{t("legacy.external.description")}</p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => void load()} disabled={loading}>
            {t("common.refresh")}
          </Button>
          {canManage && (
            <Button type="button" onClick={() => { setEditTarget(null); setShowForm(true); }}>
              {t("legacy.external.actions.create")}
            </Button>
          )}
        </div>
      </section>

      <div className="stitch-metric-grid">
        <article className="dashboard-metric dashboard-metric--accent">
          <div className="dashboard-metric__icon"><Icon name="language" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("legacy.external.metrics.active")}</p>
            <strong className="dashboard-metric__value">{exams.length}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--neutral">
          <div className="dashboard-metric__icon"><Icon name="groups" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("legacy.external.metrics.assigned")}</p>
            <strong className="dashboard-metric__value">{totalAssigned}</strong>
          </div>
        </article>
        <article className={`dashboard-metric ${pendingCount > 0 ? "dashboard-metric--warning" : "dashboard-metric--success"}`}>
          <div className="dashboard-metric__icon"><Icon name={pendingCount > 0 ? "warning" : "check_circle"} /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("legacy.external.metrics.pending")}</p>
            <strong className="dashboard-metric__value">{pendingCount}</strong>
          </div>
        </article>
      </div>

      {loading ? (
        <div className="page-stack">
          {[0, 1, 2].map((index) => <Skeleton key={index} className="dashboard-skeleton" />)}
        </div>
      ) : exams.length === 0 ? (
        <Card title={t("legacy.external.cardTitle")}>
          <EmptyState
            icon={<Icon name="language" />}
            title={t("legacy.external.emptyTitle")}
            description={canManage ? t("legacy.external.emptyManage") : t("legacy.external.emptyReadOnly")}
          />
        </Card>
      ) : (
        <Card title={t("legacy.external.currentTitle")} subtitle={t("legacy.external.currentSubtitle", { count: exams.length })}>
          <div className="page-stack">
            {exams.map((exam) => (
              <ExamCard
                key={exam.id}
                exam={exam}
                canManage={canManage}
                canOptimize={canOptimize}
                onEdit={() => { setEditTarget(exam); setShowForm(true); }}
                onDelete={() => void handleDelete(exam)}
                onPreview={() => void handlePreview(exam.id)}
              />
            ))}
          </div>
        </Card>
      )}

      {previewLoading && <Skeleton className="dashboard-skeleton" />}

      {preview && !previewLoading && (
        <AssignmentPreviewPanel
          preview={preview}
          busy={assignBusy}
          onClose={() => setPreview(null)}
          onConfirm={() => void handleConfirm()}
        />
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
