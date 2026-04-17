import { StudentEnrollmentFlow } from "@/components/students/StudentEnrollmentFlow";
import { StudentFilters } from "@/components/students/StudentFilters";
import { StudentImportPlaceholder } from "@/components/students/StudentImportPlaceholder";
import { StudentStatsCards } from "@/components/students/StudentStatsCards";
import { StudentsTableV2 } from "@/components/students/StudentsTableV2";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useStudentsData } from "@/hooks/useStudentsData";
import { useUi } from "@/store/ui.store";

export function StudentsV2Page() {
  const { toast } = useUi();
  const {
    faculties,
    facultyFilter,
    flow,
    query,
    resetFilters,
    rows,
    setFacultyFilter,
    setQuery,
    setStageFilter,
    stageFilter,
    stats,
  } = useStudentsData();

  const showImportPlaceholder = () => {
    toast("Excel import is a Milestone 5 UI placeholder only.", "info");
  };

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">Admin Student Management (V2)</span>
          <h1 className="page-hero__title">Student enrollment operations</h1>
          <p className="page-hero__description">
            Stitch-based first-enrollment management view with import placeholder, search filters, and enrollment flow tracking.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={showImportPlaceholder}>Import from Excel</Button>
          <Button type="button" onClick={() => toast("Add single student is preview-only in Milestone 5.", "info")}>Add Single Student</Button>
        </div>
      </section>

      <StudentStatsCards stats={stats} />

      <div className="dashboard-shell-grid">
        <StudentImportPlaceholder onImportClick={showImportPlaceholder} />
        <StudentEnrollmentFlow flow={flow} />
      </div>

      <StudentFilters
        query={query}
        facultyFilter={facultyFilter}
        stageFilter={stageFilter}
        faculties={faculties}
        onQueryChange={setQuery}
        onFacultyChange={setFacultyFilter}
        onStageChange={setStageFilter}
        onReset={resetFilters}
      />

      <Card title="Registered Students" subtitle="Mock enrollment records for UI validation">
        <StudentsTableV2 rows={rows} />
      </Card>
    </div>
  );
}
