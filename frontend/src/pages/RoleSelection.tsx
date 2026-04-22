import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { RoleSelectionCard } from "@/components/role-entry/RoleSelectionCard";
import { getRoleSelectionEntries, type RoleEntryKey } from "@/components/role-entry/roleEntryConfig";
import { Button } from "@/components/ui/Button";
import { LanguageToggle } from "@/components/ui/LanguageToggle";
import { useI18n } from "@/i18n";
import { useAuth } from "@/store/auth.store";
import { getDefaultRoute, getStoredPendingRole, storePendingRole } from "@/utils/roles";

export function RoleSelectionPage() {
  const { language, t } = useI18n();
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedEntryKey, setSelectedEntryKey] = useState<RoleEntryKey | null>(() => {
    const pendingRole = getStoredPendingRole();
    return pendingRole ?? null;
  });

  const entries = useMemo(() => getRoleSelectionEntries(), [language]);

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
            <span className="page-hero__eyebrow">{t("auth.roleSelection.eyebrow")}</span>
            <h1 className="page-hero__title">{t("auth.roleSelection.title")}</h1>
            <p className="page-hero__description">{t("auth.roleSelection.description")}</p>
          </div>
          <div className="page-hero__actions">
            <LanguageToggle />
            <div className="role-entry-user">
              <strong>{t("auth.roleSelection.validationTitle")}</strong>
              <span>{t("auth.roleSelection.validationDescription")}</span>
              <small>{t("auth.roleSelection.validationNote")}</small>
            </div>
          </div>
        </section>

        <section className="role-entry-grid" aria-label={t("auth.roleSelection.aria")}>
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
          <p className="role-entry-note">{t("auth.roleSelection.note")}</p>
          <div className="inline-actions">
            <Button type="button" variant="outline" onClick={() => navigate("/student-search")}>
              {t("auth.roleSelection.publicSearch")}
            </Button>
            <Button disabled={!selectedEntryKey} type="button" onClick={handleContinue}>
              {t("auth.roleSelection.continue")}
            </Button>
          </div>
        </div>
      </div>
    </main>
  );
}
