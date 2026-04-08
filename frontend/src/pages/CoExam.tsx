import { useCallback } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { useAsyncData } from "@/hooks/useAsyncData";
import { autoDetectCoExam, listCoExamGroups } from "@/services/coexam.service";
import { useUi } from "@/store/ui.store";
import { formatNumber } from "@/utils/format";

export function CoExamPage() {
  const { toast } = useUi();
  const loader = useCallback(() => listCoExamGroups(), []);
  const state = useAsyncData(loader, [loader]);

  const handleAutoDetect = async () => {
    try {
      const response = await autoDetectCoExam();
      toast(`ตรวจพบ ${response.count} กลุ่มที่น่าจะรวมสอบร่วม`, "info");
    } catch (err) {
      toast(err instanceof Error ? err.message : "ตรวจหากลุ่มไม่สำเร็จ", "error");
    }
  };

  if (!state.data || state.data.length === 0) {
    return (
      <Card title="Co-Exam Groups" actions={<Button type="button" onClick={() => void handleAutoDetect()}>ตรวจหาอัตโนมัติ</Button>}>
        <EmptyState icon="🔗" title="ยังไม่มีกลุ่ม Co-Exam" />
      </Card>
    );
  }

  return (
    <div className="page-stack">
      <Card title="Co-Exam Groups" actions={<Button type="button" onClick={() => void handleAutoDetect()}>ตรวจหาอัตโนมัติ</Button>} />
      {state.data.map((group) => (
        <Card
          key={group.id}
          title={group.label}
          subtitle={`${group.exam_date} • ${group.exam_time}`}
        >
          <p>นักศึกษารวม {formatNumber(group.total_students)} คน</p>
          <div className="tag-list">
            {group.members.map((member) => (
              <span key={`${group.id}-${member.section_id}`} className="tag-list__item">
                {member.course_id}-{member.section_no}
              </span>
            ))}
          </div>
        </Card>
      ))}
    </div>
  );
}
