import { useMemo, useState } from "react";

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
import { usePaymentDocumentReviews } from "@/hooks/domain/usePaymentDocumentReviews";
import { useI18n } from "@/i18n";
import { useAuth } from "@/store/auth.store";
import type { OfficialPaymentDraftManualPaperRow, OfficialPaymentDraftRow } from "@/types/officialPaymentDraft";
import type { PaymentDocumentReviewRecord, PaymentDocumentReviewStatus } from "@/types/paymentDocumentReview";
import { formatCurrency } from "@/utils/format";
import { canCommentOnPaymentDocumentReview, canManagePaymentDocumentReview } from "@/utils/permissions";

type EditablePaperRow = OfficialPaymentDraftManualPaperRow & { local_id: string };

const REVIEW_STATUS_OPTIONS: PaymentDocumentReviewStatus[] = [
  "DRAFT_READY_FOR_REVIEW",
  "UNDER_REVIEW",
  "REVISIONS_REQUESTED",
  "ACCEPTED_FOR_DRAFT_EXPORT",
  "REJECTED_REDESIGN_REQUIRED",
  "FINAL_AUTHORIZATION_REQUIRED",
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

export default function OfficialPaymentDocumentDraft() {
  const { t } = useI18n();
  const { user } = useAuth();
  const [periodId, setPeriodId] = useState("");
  const [academicYear, setAcademicYear] = useState("2568");
  const [semester, setSemester] = useState("2");
  const [examType, setExamType] = useState("final");
  const [paperRows, setPaperRows] = useState<EditablePaperRow[]>([newPaperRow()]);
  const { data, isError, isLoading, preview } = useOfficialPaymentDraftPreview();
  const [reviewComment, setReviewComment] = useState("");
  const [reviewDecision, setReviewDecision] = useState("");
  const [reviewStatus, setReviewStatus] = useState<PaymentDocumentReviewStatus>("DRAFT_READY_FOR_REVIEW");
  const canCommentReview = canCommentOnPaymentDocumentReview(user);
  const canManageReview = canManagePaymentDocumentReview(user);
  const documentId = useMemo(
    () => `ADVANCE_PAYMENT_DRAFT_SUMMARY:${academicYear || "unknown"}:${semester || "unknown"}:${examType || "unknown"}:${periodId || "all"}`,
    [academicYear, examType, periodId, semester],
  );
  const settingsTerm = useMemo(() => `${semester || "2"}/${academicYear || "2568"}`, [academicYear, semester]);
  const reviewTerm = useMemo(() => `${semester || "-"} / ${academicYear || "-"}`, [academicYear, semester]);
  const reviewRecords = usePaymentDocumentReviews(documentId);
  const paymentSettings = usePaymentDocumentSettings(settingsTerm);

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
        <Badge variant={reviewStatusVariant(row.review_status)}>{row.review_status}</Badge>
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
          <Badge variant={paymentSettings.data?.configuration_status === "CONFIGURED" ? "green" : "gold"}>
            {paymentSettings.data?.configuration_status ?? "PENDING_CONFIGURATION"}
          </Badge>
        }
      >
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="summary-box">
            <span>{t("paymentDraft.settings.term")}</span>
            <strong>{settingsTerm}</strong>
          </div>
          <div className="summary-box">
            <span>{t("paymentDraft.settings.weekdayRate")}</span>
            <strong>{amountToCurrency(paymentSettings.data?.weekday_rate)}</strong>
          </div>
          <div className="summary-box">
            <span>{t("paymentDraft.settings.weekendRate")}</span>
            <strong>{amountToCurrency(paymentSettings.data?.weekend_rate)}</strong>
          </div>
          <div className="summary-box">
            <span>{t("paymentDraft.settings.group")}</span>
            <strong>{paymentSettings.data?.paper_distribution_responsible_group ?? "Education_Student_Quality"}</strong>
          </div>
        </div>
        <p className="mt-4 text-sm text-gray-500">{t("paymentDraft.settings.nonCalculationNote")}</p>
      </Card>

      <Card
        title={t("paymentDraft.review.title")}
        subtitle={t("paymentDraft.review.subtitle")}
        actions={<Badge variant={reviewStatusVariant(latestReviewStatus)}>{latestReviewStatus}</Badge>}
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
                      {status}
                    </option>
                  ))}
                </select>
              </FormField>
            ) : (
              <FormField label={t("paymentDraft.review.status")}>
                <input value="DRAFT_READY_FOR_REVIEW" readOnly />
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
        </div>
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
