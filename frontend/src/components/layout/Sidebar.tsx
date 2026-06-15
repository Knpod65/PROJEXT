import { NavLink } from "react-router-dom";

import { appPages, getNavGroupLabel, getPageDescription, getPageTitle, navGroupOrder } from "@/config/navigation";
import { useEffectiveRole } from "@/hooks/useEffectiveRole";
import { useI18n } from "@/i18n";
import { useAuth } from "@/store/auth.store";
import { usePeriod } from "@/store/period.store";
import { getRoleTheme } from "@/theme/roleThemes";
import { formatRole } from "@/utils/format";
import { getEffectiveRole, hasRole } from "@/utils/roles";

import { Icon } from "../ui/Icon";

function getGroupedPages(userRole: ReturnType<typeof getEffectiveRole>, user: ReturnType<typeof useAuth>["user"]) {
  const visiblePages = appPages.filter(
    (page) =>
      !page.hidden &&
      page.navGroup &&
      hasRole(user, page.roles, { allowBaseAdminPreview: page.allowBaseAdminPreview }),
  );

  return navGroupOrder
    .map((group) => ({
      group,
      pages: visiblePages.filter((page) => page.navGroup === group),
    }))
    .filter((entry) => entry.pages.length > 0 && Boolean(userRole));
}

export function Sidebar() {
  const { t } = useI18n();
  const { signOut, user } = useAuth();
  const { activePeriod } = usePeriod();
  const role = useEffectiveRole();
  const theme = getRoleTheme(role);
  const groupedPages = getGroupedPages(role, user);

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <div className="sidebar__brand-icon">
          <Icon filled name={theme.brandIcon} />
        </div>
        <div className="sidebar__brand-copy">
          <strong>{theme.shellTitle}</strong>
          <p>{theme.shellSubtitle}</p>
        </div>
      </div>

      <section className="sidebar__summary">
        <span className="sidebar__eyebrow">{t("common.activePeriod")}</span>
        <strong>{activePeriod?.label ?? t("common.noActiveExamPeriod")}</strong>
        <p>{user?.full_name ?? user?.username ?? t("common.operator")}</p>
      </section>

      <nav className="sidebar__nav" aria-label={t("layout.navigation.primary")}>
        {groupedPages.map(({ group, pages }) => (
          <div key={group} className="sidebar__group">
            <p className="sidebar__group-title">{getNavGroupLabel(group)}</p>
            {pages.map((page) => (
              <NavLink
                key={page.key}
                className={({ isActive }: { isActive: boolean }) =>
                  isActive ? "sidebar__link sidebar__link--active" : "sidebar__link"
                }
                to={page.path}
              >
                <Icon className="sidebar__link-icon" name={page.icon} />
                <span className="sidebar__link-copy">
                  <strong>{getPageTitle(page)}</strong>
                  <small>{getPageDescription(page)}</small>
                </span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar__footer">
        <div className="sidebar__footer-card">
          <span className="sidebar__eyebrow">{t("common.currentRole")}</span>
          <strong>{formatRole(role)}</strong>
          <p>{theme.badgeLabel}</p>
        </div>
        <button className="sidebar__logout" onClick={() => void signOut()} type="button">
          <Icon name="logout" />
          <span>{t("common.signOut")}</span>
        </button>
      </div>
    </aside>
  );
}
