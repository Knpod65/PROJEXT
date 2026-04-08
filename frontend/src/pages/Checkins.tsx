import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";

import { CheckinCard } from "@/components/checkins/CheckinCard";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { createCheckin, getCheckinsForSchedule } from "@/services/checkin.service";
import { listSchedules } from "@/services/schedule.service";
import type { CheckinEventItem, ScheduleWithSection } from "@/types/api";
import { useUi } from "@/store/ui.store";
import { getCurrentPosition } from "@/utils/gps";

export function CheckinsPage() {
  const { toast } = useUi();
  const [schedules, setSchedules] = useState<ScheduleWithSection[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<ScheduleWithSection | null>(null);
  const [events, setEvents] = useState<Record<string, CheckinEventItem[]>>({});
  const [submitting, setSubmitting] = useState(false);
  const [notes, setNotes] = useState("");
  const [studentsPresent, setStudentsPresent] = useState("");

  const loadPage = useCallback(async () => {
    setLoading(true);
    try {
      const allSchedules = await listSchedules();
      const today = new Date().toISOString().slice(0, 10);
      const todaySchedules = allSchedules.filter((item) => item.exam_date === today);
      setSchedules(todaySchedules);

      const pairs = await Promise.all(
        todaySchedules.map(async (item) => [item.id, await getCheckinsForSchedule(item.id)] as const),
      );
      setEvents(Object.fromEntries(pairs) as Record<string, CheckinEventItem[]>);
    } catch (err) {
      toast(err instanceof Error ? err.message : "โหลดข้อมูล check-in ไม่สำเร็จ", "error");
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    void loadPage();
  }, [loadPage]);

  const selectedEvents = useMemo(
    () => (selected ? events[String(selected.id)] ?? [] : []),
    [events, selected],
  );

  const handleCheckin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selected) return;

    setSubmitting(true);
    try {
      const position = await getCurrentPosition({ enableHighAccuracy: true, timeout: 8000 });
      await createCheckin({
        schedule_id: selected.id,
        checkin_type: "at_room",
        notes: `${notes}\nGPS: ${position.coords.latitude.toFixed(6)}, ${position.coords.longitude.toFixed(6)}`.trim(),
        students_present: studentsPresent ? Number(studentsPresent) : undefined,
      });
      toast("บันทึก check-in แล้ว", "success");
      setSelected(null);
      setNotes("");
      setStudentsPresent("");
      await loadPage();
    } catch (err) {
      toast(err instanceof Error ? err.message : "check-in ไม่สำเร็จ", "error");
    } finally {
      setSubmitting(false);
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
    <div className="page-stack">
      {schedules.length === 0 ? (
        <EmptyState icon="✅" title="ไม่มีกำหนดสอบวันนี้" />
      ) : (
        schedules.map((schedule) => (
          <CheckinCard
            key={schedule.id}
            checkedIn={(events[String(schedule.id)] ?? []).length > 0}
            onCheckin={() => setSelected(schedule)}
            schedule={schedule}
          />
        ))
      )}

      <Modal
        open={Boolean(selected)}
        title={selected ? `ยืนยัน Check-in • ${selected.room?.room_name ?? "ยังไม่กำหนดห้อง"}` : "ยืนยัน Check-in"}
        onClose={() => setSelected(null)}
      >
        <form className="page-stack" onSubmit={handleCheckin}>
          <label className="form-field">
            <span>จำนวนนักศึกษาที่มา</span>
            <input
              inputMode="numeric"
              onChange={(event) => setStudentsPresent(event.target.value)}
              placeholder="เช่น 28"
              value={studentsPresent}
            />
          </label>
          <label className="form-field">
            <span>หมายเหตุ</span>
            <textarea
              onChange={(event) => setNotes(event.target.value)}
              placeholder="เช่น มาถึงห้องแล้วและเริ่มเตรียมเอกสาร"
              rows={4}
              value={notes}
            />
          </label>
          <Button loading={submitting} type="submit">
            ยืนยัน Check-in
          </Button>
        </form>

        {selectedEvents.length ? (
          <div className="checkin-history">
            <h3>ประวัติ check-in ของตารางนี้</h3>
            {selectedEvents.map((item) => (
              <div key={item.id} className="checkin-history__item">
                <strong>{item.user ?? "ผู้ใช้"}</strong>
                <span>{item.checkin_type}</span>
                <span>{item.checked_in_at ? new Date(item.checked_in_at).toLocaleString("th-TH") : "-"}</span>
              </div>
            ))}
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
