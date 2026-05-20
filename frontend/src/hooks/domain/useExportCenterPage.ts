import { useMemo } from "react";
import { useAsyncData } from "@/hooks/useAsyncData";
import { translate } from "@/i18n";
import {
  getPaperDistributionAssignments,
  getStaffWorkloadReport,
  type PaperDistributionAssignmentRow,
  type WorkloadSummaryRow,
} from "@/services/optimizer.service";
import { useAuth } from "@/store/auth.store";
import { getEffectiveRole } from "@/utils/roles";
import { formatNumber } from "@/utils/format";
import { buildDocumentExportUrl } from "@/services/documents.service";

export interface ExportCardAction {
  label: string;
  onClick: () => void;
}

export interface ExportCard {
  title: string;
  description: string;
  actions: ExportCardAction[];
}

export interface ExportStats {
  label: string;
  value: number | string;
}

export interface UseExportCenterPageReturn {
  isLoading: boolean;
  workloadLoading: boolean;
  distributionLoading: boolean;
  error: string | null;
  workloadSummary: WorkloadSummaryRow[];
  distributionRows: PaperDistributionAssignmentRow[];
  stats: ExportStats[];
  exportCards: ExportCard[];
  isAdmin: boolean;
  totalAssignments: number;
  fairnessScore: number;
}

function openExport(url: string) {
  window.open(url, "_blank", "noopener,noreferrer");
}

export function useExportCenterPage(): UseExportCenterPageReturn {
  const { user } = useAuth();
  const effectiveRole = getEffectiveRole(user);
  const isAdmin = effectiveRole === "admin";

  const workloadLoader = () => getStaffWorkloadReport();
  const distributionLoader = () => getPaperDistributionAssignments();

  const workloadState = useAsyncData(workloadLoader, [workloadLoader]);
  const distributionState = useAsyncData(distributionLoader, [distributionLoader]);

  const workloadSummary = workloadState.data?.summary ?? [];
  const distributionRows = distributionState.data?.rows ?? [];

  const stats = useMemo<ExportStats[]>(() => {
    const totalAssignments = workloadState.data?.total_assignments ?? 0;
    const fairnessScore = workloadState.data?.fairness_score ?? 0;
    return [
      { label: translate("exportCenter.stats.staffWorkloadRows"), value: formatNumber(workloadSummary.length) },
      { label: translate("exportCenter.stats.paperDistributionSlots"), value: formatNumber(distributionRows.length) },
      { label: translate("exportCenter.stats.totalDutyAssignments"), value: formatNumber(totalAssignments) },
      { label: translate("exportCenter.stats.fairnessSnapshot"), value: fairnessScore },
    ];
  }, [workloadSummary.length, distributionRows.length, workloadState.data?.total_assignments, workloadState.data?.fairness_score]);

  const exportCards = useMemo<ExportCard[]>(() => {
    return [
      {
        title: translate("exportCenter.cards.examDocuments.title"),
        description: translate("exportCenter.cards.examDocuments.description"),
        actions: [
          { label: translate("exportCenter.actions.allDocuments"), onClick: () => openExport(buildDocumentExportUrl({ document_type: "all" })) },
          { label: translate("exportCenter.actions.participantCodes"), onClick: () => openExport(buildDocumentExportUrl({ document_type: "participant_codes" })) },
          { label: translate("exportCenter.actions.signatureSheets"), onClick: () => openExport(buildDocumentExportUrl({ document_type: "signature_sheet" })) },
          { label: translate("exportCenter.actions.coverSheets"), onClick: () => openExport(buildDocumentExportUrl({ document_type: "envelope_cover" })) },
        ],
      },
      {
        title: translate("exportCenter.cards.optimizationResults.title"),
        description: translate("exportCenter.cards.optimizationResults.description"),
        actions: [
          { label: translate("exportCenter.actions.schedulePdf"), onClick: () => openExport("/api/exports/schedule") },
          { label: translate("exportCenter.actions.scheduleExcel"), onClick: () => openExport("/api/exports/schedule-excel") },
          { label: translate("exportCenter.actions.paperDistributionPdf"), onClick: () => openExport("/api/exports/paper-distribution-pdf") },
          { label: translate("exportCenter.actions.paperDistributionExcel"), onClick: () => openExport("/api/exports/paper-distribution-excel") },
        ],
      },
      {
        title: translate("exportCenter.cards.staffWorkload.title"),
        description: translate("exportCenter.cards.staffWorkload.description"),
        actions: [
          { label: translate("exportCenter.actions.summaryPdf"), onClick: () => openExport("/api/exports/workload-summary-pdf") },
          { label: translate("exportCenter.actions.workloadSummary"), onClick: () => openExport("/api/exports/workload-summary-excel") },
          { label: translate("exportCenter.actions.dutyDetail"), onClick: () => openExport("/api/exports/workload-detail-excel") },
          { label: translate("exportCenter.actions.fairnessSheet"), onClick: () => openExport("/api/exports/workload-summary-excel") },
        ],
      },
      {
        title: translate("exportCenter.cards.copyReports.title"),
        description: translate("exportCenter.cards.copyReports.description"),
        actions: [{ label: translate("exportCenter.actions.openCopyCount"), onClick: () => { window.location.href = "/copy"; } }],
      },
      ...(isAdmin
        ? [
            {
              title: translate("exportCenter.cards.workflowReports.title"),
              description: translate("exportCenter.cards.workflowReports.description"),
              actions: [{ label: translate("exportCenter.actions.openWorkflow"), onClick: () => { window.location.href = "/workflow"; } }],
            },
            {
              title: translate("exportCenter.cards.externalExams.title"),
              description: translate("exportCenter.cards.externalExams.description"),
              actions: [{ label: translate("exportCenter.actions.openExternalExams"), onClick: () => { window.location.href = "/external"; } }],
            },
            {
              title: translate("exportCenter.cards.historicalSchedule.title"),
              description: translate("exportCenter.cards.historicalSchedule.description"),
              actions: [{ label: translate("exportCenter.actions.openHistoricalReview"), onClick: () => { window.location.href = "/historical-schedules"; } }],
            },
          ]
        : []),
    ];
  }, [isAdmin, translate]);

  return {
    isLoading: workloadState.loading || distributionState.loading,
    workloadLoading: workloadState.loading,
    distributionLoading: distributionState.loading,
    error: workloadState.error || distributionState.error,
    workloadSummary,
    distributionRows,
    stats,
    exportCards,
    isAdmin,
    totalAssignments: workloadState.data?.total_assignments ?? 0,
    fairnessScore: workloadState.data?.fairness_score ?? 0,
  };
}