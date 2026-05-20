import { useAuth } from "@/store/auth.store";
import {
    canManageUsers,
    canViewUserList,
    canUseViewAs,
    canViewAll,
    canExportAdminReports,
    canExportOwnDepartment,
    canManageWorkflow,
    canSignWorkflow,
    canManageExamPeriods,
    canSubmitExamPaper,
    canApproveSubmission,
    canManageSchedule,
    canAccessPrintQueue,
    canManageOperationalWork,
    canAccessExternalExams,
    canViewOwnExamWork,
    canManageCoExam,
    canViewSettings,
    canEditSettings,
} from "@/utils/permissions";
import type { UserMe } from "@/types/api";

export interface PermissionState {
    user: UserMe | null;
    canManageUsers: boolean;
    canViewUserList: boolean;
    canUseViewAs: boolean;
    canViewAll: boolean;
    canExportAdminReports: boolean;
    canExportOwnDepartment: boolean;
    canManageWorkflow: boolean;
    canSignWorkflow: boolean;
    canManageExamPeriods: boolean;
    canSubmitExamPaper: boolean;
    canApproveSubmission: boolean;
    canManageSchedule: boolean;
    canAccessPrintQueue: boolean;
    canManageOperationalWork: boolean;
    canAccessExternalExams: boolean;
    canViewOwnExamWork: boolean;
    canManageCoExam: boolean;
    canViewSettings: boolean;
    canEditSettings: boolean;
}

export function usePermission(): PermissionState {
    const { user } = useAuth();

    return {
        user,
        canManageUsers: canManageUsers(user),
        canViewUserList: canViewUserList(user),
        canUseViewAs: canUseViewAs(user),
        canViewAll: canViewAll(user),
        canExportAdminReports: canExportAdminReports(user),
        canExportOwnDepartment: canExportOwnDepartment(user),
        canManageWorkflow: canManageWorkflow(user),
        canSignWorkflow: canSignWorkflow(user),
        canManageExamPeriods: canManageExamPeriods(user),
        canSubmitExamPaper: canSubmitExamPaper(user),
        canApproveSubmission: canApproveSubmission(user),
        canManageSchedule: canManageSchedule(user),
        canAccessPrintQueue: canAccessPrintQueue(user),
        canManageOperationalWork: canManageOperationalWork(user),
        canAccessExternalExams: canAccessExternalExams(user),
        canViewOwnExamWork: canViewOwnExamWork(user),
        canManageCoExam: canManageCoExam(user),
        canViewSettings: canViewSettings(user),
        canEditSettings: canEditSettings(user),
    };
}