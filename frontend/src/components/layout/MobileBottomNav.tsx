import { NavLink } from "react-router-dom";

import { appPages, getPageTitle, mobilePageKeys } from "@/config/navigation";
import { useI18n } from "@/i18n";
import { useAuth } from "@/store/auth.store";
import { hasRole } from "@/utils/roles";

import { Icon } from "../ui/Icon";

export function MobileBottomNav() {
  const { t } = useI18n();
  const { user } = useAuth();
  const pages = appPages.filter(
    (page) =>
      mobilePageKeys.includes(page.key) &&
      hasRole(user, page.roles, { allowBaseAdminPreview: page.allowBaseAdminPreview }),
  );

  return (
    <nav className="mobile-nav" aria-label={t("layout.navigation.mobile")}>
      {pages.map((page) => (
        <NavLink
          key={page.key}
          className={({ isActive }: { isActive: boolean }) =>
            isActive ? "mobile-nav__item mobile-nav__item--active" : "mobile-nav__item"
          }
          to={page.path}
        >
          <Icon className="mobile-nav__icon" name={page.icon} />
          <span>{getPageTitle(page)}</span>
        </NavLink>
      ))}
    </nav>
  );
}
