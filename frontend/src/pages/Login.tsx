import type React from "react";
import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { getPageConfig } from "@/config/navigation";
import { getRoleSelectionEntry } from "@/components/role-entry/roleEntryConfig";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { LanguageToggle } from "@/components/ui/LanguageToggle";
import { useI18n } from "@/i18n";
import { useAuth } from "@/store/auth.store";
import { getDefaultRoute, getPublicEntryRoute, getStoredPendingRole, hasRole } from "@/utils/roles";

export function LoginPage() {
  const { language, t } = useI18n();
  const { signIn, user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pendingRole = getStoredPendingRole();
  const selectedEntry = useMemo(() => getRoleSelectionEntry(pendingRole), [language, pendingRole]);

  useEffect(() => {
    if (user) {
      navigate(getDefaultRoute(user), { replace: true });
      return;
    }

    if (!pendingRole) {
      navigate(getPublicEntryRoute(), {
        replace: true,
        state: (location.state as { from?: string } | null) ?? undefined,
      });
    }
  }, [location.state, navigate, pendingRole, user]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!pendingRole) {
      navigate("/role-selection", { replace: true });
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const signedInUser = await signIn(username, password, pendingRole);
      const requestedPath = (location.state as { from?: string } | null)?.from;
      const requestedRoutePath = requestedPath ? requestedPath.split(/[?#]/)[0] : undefined;
      const requestedPage = requestedRoutePath ? getPageConfig(requestedRoutePath) : undefined;

      const target =
        requestedPath &&
        requestedPage &&
        (requestedPage.public ||
          hasRole(signedInUser, requestedPage.roles, {
            allowBaseAdminPreview: requestedPage.allowBaseAdminPreview,
          }))
          ? requestedPath
          : getDefaultRoute(signedInUser);

      navigate(target || "/dashboard", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : t("errors.loginFailed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <Card className="login-card">
        <div className="login-card__language">
          <LanguageToggle />
        </div>

        <div className="login-card__brand">
          <div className="login-card__logo">EMS</div>
          <div>
            <h1>{t("auth.login.heading")}</h1>
            <p>{t("auth.login.subheading")}</p>
          </div>
        </div>

        <div className="login-card__meta">
          <strong>{selectedEntry?.title ?? t("auth.login.selectedWorkspace")}</strong>
          <p>{selectedEntry?.description ?? t("auth.login.selectedWorkspaceDescription")}</p>
          <button className="sidebar__logout" type="button" onClick={() => navigate("/role-selection", { state: location.state ?? undefined })}>
            {t("auth.login.changeRole")}
          </button>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <label className="form-field">
            <span>{t("auth.login.username")}</span>
            <input
              autoComplete="username"
              onChange={(event) => setUsername(event.target.value)}
              placeholder={t("auth.login.usernamePlaceholder")}
              required
              value={username}
            />
          </label>

          <label className="form-field">
            <span>{t("auth.login.password")}</span>
            <input
              autoComplete="current-password"
              onChange={(event) => setPassword(event.target.value)}
              placeholder={t("auth.login.passwordPlaceholder")}
              required
              type="password"
              value={password}
            />
          </label>

          {error ? <p className="form-error">{error}</p> : null}

          <Button fullWidth loading={loading} type="submit">
            {t("auth.login.submit")}
          </Button>
          <Button
            fullWidth
            type="button"
            variant="outline"
            onClick={() => {
              const query = pendingRole ? `?selected_role=${encodeURIComponent(pendingRole)}` : "";
              window.location.href = `/api/auth/sso/login${query}`;
            }}
          >
            {t("auth.login.sso")}
          </Button>
        </form>
      </Card>
    </div>
  );
}
