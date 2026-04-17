import { useMemo, useState, type FormEvent } from "react";

import { OperationsSummaryCard } from "@/components/attendance/OperationsSummaryCard";
import { RoomOperationsTable } from "@/components/attendance/RoomOperationsTable";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { FilterBar } from "@/components/ui/FilterBar";
import { Icon } from "@/components/ui/Icon";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { useRoomOperationsData } from "@/hooks/useRoomOperationsData";
import { confirmCheckin, createCheckin } from "@/services/checkin.service";
import { useUi } from "@/store/ui.store";
import type { CheckinEventItem, ScheduleWithSection } from "@/types/api";
import { formatDateTime, formatNumber } from "@/utils/format";
import { getCurrentPosition } from "@/utils/gps";

function getToday() {
  return new Date().toISOString().slice(0, 10);
}

export function CheckinsPage() {
  const { toast } = useUi();
  const [selectedDate, setSelectedDate] = useState(getToday);
  const [selectedSchedule, setSelectedSchedule] = useState<ScheduleWithSection | null>(null);
  const [studentsPresent, setStudentsPresent] = useState("");
  const [lateCount, setLateCount] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [confirmingId, setConfirmingId] = useState<number | null>(null);
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
  const checkedInCount = rows.filter((row) => row.events.length > 0).length;
  const confirmedCount = rows.filter((row) => row.events[0]?.confirmed || row.events[0]?.confirmed_by_all).length;
  const pendingCount = rows.filter((row) => row.events[0] && !row.events[0]?.confirmed && !row.events[0]?.confirmed_by_all).length;

  const handleCreateCheckin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedSchedule) return;

    setSubmitting(true);
    try {
      const position = await getCurrentPosition({ enableHighAccuracy: true, timeout: 8_000 });
      await createCheckin({
        schedule_id: selectedSchedule.id,
        checkin_type: "at_room",
        students_present: studentsPresent ? Number(studentsPresent) : undefined,
        late_count: lateCount ? Number(lateCount) : undefined,
        notes: `${notes}\nGPS: ${position.coords.latitude.toFixed(6)}, ${position.coords.longitude.toFixed(6)}`.trim(),
      });

      toast("Check-in recorded.", "success");
      setStudentsPresent("");
      setLateCount("");
      setNotes("");
      setSelectedSchedule(null);
      await refresh();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Unable to record check-in.", "error");
    } finally {
      setSubmitting(false);
    }
  };

  const handleConfirmLatest = async (item: CheckinEventItem) => {
    setConfirmingId(item.id);
    try {
      await confirmCheckin(item.id);
      toast("Check-in confirmed.", "success");
      await refresh();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Unable to confirm this check-in.", "error");
    } finally {
      setConfirmingId(null);
    }
  };

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
          <span className="page-hero__eyebrow">Room operations mode</span>
          <h2 className="page-hero__title">Operational check-ins</h2>
          <p className="page-hero__description">
            This mode reuses the shared room-operations family for action taking: create check-ins, confirm the latest update, and monitor room readiness in one flow.
          </p>
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

      {error ? <EmptyState icon={<Icon name="warning" />} title="Unable to load check-in data." description={error} /> : null}

      {rows.length === 0 ? (
        <EmptyState
          icon={<Icon name="how_to_reg" />}
          title="No sessions found for this date."
          description="Pick another date or check whether schedules have been assigned yet."
        />
      ) : (
        <>
          <section className="operations-summary-grid">
            <OperationsSummaryCard
              icon="calendar_today"
              label="Sessions"
              note="All scheduled rows for the selected day."
              value={formatNumber(rows.length)}
            />
            <OperationsSummaryCard
              icon="how_to_reg"
              label="Checked in"
              note="Sessions with at least one check-in event."
              tone="success"
              value={formatNumber(checkedInCount)}
            />
            <OperationsSummaryCard
              icon="pending_actions"
              label="Pending confirm"
              note="Latest check-in exists but still needs confirmation."
              tone="neutral"
              value={formatNumber(pendingCount)}
            />
            <OperationsSummaryCard
              icon="verified"
              label="Confirmed"
              note="Latest room report is already confirmed."
              tone="accent"
              value={formatNumber(confirmedCount)}
            />
          </section>

          <RoomOperationsTable
            confirmingId={confirmingId}
            mode="checkins"
            rows={rows}
            onConfirmLatest={handleConfirmLatest}
            onOpenDetails={setSelectedSchedule}
            onPrimaryAction={setSelectedSchedule}
          />
        </>
      )}

      <Modal
        open={Boolean(selectedSchedule)}
        title={selectedSchedule ? `Check-in update for ${selectedSchedule.room?.room_name ?? "assigned room"}` : "Check-in update"}
        onClose={() => setSelectedSchedule(null)}
      >
        <form className="page-stack" onSubmit={handleCreateCheckin}>
          <label className="form-field">
            <span>Students present</span>
            <input
              inputMode="numeric"
              onChange={(event) => setStudentsPresent(event.target.value)}
              placeholder="e.g. 28"
              value={studentsPresent}
            />
          </label>
          <label className="form-field">
            <span>Late count</span>
            <input
              inputMode="numeric"
              onChange={(event) => setLateCount(event.target.value)}
              placeholder="e.g. 2"
              value={lateCount}
            />
          </label>
          <label className="form-field">
            <span>Notes</span>
            <textarea
              onChange={(event) => setNotes(event.target.value)}
              placeholder="Add room notes, incidents, or readiness details"
              rows={4}
              value={notes}
            />
          </label>
          <Button loading={submitting} type="submit">
            Save check-in
          </Button>
        </form>

        {selectedEvents.length > 0 ? (
          <div className="checkin-history">
            <h3>Recent check-in history</h3>
            {selectedEvents.map((item) => (
              <div key={item.id} className="checkin-history__item">
                <strong>{item.user ?? "EMS user"}</strong>
                <span>{formatDateTime(item.checked_in_at)}</span>
                <span>
                  Present {formatNumber(item.students_present ?? 0)} / Late {formatNumber(item.late_count ?? 0)}
                </span>
                <p>{item.notes ?? "No notes attached."}</p>
              </div>
            ))}
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
