import { useState } from "react";

import { SwapFilters } from "@/components/swaps/SwapFilters";
import { SwapRequestTable } from "@/components/swaps/SwapRequestTable";
import { SwapStatsCards } from "@/components/swaps/SwapStatsCards";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { useSwapsData } from "@/hooks/useSwapsData";
import { useAuth } from "@/store/auth.store";
import { useUi } from "@/store/ui.store";
import { getEffectiveRole } from "@/utils/roles";

function roleCopy(viewRole: "admin" | "staff" | "teacher") {
  if (viewRole === "teacher") {
    return {
      eyebrow: "Teacher swaps",
      title: "My swap requests",
      description: "Simple request and status tracking view for teacher-side swap coordination.",
      cardSubtitle: "Teacher mode: simple request tracking and withdraw action",
      primaryAction: "Create Request",
    };
  }

  if (viewRole === "staff") {
    return {
      eyebrow: "Staff resolution queue",
      title: "Department swap queue",
      description: "Operational review mode for approving or rejecting pending swap requests.",
      cardSubtitle: "Staff mode: queue triage and resolution actions",
      primaryAction: "Refresh Queue",
    };
  }

  return {
    eyebrow: "Admin swap command",
    title: "System-wide swap management",
    description: "Stitch-based admin oversight view for queue triage, staffing risk checks, and final actions.",
    cardSubtitle: "Preview mode — actions update local state only, no API calls are made",
    primaryAction: "Export Queue",
  };
}

export function SwapsV2Page() {
  const { toast } = useUi();
  const { user } = useAuth();
  const role = getEffectiveRole(user);
  const {
    approveSwap,
    escalateSwap,
    priorityFilter,
    query,
    requestSwap,
    rejectSwap,
    resetFilters,
    rows,
    setPriorityFilter,
    setQuery,
    setStatusFilter,
    stats,
    statusFilter,
    viewRole,
    withdrawSwap,
  } = useSwapsData(role);

  const content = roleCopy(viewRole);

  const [pendingAction, setPendingAction] = useState<{ id: number; action: "approve" | "reject" } | null>(null);

  // Approve and reject are irreversible status changes — require confirmation.
  const handleApprove = (id: number) => setPendingAction({ id, action: "approve" });
  const handleReject = (id: number) => setPendingAction({ id, action: "reject" });

  const handleConfirmAction = () => {
    if (!pendingAction) return;
    if (pendingAction.action === "approve") {
      approveSwap(pendingAction.id);
      toast(`Approved swap request #${pendingAction.id}`, "success");
    } else {
      rejectSwap(pendingAction.id);
      toast(`Rejected swap request #${pendingAction.id}`, "warning");
    }
    setPendingAction(null);
  };

  const handleEscalate = (id: number) => {
    escalateSwap(id);
    toast(`Escalated swap request #${id} for review`, "info");
  };

  const handleWithdraw = (id: number) => {
    withdrawSwap(id);
    toast(`Withdrawn swap request #${id}`, "warning");
  };

  const handlePrimaryAction = () => {
    if (viewRole === "teacher") {
      requestSwap();
      toast("Created a new test swap request", "success");
      return;
    }

    toast("Queue refreshed by filters", "info");
  };

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">{content.eyebrow}</span>
          <h1 className="page-hero__title">{content.title}</h1>
          <p className="page-hero__description">{content.description}</p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={resetFilters}>
            Clear Filters
          </Button>
          <Button type="button" onClick={handlePrimaryAction}>{content.primaryAction}</Button>
        </div>
      </section>

      <SwapStatsCards mode={viewRole} stats={stats} />

      <SwapFilters
        query={query}
        statusFilter={statusFilter}
        priorityFilter={priorityFilter}
        onQueryChange={setQuery}
        onStatusChange={setStatusFilter}
        onPriorityChange={setPriorityFilter}
        onReset={resetFilters}
      />

      <Card
        title="Swap Request Queue"
        subtitle={content.cardSubtitle}
      >
        <SwapRequestTable
          mode={viewRole}
          rows={rows}
          onApprove={handleApprove}
          onReject={handleReject}
          onEscalate={handleEscalate}
          onWithdraw={handleWithdraw}
        />
      </Card>

      <ConfirmDialog
        open={pendingAction !== null}
        title={pendingAction?.action === "approve" ? "Approve swap request" : "Reject swap request"}
        description={
          pendingAction?.action === "approve"
            ? `Approving swap request #${pendingAction?.id} will confirm the coverage change. This action updates the record status and cannot be undone from this view.`
            : `Rejecting swap request #${pendingAction?.id} will notify the requester and close the request. This action cannot be undone from this view.`
        }
        confirmLabel={pendingAction?.action === "approve" ? "Approve" : "Reject"}
        variant={pendingAction?.action === "approve" ? "primary" : "danger"}
        onConfirm={handleConfirmAction}
        onCancel={() => setPendingAction(null)}
      />
    </div>
  );
}
