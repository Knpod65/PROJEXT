import { useEffect, useState } from "react";

import type { RoomOut } from "@/types/api";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import type { RoomUpdateData } from "@/services/rooms.service";

interface RoomEditModalProps {
  room: RoomOut | null;
  busy: boolean;
  onClose: () => void;
  onSave: (roomId: number, data: RoomUpdateData) => Promise<void>;
}

export function RoomEditModal({ busy, onClose, onSave, room }: RoomEditModalProps) {
  const [form, setForm] = useState<RoomUpdateData>({});

  useEffect(() => {
    if (room) {
      setForm({
        room_name: room.room_name,
        building: room.building ?? "",
        capacity: room.capacity,
        is_active: room.is_active ?? true,
      });
    }
  }, [room]);

  if (!room) return null;

  const handleSave = async () => {
    const payload: RoomUpdateData = {};
    if (form.room_name !== room.room_name) payload.room_name = form.room_name;
    if (form.building !== (room.building ?? "")) payload.building = form.building || undefined;
    if (form.capacity !== room.capacity) payload.capacity = form.capacity;
    if (form.is_active !== (room.is_active ?? true)) payload.is_active = form.is_active;

    if (Object.keys(payload).length === 0) {
      onClose();
      return;
    }
    await onSave(room.id, payload);
  };

  return (
    <Modal
      open={room !== null}
      title={`Edit room — ${room.room_name}`}
      onClose={onClose}
      footer={
        <div className="inline-actions">
          <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="button" loading={busy} onClick={() => void handleSave()}>Save changes</Button>
        </div>
      }
    >
      <div className="room-edit-form">
        <div className="form-field">
          <label htmlFor="re-name">Room name</label>
          <input
            id="re-name"
            type="text"
            value={form.room_name ?? ""}
            onChange={(e) => setForm((f) => ({ ...f, room_name: e.target.value }))}
          />
        </div>
        <div className="form-field">
          <label htmlFor="re-building">Building</label>
          <input
            id="re-building"
            type="text"
            value={form.building ?? ""}
            placeholder="e.g. Main Tower"
            onChange={(e) => setForm((f) => ({ ...f, building: e.target.value }))}
          />
        </div>
        <div className="form-field">
          <label htmlFor="re-capacity">Capacity (seats)</label>
          <input
            id="re-capacity"
            type="number"
            min={1}
            value={form.capacity ?? 0}
            onChange={(e) => setForm((f) => ({ ...f, capacity: Number(e.target.value) }))}
          />
          <span className="form-hint">Room must fit all assigned students. Optimizer uses this limit.</span>
        </div>
        <div className="form-field form-field--checkbox">
          <label>
            <input
              type="checkbox"
              checked={form.is_active ?? true}
              onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))}
            />
            Room is active (available for scheduling)
          </label>
        </div>
      </div>
    </Modal>
  );
}
