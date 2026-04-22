import { useEffect, useMemo } from "react";

import { ImportConfirmPanel } from "@/components/import/ImportConfirmPanel";
import { ImportOverridePanel } from "@/components/import/ImportOverridePanel";
import { ImportResultSummary } from "@/components/import/ImportResultSummary";
import { ImportRowReviewTable } from "@/components/import/ImportRowReviewTable";
import { ImportValidationSummary } from "@/components/import/ImportValidationSummary";
import { ImportWizardSteps } from "@/components/import/ImportWizardSteps";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { useImportWizard } from "@/hooks/useImportWizard";
import { useI18n } from "@/i18n";
import { usePeriod } from "@/store/period.store";
import { useUi } from "@/store/ui.store";
import type { ImportV2Type } from "@/types/api";

function formatValue(value: unknown, fallback: string) {
  if (value === null || value === undefined || value === "") return fallback;
  if (typeof value === "object") {
    try {
      return JSON.stringify(value);
    } catch {
      return String(value);
    }
  }
  return String(value);
}

export function ImportV2Page() {
  const { t } = useI18n();
  const { toast } = useUi();
  const { activePeriod } = usePeriod();
  const wizard = useImportWizard();

  const importTypeOptions: Array<{ value: ImportV2Type; label: string; description: string }> = [
    { value: "opencourse", label: t("import.v2.type.opencourse.label"), description: t("import.v2.type.opencourse.description") },
    { value: "enrollment", label: t("import.v2.type.enrollment.label"), description: t("import.v2.type.enrollment.description") },
    { value: "personnel", label: t("import.v2.type.personnel.label"), description: t("import.v2.type.personnel.description") },
    { value: "employee", label: t("import.v2.type.employee.label"), description: t("import.v2.type.employee.description") },
    { value: "room_capacity", label: t("import.v2.type.room_capacity.label"), description: t("import.v2.type.room_capacity.description") },
  ];

  useEffect(() => {
    if (activePeriod && wizard.step === 1) {
      if (activePeriod.academic_year) wizard.setAcademicYear(activePeriod.academic_year);
      if (activePeriod.semester) wizard.setSemester(activePeriod.semester);
      if (activePeriod.exam_type) wizard.setExamType(activePeriod.exam_type);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activePeriod]);

  const previewColumns = useMemo(() => {
    const first = wizard.preview?.sample_rows[0];
    return first ? Object.keys(first) : [];
  }, [wizard.preview]);

  const selectionIssues = wizard.runSelectionChecks();

  const selectedType = importTypeOptions.find((option) => option.value === wizard.importType);

  const handlePrimaryAction = async () => {
    try {
      if (wizard.step === 1) { await wizard.runPreview(); toast(t("import.v2.uploaded"), "success"); return; }
      if (wizard.step === 2) { await wizard.runValidate(); toast(t("import.v2.validationComplete"), "success"); return; }
      if (wizard.step === 3) { wizard.goToStep(4); return; }
      if (wizard.step === 4) { wizard.goToStep(5); return; }
      if (wizard.step === 5) { await wizard.runPrepareAndConfirmCheck(); toast(t("import.v2.precheckPassed"), "success"); return; }
      if (wizard.step === 6) { await wizard.runConfirm(); toast(t("import.v2.committed"), "success"); }
    } catch (error) {
      toast(error instanceof Error ? error.message : t("import.v2.stepFailed"), "error");
    }
  };

  const primaryLabel =
    wizard.step === 1 ? t("import.v2.primary.upload")
    : wizard.step === 2 ? t("import.v2.primary.validate")
    : wizard.step === 3 ? t("import.v2.primary.reviewRows")
    : wizard.step === 4 ? t("import.v2.primary.applyOverrides")
    : wizard.step === 5 ? t("import.v2.primary.prepare")
    : wizard.step === 6 ? t("import.v2.primary.commit")
    : t("import.v2.primary.done");

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">{t("import.v2.heroEyebrow")}</span>
          <h1 className="page-hero__title">{t("import.v2.heroTitle")}</h1>
          <p className="page-hero__description">{t("import.v2.heroDescription")}</p>
        </div>
        <div className="page-hero__actions">
          {wizard.step > 1 && (
            <Button type="button" variant="outline" onClick={wizard.resetWizard}>
              {t("import.v2.startOver")}
            </Button>
          )}
        </div>
      </section>

      <Card title={t("import.v2.progressTitle")} subtitle={t("import.v2.progressSubtitle", { step: wizard.step })}>
        <ImportWizardSteps currentStep={wizard.step} steps={wizard.steps} />
      </Card>

      {wizard.errorMessage && (
        <Card title={t("import.v2.issueDetected")}>
          <div className="import-error-banner">
            <Icon name="warning" />
            <p>{wizard.errorMessage}</p>
          </div>
          <Button type="button" variant="ghost" size="sm" onClick={wizard.clearError}>
            {t("common.dismiss")}
          </Button>
        </Card>
      )}

      {wizard.step === 1 && (
        <Card title={t("import.v2.step1.title")} subtitle={t("import.v2.step1.subtitle")}>
          {activePeriod && (
            <div className="import-period-hint">
              <Icon name="info" />
              <span>{t("import.v2.activePeriod", { label: activePeriod.label })}</span>
            </div>
          )}

          <div className="import-upload-grid">
            <div className="form-field">
              <label htmlFor="imp-type">{t("import.v2.importType")}</label>
              <select
                id="imp-type"
                value={wizard.importType}
                onChange={(e) => wizard.setImportType(e.currentTarget.value as ImportV2Type)}
              >
                {importTypeOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
              {selectedType && <span className="form-hint">{selectedType.description}</span>}
            </div>

            <div className="form-field">
              <label htmlFor="imp-ay">{t("import.v2.academicYear")}</label>
              <input
                id="imp-ay"
                type="text"
                value={wizard.academicYear}
                placeholder={t("import.v2.academicYearPlaceholder")}
                onChange={(e) => wizard.setAcademicYear(e.currentTarget.value)}
              />
            </div>

            <div className="form-field">
              <label htmlFor="imp-sem">{t("import.v2.semester")}</label>
              <select
                id="imp-sem"
                value={wizard.semester}
                onChange={(e) => wizard.setSemester(e.currentTarget.value)}
              >
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="summer">{t("import.v2.semesterSummer")}</option>
              </select>
            </div>

            <div className="form-field">
              <label htmlFor="imp-exam">{t("import.v2.examType")}</label>
              <select
                id="imp-exam"
                value={wizard.examType}
                onChange={(e) => wizard.setExamType(e.currentTarget.value)}
              >
                <option value="midterm">{t("import.v2.examTypeMidterm")}</option>
                <option value="final">{t("import.v2.examTypeFinal")}</option>
              </select>
            </div>

            <div className="form-field form-field--full">
              <label htmlFor="imp-file">{t("import.v2.file")}</label>
              <input
                id="imp-file"
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={(e) => wizard.setFile(e.currentTarget.files?.[0] ?? null)}
              />
              <span className="form-hint">{t("import.v2.fileHint")}</span>
            </div>
          </div>
        </Card>
      )}

      {wizard.step === 2 && (
        <Card
          title={t("import.v2.step2.title")}
          subtitle={wizard.preview ? t("import.v2.step2.subtitle", { rows: wizard.preview.total_rows, file: wizard.preview.file_name }) : ""}
        >
          {!wizard.preview ? (
            <EmptyState title={t("import.v2.noPreviewTitle")} description={t("import.v2.noPreviewDescription")} />
          ) : (
            <div className="page-stack">
              <div className="import-summary-grid">
                <article className="import-summary-card">
                  <span>{t("import.v2.fileLabel")}</span>
                  <strong>{wizard.preview.file_name}</strong>
                </article>
                <article className="import-summary-card">
                  <span>{t("import.v2.totalRows")}</span>
                  <strong>{wizard.preview.total_rows}</strong>
                </article>
                <article className="import-summary-card">
                  <span>{t("import.v2.columns")}</span>
                  <strong>{previewColumns.length}</strong>
                </article>
              </div>

              <p className="text-muted">{t("import.v2.previewHint", { count: wizard.preview.sample_rows.length })}</p>
              <div className="table-wrap">
                <table className="data-table">
                  <thead>
                    <tr>{previewColumns.map((col) => <th key={col}>{col}</th>)}</tr>
                  </thead>
                  <tbody>
                    {wizard.preview.sample_rows.map((row, i) => (
                      <tr key={`r-${i}`}>
                        {previewColumns.map((col) => <td key={col}>{formatValue(row[col], t("common.notAvailable"))}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </Card>
      )}

      {wizard.step === 3 && wizard.validation && (
        <Card
          title={t("import.v2.step3.title")}
          subtitle={t("import.v2.step3.subtitle")}
        >
          <ImportValidationSummary
            totalRows={wizard.validation.total_rows}
            validCount={wizard.validation.valid_count}
            warningCount={wizard.validation.warning_count}
            errorCount={wizard.validation.error_count}
            errorSummary={wizard.validation.error_summary}
            warningSummary={wizard.validation.warning_summary}
          />
        </Card>
      )}

      {wizard.step === 4 && (
        <Card
          title={t("import.v2.step4.title")}
          subtitle={t("import.v2.step4.subtitle")}
        >
          <ImportRowReviewTable
            rows={wizard.rows}
            onSelectRow={wizard.selectRow}
            onToggleOverride={wizard.toggleOverride}
            onUpdateOverrideReason={wizard.updateOverrideReason}
            onUpdateMappingValue={wizard.updateMappingValue}
            onUpdateMappingNote={wizard.updateMappingNote}
          />
        </Card>
      )}

      {wizard.step === 5 && (
        <Card
          title={t("import.v2.step5.title")}
          subtitle={t("import.v2.step5.subtitle")}
        >
          <ImportOverridePanel rows={wizard.overrideRows} issues={selectionIssues} />
        </Card>
      )}

      {wizard.step === 6 && (
        <Card
          title={t("import.v2.step6.title")}
          subtitle={t("import.v2.step6.subtitle")}
        >
          <ImportConfirmPanel prepareResult={wizard.prepareResult} confirmCheck={wizard.confirmCheck} />
        </Card>
      )}

      {wizard.step === 7 && wizard.executeResult && (
        <Card title={t("import.v2.step7.title")} subtitle={t("import.v2.step7.subtitle")}>
          <ImportResultSummary result={wizard.executeResult} />
        </Card>
      )}

      <Card title={t("import.v2.actionsTitle")}>
        <div className="inline-actions">
          <Button
            type="button"
            variant="outline"
            disabled={!wizard.canMoveBack || wizard.busy}
            onClick={() => wizard.goToStep(wizard.step - 1)}
          >
            {t("common.back")}
          </Button>
          <Button
            type="button"
            disabled={!wizard.canMoveNext || wizard.busy || wizard.step === 7}
            loading={wizard.busy}
            onClick={() => void handlePrimaryAction()}
          >
            {primaryLabel}
          </Button>
        </div>
      </Card>
    </div>
  );
}
