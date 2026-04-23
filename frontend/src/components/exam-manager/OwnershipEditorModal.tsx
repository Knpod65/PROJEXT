import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { useI18n } from "@/i18n";
import type {
  ExamManagerOverviewItem,
  OwnershipUpdatePayload,
} from "@/services/exam-manager.service";
import type { UserOut } from "@/types/api";

interface OwnershipEditorModalProps {
  open: boolean;
  row: ExamManagerOverviewItem | null;
  teachers: UserOut[];
  saving?: boolean;
  onClose: () => void;
  onSave: (payload: OwnershipUpdatePayload) => Promise<void>;
}

export function OwnershipEditorModal({
  onClose,
  onSave,
  open,
  row,
  saving = false,
  teachers,
}: OwnershipEditorModalProps) {
  const { t } = useI18n();
  const [midtermManagerId, setMidtermManagerId] = useState<string>("");
  const [finalManagerId, setFinalManagerId] = useState<string>("");

  const scopedTeachers = useMemo(() => {
    if (!row?.department) {
      return teachers;
    }

    const filtered = teachers.filter((teacher) => teacher.dept_code === row.department);
    return filtered.length > 0 ? filtered : teachers;
  }, [row?.department, teachers]);

  useEffect(() => {
    if (!open || !row) {
      return;
    }

    const fallbackTeacherId =
      scopedTeachers.length === 1 ? String(scopedTeachers[0].id) : "";
    setMidtermManagerId(String(row.midterm?.manager_id ?? fallbackTeacherId));
    setFinalManagerId(String(row.final?.manager_id ?? fallbackTeacherId));
  }, [open, row, scopedTeachers]);

  const handleSave = async () => {
    await onSave({
      midterm_manager_id: midtermManagerId ? Number(midtermManagerId) : null,
      final_manager_id: finalManagerId ? Number(finalManagerId) : null,
    });
  };

  return (
    <Modal
      open={open}
      title={t("ownership.modal.title")}
      onClose={onClose}
      footer={
        <div className="inline-actions">
          <Button type="button" variant="outline" onClick={onClose} disabled={saving}>
            {t("common.cancel")}
          </Button>
          <Button type="button" loading={saving} onClick={() => void handleSave()}>
            {t("common.save")}
          </Button>
        </div>
      }
    >
      {row ? (
        <div className="user-editor-grid">
          <div className="ownership-editor-summary">
            <strong>{row.course_id} {row.course_name}</strong>
            <span>{t("ownership.table.section")}: {row.section_no}</span>
            <span>{t("common.department")}: {row.department ?? t("common.notRecorded")}</span>
            <span>{t("schedule.table.teachingRoom")}: {row.teaching_room ?? t("common.notRecorded")}</span>
          </div>

          <div className="ownership-editor-summary">
            <strong>{t("ownership.table.importedTeachers")}</strong>
            {row.imported_teachers.length > 0 ? (
              row.imported_teachers.map((teacher) => (
                <span key={teacher.id}>{teacher.full_name ?? teacher.email ?? "-"}</span>
              ))
            ) : (
              <span>{t("ownership.emptyImportedTeachers")}</span>
            )}
          </div>

          <label className="form-field">
            <span>{t("ownership.modal.midtermOwner")}</span>
            <select value={midtermManagerId} onChange={(event) => setMidtermManagerId(event.currentTarget.value)}>
              <option value="">{t("ownership.modal.unassigned")}</option>
              {scopedTeachers.map((teacher) => (
                <option key={`mid-${teacher.id}`} value={teacher.id}>
                  {teacher.full_name ?? teacher.username}
                </option>
              ))}
            </select>
          </label>

          <label className="form-field">
            <span>{t("ownership.modal.finalOwner")}</span>
            <select value={finalManagerId} onChange={(event) => setFinalManagerId(event.currentTarget.value)}>
              <option value="">{t("ownership.modal.unassigned")}</option>
              {scopedTeachers.map((teacher) => (
                <option key={`final-${teacher.id}`} value={teacher.id}>
                  {teacher.full_name ?? teacher.username}
                </option>
              ))}
            </select>
          </label>
        </div>
      ) : null}
    </Modal>
  );
}
