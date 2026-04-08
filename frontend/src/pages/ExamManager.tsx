import { useCallback } from "react";

import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { useAsyncData } from "@/hooks/useAsyncData";
import { getExamManagerOverview, type ExamManagerOverviewItem } from "@/services/exam-manager.service";

export function ExamManagerPage() {
  const loader = useCallback(() => getExamManagerOverview(), []);
  const state = useAsyncData(loader, [loader]);

  return (
    <div className="page-stack">
      {state.data ? (
        <Card title="ภาพรวมการมอบหมาย">
          <div className="summary-grid">
            <div className="summary-box">
              <span>ทั้งหมด</span>
              <strong>{state.data.total}</strong>
            </div>
            <div className="summary-box">
              <span>มอบหมายแล้ว</span>
              <strong>{state.data.assigned}</strong>
            </div>
            <div className="summary-box">
              <span>คงเหลือ</span>
              <strong>{state.data.unassigned}</strong>
            </div>
          </div>
        </Card>
      ) : null}

      <DataTable<ExamManagerOverviewItem>
        columns={[
          { key: "course_id", label: "วิชา" },
          { key: "course_name", label: "ชื่อวิชา" },
          { key: "section_no", label: "ตอน" },
          { key: "teacher_name", label: "อาจารย์" },
          { key: "manager_name", label: "Exam Manager" },
          {
            key: "confirmed",
            label: "สถานะ",
            render: (row) => (row.confirmed ? "confirmed" : "pending"),
          },
        ]}
        emptyTitle="ยังไม่มีการมอบหมาย"
        loading={state.loading}
        rowKey={(row) => row.id}
        rows={state.data?.sections ?? []}
      />
    </div>
  );
}
