import { useCallback, useMemo } from "react";

import type { PrintQueueJob } from "@/types/api";
import { getCopyCount } from "@/services/schedule.service";
import {
  completePrintJob,
  deliverPrintJob,
  dispatchPrintJob,
  listPrintQueue,
  startPrintJob,
} from "@/services/printing.service";

import { useAsyncData } from "./useAsyncData";
import { useEffectiveRole } from "./useEffectiveRole";

const supplyAlerts = [
  {
    id: "cyan",
    label: "Cyan toner",
    note: "Low stock detected for the next high-volume batch window.",
  },
  {
    id: "paper",
    label: "A4 security stock",
    note: "Dispatch cabinet refill recommended before the afternoon session.",
  },
  {
    id: "seal",
    label: "Tamper seals",
    note: "Enough for the current cycle, but reorder threshold is close.",
  },
];

export function getPrintJobActionLabel(status: PrintQueueJob["status"]) {
  switch (status) {
    case "queued":
      return "Start Job";
    case "processing":
      return "Complete";
    case "completed":
      return "Dispatch";
    case "dispatched":
      return "Mark Delivered";
    default:
      return "Delivered";
  }
}

export function usePrintQueueData() {
  const effectiveRole = useEffectiveRole();

  const loader = useCallback(async () => {
    const copyCountPromise =
      effectiveRole === "print_shop" ? Promise.resolve(null) : getCopyCount().catch(() => null);

    const [jobs, copyCount] = await Promise.all([
      listPrintQueue(),
      copyCountPromise,
    ]);

    return { jobs, copyCount };
  }, [effectiveRole]);

  const state = useAsyncData(loader, [loader]);
  const jobs = state.data?.jobs ?? [];

  const metrics = useMemo(
    () => ({
      pendingJobs: jobs.filter((job) => job.status !== "delivered").length,
      urgentJobs: jobs.filter((job) => job.priority === "high" && job.status !== "delivered").length,
      totalSheets:
        state.data?.copyCount?.grand_total ??
        jobs.reduce((sum, job) => sum + job.total_sheets, 0),
      totalCost: state.data?.copyCount?.cost ?? 0,
      sections: state.data?.copyCount?.sections_count ?? jobs.length,
    }),
    [jobs, state.data],
  );

  const advanceJob = useCallback(
    async (job: PrintQueueJob) => {
      switch (job.status) {
        case "queued":
          await startPrintJob(job.id);
          break;
        case "processing":
          await completePrintJob(job.id);
          break;
        case "completed":
          await dispatchPrintJob(job.id);
          break;
        case "dispatched":
          await deliverPrintJob(job.id);
          break;
        default:
          return;
      }

      await state.reload();
    },
    [state.reload],
  );

  return {
    ...state,
    jobs,
    metrics,
    supplyAlerts,
    advanceJob,
  };
}
