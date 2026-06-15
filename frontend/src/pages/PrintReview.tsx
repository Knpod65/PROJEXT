import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs } from "@/components/ui/Tabs";
import { useI18n } from "@/i18n";
import {
  approveSubmission,
  getSubmissionForSection,
  listSubmissions,
  sendMessage,
} from "@/services/submission.service";
import { useAuth } from "@/store/auth.store";
import { useEffectiveRole } from "@/hooks/useEffectiveRole";
import { usePeriod } from "@/store/period.store";
import { useUi } from "@/store/ui.store";
import type { SubmissionDetail, SubmissionListItem } from "@/types/api";
import { canApproveSubmission } from "@/utils/permissions";

// ── Status badge ───────────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const { t } = useI18n();
  const map: Record<string, { labelKey: string; cls: string }> = {
    draft:     { labelKey: "legacy.printReview.status.draft",     cls: "pr-badge pr-badge--draft" },
    submitted: { labelKey: "legacy.printReview.status.submitted", cls: "pr-badge pr-badge--submitted" },
    approved:  { labelKey: "legacy.printReview.status.approved",  cls: "pr-badge pr-badge--approved" },
    rejected:  { labelKey: "legacy.printReview.status.rejected",  cls: "pr-badge pr-badge--rejected" },
    released:  { labelKey: "legacy.printReview.status.released",  cls: "pr-badge pr-badge--released" },
  };
  const entry = map[status];
  return <span className={entry?.cls ?? "pr-badge"}>{entry ? t(entry.labelKey) : status}</span>;
}

function PrintSpecBadge({ duplex, staple }: { duplex?: boolean; staple?: string }) {
  const { t } = useI18n();
  if (duplex === undefined && !staple) return null;
  const parts = [];
  if (duplex) parts.push(t("legacy.printReview.spec.duplex"));
  if (staple && staple !== "none") parts.push(t("legacy.printReview.spec.staple", { value: staple.replace("_", " ") }));
  if (parts.length === 0) parts.push(t("legacy.printReview.spec.simplexNoStaple"));
  return <span className="pr-spec-tag">{parts.join(" / ")}</span>;
}

// ── Detail panel ───────────────────────────────────────────────

function SubmissionDetailPanel({
  item,
  onClose,
  onApprove,
  onReject,
  isAdmin,
}: {
  item: SubmissionListItem;
  onClose: () => void;
  onApprove: (id: number) => Promise<void>;
  onReject: (id: number, reason: string) => Promise<void>;
  isAdmin: boolean;
}) {
  const { t } = useI18n();
  const { toast } = useUi();
  const [detail, setDetail] = useState<SubmissionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [rejectReason, setRejectReason] = useState("");
  const [showReject, setShowReject] = useState(false);
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState("");
  const [sendingNote, setSendingNote] = useState(false);

  useEffect(() => {
    setLoading(true);
    getSubmissionForSection(item.section_id)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setLoading(false));
  }, [item.section_id]);

  const handleApprove = async () => {
    setBusy(true);
    try {
      await onApprove(item.id);
      toast(t("legacy.printReview.toast.approved"), "success");
      onClose();
    } finally { setBusy(false); }
  };

  const handleReject = async () => {
    if (!rejectReason.trim()) { toast(t("legacy.printReview.toast.reasonRequired"), "error"); return; }
    setBusy(true);
    try {
      await onReject(item.id, rejectReason.trim());
      toast(t("legacy.printReview.toast.returned"), "warning");
      onClose();
    } finally { setBusy(false); }
  };

  const handleSendNote = async () => {
    if (!note.trim()) return;
    setSendingNote(true);
    try {
      await sendMessage(item.id, note.trim());
      setNote("");
      toast(t("legacy.printReview.toast.noteSent"), "success");
    } catch {
      toast(t("legacy.printReview.toast.noteFailed"), "error");
    } finally { setSendingNote(false); }
  };

  return (
    <Modal
      open
      title={t("legacy.printReview.detail.title", { name: item.course_name ?? item.course_id ?? t("legacy.printReview.cardTitle"), section: item.section_no ?? "" })}
      onClose={onClose}
      footer={
        isAdmin && item.status === "submitted" ? (
          <div className="inline-actions">
            <Button type="button" variant="outline" onClick={onClose}>{t("common.cancel")}</Button>
            {showReject ? (
              <>
                <Button type="button" variant="outline" onClick={() => setShowReject(false)}>{t("common.back")}</Button>
                <Button type="button" variant="danger" loading={busy} disabled={!rejectReason.trim()} onClick={handleReject}>
                  {t("legacy.printReview.actions.returnWithComments")}
                </Button>
              </>
            ) : (
              <>
                <Button type="button" variant="ghost" onClick={() => setShowReject(true)}>
                  {t("legacy.printReview.actions.return")}
                </Button>
                <Button type="button" loading={busy} onClick={handleApprove}>
                  {t("legacy.printReview.actions.approve")}
                </Button>
              </>
            )}
          </div>
        ) : (
          <Button type="button" variant="outline" onClick={onClose}>{t("common.close")}</Button>
        )
      }
    >
      {loading ? (
        <Skeleton className="dashboard-skeleton" />
      ) : !detail ? (
        <p className="text-muted">{t("legacy.printReview.detail.loadFailed")}</p>
      ) : (
        <div className="pr-detail">
          <div className="pr-detail__grid">
            <div className="pr-detail__field">
              <span>{t("common.status")}</span>
              <StatusBadge status={detail.status ?? "draft"} />
            </div>
            <div className="pr-detail__field">
              <span>{t("legacy.printReview.detail.examMethod")}</span>
              <strong>{detail.exam_type_choice ? t(`legacy.printReview.method.${detail.exam_type_choice}`) : t("common.notRecorded")}</strong>
            </div>
            <div className="pr-detail__field">
              <span>{t("legacy.printReview.detail.pdfUploaded")}</span>
              <strong>{detail.has_uploaded_pdf ? t("common.yes") : t("common.no")}</strong>
            </div>
            <div className="pr-detail__field">
              <span>{t("legacy.printReview.detail.pages")}</span>
              <strong>{detail.a4_pages_count ?? "—"}</strong>
            </div>
            <div className="pr-detail__field">
              <span>{t("legacy.printReview.detail.sharedExam")}</span>
              <strong>{detail.is_shared_exam ? t("common.yes") : t("common.no")}</strong>
            </div>
            {detail.answer_formats && detail.answer_formats.length > 0 && (
              <div className="pr-detail__field pr-detail__field--full">
                <span>{t("legacy.printReview.detail.answerFormats")}</span>
                <strong>{detail.answer_formats.join(", ")}</strong>
              </div>
            )}
          </div>

          {detail.admin_note && (
            <div className="pr-admin-note">
              <Icon name="info" /> <span>{detail.admin_note}</span>
            </div>
          )}

          {detail.rejected_reason && (
            <div className="pr-rejected-note">
              <Icon name="undo" /> <span><strong>{t("legacy.printReview.detail.returned")}:</strong> {detail.rejected_reason}</span>
            </div>
          )}

          {showReject && (
            <div className="form-field" style={{ marginTop: "12px" }}>
              <label htmlFor="reject-reason">{t("legacy.printReview.detail.returnReason")}</label>
              <textarea
                id="reject-reason"
                rows={3}
                value={rejectReason}
                placeholder={t("legacy.printReview.detail.returnPlaceholder")}
                onChange={(e) => setRejectReason(e.target.value)}
              />
            </div>
          )}

          {/* Quick note */}
          <div className="pr-note-row">
            <input
              type="text"
              placeholder={t("legacy.printReview.detail.notePlaceholder")}
              value={note}
              onChange={(e) => setNote(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") void handleSendNote(); }}
            />
            <Button type="button" size="sm" variant="outline" loading={sendingNote} onClick={handleSendNote}>
              {t("legacy.printReview.actions.sendNote")}
            </Button>
          </div>
        </div>
      )}
    </Modal>
  );
}

// ── Row ────────────────────────────────────────────────────────

function PrintRow({
  item,
  onOpen,
}: {
  item: SubmissionListItem;
  onOpen: () => void;
}) {
  const { t } = useI18n();
  const isOnsite = item.exam_type_choice === "onsite";
  const missingPdf = isOnsite && !item.has_uploaded_pdf;

  return (
    <tr className={missingPdf ? "row-warning" : ""}>
      <td>
        <div>
          <strong>{item.course_id ?? "—"}</strong>
          <span className="text-muted"> §{item.section_no ?? "?"}</span>
        </div>
        <div className="text-muted" style={{ fontSize: "0.8rem" }}>{item.course_name ?? ""}</div>
      </td>
      <td className="text-muted">{item.submitter ?? "—"}</td>
      <td>
        <StatusBadge status={item.status} />
      </td>
      <td>
        <span className="pr-type-tag">{item.exam_type_choice ? t(`legacy.printReview.method.${item.exam_type_choice}`) : t("common.notRecorded")}</span>
      </td>
      <td>
        {missingPdf && <span className="pr-missing-chip"><Icon name="warning" /> {t("legacy.printReview.readiness.missingPdf")}</span>}
        {isOnsite && item.has_uploaded_pdf && <span className="pr-ok-chip"><Icon name="picture_as_pdf" /> {t("legacy.printReview.readiness.pdfReady")}</span>}
        {!isOnsite && item.exam_type_choice && <span className="pr-na-chip">{t("legacy.printReview.readiness.noPrint")}</span>}
      </td>
      <td>
        <Button type="button" size="sm" variant="outline" onClick={onOpen}>
          {t("legacy.printReview.actions.review")}
        </Button>
      </td>
    </tr>
  );
}

// ── Main page ──────────────────────────────────────────────────

type PrintTab = "all" | "submitted" | "approved" | "released" | "needs_attention";

export function PrintReviewPage() {
  const { t } = useI18n();
  const { toast } = useUi();
  const { user } = useAuth();
  const { activePeriod } = usePeriod();
  const role = useEffectiveRole();
  const isAdmin = canApproveSubmission(user);

  const [items, setItems] = useState<SubmissionListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<PrintTab>("all");
  const [selected, setSelected] = useState<SubmissionListItem | null>(null);
  const [search, setSearch] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listSubmissions();
      setItems(data);
    } catch (err) {
      toast(err instanceof Error ? err.message : t("legacy.printReview.toast.loadFailed"), "error");
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => { void load(); }, [load]);

  const handleApprove = async (submissionId: number) => {
    await approveSubmission(submissionId, true);
    await load();
  };

  const handleReject = async (submissionId: number, reason: string) => {
    await approveSubmission(submissionId, false, reason);
    await load();
  };

  const filtered = useMemo(() => {
    let base = items;
    if (activeTab === "submitted") base = items.filter((i) => i.status === "submitted");
    else if (activeTab === "approved") base = items.filter((i) => i.status === "approved");
    else if (activeTab === "released") base = items.filter((i) => i.status === "released");
    else if (activeTab === "needs_attention") {
      base = items.filter((i) => i.status === "rejected" || (i.exam_type_choice === "onsite" && !i.has_uploaded_pdf));
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      base = base.filter((i) =>
        `${i.course_id ?? ""} ${i.course_name ?? ""} ${i.submitter ?? ""} ${i.section_no ?? ""}`.toLowerCase().includes(q),
      );
    }
    return base;
  }, [items, activeTab, search]);

  const stats = useMemo(() => ({
    total: items.length,
    submitted: items.filter((i) => i.status === "submitted").length,
    approved: items.filter((i) => i.status === "approved" || i.status === "released").length,
    needsAction: items.filter((i) => i.status === "rejected" || (i.exam_type_choice === "onsite" && !i.has_uploaded_pdf)).length,
    onsiteReady: items.filter((i) => i.exam_type_choice === "onsite" && i.has_uploaded_pdf).length,
  }), [items]);

  const tabItems = [
    { key: "all", label: t("common.all"), badge: stats.total },
    { key: "submitted", label: t("legacy.printReview.status.submitted"), badge: stats.submitted || undefined },
    { key: "approved", label: t("legacy.printReview.tabs.approvedReleased"), badge: stats.approved || undefined },
    { key: "needs_attention", label: t("legacy.printReview.metrics.needsAttention"), badge: stats.needsAction || undefined },
    { key: "released", label: t("legacy.printReview.status.released") },
  ];

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">{t("legacy.printReview.eyebrow")}</span>
          <h1 className="page-hero__title">{t("legacy.printReview.title")}</h1>
          <p className="page-hero__description">{t("legacy.printReview.description")}</p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => void load()} disabled={loading}>
            {t("common.refresh")}
          </Button>
        </div>
      </section>

      {activePeriod && (
        <div className="wf-period-bar">
          <Icon name="calendar_month" />
          <span>{t("common.activePeriod")}: <strong>{activePeriod.label}</strong></span>
        </div>
      )}

      <div className="stitch-metric-grid">
        <article className="dashboard-metric dashboard-metric--accent">
          <div className="dashboard-metric__icon"><Icon name="description" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("legacy.printReview.metrics.total")}</p>
            <strong className="dashboard-metric__value">{stats.total}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--warning">
          <div className="dashboard-metric__icon"><Icon name="pending_actions" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("legacy.printReview.metrics.pending")}</p>
            <strong className="dashboard-metric__value">{stats.submitted}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--success">
          <div className="dashboard-metric__icon"><Icon name="check_circle" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("legacy.printReview.metrics.approved")}</p>
            <strong className="dashboard-metric__value">{stats.approved}</strong>
          </div>
        </article>
        <article className={`dashboard-metric ${stats.needsAction > 0 ? "dashboard-metric--danger" : "dashboard-metric--neutral"}`}>
          <div className="dashboard-metric__icon"><Icon name="warning" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("legacy.printReview.metrics.needsAttention")}</p>
            <strong className="dashboard-metric__value">{stats.needsAction}</strong>
          </div>
        </article>
      </div>

      <Card title={t("legacy.printReview.cardTitle")}>
        <Tabs activeKey={activeTab} items={tabItems} onChange={(k) => setActiveTab(k as PrintTab)} />

        <div className="filter-bar" style={{ marginBottom: "12px" }}>
          <input
            type="text"
            className="filter-bar__search"
            placeholder={t("legacy.printReview.searchPlaceholder")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <Button type="button" size="sm" variant="ghost" onClick={() => setSearch("")}>{t("common.clear")}</Button>
          )}
        </div>

        {loading ? (
          <div className="page-stack">
            {[0, 1, 2, 3].map((i) => <Skeleton key={i} className="dashboard-skeleton" />)}
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState
            icon={<Icon name="inbox" />}
            title={t("legacy.printReview.emptyTitle")}
            description={t("legacy.printReview.emptyDescription")}
          />
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>{t("legacy.printReview.table.courseSection")}</th>
                  <th>{t("legacy.printReview.table.teacher")}</th>
                  <th>{t("common.status")}</th>
                  <th>{t("legacy.printReview.table.method")}</th>
                  <th>{t("legacy.printReview.table.readiness")}</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((item) => (
                  <PrintRow key={item.id} item={item} onOpen={() => setSelected(item)} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {selected && (
        <SubmissionDetailPanel
          item={selected}
          onClose={() => setSelected(null)}
          onApprove={handleApprove}
          onReject={handleReject}
          isAdmin={isAdmin}
        />
      )}
    </div>
  );
}
