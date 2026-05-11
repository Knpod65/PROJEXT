import { useCallback, useMemo, useState } from "react";

import { ScheduleSummaryCard } from "@/components/schedule/ScheduleSummaryCard";
import { ScheduleTable } from "@/components/schedule/ScheduleTable";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { FilterBar } from "@/components/ui/FilterBar";
import { Icon } from "@/components/ui/Icon";
import { Skeleton } from "@/components/ui/Skeleton";
import { useAsyncData } from "@/hooks/useAsyncData";
import { buildDocumentExportUrl } from "@/services/documents.service";
import { getRooms, listSchedules } from "@/services/schedule.service";
import { useAuth } from "@/store/auth.store";
import type { ScheduleWithSection } from "@/types/api";
import { formatDate, formatNumber } from "@/utils/format";
import { getEffectiveRole } from "@/utils/roles";

type ViewMode = "date" | "room";

export function SchedulePage() {
  const { user } = useAuth();
  const effectiveRole = getEffectiveRole(user);
  const canExportOperationalDocs = effectiveRole === "admin" || effectiveRole === "staff";
  const [roomId, setRoomId] = useState("");
  const [status, setStatus] = useState("");
  const [selectedDate, setSelectedDate] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<ViewMode>("date");

  const roomsLoader = useCallback(() => getRooms(), []);
  const schedulesLoader = useCallback(
    () =>
      listSchedules({
        date: selectedDate || undefined,
        room_id: roomId ? Number(roomId) : undefined,
        status: status || undefined,
      }),
    [roomId, selectedDate, status],
  );

  const roomsState = useAsyncData(roomsLoader, [roomsLoader]);
  const schedulesState = useAsyncData(schedulesLoader, [schedulesLoader]);

  const filteredSchedules = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    return (schedulesState.data ?? []).filter((schedule) => {
      if (!query) {
        return true;
      }

      const haystack = [
        schedule.section?.course?.course_id,
        schedule.section?.course?.course_name_th,
        schedule.room?.room_name,
        schedule.room?.building,
        schedule.section?.teaching_room?.room_name,
        schedule.section?.teacher?.full_name,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return haystack.includes(query);
    });
  }, [schedulesState.data, searchQuery]);

  const groupedBoards = useMemo(() => {
    const groups = new Map<string, ScheduleWithSection[]>();

    filteredSchedules.forEach((schedule) => {
      const key = viewMode === "date" ? schedule.exam_date : schedule.room?.room_name ?? "Exam room not assigned yet";
      const items = groups.get(key) ?? [];
      items.push(schedule);
      groups.set(key, items);
    });

    return Array.from(groups.entries()).map(([key, items]) => ({
      key,
      title: viewMode === "date" ? formatDate(key) : key,
      subtitle:
        viewMode === "date"
          ? `${items.length} sessions scheduled for this date`
          : `${items.length} sessions assigned to this exam room`,
      items,
    }));
  }, [filteredSchedules, viewMode]);

  const confirmedCount = filteredSchedules.filter((item) => item.status === "confirmed").length;
  const publishedCount = filteredSchedules.filter((item) => item.status === "published").length;
  const draftCount = filteredSchedules.filter((item) => item.status === "draft").length;
  const totalSheets = filteredSchedules.reduce((total, item) => total + item.total_sheets, 0);

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">Master schedule oversight</span>
          <h2 className="page-hero__title">Reusable schedule board</h2>
          <p className="page-hero__description">
            This page adapts the chosen admin master schedule Stitch export into a reusable EMS board with real filtering, grouped tables, and the working export endpoints.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button
            iconLeft={<Icon name="download" />}
            type="button"
            variant="outline"
            onClick={() => window.open("/api/exports/schedule-excel", "_blank")}
          >
            Export Excel
          </Button>
          <Button
            iconLeft={<Icon name="picture_as_pdf" />}
            type="button"
            variant="outline"
            onClick={() => window.open("/api/exports/schedule", "_blank")}
          >
            Export PDF
          </Button>
          {canExportOperationalDocs ? (
            <>
              <Button
                iconLeft={<Icon name="inventory_2" />}
                type="button"
                variant="outline"
                onClick={() => window.open(buildDocumentExportUrl({ document_type: "all" }), "_blank")}
              >
                Generate Exam Documents
              </Button>
              <Button
                iconLeft={<Icon name="qr_code" />}
                type="button"
                variant="outline"
                onClick={() => window.open(buildDocumentExportUrl({ document_type: "envelope_cover" }), "_blank")}
              >
                Export Cover Sheets
              </Button>
            </>
          ) : null}
        </div>
      </section>

      <FilterBar
        actions={
          <div className="view-toggle">
            <Button type="button" variant={viewMode === "date" ? "primary" : "ghost"} onClick={() => setViewMode("date")}>
              Group by date
            </Button>
            <Button type="button" variant={viewMode === "room" ? "primary" : "ghost"} onClick={() => setViewMode("room")}>
              Group by exam room
            </Button>
          </div>
        }
      >
        <label className="filter-field">
          <span>Search</span>
          <input
            onChange={(event) => setSearchQuery(event.target.value)}
            placeholder="Search course, exam room, teaching room, or teacher"
            value={searchQuery}
          />
        </label>
        <label className="filter-field">
          <span>Date</span>
          <input onChange={(event) => setSelectedDate(event.target.value)} type="date" value={selectedDate} />
        </label>
        <label className="filter-field">
          <span>Exam room</span>
          <select value={roomId} onChange={(event) => setRoomId(event.target.value)}>
            <option value="">All rooms</option>
            {(roomsState.data ?? []).map((room) => (
              <option key={room.id} value={room.id}>
                {room.room_name}
              </option>
            ))}
          </select>
        </label>
        <label className="filter-field">
          <span>Status</span>
          <select value={status} onChange={(event) => setStatus(event.target.value)}>
            <option value="">All statuses</option>
            <option value="draft">Draft</option>
            <option value="published">Published</option>
            <option value="confirmed">Confirmed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </label>
      </FilterBar>

      {schedulesState.loading ? (
        <div className="page-stack">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="card-skeleton" />
          ))}
        </div>
      ) : groupedBoards.length === 0 ? (
        <EmptyState
          icon={<Icon name="calendar_today" />}
          title="No schedule sessions match these filters."
          description="Try clearing the room, date, or status filters to widen the result set."
        />
      ) : (
        <>
          <section className="schedule-summary-grid">
            <ScheduleSummaryCard
              hint="Sessions visible in the current board"
              icon="event_note"
              label="Total sessions"
              value={formatNumber(filteredSchedules.length)}
            />
            <ScheduleSummaryCard
              hint="Published schedule rows"
              icon="publish"
              label="Published"
              value={formatNumber(publishedCount)}
            />
            <ScheduleSummaryCard
              hint="Confirmed invigilation-ready rows"
              icon="verified"
              label="Confirmed"
              value={formatNumber(confirmedCount)}
            />
            <ScheduleSummaryCard
              hint={`${formatNumber(draftCount)} draft sessions pending`}
              icon="print"
              label="Sheets required"
              value={formatNumber(totalSheets)}
            />
          </section>

          <div className="page-stack">
            {groupedBoards.map((group) => (
              <ScheduleTable key={group.key} items={group.items} subtitle={group.subtitle} title={group.title} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
