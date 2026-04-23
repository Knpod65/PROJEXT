import { useState } from "react";

import { UserEditorModal, type UserEditorValues } from "@/components/users/UserEditorModal";
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
import type { UserOut } from "@/types/api";
import { formatRole } from "@/utils/format";

type PendingAction =
  | { type: "status"; user: UserOut }
  | { type: "delete"; user: UserOut }
  | null;

export function UsersV2Page() {
  const { t } = useI18n();
  const { toast } = useUi();
  const { clearSession, user: currentUser } = useAuth();
  const {
    activeFilter,
    createUser,
    deleteUser,
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
    updateUser,
    updateUserStatus,
  } = useUsersData();

  const [editorUser, setEditorUser] = useState<UserOut | null>(null);
  const [editorOpen, setEditorOpen] = useState(false);
  const [savingUser, setSavingUser] = useState(false);
  const [pendingAction, setPendingAction] = useState<PendingAction>(null);
  const [busyUserId, setBusyUserId] = useState<number | null>(null);

  const closeEditor = () => {
    if (savingUser) {
      return;
    }
    setEditorOpen(false);
    setEditorUser(null);
  };

  const forceSessionReset = async () => {
    try {
      await logout();
    } catch {
      // Ignore API logout failures and clear the local session anyway.
    }
    clearSession();
  };

  const handleSaveUser = async (values: UserEditorValues) => {
    setSavingUser(true);
    try {
      if (editorUser) {
        await updateUser(editorUser.id, {
          username: values.username,
          email: values.email,
          full_name: values.full_name,
          department: values.department || null,
          role: values.role,
          is_active: values.is_active,
        });

        const affectsCurrentSession =
          currentUser?.id === editorUser.id &&
          (currentUser.role !== values.role || !values.is_active);

        if (affectsCurrentSession) {
          toast(t("users.roleUpdatedCurrentSession", { role: formatRole(values.role) }), "success");
          await forceSessionReset();
          return;
        }

        toast(t("users.toastUpdated", { id: editorUser.id }), "success");
      } else {
        await createUser({
          username: values.username,
          email: values.email,
          full_name: values.full_name,
          department: values.department || null,
          role: values.role,
          password: values.password,
          is_active: values.is_active,
        });
        toast(t("users.toastCreated", { username: values.username }), "success");
      }

      closeEditor();
      await reload();
    } catch (err) {
      toast(err instanceof Error ? err.message : t("errors.unexpected"), "error");
      throw err;
    } finally {
      setSavingUser(false);
    }
  };

  const handleConfirmAction = async () => {
    if (!pendingAction) {
      return;
    }

    const { type, user } = pendingAction;
    setBusyUserId(user.id);
    try {
      if (type === "status") {
        const nextActive = !user.is_active;
        await updateUserStatus(user.id, nextActive);
        if (currentUser?.id === user.id && !nextActive) {
          toast(t("users.roleUpdatedCurrentSession", { role: formatRole(user.role) }), "info");
          await forceSessionReset();
          return;
        }

        toast(
          nextActive
            ? t("users.toastActivated", { id: user.id })
            : t("users.toastDeactivated", { id: user.id }),
          "success",
        );
      }

      if (type === "delete") {
        await deleteUser(user.id);
        toast(t("users.toastDeleted", { id: user.id }), "success");
      }

      setPendingAction(null);
      await reload();
    } catch (err) {
      toast(err instanceof Error ? err.message : t("errors.unexpected"), "error");
    } finally {
      setBusyUserId(null);
    }
  };

  const pendingTitle =
    pendingAction?.type === "delete" ? t("users.deleteTitle") : t("users.statusTitle");
  const pendingDescription =
    pendingAction?.type === "delete"
      ? t("users.deleteDescription", { id: pendingAction.user.id })
      : t("users.statusDescription", {
          id: pendingAction?.user.id ?? "-",
          status: pendingAction?.user.is_active ? t("common.inactive") : t("common.active"),
        });

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
          <Button type="button" variant="outline" onClick={() => void reload()}>
            {t("common.refresh")}
          </Button>
          <Button
            type="button"
            onClick={() => {
              setEditorUser(null);
              setEditorOpen(true);
            }}
          >
            {t("users.addUser")}
          </Button>
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
            busyUserId={busyUserId}
            onEdit={(user) => {
              setEditorUser(user);
              setEditorOpen(true);
            }}
            onToggleStatus={(user) => setPendingAction({ type: "status", user })}
            onDelete={(user) => setPendingAction({ type: "delete", user })}
          />
          {loading ? <p>{t("users.loading")}</p> : null}
        </Card>
        <UserRoleBreakdown rows={roleBreakdown} />
      </div>

      <UserEditorModal
        open={editorOpen}
        user={editorUser}
        saving={savingUser}
        onClose={closeEditor}
        onSave={handleSaveUser}
      />

      <ConfirmDialog
        open={pendingAction !== null}
        title={pendingTitle}
        description={pendingDescription}
        confirmLabel={
          pendingAction?.type === "delete"
            ? t("users.deleteConfirm")
            : pendingAction?.user.is_active
              ? t("users.deactivateConfirm")
              : t("users.activateConfirm")
        }
        variant={pendingAction?.type === "delete" ? "danger" : "primary"}
        loading={busyUserId !== null}
        onConfirm={() => void handleConfirmAction()}
        onCancel={() => setPendingAction(null)}
      />
    </div>
  );
}
