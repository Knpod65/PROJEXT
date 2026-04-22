import { useMemo, useState } from "react";

import { useI18n } from "@/i18n";
import { ApiError } from "@/services/api";
import {
  confirmCheckImportV2,
  confirmImportV2,
  prepareImportV2,
  previewImportV2,
  validateImportV2,
} from "@/services/import-v2.service";
import { useAuth } from "@/store/auth.store";
import type {
  ImportV2ConfirmCheckResponse,
  ImportV2ExecuteResponse,
  ImportV2OverrideRequestItem,
  ImportV2PrepareResponse,
  ImportV2PreviewResponse,
  ImportV2Type,
  ImportV2ValidationResponse,
  ImportV2ValidationRow,
} from "@/types/api";

export interface ImportWizardRowDraft extends ImportV2ValidationRow {
  override_enabled: boolean;
  mapping_value: string;
  mapping_note: string;
}

export interface ImportWizardIssue {
  row: number;
  message: string;
}

export interface ImportWizardStepItem {
  number: number;
  key: string;
  title: string;
}

function createRowDraft(row: ImportV2ValidationRow): ImportWizardRowDraft {
  const selected = row.status === "error" ? false : row.selected;
  return {
    ...row,
    selected,
    override_reason: row.override_reason ?? "",
    override_enabled: Boolean(row.override_reason),
    mapping_value: "",
    mapping_note: "",
  };
}

function sortIssues(issues: ImportWizardIssue[]) {
  return [...issues].sort((left, right) => left.row - right.row);
}

export function useImportWizard() {
  const { t } = useI18n();
  const { user } = useAuth();
  const [step, setStep] = useState<number>(1);
  const [importType, setImportType] = useState<ImportV2Type>("opencourse");
  const [academicYear, setAcademicYear] = useState("");
  const [semester, setSemester] = useState("");
  const [examType, setExamType] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const [preview, setPreview] = useState<ImportV2PreviewResponse | null>(null);
  const [validation, setValidation] = useState<ImportV2ValidationResponse | null>(null);
  const [prepareResult, setPrepareResult] = useState<ImportV2PrepareResponse | null>(null);
  const [confirmCheck, setConfirmCheck] = useState<ImportV2ConfirmCheckResponse | null>(null);
  const [executeResult, setExecuteResult] = useState<ImportV2ExecuteResponse | null>(null);
  const [rows, setRows] = useState<ImportWizardRowDraft[]>([]);

  const [busy, setBusy] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const steps = useMemo<ImportWizardStepItem[]>(
    () => [
      { number: 1, key: "upload", title: t("import.v2.step.upload") },
      { number: 2, key: "preview", title: t("import.v2.step.preview") },
      { number: 3, key: "summary", title: t("import.v2.step.summary") },
      { number: 4, key: "rows", title: t("import.v2.step.rows") },
      { number: 5, key: "override", title: t("import.v2.step.override") },
      { number: 6, key: "confirm", title: t("import.v2.step.confirm") },
      { number: 7, key: "result", title: t("import.v2.step.result") },
    ],
    [t],
  );

  const getApiErrorMessage = (error: unknown) => {
    if (error instanceof ApiError) {
      return error.message;
    }

    return error instanceof Error ? error.message : t("errors.importWizardUnexpected");
  };

  const overrideRows = useMemo(() => rows.filter((row) => row.status === "error"), [rows]);

  const selectedRows = useMemo(
    () => rows.filter((row) => row.selected).map((row) => row._row),
    [rows],
  );

  const overrides = useMemo<ImportV2OverrideRequestItem[]>(
    () =>
      rows
        .filter(
          (row) =>
            row.selected &&
            row.status === "error" &&
            row.can_override &&
            row.override_enabled &&
            typeof row.override_reason === "string" &&
            row.override_reason.trim().length > 0,
        )
        .map((row) => ({ row: row._row, reason: String(row.override_reason).trim() })),
    [rows],
  );

  const canMoveNext = step < 7;
  const canMoveBack = step > 1 && step < 7;

  const setRowState = (rowNumber: number, updater: (row: ImportWizardRowDraft) => ImportWizardRowDraft) => {
    setRows((current) =>
      current.map((row) => {
        if (row._row !== rowNumber) {
          return row;
        }

        return updater(row);
      }),
    );
  };

  const selectRow = (rowNumber: number, selected: boolean) => {
    setRowState(rowNumber, (row) => {
      if (!selected) {
        return { ...row, selected: false };
      }

      if (row.status !== "error") {
        return { ...row, selected: true };
      }

      if (!row.can_override) {
        return row;
      }

      if (row.override_policy !== "allowed") {
        return row;
      }

      return { ...row, selected: true, override_enabled: true };
    });
  };

  const toggleOverride = (rowNumber: number, enabled: boolean) => {
    setRowState(rowNumber, (row) => {
      if (row.status !== "error" || !row.can_override || row.override_policy !== "allowed") {
        return row;
      }

      return {
        ...row,
        override_enabled: enabled,
        selected: enabled ? true : false,
      };
    });
  };

  const updateOverrideReason = (rowNumber: number, reason: string) => {
    setRowState(rowNumber, (row) => ({ ...row, override_reason: reason }));
  };

  const updateMappingValue = (rowNumber: number, value: string) => {
    setRowState(rowNumber, (row) => ({ ...row, mapping_value: value }));
  };

  const updateMappingNote = (rowNumber: number, value: string) => {
    setRowState(rowNumber, (row) => ({ ...row, mapping_note: value }));
  };

  const clearError = () => setErrorMessage(null);

  const resetWizard = () => {
    setStep(1);
    setFile(null);
    setPreview(null);
    setValidation(null);
    setPrepareResult(null);
    setConfirmCheck(null);
    setExecuteResult(null);
    setRows([]);
    setErrorMessage(null);
    setBusy(false);
  };

  const runPreview = async () => {
    if (!file) {
      throw new Error(t("import.v2.chooseFile"));
    }

    if (!academicYear.trim() || !semester.trim() || !examType.trim()) {
      throw new Error(t("import.v2.requireTermContext"));
    }

    setBusy(true);
    setErrorMessage(null);

    try {
      const response = await previewImportV2({
        file,
        academic_year: academicYear.trim(),
        semester: semester.trim(),
        exam_type: examType.trim(),
      });

      setPreview(response);
      setStep(2);
      return response;
    } catch (error) {
      const message = getApiErrorMessage(error);
      setErrorMessage(message);
      throw new Error(message);
    } finally {
      setBusy(false);
    }
  };

  const runValidate = async () => {
    if (!preview) {
      throw new Error(t("import.v2.previewFirst"));
    }

    setBusy(true);
    setErrorMessage(null);

    try {
      const response = await validateImportV2({
        file_token: preview.file_token,
        import_type: importType,
        academic_year: academicYear.trim(),
        semester: semester.trim(),
        exam_type: examType.trim(),
        selected_rows: [],
        overrides: [],
      });

      setValidation(response);
      setRows(response.rows.map(createRowDraft));
      setStep(3);
      return response;
    } catch (error) {
      const message = getApiErrorMessage(error);
      setErrorMessage(message);
      throw new Error(message);
    } finally {
      setBusy(false);
    }
  };

  const goToStep = (targetStep: number) => {
    if (targetStep < 1 || targetStep > 7) {
      return;
    }

    if (targetStep > step + 1) {
      return;
    }

    setStep(targetStep);
  };

  const runSelectionChecks = () => {
    const issues: ImportWizardIssue[] = [];

    if (selectedRows.length === 0) {
      issues.push({ row: 0, message: t("import.v2.selectOneRow") });
    }

    rows.forEach((row) => {
      if (!row.selected || row.status !== "error") {
        return;
      }

      if (row.override_policy === "requires_mapping") {
        issues.push({ row: row._row, message: t("import.v2.rowRequiresMapping") });
        return;
      }

      if (row.override_policy === "disallowed" || !row.can_override) {
        issues.push({ row: row._row, message: t("import.v2.rowDisallowed") });
        return;
      }

      if (!row.override_enabled) {
        issues.push({ row: row._row, message: t("import.v2.rowEnableOverride") });
      }

      if (!row.override_reason || row.override_reason.trim().length === 0) {
        issues.push({ row: row._row, message: t("import.v2.rowOverrideReason") });
      }
    });

    return sortIssues(issues);
  };

  const runPrepareAndConfirmCheck = async () => {
    if (!preview || !user) {
      throw new Error(t("import.v2.missingPreviewOrUser"));
    }

    const issues = runSelectionChecks();
    if (issues.length > 0) {
      const first = issues[0];
      throw new Error(first ? first.message : t("import.v2.selectionCheckFailed"));
    }

    setBusy(true);
    setErrorMessage(null);

    try {
      const prepareResponse = await prepareImportV2({
        file_token: preview.file_token,
        import_type: importType,
        academic_year: academicYear.trim(),
        semester: semester.trim(),
        exam_type: examType.trim(),
        selected_rows: selectedRows,
        overrides,
      });
      setPrepareResult(prepareResponse);

      const checkResponse = await confirmCheckImportV2({
        file_token: preview.file_token,
        import_type: importType,
        academic_year: academicYear.trim(),
        semester: semester.trim(),
        exam_type: examType.trim(),
        selected_rows: selectedRows,
        overrides,
        confirmed_by: user.id,
        dry_run: true,
      });

      setConfirmCheck(checkResponse);
      setStep(6);
      return { prepareResponse, checkResponse };
    } catch (error) {
      const message = getApiErrorMessage(error);
      setErrorMessage(message);
      throw new Error(message);
    } finally {
      setBusy(false);
    }
  };

  const runConfirm = async () => {
    if (!preview || !user) {
      throw new Error(t("import.v2.missingPreviewOrUser"));
    }

    setBusy(true);
    setErrorMessage(null);

    try {
      const response = await confirmImportV2({
        file_token: preview.file_token,
        import_type: importType,
        academic_year: academicYear.trim(),
        semester: semester.trim(),
        exam_type: examType.trim(),
        selected_rows: selectedRows,
        overrides,
        confirmed_by: user.id,
        dry_run: false,
      });

      setExecuteResult(response);
      setStep(7);
      return response;
    } catch (error) {
      const message = getApiErrorMessage(error);
      setErrorMessage(message);
      throw new Error(message);
    } finally {
      setBusy(false);
    }
  };

  const statusCounts = useMemo(
    () => ({
      total: rows.length,
      valid: rows.filter((row) => row.status === "valid").length,
      warning: rows.filter((row) => row.status === "warning").length,
      error: rows.filter((row) => row.status === "error").length,
    }),
    [rows],
  );

  const overrideCounts = useMemo(
    () => ({
      selected: selectedRows.length,
      overridden: overrides.length,
      requiresMapping: rows.filter((row) => row.override_policy === "requires_mapping").length,
    }),
    [overrides.length, rows, selectedRows.length],
  );

  return {
    steps,
    step,
    setStep,
    goToStep,
    canMoveNext,
    canMoveBack,
    busy,
    errorMessage,
    clearError,
    resetWizard,

    importType,
    setImportType,
    academicYear,
    setAcademicYear,
    semester,
    setSemester,
    examType,
    setExamType,
    file,
    setFile,

    preview,
    validation,
    prepareResult,
    confirmCheck,
    executeResult,
    rows,
    overrideRows,
    selectedRows,
    overrides,
    statusCounts,
    overrideCounts,

    selectRow,
    toggleOverride,
    updateOverrideReason,
    updateMappingValue,
    updateMappingNote,

    runPreview,
    runValidate,
    runSelectionChecks,
    runPrepareAndConfirmCheck,
    runConfirm,
  };
}
