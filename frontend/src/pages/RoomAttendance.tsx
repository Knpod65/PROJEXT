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
import { useI18n } from "@/i18n";
import type { ScheduleWithSection } from "@/types/api";
import { formatDate, formatDateTime, formatNumber } from "@/utils/format";

function getToday() {
  return new Date().toISOString().slice(0, 10);
}

export function RoomAttendancePage() {
  const { t } = useI18n();
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
          <span className="page-hero__eyebrow">{t("attendance.heroEyebrow")}</span>
          <h2 className="page-hero__title">{t("attendance.heroTitle")}</h2>
          <p className="page-hero__description">{t("attendance.heroDescription")}</p>
        </div>
        <div className="page-hero__actions">
          <Button iconLeft={<Icon name="how_to_reg" />} type="button" onClick={() => navigate("/checkins")}>
            {t("attendance.openCheckins")}
          </Button>
        </div>
      </section>

      <FilterBar
        actions={
          <Button iconLeft={<Icon name="refresh" />} type="button" variant="outline" onClick={() => void refresh()}>
            {t("common.refresh")}
          </Button>
        }
      >
        <label className="filter-field">
          <span>{t("attendance.operatingDate")}</span>
          <input onChange={(event) => setSelectedDate(event.target.value)} type="date" value={selectedDate} />
        </label>
      </FilterBar>

      {error ? <EmptyState icon={<Icon name="warning" />} title={t("attendance.loadError")} description={error} /> : null}

      {rows.length === 0 ? (
        <EmptyState
          icon={<Icon name="assignment_ind" />}
          title={t("attendance.emptyTitle")}
          description={t("attendance.emptyDescription")}
        />
      ) : (
        <>
          <section className="operations-summary-grid">
            <OperationsSummaryCard
              icon="meeting_room"
              label={t("attendance.stats.roomsActive")}
              note={t("attendance.stats.roomsActiveNote")}
              value={formatNumber(roomCount)}
            />
            <OperationsSummaryCard
              icon="how_to_reg"
              label={t("attendance.stats.studentsPresent")}
              note={t("attendance.stats.studentsPresentNote")}
              tone="success"
              value={formatNumber(presentCount)}
            />
            <OperationsSummaryCard
              icon="person_off"
              label={t("attendance.stats.studentsAbsent")}
              note={t("attendance.stats.studentsAbsentNote")}
              tone="danger"
              value={formatNumber(absentCount)}
            />
            <OperationsSummaryCard
              icon="hourglass_top"
              label={t("attendance.stats.awaitingUpdate")}
              note={t("attendance.stats.awaitingUpdateNote")}
              tone="neutral"
              value={formatNumber(uncheckedCount)}
            />
          </section>

          <RoomOperationsTable mode="attendance" rows={rows} onOpenDetails={setSelectedSchedule} />
        </>
      )}

      <Modal
        open={Boolean(selectedSchedule)}
        title={
          selectedSchedule
            ? t("attendance.modal.titleWithRoom", { room: selectedSchedule.room?.room_name ?? t("common.room") })
            : t("attendance.modal.title")
        }
        onClose={() => setSelectedSchedule(null)}
      >
        {selectedSchedule ? (
          <div className="page-stack">
            <div className="attendance-detail-grid">
              <div className="attendance-detail-card">
                <span>{t("common.date")}</span>
                <strong>{formatDate(selectedSchedule.exam_date)}</strong>
              </div>
              <div className="attendance-detail-card">
                <span>{t("common.time")}</span>
                <strong>{selectedSchedule.exam_time}</strong>
              </div>
              <div className="attendance-detail-card">
                <span>{t("common.course")}</span>
                <strong>{selectedSchedule.section?.course?.course_id ?? t("attendance.modal.pendingCourse")}</strong>
              </div>
              <div className="attendance-detail-card">
                <span>{t("common.section")}</span>
                <strong>{selectedSchedule.section?.section_no ?? "-"}</strong>
              </div>
            </div>

            <div className="attendance-detail-block">
              <h3>{t("attendance.modal.invigilationCoverage")}</h3>
              <div className="tag-list">
                {selectedSchedule.supervisions.length === 0 ? (
                  <span className="tag-list__item">{t("attendance.modal.noInvigilators")}</span>
                ) : (
                  selectedSchedule.supervisions.map((item) => (
                    <span key={item.id} className="tag-list__item">
                      {item.user?.full_name ?? item.user?.username ?? item.role_in_exam ?? t("common.staff")}
                      <Badge size="sm" variant={item.confirmed ? "green" : "gray"}>
                        {item.confirmed ? t("common.confirmed") : t("common.pending")}
                      </Badge>
                    </span>
                  ))
                )}
              </div>
            </div>

            <div className="attendance-detail-block">
              <h3>{t("attendance.modal.roomHistory")}</h3>
              {selectedEvents.length === 0 ? (
                <EmptyState icon={<Icon name="history" />} title={t("attendance.modal.noHistory")} />
              ) : (
                <div className="checkin-history">
                  {selectedEvents.map((item) => (
                    <div key={item.id} className="checkin-history__item">
                      <strong>{item.user ?? t("attendance.modal.emsUser")}</strong>
                      <span>{formatDateTime(item.checked_in_at)}</span>
                      <span>
                        {t("attendance.modal.presentAbsent", {
                          present: formatNumber(item.students_present ?? 0),
                          absent: formatNumber(item.absent_count ?? 0),
                        })}
                      </span>
                      <p>{item.notes ?? t("attendance.modal.noNotes")}</p>
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
