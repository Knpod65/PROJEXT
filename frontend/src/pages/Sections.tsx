import { useCallback } from "react";

import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { PageHeader } from "@/components/ui/PageHeader";
import { useAsyncData } from "@/hooks/useAsyncData";
import { useI18n } from "@/i18n";
import { listSections } from "@/services/sections.service";
import type { SectionOut } from "@/types/api";
import { getAcademicGroupFromCourseId, getAcademicGroupLabel } from "@/utils/academicGroups";

function resolveAcademicGroup(section: SectionOut, fallback: string) {
  return (
    section.academic_group_label ??
    getAcademicGroupLabel(section.academic_group) ??
    getAcademicGroupLabel(section.course?.academic_group) ??
    getAcademicGroupLabel(getAcademicGroupFromCourseId(section.course?.course_id)) ??
    fallback
  );
}

export function SectionsPage() {
  const { t } = useI18n();
  const loader = useCallback(() => listSections(), []);
  const { data, loading } = useAsyncData(loader, [loader]);

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        eyebrow={t("navigation.groups.examManagement")}
        title={t("navigation.pages.sections.title")}
        description={t("navigation.pages.sections.description")}
      />
      <Card title={t("sections.title")} subtitle={t("sections.subtitle")}>
        <DataTable<SectionOut>
        columns={[
          {
            key: "course.course_id",
            label: t("common.course"),
            width: "12%",
            render: (row) => <strong>{row.course?.course_id ?? "-"}</strong>,
          },
          {
            key: "course.course_name_th",
            label: t("sections.table.courseName"),
            width: "24%",
          },
          {
            key: "section_no",
            label: t("common.section"),
            width: "9%",
            align: "center",
          },
          {
            key: "academic_group_label",
            label: t("sections.table.academicGroup"),
            width: "16%",
            render: (row) => resolveAcademicGroup(row, t("sections.table.unmapped")),
          },
          {
            key: "teacher.full_name",
            label: t("sections.table.teacher"),
            width: "22%",
            render: (row) => row.teacher?.full_name ?? "-",
          },
          {
            key: "teaching_room.room_name",
            label: t("schedule.table.teachingRoom"),
            width: "9%",
            render: (row) => row.teaching_room?.room_name ?? "-",
          },
          {
            key: "num_students",
            label: t("common.students"),
            width: "8%",
            align: "right",
          },
        ]}
        emptyDescription={t("sections.emptyDescription")}
        loading={loading}
        rowKey={(row) => row.id}
        rows={data ?? []}
        scrollThreshold={5}
        tableLayout="fixed"
        />
      </Card>
    </div>
  );
}
