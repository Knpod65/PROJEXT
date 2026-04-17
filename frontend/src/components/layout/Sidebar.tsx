import { NavLink } from "react-router-dom";

import { appPages, navGroupOrder } from "@/config/navigation";
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
  const { signOut, user } = useAuth();
  const { activePeriod } = usePeriod();
  const role = getEffectiveRole(user);
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
        <span className="sidebar__eyebrow">Active period</span>
        <strong>{activePeriod?.label ?? "No active exam period"}</strong>
        <p>{user?.full_name ?? user?.username ?? "EMS operator"}</p>
      </section>

      <nav className="sidebar__nav" aria-label="Primary navigation">
        {groupedPages.map(({ group, pages }) => (
          <div key={group} className="sidebar__group">
            <p className="sidebar__group-title">{group}</p>
            {pages.map((page) => (
              <NavLink
                key={page.key}
                className={({ isActive }) => (isActive ? "sidebar__link sidebar__link--active" : "sidebar__link")}
                to={page.path}
              >
                <Icon className="sidebar__link-icon" name={page.icon} />
                <span className="sidebar__link-copy">
                  <strong>{page.title}</strong>
                  <small>{page.description}</small>
                </span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar__footer">
        <div className="sidebar__footer-card">
          <span className="sidebar__eyebrow">Current role</span>
          <strong>{formatRole(role)}</strong>
          <p>{theme.badgeLabel}</p>
        </div>
        <button className="sidebar__logout" onClick={() => void signOut()} type="button">
          <Icon name="logout" />
          <span>Sign out</span>
        </button>
      </div>
    </aside>
  );
}
