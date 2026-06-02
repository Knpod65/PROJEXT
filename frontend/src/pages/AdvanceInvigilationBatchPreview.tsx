import { useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Skeleton } from "@/components/ui/Skeleton";
import { useI18n } from "@/i18n";
import { useAdvanceBatchPreview } from "@/hooks/domain/useAdvanceBatchPreview";

function SummaryCard({ label, value, hint }: { label: string; value: string | number; hint: string }) {
  return (
    <Card className="p-4">
      <div className="text-xs uppercase text-gray-500">{label}</div>
      <div className="mt-2 text-3xl font-bold">{value}</div>
      <div className="mt-1 text-sm text-gray-500">{hint}</div>
    </Card>
  );
}

function StatusPill({ value }: { value: string }) {
  const isBlocked = value.includes("BLOCKED");
  const className = isBlocked
    ? "inline-flex rounded bg-red-50 px-2 py-1 text-xs font-medium text-red-700"
    : "inline-flex rounded bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700";
  return <span className={className}>{value}</span>;
}

export default function AdvanceInvigilationBatchPreview() {
  const { t } = useI18n();
  const [periodId, setPeriodId] = useState("");
  const [academicYear, setAcademicYear] = useState("2568");
  const [semester, setSemester] = useState("2");
  const [examType, setExamType] = useState("final");

  const query = {
    period_id: periodId ? Number(periodId) : null,
    academic_year: academicYear || null,
    semester: semester || null,
    exam_type: examType || null,
  };
  const { data, isError, isLoading } = useAdvanceBatchPreview(query);

  const summaryCards = useMemo(() => {
    if (!data) return [];
    return [
      {
        label: t("advanceBatch.summary.totalAssignments"),
        value: data.summary.total_assignments,
        hint: t("advanceBatch.summary.previewOnly"),
      },
      {
        label: t("advanceBatch.summary.ready"),
        value: data.summary.ready_for_batch_review,
        hint: t("advanceBatch.summary.reviewRequired"),
      },
      {
        label: t("advanceBatch.summary.blocked"),
        value: data.summary.blocked_rows,
        hint: t("advanceBatch.summary.blockerHint"),
      },
      {
        label: t("advanceBatch.summary.pendingRate"),
        value: data.summary.pending_rate_rule_count,
        hint: t("advanceBatch.summary.noAmount"),
      },
    ];
  }, [data, t]);

  if (isLoading) {
    return (
      <div className="page-stack page-stack--spacious">
        <div className="stitch-metric-grid">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="dashboard-skeleton" />
          ))}
        </div>
        <Skeleton className="dashboard-chart-skeleton" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="page-stack page-stack--spacious">
        <EmptyState icon={<Icon name="warning" />} title={t("advanceBatch.empty.errorTitle")} />
      </div>
    );
  }

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero page-hero--dashboard">
        <div>
          <span className="page-hero__eyebrow">{t("advanceBatch.eyebrow")}</span>
          <h2 className="page-hero__title">{t("advanceBatch.title")}</h2>
          <p className="page-hero__description">{t("advanceBatch.description")}</p>
        </div>
      </section>

      <div className="rounded border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        <strong>{t("advanceBatch.warning.title")}</strong>
        <div className="mt-1">{t("advanceBatch.warning.body")}</div>
      </div>

      <Card className="p-4">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("advanceBatch.filters.period")}</span>
            <input
              className="w-full rounded border px-3 py-2"
              value={periodId}
              onChange={(event) => setPeriodId(event.target.value)}
              placeholder={t("advanceBatch.filters.periodPlaceholder")}
            />
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("advanceBatch.filters.academicYear")}</span>
            <input className="w-full rounded border px-3 py-2" value={academicYear} onChange={(event) => setAcademicYear(event.target.value)} />
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("advanceBatch.filters.semester")}</span>
            <input className="w-full rounded border px-3 py-2" value={semester} onChange={(event) => setSemester(event.target.value)} />
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("advanceBatch.filters.examType")}</span>
            <input className="w-full rounded border px-3 py-2" value={examType} onChange={(event) => setExamType(event.target.value)} />
          </label>
        </div>
        <div className="mt-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setPeriodId("");
              setAcademicYear("2568");
              setSemester("2");
              setExamType("final");
            }}
          >
            {t("common.reset")}
          </Button>
        </div>
      </Card>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        {summaryCards.map((card) => (
          <SummaryCard key={card.label} {...card} />
        ))}
      </section>

      {data.roster_rows.length === 0 ? (
        <Card className="p-4">
          <EmptyState
            icon={<Icon name="info" />}
            title={t("advanceBatch.empty.noRowsTitle")}
            description={t("advanceBatch.empty.noRowsDescription")}
          />
        </Card>
      ) : (
        <Card title={t("advanceBatch.roster.title")} subtitle={t("advanceBatch.roster.subtitle")}>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b text-left">
                  <th className="py-2 pr-4">{t("advanceBatch.table.person")}</th>
                  <th className="py-2 pr-4">{t("advanceBatch.table.role")}</th>
                  <th className="py-2 pr-4">{t("advanceBatch.table.exam")}</th>
                  <th className="py-2 pr-4">{t("advanceBatch.table.room")}</th>
                  <th className="py-2 pr-4">{t("advanceBatch.table.inclusion")}</th>
                  <th className="py-2 pr-4">{t("advanceBatch.table.amount")}</th>
                  <th className="py-2 pr-4">{t("advanceBatch.table.reconciliation")}</th>
                  <th className="py-2 pr-4">{t("advanceBatch.table.warning")}</th>
                </tr>
              </thead>
              <tbody>
                {data.roster_rows.map((row) => (
                  <tr key={row.source_record_ref} className="border-b align-top">
                    <td className="py-2 pr-4">
                      <div className="font-medium">{row.person_name || t("advanceBatch.table.unknownPerson")}</div>
                      <div className="text-xs text-gray-500">{row.department || row.person_type || "-"}</div>
                    </td>
                    <td className="py-2 pr-4">{row.duty_role}</td>
                    <td className="py-2 pr-4">
                      <div>{row.course_code || "-"} {row.section ? `(${row.section})` : ""}</div>
                      <div className="text-xs text-gray-500">{row.exam_date || "-"} {row.start_time || ""}-{row.end_time || ""}</div>
                    </td>
                    <td className="py-2 pr-4">{row.room_name || "-"}</td>
                    <td className="py-2 pr-4"><StatusPill value={row.advance_inclusion_status} /></td>
                    <td className="py-2 pr-4">
                      <div className="font-medium">{row.amount_status}</div>
                      <div className="text-xs text-gray-500">{row.amount_preview}</div>
                    </td>
                    <td className="py-2 pr-4">{row.reconciliation_status}</td>
                    <td className="py-2 pr-4">{row.warnings.join("; ") || row.blocked_reason || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <Card title={t("advanceBatch.blockers.title")} subtitle={t("advanceBatch.blockers.subtitle")}>
          <ul className="space-y-2 text-sm text-gray-600">
            {(data.blockers.length ? data.blockers : [t("advanceBatch.blockers.none")]).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </Card>
        <Card title={t("advanceBatch.warnings.title")} subtitle={t("advanceBatch.warnings.subtitle")}>
          <ul className="space-y-2 text-sm text-gray-600">
            {(data.warnings.length ? data.warnings : [t("advanceBatch.warnings.none")]).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </Card>
        <Card title={t("advanceBatch.ruleGaps.title")} subtitle={t("advanceBatch.ruleGaps.subtitle")}>
          <ul className="space-y-2 text-sm text-gray-600">
            {data.rule_gaps.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </Card>
      </section>
    </div>
  );
}
