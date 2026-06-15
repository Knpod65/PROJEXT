import { useEffect, useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { AlertBanner } from "@/components/ui/AlertBanner";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { FormField } from "@/components/ui/FormField";
import { Icon } from "@/components/ui/Icon";
import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton } from "@/components/ui/Skeleton";
import { StatusChip } from "@/components/ui/StatusChip";
import {
  invigilationSimpleRatesQueryKey,
  useInvigilationSimpleRates,
} from "@/hooks/domain/useInvigilationSimpleRates";
import { useI18n } from "@/i18n";
import { saveSimpleInvigilationRates } from "@/services/invigilationSimpleRates.service";
import { useAuth } from "@/store/auth.store";
import { useUi } from "@/store/ui.store";
import { formatDateTime } from "@/utils/format";

interface RateForm {
  weekdayAmount: string;
  weekendAmount: string;
}

interface RateErrors {
  weekdayAmount?: string;
  weekendAmount?: string;
}

const EMPTY_FORM: RateForm = {
  weekdayAmount: "",
  weekendAmount: "",
};

function amountToInput(value: number | string | null) {
  return value === null ? "" : String(value);
}

export default function InvigilationRateRules() {
  const { t } = useI18n();
  const { activeRole } = useAuth();
  const { toast } = useUi();
  const queryClient = useQueryClient();
  const { data, isError, isLoading } = useInvigilationSimpleRates();
  const [form, setForm] = useState<RateForm>(EMPTY_FORM);
  const [errors, setErrors] = useState<RateErrors>({});
  const [isSaving, setIsSaving] = useState(false);

  const isAdmin = activeRole === "admin";

  const serverForm = useMemo<RateForm>(() => ({
    weekdayAmount: amountToInput(data?.weekday_rate.amount ?? null),
    weekendAmount: amountToInput(data?.weekend_rate.amount ?? null),
  }), [data]);

  useEffect(() => {
    setForm(serverForm);
    setErrors({});
  }, [serverForm]);

  const latestSavedAt = useMemo(() => {
    const values = [data?.weekday_rate.saved_at, data?.weekend_rate.saved_at].filter(
      (value): value is string => Boolean(value),
    );
    const sortedValues = values.sort();
    return sortedValues.length > 0 ? sortedValues[sortedValues.length - 1] : null;
  }, [data]);

  const validateAmount = (value: string) => {
    if (!value.trim()) return t("rateRules.simple.validation.required");
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) return t("rateRules.simple.validation.numeric");
    if (parsed <= 0) return t("rateRules.simple.validation.positive");
    return null;
  };

  const validateForm = () => {
    const nextErrors: RateErrors = {};
    const weekdayError = validateAmount(form.weekdayAmount);
    const weekendError = validateAmount(form.weekendAmount);
    if (weekdayError) nextErrors.weekdayAmount = weekdayError;
    if (weekendError) nextErrors.weekendAmount = weekendError;
    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleReset = () => {
    setForm(serverForm);
    setErrors({});
  };

  const handleSave = async () => {
    if (!isAdmin) {
      toast(t("rateRules.simple.toast.adminOnly"), "warning");
      return;
    }
    if (!validateForm()) {
      toast(t("rateRules.simple.toast.invalid"), "error");
      return;
    }

    setIsSaving(true);
    try {
      const saved = await saveSimpleInvigilationRates({
        weekday_amount: Number(form.weekdayAmount),
        weekend_amount: Number(form.weekendAmount),
      });
      queryClient.setQueryData(invigilationSimpleRatesQueryKey, saved);
      setForm({
        weekdayAmount: amountToInput(saved.weekday_rate.amount),
        weekendAmount: amountToInput(saved.weekend_rate.amount),
      });
      setErrors({});
      toast(t("rateRules.simple.toast.saved"), "success");
    } catch (error) {
      toast(error instanceof Error ? error.message : t("rateRules.simple.toast.saveFailed"), "error");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="page-stack page-stack--spacious">
        <Skeleton className="dashboard-chart-skeleton" />
        <Skeleton className="dashboard-chart-skeleton" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="page-stack page-stack--spacious">
        <EmptyState
          icon={<Icon name="warning" />}
          title={t("rateRules.simple.loadErrorTitle")}
          description={t("rateRules.simple.loadErrorDescription")}
        />
      </div>
    );
  }

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        className="page-hero--dashboard"
        eyebrow={t("rateRules.simple.eyebrow")}
        title={t("rateRules.simple.title")}
        description={t("rateRules.simple.description")}
        status={
          <>
            <StatusChip tone="draft">{t("rateRules.simple.previewOnly")}</StatusChip>
            {!isAdmin ? <StatusChip tone="readOnly">{t("rateRules.simple.readOnly")}</StatusChip> : null}
          </>
        }
      />

      <AlertBanner
        variant="warning"
        title={t("rateRules.simple.warningTitle")}
        action={<StatusChip tone="blocked">{t("rateRules.simple.noAuthorization")}</StatusChip>}
      >
        {t("rateRules.simple.warningBody")}
      </AlertBanner>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card
          title={t("rateRules.simple.weekdayTitle")}
          subtitle={t("rateRules.simple.weekdayDescription")}
          actions={
            <Badge variant={data.weekday_rate.amount_status === "CONFIGURED" ? "green" : "gold"}>
              {t(`rateRules.simple.status.${data.weekday_rate.amount_status}`)}
            </Badge>
          }
        >
          <FormField label={t("rateRules.simple.amountLabel")}>
            <input
              aria-describedby={errors.weekdayAmount ? "weekday-rate-error" : "weekday-rate-helper"}
              aria-invalid={Boolean(errors.weekdayAmount)}
              inputMode="decimal"
              min="0"
              readOnly={!isAdmin}
              step="0.01"
              type="number"
              value={form.weekdayAmount}
              onChange={(event) => {
                setForm((current) => ({ ...current, weekdayAmount: event.target.value }));
                setErrors((current) => ({ ...current, weekdayAmount: undefined }));
              }}
            />
            <small className="form-hint" id="weekday-rate-helper">
              {t("rateRules.simple.bahtPerSession")} · THB · PER_SESSION
            </small>
            {errors.weekdayAmount ? <p className="form-error" id="weekday-rate-error">{errors.weekdayAmount}</p> : null}
          </FormField>
        </Card>

        <Card
          title={t("rateRules.simple.weekendTitle")}
          subtitle={t("rateRules.simple.weekendDescription")}
          actions={
            <Badge variant={data.weekend_rate.amount_status === "CONFIGURED" ? "green" : "gold"}>
              {t(`rateRules.simple.status.${data.weekend_rate.amount_status}`)}
            </Badge>
          }
        >
          <FormField label={t("rateRules.simple.amountLabel")}>
            <input
              aria-describedby={errors.weekendAmount ? "weekend-rate-error" : "weekend-rate-helper"}
              aria-invalid={Boolean(errors.weekendAmount)}
              inputMode="decimal"
              min="0"
              readOnly={!isAdmin}
              step="0.01"
              type="number"
              value={form.weekendAmount}
              onChange={(event) => {
                setForm((current) => ({ ...current, weekendAmount: event.target.value }));
                setErrors((current) => ({ ...current, weekendAmount: undefined }));
              }}
            />
            <small className="form-hint" id="weekend-rate-helper">
              {t("rateRules.simple.bahtPerSession")} · THB · PER_SESSION
            </small>
            {errors.weekendAmount ? <p className="form-error" id="weekend-rate-error">{errors.weekendAmount}</p> : null}
          </FormField>
        </Card>
      </div>

      <Card
        title={t("rateRules.simple.configurationTitle")}
        subtitle={isAdmin ? t("rateRules.simple.adminHint") : t("rateRules.simple.staffHint")}
        actions={
          <Badge variant={data.configuration_status === "CONFIGURED" ? "green" : "gold"}>
            {t(`rateRules.simple.configuration.${data.configuration_status}`)}
          </Badge>
        }
      >
        <div className="summary-box">
          <span>{t("rateRules.simple.latestSaved")}</span>
          <strong>{latestSavedAt ? formatDateTime(latestSavedAt) : t("rateRules.simple.notSaved")}</strong>
        </div>
        {isAdmin ? (
          <div className="mt-4 flex flex-wrap gap-2">
            <Button type="button" loading={isSaving} onClick={() => void handleSave()}>
              {t("rateRules.simple.save")}
            </Button>
            <Button type="button" variant="outline" disabled={isSaving} onClick={handleReset}>
              {t("rateRules.simple.reset")}
            </Button>
          </div>
        ) : null}
      </Card>
    </div>
  );
}
