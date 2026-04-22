import { useState } from "react";

import type { RoomOut } from "@/types/api";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";

interface RoomBlockModalProps {
  open: boolean;
  rooms: RoomOut[];
  busy: boolean;
  onClose: () => void;
  onAdd: (data: { room_id: number; block_date: string; block_time?: string; reason?: string }) => Promise<void>;
}

export function RoomBlockModal({ busy, onAdd, onClose, open, rooms }: RoomBlockModalProps) {
  const [form, setForm] = useState({
    room_id: "",
    block_date: "",
    block_time: "",
    reason: "",
  });

  const canSubmit = form.room_id !== "" && form.block_date !== "";

  const handleSubmit = async () => {
    if (!canSubmit) return;
    await onAdd({
      room_id: Number(form.room_id),
      block_date: form.block_date,
      block_time: form.block_time || undefined,
      reason: form.reason || undefined,
    });
    setForm({ room_id: "", block_date: "", block_time: "", reason: "" });
  };

  return (
    <Modal
      open={open}
      title="Block room date"
      onClose={onClose}
      footer={
        <div className="inline-actions">
          <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="button" disabled={!canSubmit} loading={busy} onClick={() => void handleSubmit()}>
            Add block
          </Button>
        </div>
      }
    >
      <div className="room-block-form">
        <div className="form-field">
          <label htmlFor="rb-room">Room</label>
          <select
            id="rb-room"
            value={form.room_id}
            onChange={(e) => setForm((f) => ({ ...f, room_id: e.target.value }))}
          >
            <option value="">Select room…</option>
            {rooms.map((r) => (
              <option key={r.id} value={r.id}>
                {r.room_name}{r.building ? ` — ${r.building}` : ""} (cap: {r.capacity})
              </option>
            ))}
          </select>
        </div>
        <div className="form-field">
          <label htmlFor="rb-date">Date</label>
          <input
            id="rb-date"
            type="date"
            value={form.block_date}
            onChange={(e) => setForm((f) => ({ ...f, block_date: e.target.value }))}
          />
        </div>
        <div className="form-field">
          <label htmlFor="rb-time">Time slot (leave blank for all-day)</label>
          <input
            id="rb-time"
            type="text"
            placeholder="e.g. 09:00 or 09.00-12.00"
            value={form.block_time}
            onChange={(e) => setForm((f) => ({ ...f, block_time: e.target.value }))}
          />
        </div>
        <div className="form-field">
          <label htmlFor="rb-reason">Reason (optional)</label>
          <input
            id="rb-reason"
            type="text"
            placeholder="e.g. Maintenance, Ceremony"
            value={form.reason}
            onChange={(e) => setForm((f) => ({ ...f, reason: e.target.value }))}
          />
        </div>
        <p className="form-hint">Blocked rooms are excluded from optimizer assignments for the selected date and time.</p>
      </div>
    </Modal>
  );
}
