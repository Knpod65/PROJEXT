import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export type ToastVariant = "success" | "error" | "warning" | "info";

export interface ToastItem {
  id: string;
  message: string;
  variant: ToastVariant;
}

interface UiContextValue {
  toasts: ToastItem[];
  toast: (message: string, variant?: ToastVariant) => void;
  dismissToast: (id: string) => void;
}

const UiContext = createContext<UiContextValue | undefined>(undefined);

function createToastId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function UiProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const dismissToast = useCallback((id: string) => {
    setToasts((current) => current.filter((item) => item.id !== id));
  }, []);

  const toast = useCallback(
    (message: string, variant: ToastVariant = "info") => {
      const id = createToastId();
      setToasts((current) => [...current, { id, message, variant }]);
      window.setTimeout(() => dismissToast(id), 3200);
    },
    [dismissToast],
  );

  const value = useMemo(
    () => ({
      toasts,
      toast,
      dismissToast,
    }),
    [dismissToast, toast, toasts],
  );

  return <UiContext.Provider value={value}>{children}</UiContext.Provider>;
}

export function useUi() {
  const context = useContext(UiContext);
  if (!context) {
    throw new Error("useUi must be used inside UiProvider");
  }
  return context;
}
