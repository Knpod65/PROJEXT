import { get } from "./api";
import type { AdvanceBatchPreviewPayload, AdvanceBatchPreviewQuery } from "@/types/invigilationAdvanceBatch";

export function fetchAdvanceBatchPreview(
  query: AdvanceBatchPreviewQuery = {},
): Promise<AdvanceBatchPreviewPayload> {
  const params: Record<string, string | number> = {};

  if (query.period_id) params.period_id = query.period_id;
  if (query.academic_year) params.academic_year = query.academic_year;
  if (query.semester) params.semester = query.semester;
  if (query.exam_type) params.exam_type = query.exam_type;

  return get<AdvanceBatchPreviewPayload>("/invigilation-advance-batch/preview", { query: params });
}
