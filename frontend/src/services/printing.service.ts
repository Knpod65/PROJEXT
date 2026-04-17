import type { PrintQueueJob } from "@/types/api";
import { get, post, put } from "./api";

export function listPrintQueue() {
  return get<PrintQueueJob[]>("/printing/queue");
}

export function getPrintJob(jobId: number) {
  return get<PrintQueueJob>(`/printing/queue/${jobId}`);
}

export function startPrintJob(jobId: number) {
  return post<PrintQueueJob>(`/printing/queue/${jobId}/start`);
}

export function completePrintJob(jobId: number) {
  return post<PrintQueueJob>(`/printing/queue/${jobId}/complete`);
}

export function dispatchPrintJob(jobId: number) {
  return post<PrintQueueJob>(`/printing/queue/${jobId}/dispatch`);
}

export function deliverPrintJob(jobId: number) {
  return post<PrintQueueJob>(`/printing/queue/${jobId}/deliver`);
}

export function updatePrintJobNotes(
  jobId: number,
  body: { notes?: string | null; delivery_note?: string | null },
) {
  return put<PrintQueueJob>(`/printing/queue/${jobId}/notes`, body);
}
