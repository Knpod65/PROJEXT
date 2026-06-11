import type React from "react";
import { useCallback, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { FormField } from "@/components/ui/FormField";
import { Icon } from "@/components/ui/Icon";
import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton } from "@/components/ui/Skeleton";
import { createPeriod, activatePeriod, listPeriods } from "@/services/period.service";
import { useAsyncData } from "@/hooks/useAsyncData";
import { useI18n } from "@/i18n";
import { useUi } from "@/store/ui.store";

export function PeriodPage() {
  const { t } = useI18n();
  const { toast } = useUi();
  const loader = useCallback(() => listPeriods(), []);
  const state = useAsyncData(loader, [loader]);
  const [form, setForm] = useState({
    academic_year: "2568",
    semester: "2",
    exam_type: "final",
    label: "",
  });

  const handleCreate = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      await createPeriod(form);
      toast(t("legacy.period.toast.created"), "success");
      await state.reload();
    } catch (err) {
      toast(err instanceof Error ? err.message : t("legacy.period.toast.createFailed"), "error");
    }
  };

  const handleActivate = async (periodId: number) => {
    try {
      await activatePeriod(periodId);
      toast(t("legacy.period.toast.activated"), "success");
      await state.reload();
    } catch (err) {
      toast(err instanceof Error ? err.message : t("legacy.period.toast.activateFailed"), "error");
    }
  };

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        eyebrow={t("legacy.period.eyebrow")}
        title={t("legacy.period.title")}
        description={t("legacy.period.description")}
      />

      <Card title={t("legacy.period.createTitle")} subtitle={t("legacy.period.createSubtitle")}>
        <form className="inline-form" onSubmit={handleCreate}>
          <FormField label={t("legacy.period.academicYear")}>
            <input onChange={(event) => setForm((current) => ({ ...current, academic_year: event.target.value }))} value={form.academic_year} />
          </FormField>
          <FormField label={t("legacy.period.semester")}>
            <select onChange={(event) => setForm((current) => ({ ...current, semester: event.target.value }))} value={form.semester}>
              <option value="1">{t("legacy.period.semesterOne")}</option>
              <option value="2">{t("legacy.period.semesterTwo")}</option>
              <option value="summer">{t("legacy.period.semesterSummer")}</option>
            </select>
          </FormField>
          <FormField label={t("legacy.period.examType")}>
            <select onChange={(event) => setForm((current) => ({ ...current, exam_type: event.target.value }))} value={form.exam_type}>
              <option value="midterm">{t("legacy.period.midterm")}</option>
              <option value="final">{t("legacy.period.final")}</option>
            </select>
          </FormField>
          <FormField label={t("legacy.period.label")}>
            <input onChange={(event) => setForm((current) => ({ ...current, label: event.target.value }))} placeholder={t("legacy.period.labelPlaceholder")} value={form.label} />
          </FormField>
          <Button type="submit">{t("legacy.period.actions.create")}</Button>
        </form>
      </Card>

      {state.loading ? (
        <div className="page-stack">{[0, 1].map((item) => <Skeleton key={item} className="dashboard-skeleton" />)}</div>
      ) : state.error ? (
        <EmptyState icon={<Icon name="error" />} title={t("legacy.period.errorTitle")} description={state.error} />
      ) : (state.data ?? []).length === 0 ? (
        <EmptyState icon={<Icon name="event" />} title={t("legacy.period.emptyTitle")} description={t("legacy.period.emptyDescription")} />
      ) : (
        <div className="page-stack">
          {(state.data ?? []).map((period) => (
          <Card
            key={period.id}
            title={period.label}
            subtitle={`${t(`legacy.period.type.${period.exam_type}`)} · ${period.semester}/${period.academic_year}`}
            actions={<Badge variant={period.is_active ? "green" : "gray"}>{period.is_active ? t("status.active") : t("status.archived")}</Badge>}
          >
            {!period.is_active ? (
              <Button type="button" variant="outline" onClick={() => void handleActivate(period.id)}>
                {t("legacy.period.actions.activate")}
              </Button>
            ) : null}
          </Card>
        ))}
        </div>
      )}
    </div>
  );
}
