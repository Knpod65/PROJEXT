import { useCallback, useState, type FormEvent } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { createPeriod, activatePeriod, listPeriods } from "@/services/period.service";
import { useAsyncData } from "@/hooks/useAsyncData";
import { useUi } from "@/store/ui.store";

export function PeriodPage() {
  const { toast } = useUi();
  const loader = useCallback(() => listPeriods(), []);
  const state = useAsyncData(loader, [loader]);
  const [form, setForm] = useState({
    academic_year: "2568",
    semester: "2",
    exam_type: "final",
    label: "",
  });

  const handleCreate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      await createPeriod(form);
      toast("สร้างรอบสอบใหม่แล้ว", "success");
      await state.reload();
    } catch (err) {
      toast(err instanceof Error ? err.message : "สร้างรอบสอบไม่สำเร็จ", "error");
    }
  };

  const handleActivate = async (periodId: number) => {
    try {
      await activatePeriod(periodId);
      toast("เปลี่ยน active period แล้ว", "success");
      await state.reload();
    } catch (err) {
      toast(err instanceof Error ? err.message : "เปลี่ยนรอบสอบไม่สำเร็จ", "error");
    }
  };

  return (
    <div className="page-stack">
      <Card title="สร้างรอบสอบใหม่">
        <form className="inline-form" onSubmit={handleCreate}>
          <input
            onChange={(event) => setForm((current) => ({ ...current, academic_year: event.target.value }))}
            placeholder="ปีการศึกษา"
            value={form.academic_year}
          />
          <select
            onChange={(event) => setForm((current) => ({ ...current, semester: event.target.value }))}
            value={form.semester}
          >
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="summer">summer</option>
          </select>
          <select
            onChange={(event) => setForm((current) => ({ ...current, exam_type: event.target.value }))}
            value={form.exam_type}
          >
            <option value="midterm">midterm</option>
            <option value="final">final</option>
          </select>
          <input
            onChange={(event) => setForm((current) => ({ ...current, label: event.target.value }))}
            placeholder="ชื่อรอบสอบ"
            value={form.label}
          />
          <Button type="submit">สร้างรอบ</Button>
        </form>
      </Card>

      <div className="page-stack">
        {(state.data ?? []).map((period) => (
          <Card
            key={period.id}
            title={period.label}
            subtitle={`${period.exam_type} • ${period.semester}/${period.academic_year}`}
            actions={<Badge variant={period.is_active ? "green" : "gray"}>{period.is_active ? "active" : "archived"}</Badge>}
          >
            {!period.is_active ? (
              <Button type="button" variant="outline" onClick={() => void handleActivate(period.id)}>
                Activate
              </Button>
            ) : null}
          </Card>
        ))}
      </div>
    </div>
  );
}
