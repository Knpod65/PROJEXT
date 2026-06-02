import { useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, type DataTableColumn } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Skeleton } from "@/components/ui/Skeleton";
import { invigilationRateRulesQueryKey, useInvigilationRateRules } from "@/hooks/domain/useInvigilationRateRules";
import { useI18n } from "@/i18n";
import {
  activateInvigilationRateRule,
  archiveInvigilationRateRule,
  createInvigilationRateRule,
  updateInvigilationRateRule,
} from "@/services/invigilationRateRules.service";
import { useAuth } from "@/store/auth.store";
import { useUi } from "@/store/ui.store";
import type { InvigilationRateRule, InvigilationRateRulePayload } from "@/types/invigilationRateRules";

interface FormState {
  rate_name: string;
  payment_unit: "PER_SESSION";
  rate_amount: string;
  currency: string;
  role_scope: string;
  person_type_scope: string;
  effective_from: string;
  effective_to: string;
  note: string;
}

const EMPTY_FORM: FormState = {
  rate_name: "",
  payment_unit: "PER_SESSION",
  rate_amount: "",
  currency: "THB",
  role_scope: "ALL",
  person_type_scope: "ALL",
  effective_from: "",
  effective_to: "",
  note: "",
};

function statusVariant(status: string) {
  if (status === "ACTIVE") return "green";
  if (status === "DRAFT") return "gold";
  if (status === "ARCHIVED") return "gray";
  return "blue";
}

function toForm(rule: InvigilationRateRule): FormState {
  return {
    rate_name: rule.rate_name,
    payment_unit: "PER_SESSION",
    rate_amount: String(rule.rate_amount ?? ""),
    currency: rule.currency || "THB",
    role_scope: rule.role_scope || "ALL",
    person_type_scope: rule.person_type_scope || "ALL",
    effective_from: rule.effective_from || "",
    effective_to: rule.effective_to || "",
    note: rule.note || "",
  };
}

function toPayload(form: FormState): InvigilationRateRulePayload {
  return {
    rate_name: form.rate_name.trim(),
    payment_unit: "PER_SESSION",
    rate_amount: form.rate_amount.trim(),
    currency: (form.currency.trim() || "THB").toUpperCase(),
    role_scope: (form.role_scope.trim() || "ALL").toUpperCase(),
    person_type_scope: (form.person_type_scope.trim() || "ALL").toUpperCase(),
    effective_from: form.effective_from || null,
    effective_to: form.effective_to || null,
    note: form.note.trim() || null,
  };
}

export default function InvigilationRateRules() {
  const { t } = useI18n();
  const { activeRole } = useAuth();
  const { toast } = useUi();
  const queryClient = useQueryClient();
  const { data, isError, isLoading } = useInvigilationRateRules();
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [busyAction, setBusyAction] = useState<string | null>(null);

  const isAdmin = activeRole === "admin";

  const resetForm = () => {
    setEditingId(null);
    setForm(EMPTY_FORM);
  };

  const reload = async () => {
    await queryClient.invalidateQueries({ queryKey: invigilationRateRulesQueryKey });
  };

  const handleSubmit = async () => {
    if (!isAdmin) {
      toast(t("rateRules.toast.adminOnly"), "warning");
      return;
    }
    const payload = toPayload(form);
    if (!payload.rate_name || !payload.rate_amount) {
      toast(t("rateRules.toast.required"), "error");
      return;
    }

    setBusyAction("save");
    try {
      if (editingId) {
        await updateInvigilationRateRule(editingId, payload);
        toast(t("rateRules.toast.updated"), "success");
      } else {
        await createInvigilationRateRule(payload);
        toast(t("rateRules.toast.created"), "success");
      }
      resetForm();
      await reload();
    } catch (error) {
      toast(error instanceof Error ? error.message : t("rateRules.toast.saveFailed"), "error");
    } finally {
      setBusyAction(null);
    }
  };

  const handleActivate = async (rule: InvigilationRateRule) => {
    if (!isAdmin) {
      toast(t("rateRules.toast.adminOnly"), "warning");
      return;
    }
    setBusyAction(`activate-${rule.rate_rule_id}`);
    try {
      await activateInvigilationRateRule(rule.rate_rule_id);
      toast(t("rateRules.toast.activated"), "success");
      await reload();
    } catch (error) {
      toast(error instanceof Error ? error.message : t("rateRules.toast.actionFailed"), "error");
    } finally {
      setBusyAction(null);
    }
  };

  const handleArchive = async (rule: InvigilationRateRule) => {
    if (!isAdmin) {
      toast(t("rateRules.toast.adminOnly"), "warning");
      return;
    }
    setBusyAction(`archive-${rule.rate_rule_id}`);
    try {
      await archiveInvigilationRateRule(rule.rate_rule_id);
      toast(t("rateRules.toast.archived"), "success");
      if (editingId === rule.rate_rule_id) resetForm();
      await reload();
    } catch (error) {
      toast(error instanceof Error ? error.message : t("rateRules.toast.actionFailed"), "error");
    } finally {
      setBusyAction(null);
    }
  };

  const columns = useMemo<Array<DataTableColumn<InvigilationRateRule>>>(() => [
    {
      key: "name",
      label: t("rateRules.table.name"),
      minWidth: "220px",
      render: (rule) => (
        <div className="data-table__content">
          <strong>{rule.rate_name}</strong>
          <p>{rule.note || t("rateRules.table.noNote")}</p>
        </div>
      ),
    },
    {
      key: "status",
      label: t("rateRules.table.status"),
      width: "130px",
      render: (rule) => <Badge variant={statusVariant(rule.status)} size="sm">{rule.status}</Badge>,
    },
    {
      key: "amount",
      label: t("rateRules.table.amount"),
      width: "160px",
      render: (rule) => `${rule.rate_amount} ${rule.currency}`,
    },
    {
      key: "scope",
      label: t("rateRules.table.scope"),
      minWidth: "190px",
      render: (rule) => (
        <div className="data-table__content">
          <strong>{rule.role_scope}</strong>
          <p>{rule.person_type_scope}</p>
        </div>
      ),
    },
    {
      key: "effective",
      label: t("rateRules.table.effective"),
      minWidth: "180px",
      render: (rule) => `${rule.effective_from || "-"} - ${rule.effective_to || t("rateRules.table.openEnded")}`,
    },
    {
      key: "safety",
      label: t("rateRules.table.safety"),
      minWidth: "170px",
      render: (rule) => (
        <div className="data-table__content">
          <Badge variant="blue" size="sm">{t("rateRules.previewOnly")}</Badge>
          <p>{rule.payment_authorization_enabled ? t("common.yes") : t("rateRules.noAuthorization")}</p>
        </div>
      ),
    },
    {
      key: "actions",
      label: t("rateRules.table.actions"),
      minWidth: "260px",
      render: (rule) => (
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            size="sm"
            variant="outline"
            disabled={!isAdmin || rule.status === "ARCHIVED" || busyAction !== null}
            onClick={() => {
              setEditingId(rule.rate_rule_id);
              setForm(toForm(rule));
            }}
          >
            {t("common.edit")}
          </Button>
          <Button
            type="button"
            size="sm"
            variant="gold"
            disabled={!isAdmin || rule.status === "ACTIVE" || rule.status === "ARCHIVED" || busyAction !== null}
            loading={busyAction === `activate-${rule.rate_rule_id}`}
            onClick={() => void handleActivate(rule)}
          >
            {t("rateRules.actions.activate")}
          </Button>
          <Button
            type="button"
            size="sm"
            variant="danger"
            disabled={!isAdmin || rule.status === "ARCHIVED" || busyAction !== null}
            loading={busyAction === `archive-${rule.rate_rule_id}`}
            onClick={() => void handleArchive(rule)}
          >
            {t("rateRules.actions.archive")}
          </Button>
        </div>
      ),
    },
  ], [busyAction, editingId, isAdmin, t]);

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
        <EmptyState icon={<Icon name="warning" />} title={t("rateRules.empty.errorTitle")} />
      </div>
    );
  }

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero page-hero--dashboard">
        <div>
          <span className="page-hero__eyebrow">{t("rateRules.eyebrow")}</span>
          <h2 className="page-hero__title">{t("rateRules.title")}</h2>
          <p className="page-hero__description">{t("rateRules.description")}</p>
        </div>
        <div className="page-hero__actions">
          <Badge variant="gold">{t("rateRules.previewOnly")}</Badge>
        </div>
      </section>

      <Card
        title={t("rateRules.warning.title")}
        subtitle={t("rateRules.warning.body")}
        actions={<Badge variant="blue">{data.payment_authorization_enabled ? t("common.yes") : t("rateRules.noAuthorization")}</Badge>}
      />

      <Card
        title={editingId ? t("rateRules.form.editTitle") : t("rateRules.form.createTitle")}
        subtitle={isAdmin ? t("rateRules.form.subtitle") : t("rateRules.form.adminOnly")}
      >
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("rateRules.form.name")}</span>
            <input className="w-full rounded border px-3 py-2" value={form.rate_name} disabled={!isAdmin} onChange={(event) => setForm({ ...form, rate_name: event.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("rateRules.form.unit")}</span>
            <select className="w-full rounded border px-3 py-2" value={form.payment_unit} disabled={!isAdmin} onChange={() => setForm({ ...form, payment_unit: "PER_SESSION" })}>
              <option value="PER_SESSION">{t("rateRules.units.perSession")}</option>
            </select>
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("rateRules.form.amount")}</span>
            <input className="w-full rounded border px-3 py-2" type="number" min="0" step="0.01" value={form.rate_amount} disabled={!isAdmin} onChange={(event) => setForm({ ...form, rate_amount: event.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("rateRules.form.currency")}</span>
            <input className="w-full rounded border px-3 py-2" value={form.currency} disabled={!isAdmin} onChange={(event) => setForm({ ...form, currency: event.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("rateRules.form.roleScope")}</span>
            <input className="w-full rounded border px-3 py-2" value={form.role_scope} disabled={!isAdmin} onChange={(event) => setForm({ ...form, role_scope: event.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("rateRules.form.personTypeScope")}</span>
            <input className="w-full rounded border px-3 py-2" value={form.person_type_scope} disabled={!isAdmin} onChange={(event) => setForm({ ...form, person_type_scope: event.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("rateRules.form.effectiveFrom")}</span>
            <input className="w-full rounded border px-3 py-2" type="date" value={form.effective_from} disabled={!isAdmin} onChange={(event) => setForm({ ...form, effective_from: event.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("rateRules.form.effectiveTo")}</span>
            <input className="w-full rounded border px-3 py-2" type="date" value={form.effective_to} disabled={!isAdmin} onChange={(event) => setForm({ ...form, effective_to: event.target.value })} />
          </label>
        </div>
        <label className="mt-4 block space-y-1 text-sm">
          <span className="block text-gray-500">{t("rateRules.form.note")}</span>
          <textarea className="w-full rounded border px-3 py-2" rows={3} value={form.note} disabled={!isAdmin} onChange={(event) => setForm({ ...form, note: event.target.value })} />
        </label>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button type="button" loading={busyAction === "save"} disabled={!isAdmin || busyAction !== null} onClick={() => void handleSubmit()}>
            {editingId ? t("rateRules.actions.saveEdit") : t("rateRules.actions.createDraft")}
          </Button>
          <Button type="button" variant="outline" disabled={busyAction !== null} onClick={resetForm}>
            {t("common.reset")}
          </Button>
        </div>
      </Card>

      {data.rate_rules.length === 0 ? (
        <Card>
          <EmptyState
            icon={<Icon name="payments" />}
            title={t("rateRules.empty.noRowsTitle")}
            description={t("rateRules.empty.noRowsDescription")}
          />
        </Card>
      ) : (
        <Card title={t("rateRules.table.title")} subtitle={t("rateRules.table.subtitle")}>
          <DataTable columns={columns} rows={data.rate_rules} rowKey={(rule) => String(rule.rate_rule_id)} compact tableLayout="fixed" />
        </Card>
      )}
    </div>
  );
}

