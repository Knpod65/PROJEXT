import { useCallback } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { useAsyncData } from "@/hooks/useAsyncData";
import {
  getWorkflowSession,
  initWorkflowSession,
  listWorkflowSigners,
  openSwapWindow,
  signWorkflow,
} from "@/services/workflow.service";
import { useUi } from "@/store/ui.store";

export function WorkflowPage() {
  const { toast } = useUi();
  const sessionLoader = useCallback(() => getWorkflowSession(), []);
  const signersLoader = useCallback(() => listWorkflowSigners(), []);
  const sessionState = useAsyncData(sessionLoader, [sessionLoader]);
  const signersState = useAsyncData(signersLoader, [signersLoader]);

  const runAction = async (action: () => Promise<unknown>, message: string) => {
    try {
      await action();
      toast(message, "success");
      await Promise.all([sessionState.reload(), signersState.reload()]);
    } catch (err) {
      toast(err instanceof Error ? err.message : "ดำเนินการไม่สำเร็จ", "error");
    }
  };

  if (!sessionState.data) {
    return (
      <Card title="Workflow Session">
        <EmptyState icon="🖊" title="ยังไม่มี workflow session" />
        <Button type="button" onClick={() => void runAction(initWorkflowSession, "สร้าง workflow session แล้ว")}>
          เริ่ม session
        </Button>
      </Card>
    );
  }

  const session = sessionState.data;

  return (
    <div className="page-stack">
      <Card
        title="สถานะ Workflow"
        subtitle={`status: ${session.status}`}
        actions={<Badge variant={session.status === "locked" ? "gold" : "green"}>{session.status}</Badge>}
      >
        <div className="summary-grid">
          <div className="summary-box">
            <span>Round 1</span>
            <strong>{session.round1 ? `${session.round1.done}/${session.round1.total}` : "-"}</strong>
          </div>
          <div className="summary-box">
            <span>Round 2</span>
            <strong>{session.round2 ? `${session.round2.done}/${session.round2.total}` : "-"}</strong>
          </div>
        </div>
        <div className="inline-actions">
          <Button type="button" variant="outline" onClick={() => void runAction(() => signWorkflow(1), "ลงนามรอบที่ 1 แล้ว")}>
            ลงนามรอบ 1
          </Button>
          <Button type="button" variant="outline" onClick={() => void runAction(() => signWorkflow(2), "ลงนามรอบที่ 2 แล้ว")}>
            ลงนามรอบ 2
          </Button>
          <Button type="button" variant="gold" onClick={() => void runAction(openSwapWindow, "เปิด swap window แล้ว")}>
            เปิด Swap
          </Button>
        </div>
      </Card>

      <Card title="ผู้ลงนาม">
        <div className="signer-list">
          {(signersState.data ?? []).map((signer) => (
            <div key={`${signer.order}-${signer.username}`} className="signer-list__item">
              <strong>{signer.full_name}</strong>
              <span>{signer.username}</span>
              {signer.is_me ? <Badge variant="blue">คุณ</Badge> : null}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
