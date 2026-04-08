import { useCallback } from "react";

import { DataTable } from "@/components/ui/DataTable";
import { useAsyncData } from "@/hooks/useAsyncData";
import { listImportSessions } from "@/services/import.service";
import type { ImportSession } from "@/types/api";

export function ImportPage() {
  const loader = useCallback(() => listImportSessions(), []);
  const state = useAsyncData(loader, [loader]);

  return (
    <DataTable<ImportSession>
      columns={[
        { key: "id", label: "Session" },
        { key: "academic_year", label: "ปีการศึกษา" },
        { key: "semester", label: "ภาค" },
        { key: "exam_type", label: "ประเภทสอบ" },
        { key: "opencourse_rows", label: "OpenCourse" },
        { key: "enrollment_rows", label: "Enrollment" },
      ]}
      emptyTitle="ยังไม่มีประวัติการนำเข้า"
      loading={state.loading}
      rowKey={(row) => row.id}
      rows={state.data ?? []}
    />
  );
}
