import { useEffect, useMemo, useState } from "react";

import { AlertBanner } from "@/components/ui/AlertBanner";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { FormField } from "@/components/ui/FormField";
import { Icon } from "@/components/ui/Icon";
import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton } from "@/components/ui/Skeleton";
import { usePaymentDocumentSettings } from "@/hooks/domain/usePaymentDocumentSettings";
import { useI18n } from "@/i18n";
import { useAuth } from "@/store/auth.store";
import { useUi } from "@/store/ui.store";
import type { PaymentDocumentSettingsStatus } from "@/types/paymentDocumentSettings";
import { formatDateTime } from "@/utils/format";
import {
  canManagePaymentDocumentSettings,
  canViewPaymentDocumentSettings,
} from "@/utils/permissions";

interface SettingsForm {
  term: string;
  weekdayRate: string;
  weekendRate: string;
  responsibleGroup: string;
  responsiblePerson: string;
  status: Exclude<PaymentDocumentSettingsStatus, "ARCHIVED">;
  note: string;
}

interface SettingsErrors {
  weekdayRate?: string;
  weekendRate?: string;
  responsibleGroup?: string;
}

const DEFAULT_FORM: SettingsForm = {
  term: "2/2568",
  weekdayRate: "",
  weekendRate: "",
  responsibleGroup: "Education_Student_Quality",
  responsiblePerson: "",
  status: "DRAFT_CONFIG",
  note: "",
};

function amountToInput(value: number | string | null | undefined) {
  return value === null || value === undefined ? "" : String(value);
}

function statusVariant(status: string, configured: boolean) {
  if (!configured) return "gold";
  if (status === "ACTIVE_FOR_DRAFT_PREVIEW") return "green";
  return "blue";
}

export default function PaymentDocumentSettings() {
  const { t } = useI18n();
  const { user } = useAuth();
  const { toast } = useUi();
  const [form, setForm] = useState<SettingsForm>(DEFAULT_FORM);
  const [errors, setErrors] = useState<SettingsErrors>({});
  const term = form.term.trim();
  const settings = usePaymentDocumentSettings(term);
  const canView = canViewPaymentDocumentSettings(user);
  const canEdit = canManagePaymentDocumentSettings(user);

  const serverForm = useMemo<SettingsForm>(() => ({
    term: settings.data?.term ?? (term || DEFAULT_FORM.term),
    weekdayRate: amountToInput(settings.data?.weekday_rate),
    weekendRate: amountToInput(settings.data?.weekend_rate),
    responsibleGroup: settings.data?.paper_distribution_responsible_group ?? DEFAULT_FORM.responsibleGroup,
    responsiblePerson: settings.data?.paper_distribution_responsible_person ?? "",
    status: settings.data?.status === "ACTIVE_FOR_DRAFT_PREVIEW" ? "ACTIVE_FOR_DRAFT_PREVIEW" : "DRAFT_CONFIG",
    note: settings.data?.note ?? "",
  }), [settings.data, term]);

  useEffect(() => {
    if (settings.data) {
      setForm(serverForm);
      setErrors({});
    }
  }, [serverForm, settings.data]);

  const configured = settings.data?.configuration_status === "CONFIGURED";
  const readOnly = !canEdit;
  const displayStatus = configured ? form.status : "PENDING_CONFIGURATION";
  const statusLabel = (status: string) => t(`paymentDraft.status.${status}`);

  const validateAmount = (value: string) => {
    if (!value.trim()) return t("paymentSettings.validation.required");
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) return t("paymentSettings.validation.numeric");
    if (parsed <= 0) return t("paymentSettings.validation.positive");
    return null;
  };

  const validateForm = () => {
    const nextErrors: SettingsErrors = {};
    const weekdayError = validateAmount(form.weekdayRate);
    const weekendError = validateAmount(form.weekendRate);
    if (weekdayError) nextErrors.weekdayRate = weekdayError;
    if (weekendError) nextErrors.weekendRate = weekendError;
    if (!form.responsibleGroup.trim()) {
      nextErrors.responsibleGroup = t("paymentSettings.validation.groupRequired");
    }
    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleReset = () => {
    setForm(serverForm);
    setErrors({});
  };

  const handleSave = async () => {
    if (!canEdit) {
      toast(t("paymentSettings.toast.readOnly"), "warning");
      return;
    }
    if (!validateForm()) {
      toast(t("paymentSettings.toast.invalid"), "error");
      return;
    }

    try {
      const saved = await settings.save({
        term,
        weekday_rate: Number(form.weekdayRate),
        weekend_rate: Number(form.weekendRate),
        currency: "THB",
        payment_unit: "PER_PERSON_SESSION",
        paper_distribution_responsible_group: form.responsibleGroup.trim(),
        paper_distribution_responsible_person: form.responsiblePerson.trim() || null,
        status: form.status,
        effective_from: null,
        effective_to: null,
        note: form.note.trim() || null,
      });
      setForm({
        term: saved.term,
        weekdayRate: amountToInput(saved.weekday_rate),
        weekendRate: amountToInput(saved.weekend_rate),
        responsibleGroup: saved.paper_distribution_responsible_group,
        responsiblePerson: saved.paper_distribution_responsible_person ?? "",
        status: saved.status === "ACTIVE_FOR_DRAFT_PREVIEW" ? "ACTIVE_FOR_DRAFT_PREVIEW" : "DRAFT_CONFIG",
        note: saved.note ?? "",
      });
      toast(t("paymentSettings.toast.saved"), "success");
    } catch (error) {
      toast(error instanceof Error ? error.message : t("paymentSettings.toast.saveFailed"), "error");
    }
  };

  if (!canView) {
    return (
      <div className="page-stack page-stack--spacious">
        <EmptyState icon={<Icon name="shield" />} title={t("app.unauthorized.title")} />
      </div>
    );
  }

  if (settings.isLoading && !settings.data) {
    return (
      <div className="page-stack page-stack--spacious">
        <Skeleton className="dashboard-chart-skeleton" />
        <Skeleton className="dashboard-chart-skeleton" />
      </div>
    );
  }

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        className="page-hero--dashboard"
        eyebrow={t("paymentSettings.eyebrow")}
        title={t("paymentSettings.title")}
        description={t("paymentSettings.description")}
        status={
          <>
            <Badge variant={statusVariant(form.status, configured)}>{statusLabel(displayStatus)}</Badge>
            {readOnly ? <Badge variant="blue">{t("paymentSettings.readOnly")}</Badge> : null}
          </>
        }
      />

      <AlertBanner
        variant="warning"
        title={t("paymentSettings.warning.title")}
        action={<Badge variant="gold">{t("paymentSettings.noAuthorization")}</Badge>}
      >
        {t("paymentSettings.warning.body")}
      </AlertBanner>

      {settings.isError ? (
        <AlertBanner variant="danger" title={t("paymentSettings.loadErrorTitle")}>
          {t("paymentSettings.loadErrorBody")}
        </AlertBanner>
      ) : null}

      <Card title={t("paymentSettings.rateSection.title")} subtitle={t("paymentSettings.rateSection.subtitle")}>
        <div className="form-grid">
          <FormField label={t("paymentSettings.term")}>
            <input
              value={form.term}
              onChange={(event) => setForm((current) => ({ ...current, term: event.target.value }))}
              placeholder="2/2568"
            />
          </FormField>
          <FormField
            label={t("paymentSettings.weekdayRate")}
            helper={t("paymentSettings.unit")}
            error={errors.weekdayRate}
          >
            <input
              aria-invalid={Boolean(errors.weekdayRate)}
              inputMode="decimal"
              min="0"
              readOnly={readOnly}
              step="0.01"
              type="number"
              value={form.weekdayRate}
              onChange={(event) => {
                setForm((current) => ({ ...current, weekdayRate: event.target.value }));
                setErrors((current) => ({ ...current, weekdayRate: undefined }));
              }}
            />
          </FormField>
          <FormField
            label={t("paymentSettings.weekendRate")}
            helper={t("paymentSettings.unit")}
            error={errors.weekendRate}
          >
            <input
              aria-invalid={Boolean(errors.weekendRate)}
              inputMode="decimal"
              min="0"
              readOnly={readOnly}
              step="0.01"
              type="number"
              value={form.weekendRate}
              onChange={(event) => {
                setForm((current) => ({ ...current, weekendRate: event.target.value }));
                setErrors((current) => ({ ...current, weekendRate: undefined }));
              }}
            />
          </FormField>
          <FormField label={t("paymentSettings.status")}>
            <select
              disabled={readOnly}
              value={form.status}
              onChange={(event) => setForm((current) => ({ ...current, status: event.target.value as SettingsForm["status"] }))}
            >
              <option value="DRAFT_CONFIG">{statusLabel("DRAFT_CONFIG")}</option>
              <option value="ACTIVE_FOR_DRAFT_PREVIEW">{statusLabel("ACTIVE_FOR_DRAFT_PREVIEW")}</option>
            </select>
          </FormField>
        </div>
      </Card>

      <Card title={t("paymentSettings.paperSection.title")} subtitle={t("paymentSettings.paperSection.subtitle")}>
        <div className="form-grid">
          <FormField
            label={t("paymentSettings.responsibleGroup")}
            helper={t("paymentSettings.groupHint")}
            error={errors.responsibleGroup}
          >
            <input
              aria-invalid={Boolean(errors.responsibleGroup)}
              readOnly={readOnly}
              value={form.responsibleGroup}
              onChange={(event) => {
                setForm((current) => ({ ...current, responsibleGroup: event.target.value }));
                setErrors((current) => ({ ...current, responsibleGroup: undefined }));
              }}
            />
          </FormField>
          <FormField label={t("paymentSettings.responsiblePerson")}>
            <input
              readOnly={readOnly}
              value={form.responsiblePerson}
              onChange={(event) => setForm((current) => ({ ...current, responsiblePerson: event.target.value }))}
              placeholder={t("paymentSettings.optional")}
            />
          </FormField>
        </div>
        <FormField label={t("paymentSettings.note")}>
          <textarea
            readOnly={readOnly}
            rows={4}
            value={form.note}
            onChange={(event) => setForm((current) => ({ ...current, note: event.target.value }))}
            placeholder={t("paymentSettings.notePlaceholder")}
          />
        </FormField>
      </Card>

      <Card
        title={t("paymentSettings.audit.title")}
        subtitle={settings.data?.updated_at ? formatDateTime(settings.data.updated_at) : t("paymentSettings.audit.notSaved")}
        actions={<Badge variant="gold">{t("paymentSettings.audit.draftOnly")}</Badge>}
      >
        <div className="summary-box">
          <span>{t("paymentSettings.audit.updatedBy")}</span>
          <strong>{settings.data?.updated_by ?? t("paymentSettings.audit.noUpdater")}</strong>
        </div>
        {canEdit ? (
          <div className="mt-4 flex flex-wrap gap-2">
            <Button type="button" iconLeft={<Icon name="save" />} loading={settings.isSaving} onClick={() => void handleSave()}>
              {t("paymentSettings.save")}
            </Button>
            <Button type="button" variant="outline" disabled={settings.isSaving} onClick={handleReset}>
              {t("common.reset")}
            </Button>
          </div>
        ) : (
          <p className="mt-4 text-sm text-gray-500">{t("paymentSettings.readOnlyBody")}</p>
        )}
      </Card>
    </div>
  );
}
