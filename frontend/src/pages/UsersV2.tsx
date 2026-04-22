import { useState } from "react";

import { UserFilters } from "@/components/users/UserFilters";
import { UserRoleBreakdown } from "@/components/users/UserRoleBreakdown";
import { UserStatsCards } from "@/components/users/UserStatsCards";
import { UsersTableV2 } from "@/components/users/UsersTableV2";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { useUsersData } from "@/hooks/useUsersData";
import { useI18n } from "@/i18n";
import { logout } from "@/services/auth.service";
import { useAuth } from "@/store/auth.store";
import { useUi } from "@/store/ui.store";
import type { UserRole } from "@/types/api";
import { formatRole } from "@/utils/format";

export function UsersV2Page() {
  const { t } = useI18n();
  const { toast } = useUi();
  const { clearSession, user: currentUser } = useAuth();
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
    updateUserRole,
  } = useUsersData();

  const [pendingDeactivateId, setPendingDeactivateId] = useState<number | null>(null);
  const [deactivating, setDeactivating] = useState(false);
  const [savingRoleId, setSavingRoleId] = useState<number | null>(null);

  const handleDeactivate = (userId: number) => {
    setPendingDeactivateId(userId);
  };

  const handleConfirmDeactivate = async () => {
    if (pendingDeactivateId === null) return;
    setDeactivating(true);
    try {
      await deactivateUser(pendingDeactivateId);
      toast(t("users.toastDeactivated", { id: pendingDeactivateId }), "success");
      setPendingDeactivateId(null);
      await reload();
    } catch (err) {
      toast(err instanceof Error ? err.message : t("errors.unexpected"), "error");
    } finally {
      setDeactivating(false);
    }
  };

  const handlePreviewAction = (label: string) => {
    toast(t("users.previewAction", { label }), "info");
  };

  const handleRoleUpdate = async (userId: number, role: UserRole) => {
    setSavingRoleId(userId);
    try {
      await updateUserRole(userId, role);

      if (currentUser?.id === userId && currentUser.role !== role) {
        try {
          await logout();
        } catch {
          // The backend may already reject the old session after the role change.
        }

        toast(t("users.roleUpdatedCurrentSession", { role: formatRole(role) }), "success");
        clearSession();
        return;
      }

      toast(t("users.roleUpdated", { id: userId, role: formatRole(role) }), "success");
      await reload();
    } catch (err) {
      toast(err instanceof Error ? err.message : t("errors.unexpected"), "error");
      throw err;
    } finally {
      setSavingRoleId(null);
    }
  };

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">{t("users.heroEyebrow")}</span>
          <h1 className="page-hero__title">{t("users.heroTitle")}</h1>
          <p className="page-hero__description">{t("users.heroDescription")}</p>
          {error ? <p className="page-hero__description">{t("users.loadWarning", { message: error })}</p> : null}
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => handlePreviewAction(t("users.importExcel"))}>{t("users.importExcel")}</Button>
          <Button type="button" onClick={() => handlePreviewAction(t("users.addUser"))}>{t("users.addUser")}</Button>
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
        <Card title={t("users.registryTitle")} subtitle={t("users.registrySubtitle")}>
          <UsersTableV2
            rows={rows}
            savingRoleId={savingRoleId}
            onDeactivate={handleDeactivate}
            onUpdateRole={handleRoleUpdate}
          />
          {loading ? <p>{t("users.loading")}</p> : null}
        </Card>
        <UserRoleBreakdown rows={roleBreakdown} />
      </div>

      <ConfirmDialog
        open={pendingDeactivateId !== null}
        title={t("users.deactivateTitle")}
        description={t("users.deactivateDescription", { id: pendingDeactivateId ?? "-" })}
        confirmLabel={t("users.deactivateConfirm")}
        variant="danger"
        loading={deactivating}
        onConfirm={() => void handleConfirmDeactivate()}
        onCancel={() => setPendingDeactivateId(null)}
      />
    </div>
  );
}
