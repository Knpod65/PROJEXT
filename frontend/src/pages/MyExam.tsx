import { useCallback } from "react";

import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { useAsyncData } from "@/hooks/useAsyncData";
import { getMyExamManagerSections } from "@/services/exam-manager.service";
import { formatNumber } from "@/utils/format";

export function MyExamPage() {
  const loader = useCallback(() => getMyExamManagerSections(), []);
  const state = useAsyncData(loader, [loader]);
  const sections = state.data?.sections ?? [];

  if (sections.length === 0) {
    return <EmptyState icon="📋" title="ไม่มีวิชาที่มอบหมาย" />;
  }

  return (
    <div className="page-stack">
      {sections.map((section, index) => (
        <Card
          key={String(section.section_id ?? index)}
          title={`${section.course_id ?? "—"} ${section.course_name ?? ""}`}
          subtitle={`ตอน ${section.section_no ?? "-"} • ${formatNumber(Number(section.num_students ?? 0))} คน`}
        >
          <div className="summary-grid">
            <div className="summary-box">
              <span>Midterm Manager</span>
              <strong>{(section.midterm as { manager_name?: string } | null)?.manager_name ?? "-"}</strong>
            </div>
            <div className="summary-box">
              <span>Final Manager</span>
              <strong>{(section.final as { manager_name?: string } | null)?.manager_name ?? "-"}</strong>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
