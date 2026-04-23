import { useCallback, useEffect, useMemo, useState } from "react";

import { OwnershipEditorModal } from "@/components/exam-manager/OwnershipEditorModal";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { useI18n } from "@/i18n";
import {
  getExamManagerOverview,
  updateSectionOwnership,
  type ExamManagerOverviewItem,
  type OwnershipAssignmentItem,
  type ExamManagerOverviewResponse,
} from "@/services/exam-manager.service";
import { listTeachers } from "@/services/users.service";
import { useAuth } from "@/store/auth.store";
import { usePeriod } from "@/store/period.store";
import { useUi } from "@/store/ui.store";
import type { UserOut } from "@/types/api";

function assignmentTone(assignment?: OwnershipAssignmentItem | null) {
  const status = assignment?.assignment_status;
  if (status === "manual_assigned") {
    return "navy" as const;
  }
  if (status === "auto_assigned") {
    return "green" as const;
  }
  if (status === "pending") {
    return "gold" as const;
  }
  return "gray" as const;
}

export function ExamManagerPage() {
  const { t } = useI18n();
  const { user } = useAuth();
  const { activePeriod } = usePeriod();
  const { toast } = useUi();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [query, setQuery] = useState("");
  const [overview, setOverview] = useState<ExamManagerOverviewResponse | null>(null);
  const [teachers, setTeachers] = useState<UserOut[]>([]);
  const [selectedRow, setSelectedRow] = useState<ExamManagerOverviewItem | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [overviewData, teacherData] = await Promise.all([
        getExamManagerOverview({
          semester: activePeriod?.semester,
          academic_year: activePeriod?.academic_year,
        }),
        listTeachers(),
      ]);
      setOverview(overviewData);
      setTeachers(teacherData);
    } catch (err) {
      toast(err instanceof Error ? err.message : t("errors.unexpected"), "error");
    } finally {
      setLoading(false);
    }
  }, [activePeriod?.academic_year, activePeriod?.semester, t, toast]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const filteredRows = useMemo(() => {
    const rows = overview?.sections ?? [];
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) {
      return rows;
    }

    return rows.filter((row) =>
      [
        row.course_id,
        row.course_name,
        row.section_no,
        row.department,
        row.main_teacher,
        ...row.imported_teachers.map((teacher) => teacher.full_name ?? teacher.email ?? ""),
        row.midterm?.manager_name,
        row.final?.manager_name,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(normalizedQuery),
    );
  }, [overview?.sections, query]);

  const handleSaveOwnership = async (payload: { midterm_manager_id?: number | null; final_manager_id?: number | null }) => {
    if (!selectedRow) {
      return;
    }

    setSaving(true);
    try {
      await updateSectionOwnership(selectedRow.section_id, payload);
      toast(t("ownership.toastSaved"), "success");
      setSelectedRow(null);
      await loadData();
    } catch (err) {
      toast(err instanceof Error ? err.message : t("errors.unexpected"), "error");
      throw err;
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">{t("ownership.heroEyebrow")}</span>
          <h1 className="page-hero__title">{t("ownership.heroTitle")}</h1>
          <p className="page-hero__description">
            {t("ownership.heroDescription", {
              role: user?.role === "dept_supervisor" ? t("roles.dept_supervisor") : t("roles.admin"),
            })}
          </p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => void loadData()}>
            {t("common.refresh")}
          </Button>
        </div>
      </section>

      <div className="summary-grid">
        <div className="summary-box">
          <span>{t("ownership.stats.total")}</span>
          <strong>{overview?.total ?? 0}</strong>
        </div>
        <div className="summary-box">
          <span>{t("ownership.stats.ready")}</span>
          <strong>{overview?.ready_count ?? 0}</strong>
        </div>
        <div className="summary-box summary-box--warning">
          <span>{t("ownership.stats.needsAttention")}</span>
          <strong>{overview?.needs_attention_count ?? 0}</strong>
        </div>
        <div className="summary-box">
          <span>{t("ownership.stats.auto")}</span>
          <strong>{overview?.auto_assigned_count ?? 0}</strong>
        </div>
        <div className="summary-box">
          <span>{t("ownership.stats.manual")}</span>
          <strong>{overview?.manual_assigned_count ?? 0}</strong>
        </div>
      </div>

      <Card
        title={t("ownership.tableTitle")}
        subtitle={t("ownership.tableSubtitle", {
          term: activePeriod?.label ?? `${overview?.semester ?? "-"} / ${overview?.academic_year ?? "-"}`,
        })}
        actions={
          <label className="filter-field">
            <span>{t("common.search")}</span>
            <input
              value={query}
              onChange={(event) => setQuery(event.currentTarget.value)}
              placeholder={t("ownership.searchPlaceholder")}
            />
          </label>
        }
      >
        {loading ? (
          <p>{t("common.loading")}...</p>
        ) : filteredRows.length === 0 ? (
          <EmptyState
            icon={<Icon name="assignment" />}
            title={t("ownership.emptyTitle")}
            description={t("ownership.emptyDescription")}
          />
        ) : (
          <DataTable<ExamManagerOverviewItem>
            columns={[
              {
                key: "course",
                label: t("ownership.table.course"),
                width: "260px",
                minWidth: "220px",
                render: (row) => (
                  <div>
                    <strong>{row.course_id}</strong>
                    <p>{row.course_name}</p>
                  </div>
                ),
              },
              {
                key: "section",
                label: t("ownership.table.section"),
                width: "160px",
                minWidth: "150px",
                render: (row) => (
                  <div>
                    <strong>{row.section_no}</strong>
                    <p>{row.department ?? t("common.notRecorded")}</p>
                  </div>
                ),
              },
              {
                key: "imported_teachers",
                label: t("ownership.table.importedTeachers"),
                width: "220px",
                minWidth: "190px",
                render: (row) => (
                  <div>
                    {row.imported_teachers.length > 0 ? (
                      row.imported_teachers.map((teacher) => (
                        <p key={teacher.id}>{teacher.full_name ?? teacher.email ?? "-"}</p>
                      ))
                    ) : (
                      <span>{t("ownership.emptyImportedTeachers")}</span>
                    )}
                  </div>
                ),
              },
              {
                key: "midterm",
                label: t("ownership.table.midtermOwner"),
                width: "210px",
                minWidth: "180px",
                render: (row) => (
                  <div>
                    <strong>{row.midterm?.manager_name ?? t("ownership.unassigned")}</strong>
                    <p>
                      <Badge variant={assignmentTone(row.midterm)} size="sm">
                        {t(`ownership.status.${row.midterm?.assignment_status ?? "needs_attention"}`)}
                      </Badge>
                    </p>
                  </div>
                ),
              },
              {
                key: "final",
                label: t("ownership.table.finalOwner"),
                width: "210px",
                minWidth: "180px",
                render: (row) => (
                  <div>
                    <strong>{row.final?.manager_name ?? t("ownership.unassigned")}</strong>
                    <p>
                      <Badge variant={assignmentTone(row.final)} size="sm">
                        {t(`ownership.status.${row.final?.assignment_status ?? "needs_attention"}`)}
                      </Badge>
                    </p>
                  </div>
                ),
              },
              {
                key: "status",
                label: t("ownership.table.status"),
                width: "140px",
                minWidth: "130px",
                render: (row) => (
                  <Badge variant={row.needs_attention ? "gold" : "green"}>
                    {row.needs_attention ? t("ownership.status.needs_attention") : t("ownership.status.ready")}
                  </Badge>
                ),
              },
              {
                key: "actions",
                label: t("common.actions"),
                width: "120px",
                minWidth: "110px",
                render: (row) => (
                  <Button size="sm" type="button" variant="outline" onClick={() => setSelectedRow(row)}>
                    {t("common.edit")}
                  </Button>
                ),
              },
            ]}
            rows={filteredRows}
            rowKey={(row) => row.section_id}
            compact
            tableLayout="fixed"
            scrollThreshold={5}
            maxHeight={520}
            emptyTitle={t("ownership.emptyTitle")}
            emptyDescription={t("ownership.emptyDescription")}
          />
        )}
      </Card>

      <OwnershipEditorModal
        open={selectedRow !== null}
        row={selectedRow}
        teachers={teachers}
        saving={saving}
        onClose={() => setSelectedRow(null)}
        onSave={handleSaveOwnership}
      />
    </div>
  );
}
