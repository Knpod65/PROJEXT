import { useCallback, useEffect, useState } from "react";

import { RoomBlockModal } from "@/components/rooms/RoomBlockModal";
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
import type { RoomOut } from "@/types/api";
import { useUi } from "@/store/ui.store";

function RoomStatusBadge({ active }: { active: boolean }) {
  return (
    <span className={`room-badge ${active ? "room-badge--active" : "room-badge--inactive"}`}>
      {active ? "Active" : "Inactive"}
    </span>
  );
}

function RoomsTable({
  rooms,
  loading,
  onEdit,
}: {
  rooms: RoomOut[];
  loading: boolean;
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
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            <th>Room name</th>
            <th>Building</th>
            <th>Capacity</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {rooms.map((room) => (
            <tr key={room.id} className={room.is_active ? "" : "row-inactive"}>
              <td><strong>{room.room_name}</strong></td>
              <td className="text-muted">{room.building ?? "—"}</td>
              <td>{room.capacity}</td>
              <td><RoomStatusBadge active={room.is_active ?? true} /></td>
              <td>
                <Button type="button" size="sm" variant="outline" onClick={() => onEdit(room)}>
                  Edit
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function UnavailabilityTable({
  rows,
  loading,
  onDelete,
}: {
  rows: RoomUnavailabilityRecord[];
  loading: boolean;
  onDelete: (id: number) => Promise<void>;
}) {
  if (loading) return <Skeleton className="dashboard-skeleton" />;

  if (rows.length === 0) {
    return <p className="text-muted">No room blocks. All rooms are available for scheduling.</p>;
  }

  return (
    <div className="table-wrap">
      <table className="data-table data-table--compact">
        <thead>
          <tr>
            <th>Room</th>
            <th>Date</th>
            <th>Time</th>
            <th>Reason</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              <td><strong>{row.room_name ?? `Room #${row.room_id}`}</strong></td>
              <td>{row.block_date}</td>
              <td>{row.all_day ? "All day" : (row.block_time ?? "—")}</td>
              <td className="text-muted">{row.reason ?? "—"}</td>
              <td>
                <Button type="button" size="sm" variant="ghost" onClick={() => void onDelete(row.id)}>
                  Remove
                </Button>
              </td>
            </tr>
          ))}
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
  const [showBlockModal, setShowBlockModal] = useState(false);
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

  const handleEditSave = async (roomId: number, data: RoomUpdateData) => {
    setEditBusy(true);
    try {
      const updated = await updateRoom(roomId, data);
      setRooms((prev) => prev.map((r) => (r.id === roomId ? updated : r)));
      setEditTarget(null);
      toast("Room updated.", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to update room.", "error");
    } finally {
      setEditBusy(false);
    }
  };

  const handleAddBlock = async (data: {
    room_id: number;
    block_date: string;
    block_time?: string;
    reason?: string;
  }) => {
    setBlockBusy(true);
    try {
      await addRoomUnavailability(data);
      await loadBlocks();
      setShowBlockModal(false);
      toast("Room block added.", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to add block.", "error");
    } finally {
      setBlockBusy(false);
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

  const filteredRooms = rooms.filter((r) => {
    const matchQuery =
      query.trim().length === 0 ||
      `${r.room_name} ${r.building ?? ""}`.toLowerCase().includes(query.toLowerCase());
    const matchActive = showInactive || (r.is_active ?? true);
    return matchQuery && matchActive;
  });

  const totalCapacity = rooms.filter((r) => r.is_active).reduce((s, r) => s + r.capacity, 0);
  const activeCount = rooms.filter((r) => r.is_active ?? true).length;
  const inactiveCount = rooms.filter((r) => !(r.is_active ?? true)).length;

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">Room management</span>
          <h1 className="page-hero__title">Room capacity & availability</h1>
          <p className="page-hero__description">
            Manage room capacity and block dates. These settings are read by the optimizer during assignment.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => void loadRooms()} disabled={roomsLoading}>
            Refresh
          </Button>
          <Button type="button" onClick={() => setShowBlockModal(true)}>
            Block date
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
            <p className="dashboard-metric__label">Date blocks</p>
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

      <Card title="Rooms" subtitle="Click Edit to update capacity or toggle active status">
        <div className="filter-bar">
          <input
            type="text"
            placeholder="Search room name or building…"
            value={query}
            className="filter-bar__search"
            onChange={(e) => setQuery(e.target.value)}
          />
          <label className="filter-bar__checkbox">
            <input
              type="checkbox"
              checked={showInactive}
              onChange={(e) => setShowInactive(e.target.checked)}
            />
            Show inactive
          </label>
          {query && (
            <Button type="button" size="sm" variant="ghost" onClick={() => setQuery("")}>
              Clear
            </Button>
          )}
        </div>
        <RoomsTable rooms={filteredRooms} loading={roomsLoading} onEdit={setEditTarget} />
      </Card>

      <Card
        title="Room blocks"
        subtitle="Blocked rooms are excluded from optimizer assignments for those dates"
      >
        <UnavailabilityTable rows={blocks} loading={blocksLoading} onDelete={handleDeleteBlock} />
      </Card>

      <RoomEditModal
        room={editTarget}
        busy={editBusy}
        onClose={() => setEditTarget(null)}
        onSave={handleEditSave}
      />

      <RoomBlockModal
        open={showBlockModal}
        rooms={rooms.filter((r) => r.is_active ?? true)}
        busy={blockBusy}
        onClose={() => setShowBlockModal(false)}
        onAdd={handleAddBlock}
      />
    </div>
  );
}
