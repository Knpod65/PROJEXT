import { useMemo, useState } from "react";

export type EnrollmentStage = "new" | "verified" | "enrolled" | "flagged";

export interface StudentRecordV2 {
  id: number;
  studentId: string;
  fullName: string;
  faculty: string;
  program: string;
  section: string;
  yearLevel: number;
  stage: EnrollmentStage;
  firstEnrollment: boolean;
  pendingDocs: number;
  lastUpdated: string;
}

const mockStudents: StudentRecordV2[] = [
  {
    id: 1,
    studentId: "66010011",
    fullName: "Napat Lertchai",
    faculty: "Political Science",
    program: "Public Administration",
    section: "SEC 001",
    yearLevel: 1,
    stage: "new",
    firstEnrollment: true,
    pendingDocs: 2,
    lastUpdated: "17 Apr, 09:20",
  },
  {
    id: 2,
    studentId: "65030582",
    fullName: "Sirinya Pongsak",
    faculty: "Political Science",
    program: "International Relations",
    section: "SEC 001",
    yearLevel: 2,
    stage: "verified",
    firstEnrollment: false,
    pendingDocs: 0,
    lastUpdated: "17 Apr, 08:50",
  },
  {
    id: 3,
    studentId: "67024003",
    fullName: "Kritsada Tansri",
    faculty: "Political Science",
    program: "Governance Studies",
    section: "SEC 002",
    yearLevel: 1,
    stage: "flagged",
    firstEnrollment: true,
    pendingDocs: 3,
    lastUpdated: "16 Apr, 18:12",
  },
  {
    id: 4,
    studentId: "64099821",
    fullName: "Pimchanok Viroj",
    faculty: "Economics",
    program: "Development Economics",
    section: "SEC 001",
    yearLevel: 3,
    stage: "enrolled",
    firstEnrollment: false,
    pendingDocs: 0,
    lastUpdated: "17 Apr, 10:04",
  },
  {
    id: 5,
    studentId: "67019977",
    fullName: "Anucha Meesuk",
    faculty: "Law",
    program: "Legal Studies",
    section: "SEC 003",
    yearLevel: 1,
    stage: "new",
    firstEnrollment: true,
    pendingDocs: 1,
    lastUpdated: "17 Apr, 07:42",
  },
  {
    id: 6,
    studentId: "65077812",
    fullName: "Nicha Wongchai",
    faculty: "Political Science",
    program: "Public Policy",
    section: "SEC 002",
    yearLevel: 2,
    stage: "verified",
    firstEnrollment: false,
    pendingDocs: 0,
    lastUpdated: "16 Apr, 16:30",
  },
];

export function useStudentsData() {
  const [rows] = useState<StudentRecordV2[]>(mockStudents);
  const [query, setQuery] = useState("");
  const [facultyFilter, setFacultyFilter] = useState<"all" | string>("all");
  const [stageFilter, setStageFilter] = useState<"all" | EnrollmentStage>("all");

  const filteredRows = useMemo(() => {
    return rows.filter((row) => {
      const matchesQuery =
        query.trim().length === 0 ||
        `${row.studentId} ${row.fullName} ${row.program} ${row.section}`.toLowerCase().includes(query.toLowerCase());
      const matchesFaculty = facultyFilter === "all" || row.faculty === facultyFilter;
      const matchesStage = stageFilter === "all" || row.stage === stageFilter;

      return matchesQuery && matchesFaculty && matchesStage;
    });
  }, [facultyFilter, query, rows, stageFilter]);

  const stats = useMemo(() => {
    const firstEnrollment = rows.filter((row) => row.firstEnrollment).length;
    const flagged = rows.filter((row) => row.stage === "flagged").length;
    const enrolled = rows.filter((row) => row.stage === "enrolled").length;

    return {
      total: rows.length,
      firstEnrollment,
      flagged,
      enrolled,
      pendingImport: 24,
      remainingCapacity: 8,
    };
  }, [rows]);

  const faculties = useMemo(() => {
    return Array.from(new Set(rows.map((row) => row.faculty))).sort();
  }, [rows]);

  const flow = useMemo(() => {
    return {
      received: rows.filter((row) => row.stage === "new").length,
      verified: rows.filter((row) => row.stage === "verified").length,
      enrolled: rows.filter((row) => row.stage === "enrolled").length,
      flagged: rows.filter((row) => row.stage === "flagged").length,
    };
  }, [rows]);

  const resetFilters = () => {
    setQuery("");
    setFacultyFilter("all");
    setStageFilter("all");
  };

  return {
    rows: filteredRows,
    query,
    facultyFilter,
    stageFilter,
    setQuery,
    setFacultyFilter,
    setStageFilter,
    resetFilters,
    stats,
    faculties,
    flow,
  };
}
