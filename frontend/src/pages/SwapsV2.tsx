import { useEffect, useState } from "react";

import { SwapCreateModal } from "@/components/swaps/SwapCreateModal";
import { SwapRespondModal } from "@/components/swaps/SwapRespondModal";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs } from "@/components/ui/Tabs";
import { useI18n } from "@/i18n";
import { useSwapsLive, type SwapsTab } from "@/hooks/useSwapsLive";
import type { MySupervisionSlot } from "@/services/swap.service";
import { useAuth } from "@/store/auth.store";
import { useEffectiveRole } from "@/hooks/useEffectiveRole";
import { useUi } from "@/store/ui.store";
import type { SwapItem } from "@/types/api";
import { formatDateTime } from "@/utils/format";
import { canManageExamPeriods } from "@/utils/permissions";

function SwapStatusBadge({ status }: { status: string }) {
  const { t } = useI18n();
  const cls = `swap-badge swap-badge--${status}`;
  return <span className={cls}>{t(`legacy.swaps.status.${status}`)}</span>;
}

function ShiftCell({ shift }: { shift: SwapItem["my_shift"] }) {
  if (!shift) return <span className="text-muted">—</span>;
  return (
    <div className="swap-shift-mini">
      <strong>{shift.course ?? "?"} §{shift.section_no ?? "?"}</strong>
      <span>{shift.date ?? "?"} {shift.time ?? "?"}</span>
      <span className="text-muted">{shift.room ?? "?"}</span>
    </div>
  );
}

function SwapRow({
  swap,
  isIncoming,
  onCancel,
  onRespond,
}: {
  swap: SwapItem;
  isIncoming: boolean;
  onCancel: (id: number) => void;
  onRespond: (swap: SwapItem) => void;
}) {
  const { t } = useI18n();
  const canCancel = swap.status === "pending" && swap.is_requester;

  return (
    <tr>
      <td>
        <SwapStatusBadge status={swap.status} />
      </td>
      <td>
        <div className="swap-party">
          <strong>{swap.requester_name ?? "—"}</strong>
          <span className="text-muted">{swap.is_requester ? t("legacy.swaps.you") : t("legacy.swaps.requester")}</span>
        </div>
      </td>
      <td><ShiftCell shift={swap.my_shift} /></td>
      <td><ShiftCell shift={swap.their_shift} /></td>
      <td>
        <div className="swap-party">
          <strong>{swap.target_name ?? "—"}</strong>
        </div>
      </td>
      <td>
        {swap.message ? <span className="text-muted">{swap.message}</span> : <span className="text-muted">—</span>}
        {swap.reject_reason ? (
          <span className="swap-reject-reason">{swap.reject_reason}</span>
        ) : null}
      </td>
      <td className="text-muted">{swap.created_at ? formatDateTime(swap.created_at) : "—"}</td>
      <td>
        <div className="inline-actions">
          {isIncoming && swap.status === "pending" && (
            <Button type="button" size="sm" onClick={() => onRespond(swap)}>
              {t("legacy.swaps.actions.respond")}
            </Button>
          )}
          {canCancel && (
            <Button type="button" size="sm" variant="ghost" onClick={() => onCancel(swap.id)}>
              {t("common.cancel")}
            </Button>
          )}
        </div>
      </td>
    </tr>
  );
}

function SwapTable({
  rows,
  isIncoming,
  onCancel,
  onRespond,
}: {
  rows: SwapItem[];
  isIncoming: boolean;
  onCancel: (id: number) => void;
  onRespond: (swap: SwapItem) => void;
}) {
  const { t } = useI18n();
  if (rows.length === 0) {
    return (
      <EmptyState
        icon={<Icon name="swap_horiz" />}
        title={t("legacy.swaps.emptyTitle")}
        description={t("legacy.swaps.emptyDescription")}
      />
    );
  }

  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            <th>{t("common.status")}</th>
            <th>{t("legacy.swaps.table.from")}</th>
            <th>{t("legacy.swaps.table.theirSlot")}</th>
            <th>{t("legacy.swaps.table.yourSlot")}</th>
            <th>{t("legacy.swaps.table.to")}</th>
            <th>{t("common.notes")}</th>
            <th>{t("common.date")}</th>
            <th>{t("common.actions")}</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((swap) => (
            <SwapRow
              key={swap.id}
              swap={swap}
              isIncoming={isIncoming}
              onCancel={onCancel}
              onRespond={onRespond}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function SwapsV2Page() {
  const { t } = useI18n();
  const { toast } = useUi();
  const { user } = useAuth();
  const role = useEffectiveRole();
  const isAdmin = canManageExamPeriods(user);

  const {
    busy,
    doCancel,
    doCreate,
    doRespond,
    error,
    history,
    incoming,
    load,
    loadMySupervisions,
    loading,
    mine,
    setTab,
    stats,
    tab,
  } = useSwapsLive();

  const [showCreate, setShowCreate] = useState(false);
  const [respondTarget, setRespondTarget] = useState<SwapItem | null>(null);
  const [mySlots, setMySlots] = useState<MySupervisionSlot[]>([]);
  const [loadingSlots, setLoadingSlots] = useState(false);

  useEffect(() => {
    void load();
  }, [load]);

  const handleOpenCreate = async () => {
    setShowCreate(true);
    setLoadingSlots(true);
    try {
      const slots = await loadMySupervisions();
      setMySlots(slots);
    } catch {
      setMySlots([]);
    } finally {
      setLoadingSlots(false);
    }
  };

  const handleCreate = async (supervisionId: number, targetUserId: number, message?: string) => {
    try {
      await doCreate(supervisionId, targetUserId, message);
      setShowCreate(false);
      toast(t("legacy.swaps.toast.sent"), "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : t("legacy.swaps.toast.createFailed"), "error");
    }
  };

  const handleRespond = async (swapId: number, accept: boolean, reason?: string) => {
    try {
      await doRespond(swapId, accept, reason);
      setRespondTarget(null);
      toast(accept ? t("legacy.swaps.toast.accepted") : t("legacy.swaps.toast.rejected"), accept ? "success" : "warning");
    } catch (err) {
      toast(err instanceof Error ? err.message : t("legacy.swaps.toast.respondFailed"), "error");
    }
  };

  const handleCancel = async (swapId: number) => {
    try {
      await doCancel(swapId);
      toast(t("legacy.swaps.toast.cancelled"), "warning");
    } catch (err) {
      toast(err instanceof Error ? err.message : t("legacy.swaps.toast.cancelFailed"), "error");
    }
  };

  const tabItems = [
    { key: "mine" as SwapsTab, label: t("legacy.swaps.tabs.mine"), badge: stats.pendingMine || undefined },
    { key: "incoming" as SwapsTab, label: t("legacy.swaps.tabs.incoming"), badge: stats.incomingCount || undefined },
    { key: "history" as SwapsTab, label: t("legacy.swaps.tabs.history") },
  ];

  const activeRows = tab === "mine" ? mine : tab === "incoming" ? incoming : history;
  const isIncomingTab = tab === "incoming";

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">{t("legacy.swaps.eyebrow")}</span>
          <h1 className="page-hero__title">{t("legacy.swaps.title")}</h1>
          <p className="page-hero__description">{t("legacy.swaps.description")}</p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => void load()} disabled={loading}>
            {t("common.refresh")}
          </Button>
          {!isAdmin && (
            <Button type="button" onClick={() => void handleOpenCreate()}>
              {t("legacy.swaps.actions.request")}
            </Button>
          )}
        </div>
      </section>

      <div className="stitch-metric-grid">
        <article className="dashboard-metric dashboard-metric--accent">
          <div className="dashboard-metric__icon"><Icon name="pending_actions" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("legacy.swaps.metrics.pendingMine")}</p>
            <strong className="dashboard-metric__value">{stats.pendingMine}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--warning">
          <div className="dashboard-metric__icon"><Icon name="inbox" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("legacy.swaps.metrics.incoming")}</p>
            <strong className="dashboard-metric__value">{stats.incomingCount}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--neutral">
          <div className="dashboard-metric__icon"><Icon name="history" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("legacy.swaps.metrics.totalMine")}</p>
            <strong className="dashboard-metric__value">{stats.totalMine}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--success">
          <div className="dashboard-metric__icon"><Icon name="task_alt" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("legacy.swaps.metrics.resolved")}</p>
            <strong className="dashboard-metric__value">{stats.historyCount}</strong>
          </div>
        </article>
      </div>

      {error && (
        <Card title={t("legacy.swaps.errorTitle")}>
          <p className="import-issue import-issue--error">{error}</p>
          <Button type="button" variant="ghost" onClick={() => void load()}>{t("common.retry")}</Button>
        </Card>
      )}

      <Card title={t("legacy.swaps.cardTitle")}>
        <Tabs
          activeKey={tab}
          items={tabItems}
          onChange={(key) => setTab(key as SwapsTab)}
        />

        {loading ? (
          <div className="page-stack">
            {[0, 1, 2].map((i) => <Skeleton key={i} className="dashboard-skeleton" />)}
          </div>
        ) : (
          <SwapTable
            rows={activeRows}
            isIncoming={isIncomingTab}
            onCancel={(id) => void handleCancel(id)}
            onRespond={(swap) => setRespondTarget(swap)}
          />
        )}
      </Card>

      <SwapCreateModal
        open={showCreate}
        supervisions={mySlots}
        loadingSlots={loadingSlots}
        busy={busy}
        onClose={() => setShowCreate(false)}
        onSubmit={(supId, targetId, msg) => void handleCreate(supId, targetId, msg)}
      />

      <SwapRespondModal
        swap={respondTarget}
        busy={busy}
        onClose={() => setRespondTarget(null)}
        onRespond={(id, accept, reason) => void handleRespond(id, accept, reason)}
      />
    </div>
  );
}
