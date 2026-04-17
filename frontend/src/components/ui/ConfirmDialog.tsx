import { Button } from "./Button";
import { Modal } from "./Modal";

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  /**
   * "danger" renders the confirm button in the destructive red variant.
   * Use "danger" for irreversible actions (deactivate, reject, sign-off).
   */
  variant?: "danger" | "primary" | "gold";
  loading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

/**
 * Reusable confirmation dialog built on top of Modal.
 * Provides a standard two-button (Cancel / Confirm) footer.
 * Always pass a clear, consequence-describing `description` to the user.
 */
export function ConfirmDialog({
  cancelLabel = "Cancel",
  confirmLabel = "Confirm",
  description,
  loading = false,
  onCancel,
  onConfirm,
  open,
  title,
  variant = "primary",
}: ConfirmDialogProps) {
  return (
    <Modal
      open={open}
      title={title}
      onClose={onCancel}
      footer={
        <div className="inline-actions">
          <Button type="button" variant="ghost" disabled={loading} onClick={onCancel}>
            {cancelLabel}
          </Button>
          <Button type="button" variant={variant} loading={loading} onClick={onConfirm}>
            {confirmLabel}
          </Button>
        </div>
      }
    >
      <p style={{ margin: 0 }}>{description}</p>
    </Modal>
  );
}
