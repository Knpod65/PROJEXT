import { useCallback, useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import type { DataTableColumn } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { StatusChip, type StatusTone } from "@/components/ui/StatusChip";
import { useI18n } from "@/i18n";
import {
  getImportAuditSessionDetail,
  listImportAuditRows,
  listImportAuditSessions,
} from "@/services/import-audit.service";
import { useUi } from "@/store/ui.store";
import type {
  ImportAuditIssueSummaryItem,
  ImportAuditRowLog,
  ImportAuditSessionDetail,
  ImportSession,
} from "@/types/api";
import { formatDateTime, formatNumber, formatTranslatedValue } from "@/utils/format";

function statusVariant(status?: string) {
  if (status === "completed") return "success" satisfies StatusTone;
  if (status === "completed_with_skips") return "warning" satisfies StatusTone;
  if (status === "blocked") return "blocked" satisfies StatusTone;
  if (status === "error") return "danger" satisfies StatusTone;
  if (status === "warning") return "warning" satisfies StatusTone;
  return "neutral" satisfies StatusTone;
}

export function ImportAuditPage() {
  const { t } = useI18n();
  const { toast } = useUi();

  const [sessions, setSessions] = useState<ImportSession[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(null);

  const [sessionDetail, setSessionDetail] = useState<ImportAuditSessionDetail | null>(null);
  const [rows, setRows] = useState<ImportAuditRowLog[]>([]);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [loadingRows, setLoadingRows] = useState(false);

  const [statusFilter, setStatusFilter] = useState("");
  const [errorCodeFilter, setErrorCodeFilter] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

  const loadSessions = useCallback(async () => {
    setLoadingSessions(true);
    try {
      const response = await listImportAuditSessions();
      setSessions(response);
      if (!selectedSessionId && response.length > 0) {
        setSelectedSessionId(response[0].id);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : t("errors.loadImportSessions");
      toast(message, "error");
    } finally {
      setLoadingSessions(false);
    }
  }, [selectedSessionId, t, toast]);

  const loadSessionDetail = useCallback(
    async (sessionId: number) => {
      setLoadingDetail(true);
      try {
        const response = await getImportAuditSessionDetail(sessionId);
        setSessionDetail(response);
      } catch (error) {
        const message = error instanceof Error ? error.message : t("errors.loadImportSessionDetail");
        toast(message, "error");
      } finally {
        setLoadingDetail(false);
      }
    },
    [t, toast],
  );

  const loadRows = useCallback(
    async (sessionId: number) => {
      setLoadingRows(true);
      try {
        const response = await listImportAuditRows(sessionId, {
          status: statusFilter || undefined,
          error_code: errorCodeFilter || undefined,
          q: searchTerm || undefined,
        });
        setRows(response.rows);
      } catch (error) {
        const message = error instanceof Error ? error.message : t("errors.loadImportRowLogs");
        toast(message, "error");
      } finally {
        setLoadingRows(false);
      }
    },
    [errorCodeFilter, searchTerm, statusFilter, t, toast],
  );

  useEffect(() => {
    void loadSessions();
  }, [loadSessions]);

  useEffect(() => {
    if (!selectedSessionId) {
      setSessionDetail(null);
      setRows([]);
      return;
    }

    void loadSessionDetail(selectedSessionId);
    void loadRows(selectedSessionId);
  }, [selectedSessionId, loadRows, loadSessionDetail]);

  const issueCodeOptions = useMemo(() => {
    const summary = sessionDetail?.issue_summary ?? [];
    return summary
      .map((item) => item.code)
      .filter((code): code is string => Boolean(code));
  }, [sessionDetail]);

  const sessionColumns = useMemo<DataTableColumn<ImportSession>[]>(
    () => [
      {
        key: "import_session_id",
        label: t("import.audit.sessionColumn.session"),
        width: "90px",
        minWidth: "90px",
        align: "center",
        render: (row: ImportSession) => `#${row.import_session_id ?? row.id}`,
      },
      {
        key: "import_type",
        label: t("import.audit.sessionColumn.type"),
        width: "130px",
        minWidth: "130px",
        render: (row: ImportSession) => row.import_type ?? "-",
      },
      {
        key: "status",
        label: t("common.status"),
        width: "130px",
        minWidth: "130px",
        align: "center",
        render: (row: ImportSession) => (
          <StatusChip tone={statusVariant(row.status)}>{row.status ? formatTranslatedValue("status", row.status) : t("common.unknown")}</StatusChip>
        ),
      },
      {
        key: "term",
        label: t("import.audit.sessionColumn.term"),
        minWidth: "160px",
        render: (row: ImportSession) => `${row.academic_year}/${row.semester} (${row.exam_type})`,
      },
      {
        key: "imported_by",
        label: t("import.audit.sessionColumn.importedBy"),
        minWidth: "150px",
        render: (row: ImportSession) => row.imported_by ?? "-",
      },
      {
        key: "started_at",
        label: t("import.audit.sessionColumn.started"),
        width: "170px",
        minWidth: "170px",
        render: (row: ImportSession) => formatDateTime(row.started_at),
      },
      {
        key: "completed_at",
        label: t("import.audit.sessionColumn.completed"),
        width: "170px",
        minWidth: "170px",
        render: (row: ImportSession) => formatDateTime(row.completed_at),
      },
      {
        key: "counts",
        label: t("import.audit.sessionColumn.counts"),
        width: "140px",
        minWidth: "140px",
        align: "center",
        render: (row: ImportSession) =>
          `${formatNumber(row.imported_rows)} / ${formatNumber(row.skipped_rows)} / ${formatNumber(row.error_rows)}`,
      },
      {
        key: "action",
        label: t("common.actions"),
        width: "110px",
        minWidth: "110px",
        align: "center",
        render: (row: ImportSession) => (
          <Button
            type="button"
            size="sm"
            variant={selectedSessionId === row.id ? "primary" : "outline"}
            onClick={() => setSelectedSessionId(row.id)}
          >
            {t("common.view")}
          </Button>
        ),
      },
    ],
    [selectedSessionId, t],
  );

  const rowColumns = useMemo<DataTableColumn<ImportAuditRowLog>[]>(
    () => [
      {
        key: "row_number",
        label: t("import.audit.rowColumn.row"),
        width: "90px",
        minWidth: "90px",
        align: "center",
      },
      {
        key: "status",
        label: t("common.status"),
        width: "120px",
        minWidth: "120px",
        align: "center",
        render: (row: ImportAuditRowLog) => (
          <StatusChip tone={statusVariant(row.status)}>{formatTranslatedValue("status", row.status)}</StatusChip>
        ),
      },
      {
        key: "error_code",
        label: t("common.errorCode"),
        width: "130px",
        minWidth: "130px",
        render: (row: ImportAuditRowLog) => row.error_code ?? "-",
      },
      {
        key: "error_message",
        label: t("import.audit.rowColumn.errorMessage"),
        minWidth: "240px",
        render: (row: ImportAuditRowLog) => row.error_message ?? "-",
      },
      {
        key: "was_selected",
        label: t("common.selected"),
        width: "100px",
        minWidth: "100px",
        align: "center",
        render: (row: ImportAuditRowLog) => (row.was_selected ? t("common.yes") : t("common.no")),
      },
      {
        key: "was_imported",
        label: t("common.imported"),
        width: "100px",
        minWidth: "100px",
        align: "center",
        render: (row: ImportAuditRowLog) => (row.was_imported ? t("common.yes") : t("common.no")),
      },
      {
        key: "override_reason",
        label: t("import.audit.rowColumn.overrideReason"),
        minWidth: "220px",
        render: (row: ImportAuditRowLog) => row.override_reason ?? "-",
      },
      {
        key: "raw_data_preview",
        label: t("import.audit.rowColumn.rawPreview"),
        minWidth: "260px",
      },
    ],
    [t],
  );

  const selectedSession = sessionDetail?.session;

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">{t("import.audit.heroEyebrow")}</span>
          <h1 className="page-hero__title">{t("import.audit.heroTitle")}</h1>
          <p className="page-hero__description">{t("import.audit.heroDescription")}</p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => void loadSessions()} loading={loadingSessions}>
            {t("import.audit.refreshSessions")}
          </Button>
        </div>
      </section>

      <Card title={t("import.audit.sessionListTitle")} subtitle={t("import.audit.sessionListSubtitle")}>
        <DataTable
          columns={sessionColumns}
          rows={sessions}
          rowKey={(row) => row.id}
          loading={loadingSessions}
          compact
          tableLayout="fixed"
          maxHeight={380}
          scrollThreshold={5}
          emptyTitle={t("import.audit.noSessionsTitle")}
          emptyDescription={t("import.audit.noSessionsDescription")}
        />
      </Card>

      <Card title={t("import.audit.sessionDetailTitle")} subtitle={t("import.audit.sessionDetailSubtitle")}>
        {!selectedSession ? (
          <EmptyState title={t("import.audit.noSessionSelectedTitle")} description={t("import.audit.noSessionSelectedDescription")} />
        ) : (
          <div className="page-stack">
            <div className="import-summary-grid">
              <article className="import-summary-card">
                <span>{t("import.audit.summarySession")}</span>
                <strong>#{selectedSession.import_session_id ?? selectedSession.id}</strong>
              </article>
              <article className="import-summary-card">
                <span>{t("common.status")}</span>
                <strong>{selectedSession.status ? formatTranslatedValue("status", selectedSession.status) : "-"}</strong>
              </article>
              <article className="import-summary-card">
                <span>{t("import.audit.summaryTotalRows")}</span>
                <strong>{formatNumber(selectedSession.total_rows)}</strong>
              </article>
              <article className="import-summary-card">
                <span>{t("import.audit.summaryImportedRows")}</span>
                <strong>{formatNumber(selectedSession.imported_rows)}</strong>
              </article>
              <article className="import-summary-card">
                <span>{t("import.audit.summarySkippedRows")}</span>
                <strong>{formatNumber(selectedSession.skipped_rows)}</strong>
              </article>
              <article className="import-summary-card">
                <span>{t("import.audit.summaryErrorRows")}</span>
                <strong>{formatNumber(selectedSession.error_rows)}</strong>
              </article>
            </div>

            <div className="page-stack">
              {loadingDetail ? <p>{t("common.loading")}</p> : null}
              {(sessionDetail?.issue_summary ?? []).length === 0 ? (
                <p>{t("import.audit.noIssueSummary")}</p>
              ) : (
                (sessionDetail?.issue_summary ?? []).map((issue: ImportAuditIssueSummaryItem, index: number) => (
                  <p key={`${issue.code ?? "none"}-${index}`} className="import-issue import-issue--warning">
                    <strong>{issue.code ?? "-"}</strong> ({formatNumber(issue.count)}): {issue.message ?? "-"}
                  </p>
                ))
              )}
            </div>
          </div>
        )}
      </Card>

      <Card title={t("import.audit.rowLogsTitle")} subtitle={t("import.audit.rowLogsSubtitle")}>
        <div className="dashboard-shell-grid">
          <label className="form-field">
            <span>{t("common.status")}</span>
            <select value={statusFilter} onChange={(event) => setStatusFilter(event.currentTarget.value)}>
              <option value="">{t("common.allStatuses")}</option>
              <option value="valid">{formatTranslatedValue("status", "valid")}</option>
              <option value="warning">{formatTranslatedValue("status", "warning")}</option>
              <option value="error">{formatTranslatedValue("status", "error")}</option>
            </select>
          </label>

          <label className="form-field">
            <span>{t("common.errorCode")}</span>
            <select value={errorCodeFilter} onChange={(event) => setErrorCodeFilter(event.currentTarget.value)}>
              <option value="">{t("common.all")}</option>
              {issueCodeOptions.map((code) => (
                <option key={code} value={code}>
                  {code}
                </option>
              ))}
            </select>
          </label>

          <label className="form-field">
            <span>{t("common.search")}</span>
            <input
              type="text"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.currentTarget.value)}
              placeholder={t("import.audit.searchPlaceholder")}
            />
          </label>

          <div className="inline-actions">
            <Button
              type="button"
              onClick={() => selectedSessionId && void loadRows(selectedSessionId)}
              disabled={!selectedSessionId}
              loading={loadingRows}
            >
              {t("common.applyFilters")}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setStatusFilter("");
                setErrorCodeFilter("");
                setSearchTerm("");
              }}
            >
              {t("import.audit.resetFilters")}
            </Button>
          </div>
        </div>

        <DataTable
          columns={rowColumns}
          rows={rows}
          rowKey={(row) => row.id}
          loading={loadingRows}
          compact
          tableLayout="fixed"
          maxHeight={560}
          scrollThreshold={5}
          emptyTitle={t("import.audit.noRowLogsTitle")}
          emptyDescription={t("import.audit.noRowLogsDescription")}
        />
      </Card>
    </div>
  );
}
