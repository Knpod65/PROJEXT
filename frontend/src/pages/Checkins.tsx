import type React from "react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { PickupQrScanner } from "@/components/checkins/PickupQrScanner";
import { OperationsSummaryCard } from "@/components/attendance/OperationsSummaryCard";
import { RoomOperationsTable } from "@/components/attendance/RoomOperationsTable";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { FilterBar } from "@/components/ui/FilterBar";
import { Icon } from "@/components/ui/Icon";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs } from "@/components/ui/Tabs";
import { useRoomOperationsData } from "@/hooks/useRoomOperationsData";
import {
  confirmCheckin,
  createCheckin,
  getPickupMonitor,
  scanPickupQr,
} from "@/services/checkin.service";
import {
  buildDocumentExportUrl,
  confirmPickupQr,
  getPickupQrStatus,
  regeneratePickupQr,
} from "@/services/documents.service";
import { useAuth } from "@/store/auth.store";
import { useUi } from "@/store/ui.store";
import type {
  CheckinEventItem,
  PickupMonitorRow,
  PickupQrStatusResponse,
  PickupScanResult,
  ScheduleWithSection,
} from "@/types/api";
import { formatDate, formatDateTime, formatNumber } from "@/utils/format";
import { getCurrentPosition } from "@/utils/gps";

function getToday() {
  return new Date().toISOString().slice(0, 10);
}

type CheckinTab = "room_ops" | "pickup_qr";

function getPickupStatusVariant(status: string) {
  switch (status) {
    case "checked_in":
      return "green";
    case "late":
      return "orange";
    case "missed":
      return "crimson";
    default:
      return "gray";
  }
}

export function CheckinsPage() {
  const { toast } = useUi();
  const { user } = useAuth();
  const effectiveRole = user?.effective_role ?? user?.active_role ?? user?.role ?? null;
  const canManagePickup = effectiveRole === "admin" || effectiveRole === "staff";

  const [activeTab, setActiveTab] = useState<CheckinTab>("room_ops");
  const [selectedDate, setSelectedDate] = useState(getToday);
  const [selectedSchedule, setSelectedSchedule] = useState<ScheduleWithSection | null>(null);
  const [studentsPresent, setStudentsPresent] = useState("");
  const [lateCount, setLateCount] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [confirmingId, setConfirmingId] = useState<number | null>(null);
  const [scannerOpen, setScannerOpen] = useState(false);
  const [scannerBusy, setScannerBusy] = useState(false);
  const [lastPickupResult, setLastPickupResult] = useState<PickupScanResult | null>(null);
  const [pickupRows, setPickupRows] = useState<PickupMonitorRow[]>([]);
  const [pickupLoading, setPickupLoading] = useState(false);
  const [pickupError, setPickupError] = useState<string | null>(null);
  const [pickupScheduleId, setPickupScheduleId] = useState<number | null>(null);
  const [pickupDetail, setPickupDetail] = useState<PickupQrStatusResponse | null>(null);
  const [pickupDetailLoading, setPickupDetailLoading] = useState(false);
  const [pickupActionBusy, setPickupActionBusy] = useState<"regenerate" | "confirm" | null>(null);

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

  const pickupStats = useMemo(() => {
    return pickupRows.reduce(
      (totals, row) => {
        totals.total += 1;
        if (row.checkin_status === "checked_in") totals.checkedIn += 1;
        if (row.checkin_status === "late") totals.late += 1;
        if (row.checkin_status === "missed") totals.missed += 1;
        if (row.checkin_status === "not_checked_in") totals.pending += 1;
        return totals;
      },
      { total: 0, checkedIn: 0, late: 0, missed: 0, pending: 0 },
    );
  }, [pickupRows]);

  const refreshPickupMonitor = useCallback(async () => {
    if (!canManagePickup) {
      setPickupRows([]);
      setPickupError(null);
      return;
    }

    setPickupLoading(true);
    setPickupError(null);
    try {
      const data = await getPickupMonitor(selectedDate);
      setPickupRows(data);
    } catch (err) {
      setPickupError(err instanceof Error ? err.message : "Unable to load QR pickup monitoring.");
    } finally {
      setPickupLoading(false);
    }
  }, [canManagePickup, selectedDate]);

  useEffect(() => {
    if (activeTab === "pickup_qr" && canManagePickup) {
      void refreshPickupMonitor();
    }
  }, [activeTab, canManagePickup, refreshPickupMonitor]);

  useEffect(() => {
    if (!pickupScheduleId) {
      setPickupDetail(null);
      return;
    }

    setPickupDetailLoading(true);
    void getPickupQrStatus(pickupScheduleId)
      .then((data) => setPickupDetail(data))
      .catch((err) => {
        toast(err instanceof Error ? err.message : "Unable to load QR details.", "error");
        setPickupDetail(null);
      })
      .finally(() => setPickupDetailLoading(false));
  }, [pickupScheduleId, toast]);

  const handleCreateCheckin = async (event: React.FormEvent<HTMLFormElement>) => {
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

  const handlePickupDetected = async (qrValue: string) => {
    setScannerBusy(true);
    try {
      const result = await scanPickupQr({
        qr_value: qrValue,
        device_metadata: {
          userAgent: navigator.userAgent,
          platform: navigator.platform,
          language: navigator.language,
        },
      });
      setLastPickupResult(result);
      setScannerOpen(false);
      toast(result.message, "success");
      if (canManagePickup) {
        await refreshPickupMonitor();
      }
    } catch (err) {
      toast(err instanceof Error ? err.message : "Unable to confirm QR pickup.", "error");
    } finally {
      setScannerBusy(false);
    }
  };

  const openDocumentExport = (query: Parameters<typeof buildDocumentExportUrl>[0]) => {
    window.open(buildDocumentExportUrl(query), "_blank", "noopener,noreferrer");
  };

  const handleRegeneratePickupQr = async () => {
    if (!pickupScheduleId) return;
    setPickupActionBusy("regenerate");
    try {
      const data = await regeneratePickupQr(pickupScheduleId);
      setPickupDetail(data);
      toast("QR X regenerated. Confirm the new version to activate it.", "success");
      await refreshPickupMonitor();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Unable to regenerate QR X.", "error");
    } finally {
      setPickupActionBusy(null);
    }
  };

  const handleConfirmPickupQr = async () => {
    if (!pickupScheduleId) return;
    setPickupActionBusy("confirm");
    try {
      const qrId = pickupDetail?.latest_qr?.id;
      const data = await confirmPickupQr(pickupScheduleId, qrId);
      setPickupDetail(data);
      toast("The latest QR X is now active.", "success");
      await refreshPickupMonitor();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Unable to confirm the regenerated QR.", "error");
    } finally {
      setPickupActionBusy(null);
    }
  };

  const pickupColumns = useMemo(
    () => [
      {
        key: "date_time",
        label: "Date & time",
        width: "14%",
        render: (row: PickupMonitorRow) => (
          <div className="data-table__content data-table__content--truncate">
            <strong>{formatDate(row.date)}</strong>
            <p>{row.time}</p>
          </div>
        ),
      },
      {
        key: "exam",
        label: "Exam",
        width: "24%",
        render: (row: PickupMonitorRow) => (
          <div className="data-table__content">
            <strong>{row.course_name ?? row.course_code ?? "Untitled exam"}</strong>
            <p>
              {row.course_code ?? "-"} / Section {row.section_no ?? "-"}
            </p>
          </div>
        ),
      },
      {
        key: "room",
        label: "Exam room",
        width: "12%",
        render: (row: PickupMonitorRow) => (
          <div className="data-table__content data-table__content--truncate">
            <strong>{row.room_name ?? "Room pending"}</strong>
            <p>QR X pickup point</p>
          </div>
        ),
      },
      {
        key: "assigned_person",
        label: "Assigned person",
        width: "16%",
        render: (row: PickupMonitorRow) => (
          <div className="data-table__content data-table__content--truncate">
            <strong>{row.assigned_person}</strong>
            <p>{row.role}</p>
          </div>
        ),
      },
      {
        key: "checkin_status",
        label: "Pickup status",
        width: "14%",
        render: (row: PickupMonitorRow) => (
          <div className="data-table__content">
            <Badge variant={getPickupStatusVariant(row.checkin_status)}>
              {row.checkin_status.split("_").join(" ")}
            </Badge>
            <p>{row.checkin_time ? formatDateTime(row.checkin_time) : row.latest_message ?? "Waiting for QR scan"}</p>
          </div>
        ),
      },
      {
        key: "qr",
        label: "QR X",
        width: "10%",
        render: (row: PickupMonitorRow) => (
          <div className="data-table__content data-table__content--truncate">
            <strong>V{row.active_qr_version ?? "-"}</strong>
            <p>{row.has_pending_regeneration ? `Pending V${row.latest_qr_version ?? "-"}` : "Active"}</p>
          </div>
        ),
      },
      {
        key: "actions",
        label: "Actions",
        width: "10%",
        align: "right" as const,
        render: (row: PickupMonitorRow) => (
          <div className="pickup-monitor__actions">
            <Button size="sm" type="button" variant="outline" onClick={() => setPickupScheduleId(row.schedule_id)}>
              Details
            </Button>
          </div>
        ),
      },
    ],
    [],
  );

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
          <span className="page-hero__eyebrow">Room operations + QR pickup</span>
          <h2 className="page-hero__title">Operational check-ins</h2>
          <p className="page-hero__description">
            Manage room updates and QR X exam-paper pickup confirmations from one operational workspace. QR scanning uses the device camera only.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button iconLeft={<Icon name="qr_code_scanner" />} type="button" variant="outline" onClick={() => setScannerOpen(true)}>
            Scan QR
          </Button>
          {canManagePickup ? (
            <Button
              iconLeft={<Icon name="picture_as_pdf" />}
              type="button"
              variant="outline"
              onClick={() => openDocumentExport({ document_type: "all" })}
            >
              Export all documents
            </Button>
          ) : null}
        </div>
      </section>

      <Tabs
        activeKey={activeTab}
        items={[
          { key: "room_ops", label: "Room operations" },
          { key: "pickup_qr", label: "QR pickup", badge: canManagePickup ? pickupStats.pending + pickupStats.missed : undefined },
        ]}
        onChange={(key) => setActiveTab(key as CheckinTab)}
      />

      <FilterBar
        actions={
          <div className="pickup-toolbar">
            <Button iconLeft={<Icon name="refresh" />} type="button" variant="outline" onClick={() => void refresh()}>
              Refresh room ops
            </Button>
            {canManagePickup ? (
              <Button iconLeft={<Icon name="refresh" />} type="button" variant="outline" onClick={() => void refreshPickupMonitor()}>
                Refresh pickup monitor
              </Button>
            ) : null}
          </div>
        }
      >
        <label className="filter-field">
          <span>Operating date</span>
          <input onChange={(event) => setSelectedDate(event.target.value)} type="date" value={selectedDate} />
        </label>
      </FilterBar>

      {activeTab === "room_ops" ? (
        <>
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
        </>
      ) : (
        <>
          <section className="operations-summary-grid">
            <OperationsSummaryCard
              icon="qr_code_scanner"
              label="Assignments"
              note="People expected to confirm pickup for the selected day."
              value={formatNumber(pickupStats.total)}
            />
            <OperationsSummaryCard
              icon="verified"
              label="Checked in"
              note="QR X pickup completed before exam start."
              tone="success"
              value={formatNumber(pickupStats.checkedIn)}
            />
            <OperationsSummaryCard
              icon="warning"
              label="Late / missed"
              note="Assignments that are already late or missed."
              tone="danger"
              value={formatNumber(pickupStats.late + pickupStats.missed)}
            />
            <OperationsSummaryCard
              icon="pending_actions"
              label="Pending"
              note="Still waiting for a camera-based QR scan."
              tone="neutral"
              value={formatNumber(pickupStats.pending)}
            />
          </section>

          {lastPickupResult ? (
            <section className="pickup-result-card ui-card">
              <div className="ui-card__body pickup-result-card__body">
                <div>
                  <span className="pickup-result-card__eyebrow">Latest QR pickup confirmation</span>
                  <h3>{lastPickupResult.schedule.course_code ?? "Exam assignment"}</h3>
                  <p>{lastPickupResult.message}</p>
                </div>
                <div className="pickup-result-card__meta">
                  <span>{lastPickupResult.schedule.room_name ?? "Room pending"}</span>
                  <span>{lastPickupResult.checked_in_at ? formatDateTime(lastPickupResult.checked_in_at) : "Just confirmed"}</span>
                </div>
              </div>
            </section>
          ) : null}

          {!canManagePickup ? (
            <EmptyState
              icon={<Icon name="qr_code_scanner" />}
              title="Camera-based QR pickup"
              description="Use Scan QR when you arrive to receive exam papers for your assigned room. Image upload is disabled by policy."
            />
          ) : pickupLoading ? (
            <div className="page-stack">
              {Array.from({ length: 2 }).map((_, index) => (
                <Skeleton key={index} className="card-skeleton" />
              ))}
            </div>
          ) : pickupError ? (
            <EmptyState icon={<Icon name="warning" />} title="Unable to load QR pickup monitor." description={pickupError} />
          ) : pickupRows.length === 0 ? (
            <EmptyState
              icon={<Icon name="inventory_2" />}
              title="No pickup assignments for this date."
              description="Choose another date or confirm the exam workflow first."
            />
          ) : (
            <DataTable<PickupMonitorRow>
              columns={pickupColumns}
              rows={pickupRows}
              rowKey={(row) => `${row.schedule_id}-${row.assigned_person}-${row.role}`}
              compact
              tableLayout="fixed"
              scrollThreshold={5}
              maxHeight={420}
            />
          )}
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

      <Modal
        open={Boolean(pickupScheduleId)}
        title={pickupDetail?.schedule.course_code ? `Pickup QR X for ${pickupDetail.schedule.course_code}` : "Pickup QR X"}
        onClose={() => setPickupScheduleId(null)}
      >
        {pickupDetailLoading ? (
          <div className="page-stack">
            <Skeleton className="card-skeleton" />
            <Skeleton className="card-skeleton" />
          </div>
        ) : pickupDetail ? (
          <div className="page-stack">
            <section className="pickup-detail-grid">
              <div className="pickup-detail-tile">
                <span>Course</span>
                <strong>{pickupDetail.schedule.course_code ?? "-"}</strong>
                <p>{pickupDetail.schedule.course_name ?? "Course name pending"}</p>
              </div>
              <div className="pickup-detail-tile">
                <span>Exam slot</span>
                <strong>{pickupDetail.schedule.exam_time ?? "-"}</strong>
                <p>{pickupDetail.schedule.exam_date ? formatDate(pickupDetail.schedule.exam_date) : "Date pending"}</p>
              </div>
              <div className="pickup-detail-tile">
                <span>Exam room</span>
                <strong>{pickupDetail.schedule.room_name ?? "-"}</strong>
                <p>QR X is bound to this confirmed room only.</p>
              </div>
            </section>

            <section className="pickup-qr-status-card ui-card">
              <div className="ui-card__body page-stack">
                <div className="pickup-qr-status-card__row">
                  <div>
                    <span className="pickup-result-card__eyebrow">Active QR X</span>
                    <h3>Version {pickupDetail.active_qr?.version ?? "-"}</h3>
                    <p>
                      {pickupDetail.active_qr?.confirmed_at
                        ? `Confirmed ${formatDateTime(pickupDetail.active_qr.confirmed_at)}`
                        : "No active QR confirmed yet."}
                    </p>
                  </div>
                  <div>
                    <span className="pickup-result-card__eyebrow">Latest QR X</span>
                    <h3>Version {pickupDetail.latest_qr?.version ?? "-"}</h3>
                    <p>{pickupDetail.has_pending_regeneration ? "Waiting for confirmation" : "Already active"}</p>
                  </div>
                </div>
                <div className="pickup-qr-status-card__actions">
                  <Button type="button" variant="outline" onClick={() => openDocumentExport({ schedule_id: pickupScheduleId ?? undefined, document_type: "all" })}>
                    Export all documents
                  </Button>
                  <Button type="button" variant="outline" onClick={() => openDocumentExport({ schedule_id: pickupScheduleId ?? undefined, document_type: "participant_codes" })}>
                    Participant codes
                  </Button>
                  <Button type="button" variant="outline" onClick={() => openDocumentExport({ schedule_id: pickupScheduleId ?? undefined, document_type: "signature_sheet" })}>
                    Signature sheet
                  </Button>
                  <Button type="button" variant="outline" onClick={() => openDocumentExport({ schedule_id: pickupScheduleId ?? undefined, document_type: "envelope_cover" })}>
                    Cover sheet
                  </Button>
                  {canManagePickup ? (
                    <Button type="button" variant="ghost" loading={pickupActionBusy === "regenerate"} onClick={() => void handleRegeneratePickupQr()}>
                      Regenerate QR X
                    </Button>
                  ) : null}
                  {canManagePickup && pickupDetail.has_pending_regeneration ? (
                    <Button type="button" loading={pickupActionBusy === "confirm"} onClick={() => void handleConfirmPickupQr()}>
                      Confirm regenerated QR X
                    </Button>
                  ) : null}
                </div>
                <p className="pickup-qr-status-card__note">
                  QR Y stays as a separate regulation/method placeholder on the envelope cover and is not used for pickup confirmation.
                </p>
              </div>
            </section>

            <section className="pickup-assignment-list">
              <h3>Assigned pickup personnel</h3>
              {pickupDetail.assignments.length === 0 ? (
                <p>No invigilator or pickup assignments were found for this exam yet.</p>
              ) : (
                <div className="pickup-assignment-list__grid">
                  {pickupDetail.assignments.map((assignment) => (
                    <div key={`${assignment.user_id}-${assignment.role}`} className="pickup-assignment-list__item">
                      <strong>{assignment.full_name}</strong>
                      <span>{assignment.role}</span>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        ) : (
          <EmptyState icon={<Icon name="qr_code" />} title="No QR details available." description="Select another assignment or regenerate QR X." />
        )}
      </Modal>

      <PickupQrScanner open={scannerOpen} busy={scannerBusy} onClose={() => setScannerOpen(false)} onDetected={handlePickupDetected} />
    </div>
  );
}
