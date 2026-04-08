import { NavLink } from "react-router-dom";

import { appPages } from "@/config/navigation";
import { useAuth } from "@/store/auth.store";
import { hasRole } from "@/utils/roles";

function groupPages() {
  const groups = new Map<string, typeof appPages>();
  appPages.forEach((page) => {
    if (page.hidden || !page.navGroup) return;
    const pages = groups.get(page.navGroup) ?? [];
    pages.push(page);
    groups.set(page.navGroup, pages);
  });
  return Array.from(groups.entries());
}

export function Sidebar() {
  const { signOut, user } = useAuth();
  const groupedPages = groupPages();

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <div className="sidebar__logo">EMS</div>
        <div>
          <strong>Exam Management</strong>
          <p>คณะรัฐศาสตร์ มช.</p>
        </div>
      </div>

      <nav className="sidebar__nav" aria-label="เมนูหลัก">
        {groupedPages.map(([group, pages]) => {
          const visiblePages = pages.filter((page) => hasRole(user, page.roles));
          if (visiblePages.length === 0) return null;

          return (
            <div key={group} className="sidebar__group">
              <p className="sidebar__group-title">{group}</p>
              {visiblePages.map((page) => (
                <NavLink
                  key={page.key}
                  className={({ isActive }) => (isActive ? "sidebar__link sidebar__link--active" : "sidebar__link")}
                  to={page.path}
                >
                  <span>{page.icon}</span>
                  <span>{page.title}</span>
                </NavLink>
              ))}
            </div>
          );
        })}
      </nav>

      <div className="sidebar__footer">
        <button className="sidebar__logout" onClick={() => void signOut()} type="button">
          <span>🚪</span>
          <span>ออกจากระบบ</span>
        </button>
      </div>
    </aside>
  );
}
