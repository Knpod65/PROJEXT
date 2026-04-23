import { useCallback, useEffect, useMemo, useState } from "react";

import { RoomEditModal } from "@/components/rooms/RoomEditModal";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Skeleton } from "@/components/ui/Skeleton";
import {
  addRoomUnavailability,
  deleteRoomUnavailability,
  getRoomUnavailability,
  getRooms,
  updateRoom,
  type RoomUnavailabilityRecord,
  type RoomUpdateData,
} from "@/services/rooms.service";
import { useUi } from "@/store/ui.store";
import type { RoomOut } from "@/types/api";

type SlotDefinition = {
  start: string;
  end: string;
  label: string;
};

function RoomStatusBadge({ active }: { active: boolean }) {
  return (
    <span className={`room-badge ${active ? "room-badge--active" : "room-badge--inactive"}`}>
      {active ? "Active" : "Inactive"}
    </span>
  );
}

function toMinutes(value: string) {
  const [hours, minutes] = value.split(":").map(Number);
  return (hours * 60) + minutes;
}

function formatTime(minutes: number) {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${String(hours).padStart(2, "0")}:${String(mins).padStart(2, "0")}`;
}

function buildSlots(): SlotDefinition[] {
  const slots: SlotDefinition[] = [];
  for (let minutes = 8 * 60; minutes < 19 * 60; minutes += 30) {
    const start = formatTime(minutes);
    const end = formatTime(minutes + 30);
    slots.push({ start, end, label: `${start}-${end}` });
  }
  return slots;
}

const ROOM_SLOTS = buildSlots();

function getRangeBounds(row: RoomUnavailabilityRecord) {
  if (row.all_day) {
    return null;
  }
  const start = row.start_time ?? row.block_time?.split("-")[0] ?? null;
  const end = row.end_time ?? row.block_time?.split("-")[1] ?? null;
  if (!start || !end) {
    return null;
  }
  return { start, end };
}

function slotCoveredByRow(slot: SlotDefinition, row: RoomUnavailabilityRecord) {
  if (row.all_day) {
    return true;
  }
  const bounds = getRangeBounds(row);
  if (!bounds) {
    return false;
  }
  return toMinutes(slot.start) < toMinutes(bounds.end) && toMinutes(slot.end) > toMinutes(bounds.start);
}

function compressSlotStarts(slotStarts: string[]) {
  const sorted = [...slotStarts].sort();
  const intervals: Array<{ start_time: string; end_time: string; block_time: string }> = [];

  let rangeStart: string | null = null;
  let previousStart: string | null = null;

  for (const start of sorted) {
    if (!rangeStart) {
      rangeStart = start;
      previousStart = start;
      continue;
    }

    if (toMinutes(start) === toMinutes(previousStart ?? start) + 30) {
      previousStart = start;
      continue;
    }

    const previousSlot = ROOM_SLOTS.find((slot) => slot.start === previousStart);
    if (previousSlot) {
      intervals.push({
        start_time: rangeStart,
        end_time: previousSlot.end,
        block_time: `${rangeStart}-${previousSlot.end}`,
      });
    }
    rangeStart = start;
    previousStart = start;
  }

  if (rangeStart && previousStart) {
    const previousSlot = ROOM_SLOTS.find((slot) => slot.start === previousStart);
    if (previousSlot) {
      intervals.push({
        start_time: rangeStart,
        end_time: previousSlot.end,
        block_time: `${rangeStart}-${previousSlot.end}`,
      });
    }
  }

  return intervals;
}

function RoomsTable({
  rooms,
  loading,
  selectedRoomId,
  onSelect,
  onEdit,
}: {
  rooms: RoomOut[];
  loading: boolean;
  selectedRoomId: number | null;
  onSelect: (room: RoomOut) => void;
  onEdit: (room: RoomOut) => void;
}) {
  if (loading) {
    return (
      <div className="page-stack">
        {[0, 1, 2].map((i) => <Skeleton key={i} className="dashboard-skeleton" />)}
      </div>
    );
  }

  if (rooms.length === 0) {
    return (
      <EmptyState
        icon={<Icon name="meeting_room" />}
        title="No rooms found."
        description="Add a room using the button above, or adjust your filters."
      />
    );
  }

  return (
    <div className="table-wrap table-wrap--scrollable" style={{ maxHeight: "420px" }}>
      <table className="data-table data-table--compact data-table--fixed">
        <colgroup>
          <col style={{ width: "26%" }} />
          <col style={{ width: "18%" }} />
          <col style={{ width: "12%" }} />
          <col style={{ width: "12%" }} />
          <col style={{ width: "32%" }} />
        </colgroup>
        <thead>
          <tr>
            <th>Room</th>
            <th>Building</th>
            <th>Capacity</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {rooms.map((room) => {
            const selected = room.id === selectedRoomId;
            return (
              <tr key={room.id} className={`${room.is_active ? "" : "row-inactive"}${selected ? " row-selected" : ""}`}>
                <td>
                  <div className="data-table__content data-table__content--clamp">
                    <strong>{room.room_name}</strong>
                    <p>{selected ? "Selected for availability editing" : "Select to edit availability"}</p>
                  </div>
                </td>
                <td className="text-muted">{room.building ?? "-"}</td>
                <td>{room.capacity}</td>
                <td><RoomStatusBadge active={room.is_active ?? true} /></td>
                <td>
                  <div className="inline-actions">
                    <Button type="button" size="sm" variant={selected ? "primary" : "outline"} onClick={() => onSelect(room)}>
                      {selected ? "Selected" : "Select"}
                    </Button>
                    <Button type="button" size="sm" variant="ghost" onClick={() => onEdit(room)}>
                      Edit
                    </Button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export function RoomManagementV2Page() {
  const { toast } = useUi();

  const [rooms, setRooms] = useState<RoomOut[]>([]);
  const [roomsLoading, setRoomsLoading] = useState(true);
  const [blocks, setBlocks] = useState<RoomUnavailabilityRecord[]>([]);
  const [blocksLoading, setBlocksLoading] = useState(true);
  const [selectedRoomId, setSelectedRoomId] = useState<number | null>(null);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().slice(0, 10));
  const [selectedSlots, setSelectedSlots] = useState<string[]>([]);
  const [draftAllDay, setDraftAllDay] = useState(false);
  const [blockBusy, setBlockBusy] = useState(false);

  const [editTarget, setEditTarget] = useState<RoomOut | null>(null);
  const [editBusy, setEditBusy] = useState(false);

  const [query, setQuery] = useState("");
  const [showInactive, setShowInactive] = useState(false);

  const loadRooms = useCallback(async () => {
    setRoomsLoading(true);
    try {
      const data = await getRooms(true);
      setRooms(data);
    } catch {
      setRooms([]);
    } finally {
      setRoomsLoading(false);
    }
  }, []);

  const loadBlocks = useCallback(async () => {
    setBlocksLoading(true);
    try {
      const data = await getRoomUnavailability();
      setBlocks(data);
    } catch {
      setBlocks([]);
    } finally {
      setBlocksLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadRooms();
    void loadBlocks();
  }, [loadRooms, loadBlocks]);

  const filteredRooms = useMemo(() => {
    return rooms.filter((room) => {
      const matchesQuery =
        query.trim().length === 0 ||
        `${room.room_name} ${room.building ?? ""}`.toLowerCase().includes(query.toLowerCase());
      const matchesActive = showInactive || (room.is_active ?? true);
      return matchesQuery && matchesActive;
    });
  }, [query, rooms, showInactive]);

  useEffect(() => {
    if (filteredRooms.length === 0) {
      setSelectedRoomId(null);
      return;
    }
    if (!filteredRooms.some((room) => room.id === selectedRoomId)) {
      setSelectedRoomId(filteredRooms[0].id);
    }
  }, [filteredRooms, selectedRoomId]);

  useEffect(() => {
    setSelectedSlots([]);
    setDraftAllDay(false);
  }, [selectedDate, selectedRoomId]);

  const selectedRoom = useMemo(
    () => rooms.find((room) => room.id === selectedRoomId) ?? null,
    [rooms, selectedRoomId],
  );

  const selectedRoomBlocks = useMemo(
    () => blocks.filter((row) => row.room_id === selectedRoomId),
    [blocks, selectedRoomId],
  );

  const blocksForSelectedDate = useMemo(
    () => selectedRoomBlocks.filter((row) => row.block_date === selectedDate),
    [selectedDate, selectedRoomBlocks],
  );

  const existingAllDayBlock = blocksForSelectedDate.find((row) => row.all_day) ?? null;
  const blockedSlotStarts = useMemo(() => {
    const covered = new Set<string>();
    for (const row of blocksForSelectedDate) {
      for (const slot of ROOM_SLOTS) {
        if (slotCoveredByRow(slot, row)) {
          covered.add(slot.start);
        }
      }
    }
    return covered;
  }, [blocksForSelectedDate]);

  const handleEditSave = async (roomId: number, data: RoomUpdateData) => {
    setEditBusy(true);
    try {
      const updated = await updateRoom(roomId, data);
      setRooms((prev) => prev.map((room) => (room.id === roomId ? updated : room)));
      setEditTarget(null);
      toast("Room updated.", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to update room.", "error");
    } finally {
      setEditBusy(false);
    }
  };

  const handleDeleteBlock = async (id: number) => {
    try {
      await deleteRoomUnavailability(id);
      await loadBlocks();
      toast("Block removed.", "warning");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to remove block.", "error");
    }
  };

  const handleSaveAvailability = async () => {
    if (!selectedRoomId) {
      return;
    }

    const payloads = draftAllDay
      ? [{ room_id: selectedRoomId, block_date: selectedDate }]
      : compressSlotStarts(selectedSlots).map((interval) => ({
          room_id: selectedRoomId,
          block_date: selectedDate,
          start_time: interval.start_time,
          end_time: interval.end_time,
          reason: "Manually blocked from room calendar",
        }));

    if (payloads.length === 0) {
      toast("Select at least one time slot to block.", "warning");
      return;
    }

    setBlockBusy(true);
    try {
      for (const payload of payloads) {
        await addRoomUnavailability(payload);
      }
      await loadBlocks();
      setSelectedSlots([]);
      setDraftAllDay(false);
      toast("Room availability updated.", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to save room availability.", "error");
    } finally {
      setBlockBusy(false);
    }
  };

  const toggleSlot = (slotStart: string) => {
    if (blockedSlotStarts.has(slotStart) || existingAllDayBlock) {
      return;
    }
    setDraftAllDay(false);
    setSelectedSlots((prev) =>
      prev.includes(slotStart) ? prev.filter((value) => value !== slotStart) : [...prev, slotStart],
    );
  };

  const totalCapacity = rooms.filter((room) => room.is_active ?? true).reduce((sum, room) => sum + room.capacity, 0);
  const activeCount = rooms.filter((room) => room.is_active ?? true).length;
  const inactiveCount = rooms.filter((room) => !(room.is_active ?? true)).length;

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">Room operations</span>
          <h1 className="page-hero__title">Room capacity & availability</h1>
          <p className="page-hero__description">
            Select a room, review its operational calendar, and block unavailable time ranges before optimization runs.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => { void loadRooms(); void loadBlocks(); }} disabled={roomsLoading || blocksLoading}>
            Refresh
          </Button>
        </div>
      </section>

      <div className="stitch-metric-grid">
        <article className="dashboard-metric dashboard-metric--accent">
          <div className="dashboard-metric__icon"><Icon name="meeting_room" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Active rooms</p>
            <strong className="dashboard-metric__value">{activeCount}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--neutral">
          <div className="dashboard-metric__icon"><Icon name="chair" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Total capacity</p>
            <strong className="dashboard-metric__value">{totalCapacity}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--warning">
          <div className="dashboard-metric__icon"><Icon name="block" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Availability blocks</p>
            <strong className="dashboard-metric__value">{blocks.length}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--neutral">
          <div className="dashboard-metric__icon"><Icon name="visibility_off" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Inactive rooms</p>
            <strong className="dashboard-metric__value">{inactiveCount}</strong>
          </div>
        </article>
      </div>

      <Card title="Rooms" subtitle="Choose a room to edit its operational availability for the active period">
        <div className="filter-bar">
          <input
            type="text"
            placeholder="Search room name or building..."
            value={query}
            className="filter-bar__search"
            onChange={(event) => setQuery(event.target.value)}
          />
          <label className="filter-bar__checkbox">
            <input
              type="checkbox"
              checked={showInactive}
              onChange={(event) => setShowInactive(event.target.checked)}
            />
            Show inactive
          </label>
          {query && (
            <Button type="button" size="sm" variant="ghost" onClick={() => setQuery("")}>
              Clear
            </Button>
          )}
        </div>
        <RoomsTable
          rooms={filteredRooms}
          loading={roomsLoading}
          selectedRoomId={selectedRoomId}
          onSelect={(room) => setSelectedRoomId(room.id)}
          onEdit={setEditTarget}
        />
      </Card>

      <Card
        title={selectedRoom ? `Availability calendar: ${selectedRoom.room_name}` : "Availability calendar"}
        subtitle={selectedRoom ? "Manual blocks here are optimizer room constraints. They do not change teaching rooms or exam-room assignments." : "Select a room above to edit its calendar."}
      >
        {!selectedRoom ? (
          <EmptyState
            icon={<Icon name="calendar_month" />}
            title="No room selected"
            description="Select a room from the table above to edit its availability."
          />
        ) : (
          <div className="room-availability-layout">
            <div className="room-availability-editor">
              <div className="filter-bar">
                <div className="filter-field">
                  <span>Date</span>
                  <input type="date" value={selectedDate} onChange={(event) => setSelectedDate(event.target.value)} />
                </div>
                <div className="filter-bar__actions">
                  <Button
                    type="button"
                    size="sm"
                    variant={draftAllDay ? "primary" : "outline"}
                    onClick={() => {
                      setDraftAllDay((prev) => !prev);
                      setSelectedSlots([]);
                    }}
                    disabled={Boolean(existingAllDayBlock)}
                  >
                    {draftAllDay ? "All day selected" : "Mark all day unavailable"}
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    onClick={() => {
                      setSelectedSlots([]);
                      setDraftAllDay(false);
                    }}
                    disabled={selectedSlots.length === 0 && !draftAllDay}
                  >
                    Clear selection
                  </Button>
                  <Button type="button" size="sm" loading={blockBusy} onClick={() => void handleSaveAvailability()}>
                    Save unavailable time
                  </Button>
                </div>
              </div>

              {existingAllDayBlock ? (
                <div className="wf-validation wf-validation--ok">
                  <Icon name="event_busy" />
                  <span>This room is already blocked for the full day. Remove the full-day block from the list to edit half-hour slots.</span>
                </div>
              ) : (
                <div className="room-slot-grid" role="grid" aria-label="Room availability slots">
                  {ROOM_SLOTS.map((slot) => {
                    const isBlocked = blockedSlotStarts.has(slot.start);
                    const isSelected = draftAllDay || selectedSlots.includes(slot.start);
                    return (
                      <button
                        key={slot.start}
                        type="button"
                        className={`room-slot${isBlocked ? " room-slot--blocked" : ""}${isSelected ? " room-slot--selected" : ""}`}
                        onClick={() => toggleSlot(slot.start)}
                        disabled={isBlocked}
                      >
                        <strong>{slot.label}</strong>
                        <span>{isBlocked ? "Blocked" : isSelected ? "Selected" : "Available"}</span>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="room-availability-sidebar">
              <div className="room-availability-sidebar__summary">
                <strong>{selectedRoom.room_name}</strong>
                <span>{selectedRoom.building ?? "No building label"}</span>
                <span>Capacity {selectedRoom.capacity}</span>
              </div>

              <div className="page-stack">
                <div>
                  <strong>Saved blocks on {selectedDate}</strong>
                  {blocksLoading ? (
                    <Skeleton className="dashboard-skeleton" />
                  ) : blocksForSelectedDate.length === 0 ? (
                    <p className="text-muted">No saved unavailability for this date.</p>
                  ) : (
                    <div className="room-block-list">
                      {blocksForSelectedDate.map((row) => (
                        <div key={row.id} className="room-block-list__item">
                          <div>
                            <strong>{row.all_day ? "All day" : row.block_time ?? "Blocked"}</strong>
                            <p>{row.reason ?? "Manual operational block"}</p>
                          </div>
                          <Button type="button" size="sm" variant="ghost" onClick={() => void handleDeleteBlock(row.id)}>
                            Remove
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div>
                  <strong>Upcoming saved blocks</strong>
                  {blocksLoading ? (
                    <Skeleton className="dashboard-skeleton" />
                  ) : selectedRoomBlocks.length === 0 ? (
                    <p className="text-muted">No saved blocks for this room in the active period.</p>
                  ) : (
                    <div className="room-block-list room-block-list--compact">
                      {selectedRoomBlocks.slice(0, 8).map((row) => (
                        <div key={row.id} className="room-block-list__item">
                          <div>
                            <strong>{row.block_date}</strong>
                            <p>{row.all_day ? "All day" : row.block_time ?? "Blocked"}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </Card>

      <RoomEditModal
        room={editTarget}
        busy={editBusy}
        onClose={() => setEditTarget(null)}
        onSave={handleEditSave}
      />
    </div>
  );
}
