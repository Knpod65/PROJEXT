import { useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { useI18n } from "@/i18n";
import type { UserOut, UserRole } from "@/types/api";

const roleOptions: UserRole[] = [
  "admin",
  "teacher",
  "staff",
  "dept_supervisor",
  "esq_head",
  "secretary",
  "print_shop",
  "student",
];

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export interface UserEditorValues {
  username: string;
  email: string;
  full_name: string;
  department: string;
  role: UserRole;
  is_active: boolean;
  password?: string;
}

interface UserEditorModalProps {
  open: boolean;
  user?: UserOut | null;
  saving?: boolean;
  onClose: () => void;
  onSave: (values: UserEditorValues) => Promise<void>;
}

function initialValues(user?: UserOut | null): UserEditorValues {
  return {
    username: user?.username ?? "",
    email: user?.email ?? "",
    full_name: user?.full_name ?? "",
    department: user?.department ?? user?.dept_code ?? "",
    role: user?.role ?? "staff",
    is_active: user?.is_active ?? true,
    password: "",
  };
}

export function UserEditorModal({ onClose, onSave, open, saving = false, user }: UserEditorModalProps) {
  const { t } = useI18n();
  const [values, setValues] = useState<UserEditorValues>(() => initialValues(user));
  const [error, setError] = useState<string | null>(null);
  const isCreateMode = !user;

  useEffect(() => {
    if (!open) {
      return;
    }
    setValues(initialValues(user));
    setError(null);
  }, [open, user]);

  const setField = <K extends keyof UserEditorValues>(field: K, value: UserEditorValues[K]) => {
    setValues((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async () => {
    if (!values.full_name.trim()) {
      setError(t("users.form.validation.fullName"));
      return;
    }
    if (!values.username.trim()) {
      setError(t("users.form.validation.username"));
      return;
    }
    if (!values.email.trim()) {
      setError(t("users.form.validation.email"));
      return;
    }
    if (!EMAIL_PATTERN.test(values.email.trim())) {
      setError(t("users.form.validation.emailFormat"));
      return;
    }
    if (isCreateMode && !(values.password ?? "").trim()) {
      setError(t("users.form.validation.password"));
      return;
    }

    setError(null);
    await onSave({
      ...values,
      username: values.username.trim(),
      email: values.email.trim(),
      full_name: values.full_name.trim(),
      department: values.department.trim(),
      password: values.password?.trim() || undefined,
    });
  };

  return (
    <Modal
      open={open}
      title={isCreateMode ? t("users.modal.addTitle") : t("users.modal.editTitle")}
      onClose={onClose}
      footer={
        <div className="inline-actions">
          <Button type="button" variant="outline" onClick={onClose} disabled={saving}>
            {t("common.cancel")}
          </Button>
          <Button type="button" loading={saving} onClick={() => void handleSubmit()}>
            {isCreateMode ? t("users.modal.createAction") : t("users.modal.saveAction")}
          </Button>
        </div>
      }
    >
      <div className="user-editor-grid">
        <label className="form-field">
          <span>{t("users.form.fullName")}</span>
          <input
            value={values.full_name}
            onChange={(event) => setField("full_name", event.currentTarget.value)}
            placeholder={t("users.form.fullNamePlaceholder")}
          />
        </label>

        <label className="form-field">
          <span>{t("users.form.username")}</span>
          <input
            value={values.username}
            onChange={(event) => setField("username", event.currentTarget.value)}
            placeholder={t("users.form.usernamePlaceholder")}
          />
        </label>

        <label className="form-field">
          <span>{t("users.form.email")}</span>
          <input
            type="email"
            value={values.email}
            onChange={(event) => setField("email", event.currentTarget.value)}
            placeholder={t("users.form.emailPlaceholder")}
          />
        </label>

        <label className="form-field">
          <span>{t("users.form.department")}</span>
          <input
            value={values.department}
            onChange={(event) => setField("department", event.currentTarget.value)}
            placeholder={t("users.form.departmentPlaceholder")}
          />
        </label>

        <label className="form-field">
          <span>{t("users.form.role")}</span>
          <select
            value={values.role}
            onChange={(event) => setField("role", event.currentTarget.value as UserRole)}
          >
            {roleOptions.map((role) => (
              <option key={role} value={role}>
                {t(`roles.${role}`)}
              </option>
            ))}
          </select>
        </label>

        {isCreateMode ? (
          <label className="form-field">
            <span>{t("users.form.password")}</span>
            <input
              type="password"
              value={values.password ?? ""}
              onChange={(event) => setField("password", event.currentTarget.value)}
              placeholder={t("users.form.passwordPlaceholder")}
            />
          </label>
        ) : (
          <label className="form-field">
            <span>{t("users.form.status")}</span>
            <select
              value={values.is_active ? "active" : "inactive"}
              onChange={(event) => setField("is_active", event.currentTarget.value === "active")}
            >
              <option value="active">{t("common.active")}</option>
              <option value="inactive">{t("common.inactive")}</option>
            </select>
          </label>
        )}

        {error ? <p className="user-editor-error">{error}</p> : null}
      </div>
    </Modal>
  );
}
