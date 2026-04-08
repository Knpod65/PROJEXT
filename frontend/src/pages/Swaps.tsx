import { useCallback, useEffect, useMemo, useState } from "react";

import { SwapCard } from "@/components/swaps/SwapCard";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs } from "@/components/ui/Tabs";
import { cancelSwap, getMySwaps, getWaitingSwaps, respondSwap } from "@/services/swap.service";
import type { SwapItem } from "@/types/api";
import { useUi } from "@/store/ui.store";

export function SwapsPage() {
  const { toast } = useUi();
  const [activeTab, setActiveTab] = useState("waiting");
  const [mySwaps, setMySwaps] = useState<SwapItem[]>([]);
  const [waiting, setWaiting] = useState<SwapItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [myItems, waitingItems] = await Promise.all([getMySwaps(), getWaitingSwaps()]);
      setMySwaps(myItems);
      setWaiting(waitingItems);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const tabs = useMemo(
    () => [
      { key: "waiting", label: "รอตอบ", badge: waiting.length },
      { key: "mine", label: "ของฉัน", badge: mySwaps.length },
      { key: "all", label: "ทั้งหมด", badge: waiting.length + mySwaps.length },
    ],
    [mySwaps.length, waiting.length],
  );

  const visibleItems = useMemo(() => {
    if (activeTab === "waiting") return waiting;
    if (activeTab === "mine") return mySwaps;
    return [...waiting, ...mySwaps];
  }, [activeTab, mySwaps, waiting]);

  const handleRespond = async (swapId: number, accept: boolean) => {
    try {
      await respondSwap(swapId, accept);
      toast(accept ? "ตอบรับคำขอสลับแล้ว" : "ปฏิเสธคำขอสลับแล้ว", "success");
      await loadData();
    } catch (err) {
      toast(err instanceof Error ? err.message : "อัปเดตคำขอไม่สำเร็จ", "error");
    }
  };

  const handleCancel = async (swapId: number) => {
    try {
      await cancelSwap(swapId);
      toast("ยกเลิกคำขอสลับแล้ว", "info");
      await loadData();
    } catch (err) {
      toast(err instanceof Error ? err.message : "ยกเลิกคำขอไม่สำเร็จ", "error");
    }
  };

  return (
    <div className="page-stack">
      <Card
        title="การสลับกะ"
        actions={
          <Button type="button" variant="outline" disabled>
            ฟอร์มขอสลับจะต่อจาก supervision จริงในรอบถัดไป
          </Button>
        }
      >
        <Tabs activeKey={activeTab} items={tabs} onChange={setActiveTab} />
      </Card>

      {loading ? (
        <div className="page-stack">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="card-skeleton" />
          ))}
        </div>
      ) : visibleItems.length === 0 ? (
        <EmptyState icon="🔄" title="ไม่มีคำขอสลับ" />
      ) : (
        <div className="page-stack">
          {visibleItems.map((item) => (
            <SwapCard
              key={item.id}
              item={item}
              onAccept={activeTab !== "mine" && item.status === "pending" ? () => void handleRespond(item.id, true) : undefined}
              onReject={activeTab !== "mine" && item.status === "pending" ? () => void handleRespond(item.id, false) : undefined}
              onCancel={activeTab !== "waiting" && item.status === "pending" ? () => void handleCancel(item.id) : undefined}
            />
          ))}
        </div>
      )}
    </div>
  );
}
