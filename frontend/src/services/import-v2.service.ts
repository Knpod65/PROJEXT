import { request } from "./api";
import type {
  ImportV2ConfirmCheckResponse,
  ImportV2ExecuteResponse,
  ImportV2OverrideRequestItem,
  ImportV2PrepareResponse,
  ImportV2PreviewResponse,
  ImportV2Type,
  ImportV2ValidationResponse,
} from "@/types/api";

interface ImportV2TermInput {
  academic_year: string;
  semester: string;
  exam_type: string;
}

interface ImportV2PrepareInput extends ImportV2TermInput {
  file_token: string;
  import_type: ImportV2Type;
  selected_rows: number[];
  overrides: ImportV2OverrideRequestItem[];
}

interface ImportV2ConfirmInput extends ImportV2PrepareInput {
  confirmed_by: number;
  dry_run: boolean;
}

export function previewImportV2(input: ImportV2TermInput & { file: File }) {
  const formData = new FormData();
  formData.set("file", input.file);
  formData.set("academic_year", input.academic_year);
  formData.set("semester", input.semester);
  formData.set("exam_type", input.exam_type);

  return request<ImportV2PreviewResponse>("POST", "/import/v2/preview", { formData });
}

export function validateImportV2(input: ImportV2PrepareInput) {
  return request<ImportV2ValidationResponse>("POST", "/import/v2/validate", {
    body: {
      file_token: input.file_token,
      import_type: input.import_type,
      academic_year: input.academic_year,
      semester: input.semester,
      exam_type: input.exam_type,
    },
  });
}

export function prepareImportV2(input: ImportV2PrepareInput) {
  return request<ImportV2PrepareResponse>("POST", "/import/v2/prepare", {
    body: input,
  });
}

export function confirmCheckImportV2(input: ImportV2ConfirmInput) {
  return request<ImportV2ConfirmCheckResponse>("POST", "/import/v2/confirm-check", {
    body: input,
  });
}

export function confirmImportV2(input: ImportV2ConfirmInput) {
  return request<ImportV2ExecuteResponse>("POST", "/import/v2/confirm", {
    body: input,
  });
}
