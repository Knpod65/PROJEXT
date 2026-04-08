import { useCallback, useEffect, useState, type FormEvent } from "react";

import { SubmissionCard } from "@/components/submissions/SubmissionCard";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs } from "@/components/ui/Tabs";
import { listMessages, listSubmissions, sendMessage } from "@/services/submission.service";
import type { SubmissionListItem, SubmissionMessage } from "@/types/api";
import { useUi } from "@/store/ui.store";
import { formatDateTime } from "@/utils/format";

const submissionTabs = [
  { key: "all", label: "ทั้งหมด" },
  { key: "pending", label: "รออนุมัติ" },
  { key: "approved", label: "อนุมัติแล้ว" },
  { key: "rejected", label: "ต้องแก้ไข" },
];

export function SubmissionsPage() {
  const { toast } = useUi();
  const [activeTab, setActiveTab] = useState("all");
  const [items, setItems] = useState<SubmissionListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<SubmissionListItem | null>(null);
  const [messages, setMessages] = useState<SubmissionMessage[]>([]);
  const [messageText, setMessageText] = useState("");
  const [messageLoading, setMessageLoading] = useState(false);

  const loadSubmissions = useCallback(async () => {
    setLoading(true);
    try {
      const response = await listSubmissions(activeTab === "all" ? undefined : activeTab);
      setItems(response);
    } finally {
      setLoading(false);
    }
  }, [activeTab]);

  useEffect(() => {
    void loadSubmissions();
  }, [loadSubmissions]);

  useEffect(() => {
    if (!selected) return;
    void listMessages(selected.id).then(setMessages).catch(() => setMessages([]));
  }, [selected]);

  const handleSendMessage = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selected || !messageText.trim()) return;

    setMessageLoading(true);
    try {
      await sendMessage(selected.id, messageText.trim());
      setMessageText("");
      const updated = await listMessages(selected.id);
      setMessages(updated);
      toast("ส่งข้อความแล้ว", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "ส่งข้อความไม่สำเร็จ", "error");
    } finally {
      setMessageLoading(false);
    }
  };

  return (
    <div className="page-stack">
      <Tabs activeKey={activeTab} items={submissionTabs} onChange={setActiveTab} />

      {loading ? (
        <div className="page-stack">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="card-skeleton" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <EmptyState icon="📤" title="ยังไม่มี submission" description="เมื่ออาจารย์เริ่มส่งข้อสอบ รายการจะแสดงที่หน้านี้" />
      ) : (
        <div className="page-stack">
          {items.map((item) => (
            <SubmissionCard key={item.id} item={item} onOpenMessages={setSelected} />
          ))}
        </div>
      )}

      <Modal
        open={Boolean(selected)}
        title={selected ? `ข้อความสำหรับ ${selected.course_id ?? ""}` : "ข้อความ"}
        onClose={() => setSelected(null)}
      >
        <div className="message-thread">
          {messages.length === 0 ? (
            <EmptyState icon="💬" title="ยังไม่มีข้อความ" />
          ) : (
            messages.map((message) => (
              <div key={message.id} className="message-thread__item">
                <strong>{message.sender_name ?? "ผู้ใช้"}</strong>
                <p>{message.message}</p>
                <span>{formatDateTime(message.created_at)}</span>
              </div>
            ))
          )}
        </div>

        <form className="message-thread__composer" onSubmit={handleSendMessage}>
          <textarea
            onChange={(event) => setMessageText(event.target.value)}
            placeholder="พิมพ์ข้อความถึง staff หรือ reviewer"
            rows={4}
            value={messageText}
          />
          <Button loading={messageLoading} type="submit">
            ส่งข้อความ
          </Button>
        </form>
      </Modal>
    </div>
  );
}
