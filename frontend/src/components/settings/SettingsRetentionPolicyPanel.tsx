import { useEffect, useMemo, useState } from "react";

import { SettingsField } from "@/components/settings/SettingsField";
import { SettingsToggle } from "@/components/settings/SettingsToggle";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { useI18n } from "@/i18n";
import { ApiError } from "@/services/api";
import { getRetentionPolicy, updateRetentionPolicy } from "@/services/settings.service";
import { useUi } from "@/store/ui.store";
import type { ExamFileRetentionMode, RetentionPolicy, RetentionPolicyUpdateInput } from "@/types/api";
import { formatTranslatedValue } from "@/utils/format";

interface RetentionPolicyDraft {
  exam_file_retention_mode: ExamFileRetentionMode;
  exam_file_retention_years: string;
  exam_file_destroy_requires_approval: boolean;
  exam_file_archive_before_destroy: boolean;
  retain_import_audit_logs_years: string;
  retain_import_raw_files: boolean;
  historical_term_data_retained_indefinitely: boolean;
}

function toDraft(policy: RetentionPolicy): RetentionPolicyDraft {
  return {
    exam_file_retention_mode: policy.exam_file_retention_mode,
    exam_file_retention_years:
      policy.exam_file_retention_years === null || policy.exam_file_retention_years === undefined
        ? ""
        : String(policy.exam_file_retention_years),
    exam_file_destroy_requires_approval: policy.exam_file_destroy_requires_approval,
    exam_file_archive_before_destroy: policy.exam_file_archive_before_destroy,
    retain_import_audit_logs_years: String(policy.retain_import_audit_logs_years),
    retain_import_raw_files: policy.retain_import_raw_files,
    historical_term_data_retained_indefinitely: policy.historical_term_data_retained_indefinitely,
  };
}

function toPayload(draft: RetentionPolicyDraft): RetentionPolicyUpdateInput {
  const yearsValue = draft.exam_file_retention_years.trim();
  const auditYearsValue = draft.retain_import_audit_logs_years.trim();

  return {
    exam_file_retention_mode: draft.exam_file_retention_mode,
    exam_file_retention_years: yearsValue ? Number(yearsValue) : null,
    exam_file_destroy_requires_approval: draft.exam_file_destroy_requires_approval,
    exam_file_archive_before_destroy: draft.exam_file_archive_before_destroy,
    retain_import_audit_logs_years: Number(auditYearsValue),
    retain_import_raw_files: draft.retain_import_raw_files,
    historical_term_data_retained_indefinitely: draft.historical_term_data_retained_indefinitely,
  };
}

function getStatusVariant(mode: ExamFileRetentionMode) {
  if (mode === "manual") return "blue" as const;
  if (mode === "years") return "gold" as const;
  return "green" as const;
}

function getSaveErrorMessage(error: unknown, fallback: string) {
  if (error instanceof ApiError) {
    return error.message;
  }

  return error instanceof Error ? error.message : fallback;
}

export function SettingsRetentionPolicyPanel() {
  const { t } = useI18n();
  const { toast } = useUi();
  const [policy, setPolicy] = useState<RetentionPolicy | null>(null);
  const [draft, setDraft] = useState<RetentionPolicyDraft | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const retentionModeOptions: Array<{ value: ExamFileRetentionMode; label: string }> = [
    { value: "manual", label: formatTranslatedValue("status", "manual") },
    { value: "semester_end", label: formatTranslatedValue("status", "semester_end") },
    { value: "academic_year_end", label: formatTranslatedValue("status", "academic_year_end") },
    { value: "years", label: formatTranslatedValue("status", "years") },
  ];

  const getDraftValidationError = (currentDraft: RetentionPolicyDraft): string | null => {
    const auditYears = Number(currentDraft.retain_import_audit_logs_years.trim());
    if (!Number.isInteger(auditYears) || auditYears <= 0) {
      return t("settings.retention.validationAuditYears");
    }

    if (currentDraft.exam_file_retention_mode === "years") {
      const retentionYears = Number(currentDraft.exam_file_retention_years.trim());
      if (!Number.isInteger(retentionYears) || retentionYears <= 0) {
        return t("settings.retention.validationRetentionYears");
      }
    }

    if (!currentDraft.historical_term_data_retained_indefinitely) {
      return t("settings.retention.validationHistoricalVisibility");
    }

    return null;
  };

  const loadPolicy = async () => {
    setLoading(true);
    try {
      const response = await getRetentionPolicy();
      setPolicy(response);
      setDraft(toDraft(response));
    } catch (error) {
      toast(error instanceof Error ? error.message : t("errors.loadRetentionPolicy"), "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadPolicy();
  }, []);

  const summaryCards = useMemo(() => {
    if (!policy) return [];

    return [
      { label: t("settings.retention.summaryMode"), value: formatTranslatedValue("status", policy.exam_file_retention_mode) },
      {
        label: t("settings.retention.summaryDuration"),
        value:
          policy.exam_file_retention_mode === "years"
            ? t("settings.retention.summaryDurationYears", { count: policy.exam_file_retention_years ?? "-" })
            : t("settings.retention.summaryDurationDerived"),
      },
      {
        label: t("settings.retention.summaryVisibility"),
        value: policy.historical_term_data_retained_indefinitely
          ? t("settings.retention.summaryVisibilityRetained")
          : t("settings.retention.summaryVisibilityDisabled"),
      },
    ];
  }, [policy, t]);

  const canEditYears = draft?.exam_file_retention_mode === "years";
  const draftValidationError = draft ? getDraftValidationError(draft) : null;

  const handleSave = async () => {
    if (!draft) {
      return;
    }
    if (draftValidationError) {
      toast(draftValidationError, "error");
      return;
    }

    setSaving(true);
    try {
      const payload = toPayload(draft);
      const response = await updateRetentionPolicy(payload);
      setPolicy(response);
      setDraft(toDraft(response));
      toast(t("settings.retention.saved"), "success");
    } catch (error) {
      toast(getSaveErrorMessage(error, t("errors.saveRetentionPolicy")), "error");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <EmptyState title={t("settings.retention.loadingTitle")} description={t("settings.retention.loadingDescription")} />;
  }

  if (!policy || !draft) {
    return <EmptyState title={t("settings.retention.unavailableTitle")} description={t("settings.retention.unavailableDescription")} />;
  }

  return (
    <div style={{ display: "grid", gap: "14px" }}>
      <div className="summary-grid" style={{ display: "grid", gap: "12px" }}>
        {summaryCards.map((item) => (
          <div key={item.label} className="summary-box">
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gap: "12px" }}>
        <div className="settings-row" style={{ alignItems: "flex-start" }}>
          <SettingsField label={t("settings.retention.mode")}>
            <select
              value={draft.exam_file_retention_mode}
              onChange={(event) =>
                setDraft((current) =>
                  current
                    ? {
                        ...current,
                        exam_file_retention_mode: event.target.value as ExamFileRetentionMode,
                        exam_file_retention_years:
                          event.target.value === "years" ? current.exam_file_retention_years : "",
                      }
                    : current,
                )
              }
            >
              {retentionModeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </SettingsField>

          <SettingsField
            label={t("settings.retention.years")}
            helper={canEditYears ? t("settings.retention.yearsHelper") : t("settings.retention.yearsUnused")}
          >
            <input
              type="number"
              min={1}
              step={1}
              disabled={!canEditYears}
              value={draft.exam_file_retention_years}
              onChange={(event) =>
                setDraft((current) =>
                  current
                    ? {
                        ...current,
                        exam_file_retention_years: event.target.value,
                      }
                    : current,
                )
              }
            />
          </SettingsField>

          <SettingsField label={t("settings.retention.auditYears")} helper={t("settings.retention.auditYearsHelper")}>
            <input
              type="number"
              min={1}
              step={1}
              value={draft.retain_import_audit_logs_years}
              onChange={(event) =>
                setDraft((current) =>
                  current
                    ? {
                        ...current,
                        retain_import_audit_logs_years: event.target.value,
                      }
                    : current,
                )
              }
            />
          </SettingsField>
        </div>

        <div style={{ display: "grid", gap: "10px" }}>
          <SettingsToggle
            label={t("settings.retention.archiveFirst")}
            description={t("settings.retention.archiveFirstDescription")}
            checked={draft.exam_file_archive_before_destroy}
            onChange={(checked) =>
              setDraft((current) =>
                current
                  ? {
                      ...current,
                      exam_file_archive_before_destroy: checked,
                    }
                  : current,
              )
            }
          />

          <SettingsToggle
            label={t("settings.retention.requireApproval")}
            description={t("settings.retention.requireApprovalDescription")}
            checked={draft.exam_file_destroy_requires_approval}
            onChange={(checked) =>
              setDraft((current) =>
                current
                  ? {
                      ...current,
                      exam_file_destroy_requires_approval: checked,
                    }
                  : current,
              )
            }
          />

          <SettingsToggle
            label={t("settings.retention.retainRawFiles")}
            description={t("settings.retention.retainRawFilesDescription")}
            checked={draft.retain_import_raw_files}
            onChange={(checked) =>
              setDraft((current) =>
                current
                  ? {
                      ...current,
                      retain_import_raw_files: checked,
                    }
                  : current,
              )
            }
          />

          <SettingsToggle
            label={t("settings.retention.historicalData")}
            description={t("settings.retention.historicalDataDescription")}
            checked={draft.historical_term_data_retained_indefinitely}
            onChange={() => {}}
            disabled
            rightSlot={<Badge variant="green" size="sm">{t("settings.retention.locked")}</Badge>}
          />
        </div>
      </div>

      {draftValidationError ? (
        <div
          style={{
            padding: "12px 14px",
            borderRadius: "14px",
            border: "1px solid rgba(220, 38, 38, 0.2)",
            background: "rgba(220, 38, 38, 0.08)",
          }}
        >
          <strong>{t("settings.retention.validationTitle")}</strong>
          <p style={{ margin: 0 }}>{draftValidationError}</p>
        </div>
      ) : null}

      <div
        style={{
          padding: "14px 16px",
          borderRadius: "16px",
          border: "1px solid rgba(231, 226, 218, 0.9)",
          background: "rgba(255, 255, 255, 0.82)",
          display: "grid",
          gap: "8px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
          <strong>{t("settings.retention.policyExplanation")}</strong>
          <Badge variant={getStatusVariant(policy.exam_file_retention_mode)} size="sm">
            {formatTranslatedValue("status", policy.exam_file_retention_mode)}
          </Badge>
        </div>
        <p style={{ margin: 0 }}>{policy.plain_language.exam_file_retention_summary}</p>
        <p style={{ margin: 0 }}>{policy.plain_language.archive_summary}</p>
        <p style={{ margin: 0 }}>{policy.plain_language.destruction_summary}</p>
        <p style={{ margin: 0 }}>{policy.plain_language.historical_visibility_summary}</p>
      </div>

      <div
        style={{
          padding: "14px 16px",
          borderRadius: "16px",
          border: "1px solid rgba(37, 99, 235, 0.15)",
          background: "rgba(37, 99, 235, 0.08)",
          display: "grid",
          gap: "6px",
        }}
      >
        <strong>{t("settings.retention.safetyNotes")}</strong>
        <p style={{ margin: 0 }}>{t("settings.retention.safetyNoteOne")}</p>
        <p style={{ margin: 0 }}>{t("settings.retention.safetyNoteTwo", { value: policy.parsed_snapshot_storage })}</p>
      </div>

      <div className="inline-actions">
        <Button type="button" variant="outline" onClick={() => void loadPolicy()} disabled={saving}>
          {t("settings.retention.reload")}
        </Button>
        <Button type="button" onClick={() => void handleSave()} loading={saving} disabled={Boolean(draftValidationError)}>
          {t("settings.retention.save")}
        </Button>
      </div>
    </div>
  );
}
