import { useCallback, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageHeader } from "@/components/ui/PageHeader";
import { useAsyncData } from "@/hooks/useAsyncData";
import { useI18n } from "@/i18n";
import { autoDetectCoExam, createCoExamGroup, listCoExamGroups } from "@/services/coexam.service";
import { useUi } from "@/store/ui.store";
import type { CoExamGroup, CoExamSuggestion } from "@/types/api";
import { formatNumber } from "@/utils/format";

function suggestionTypeLabel(type: string) {
  switch (type) {
    case "same_course":
      return "Same course slot";
    case "same_teacher":
      return "Same teacher slot";
    default:
      return type;
  }
}

function renderSuggestionMembers(suggestion: CoExamSuggestion) {
  return (
    <div className="data-table__content data-table__content--clamp">
      {suggestion.sections.slice(0, 4).map((section, index) => {
        const course = typeof section.course === "string" ? section.course : typeof section.course_id === "string" ? section.course_id : "";
        const sectionNo = typeof section.no === "string" ? section.no : typeof section.section_no === "string" ? section.section_no : "-";
        const size = typeof section.n === "number" ? section.n : typeof section.num_students === "number" ? section.num_students : null;
        const label = [course, sectionNo !== "-" ? `sec ${sectionNo}` : null, size !== null ? `${formatNumber(size)} students` : null]
          .filter(Boolean)
          .join(" • ");
        return <p key={`${suggestion.label}-${index}`}>{label || "Section member"}</p>;
      })}
      {suggestion.sections.length > 4 && <p>+{suggestion.sections.length - 4} more sections</p>}
    </div>
  );
}

function renderPersistedMembers(group: CoExamGroup) {
  return (
    <div className="data-table__content data-table__content--clamp">
      {group.members.slice(0, 4).map((member) => (
        <p key={`${group.id}-${member.section_id}`}>
          {member.course_id ?? "-"} • sec {member.section_no ?? "-"} • {formatNumber(member.num_students ?? 0)} students
        </p>
      ))}
      {group.members.length > 4 && <p>+{group.members.length - 4} more sections</p>}
    </div>
  );
}

export function CoExamPage() {
  const { t } = useI18n();
  const { toast } = useUi();
  const loader = useCallback(() => listCoExamGroups(), []);
  const state = useAsyncData(loader, [loader]);

  const [suggestions, setSuggestions] = useState<CoExamSuggestion[]>([]);
  const [detecting, setDetecting] = useState(false);
  const [savingLabel, setSavingLabel] = useState<string | null>(null);

  const handleAutoDetect = async () => {
    setDetecting(true);
    try {
      const response = await autoDetectCoExam();
      setSuggestions(response.suggestions);
      toast(`Detected ${response.count} likely co-exam groups. Review them below before saving.`, "info");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to detect co-exam suggestions.", "error");
    } finally {
      setDetecting(false);
    }
  };

  const handlePersistSuggestion = async (suggestion: CoExamSuggestion) => {
    setSavingLabel(suggestion.label);
    try {
      await createCoExamGroup({
        label: suggestion.label,
        exam_date: suggestion.exam_date,
        exam_time: suggestion.exam_time,
        exam_type: suggestion.exam_type,
        section_ids: suggestion.section_ids,
      });
      setSuggestions((prev) => prev.filter((item) => item.label !== suggestion.label));
      toast("Co-exam group created.", "success");
      await state.reload();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to create co-exam group.", "error");
    } finally {
      setSavingLabel(null);
    }
  };

  const persistedGroups = useMemo(() => state.data ?? [], [state.data]);

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        eyebrow={t("navigation.groups.operations")}
        title={t("navigation.pages.coexam.title")}
        description={t("navigation.pages.coexam.description")}
      />
      <Card
        title="Co-exam review"
        subtitle="Detect likely shared-exam groups, review the underlying sections, then persist the groups you actually want to use."
        actions={<Button type="button" loading={detecting} onClick={() => void handleAutoDetect()}>Auto-detect candidates</Button>}
      >
        {suggestions.length === 0 ? (
          <EmptyState
            icon="🔎"
            title="No pending suggestions"
            description="Run auto-detect to surface likely co-exam groups for review."
          />
        ) : (
          <DataTable<CoExamSuggestion>
            columns={[
              {
                key: "label",
                label: "Candidate",
                width: "24%",
                render: (row) => (
                  <div className="data-table__content data-table__content--clamp">
                    <strong>{row.label}</strong>
                    <p>{suggestionTypeLabel(row.type)}</p>
                  </div>
                ),
              },
              {
                key: "exam_date",
                label: "Exam Slot",
                width: "16%",
                render: (row) => (
                  <div className="data-table__content data-table__content--clamp">
                    <strong>{row.exam_date}</strong>
                    <p>{row.exam_time}</p>
                    <p>{row.exam_type}</p>
                  </div>
                ),
              },
              {
                key: "sections",
                label: "Sections",
                width: "30%",
                render: renderSuggestionMembers,
              },
              {
                key: "total_students",
                label: "Students",
                width: "12%",
                align: "right",
                render: (row) => formatNumber(row.total_students),
              },
              {
                key: "label-actions",
                label: "Actions",
                width: "18%",
                render: (row) => (
                  <div className="inline-actions">
                    <Button type="button" size="sm" loading={savingLabel === row.label} onClick={() => void handlePersistSuggestion(row)}>
                      Save group
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      onClick={() => setSuggestions((prev) => prev.filter((item) => item.label !== row.label))}
                    >
                      Dismiss
                    </Button>
                  </div>
                ),
              },
            ]}
            emptyTitle="No co-exam suggestions"
            rowKey={(row) => `${row.type}-${row.label}`}
            rows={suggestions}
            scrollThreshold={5}
            tableLayout="fixed"
          />
        )}
      </Card>

      <Card title="Persisted co-exam groups" subtitle="These groups are already part of the current active-period workflow">
        {state.loading ? (
          <EmptyState icon="⌛" title="Loading co-exam groups..." />
        ) : persistedGroups.length === 0 ? (
          <EmptyState icon="👥" title="No co-exam groups yet" description="Saved co-exam groups will appear here once they are created." />
        ) : (
          <DataTable<CoExamGroup>
            columns={[
              {
                key: "label",
                label: "Group",
                width: "26%",
              },
              {
                key: "exam_date",
                label: "Exam Slot",
                width: "16%",
                render: (row) => (
                  <div className="data-table__content data-table__content--clamp">
                    <strong>{row.exam_date}</strong>
                    <p>{row.exam_time}</p>
                    <p>{row.exam_type}</p>
                  </div>
                ),
              },
              {
                key: "members",
                label: "Members",
                width: "34%",
                render: renderPersistedMembers,
              },
              {
                key: "total_students",
                label: "Students",
                width: "12%",
                align: "right",
                render: (row) => formatNumber(row.total_students),
              },
              {
                key: "member_count",
                label: "Sections",
                width: "12%",
                align: "right",
                render: (row) => formatNumber(row.member_count),
              },
            ]}
            emptyTitle="No co-exam groups"
            rowKey={(row) => row.id}
            rows={persistedGroups}
            scrollThreshold={5}
            tableLayout="fixed"
          />
        )}
      </Card>
    </div>
  );
}
