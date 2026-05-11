import type React from "react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { OperationsSummaryCard } from "@/components/attendance/OperationsSummaryCard";
import { PickupQrScanner } from "@/components/checkins/PickupQrScanner";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { FilterBar } from "@/components/ui/FilterBar";
import { Icon } from "@/components/ui/Icon";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs } from "@/components/ui/Tabs";
import { RoomOperationsTable } from "@/components/attendance/RoomOperationsTable";
import { useRoomOperationsData } from "@/hooks/useRoomOperationsData";
import { useI18n } from "@/i18n";
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
import { formatDate, formatDateTime, formatNumber, formatTranslatedValue } from "@/utils/format";
import { getEffectiveRole } from "@/utils/roles";
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

function getPickupStatusLabel(t: ReturnType<typeof useI18n>["t"], status: string) {
  switch (status) {
    case "checked_in":
    case "late":
    case "missed":
    case "not_checked_in":
      return t(`checkins.pickupStatus.${status}`);
    default:
      return status;
  }
}

export function CheckinsPage() {
  const { t } = useI18n();
  const { toast } = useUi();
  const { user } = useAuth();
  const effectiveRole = getEffectiveRole(user);
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
      setPickupError(err instanceof Error ? err.message : t("checkins.toast.pickupMonitorLoadFailed"));
    } finally {
      setPickupLoading(false);
    }
  }, [canManagePickup, selectedDate, t]);

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
        toast(err instanceof Error ? err.message : t("checkins.toast.pickupDetailLoadFailed"), "error");
        setPickupDetail(null);
      })
      .finally(() => setPickupDetailLoading(false));
  }, [pickupScheduleId, t, toast]);

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

      toast(t("checkins.toast.checkinRecorded"), "success");
      setStudentsPresent("");
      setLateCount("");
      setNotes("");
      setSelectedSchedule(null);
      await refresh();
    } catch (err) {
      toast(err instanceof Error ? err.message : t("checkins.toast.checkinFailed"), "error");
    } finally {
      setSubmitting(false);
    }
  };

  const handleConfirmLatest = async (item: CheckinEventItem) => {
    setConfirmingId(item.id);
    try {
      await confirmCheckin(item.id);
      toast(t("checkins.toast.checkinConfirmed"), "success");
      await refresh();
    } catch (err) {
      toast(err instanceof Error ? err.message : t("checkins.toast.confirmFailed"), "error");
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
      toast(err instanceof Error ? err.message : t("checkins.toast.qrConfirmFailed"), "error");
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
      toast(t("checkins.toast.qrRegenerated"), "success");
      await refreshPickupMonitor();
    } catch (err) {
      toast(err instanceof Error ? err.message : t("checkins.toast.qrRegenerateFailed"), "error");
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
      toast(t("checkins.toast.qrActivated"), "success");
      await refreshPickupMonitor();
    } catch (err) {
      toast(err instanceof Error ? err.message : t("checkins.toast.qrActivateFailed"), "error");
    } finally {
      setPickupActionBusy(null);
    }
  };

  const pickupColumns = useMemo(
    () => [
      {
        key: "date_time",
        label: t("checkins.pickupTable.dateTime"),
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
        label: t("checkins.pickupTable.exam"),
        width: "24%",
        render: (row: PickupMonitorRow) => (
          <div className="data-table__content">
            <strong>{row.course_name ?? row.course_code ?? t("checkins.pickupTable.untitledExam")}</strong>
            <p>{t("checkins.pickupTable.courseSection", { course: row.course_code ?? "-", section: row.section_no ?? "-" })}</p>
          </div>
        ),
      },
      {
        key: "room",
        label: t("checkins.pickupTable.examRoom"),
        width: "12%",
        render: (row: PickupMonitorRow) => (
          <div className="data-table__content data-table__content--truncate">
            <strong>{row.room_name ?? t("checkins.pickupTable.roomPending")}</strong>
            <p>{t("checkins.pickupTable.pickupPoint")}</p>
          </div>
        ),
      },
      {
        key: "assigned_person",
        label: t("checkins.pickupTable.assignedPerson"),
        width: "16%",
        render: (row: PickupMonitorRow) => (
          <div className="data-table__content data-table__content--truncate">
            <strong>{row.assigned_person}</strong>
            <p>{formatTranslatedValue("roles", row.role)}</p>
          </div>
        ),
      },
      {
        key: "checkin_status",
        label: t("checkins.pickupTable.pickupStatus"),
        width: "14%",
        render: (row: PickupMonitorRow) => (
          <div className="data-table__content">
            <Badge variant={getPickupStatusVariant(row.checkin_status)}>
              {getPickupStatusLabel(t, row.checkin_status)}
            </Badge>
            <p>{row.checkin_time ? formatDateTime(row.checkin_time) : row.latest_message ?? t("checkins.pickupTable.waitingForScan")}</p>
          </div>
        ),
      },
      {
        key: "qr",
        label: t("checkins.pickupTable.qrX"),
        width: "10%",
        render: (row: PickupMonitorRow) => (
          <div className="data-table__content data-table__content--truncate">
            <strong>{t("checkins.pickupTable.version", { version: row.active_qr_version ?? "-" })}</strong>
            <p>{row.has_pending_regeneration ? t("checkins.pickupTable.pendingVersion", { version: row.latest_qr_version ?? "-" }) : t("checkins.pickupTable.active")}</p>
          </div>
        ),
      },
      {
        key: "actions",
        label: t("common.actions"),
        width: "10%",
        align: "right" as const,
        render: (row: PickupMonitorRow) => (
          <div className="pickup-monitor__actions">
            <Button size="sm" type="button" variant="outline" onClick={() => setPickupScheduleId(row.schedule_id)}>
              {t("common.details")}
            </Button>
          </div>
        ),
      },
    ],
    [t],
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
          <span className="page-hero__eyebrow">{t("checkins.heroEyebrow")}</span>
          <h2 className="page-hero__title">{t("checkins.heroTitle")}</h2>
          <p className="page-hero__description">{t("checkins.heroDescription")}</p>
        </div>
        <div className="page-hero__actions">
          <Button iconLeft={<Icon name="qr_code_scanner" />} type="button" variant="outline" onClick={() => setScannerOpen(true)}>
            {t("checkins.actions.scanQr")}
          </Button>
          {canManagePickup ? (
            <Button
              iconLeft={<Icon name="picture_as_pdf" />}
              type="button"
              variant="outline"
              onClick={() => openDocumentExport({ document_type: "all" })}
            >
              {t("checkins.actions.exportAllDocuments")}
            </Button>
          ) : null}
        </div>
      </section>

      <Tabs
        activeKey={activeTab}
        items={[
          { key: "room_ops", label: t("checkins.tabs.roomOperations") },
          { key: "pickup_qr", label: t("checkins.tabs.qrPickup"), badge: canManagePickup ? pickupStats.pending + pickupStats.missed : undefined },
        ]}
        onChange={(key) => setActiveTab(key as CheckinTab)}
      />

      <FilterBar
        actions={
          <div className="pickup-toolbar">
            <Button iconLeft={<Icon name="refresh" />} type="button" variant="outline" onClick={() => void refresh()}>
              {t("checkins.actions.refreshRoomOps")}
            </Button>
            {canManagePickup ? (
              <Button iconLeft={<Icon name="refresh" />} type="button" variant="outline" onClick={() => void refreshPickupMonitor()}>
                {t("checkins.actions.refreshPickupMonitor")}
              </Button>
            ) : null}
          </div>
        }
      >
        <label className="filter-field">
          <span>{t("checkins.operatingDate")}</span>
          <input onChange={(event) => setSelectedDate(event.target.value)} type="date" value={selectedDate} />
        </label>
      </FilterBar>

      {activeTab === "room_ops" ? (
        <>
          {error ? <EmptyState icon={<Icon name="warning" />} title={t("checkins.loadError")} description={error} /> : null}

          {rows.length === 0 ? (
            <EmptyState
              icon={<Icon name="how_to_reg" />}
              title={t("checkins.emptyTitle")}
              description={t("checkins.emptyDescription")}
            />
          ) : (
            <>
              <section className="operations-summary-grid">
                <OperationsSummaryCard
                  icon="calendar_today"
                  label={t("checkins.stats.sessions")}
                  note={t("checkins.stats.sessionsNote")}
                  value={formatNumber(rows.length)}
                />
                <OperationsSummaryCard
                  icon="how_to_reg"
                  label={t("checkins.stats.checkedIn")}
                  note={t("checkins.stats.checkedInNote")}
                  tone="success"
                  value={formatNumber(checkedInCount)}
                />
                <OperationsSummaryCard
                  icon="pending_actions"
                  label={t("checkins.stats.pendingConfirm")}
                  note={t("checkins.stats.pendingConfirmNote")}
                  tone="neutral"
                  value={formatNumber(pendingCount)}
                />
                <OperationsSummaryCard
                  icon="verified"
                  label={t("checkins.stats.confirmed")}
                  note={t("checkins.stats.confirmedNote")}
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
              label={t("checkins.pickupStats.assignments")}
              note={t("checkins.pickupStats.assignmentsNote")}
              value={formatNumber(pickupStats.total)}
            />
            <OperationsSummaryCard
              icon="verified"
              label={t("checkins.pickupStats.checkedIn")}
              note={t("checkins.pickupStats.checkedInNote")}
              tone="success"
              value={formatNumber(pickupStats.checkedIn)}
            />
            <OperationsSummaryCard
              icon="warning"
              label={t("checkins.pickupStats.lateOrMissed")}
              note={t("checkins.pickupStats.lateOrMissedNote")}
              tone="danger"
              value={formatNumber(pickupStats.late + pickupStats.missed)}
            />
            <OperationsSummaryCard
              icon="pending_actions"
              label={t("common.pending")}
              note={t("checkins.pickupStats.pendingNote")}
              tone="neutral"
              value={formatNumber(pickupStats.pending)}
            />
          </section>

          {lastPickupResult ? (
            <section className="pickup-result-card ui-card">
              <div className="ui-card__body pickup-result-card__body">
                <div>
                  <span className="pickup-result-card__eyebrow">{t("checkins.latestPickupTitle")}</span>
                  <h3>{lastPickupResult.schedule.course_code ?? t("checkins.latestPickupFallback")}</h3>
                  <p>{lastPickupResult.message}</p>
                </div>
                <div className="pickup-result-card__meta">
                  <span>{lastPickupResult.schedule.room_name ?? t("checkins.pickupRoomPending")}</span>
                  <span>{lastPickupResult.checked_in_at ? formatDateTime(lastPickupResult.checked_in_at) : t("checkins.justConfirmed")}</span>
                </div>
              </div>
            </section>
          ) : null}

          {!canManagePickup ? (
            <EmptyState
              icon={<Icon name="qr_code_scanner" />}
              title={t("checkins.publicPickupTitle")}
              description={t("checkins.publicPickupDescription")}
            />
          ) : pickupLoading ? (
            <div className="page-stack">
              {Array.from({ length: 2 }).map((_, index) => (
                <Skeleton key={index} className="card-skeleton" />
              ))}
            </div>
          ) : pickupError ? (
            <EmptyState icon={<Icon name="warning" />} title={t("checkins.pickupMonitorLoadError")} description={pickupError} />
          ) : pickupRows.length === 0 ? (
            <EmptyState
              icon={<Icon name="inventory_2" />}
              title={t("checkins.pickupEmptyTitle")}
              description={t("checkins.pickupEmptyDescription")}
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
        title={
          selectedSchedule
            ? t("checkins.modal.titleWithRoom", { room: selectedSchedule.room?.room_name ?? t("checkins.modal.assignedRoom") })
            : t("checkins.modal.title")
        }
        onClose={() => setSelectedSchedule(null)}
      >
        <form className="page-stack" onSubmit={handleCreateCheckin}>
          <label className="form-field">
            <span>{t("checkins.form.studentsPresent")}</span>
            <input
              inputMode="numeric"
              onChange={(event) => setStudentsPresent(event.target.value)}
              placeholder={t("checkins.form.studentsPresentPlaceholder")}
              value={studentsPresent}
            />
          </label>
          <label className="form-field">
            <span>{t("checkins.form.lateCount")}</span>
            <input
              inputMode="numeric"
              onChange={(event) => setLateCount(event.target.value)}
              placeholder={t("checkins.form.lateCountPlaceholder")}
              value={lateCount}
            />
          </label>
          <label className="form-field">
            <span>{t("common.notes")}</span>
            <textarea
              onChange={(event) => setNotes(event.target.value)}
              placeholder={t("checkins.form.notesPlaceholder")}
              rows={4}
              value={notes}
            />
          </label>
          <Button loading={submitting} type="submit">
            {t("checkins.actions.saveCheckin")}
          </Button>
        </form>

        {selectedEvents.length > 0 ? (
          <div className="checkin-history">
            <h3>{t("checkins.history.title")}</h3>
            {selectedEvents.map((item) => (
              <div key={item.id} className="checkin-history__item">
                <strong>{item.user ?? t("checkins.history.emsUser")}</strong>
                <span>{formatDateTime(item.checked_in_at)}</span>
                <span>
                  {t("checkins.history.presentLate", {
                    present: formatNumber(item.students_present ?? 0),
                    late: formatNumber(item.late_count ?? 0),
                  })}
                </span>
                <p>{item.notes ?? t("checkins.history.noNotes")}</p>
              </div>
            ))}
          </div>
        ) : null}
      </Modal>

      <Modal
        open={Boolean(pickupScheduleId)}
        title={pickupDetail?.schedule.course_code ? t("checkins.pickupModal.titleWithCourse", { course: pickupDetail.schedule.course_code }) : t("checkins.pickupModal.title")}
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
                <span>{t("common.course")}</span>
                <strong>{pickupDetail.schedule.course_code ?? "-"}</strong>
                <p>{pickupDetail.schedule.course_name ?? t("checkins.pickupModal.coursePending")}</p>
              </div>
              <div className="pickup-detail-tile">
                <span>{t("checkins.pickupModal.examSlot")}</span>
                <strong>{pickupDetail.schedule.exam_time ?? "-"}</strong>
                <p>{pickupDetail.schedule.exam_date ? formatDate(pickupDetail.schedule.exam_date) : t("checkins.pickupModal.datePending")}</p>
              </div>
              <div className="pickup-detail-tile">
                <span>{t("checkins.pickupModal.examRoom")}</span>
                <strong>{pickupDetail.schedule.room_name ?? "-"}</strong>
                <p>{t("checkins.pickupModal.roomNote")}</p>
              </div>
            </section>

            <section className="pickup-qr-status-card ui-card">
              <div className="ui-card__body page-stack">
                <div className="pickup-qr-status-card__row">
                  <div>
                    <span className="pickup-result-card__eyebrow">{t("checkins.pickupModal.activeQr")}</span>
                    <h3>{t("checkins.pickupTable.version", { version: pickupDetail.active_qr?.version ?? "-" })}</h3>
                    <p>
                      {pickupDetail.active_qr?.confirmed_at
                        ? t("checkins.pickupModal.confirmedAt", { value: formatDateTime(pickupDetail.active_qr.confirmed_at) })
                        : t("checkins.pickupModal.noActiveQr")}
                    </p>
                  </div>
                  <div>
                    <span className="pickup-result-card__eyebrow">{t("checkins.pickupModal.latestQr")}</span>
                    <h3>{t("checkins.pickupTable.version", { version: pickupDetail.latest_qr?.version ?? "-" })}</h3>
                    <p>{pickupDetail.has_pending_regeneration ? t("checkins.pickupModal.waitingForConfirmation") : t("checkins.pickupTable.active")}</p>
                  </div>
                </div>
                <div className="pickup-qr-status-card__actions">
                  <Button type="button" variant="outline" onClick={() => openDocumentExport({ schedule_id: pickupScheduleId ?? undefined, document_type: "all" })}>
                    {t("checkins.actions.exportAllDocuments")}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => openDocumentExport({ schedule_id: pickupScheduleId ?? undefined, document_type: "participant_codes" })}>
                    {t("exportCenter.actions.participantCodes")}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => openDocumentExport({ schedule_id: pickupScheduleId ?? undefined, document_type: "signature_sheet" })}>
                    {t("exportCenter.actions.signatureSheets")}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => openDocumentExport({ schedule_id: pickupScheduleId ?? undefined, document_type: "envelope_cover" })}>
                    {t("exportCenter.actions.coverSheets")}
                  </Button>
                  {canManagePickup ? (
                    <Button type="button" variant="ghost" loading={pickupActionBusy === "regenerate"} onClick={() => void handleRegeneratePickupQr()}>
                      {t("checkins.actions.regenerateQr")}
                    </Button>
                  ) : null}
                  {canManagePickup && pickupDetail.has_pending_regeneration ? (
                    <Button type="button" loading={pickupActionBusy === "confirm"} onClick={() => void handleConfirmPickupQr()}>
                      {t("checkins.actions.confirmRegeneratedQr")}
                    </Button>
                  ) : null}
                </div>
                <p className="pickup-qr-status-card__note">{t("checkins.pickupModal.note")}</p>
              </div>
            </section>

            <section className="pickup-assignment-list">
              <h3>{t("checkins.pickupModal.assignedPersonnel")}</h3>
              {pickupDetail.assignments.length === 0 ? (
                <p>{t("checkins.pickupModal.noAssignments")}</p>
              ) : (
                <div className="pickup-assignment-list__grid">
                  {pickupDetail.assignments.map((assignment) => (
                    <div key={`${assignment.user_id}-${assignment.role}`} className="pickup-assignment-list__item">
                      <strong>{assignment.full_name}</strong>
                      <span>{formatTranslatedValue("roles", assignment.role)}</span>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        ) : (
          <EmptyState icon={<Icon name="qr_code" />} title={t("checkins.pickupModal.noDetailsTitle")} description={t("checkins.pickupModal.noDetailsDescription")} />
        )}
      </Modal>

      <PickupQrScanner open={scannerOpen} busy={scannerBusy} onClose={() => setScannerOpen(false)} onDetected={handlePickupDetected} />
    </div>
  );
}
