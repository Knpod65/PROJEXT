import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { RoleSelectionCard } from "@/components/role-entry/RoleSelectionCard";
import { getRoleSelectionEntries, type RoleEntryKey } from "@/components/role-entry/roleEntryConfig";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/store/auth.store";
import { getDefaultRoute, getStoredPendingRole, storePendingRole } from "@/utils/roles";

export function RoleSelectionPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedEntryKey, setSelectedEntryKey] = useState<RoleEntryKey | null>(() => {
    const pendingRole = getStoredPendingRole();
    return pendingRole ?? null;
  });

  const entries = useMemo(() => getRoleSelectionEntries(), []);

  useEffect(() => {
    if (user) {
      navigate(getDefaultRoute(user), { replace: true });
    }
  }, [navigate, user]);

  const handleContinue = () => {
    if (!selectedEntryKey) {
      return;
    }

    storePendingRole(selectedEntryKey);
    const requestedPath = (location.state as { from?: string } | null)?.from;
    navigate("/login", {
      replace: true,
      state: requestedPath ? { from: requestedPath } : undefined,
    });
  };

  return (
    <main className="role-entry-page">
      <div className="role-entry-shell">
        <section className="page-hero">
          <div>
            <span className="page-hero__eyebrow">Production Role Entry</span>
            <h1 className="page-hero__title">Choose your workspace before sign-in</h1>
            <p className="page-hero__description">
              Select the role experience you intend to enter. The login step will validate this choice and lock the
              resulting session to the matching workspace.
            </p>
          </div>
          <div className="page-hero__actions">
            <div className="role-entry-user">
              <strong>EMS role validation</strong>
              <span>Role selection happens before authentication in the production flow.</span>
              <small>Admin preview switching stays inside settings only after login.</small>
            </div>
          </div>
        </section>

        <section className="role-entry-grid" aria-label="Role selection">
          {entries.map((entry) => (
            <RoleSelectionCard
              key={entry.key}
              entry={entry}
              selected={selectedEntryKey === entry.key}
              onSelect={() => setSelectedEntryKey(entry.key)}
            />
          ))}
        </section>

        <div className="role-entry-actions">
          <p className="role-entry-note">
            This pre-login role choice captures user intent first. Authentication then confirms whether the selected
            workspace is allowed for the signed-in account.
          </p>
          <div className="inline-actions">
            <Button type="button" variant="outline" onClick={() => navigate("/student-search")}>
              Public Student Search
            </Button>
            <Button disabled={!selectedEntryKey} type="button" onClick={handleContinue}>
              Continue to sign in
            </Button>
          </div>
        </div>
      </div>
    </main>
  );
}
