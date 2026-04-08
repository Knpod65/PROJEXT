import { useCallback } from "react";

import { DataTable } from "@/components/ui/DataTable";
import { listSections } from "@/services/sections.service";
import { useAsyncData } from "@/hooks/useAsyncData";
import type { SectionOut } from "@/types/api";

export function SectionsPage() {
  const loader = useCallback(() => listSections(), []);
  const { data, loading } = useAsyncData(loader, [loader]);

  return (
    <DataTable<SectionOut>
      columns={[
        { key: "course.course_id", label: "รหัสวิชา" },
        { key: "course.course_name_th", label: "ชื่อวิชา" },
        { key: "section_no", label: "ตอน" },
        { key: "teacher.full_name", label: "อาจารย์" },
        { key: "num_students", label: "นศ." },
      ]}
      emptyDescription="ยังไม่มีข้อมูล section ในรอบปัจจุบัน"
      loading={loading}
      rowKey={(row) => row.id}
      rows={data ?? []}
    />
  );
}
