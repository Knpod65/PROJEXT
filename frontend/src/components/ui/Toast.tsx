import { useI18n } from "@/i18n";
import { useUi, type ToastItem } from "@/store/ui.store";
import { cx } from "@/utils/cx";

export function ToastViewport() {
  const { t } = useI18n();
  const { dismissToast, toasts } = useUi();

  return (
    <div className="toast-viewport" aria-live="polite" aria-atomic="true">
      {toasts.map((toast: ToastItem) => (
        <div key={toast.id} className={cx("toast", `toast--${toast.variant}`)}>
          <p>{toast.message}</p>
          <button
            aria-label={t("common.closeButton")}
            className="toast__close"
            onClick={() => dismissToast(toast.id)}
            type="button"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}
