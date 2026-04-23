import { useCallback } from "react";

import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { useAsyncData } from "@/hooks/useAsyncData";
import { listSections } from "@/services/sections.service";
import type { SectionOut } from "@/types/api";
import { getAcademicGroupFromCourseId, getAcademicGroupLabel } from "@/utils/academicGroups";

function resolveAcademicGroup(section: SectionOut) {
  return (
    section.academic_group_label ??
    getAcademicGroupLabel(section.academic_group) ??
    getAcademicGroupLabel(section.course?.academic_group) ??
    getAcademicGroupLabel(getAcademicGroupFromCourseId(section.course?.course_id)) ??
    "Unmapped"
  );
}

export function SectionsPage() {
  const loader = useCallback(() => listSections(), []);
  const { data, loading } = useAsyncData(loader, [loader]);

  return (
    <Card
      title="Sections"
      subtitle="Academic section visibility now follows the shared course-prefix grouping rules."
    >
      <DataTable<SectionOut>
        columns={[
          {
            key: "course.course_id",
            label: "Course",
            width: "12%",
            render: (row) => <strong>{row.course?.course_id ?? "-"}</strong>,
          },
          {
            key: "course.course_name_th",
            label: "Course Name",
            width: "24%",
          },
          {
            key: "section_no",
            label: "Section",
            width: "9%",
            align: "center",
          },
          {
            key: "academic_group_label",
            label: "Academic Group",
            width: "16%",
            render: (row) => resolveAcademicGroup(row),
          },
          {
            key: "teacher.full_name",
            label: "Teacher",
            width: "22%",
            render: (row) => row.teacher?.full_name ?? "-",
          },
          {
            key: "teaching_room.room_name",
            label: "Teaching Room",
            width: "9%",
            render: (row) => row.teaching_room?.room_name ?? "-",
          },
          {
            key: "num_students",
            label: "Students",
            width: "8%",
            align: "right",
          },
        ]}
        emptyDescription="No sections are available for the active visibility scope."
        loading={loading}
        rowKey={(row) => row.id}
        rows={data ?? []}
        scrollThreshold={5}
        tableLayout="fixed"
      />
    </Card>
  );
}
