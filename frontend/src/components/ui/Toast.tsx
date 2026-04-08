import { useUi } from "@/store/ui.store";
import { cx } from "@/utils/cx";

export function ToastViewport() {
  const { dismissToast, toasts } = useUi();

  return (
    <div className="toast-viewport" aria-live="polite" aria-atomic="true">
      {toasts.map((toast) => (
        <div key={toast.id} className={cx("toast", `toast--${toast.variant}`)}>
          <p>{toast.message}</p>
          <button className="toast__close" onClick={() => dismissToast(toast.id)} type="button">
            ×
          </button>
        </div>
      ))}
    </div>
  );
}
