import { Badge } from "@/components/ui/Badge";
import { DataTable } from "@/components/ui/DataTable";
import type { EnrollmentStage, StudentRecordV2 } from "@/hooks/useStudentsData";

function stageVariant(stage: EnrollmentStage) {
  if (stage === "enrolled") {
    return "green" as const;
  }

  if (stage === "verified") {
    return "blue" as const;
  }

  if (stage === "flagged") {
    return "crimson" as const;
  }

  return "gold" as const;
}

export function StudentsTableV2({ rows }: { rows: StudentRecordV2[] }) {
  return (
    <DataTable<StudentRecordV2>
      columns={[
        {
          key: "student",
          label: "Student",
          render: (row) => (
            <div>
              <strong>{row.fullName}</strong>
              <p>{row.studentId}</p>
            </div>
          ),
        },
        {
          key: "program",
          label: "Program",
          render: (row) => (
            <div>
              <strong>{row.program}</strong>
              <p>{row.faculty}</p>
            </div>
          ),
        },
        {
          key: "section",
          label: "Section",
          render: (row) => (
            <div>
              <strong>{row.section}</strong>
              <p>Year {row.yearLevel}</p>
            </div>
          ),
        },
        {
          key: "stage",
          label: "Enrollment Stage",
          render: (row) => <Badge variant={stageVariant(row.stage)}>{row.stage}</Badge>,
        },
        {
          key: "firstEnrollment",
          label: "First Enrollment",
          render: (row) => <Badge variant={row.firstEnrollment ? "orange" : "gray"}>{row.firstEnrollment ? "yes" : "no"}</Badge>,
        },
        {
          key: "pendingDocs",
          label: "Pending Docs",
          render: (row) => <span>{row.pendingDocs}</span>,
        },
        {
          key: "lastUpdated",
          label: "Last Updated",
          render: (row) => <span>{row.lastUpdated}</span>,
        },
      ]}
      rows={rows}
      rowKey={(row) => row.id}
      emptyTitle="No student records matched"
      emptyDescription="Adjust the current search or filter selection."
    />
  );
}
