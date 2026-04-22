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
import { listMessages, listSubmissions, sendMessage } from "@/services/submission.service";
import { useAuth } from "@/store/auth.store";
import { useUi } from "@/store/ui.store";
import type { SubmissionListItem, SubmissionMessage } from "@/types/api";
import { formatDateTime } from "@/utils/format";
import { getEffectiveRole } from "@/utils/roles";

type SubmissionTab = "all" | "pending" | "approved" | "rejected";

export function SubmissionsPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const role = getEffectiveRole(user);
  const { toast } = useUi();
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
      toast(err instanceof Error ? err.message : "Unable to load submissions.", "error");
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
      { key: "all", label: "All", badge: items.length },
      { key: "pending", label: "Pending", badge: items.filter((item) => item.status === "pending").length },
      { key: "approved", label: "Approved", badge: items.filter((item) => item.status === "approved").length },
      { key: "rejected", label: "Needs work", badge: items.filter((item) => item.status === "rejected").length },
    ],
    [items],
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
      toast("Message sent.", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Unable to send this message.", "error");
    } finally {
      setMessageLoading(false);
    }
  };

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero page-hero--submissions">
        <div>
          <span className="page-hero__eyebrow">Editorial authority pattern</span>
          <h2 className="page-hero__title">Submission control board</h2>
          <p className="page-hero__description">
            The chosen Stitch submissions screen has been refactored into reusable EMS cards, filters, and a data table connected to the existing submission API and message threads.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button
            iconLeft={<Icon name="description" />}
            type="button"
            onClick={() => navigate(role === "teacher" ? "/myexam" : "/schedule")}
          >
            {role === "teacher" ? "Open my exam work" : "Review schedule"}
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
              label="Total records"
              note="All submissions visible to your current role."
              value={String(items.length)}
            />
            <SubmissionSummaryCard
              icon="visibility"
              label="Pending review"
              note="Records waiting for review or action."
              tone="warning"
              value={String(items.filter((item) => item.status === "pending").length)}
            />
            <SubmissionSummaryCard
              icon="check_circle"
              label="Approved"
              note="Submissions cleared for the next workflow step."
              tone="success"
              value={String(items.filter((item) => item.status === "approved").length)}
            />
            <SubmissionSummaryCard
              icon="report"
              label="Needs work"
              note="Items that need revision or follow-up."
              tone="danger"
              value={String(items.filter((item) => item.status === "rejected").length)}
            />
          </section>

          <Tabs activeKey={activeTab} items={tabItems} onChange={(key) => setActiveTab(key as SubmissionTab)} />

          <FilterBar
            actions={
              <Button iconLeft={<Icon name="refresh" />} type="button" variant="ghost" onClick={() => void loadSubmissions()}>
                Refresh data
              </Button>
            }
          >
            <label className="filter-field">
              <span>Search</span>
              <input
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder="Search subject, code, section, or owner"
                value={searchQuery}
              />
            </label>
          </FilterBar>

          {filteredItems.length === 0 ? (
            <EmptyState
              icon={<Icon name="inbox" />}
              title="No submissions match the current filters."
              description="Try switching tabs or clearing the search field."
            />
          ) : (
            <SubmissionsTable items={filteredItems} onOpenMessages={setSelected} />
          )}
        </>
      )}

      <Modal
        open={Boolean(selected)}
        title={selected ? `Message thread for ${selected.course_name ?? selected.course_id ?? "submission"}` : "Message thread"}
        onClose={() => setSelected(null)}
      >
        <div className="message-thread">
          {messages.length === 0 ? (
            <EmptyState icon={<Icon name="mail" />} title="No messages yet." />
          ) : (
            messages.map((message) => (
              <div key={message.id} className="message-thread__item">
                <strong>{message.sender_name ?? "EMS user"}</strong>
                <p>{message.message}</p>
                <span>{formatDateTime(message.created_at)}</span>
              </div>
            ))
          )}
        </div>

        <form className="message-thread__composer" onSubmit={handleSendMessage}>
          <textarea
            onChange={(event) => setMessageText(event.target.value)}
            placeholder="Write a note to the next reviewer or operations team"
            rows={4}
            value={messageText}
          />
          <Button loading={messageLoading} type="submit">
            Send message
          </Button>
        </form>
      </Modal>
    </div>
  );
}
