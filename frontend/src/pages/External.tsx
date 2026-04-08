import { useCallback } from "react";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { useAsyncData } from "@/hooks/useAsyncData";
import { listExternalExams } from "@/services/external.service";
import { formatDateRange, formatNumber } from "@/utils/format";

export function ExternalPage() {
  const loader = useCallback(() => listExternalExams(), []);
  const state = useAsyncData(loader, [loader]);

  if (!state.data || state.data.length === 0) {
    return <EmptyState icon="🏛️" title="ยังไม่มีสอบพิเศษ" />;
  }

  return (
    <div className="page-stack">
      {state.data.map((exam) => (
        <Card
          key={exam.id}
          title={exam.title ?? "External Exam"}
          subtitle={formatDateRange(exam.exam_date, exam.exam_time)}
          actions={<Badge variant={exam.status === "draft" ? "gold" : "green"}>{exam.status ?? "draft"}</Badge>}
        >
          <div className="summary-grid">
            <div className="summary-box">
              <span>ห้องสอบ</span>
              <strong>{exam.room_name ?? "-"}</strong>
            </div>
            <div className="summary-box">
              <span>ผู้เข้าสอบ</span>
              <strong>{formatNumber(exam.num_students ?? 0)}</strong>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
