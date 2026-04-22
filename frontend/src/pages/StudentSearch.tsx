import type React from "react";
import { useMemo, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { LanguageToggle } from "@/components/ui/LanguageToggle";
import { useI18n } from "@/i18n";
import { ApiError } from "@/services/api";
import { getStudentSchedule } from "@/services/public.service";
import type { PublicStudentSchedule } from "@/types/api";
import { formatDate, formatTranslatedValue } from "@/utils/format";

function statusVariant(status: string, hasSchedule: boolean) {
  if (!hasSchedule) {
    return "gray" as const;
  }

  if (status === "locked") {
    return "green" as const;
  }

  if (status === "published") {
    return "blue" as const;
  }

  if (status === "draft") {
    return "gold" as const;
  }

  return "gray" as const;
}

export function StudentSearchPage() {
  const { t } = useI18n();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PublicStudentSchedule | null>(null);

  const handleSearch = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedQuery = query.trim();
    if (!trimmedQuery) return;

    setLoading(true);
    setError(null);
    try {
      const response = await getStudentSchedule(trimmedQuery);
      setResult(response);
    } catch (err) {
      setResult(null);

      if (err instanceof ApiError && err.status === 404) {
        setError(t("public.studentSearch.notFoundDescription"));
      } else {
        setError(err instanceof Error ? err.message : t("errors.searchFailed"));
      }
    } finally {
      setLoading(false);
    }
  };

  const scheduleRows = result?.exams ?? [];
  const scheduledCount = useMemo(
    () => scheduleRows.filter((row) => row.has_schedule).length,
    [scheduleRows],
  );

  return (
    <div className="public-search">
      <Card className="public-search__hero">
        <div className="public-search__language">
          <LanguageToggle />
        </div>
        <h1>{t("public.studentSearch.title")}</h1>
        <p>{t("public.studentSearch.description")}</p>

        <form className="public-search__form" onSubmit={handleSearch}>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={t("public.studentSearch.placeholder")}
            inputMode="numeric"
            autoComplete="off"
            aria-label={t("public.studentSearch.placeholder")}
          />
          <Button loading={loading} type="submit">
            {t("public.studentSearch.submit")}
          </Button>
        </form>
      </Card>

      {error ? (
        <Card>
          <EmptyState
            icon={<Icon name="person_search" />}
            title={t("public.studentSearch.notFoundTitle")}
            description={error}
          />
        </Card>
      ) : null}

      {result ? (
        <Card
          title={`${result.student_id} ${result.full_name}`}
          subtitle={
            result.term_label
              ? t("public.studentSearch.resultsSubtitleTerm", {
                  count: result.total_courses,
                  term: result.term_label,
                })
              : t("public.studentSearch.resultsSubtitle", { count: result.total_courses })
          }
        >
          <div className="public-search__summary">
            <div className="public-search__meta">
              {result.major ? (
                <span className="public-search__meta-item">
                  <strong>{t("public.studentSearch.major")}</strong>
                  {result.major}
                </span>
              ) : null}
              {result.faculty ? (
                <span className="public-search__meta-item">
                  <strong>{t("public.studentSearch.faculty")}</strong>
                  {result.faculty}
                </span>
              ) : null}
              <span className="public-search__meta-item">
                <strong>{t("public.studentSearch.scheduled")}</strong>
                {scheduledCount}/{result.total_courses}
              </span>
            </div>

            {scheduleRows.length === 0 ? (
              <EmptyState
                icon={<Icon name="event_busy" />}
                title={t("public.studentSearch.noExamsTitle")}
                description={t("public.studentSearch.noExamsDescription")}
              />
            ) : (
              <DataTable
                columns={[
                  {
                    key: "exam_date",
                    label: t("public.studentSearch.table.date"),
                    width: "110px",
                    minWidth: "110px",
                    render: (row) => formatDate(row.exam_date),
                  },
                  {
                    key: "exam_time",
                    label: t("public.studentSearch.table.time"),
                    width: "110px",
                    minWidth: "110px",
                    render: (row) => row.exam_time ?? t("common.notRecorded"),
                  },
                  {
                    key: "course_id",
                    label: t("public.studentSearch.table.courseCode"),
                    width: "120px",
                    minWidth: "120px",
                    render: (row) => <code>{row.course_id}</code>,
                  },
                  {
                    key: "course_name",
                    label: t("public.studentSearch.table.courseName"),
                    minWidth: "260px",
                    render: (row) => (
                      <div className="student-schedule-table__course">
                        <strong>{row.course_name}</strong>
                        <span>{t("public.studentSearch.teacherInline", { value: row.teacher })}</span>
                      </div>
                    ),
                  },
                  {
                    key: "section_no",
                    label: t("public.studentSearch.table.section"),
                    width: "90px",
                    minWidth: "90px",
                    render: (row) => row.section_no,
                  },
                  {
                    key: "room",
                    label: t("public.studentSearch.table.room"),
                    width: "140px",
                    minWidth: "140px",
                    render: (row) => row.room ?? t("public.studentSearch.roomUnknown"),
                  },
                  {
                    key: "seat_group",
                    label: t("public.studentSearch.table.seatGroup"),
                    width: "140px",
                    minWidth: "140px",
                    render: (row) => row.seat_group ?? t("public.studentSearch.groupUnknown"),
                  },
                  {
                    key: "status",
                    label: t("public.studentSearch.table.status"),
                    width: "130px",
                    minWidth: "130px",
                    render: (row) => (
                      <span className="student-schedule-table__status">
                        <Badge variant={statusVariant(row.status, row.has_schedule)}>
                          {row.has_schedule
                            ? formatTranslatedValue("status", row.status)
                            : t("public.studentSearch.notScheduled")}
                        </Badge>
                      </span>
                    ),
                  },
                ]}
                rows={scheduleRows}
                rowKey={(row) => `${row.course_id}-${row.section_no}-${row.exam_date ?? "pending"}-${row.exam_time ?? "pending"}`}
                compact
                tableLayout="fixed"
                maxHeight={560}
                scrollThreshold={5}
                emptyTitle={t("public.studentSearch.noExamsTitle")}
                emptyDescription={t("public.studentSearch.noExamsDescription")}
              />
            )}
          </div>
        </Card>
      ) : null}
    </div>
  );
}
