import { useMemo, useState } from "react";

import { BarChart } from "@/components/charts/BarChart";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Skeleton } from "@/components/ui/Skeleton";
import { useAuth } from "@/store/auth.store";
import { useI18n } from "@/i18n";
import { useWorkloadDutyAnalytics } from "@/hooks/domain/useWorkloadDutyAnalytics";
import { presentWorkloadPerson, presentWorkloadSummary } from "@/utils/presenters/workloadDutyAnalyticsPresenter";
import type { DutyType, WorkloadRoleGroup } from "@/types/workloadDutyAnalytics";

function SummaryCard({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <Card className="p-4">
      <div className="text-xs uppercase tracking-wide text-gray-500">{label}</div>
      <div className="mt-2 text-3xl font-bold">{value}</div>
      <div className="mt-1 text-sm text-gray-500">{hint}</div>
    </Card>
  );
}

function getDefaultRoleGroup(role?: string | null): WorkloadRoleGroup {
  const value = String(role ?? "").toLowerCase();
  if (value === "teacher") return "teacher";
  if (value === "staff" || value === "supervisor" || value === "dept_supervisor" || value === "esq_head" || value === "secretary") return "staff";
  return "all";
}

function getDefaultTitle(role?: string | null): string {
  const value = String(role ?? "").toLowerCase();
  if (value === "teacher") return "workloadDashboard.pageTitle.teacher";
  if (value === "staff" || value === "supervisor" || value === "dept_supervisor" || value === "esq_head" || value === "secretary") return "workloadDashboard.pageTitle.staff";
  return "workloadDashboard.pageTitle.admin";
}

export default function WorkloadDutyAnalytics() {
  const { t } = useI18n();
  const { user } = useAuth();
  const defaultRoleGroup = getDefaultRoleGroup(user?.role ?? null);
  const [semester, setSemester] = useState<string>("");
  const [academicYear, setAcademicYear] = useState<string>("");
  const [periodId, setPeriodId] = useState<string>("");
  const [examType, setExamType] = useState<string>("");
  const [roleGroup, setRoleGroup] = useState<WorkloadRoleGroup>(defaultRoleGroup);
  const [personSearch, setPersonSearch] = useState<string>("");
  const [dutyType, setDutyType] = useState<DutyType>("all");

  const query = {
    semester,
    academic_year: academicYear || null,
    period_id: periodId ? Number(periodId) : null,
    exam_type: examType || null,
    role_group: roleGroup,
    person_id: personSearch.trim() || null,
    include_teachers: true,
    include_staff: true,
    duty_type: dutyType,
  };

  const { data, isLoading, isError } = useWorkloadDutyAnalytics(query);

  const presentedSummary = useMemo(() => (data ? presentWorkloadSummary(data) : []), [data]);
  const presentedPeople = useMemo(() => (data ? data.by_person.map(presentWorkloadPerson) : []), [data]);

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-8 w-72" />
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, index) => <Skeleton key={index} className="h-32" />)}
        </div>
        <Skeleton className="h-80" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="p-6">
        <EmptyState icon={<Icon name="warning" />} title={t("workloadDashboard.empty.noData")} />
      </div>
    );
  }

  const byPersonLabels = presentedPeople.map((person) => person.displayName);
  const byPersonValues = presentedPeople.map((person) => person.combined);
  const dailyLabels = data.daily_series.map((row) => row.date);
  const dailyValues = data.daily_series.map((row) => row.cumulative_combined);
  const slotLabels = data.time_slot_series.map((row) => row.time_slot);
  const slotValues = data.time_slot_series.map((row) => row.combined_count);

  return (
    <div className="p-6 space-y-6">
      <section className="space-y-2">
        <h1 className="text-2xl font-bold">{t(getDefaultTitle(user?.role ?? null))}</h1>
        <p className="text-sm text-gray-500">{t("workloadDashboard.description")}</p>
      </section>

      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("workloadDashboard.filters.semester")}</span>
            <input className="w-full rounded border px-3 py-2" value={semester} onChange={(event) => setSemester(event.target.value)} placeholder="1 / 2 / summer" />
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("workloadDashboard.filters.academicYear")}</span>
            <input className="w-full rounded border px-3 py-2" value={academicYear} onChange={(event) => setAcademicYear(event.target.value)} placeholder="2568" />
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("workloadDashboard.filters.period")}</span>
            <input className="w-full rounded border px-3 py-2" value={periodId} onChange={(event) => setPeriodId(event.target.value)} placeholder="1" />
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("workloadDashboard.filters.examType")}</span>
            <input className="w-full rounded border px-3 py-2" value={examType} onChange={(event) => setExamType(event.target.value)} placeholder="final" />
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("workloadDashboard.filters.roleGroup")}</span>
            <select className="w-full rounded border px-3 py-2" value={roleGroup} onChange={(event) => setRoleGroup(event.target.value as WorkloadRoleGroup)}>
              <option value="all">{t("common.all")}</option>
              <option value="admin">{t("workloadDashboard.roleGroup.admin")}</option>
              <option value="staff">{t("workloadDashboard.roleGroup.staff")}</option>
              <option value="supervisor">{t("workloadDashboard.roleGroup.supervisor")}</option>
              <option value="teacher">{t("workloadDashboard.roleGroup.teacher")}</option>
            </select>
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("workloadDashboard.filters.dutyType")}</span>
            <select className="w-full rounded border px-3 py-2" value={dutyType} onChange={(event) => setDutyType(event.target.value as DutyType)}>
              <option value="all">{t("common.all")}</option>
              <option value="invigilation">Invigilation</option>
              <option value="paper_distribution">Paper distribution</option>
              <option value="combined">Combined</option>
            </select>
          </label>
          <label className="space-y-1 text-sm md:col-span-2 xl:col-span-3">
            <span className="block text-gray-500">{t("workloadDashboard.filters.personSearch")}</span>
            <input className="w-full rounded border px-3 py-2" value={personSearch} onChange={(event) => setPersonSearch(event.target.value)} placeholder={t("common.search")} />
          </label>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button type="button" variant="outline" onClick={() => {
            setSemester("");
            setAcademicYear("");
            setPeriodId("");
            setExamType("");
            setRoleGroup(defaultRoleGroup);
            setPersonSearch("");
            setDutyType("all");
          }}>
            {t("common.reset")}
          </Button>
          <div className="text-sm text-gray-500 flex items-center">{t("workloadDashboard.recommendations.balanceWorkload")}</div>
        </div>
      </Card>

      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {presentedSummary.map((card) => (
          <SummaryCard key={card.label} {...card} />
        ))}
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <Card className="p-4 xl:col-span-3">
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div>
              <h2 className="text-lg font-semibold">{t("workloadDashboard.charts.byPerson")}</h2>
              <p className="text-sm text-gray-500">{t("workloadDashboard.description")}</p>
            </div>
            <div className="text-sm text-gray-500">
              {t("workloadDashboard.summary.fairnessScore")}: {data.summary.imbalance_score.toFixed(2)}
            </div>
          </div>
          <div className="mt-4">
            <BarChart labels={byPersonLabels} values={byPersonValues} color="var(--crimson)" />
          </div>
        </Card>

        <Card className="p-4 xl:col-span-2">
          <h2 className="text-lg font-semibold">{t("workloadDashboard.charts.dailyCumulative")}</h2>
          <div className="mt-4">
            <BarChart labels={dailyLabels} values={dailyValues} color="var(--teal)" />
          </div>
        </Card>

        <Card className="p-4">
          <h2 className="text-lg font-semibold">{t("workloadDashboard.fairness.title")}</h2>
          <div className="mt-3 space-y-3 text-sm">
            <div>
              <span className="text-gray-500">{t("workloadDashboard.summary.fairnessScore")}: </span>
              <strong>{data.fairness.imbalance_score.toFixed(2)}</strong>
            </div>
            <div>
              <span className="text-gray-500">{t("workloadDashboard.fairness.riskBand")}: </span>
              <strong>{data.fairness.risk_band}</strong>
            </div>
            <div>
              <div className="font-medium text-gray-700">{t("workloadDashboard.fairness.overloaded")}</div>
              <ul className="mt-2 space-y-1 text-gray-600">
                {data.fairness.overloaded_people.slice(0, 4).map((person) => (
                  <li key={person.person_id}>{person.display_name} - {person.combined_count}</li>
                ))}
                {data.fairness.overloaded_people.length === 0 && <li>{t("workloadDashboard.empty.noData")}</li>}
              </ul>
            </div>
            <div>
              <div className="font-medium text-gray-700">{t("workloadDashboard.fairness.underloaded")}</div>
              <ul className="mt-2 space-y-1 text-gray-600">
                {data.fairness.underloaded_people.slice(0, 4).map((person) => (
                  <li key={person.person_id}>{person.display_name} - {person.combined_count}</li>
                ))}
                {data.fairness.underloaded_people.length === 0 && <li>{t("workloadDashboard.empty.noData")}</li>}
              </ul>
            </div>
          </div>
        </Card>

        <Card className="p-4 xl:col-span-3">
          <h2 className="text-lg font-semibold">{t("workloadDashboard.charts.timeSlot")}</h2>
          <div className="mt-4">
            <BarChart labels={slotLabels} values={slotValues} color="#f59e0b" />
          </div>
        </Card>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">{t("workloadDashboard.charts.byPerson")}</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2 pr-4">{t("common.role")}</th>
                <th className="py-2 pr-4">{t("workloadDashboard.filters.personSearch")}</th>
                <th className="py-2 pr-4">{t("workloadDashboard.summary.totalInvigilation")}</th>
                <th className="py-2 pr-4">{t("workloadDashboard.summary.totalDistribution")}</th>
                <th className="py-2 pr-4">{t("workloadDashboard.summary.combined")}</th>
              </tr>
            </thead>
            <tbody>
              {presentedPeople.map((person) => (
                <tr key={person.personId} className="border-b">
                  <td className="py-2 pr-4">{person.roleGroup}</td>
                  <td className="py-2 pr-4">{person.displayName}</td>
                  <td className="py-2 pr-4">{person.invigilation}</td>
                  <td className="py-2 pr-4">{person.distribution}</td>
                  <td className="py-2 pr-4">{person.combined}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
