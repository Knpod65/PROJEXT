import { NavLink } from "react-router-dom";

import { appPages, mobilePageKeys } from "@/config/navigation";
import { useAuth } from "@/store/auth.store";
import { hasRole } from "@/utils/roles";

import { Icon } from "../ui/Icon";

export function MobileBottomNav() {
  const { user } = useAuth();
  const pages = appPages.filter(
    (page) =>
      mobilePageKeys.includes(page.key) &&
      hasRole(user, page.roles, { allowBaseAdminPreview: page.allowBaseAdminPreview }),
  );

  return (
    <nav className="mobile-nav" aria-label="Mobile navigation">
      {pages.map((page) => (
        <NavLink
          key={page.key}
          className={({ isActive }) => (isActive ? "mobile-nav__item mobile-nav__item--active" : "mobile-nav__item")}
          to={page.path}
        >
          <Icon className="mobile-nav__icon" name={page.icon} />
          <span>{page.title}</span>
        </NavLink>
      ))}
    </nav>
  );
}
