import { useEffect, useState } from "react";

import { getAvailableUsers } from "@/services/swap.service";
import type { MySupervisionSlot } from "@/services/swap.service";
import type { UserOut } from "@/types/api";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { useI18n } from "@/i18n";

interface SwapCreateModalProps {
  open: boolean;
  supervisions: MySupervisionSlot[];
  loadingSlots: boolean;
  busy: boolean;
  onClose: () => void;
  onSubmit: (supervisionId: number, targetUserId: number, message?: string) => void;
}

export function SwapCreateModal({
  busy,
  loadingSlots,
  onClose,
  onSubmit,
  open,
  supervisions,
}: SwapCreateModalProps) {
  const { t } = useI18n();
  const [selectedSlot, setSelectedSlot] = useState<MySupervisionSlot | null>(null);
  const [availableUsers, setAvailableUsers] = useState<UserOut[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [targetUserId, setTargetUserId] = useState<number | null>(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!open) {
      setSelectedSlot(null);
      setAvailableUsers([]);
      setTargetUserId(null);
      setMessage("");
    }
  }, [open]);

  const handleSlotChange = async (supervisionId: number) => {
    const slot = supervisions.find((s) => s.supervision_id === supervisionId) ?? null;
    setSelectedSlot(slot);
    setTargetUserId(null);
    setAvailableUsers([]);
    if (!slot) return;

    setLoadingUsers(true);
    try {
      const users = await getAvailableUsers(slot.supervision_id);
      setAvailableUsers(users);
    } catch {
      setAvailableUsers([]);
    } finally {
      setLoadingUsers(false);
    }
  };

  const canSubmit = selectedSlot !== null && targetUserId !== null && !busy;

  const handleSubmit = () => {
    if (!selectedSlot || !targetUserId) return;
    onSubmit(selectedSlot.supervision_id, targetUserId, message.trim() || undefined);
  };

  const slotLabel = (slot: MySupervisionSlot) => {
    const parts = [slot.course, slot.section_no ? `§${slot.section_no}` : null, slot.exam_date, slot.exam_time, slot.room].filter(Boolean);
    return parts.join(" · ") || `Slot #${slot.supervision_id}`;
  };

  return (
    <Modal
      open={open}
      title={t("legacy.swaps.create.title")}
      onClose={onClose}
      footer={
        <div className="inline-actions">
          <Button type="button" variant="outline" onClick={onClose}>
            {t("common.cancel")}
          </Button>
          <Button type="button" disabled={!canSubmit} loading={busy} onClick={handleSubmit}>
            {t("legacy.swaps.actions.sendRequest")}
          </Button>
        </div>
      }
    >
      <div className="swap-create-form">
        <div className="form-field">
          <label htmlFor="swap-slot">{t("legacy.swaps.create.mySlot")}</label>
          {loadingSlots ? (
            <Skeleton className="form-skeleton" />
          ) : supervisions.length === 0 ? (
            <p className="form-hint">{t("legacy.swaps.create.noSlots")}</p>
          ) : (
            <select
              id="swap-slot"
              value={selectedSlot?.supervision_id ?? ""}
              onChange={(e) => void handleSlotChange(Number(e.target.value))}
            >
              <option value="">Select a slot…</option>
              {supervisions.map((slot) => (
                <option
                  key={slot.supervision_id}
                  value={slot.supervision_id}
                  disabled={slot.swap_requested}
                >
                  {slotLabel(slot)}
                  {slot.swap_requested ? " (pending swap)" : ""}
                </option>
              ))}
            </select>
          )}
        </div>

        {selectedSlot && (
          <div className="form-field">
            <label htmlFor="swap-target">{t("legacy.swaps.create.swapWith")}</label>
            {loadingUsers ? (
              <Skeleton className="form-skeleton" />
            ) : availableUsers.length === 0 ? (
              <p className="form-hint">{t("legacy.swaps.create.noAvailableStaff")}</p>
            ) : (
              <select
                id="swap-target"
                value={targetUserId ?? ""}
                onChange={(e) => setTargetUserId(Number(e.target.value))}
              >
                <option value="">Select a person…</option>
                {availableUsers.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.full_name ?? u.username} ({u.role})
                  </option>
                ))}
              </select>
            )}
          </div>
        )}

        <div className="form-field">
          <label htmlFor="swap-message">{t("legacy.swaps.create.message")}</label>
          <textarea
            id="swap-message"
            rows={3}
            value={message}
            placeholder="Reason for the swap request…"
            onChange={(e) => setMessage(e.target.value)}
          />
        </div>
      </div>
    </Modal>
  );
}
