import type React from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { SubmissionSummaryCard } from "@/components/submissions/SubmissionSummaryCard";
import { SubmissionsTable } from "@/components/submissions/SubmissionsTable";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { FilterBar } from "@/components/ui/FilterBar";
import { Icon } from "@/components/ui/Icon";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs } from "@/components/ui/Tabs";
import { useI18n } from "@/i18n";
import { listMessages, listSubmissions, sendMessage } from "@/services/submission.service";
import { useAuth } from "@/store/auth.store";
import { useEffectiveRole } from "@/hooks/useEffectiveRole";
import { useUi } from "@/store/ui.store";
import type { SubmissionListItem, SubmissionMessage } from "@/types/api";
import { formatDateTime } from "@/utils/format";
import { canViewOwnExamWork } from "@/utils/permissions";

type SubmissionTab = "all" | "pending" | "approved" | "rejected";

export function SubmissionsPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const role = useEffectiveRole();
  const { toast } = useUi();
  const { t } = useI18n();
  const [activeTab, setActiveTab] = useState<SubmissionTab>("all");
  const [items, setItems] = useState<SubmissionListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selected, setSelected] = useState<SubmissionListItem | null>(null);
  const [messages, setMessages] = useState<SubmissionMessage[]>([]);
  const [messageText, setMessageText] = useState("");
  const [messageLoading, setMessageLoading] = useState(false);

  const loadSubmissions = useCallback(async () => {
    setLoading(true);
    try {
      const response = await listSubmissions();
      setItems(response);
    } catch (err) {
      toast(err instanceof Error ? err.message : t("legacy.submissions.toast.loadFailed"), "error");
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    void loadSubmissions();
  }, [loadSubmissions]);

  useEffect(() => {
    if (!selected) return;

    void listMessages(selected.id)
      .then(setMessages)
      .catch(() => setMessages([]));
  }, [selected]);

  const filteredItems = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    return items
      .filter((item) => (activeTab === "all" ? true : item.status === activeTab))
      .filter((item) => {
        if (!query) {
          return true;
        }

        const haystack = [item.course_id, item.course_name, item.submitter, item.section_no]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();

        return haystack.includes(query);
      })
      .sort((left, right) => {
        const leftTime = left.submitted_at ? Date.parse(left.submitted_at) : 0;
        const rightTime = right.submitted_at ? Date.parse(right.submitted_at) : 0;
        return rightTime - leftTime;
      });
  }, [activeTab, items, searchQuery]);

  const tabItems = useMemo(
    () => [
      { key: "all", label: t("common.all"), badge: items.length },
      { key: "pending", label: t("legacy.submissions.status.pending"), badge: items.filter((item) => item.status === "pending").length },
      { key: "approved", label: t("legacy.submissions.status.approved"), badge: items.filter((item) => item.status === "approved").length },
      { key: "rejected", label: t("legacy.submissions.status.rejected"), badge: items.filter((item) => item.status === "rejected").length },
    ],
    [items, t],
  );

  const handleSendMessage = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selected || !messageText.trim()) return;

    setMessageLoading(true);
    try {
      await sendMessage(selected.id, messageText.trim());
      setMessageText("");
      const updated = await listMessages(selected.id);
      setMessages(updated);
      toast(t("legacy.submissions.toast.messageSent"), "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : t("legacy.submissions.toast.messageFailed"), "error");
    } finally {
      setMessageLoading(false);
    }
  };

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero page-hero--submissions">
        <div>
          <span className="page-hero__eyebrow">{t("legacy.submissions.eyebrow")}</span>
          <h1 className="page-hero__title">{t("legacy.submissions.title")}</h1>
          <p className="page-hero__description">{t("legacy.submissions.description")}</p>
        </div>
        <div className="page-hero__actions">
          <Button
            iconLeft={<Icon name="description" />}
            type="button"
            onClick={() => navigate(canViewOwnExamWork(user) ? "/myexam" : "/schedule")}
          >
            {canViewOwnExamWork(user) ? t("legacy.submissions.actions.openMyExam") : t("legacy.submissions.actions.reviewSchedule")}
          </Button>
        </div>
      </section>

      {loading ? (
        <div className="page-stack">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="card-skeleton" />
          ))}
        </div>
      ) : (
        <>
          <section className="submission-summary-grid">
            <SubmissionSummaryCard
              icon="database"
              label={t("legacy.submissions.metrics.total")}
              note={t("legacy.submissions.metrics.totalNote")}
              value={String(items.length)}
            />
            <SubmissionSummaryCard
              icon="visibility"
              label={t("legacy.submissions.metrics.pending")}
              note={t("legacy.submissions.metrics.pendingNote")}
              tone="warning"
              value={String(items.filter((item) => item.status === "pending").length)}
            />
            <SubmissionSummaryCard
              icon="check_circle"
              label={t("legacy.submissions.metrics.approved")}
              note={t("legacy.submissions.metrics.approvedNote")}
              tone="success"
              value={String(items.filter((item) => item.status === "approved").length)}
            />
            <SubmissionSummaryCard
              icon="report"
              label={t("legacy.submissions.metrics.rejected")}
              note={t("legacy.submissions.metrics.rejectedNote")}
              tone="danger"
              value={String(items.filter((item) => item.status === "rejected").length)}
            />
          </section>

          <Tabs activeKey={activeTab} items={tabItems} onChange={(key) => setActiveTab(key as SubmissionTab)} />

          <FilterBar
            actions={
              <Button iconLeft={<Icon name="refresh" />} type="button" variant="ghost" onClick={() => void loadSubmissions()}>
                {t("common.refresh")}
              </Button>
            }
          >
            <label className="filter-field">
              <span>{t("common.search")}</span>
              <input
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder={t("legacy.submissions.searchPlaceholder")}
                value={searchQuery}
              />
            </label>
          </FilterBar>

          {filteredItems.length === 0 ? (
            <EmptyState
              icon={<Icon name="inbox" />}
              title={t("legacy.submissions.emptyTitle")}
              description={t("legacy.submissions.emptyDescription")}
            />
          ) : (
            <SubmissionsTable items={filteredItems} onOpenMessages={setSelected} />
          )}
        </>
      )}

      <Modal
        open={Boolean(selected)}
        title={selected ? t("legacy.submissions.threadTitleFor", { value: selected.course_name ?? selected.course_id ?? t("legacy.submissions.submission") }) : t("legacy.submissions.threadTitle")}
        onClose={() => setSelected(null)}
      >
        <div className="message-thread">
          {messages.length === 0 ? (
            <EmptyState icon={<Icon name="mail" />} title={t("legacy.submissions.noMessages")} />
          ) : (
            messages.map((message) => (
              <div key={message.id} className="message-thread__item">
                <strong>{message.sender_name ?? t("legacy.submissions.emsUser")}</strong>
                <p>{message.message}</p>
                <span>{formatDateTime(message.created_at)}</span>
              </div>
            ))
          )}
        </div>

        <form className="message-thread__composer" onSubmit={handleSendMessage}>
          <textarea
            onChange={(event) => setMessageText(event.target.value)}
            placeholder={t("legacy.submissions.messagePlaceholder")}
            rows={4}
            value={messageText}
          />
          <Button loading={messageLoading} type="submit">
            {t("legacy.submissions.actions.sendMessage")}
          </Button>
        </form>
      </Modal>
    </div>
  );
}
