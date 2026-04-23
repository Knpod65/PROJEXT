import type {
  SubmissionDetail,
  SubmissionListItem,
  SubmissionMessage,
} from "@/types/api";
import { get, post } from "./api";

export type ExamTypeChoice =
  | "no_exam"
  | "online"
  | "onsite"
  | "outside_sched"
  | "in_class";

export type AnswerFormat =
  | "on_paper"
  | "mcq_omr"
  | "a4_sheets"
  | "booklet"
  | "hybrid";

export type PrintStaple = "none" | "corner_left" | "side_left" | "custom";

export interface Step2Payload {
  section_id: number;
  exam_type_choice: ExamTypeChoice;
  answer_formats?: AnswerFormat[];
  a4_pages_count?: number;
}

export interface Step4Payload {
  section_id: number;
  print_duplex: boolean;
  print_staple: PrintStaple;
  print_staple_page?: number | null;
  print_note?: string | null;
}

export function listSubmissions(status?: string) {
  return get<SubmissionListItem[]>("/submissions", {
    query: status ? { status } : undefined,
  });
}

export function getSubmissionForSection(sectionId: number) {
  return get<SubmissionDetail>(`/submissions/section/${sectionId}`);
}

export function step1ConfirmDate(sectionId: number) {
  return post<{ success: boolean; step: number; next: string }>(
    "/submissions/step1-confirm",
    { section_id: sectionId },
  );
}

export function step2ExamType(data: Step2Payload) {
  return post<{ success: boolean; step: number; needs_file: boolean; next: string }>(
    "/submissions/step2-exam-type",
    data,
  );
}

export function step3UploadPdf(
  sectionId: number,
  file: File,
  noCoverPage: boolean,
  isSharedExam: boolean,
) {
  const fd = new FormData();
  fd.append("file", file);
  return post<{ success: boolean; step: number; next: string }>(
    `/submissions/step3-upload/${sectionId}?no_cover_page_confirmed=${noCoverPage}&is_shared_exam=${isSharedExam}`,
    undefined,
    { formData: fd },
  );
}

export function step4PrintSpec(data: Step4Payload) {
  return post<{ status: string; print_duplex: boolean; print_staple: string }>(
    "/submissions/step4-print-spec",
    data,
  );
}

export function submitForReview(sectionId: number) {
  return post<{ success: boolean; status: string }>(
    "/submissions/submit",
    { section_id: sectionId },
  );
}

export function approveSubmission(
  submissionId: number,
  approve: boolean,
  reason?: string,
) {
  return post<{ success: boolean; status: string }>(
    "/submissions/approve",
    { submission_id: submissionId, approve, reason },
  );
}

export function listMessages(submissionId: number) {
  return get<SubmissionMessage[]>(`/submissions/${submissionId}/messages`);
}

export function sendMessage(submissionId: number, message: string) {
  return post(`/submissions/${submissionId}/messages`, { message });
}
