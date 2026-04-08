import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { runOptimizer } from "@/services/schedule.service";
import type { OptimizerResult } from "@/types/api";
import { useUi } from "@/store/ui.store";

export function OptimizerPage() {
  const { toast } = useUi();
  const [result, setResult] = useState<OptimizerResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    semester: "2",
    academic_year: "2568",
    exam_type: "final",
  });

  const handleRun = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    try {
      const response = await runOptimizer(form);
      setResult(response as OptimizerResult);
      toast("ประมวลผล optimizer แล้ว", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "รัน optimizer ไม่สำเร็จ", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-stack">
      <Card title="จัดตารางสอบอัตโนมัติ">
        <form className="inline-form" onSubmit={handleRun}>
          <input
            onChange={(event) => setForm((current) => ({ ...current, academic_year: event.target.value }))}
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
          <Button loading={loading} type="submit">
            Run optimizer
          </Button>
        </form>
      </Card>

      {result ? (
        <Card title="ผลลัพธ์">
          <div className="summary-grid">
            <div className="summary-box">
              <span>Assigned</span>
              <strong>
                {result.sections_assigned}/{result.sections_total}
              </strong>
            </div>
            <div className="summary-box">
              <span>Fairness</span>
              <strong>{result.fairness_score}</strong>
            </div>
          </div>
          {result.violations.length ? (
            <ul className="plain-list">
              {result.violations.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : (
            <p>ไม่พบ violation</p>
          )}
        </Card>
      ) : null}
    </div>
  );
}
