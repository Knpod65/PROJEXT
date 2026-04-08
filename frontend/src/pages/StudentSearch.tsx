import { useState, type FormEvent } from "react";

import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Button } from "@/components/ui/Button";
import { getStudentSchedule } from "@/services/public.service";
import type { PublicStudentSchedule } from "@/types/api";
import { formatDateRange } from "@/utils/format";

export function StudentSearchPage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PublicStudentSchedule | null>(null);

  const handleSearch = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const response = await getStudentSchedule(query.trim());
      setResult(response);
    } catch (err) {
      setResult(null);
      setError(err instanceof Error ? err.message : "ค้นหาไม่สำเร็จ");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="public-search">
      <Card className="public-search__hero">
        <h1>ค้นหาตารางสอบนักศึกษา</h1>
        <p>กรอกรหัสนักศึกษาเพื่อดูวันสอบ เวลา ห้องสอบ และสถานะล่าสุด</p>

        <form className="public-search__form" onSubmit={handleSearch}>
          <input
            onChange={(event) => setQuery(event.target.value)}
            placeholder="รหัสนักศึกษา"
            value={query}
          />
          <Button loading={loading} type="submit">
            ค้นหา
          </Button>
        </form>
      </Card>

      {error ? <EmptyState icon="🔍" title="ไม่พบข้อมูล" description={error} /> : null}

      {result ? (
        <Card title={`${result.student_id} ${result.full_name}`} subtitle={`${result.total_courses} วิชา`}>
          <div className="student-result-list">
            {result.exams.map((exam) => (
              <div key={`${exam.course_id}-${exam.section_no}`} className="student-result-list__item">
                <strong>
                  {exam.course_id} {exam.course_name}
                </strong>
                <span>{formatDateRange(exam.exam_date, exam.exam_time)}</span>
                <span>ห้อง: {exam.room ?? "ยังไม่กำหนด"}</span>
                <span>อาจารย์: {exam.teacher}</span>
              </div>
            ))}
          </div>
        </Card>
      ) : null}
    </div>
  );
}
