import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { DataTable } from "@/components/ui/DataTable";
import type { SwapRequestV2, SwapsViewRole } from "@/hooks/useSwapsData";

interface SwapRequestTableProps {
  mode: SwapsViewRole;
  rows: SwapRequestV2[];
  onApprove: (id: number) => void;
  onReject: (id: number) => void;
  onEscalate: (id: number) => void;
  onWithdraw: (id: number) => void;
}

function statusVariant(status: SwapRequestV2["status"]) {
  switch (status) {
    case "approved":
      return "green" as const;
    case "rejected":
      return "crimson" as const;
    case "escalated":
      return "orange" as const;
    default:
      return "gold" as const;
  }
}

function priorityVariant(priority: SwapRequestV2["priority"]) {
  switch (priority) {
    case "high":
      return "crimson" as const;
    case "medium":
      return "gold" as const;
    default:
      return "gray" as const;
  }
}

export function SwapRequestTable({ mode, onApprove, onEscalate, onReject, onWithdraw, rows }: SwapRequestTableProps) {
  const showPriority = mode !== "teacher";
  const showScope = mode === "admin";

  return (
    <DataTable<SwapRequestV2>
      columns={[
        {
          key: "requester",
          label: "Requester",
          render: (row) => (
            <div>
              <strong>{row.requester}</strong>
              <p>Target: {row.target}</p>
            </div>
          ),
        },
        {
          key: "course_slot",
          label: mode === "teacher" ? "My Exam Slot" : "Exam Slot",
          render: (row) => (
            <div>
              <strong>{row.course}</strong>
              <p>
                {row.examDate} • {row.examTime}
              </p>
              <p>{row.room}</p>
            </div>
          ),
        },
        {
          key: "status",
          label: "Status",
          render: (row) => <Badge variant={statusVariant(row.status)}>{row.status}</Badge>,
        },
        ...(showPriority
          ? [
              {
                key: "priority",
                label: "Priority",
                render: (row: SwapRequestV2) => <Badge variant={priorityVariant(row.priority)}>{row.priority}</Badge>,
              },
            ]
          : []),
        ...(showScope
          ? [
              {
                key: "scope",
                label: "Scope",
                render: (row: SwapRequestV2) => <span>{row.scope}</span>,
              },
            ]
          : []),
        {
          key: "requestedAt",
          label: "Requested",
          render: (row) => <span>{row.requestedAt}</span>,
        },
        {
          key: "actions",
          label: "Actions",
          render: (row) => {
            if (row.status !== "pending") {
              return <span>-</span>;
            }

            if (mode === "teacher") {
              return (
                <div className="swap-card__actions">
                  <Button size="sm" type="button" variant="ghost" onClick={() => onWithdraw(row.id)}>
                    Withdraw
                  </Button>
                </div>
              );
            }

            return (
              <div className="swap-card__actions">
                <Button size="sm" type="button" onClick={() => onApprove(row.id)}>
                  Approve
                </Button>
                <Button size="sm" type="button" variant="outline" onClick={() => onReject(row.id)}>
                  Reject
                </Button>
                {mode === "admin" ? (
                  <Button size="sm" type="button" variant="ghost" onClick={() => onEscalate(row.id)}>
                    Escalate
                  </Button>
                ) : null}
              </div>
            );
          },
        },
      ]}
      rows={rows}
      rowKey={(row) => row.id}
      emptyTitle="No swap requests matched"
      emptyDescription="Try changing filters or clear the search query."
    />
  );
}
