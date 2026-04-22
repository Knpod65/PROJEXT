import { useCallback, useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { useI18n } from "@/i18n";
import { ApiError } from "@/services/api";
import { closeTerm, getTermPreview } from "@/services/settings.service";
import { useUi } from "@/store/ui.store";
import type { TermLifecyclePreviewItem, TermLifecycleStatus, TermSettingsPreview } from "@/types/api";
import { formatDateTime, formatTranslatedValue } from "@/utils/format";

function getStatusBadgeVariant(status?: TermLifecycleStatus | null) {
  switch (status) {
    case "active":
      return "green";
    case "locked":
      return "crimson";
    case "archived":
      return "gold";
    case "draft":
      return "blue";
    default:
      return "gray";
  }
}

function canCloseTerm(term?: TermLifecyclePreviewItem | null) {
  if (!term) {
    return false;
  }
  return term.is_editable && !term.is_read_only && (term.lifecycle_status === "active" || term.lifecycle_status === "archived");
}

export function SettingsTermPreviewPanel() {
  const { t } = useI18n();
  const { toast } = useUi();
  const [preview, setPreview] = useState<TermSettingsPreview | null>(null);
  const [requestedPeriodId, setRequestedPeriodId] = useState<number | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [closeDialogOpen, setCloseDialogOpen] = useState(false);
  const [closing, setClosing] = useState(false);
  const [closeErrors, setCloseErrors] = useState<string[]>([]);

  const formatTermLabel = (term?: TermLifecyclePreviewItem | null) => {
    if (!term) {
      return t("settings.term.noTermAvailable");
    }
    return term.label || `${term.exam_type} ${term.semester}/${term.academic_year}`;
  };

  const getCloseErrorMessages = (closeError: unknown) => {
    if (closeError instanceof ApiError && typeof closeError.data === "object" && closeError.data) {
      const data = closeError.data as { blocking_reasons?: unknown; plain_language_summary?: unknown; detail?: unknown };
      if (Array.isArray(data.blocking_reasons) && data.blocking_reasons.length > 0) {
        return data.blocking_reasons.map((reason) => String(reason));
      }
      if (typeof data.plain_language_summary === "string" && data.plain_language_summary) {
        return [data.plain_language_summary];
      }
      if (typeof data.detail === "string" && data.detail) {
        return [data.detail];
      }
    }

    if (closeError instanceof Error && closeError.message) {
      return [closeError.message];
    }

    return [t("errors.closeTerm")];
  };

  const loadPreview = useCallback(
    async (periodId?: number) => {
      setLoading(true);
      setError(null);
      setCloseErrors([]);

      try {
        const next = await getTermPreview(periodId);
        setPreview(next);
      } catch (loadError) {
        const message = loadError instanceof Error ? loadError.message : t("errors.loadTermPreview");
        setError(message);
        toast(message, "error");
      } finally {
        setLoading(false);
      }
    },
    [t, toast],
  );

  useEffect(() => {
    void loadPreview(requestedPeriodId);
  }, [loadPreview, requestedPeriodId]);

  const selectedTerm = preview?.selected_term ?? null;
  const hasTerms = (preview?.available_terms.length ?? 0) > 0;
  const selectValue = requestedPeriodId ?? preview?.selected_term?.id ?? preview?.default_preview_term_id ?? "";
  const showCloseButton = canCloseTerm(selectedTerm);

  const handleCloseTerm = async () => {
    if (!selectedTerm) {
      return;
    }

    setClosing(true);
    setCloseErrors([]);

    try {
      const response = await closeTerm(selectedTerm.id);
      setRequestedPeriodId(selectedTerm.id);
      await loadPreview(selectedTerm.id);
      setCloseDialogOpen(false);
      toast(response.plain_language_summary || t("settings.term.closeSuccess"), "success");
    } catch (closeError) {
      const messages = getCloseErrorMessages(closeError);
      setCloseErrors(messages);
      toast(messages[0], "error");
    } finally {
      setClosing(false);
    }
  };

  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <div className="settings-row" style={{ alignItems: "end" }}>
        <label className="form-field">
          <span>{t("settings.term.previewTerm")}</span>
          <select
            disabled={!hasTerms || loading}
            value={selectValue}
            onChange={(event) => {
              const nextValue = event.target.value;
              setRequestedPeriodId(nextValue ? Number(nextValue) : undefined);
            }}
          >
            {!hasTerms ? <option value="">{t("settings.term.noTermsAvailable")}</option> : null}
            {preview?.available_terms.map((term) => (
              <option key={term.id} value={term.id}>
                {formatTermLabel(term)}
              </option>
            ))}
          </select>
        </label>
        <Button type="button" variant="outline" disabled={loading} onClick={() => setRequestedPeriodId(undefined)}>
          {t("settings.term.showDefault")}
        </Button>
        {showCloseButton ? (
          <Button type="button" variant="danger" disabled={loading || closing} onClick={() => setCloseDialogOpen(true)}>
            {t("settings.term.closeTerm")}
          </Button>
        ) : null}
      </div>

      {closeErrors.length > 0 ? (
        <div
          style={{
            padding: "14px 16px",
            borderRadius: "16px",
            border: "1px solid rgba(220, 38, 38, 0.14)",
            background: "rgba(220, 38, 38, 0.07)",
            display: "grid",
            gap: "6px",
          }}
        >
          <strong>{t("settings.term.closeBlocked")}</strong>
          <ul style={{ margin: 0, paddingLeft: "18px", color: "var(--text-mid)" }}>
            {closeErrors.map((message) => (
              <li key={message}>{message}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {error ? (
        <div className="empty-state" style={{ minHeight: "180px", background: "var(--surface2)", borderRadius: "18px" }}>
          <h3 className="empty-state__title">{t("settings.term.unavailableTitle")}</h3>
          <p className="empty-state__description">{error}</p>
        </div>
      ) : null}

      {!error ? (
        <>
          <div
            className="summary-grid"
            style={{
              display: "grid",
              gap: "12px",
            }}
          >
            <div className="summary-box">
              <span>{t("settings.term.activeTerm")}</span>
              <strong>{formatTermLabel(preview?.current_active_term)}</strong>
              <small style={{ color: "var(--text-mid)" }}>
                {preview?.current_active_term ? t("settings.term.activeTermCurrent") : t("settings.term.activeTermMissing")}
              </small>
            </div>
            <div className="summary-box">
              <span>{t("settings.term.selectedTerm")}</span>
              <strong>{formatTermLabel(selectedTerm)}</strong>
              <small style={{ color: "var(--text-mid)" }}>
                {selectedTerm ? `${selectedTerm.semester}/${selectedTerm.academic_year} • ${selectedTerm.exam_type}` : t("settings.term.selectedTermMissing")}
              </small>
            </div>
            <div className="summary-box">
              <span>{t("settings.term.statusTitle")}</span>
              <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
                <Badge variant={getStatusBadgeVariant(preview?.selected_term_status)}>
                  {preview?.selected_term_status ? formatTranslatedValue("status", preview.selected_term_status) : t("common.unknown")}
                </Badge>
                <strong>{selectedTerm?.is_historical ? t("settings.term.historicalTerm") : t("settings.term.currentContext")}</strong>
              </div>
              <small style={{ color: "var(--text-mid)" }}>
                {preview?.latest_term ? t("settings.term.latestTerm", { label: formatTermLabel(preview.latest_term) }) : t("settings.term.latestTermMissing")}
              </small>
            </div>
            <div className="summary-box">
              <span>{t("settings.term.editability")}</span>
              <strong>{preview?.selected_term_read_only ? t("settings.term.readOnly") : preview?.selected_term_editable ? t("settings.term.editable") : t("settings.term.previewOnly")}</strong>
              <small style={{ color: "var(--text-mid)" }}>
                {preview?.selected_term_read_only
                  ? t("settings.term.editingNotAllowed")
                  : t("settings.term.previewDoesNotChangeLifecycle")}
              </small>
            </div>
          </div>

          {selectedTerm?.is_read_only ? (
            <div
              style={{
                padding: "16px 18px",
                borderRadius: "18px",
                border: "1px solid rgba(220, 38, 38, 0.14)",
                background: "rgba(220, 38, 38, 0.07)",
                display: "grid",
                gap: "6px",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
                <Badge variant="crimson" size="sm">
                  {t("settings.term.lockedBadge")}
                </Badge>
                <strong>{t("settings.term.lockedMessage")}</strong>
              </div>
              <p style={{ margin: 0, color: "var(--text-mid)" }}>{t("settings.term.lockedDescription")}</p>
            </div>
          ) : null}

          <div className="dashboard-shell-grid">
            <div
              style={{
                padding: "18px",
                borderRadius: "20px",
                background: "var(--surface2)",
                border: "1px solid rgba(231, 226, 218, 0.9)",
                display: "grid",
                gap: "14px",
              }}
            >
              <div className="section-heading">
                <h4 style={{ margin: 0 }}>{t("settings.term.lifecycleDetails")}</h4>
                {selectedTerm ? <Badge variant={getStatusBadgeVariant(selectedTerm.lifecycle_status)} size="sm">{formatTranslatedValue("status", selectedTerm.lifecycle_status)}</Badge> : null}
              </div>
              <div style={{ display: "grid", gap: "10px" }}>
                <div className="summary-box" style={{ padding: "14px" }}>
                  <span>{t("settings.term.latestHistorical")}</span>
                  <strong>{formatTermLabel(preview?.latest_historical_term)}</strong>
                </div>
                <div className="summary-box" style={{ padding: "14px" }}>
                  <span>{t("settings.term.archivedAt")}</span>
                  <strong>{formatDateTime(selectedTerm?.archived_at)}</strong>
                </div>
                <div className="summary-box" style={{ padding: "14px" }}>
                  <span>{t("settings.term.lockedAt")}</span>
                  <strong>{formatDateTime(selectedTerm?.locked_at)}</strong>
                </div>
                <div className="summary-box" style={{ padding: "14px" }}>
                  <span>{t("settings.term.createdAt")}</span>
                  <strong>{formatDateTime(selectedTerm?.created_at)}</strong>
                </div>
              </div>
            </div>

            <div
              style={{
                padding: "18px",
                borderRadius: "20px",
                background: "var(--surface2)",
                border: "1px solid rgba(231, 226, 218, 0.9)",
                display: "grid",
                gap: "14px",
              }}
            >
              <div className="section-heading">
                <h4 style={{ margin: 0 }}>{t("settings.term.policyExplanation")}</h4>
                {loading ? <Badge variant="gray" size="sm">{t("common.loading")}</Badge> : null}
              </div>
              <div className="summary-box" style={{ padding: "14px" }}>
                <span>{t("settings.term.plainLanguageSummary")}</span>
                <strong style={{ fontSize: "1rem", lineHeight: 1.5 }}>{preview?.plain_language_summary ?? t("settings.term.noSummary")}</strong>
              </div>
              <div className="summary-box" style={{ padding: "14px" }}>
                <span>{t("settings.term.historicalVisibility")}</span>
                <strong style={{ fontSize: "1rem", lineHeight: 1.5 }}>
                  {preview?.historical_visibility_summary ?? t("settings.term.noHistoricalVisibility")}
                </strong>
              </div>
              <div className="summary-box" style={{ padding: "14px" }}>
                <span>{t("settings.term.previewNote")}</span>
                <strong style={{ fontSize: "1rem", lineHeight: 1.5 }}>
                  {selectedTerm?.preview_summary ?? t("settings.term.previewNoteFallback")}
                </strong>
              </div>
            </div>
          </div>
        </>
      ) : null}

      <ConfirmDialog
        open={closeDialogOpen}
        title={t("settings.term.closeDialogTitle")}
        description={
          selectedTerm
            ? t("settings.term.closeDialogDescription", { label: formatTermLabel(selectedTerm) })
            : t("settings.term.closeDialogFallback")
        }
        confirmLabel={t("settings.term.closeTerm")}
        variant="danger"
        loading={closing}
        onConfirm={() => void handleCloseTerm()}
        onCancel={() => {
          if (!closing) {
            setCloseDialogOpen(false);
          }
        }}
      />
    </div>
  );
}
