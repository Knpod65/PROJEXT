import type { SignerInfo, WorkflowIssueItem, WorkflowSession } from "@/types/api";
import { get, post } from "./api";

export function getWorkflowSession() {
  return get<WorkflowSession>("/workflow/session/");
}

export function initWorkflowSession() {
  return post("/workflow/session/init");
}

export function signWorkflow(round: 1 | 2) {
  return post("/workflow/session/sign", undefined, { query: { round } });
}

export function openSwapWindow() {
  return post("/workflow/session/open-swap");
}

export function listWorkflowSigners() {
  return get<SignerInfo[]>("/workflow/session/signers");
}

export function listWorkflowExternalIssues() {
  return get<WorkflowIssueItem[]>("/workflow/session/external-issues");
}
