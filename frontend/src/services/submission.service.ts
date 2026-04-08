import type {
  SubmissionDetail,
  SubmissionListItem,
  SubmissionMessage,
} from "@/types/api";
import { get, post } from "./api";

export function listSubmissions(status?: string) {
  return get<SubmissionListItem[]>("/submissions", {
    query: status ? { status } : undefined,
  });
}

export function getSubmissionForSection(sectionId: number) {
  return get<SubmissionDetail>(`/submissions/section/${sectionId}`);
}

export function listMessages(submissionId: number) {
  return get<SubmissionMessage[]>(`/submissions/${submissionId}/messages`);
}

export function sendMessage(submissionId: number, message: string) {
  return post(`/submissions/${submissionId}/messages`, { message });
}

