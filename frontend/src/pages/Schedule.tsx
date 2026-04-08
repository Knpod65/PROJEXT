import { useCallback, useMemo, useState } from "react";

import { ScheduleCard } from "@/components/schedule/ScheduleCard";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { FilterBar } from "@/components/ui/FilterBar";
import { Skeleton } from "@/components/ui/Skeleton";
import { getRooms, listSchedules } from "@/services/schedule.service";
import { useAsyncData } from "@/hooks/useAsyncData";
import { formatDate } from "@/utils/format";

export function SchedulePage() {
  const [roomId, setRoomId] = useState("");
  const [status, setStatus] = useState("");

  const roomsLoader = useCallback(() => getRooms(), []);
  const schedulesLoader = useCallback(
    () =>
      listSchedules({
        room_id: roomId ? Number(roomId) : undefined,
        status: status || undefined,
      }),
    [roomId, status],
  );

  const roomsState = useAsyncData(roomsLoader, [roomsLoader]);
  const schedulesState = useAsyncData(schedulesLoader, [schedulesLoader]);

  const grouped = useMemo(() => {
    const groups = new Map<string, Awaited<ReturnType<typeof listSchedules>>>();
    (schedulesState.data ?? []).forEach((schedule) => {
      const key = schedule.exam_date;
      const items = groups.get(key) ?? [];
      items.push(schedule);
      groups.set(key, items);
    });
    return Array.from(groups.entries()).sort(([left], [right]) => left.localeCompare(right));
  }, [schedulesState.data]);

  return (
    <div className="page-stack">
      <FilterBar
        actions={
          <>
            <Button type="button" variant="outline" onClick={() => window.open("/api/exports/schedule.xlsx", "_blank")}>
              ส่งออก Excel
            </Button>
            <Button type="button" variant="outline" onClick={() => window.open("/api/pdf/schedule", "_blank")}>
              พิมพ์ PDF
            </Button>
          </>
        }
      >
        <label className="filter-field">
          <span>ห้อง</span>
          <select value={roomId} onChange={(event) => setRoomId(event.target.value)}>
            <option value="">ทั้งหมด</option>
            {(roomsState.data ?? []).map((room) => (
              <option key={room.id} value={room.id}>
                {room.room_name}
              </option>
            ))}
          </select>
        </label>
        <label className="filter-field">
          <span>สถานะ</span>
          <select value={status} onChange={(event) => setStatus(event.target.value)}>
            <option value="">ทั้งหมด</option>
            <option value="draft">draft</option>
            <option value="published">published</option>
            <option value="confirmed">confirmed</option>
            <option value="cancelled">cancelled</option>
          </select>
        </label>
      </FilterBar>

      {schedulesState.loading ? (
        <div className="page-stack">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="card-skeleton" />
          ))}
        </div>
      ) : grouped.length === 0 ? (
        <EmptyState icon="📅" title="ยังไม่มีตารางสอบในรอบนี้" />
      ) : (
        grouped.map(([date, items]) => (
          <section key={date} className="page-stack">
            <div className="section-heading">
              <h2>{formatDate(date)}</h2>
              <span>{items.length} รายการ</span>
            </div>
            <div className="page-stack">
              {items.map((schedule) => (
                <ScheduleCard key={schedule.id} schedule={schedule} />
              ))}
            </div>
          </section>
        ))
      )}
    </div>
  );
}
