import { useState } from "react";

import { UserFilters } from "@/components/users/UserFilters";
import { UserRoleBreakdown } from "@/components/users/UserRoleBreakdown";
import { UserStatsCards } from "@/components/users/UserStatsCards";
import { UsersTableV2 } from "@/components/users/UsersTableV2";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { useUsersData } from "@/hooks/useUsersData";
import { useUi } from "@/store/ui.store";

export function UsersV2Page() {
  const { toast } = useUi();
  const {
    activeFilter,
    deactivateUser,
    error,
    loading,
    query,
    reload,
    resetFilters,
    roleBreakdown,
    roleFilter,
    rows,
    setActiveFilter,
    setQuery,
    setRoleFilter,
    stats,
  } = useUsersData();

  const [pendingDeactivateId, setPendingDeactivateId] = useState<number | null>(null);
  const [deactivating, setDeactivating] = useState(false);

  const handleDeactivate = (userId: number) => {
    setPendingDeactivateId(userId);
  };

  const handleConfirmDeactivate = async () => {
    if (pendingDeactivateId === null) return;
    setDeactivating(true);
    try {
      await deactivateUser(pendingDeactivateId);
      toast(`Deactivated user #${pendingDeactivateId}`, "success");
      setPendingDeactivateId(null);
      await reload();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Unable to deactivate user", "error");
    } finally {
      setDeactivating(false);
    }
  };

  const handlePreviewAction = (label: string) => {
    toast(`${label} is a Milestone 4 preview action.`, "info");
  };

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">Admin User Management (V2)</span>
          <h1 className="page-hero__title">User management and role oversight</h1>
          <p className="page-hero__description">
            Stitch-based V2 user control surface for account visibility, role breakdown, and safe administrative actions.
          </p>
          {error ? <p className="page-hero__description">Data load warning: {error}</p> : null}
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => handlePreviewAction("Excel import")}>Import from Excel</Button>
          <Button type="button" onClick={() => handlePreviewAction("Create user")}>Add New User</Button>
        </div>
      </section>

      <UserStatsCards stats={stats} />

      <UserFilters
        query={query}
        roleFilter={roleFilter}
        activeFilter={activeFilter}
        onQueryChange={setQuery}
        onRoleChange={setRoleFilter}
        onActiveChange={setActiveFilter}
        onReset={resetFilters}
      />

      <div className="dashboard-shell-grid">
        <Card title="User Registry" subtitle="Read/write preview for account status management">
          <UsersTableV2 rows={rows} onDeactivate={handleDeactivate} />
          {loading ? <p>Loading users...</p> : null}
        </Card>
        <UserRoleBreakdown rows={roleBreakdown} />
      </div>

      <ConfirmDialog
        open={pendingDeactivateId !== null}
        title="Deactivate user"
        description={`This will immediately revoke access for user #${pendingDeactivateId}. The account can be reactivated, but the user will be signed out of any active sessions.`}
        confirmLabel="Deactivate"
        variant="danger"
        loading={deactivating}
        onConfirm={() => void handleConfirmDeactivate()}
        onCancel={() => setPendingDeactivateId(null)}
      />
    </div>
  );
}
