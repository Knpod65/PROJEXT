import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs } from "@/components/ui/Tabs";
import {
  approveSubmission,
  getSubmissionForSection,
  listSubmissions,
  sendMessage,
} from "@/services/submission.service";
import { useAuth } from "@/store/auth.store";
import { usePeriod } from "@/store/period.store";
import { useUi } from "@/store/ui.store";
import type { SubmissionDetail, SubmissionListItem } from "@/types/api";
import { getEffectiveRole } from "@/utils/roles";
import { canApproveSubmission } from "@/utils/permissions";

// ── Status badge ───────────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { label: string; cls: string }> = {
    draft:     { label: "Draft",     cls: "pr-badge pr-badge--draft" },
    submitted: { label: "Submitted", cls: "pr-badge pr-badge--submitted" },
    approved:  { label: "Approved",  cls: "pr-badge pr-badge--approved" },
    rejected:  { label: "Returned",  cls: "pr-badge pr-badge--rejected" },
    released:  { label: "Released",  cls: "pr-badge pr-badge--released" },
  };
  const { label, cls } = map[status] ?? { label: status, cls: "pr-badge" };
  return <span className={cls}>{label}</span>;
}

function PrintSpecBadge({ duplex, staple }: { duplex?: boolean; staple?: string }) {
  if (duplex === undefined && !staple) return null;
  const parts = [];
  if (duplex) parts.push("Duplex");
  if (staple && staple !== "none") parts.push(`Staple: ${staple.replace("_", " ")}`);
  if (parts.length === 0) parts.push("Simplex, no staple");
  return <span className="pr-spec-tag">{parts.join(" · ")}</span>;
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
      toast("Submission approved.", "success");
      onClose();
    } finally { setBusy(false); }
  };

  const handleReject = async () => {
    if (!rejectReason.trim()) { toast("Rejection reason is required.", "error"); return; }
    setBusy(true);
    try {
      await onReject(item.id, rejectReason.trim());
      toast("Submission returned.", "warning");
      onClose();
    } finally { setBusy(false); }
  };

  const handleSendNote = async () => {
    if (!note.trim()) return;
    setSendingNote(true);
    try {
      await sendMessage(item.id, note.trim());
      setNote("");
      toast("Note sent.", "success");
    } catch {
      toast("Failed to send note.", "error");
    } finally { setSendingNote(false); }
  };

  return (
    <Modal
      open
      title={`${item.course_name ?? item.course_id ?? "Submission"} §${item.section_no ?? ""}`}
      onClose={onClose}
      footer={
        isAdmin && item.status === "submitted" ? (
          <div className="inline-actions">
            <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
            {showReject ? (
              <>
                <Button type="button" variant="outline" onClick={() => setShowReject(false)}>Back</Button>
                <Button type="button" variant="danger" loading={busy} disabled={!rejectReason.trim()} onClick={handleReject}>
                  Return with comments
                </Button>
              </>
            ) : (
              <>
                <Button type="button" variant="ghost" onClick={() => setShowReject(true)}>
                  Return
                </Button>
                <Button type="button" loading={busy} onClick={handleApprove}>
                  Approve
                </Button>
              </>
            )}
          </div>
        ) : (
          <Button type="button" variant="outline" onClick={onClose}>Close</Button>
        )
      }
    >
      {loading ? (
        <Skeleton className="dashboard-skeleton" />
      ) : !detail ? (
        <p className="text-muted">Could not load submission details.</p>
      ) : (
        <div className="pr-detail">
          <div className="pr-detail__grid">
            <div className="pr-detail__field">
              <span>Status</span>
              <StatusBadge status={detail.status ?? "draft"} />
            </div>
            <div className="pr-detail__field">
              <span>Exam method</span>
              <strong>{detail.exam_type_choice ?? "Not set"}</strong>
            </div>
            <div className="pr-detail__field">
              <span>PDF uploaded</span>
              <strong>{detail.has_uploaded_pdf ? "Yes" : "No"}</strong>
            </div>
            <div className="pr-detail__field">
              <span>Pages</span>
              <strong>{detail.a4_pages_count ?? "—"}</strong>
            </div>
            <div className="pr-detail__field">
              <span>Shared exam</span>
              <strong>{detail.is_shared_exam ? "Yes" : "No"}</strong>
            </div>
            {detail.answer_formats && detail.answer_formats.length > 0 && (
              <div className="pr-detail__field pr-detail__field--full">
                <span>Answer formats</span>
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
              <Icon name="undo" /> <span><strong>Returned:</strong> {detail.rejected_reason}</span>
            </div>
          )}

          {showReject && (
            <div className="form-field" style={{ marginTop: "12px" }}>
              <label htmlFor="reject-reason">Return reason (required)</label>
              <textarea
                id="reject-reason"
                rows={3}
                value={rejectReason}
                placeholder="Explain what needs to be corrected…"
                onChange={(e) => setRejectReason(e.target.value)}
              />
            </div>
          )}

          {/* Quick note */}
          <div className="pr-note-row">
            <input
              type="text"
              placeholder="Add a note to teacher…"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") void handleSendNote(); }}
            />
            <Button type="button" size="sm" variant="outline" loading={sendingNote} onClick={handleSendNote}>
              Send note
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
        <span className="pr-type-tag">{item.exam_type_choice ?? "Not set"}</span>
      </td>
      <td>
        {missingPdf && <span className="pr-missing-chip"><Icon name="warning" /> Missing PDF</span>}
        {isOnsite && item.has_uploaded_pdf && <span className="pr-ok-chip"><Icon name="picture_as_pdf" /> PDF ready</span>}
        {!isOnsite && item.exam_type_choice && <span className="pr-na-chip">No print needed</span>}
      </td>
      <td>
        <Button type="button" size="sm" variant="outline" onClick={onOpen}>
          Review
        </Button>
      </td>
    </tr>
  );
}

// ── Main page ──────────────────────────────────────────────────

type PrintTab = "all" | "submitted" | "approved" | "released" | "needs_attention";

export function PrintReviewPage() {
  const { toast } = useUi();
  const { user } = useAuth();
  const { activePeriod } = usePeriod();
  const role = getEffectiveRole(user);
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
      toast(err instanceof Error ? err.message : "Failed to load.", "error");
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
    { key: "all", label: "All", badge: stats.total },
    { key: "submitted", label: "Pending review", badge: stats.submitted || undefined },
    { key: "approved", label: "Approved / Released", badge: stats.approved || undefined },
    { key: "needs_attention", label: "Needs attention", badge: stats.needsAction || undefined },
    { key: "released", label: "Released" },
  ];

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">Pre-print review</span>
          <h1 className="page-hero__title">Submission review & print handoff</h1>
          <p className="page-hero__description">
            Review submitted exam papers, approve for print, and track what's missing before handoff to the print shop.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => void load()} disabled={loading}>
            Refresh
          </Button>
        </div>
      </section>

      {activePeriod && (
        <div className="wf-period-bar">
          <Icon name="calendar_month" />
          <span>Active period: <strong>{activePeriod.label}</strong></span>
        </div>
      )}

      <div className="stitch-metric-grid">
        <article className="dashboard-metric dashboard-metric--accent">
          <div className="dashboard-metric__icon"><Icon name="description" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Total courses</p>
            <strong className="dashboard-metric__value">{stats.total}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--warning">
          <div className="dashboard-metric__icon"><Icon name="pending_actions" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Pending review</p>
            <strong className="dashboard-metric__value">{stats.submitted}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--success">
          <div className="dashboard-metric__icon"><Icon name="check_circle" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Approved</p>
            <strong className="dashboard-metric__value">{stats.approved}</strong>
          </div>
        </article>
        <article className={`dashboard-metric ${stats.needsAction > 0 ? "dashboard-metric--danger" : "dashboard-metric--neutral"}`}>
          <div className="dashboard-metric__icon"><Icon name="warning" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Needs attention</p>
            <strong className="dashboard-metric__value">{stats.needsAction}</strong>
          </div>
        </article>
      </div>

      <Card title="Submissions">
        <Tabs activeKey={activeTab} items={tabItems} onChange={(k) => setActiveTab(k as PrintTab)} />

        <div className="filter-bar" style={{ marginBottom: "12px" }}>
          <input
            type="text"
            className="filter-bar__search"
            placeholder="Search course, section, teacher…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <Button type="button" size="sm" variant="ghost" onClick={() => setSearch("")}>Clear</Button>
          )}
        </div>

        {loading ? (
          <div className="page-stack">
            {[0, 1, 2, 3].map((i) => <Skeleton key={i} className="dashboard-skeleton" />)}
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState
            icon={<Icon name="inbox" />}
            title="No submissions in this view"
            description="Switch tabs or clear the search filter."
          />
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Course / Section</th>
                  <th>Teacher</th>
                  <th>Status</th>
                  <th>Method</th>
                  <th>Print readiness</th>
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
