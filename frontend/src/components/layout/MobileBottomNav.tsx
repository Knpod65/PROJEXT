import { NavLink } from "react-router-dom";

import { appPages, mobilePageKeys } from "@/config/navigation";
import { useAuth } from "@/store/auth.store";
import { hasRole } from "@/utils/roles";

export function MobileBottomNav() {
  const { user } = useAuth();
  const pages = appPages.filter((page) => mobilePageKeys.includes(page.key) && hasRole(user, page.roles));

  return (
    <nav className="mobile-nav" aria-label="เมนูมือถือ">
      {pages.map((page) => (
        <NavLink
          key={page.key}
          className={({ isActive }) => (isActive ? "mobile-nav__item mobile-nav__item--active" : "mobile-nav__item")}
          to={page.path}
        >
          <span>{page.icon}</span>
          <span>{page.title}</span>
        </NavLink>
      ))}
    </nav>
  );
}
