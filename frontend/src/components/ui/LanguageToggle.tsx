import { useI18n } from "@/i18n";
import { cx } from "@/utils/cx";

interface LanguageToggleProps {
  className?: string;
}

export function LanguageToggle({ className }: LanguageToggleProps) {
  const { language, setLanguage, t } = useI18n();

  return (
    <div className={cx("language-toggle", className)} aria-label={t("topbar.languageAria")} role="group">
      <button
        type="button"
        className={cx("language-toggle__button", language === "th" && "language-toggle__button--active")}
        aria-label={t("topbar.languageThai")}
        onClick={() => setLanguage("th")}
      >
        {t("language.th")}
      </button>
      <button
        type="button"
        className={cx("language-toggle__button", language === "en" && "language-toggle__button--active")}
        aria-label={t("topbar.languageEnglish")}
        onClick={() => setLanguage("en")}
      >
        {t("language.en")}
      </button>
    </div>
  );
}
