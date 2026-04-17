import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { OperationsSummaryCard } from "@/components/attendance/OperationsSummaryCard";
import { RoomOperationsTable } from "@/components/attendance/RoomOperationsTable";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { FilterBar } from "@/components/ui/FilterBar";
import { Icon } from "@/components/ui/Icon";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { useRoomOperationsData } from "@/hooks/useRoomOperationsData";
import type { ScheduleWithSection } from "@/types/api";
import { formatDate, formatDateTime, formatNumber } from "@/utils/format";

function getToday() {
  return new Date().toISOString().slice(0, 10);
}

export function RoomAttendancePage() {
  const navigate = useNavigate();
  const [selectedDate, setSelectedDate] = useState(getToday);
  const [selectedSchedule, setSelectedSchedule] = useState<ScheduleWithSection | null>(null);
  const { error, events, loading, refresh, schedules } = useRoomOperationsData(selectedDate);

  const rows = useMemo(
    () =>
      schedules
        .map((schedule) => ({
          schedule,
          events: events[String(schedule.id)] ?? [],
        }))
        .sort((left, right) => left.schedule.exam_time.localeCompare(right.schedule.exam_time)),
    [events, schedules],
  );

  const selectedEvents = selectedSchedule ? events[String(selectedSchedule.id)] ?? [] : [];
  const roomCount = new Set(rows.map((row) => row.schedule.room?.room_name ?? `room-${row.schedule.id}`)).size;
  const presentCount = rows.reduce((total, row) => total + (row.events[0]?.students_present ?? 0), 0);
  const absentCount = rows.reduce((total, row) => total + (row.events[0]?.absent_count ?? 0), 0);
  const uncheckedCount = rows.filter((row) => row.events.length === 0).length;

  if (loading) {
    return (
      <div className="page-stack">
        {Array.from({ length: 3 }).map((_, index) => (
          <Skeleton key={index} className="card-skeleton" />
        ))}
      </div>
    );
  }

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero page-hero--attendance">
        <div>
          <span className="page-hero__eyebrow">Assigned venue overview</span>
          <h2 className="page-hero__title">Daily room attendance</h2>
          <p className="page-hero__description">
            The staff room overview Stitch pattern is now the shared read-focused room operations page. It keeps real EMS schedules and check-in relationships while presenting a cleaner venue-first summary.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button iconLeft={<Icon name="how_to_reg" />} type="button" onClick={() => navigate("/checkins")}>
            Open check-ins
          </Button>
        </div>
      </section>

      <FilterBar
        actions={
          <Button iconLeft={<Icon name="refresh" />} type="button" variant="outline" onClick={() => void refresh()}>
            Refresh
          </Button>
        }
      >
        <label className="filter-field">
          <span>Operating date</span>
          <input onChange={(event) => setSelectedDate(event.target.value)} type="date" value={selectedDate} />
        </label>
      </FilterBar>

      {error ? <EmptyState icon={<Icon name="warning" />} title="Unable to load room attendance." description={error} /> : null}

      {rows.length === 0 ? (
        <EmptyState
          icon={<Icon name="assignment_ind" />}
          title="No room attendance data found for this date."
          description="Try another date or return after schedules and check-ins have been recorded."
        />
      ) : (
        <>
          <section className="operations-summary-grid">
            <OperationsSummaryCard
              icon="meeting_room"
              label="Rooms active"
              note="Unique rooms carrying sessions for the selected date."
              value={formatNumber(roomCount)}
            />
            <OperationsSummaryCard
              icon="how_to_reg"
              label="Students present"
              note="Latest room check-ins aggregated across visible sessions."
              tone="success"
              value={formatNumber(presentCount)}
            />
            <OperationsSummaryCard
              icon="person_off"
              label="Students absent"
              note="Latest reported absence count across the selected day."
              tone="danger"
              value={formatNumber(absentCount)}
            />
            <OperationsSummaryCard
              icon="hourglass_top"
              label="Awaiting update"
              note="Sessions still missing a room check-in."
              tone="neutral"
              value={formatNumber(uncheckedCount)}
            />
          </section>

          <RoomOperationsTable mode="attendance" rows={rows} onOpenDetails={setSelectedSchedule} />
        </>
      )}

      <Modal
        open={Boolean(selectedSchedule)}
        title={selectedSchedule ? `${selectedSchedule.room?.room_name ?? "Room"} attendance detail` : "Attendance detail"}
        onClose={() => setSelectedSchedule(null)}
      >
        {selectedSchedule ? (
          <div className="page-stack">
            <div className="attendance-detail-grid">
              <div className="attendance-detail-card">
                <span>Date</span>
                <strong>{formatDate(selectedSchedule.exam_date)}</strong>
              </div>
              <div className="attendance-detail-card">
                <span>Time</span>
                <strong>{selectedSchedule.exam_time}</strong>
              </div>
              <div className="attendance-detail-card">
                <span>Course</span>
                <strong>{selectedSchedule.section?.course?.course_id ?? "Pending course"}</strong>
              </div>
              <div className="attendance-detail-card">
                <span>Section</span>
                <strong>{selectedSchedule.section?.section_no ?? "-"}</strong>
              </div>
            </div>

            <div className="attendance-detail-block">
              <h3>Invigilation coverage</h3>
              <div className="tag-list">
                {selectedSchedule.supervisions.length === 0 ? (
                  <span className="tag-list__item">No invigilators assigned</span>
                ) : (
                  selectedSchedule.supervisions.map((item) => (
                    <span key={item.id} className="tag-list__item">
                      {item.user?.full_name ?? item.user?.username ?? item.role_in_exam ?? "Staff"}
                      <Badge size="sm" variant={item.confirmed ? "green" : "gray"}>
                        {item.confirmed ? "Confirmed" : "Pending"}
                      </Badge>
                    </span>
                  ))
                )}
              </div>
            </div>

            <div className="attendance-detail-block">
              <h3>Room history</h3>
              {selectedEvents.length === 0 ? (
                <EmptyState icon={<Icon name="history" />} title="No room history yet." />
              ) : (
                <div className="checkin-history">
                  {selectedEvents.map((item) => (
                    <div key={item.id} className="checkin-history__item">
                      <strong>{item.user ?? "EMS user"}</strong>
                      <span>{formatDateTime(item.checked_in_at)}</span>
                      <span>
                        Present {formatNumber(item.students_present ?? 0)} / Absent {formatNumber(item.absent_count ?? 0)}
                      </span>
                      <p>{item.notes ?? "No notes attached."}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
