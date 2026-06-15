import { useMemo, useState } from "react";

import { BarChart } from "@/components/charts/BarChart";
import { DashboardMetricCard } from "@/components/dashboard/DashboardMetricCard";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, type DataTableColumn } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { FilterBar } from "@/components/ui/FilterBar";
import { FormField } from "@/components/ui/FormField";
import { Icon } from "@/components/ui/Icon";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageSkeleton } from "@/components/ui/PageSkeleton";
import { StatusChip, type StatusTone } from "@/components/ui/StatusChip";
import { useWorkloadDutyAnalytics } from "@/hooks/domain/useWorkloadDutyAnalytics";
import { useI18n } from "@/i18n";
import { useAuth } from "@/store/auth.store";
import type { DutyType, WorkloadRoleGroup } from "@/types/workloadDutyAnalytics";
import {
  hasWorkloadAnalyticsResults,
  presentWorkloadPerson,
  presentWorkloadSummary,
} from "@/utils/presenters/workloadDutyAnalyticsPresenter";

interface WorkloadFilters {
  semester: string;
  academicYear: string;
  periodId: string;
  examType: string;
  roleGroup: WorkloadRoleGroup;
  personSearch: string;
  dutyType: DutyType;
}

type PersonRow = ReturnType<typeof presentWorkloadPerson>;

function getDefaultRoleGroup(role?: string | null): WorkloadRoleGroup {
  const value = String(role ?? "").toLowerCase();
  if (value === "teacher") return "teacher";
  if (["staff", "supervisor", "dept_supervisor", "esq_head", "secretary"].includes(value)) return "staff";
  return "all";
}

function getDefaultTitle(role?: string | null): string {
  const value = String(role ?? "").toLowerCase();
  if (value === "teacher") return "workloadDashboard.pageTitle.teacher";
  if (["staff", "supervisor", "dept_supervisor", "esq_head", "secretary"].includes(value)) return "workloadDashboard.pageTitle.staff";
  return "workloadDashboard.pageTitle.admin";
}

function createDefaultFilters(role?: string | null): WorkloadFilters {
  return {
    semester: "",
    academicYear: "",
    periodId: "",
    examType: "",
    roleGroup: getDefaultRoleGroup(role),
    personSearch: "",
    dutyType: "all",
  };
}

function riskTone(riskBand: string): StatusTone {
  if (riskBand === "critical") return "danger";
  if (riskBand === "warning") return "warning";
  if (riskBand === "good") return "success";
  return "information";
}

export default function WorkloadDutyAnalytics() {
  const { t } = useI18n();
  const { user } = useAuth();
  const defaults = useMemo(() => createDefaultFilters(user?.role), [user?.role]);
  const [draftFilters, setDraftFilters] = useState<WorkloadFilters>(defaults);
  const [appliedFilters, setAppliedFilters] = useState<WorkloadFilters>(defaults);
  const [sortKey, setSortKey] = useState<keyof PersonRow>("combined");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

  const query = {
    semester: appliedFilters.semester,
    academic_year: appliedFilters.academicYear || null,
    period_id: appliedFilters.periodId ? Number(appliedFilters.periodId) : null,
    exam_type: appliedFilters.examType || null,
    role_group: appliedFilters.roleGroup,
    person_id: appliedFilters.personSearch.trim() || null,
    include_teachers: true,
    include_staff: true,
    duty_type: appliedFilters.dutyType,
  };

  const { data, isLoading, isError } = useWorkloadDutyAnalytics(query);
  const presentedSummary = useMemo(() => (data ? presentWorkloadSummary(data) : []), [data]);
  const presentedPeople = useMemo(() => (data ? data.by_person.map(presentWorkloadPerson) : []), [data]);
  const sortedPeople = useMemo(() => [...presentedPeople].sort((left, right) => {
    const leftValue = left[sortKey];
    const rightValue = right[sortKey];
    const result = typeof leftValue === "number" && typeof rightValue === "number"
      ? leftValue - rightValue
      : String(leftValue).localeCompare(String(rightValue));
    return sortDirection === "asc" ? result : -result;
  }), [presentedPeople, sortDirection, sortKey]);

  const personColumns = useMemo<Array<DataTableColumn<PersonRow>>>(() => [
    { key: "roleGroup", label: t("workloadDashboard.labels.roleGroup"), sortable: true },
    { key: "displayName", label: t("workloadDashboard.labels.person"), sortable: true },
    { key: "invigilation", label: t("workloadDashboard.labels.invigilationCount"), align: "right", sortable: true },
    { key: "distribution", label: t("workloadDashboard.labels.distributionCount"), align: "right", sortable: true },
    { key: "combined", label: t("workloadDashboard.labels.combinedCount"), align: "right", sortable: true },
  ], [t]);

  const updateDraft = <K extends keyof WorkloadFilters>(key: K, value: WorkloadFilters[K]) => {
    setDraftFilters((current) => ({ ...current, [key]: value }));
  };
  const resetFilters = () => {
    setDraftFilters(defaults);
    setAppliedFilters(defaults);
  };
  const handleSort = (key: string) => {
    const nextKey = key as keyof PersonRow;
    if (nextKey === sortKey) setSortDirection((current) => current === "asc" ? "desc" : "asc");
    else {
      setSortKey(nextKey);
      setSortDirection("asc");
    }
  };

  if (isLoading) return <PageSkeleton cards={6} rows={5} />;

  if (isError || !data) {
    return (
      <div className="page-stack page-stack--spacious">
        <PageHeader eyebrow={t("workloadDashboard.eyebrow")} title={t(getDefaultTitle(user?.role))} description={t("workloadDashboard.description")} />
        <EmptyState icon={<Icon name="warning" />} title={t("workloadDashboard.empty.noData")} />
      </div>
    );
  }

  const hasAnyAnalyticsData = hasWorkloadAnalyticsResults(data);
  const roleCounts = Object.entries(data.by_person.reduce<Record<string, number>>((counts, person) => {
    counts[person.role_group] = (counts[person.role_group] ?? 0) + 1;
    return counts;
  }, {}));
  const chartPeople = [...presentedPeople].sort((left, right) => right.combined - left.combined).slice(0, 12);
  const dailySeries = data.daily_series.slice(-12);
  const timeSlotSeries = data.time_slot_series.slice(0, 12);

  return (
    <div className="page-stack page-stack--spacious workload-dashboard">
      <PageHeader
        eyebrow={t("workloadDashboard.eyebrow")}
        title={t(getDefaultTitle(user?.role))}
        description={t("workloadDashboard.description")}
        status={<StatusChip tone={riskTone(data.fairness.risk_band)}>{t(`workloadDashboard.fairness.band.${data.fairness.risk_band}`)}</StatusChip>}
      />

      <FilterBar
        layout="grid"
        actions={(
          <>
            <Button type="button" variant="outline" onClick={resetFilters}>{t("common.reset")}</Button>
            <Button type="button" onClick={() => setAppliedFilters(draftFilters)}>{t("common.applyFilters")}</Button>
          </>
        )}
      >
        <FormField label={t("workloadDashboard.filters.semester")}><input value={draftFilters.semester} onChange={(event) => updateDraft("semester", event.target.value)} placeholder={t("workloadDashboard.filters.semesterPlaceholder")} /></FormField>
        <FormField label={t("workloadDashboard.filters.academicYear")}><input value={draftFilters.academicYear} onChange={(event) => updateDraft("academicYear", event.target.value)} placeholder={t("workloadDashboard.filters.academicYearPlaceholder")} /></FormField>
        <FormField label={t("workloadDashboard.filters.period")}><input value={draftFilters.periodId} onChange={(event) => updateDraft("periodId", event.target.value)} placeholder={t("workloadDashboard.filters.periodPlaceholder")} /></FormField>
        <FormField label={t("workloadDashboard.filters.examType")}><input value={draftFilters.examType} onChange={(event) => updateDraft("examType", event.target.value)} placeholder={t("workloadDashboard.filters.examTypePlaceholder")} /></FormField>
        <FormField label={t("workloadDashboard.filters.roleGroup")}>
          <select value={draftFilters.roleGroup} onChange={(event) => updateDraft("roleGroup", event.target.value as WorkloadRoleGroup)}>
            {(["all", "admin", "staff", "supervisor", "teacher"] as WorkloadRoleGroup[]).map((value) => <option key={value} value={value}>{t(`workloadDashboard.roleGroup.${value}`)}</option>)}
          </select>
        </FormField>
        <FormField label={t("workloadDashboard.filters.dutyType")}>
          <select value={draftFilters.dutyType} onChange={(event) => updateDraft("dutyType", event.target.value as DutyType)}>
            {(["all", "invigilation", "paper_distribution", "combined"] as DutyType[]).map((value) => <option key={value} value={value}>{t(`workloadDashboard.dutyTypes.${value}`)}</option>)}
          </select>
        </FormField>
        <FormField className="filter-bar__search" label={t("workloadDashboard.filters.personSearch")}><input value={draftFilters.personSearch} onChange={(event) => updateDraft("personSearch", event.target.value)} placeholder={t("common.search")} /></FormField>
      </FilterBar>

      <section className="summary-grid" aria-label={t("workloadDashboard.summary.title")}>
        {presentedSummary.map((card) => <DashboardMetricCard key={card.label} {...card} />)}
      </section>

      {!hasAnyAnalyticsData ? (
        <Card><EmptyState icon={<Icon name="info" />} title={t("workloadDashboard.empty.noFilteredResults")} description={t("workloadDashboard.empty.adjustFilters")} /></Card>
      ) : (
        <>
          <section className="analytics-grid">
            <Card className="analytics-grid__wide" title={t("workloadDashboard.charts.byPerson")} subtitle={t("workloadDashboard.charts.byPersonHint")}>
              <BarChart labels={chartPeople.map((person) => person.displayName)} values={chartPeople.map((person) => person.combined)} color="var(--role-accent)" />
            </Card>
            <Card title={t("workloadDashboard.charts.categoryBreakdown")} subtitle={t("workloadDashboard.charts.categoryBreakdownHint")}>
              <BarChart labels={[t("workloadDashboard.dutyTypes.invigilation"), t("workloadDashboard.dutyTypes.paperDistribution")]} values={[data.summary.total_invigilation_duties, data.summary.total_distribution_duties]} color="var(--teal, var(--role-accent))" />
            </Card>
            <Card title={t("workloadDashboard.charts.roleComposition")} subtitle={t("workloadDashboard.charts.roleCompositionHint")}>
              <BarChart labels={roleCounts.map(([role]) => t(`workloadDashboard.roleGroup.${role}`))} values={roleCounts.map(([, count]) => count)} color="var(--gold)" />
            </Card>
            <Card title={t("workloadDashboard.charts.dailyCumulative")}>
              {dailySeries.length > 0 ? <BarChart labels={dailySeries.map((row) => row.date)} values={dailySeries.map((row) => row.cumulative_combined)} color="var(--teal, var(--role-accent))" /> : <EmptyState title={t("workloadDashboard.empty.noDailyData")} />}
            </Card>
            <Card title={t("workloadDashboard.charts.timeSlot")}>
              {timeSlotSeries.length > 0 ? <BarChart labels={timeSlotSeries.map((row) => row.time_slot)} values={timeSlotSeries.map((row) => row.combined_count)} color="var(--gold)" /> : <EmptyState title={t("workloadDashboard.empty.noTimeSlotData")} />}
            </Card>
            <Card title={t("workloadDashboard.fairness.title")} actions={<StatusChip tone={riskTone(data.fairness.risk_band)}>{t(`workloadDashboard.fairness.band.${data.fairness.risk_band}`)}</StatusChip>}>
              <div className="fairness-grid">
                <div><strong>{t("workloadDashboard.fairness.overloaded")}</strong><ul className="plain-list">{data.fairness.overloaded_people.slice(0, 5).map((person) => <li key={person.person_id}>{person.display_name} <StatusChip tone="warning">{person.combined_count}</StatusChip></li>)}{data.fairness.overloaded_people.length === 0 ? <li>{t("workloadDashboard.empty.noOverloadedPeople")}</li> : null}</ul></div>
                <div><strong>{t("workloadDashboard.fairness.underloaded")}</strong><ul className="plain-list">{data.fairness.underloaded_people.slice(0, 5).map((person) => <li key={person.person_id}>{person.display_name} <StatusChip tone="information">{person.combined_count}</StatusChip></li>)}{data.fairness.underloaded_people.length === 0 ? <li>{t("workloadDashboard.empty.noUnderloadedPeople")}</li> : null}</ul></div>
              </div>
            </Card>
          </section>

          <Card title={t("workloadDashboard.details.title")} subtitle={t("workloadDashboard.details.description")}>
            <DataTable
              columns={personColumns}
              rows={sortedPeople}
              rowKey={(person) => person.personId}
              compact
              sortKey={sortKey}
              sortDirection={sortDirection}
              onSort={handleSort}
              maxHeight={520}
              scrollThreshold={12}
              emptyTitle={t("workloadDashboard.empty.noPersonData")}
            />
          </Card>
        </>
      )}
    </div>
  );
}
