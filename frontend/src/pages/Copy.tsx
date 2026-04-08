import { useCallback } from "react";

import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { getCopyCount } from "@/services/schedule.service";
import { useAsyncData } from "@/hooks/useAsyncData";
import type { CopyCountSummary } from "@/types/api";
import { formatCurrency, formatNumber } from "@/utils/format";

type CopyRow = CopyCountSummary["rows"][number];

export function CopyPage() {
  const loader = useCallback(() => getCopyCount(), []);
  const { data, loading } = useAsyncData(loader, [loader]);

  return (
    <div className="page-stack">
      <Card title="สรุปค่าถ่ายเอกสาร">
        <div className="summary-grid">
          <div className="summary-box">
            <span>แผ่นข้อสอบรวม</span>
            <strong>{formatNumber(data?.grand_total ?? 0)}</strong>
          </div>
          <div className="summary-box">
            <span>ค่าใช้จ่ายรวม</span>
            <strong>{formatCurrency(data?.cost ?? 0)}</strong>
          </div>
          <div className="summary-box">
            <span>ส่วนเผื่อแบบฟอร์มทุจริต</span>
            <strong>{formatNumber(data?.fraud_forms ?? 0)}</strong>
          </div>
        </div>
      </Card>

      <DataTable<CopyRow>
        columns={[
          { key: "course_id", label: "วิชา" },
          { key: "course_name_th", label: "ชื่อวิชา" },
          { key: "section_no", label: "ตอน" },
          { key: "num_students", label: "นศ." },
          { key: "num_pages", label: "หน้า" },
          { key: "total_sheets", label: "แผ่น" },
          { key: "room", label: "ห้อง" },
        ]}
        emptyTitle="ยังไม่มีข้อมูลค่าถ่าย"
        loading={loading}
        rowKey={(row) => `${row.course_id}-${row.section_no}`}
        rows={data?.rows ?? []}
      />
    </div>
  );
}
