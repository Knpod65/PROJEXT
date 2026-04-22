import { del, get, post } from "./api";

export interface UnavailabilityRecord {
  id: number;
  user_id: number;
  full_name: string | null;
  block_date: string;
  block_time: string | null;
  all_day: boolean;
  reason: string | null;
}

export interface StaffPoolMember {
  id: number;
  full_name: string | null;
  username: string;
  role: string;
  is_esq_staff: boolean;
  special_role: string | null;
}

export interface OptimizeSessionData {
  id?: number;
  status: string;
  baseline_saved?: boolean;
  round1?: {
    signatures: Array<{ order: number; username: string; signed_at: string | null }>;
    done: number;
    total: number;
    complete: boolean;
  };
  round2?: {
    signatures: Array<{ order: number; username: string; signed_at: string | null }>;
    done: number;
    total: number;
    complete: boolean;
  };
  next_signer_r1?: string | null;
  next_signer_r2?: string | null;
  message?: string;
}

export interface OptimizerResult {
  sections_assigned: number;
  sections_total: number;
  fairness_score: number;
  violations: string[];
}

export function getSession() {
  return get<OptimizeSessionData>("/workflow/session/");
}

export function initSession() {
  return post<OptimizeSessionData>("/workflow/session/init");
}

export function signSession(round: 1 | 2) {
  return post<OptimizeSessionData>(`/workflow/session/sign?round=${round}`);
}

export function getUnavailability() {
  return get<UnavailabilityRecord[]>("/workflow/unavailability/");
}

export function addUnavailability(data: {
  user_id: number;
  block_date: string;
  block_time?: string;
  reason?: string;
}) {
  return post<{ id: number; status: string }>("/workflow/unavailability/", data);
}

export function deleteUnavailability(id: number) {
  return del<{ status: string }>(`/workflow/unavailability/${id}`);
}

export function getStaffPool() {
  return get<{ supervisors: StaffPoolMember[]; room_keepers: StaffPoolMember[] }>(
    "/workflow/staff-pool",
  );
}

export function runOptimizer(body: {
  semester: string;
  academic_year: string;
  exam_type: string;
}) {
  return post<OptimizerResult>("/schedule/optimize", body);
}
