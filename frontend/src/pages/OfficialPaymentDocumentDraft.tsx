import { useEffect, useMemo, useState } from "react";

import { AlertBanner } from "@/components/ui/AlertBanner";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, type DataTableColumn } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { FormField } from "@/components/ui/FormField";
import { Icon } from "@/components/ui/Icon";
import { PageHeader } from "@/components/ui/PageHeader";
import { useOfficialPaymentDraftPreview } from "@/hooks/domain/useOfficialPaymentDraftPreview";
import { usePaymentDocumentSettings } from "@/hooks/domain/usePaymentDocumentSettings";
import { usePaymentDocumentReviewChecklist } from "@/hooks/domain/usePaymentDocumentReviewChecklist";
import { usePaymentDocumentReviews } from "@/hooks/domain/usePaymentDocumentReviews";
import { useI18n } from "@/i18n";
import { exportOfficialPaymentDraftExcel } from "@/services/officialPaymentDraft.service";
import { useAuth } from "@/store/auth.store";
import type { OfficialPaymentDraftManualPaperRow, OfficialPaymentDraftRow } from "@/types/officialPaymentDraft";
import type { PaymentDocumentReviewRecord, PaymentDocumentReviewStatus } from "@/types/paymentDocumentReview";
import type {
  PaymentDocumentReviewChecklistItem,
  PaymentDocumentReviewChecklistStatus,
} from "@/types/paymentDocumentReviewChecklist";
import { formatCurrency } from "@/utils/format";
import {
  canCommentOnPaymentDocumentReview,
  canManagePaymentDocumentReview,
  canManagePaymentDocumentReviewChecklist,
} from "@/utils/permissions";

type EditablePaperRow = OfficialPaymentDraftManualPaperRow & { local_id: string };

const REVIEW_STATUS_OPTIONS: PaymentDocumentReviewStatus[] = [
  "DRAFT_READY_FOR_REVIEW",
  "UNDER_REVIEW",
  "REVISIONS_REQUESTED",
  "ACCEPTED_FOR_DRAFT_EXPORT",
  "REJECTED_REDESIGN_REQUIRED",
  "FINAL_AUTHORIZATION_REQUIRED",
];

const CHECKLIST_STATUS_OPTIONS: PaymentDocumentReviewChecklistStatus[] = [
  "NOT_STARTED",
  "IN_PROGRESS",
  "CHECKED",
  "NEEDS_ATTENTION",
  "BLOCKED",
];

function newPaperRow(): EditablePaperRow {
  return {
    local_id: crypto.randomUUID(),
    exam_date: "",
    exam_time: "",
    committee_count: 0,
    notes: "",
  };
}

function toRequestRow(row: EditablePaperRow): OfficialPaymentDraftManualPaperRow | null {
  if (!row.exam_date.trim()) return null;
  return {
    exam_date: row.exam_date.trim(),
    exam_time: row.exam_time?.trim() || null,
    start_time: row.start_time?.trim() || null,
    end_time: row.end_time?.trim() || null,
    committee_count: Number(row.committee_count) || 0,
    notes: row.notes?.trim() || null,
  };
}

function formatReviewDate(value: string | null) {
  if (!value) return "-";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString();
}

function amountToCurrency(value: number | string | null | undefined) {
  if (value === null || value === undefined || value === "") return "-";
  const parsed = Number(value);
  return Number.isFinite(parsed) ? formatCurrency(parsed) : String(value);
}

function reviewStatusVariant(status: PaymentDocumentReviewStatus) {
  if (status === "ACCEPTED_FOR_DRAFT_EXPORT") return "green";
  if (status === "REVISIONS_REQUESTED" || status === "REJECTED_REDESIGN_REQUIRED") return "orange";
  if (status === "FINAL_AUTHORIZATION_REQUIRED") return "crimson";
  if (status === "UNDER_REVIEW") return "blue";
  return "gold";
}

function checklistStatusVariant(status: PaymentDocumentReviewChecklistStatus) {
  if (status === "CHECKED") return "green";
  if (status === "BLOCKED") return "crimson";
  if (status === "NEEDS_ATTENTION") return "orange";
  if (status === "IN_PROGRESS") return "blue";
  return "gray";
}

function ChecklistItemEditor({
  canManage,
  item,
  isSaving,
  onSave,
}: {
  canManage: boolean;
  item: PaymentDocumentReviewChecklistItem;
  isSaving: boolean;
  onSave: (status: PaymentDocumentReviewChecklistStatus, comment: string) => Promise<unknown>;
}) {
  const { t } = useI18n();
  const [status, setStatus] = useState(item.item_status);
  const [comment, setComment] = useState(item.comment ?? "");

  useEffect(() => {
    setStatus(item.item_status);
    setComment(item.comment ?? "");
  }, [item.comment, item.item_status]);

  return (
    <div className="summary-box">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <span>{t("paymentDraft.checklist.step", { step: item.item_order })}</span>
          <strong>{t(`paymentDraft.checklist.item.${item.item_key}.label`)}</strong>
        </div>
        <Badge variant={checklistStatusVariant(item.item_status)}>
          {t(`paymentDraft.checklist.status.${item.item_status}`)}
        </Badge>
      </div>
      <p className="mt-2 text-sm text-gray-500">{t(`paymentDraft.checklist.item.${item.item_key}.description`)}</p>
      {canManage ? (
        <div className="mt-4 page-stack">
          <FormField label={t("paymentDraft.checklist.itemStatus")}>
            <select value={status} onChange={(event) => setStatus(event.target.value as PaymentDocumentReviewChecklistStatus)}>
              {CHECKLIST_STATUS_OPTIONS.map((option) => (
                <option key={option} value={option}>{t(`paymentDraft.checklist.status.${option}`)}</option>
              ))}
            </select>
          </FormField>
          <FormField label={t("paymentDraft.checklist.comment")}>
            <textarea value={comment} onChange={(event) => setComment(event.target.value)} rows={2} placeholder={t("paymentDraft.checklist.commentPlaceholder")} />
          </FormField>
          <Button type="button" size="sm" variant="outline" iconLeft={<Icon name="save" />} loading={isSaving} onClick={() => void onSave(status, comment)}>
            {t("paymentDraft.checklist.save")}
          </Button>
        </div>
      ) : (
        <p className="mt-3 text-sm text-gray-500">
          {item.comment || t("paymentDraft.checklist.readOnlyItem")}
        </p>
      )}
      {item.reviewer_name ? (
        <p className="mt-3 text-sm text-gray-500">
          {t("paymentDraft.checklist.lastUpdatedBy", { name: item.reviewer_name, role: item.reviewer_role ?? "-" })}
        </p>
      ) : null}
    </div>
  );
}

export default function OfficialPaymentDocumentDraft() {
  const { t } = useI18n();
  const { user } = useAuth();
  const [periodId, setPeriodId] = useState("");
  const [academicYear, setAcademicYear] = useState("2568");
  const [semester, setSemester] = useState("2");
  const [examType, setExamType] = useState("final");
  const [paperRows, setPaperRows] = useState<EditablePaperRow[]>([newPaperRow()]);
  const { data, isError, isLoading, preview } = useOfficialPaymentDraftPreview();
  const [isExporting, setIsExporting] = useState(false);
  const [reviewComment, setReviewComment] = useState("");
  const [reviewDecision, setReviewDecision] = useState("");
  const [reviewStatus, setReviewStatus] = useState<PaymentDocumentReviewStatus>("DRAFT_READY_FOR_REVIEW");
  const canCommentReview = canCommentOnPaymentDocumentReview(user);
  const canManageReview = canManagePaymentDocumentReview(user);
  const canManageChecklist = canManagePaymentDocumentReviewChecklist(user);
  const documentId = useMemo(
    () => `ADVANCE_PAYMENT_DRAFT_SUMMARY:${academicYear || "unknown"}:${semester || "unknown"}:${examType || "unknown"}:${periodId || "all"}`,
    [academicYear, examType, periodId, semester],
  );
  const settingsTerm = useMemo(() => `${semester || "2"}/${academicYear || "2568"}`, [academicYear, semester]);
  const reviewTerm = useMemo(() => `${semester || "-"} / ${academicYear || "-"}`, [academicYear, semester]);
  const reviewRecords = usePaymentDocumentReviews(documentId);
  const checklist = usePaymentDocumentReviewChecklist(documentId);
  const paymentSettings = usePaymentDocumentSettings(settingsTerm);
  const settingsSourceStatus = data?.metadata.settings_source_status
    ?? (paymentSettings.data?.configuration_status === "PENDING_CONFIGURATION"
      ? "PENDING_SETTINGS"
      : paymentSettings.data?.status === "ACTIVE_FOR_DRAFT_PREVIEW"
        ? "CONFIGURED"
        : "INCOMPLETE_SETTINGS");
  const settingsStatus = data?.metadata.settings_status ?? paymentSettings.data?.status ?? null;
  const settingsWeekdayRate = data?.metadata.settings_weekday_rate ?? paymentSettings.data?.weekday_rate;
  const settingsWeekendRate = data?.metadata.settings_weekend_rate ?? paymentSettings.data?.weekend_rate;
  const settingsGroup = data?.metadata.paper_distribution_responsible_group
    ?? paymentSettings.data?.paper_distribution_responsible_group
    ?? null;
  const settingsPerson = data?.metadata.paper_distribution_responsible_person
    ?? paymentSettings.data?.paper_distribution_responsible_person
    ?? null;
  const settingsCurrency = data?.metadata.currency ?? paymentSettings.data?.currency ?? "THB";
  const settingsUnit = data?.metadata.payment_unit ?? paymentSettings.data?.payment_unit ?? "PER_PERSON_SESSION";
  const settingsIssues = data?.metadata.settings_issues ?? [];
  const calculationStatus = data?.metadata.calculation_status
    ?? (settingsSourceStatus === "CONFIGURED"
      ? "CALCULATED_FROM_SETTINGS"
      : settingsSourceStatus === "INCOMPLETE_SETTINGS"
        ? "BLOCKED_INCOMPLETE_SETTINGS"
        : "BLOCKED_PENDING_SETTINGS");
  const statusLabel = (status: string | null | undefined) => (
    status ? t(`paymentDraft.status.${status}`) : "-"
  );

  const draftColumns = useMemo<Array<DataTableColumn<OfficialPaymentDraftRow>>>(() => [
    {
      key: "examDate",
      label: t("paymentDraft.table.examDate"),
      minWidth: "150px",
      render: (row) => <strong>{row.exam_date}</strong>,
    },
    {
      key: "timeSlot",
      label: t("paymentDraft.table.timeSlot"),
      minWidth: "150px",
      render: (row) => row.time_slot,
    },
    {
      key: "dayType",
      label: t("paymentDraft.table.dayType"),
      width: "140px",
      render: (row) => <Badge variant={row.day_type === "WEEKEND" ? "gold" : "gray"}>{t(`advanceBatch.dayType.${row.day_type}`)}</Badge>,
    },
    {
      key: "invigilationCount",
      label: t("paymentDraft.table.invigilationCount"),
      width: "140px",
      align: "center",
      render: (row) => row.invigilation_committee_count,
    },
    {
      key: "invigilationAmount",
      label: t("paymentDraft.table.invigilationAmount"),
      width: "160px",
      align: "right",
      render: (row) => formatCurrency(row.invigilation_compensation_amount),
    },
    {
      key: "paperCount",
      label: t("paymentDraft.table.paperCount"),
      width: "150px",
      align: "center",
      render: (row) => row.paper_distribution_committee_count,
    },
    {
      key: "paperAmount",
      label: t("paymentDraft.table.paperAmount"),
      width: "170px",
      align: "right",
      render: (row) => formatCurrency(row.paper_distribution_compensation_amount),
    },
    {
      key: "total",
      label: t("paymentDraft.table.total"),
      width: "150px",
      align: "right",
      render: (row) => <strong>{formatCurrency(row.total_compensation_amount)}</strong>,
    },
    {
      key: "warnings",
      label: t("paymentDraft.table.warnings"),
      minWidth: "240px",
      render: (row) => row.warnings.join("; ") || "-",
    },
  ], [t]);

  const reviewColumns = useMemo<Array<DataTableColumn<PaymentDocumentReviewRecord>>>(() => [
    {
      key: "review_status",
      label: t("paymentDraft.review.status"),
      minWidth: "170px",
      render: (row) => (
        <Badge variant={reviewStatusVariant(row.review_status)}>{statusLabel(row.review_status)}</Badge>
      ),
    },
    {
      key: "comment",
      label: t("paymentDraft.review.comment"),
      minWidth: "260px",
      render: (row) => row.comment || "-",
    },
    {
      key: "reviewer_name",
      label: t("paymentDraft.review.reviewer"),
      minWidth: "160px",
      render: (row) => row.reviewer_name || "-",
    },
    {
      key: "reviewer_role",
      label: t("paymentDraft.review.role"),
      width: "120px",
      render: (row) => row.reviewer_role || "-",
    },
    {
      key: "reviewed_at",
      label: t("paymentDraft.review.reviewedAt"),
      minWidth: "180px",
      render: (row) => formatReviewDate(row.reviewed_at || row.created_at),
    },
  ], [t]);

  const updatePaperRow = (localId: string, patch: Partial<EditablePaperRow>) => {
    setPaperRows((rows) => rows.map((row) => (row.local_id === localId ? { ...row, ...patch } : row)));
  };

  const submitPreview = async () => {
    const manualRows = paperRows.map(toRequestRow).filter((row): row is OfficialPaymentDraftManualPaperRow => Boolean(row));
    await preview({
      period_id: periodId ? Number(periodId) : null,
      academic_year: academicYear || null,
      semester: semester || null,
      exam_type: examType || null,
      paper_distribution_rows: manualRows,
    });
  };

  const submitExport = async () => {
    if (latestReviewStatus !== "ACCEPTED_FOR_DRAFT_EXPORT") return;
    setIsExporting(true);
    try {
      const manualRows = paperRows
        .map(toRequestRow)
        .filter((row): row is OfficialPaymentDraftManualPaperRow => Boolean(row));
      const blob = await exportOfficialPaymentDraftExcel({
        period_id: periodId ? Number(periodId) : null,
        academic_year: academicYear || null,
        semester: semester || null,
        exam_type: examType || null,
        paper_distribution_rows: manualRows,
      });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `EMS_DRAFT_PAYMENT_DOCUMENT_${semester}-${academicYear}_draft.xlsx`;
      anchor.click();
      URL.revokeObjectURL(url);
    } finally {
      setIsExporting(false);
    }
  };

  const submitReview = async () => {
    if (!canCommentReview) return;
    const requestedStatus = canManageReview ? reviewStatus : "DRAFT_READY_FOR_REVIEW";
    await reviewRecords.create({
      document_id: documentId,
      document_type: "ADVANCE_PAYMENT_DRAFT_SUMMARY",
      term: reviewTerm,
      review_status: requestedStatus,
      comment: reviewComment.trim() || null,
      decision: canManageReview ? reviewDecision.trim() || null : null,
      prepared_by: user?.full_name || user?.username || null,
      revision_required: requestedStatus === "REVISIONS_REQUESTED",
      note: t("paymentDraft.review.nonAuthorizationNote"),
    });
    setReviewComment("");
    setReviewDecision("");
  };

  const latestReviewStatus = reviewRecords.latestRecord?.review_status ?? "DRAFT_NOT_AUTHORIZED";

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        className="page-hero--dashboard"
        eyebrow={t("paymentDraft.eyebrow")}
        title={t("paymentDraft.title")}
        description={t("paymentDraft.description")}
        status={<Badge variant="gold">DRAFT_NOT_AUTHORIZED</Badge>}
      />

      <AlertBanner
        variant="warning"
        title={t("paymentDraft.warning.title")}
        action={<Badge variant="gold">DRAFT_NOT_AUTHORIZED</Badge>}
      >
        {t("paymentDraft.warning.body")}
      </AlertBanner>

      <Card
        title={t("paymentDraft.settings.title")}
        subtitle={t("paymentDraft.settings.subtitle")}
        actions={
          <Badge variant={settingsSourceStatus === "CONFIGURED" ? "green" : "gold"}>
            {statusLabel(settingsSourceStatus)}
          </Badge>
        }
      >
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="summary-box">
            <span>{t("paymentDraft.settings.term")}</span>
            <strong>{data?.metadata.settings_term ?? settingsTerm}</strong>
          </div>
          <div className="summary-box">
            <span>{t("paymentDraft.settings.weekdayRate")}</span>
            <strong>{amountToCurrency(settingsWeekdayRate)}</strong>
          </div>
          <div className="summary-box">
            <span>{t("paymentDraft.settings.weekendRate")}</span>
            <strong>{amountToCurrency(settingsWeekendRate)}</strong>
          </div>
          <div className="summary-box">
            <span>{t("paymentDraft.settings.group")}</span>
            <strong>{settingsGroup ?? "-"}</strong>
          </div>
          <div className="summary-box">
            <span>{t("paymentDraft.settings.person")}</span>
            <strong>{settingsPerson ?? "-"}</strong>
          </div>
          <div className="summary-box">
            <span>{t("paymentDraft.settings.unit")}</span>
            <strong>{settingsCurrency} / {settingsUnit}</strong>
          </div>
          <div className="summary-box">
            <span>{t("paymentDraft.settings.status")}</span>
            <strong>{statusLabel(settingsStatus)}</strong>
          </div>
          <div className="summary-box">
            <span>{t("paymentDraft.settings.calculationStatus")}</span>
            <strong>{statusLabel(calculationStatus)}</strong>
          </div>
        </div>
        <p className="mt-4 text-sm text-gray-500">{t("paymentDraft.settings.calculationNote")}</p>
      </Card>

      {settingsSourceStatus !== "CONFIGURED" ? (
        <AlertBanner
          variant="warning"
          title={t(`paymentDraft.settings.warning.${settingsSourceStatus}.title`)}
          action={<Badge variant="gold">{statusLabel(calculationStatus)}</Badge>}
        >
          {settingsIssues.length
            ? settingsIssues.join(" ")
            : t(`paymentDraft.settings.warning.${settingsSourceStatus}.body`)}
        </AlertBanner>
      ) : null}

      <Card
        title={t("paymentDraft.review.title")}
        subtitle={t("paymentDraft.review.subtitle")}
        actions={<Badge variant={reviewStatusVariant(latestReviewStatus)}>{statusLabel(latestReviewStatus)}</Badge>}
      >
        <div className="page-stack">
          <AlertBanner variant="warning" title={t("paymentDraft.review.safetyTitle")}>
            {t("paymentDraft.review.safetyBody")}
          </AlertBanner>
          <div className="form-grid">
            <FormField label={t("paymentDraft.review.documentId")}>
              <input value={documentId} readOnly />
            </FormField>
            {canManageReview ? (
              <FormField label={t("paymentDraft.review.status")}>
                <select value={reviewStatus} onChange={(event) => setReviewStatus(event.target.value as PaymentDocumentReviewStatus)}>
                  {REVIEW_STATUS_OPTIONS.map((status) => (
                    <option key={status} value={status}>
                      {statusLabel(status)}
                    </option>
                  ))}
                </select>
              </FormField>
            ) : (
              <FormField label={t("paymentDraft.review.status")}>
                <input value={statusLabel("DRAFT_READY_FOR_REVIEW")} readOnly />
              </FormField>
            )}
            <FormField label={t("paymentDraft.review.decision")}>
              <input value={reviewDecision} disabled={!canManageReview} onChange={(event) => setReviewDecision(event.target.value)} placeholder={t("paymentDraft.review.decisionPlaceholder")} />
            </FormField>
          </div>
          <FormField label={t("paymentDraft.review.comment")}>
            <textarea value={reviewComment} disabled={!canCommentReview} onChange={(event) => setReviewComment(event.target.value)} placeholder={t("paymentDraft.review.commentPlaceholder")} rows={4} />
          </FormField>
          <div className="flex flex-wrap gap-3">
            <Button type="button" iconLeft={<Icon name="save" />} loading={reviewRecords.isSaving} disabled={!canCommentReview} onClick={submitReview}>
              {t("paymentDraft.review.save")}
            </Button>
            <Button type="button" variant="outline" onClick={() => void reviewRecords.refresh()} loading={reviewRecords.isLoading}>
              {t("common.refresh")}
            </Button>
          </div>
          {reviewRecords.isError ? (
            <AlertBanner variant="danger" title={t("paymentDraft.review.errorTitle")}>
              {t("paymentDraft.review.errorBody")}
            </AlertBanner>
          ) : null}
          <DataTable
            columns={reviewColumns}
            rows={reviewRecords.records}
            rowKey={(row) => row.review_id}
            loading={reviewRecords.isLoading}
            emptyTitle={t("paymentDraft.review.emptyTitle")}
            emptyDescription={t("paymentDraft.review.emptyDescription")}
            compact
          />
        </div>
      </Card>

      <Card
        title={t("paymentDraft.checklist.title")}
        subtitle={t("paymentDraft.checklist.subtitle")}
        actions={
          <Badge variant="gold">
            {checklist.data?.decision_gate_status ?? "HOLD_PENDING_ADDITIONAL_REVIEW"}
          </Badge>
        }
      >
        <div className="page-stack">
          <AlertBanner variant="warning" title={t("paymentDraft.checklist.safetyTitle")}>
            {t("paymentDraft.checklist.safetyBody")}
          </AlertBanner>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div className="summary-box">
              <span>{t("paymentDraft.checklist.progress")}</span>
              <strong>{t("paymentDraft.checklist.progressValue", {
                checked: checklist.data?.checked_items ?? 0,
                total: checklist.data?.total_items ?? 7,
              })}</strong>
            </div>
            <div className="summary-box">
              <span>{t("paymentDraft.checklist.remaining")}</span>
              <strong>{checklist.data?.remaining_items ?? 7}</strong>
            </div>
            <div className="summary-box">
              <span>{t("paymentDraft.checklist.decisionGate")}</span>
              <strong>HOLD_PENDING_ADDITIONAL_REVIEW</strong>
            </div>
          </div>
          {!canManageChecklist ? (
            <AlertBanner variant="info" title={t("paymentDraft.checklist.readOnlyTitle")}>
              {t("paymentDraft.checklist.readOnlyBody")}
            </AlertBanner>
          ) : null}
          {checklist.isError ? (
            <AlertBanner variant="danger" title={t("paymentDraft.checklist.errorTitle")}>
              {t("paymentDraft.checklist.errorBody")}
            </AlertBanner>
          ) : null}
          <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
            {(checklist.data?.items ?? []).map((item) => (
              <ChecklistItemEditor
                key={item.item_key}
                canManage={canManageChecklist}
                item={item}
                isSaving={checklist.savingItemKey === item.item_key}
                onSave={(itemStatus, comment) => checklist.updateItem(item.item_key, {
                  item_status: itemStatus,
                  comment: comment.trim() || null,
                })}
              />
            ))}
          </div>
          <Button type="button" variant="outline" iconLeft={<Icon name="refresh" />} loading={checklist.isLoading} onClick={() => void checklist.refresh()}>
            {t("common.refresh")}
          </Button>
        </div>
      </Card>

      <Card title={t("paymentDraft.filters.title")} subtitle={t("paymentDraft.filters.subtitle")}>
        <div className="form-grid">
          <FormField label={t("advanceBatch.filters.period")}>
            <input value={periodId} onChange={(event) => setPeriodId(event.target.value)} placeholder={t("advanceBatch.filters.periodPlaceholder")} />
          </FormField>
          <FormField label={t("advanceBatch.filters.academicYear")}>
            <input value={academicYear} onChange={(event) => setAcademicYear(event.target.value)} />
          </FormField>
          <FormField label={t("advanceBatch.filters.semester")}>
            <input value={semester} onChange={(event) => setSemester(event.target.value)} />
          </FormField>
          <FormField label={t("advanceBatch.filters.examType")}>
            <input value={examType} onChange={(event) => setExamType(event.target.value)} />
          </FormField>
        </div>
      </Card>

      <Card
        title={t("paymentDraft.paper.title")}
        subtitle={t("paymentDraft.paper.subtitle")}
        actions={
          <Button type="button" variant="outline" iconLeft={<Icon name="add" />} onClick={() => setPaperRows((rows) => [...rows, newPaperRow()])}>
            {t("paymentDraft.paper.add")}
          </Button>
        }
      >
        <div className="page-stack">
          {paperRows.map((row) => (
            <div key={row.local_id} className="form-grid form-grid--paper">
              <FormField label={t("paymentDraft.table.examDate")}>
                <input value={row.exam_date} onChange={(event) => updatePaperRow(row.local_id, { exam_date: event.target.value })} placeholder={t("paymentDraft.paper.examDate")} />
              </FormField>
              <FormField label={t("paymentDraft.table.timeSlot")}>
                <input value={row.exam_time || ""} onChange={(event) => updatePaperRow(row.local_id, { exam_time: event.target.value })} placeholder={t("paymentDraft.paper.examTime")} />
              </FormField>
              <FormField label={t("paymentDraft.paper.count")}>
                <input min={0} type="number" value={row.committee_count} onChange={(event) => updatePaperRow(row.local_id, { committee_count: Number(event.target.value) })} />
              </FormField>
              <FormField label={t("paymentDraft.paper.notes")}>
                <input value={row.notes || ""} onChange={(event) => updatePaperRow(row.local_id, { notes: event.target.value })} placeholder={t("paymentDraft.paper.notes")} />
              </FormField>
              <Button type="button" variant="ghost" iconLeft={<Icon name="delete" />} onClick={() => setPaperRows((rows) => rows.filter((item) => item.local_id !== row.local_id))}>
                {t("common.delete")}
              </Button>
            </div>
          ))}
        </div>
        <div className="mt-4 flex flex-wrap gap-3">
          <Button type="button" iconLeft={<Icon name="calculate" />} loading={isLoading} onClick={submitPreview}>
            {t("paymentDraft.actions.preview")}
          </Button>
          <Button type="button" variant="outline" onClick={() => setPaperRows([newPaperRow()])}>
            {t("common.reset")}
          </Button>
          {canManageReview && (
            <Button
              type="button"
              variant="outline"
              iconLeft={<Icon name="download" />}
              loading={isExporting}
              disabled={latestReviewStatus !== "ACCEPTED_FOR_DRAFT_EXPORT" || !data}
              title={
                latestReviewStatus !== "ACCEPTED_FOR_DRAFT_EXPORT"
                  ? t("paymentDraft.actions.exportGated")
                  : undefined
              }
              onClick={submitExport}
            >
              {t("paymentDraft.actions.exportDraft")}
            </Button>
          )}
        </div>
        <AlertBanner
          variant={latestReviewStatus === "ACCEPTED_FOR_DRAFT_EXPORT" ? "info" : "warning"}
          title={t("paymentDraft.actions.exportSafetyTitle")}
          action={<Badge variant={reviewStatusVariant(latestReviewStatus)}>{statusLabel(latestReviewStatus)}</Badge>}
        >
          {latestReviewStatus === "ACCEPTED_FOR_DRAFT_EXPORT"
            ? t("paymentDraft.actions.exportSafetyReady")
            : t("paymentDraft.actions.exportSafetyBlocked")}
        </AlertBanner>
      </Card>

      {isError ? (
        <Card>
          <EmptyState icon={<Icon name="warning" />} title={t("paymentDraft.empty.errorTitle")} />
        </Card>
      ) : null}

      {data ? (
        <>
          <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            <Card title={t("paymentDraft.summary.invigilation")} subtitle={String(data.totals.invigilation_committee_count)}>
              <p className="metric-value">{formatCurrency(data.totals.invigilation_compensation_amount)}</p>
            </Card>
            <Card title={t("paymentDraft.summary.paper")} subtitle={String(data.totals.paper_distribution_committee_count)}>
              <p className="metric-value">{formatCurrency(data.totals.paper_distribution_compensation_amount)}</p>
            </Card>
            <Card title={t("paymentDraft.summary.grandTotal")} subtitle={t("paymentDraft.summary.notAuthorized")}>
              <p className="metric-value">{formatCurrency(data.totals.grand_total_amount)}</p>
            </Card>
            <Card title={t("paymentDraft.summary.review")} subtitle={data.metadata.term_label}>
              <Badge variant="gold">DRAFT_NOT_AUTHORIZED</Badge>
            </Card>
          </section>

          {data.rows.length === 0 ? (
            <Card>
              <EmptyState icon={<Icon name="info" />} title={t("paymentDraft.empty.noRowsTitle")} description={t("paymentDraft.empty.noRowsDescription")} />
            </Card>
          ) : (
            <Card title={t("paymentDraft.table.title")} subtitle={t("paymentDraft.table.subtitle")}>
              <DataTable columns={draftColumns} rows={data.rows} rowKey={(row) => `${row.normalized_exam_date || row.exam_date}:${row.time_slot}`} compact tableLayout="fixed" />
            </Card>
          )}

          <Card title={t("paymentDraft.warnings.title")} subtitle={t("paymentDraft.warnings.subtitle")}>
            <ul className="ui-list">
              {(data.warnings.length ? data.warnings : [t("paymentDraft.warnings.none")]).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </Card>
        </>
      ) : (
        <Card>
          <EmptyState icon={<Icon name="info" />} title={t("paymentDraft.empty.initialTitle")} description={t("paymentDraft.empty.initialDescription")} />
        </Card>
      )}
    </div>
  );
}
