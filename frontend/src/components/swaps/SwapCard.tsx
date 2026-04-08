import type { SwapItem } from "@/types/api";
import { formatDateTime } from "@/utils/format";

import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";

function swapVariant(status: string) {
  switch (status) {
    case "approved":
      return "green";
    case "rejected":
      return "crimson";
    case "cancelled":
      return "gray";
    default:
      return "gold";
  }
}

interface SwapCardProps {
  item: SwapItem;
  onAccept?: () => void;
  onReject?: () => void;
  onCancel?: () => void;
}

export function SwapCard({ item, onAccept, onCancel, onReject }: SwapCardProps) {
  return (
    <Card
      className="swap-card"
      title={`${item.requester_name ?? "ผู้ขอ"} → ${item.target_name ?? "ผู้รับ"}`}
      subtitle={`สร้างเมื่อ ${formatDateTime(item.created_at)}`}
      actions={<Badge variant={swapVariant(item.status)}>{item.status}</Badge>}
    >
      <div className="swap-card__shifts">
        <div>
          <strong>กะของฉัน</strong>
          <p>{item.my_shift?.course ?? "—"}</p>
          <p>
            {item.my_shift?.date ?? "-"} • {item.my_shift?.time ?? "-"}
          </p>
        </div>
        <div>
          <strong>กะที่ต้องการสลับ</strong>
          <p>{item.their_shift?.course ?? "—"}</p>
          <p>
            {item.their_shift?.date ?? "-"} • {item.their_shift?.time ?? "-"}
          </p>
        </div>
      </div>
      {item.message ? <p className="swap-card__message">"{item.message}"</p> : null}
      <div className="swap-card__actions">
        {item.status === "pending" && onAccept ? (
          <Button size="sm" type="button" onClick={onAccept}>
            ยอมรับ
          </Button>
        ) : null}
        {item.status === "pending" && onReject ? (
          <Button size="sm" type="button" variant="outline" onClick={onReject}>
            ปฏิเสธ
          </Button>
        ) : null}
        {item.status === "pending" && onCancel ? (
          <Button size="sm" type="button" variant="ghost" onClick={onCancel}>
            ยกเลิกคำขอ
          </Button>
        ) : null}
      </div>
    </Card>
  );
}
