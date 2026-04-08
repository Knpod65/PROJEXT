import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { listSettings, updateSetting, type SettingsMap } from "@/services/settings.service";
import { useAsyncData } from "@/hooks/useAsyncData";
import { useUi } from "@/store/ui.store";

export function SettingsPage() {
  const { toast } = useUi();
  const loader = useCallback(() => listSettings(), []);
  const state = useAsyncData(loader, [loader]);
  const [drafts, setDrafts] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!state.data) return;
    const nextDrafts: Record<string, string> = {};
    Object.entries(state.data).forEach(([key, value]) => {
      nextDrafts[key] = value.value ?? "";
    });
    setDrafts(nextDrafts);
  }, [state.data]);

  const handleSave = async (key: string) => {
    try {
      await updateSetting(key, drafts[key] ?? "");
      toast("บันทึกการตั้งค่าแล้ว", "success");
      await state.reload();
    } catch (err) {
      toast(err instanceof Error ? err.message : "บันทึกไม่สำเร็จ", "error");
    }
  };

  const settings = state.data as SettingsMap | null;

  return (
    <div className="page-stack">
      {settings
        ? Object.entries(settings).map(([key, value]) => (
            <Card key={key} title={key} subtitle={value.description}>
              <div className="settings-row">
                <input
                  onChange={(event) => setDrafts((current) => ({ ...current, [key]: event.target.value }))}
                  value={drafts[key] ?? ""}
                />
                <Button type="button" onClick={() => void handleSave(key)}>
                  บันทึก
                </Button>
              </div>
            </Card>
          ))
        : null}
    </div>
  );
}
