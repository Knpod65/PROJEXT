import { useState } from "react";

import type { SwapItem } from "@/types/api";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { useI18n } from "@/i18n";

interface SwapRespondModalProps {
  swap: SwapItem | null;
  busy: boolean;
  onClose: () => void;
  onRespond: (swapId: number, accept: boolean, reason?: string) => void;
}

export function SwapRespondModal({ busy, onClose, onRespond, swap }: SwapRespondModalProps) {
  const { t } = useI18n();
  const [decision, setDecision] = useState<"accept" | "reject" | null>(null);
  const [reason, setReason] = useState("");

  const handleClose = () => {
    setDecision(null);
    setReason("");
    onClose();
  };

  const handleSubmit = () => {
    if (!swap || decision === null) return;
    onRespond(swap.id, decision === "accept", reason.trim() || undefined);
    setDecision(null);
    setReason("");
  };

  const canSubmit = decision !== null && (decision === "accept" || reason.trim().length > 0) && !busy;

  if (!swap) return null;

  const theirShift = swap.my_shift ?? swap.their_shift;
  const myShift = swap.their_shift ?? swap.my_shift;

  return (
    <Modal
      open={swap !== null}
      title={t("legacy.swaps.respond.title", { value: swap.requester_name ?? t("common.unknown") })}
      onClose={handleClose}
      footer={
        <div className="inline-actions">
          <Button type="button" variant="outline" onClick={handleClose}>
            {t("common.cancel")}
          </Button>
          <Button
            type="button"
            variant={decision === "reject" ? "danger" : "primary"}
            disabled={!canSubmit}
            loading={busy}
            onClick={handleSubmit}
          >
            {decision === "accept" ? t("legacy.swaps.actions.accept") : decision === "reject" ? t("legacy.swaps.actions.reject") : t("legacy.swaps.actions.respond")}
          </Button>
        </div>
      }
    >
      <div className="swap-respond-form">
        {swap.message && (
          <blockquote className="swap-respond__message">
            "{swap.message}"
          </blockquote>
        )}

        <div className="swap-shift-pair">
          <div className="swap-shift-card">
            <span className="swap-shift-card__label">{t("legacy.swaps.table.theirSlot")}</span>
            <strong>{theirShift?.course ?? "—"} §{theirShift?.section_no ?? "—"}</strong>
            <span>{theirShift?.date ?? "—"} {theirShift?.time ?? "—"}</span>
            <span className="text-muted">{theirShift?.room ?? "—"}</span>
          </div>
          <div className="swap-shift-card__arrow">⇄</div>
          <div className="swap-shift-card">
            <span className="swap-shift-card__label">{t("legacy.swaps.table.yourSlot")}</span>
            <strong>{myShift?.course ?? "—"} §{myShift?.section_no ?? "—"}</strong>
            <span>{myShift?.date ?? "—"} {myShift?.time ?? "—"}</span>
            <span className="text-muted">{myShift?.room ?? "—"}</span>
          </div>
        </div>

        <div className="swap-respond__decision">
          <button
            type="button"
            className={`swap-respond__btn swap-respond__btn--accept${decision === "accept" ? " active" : ""}`}
            onClick={() => setDecision("accept")}
          >
            {t("legacy.swaps.actions.accept")}
          </button>
          <button
            type="button"
            className={`swap-respond__btn swap-respond__btn--reject${decision === "reject" ? " active" : ""}`}
            onClick={() => setDecision("reject")}
          >
            {t("legacy.swaps.actions.reject")}
          </button>
        </div>

        {decision === "reject" && (
          <div className="form-field">
            <label htmlFor="reject-reason">{t("legacy.swaps.respond.rejectReason")}</label>
            <textarea
              id="reject-reason"
              rows={3}
              value={reason}
              placeholder="Explain why you're rejecting this request…"
              onChange={(e) => setReason(e.target.value)}
            />
          </div>
        )}
      </div>
    </Modal>
  );
}
