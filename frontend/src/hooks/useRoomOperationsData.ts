import { useCallback, useEffect, useState } from "react";

import { getCheckinsForSchedule } from "@/services/checkin.service";
import { listSchedules } from "@/services/schedule.service";
import type { CheckinEventItem, ScheduleWithSection } from "@/types/api";

interface RoomOperationsState {
  schedules: ScheduleWithSection[];
  events: Record<string, CheckinEventItem[]>;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useRoomOperationsData(selectedDate: string): RoomOperationsState {
  const [schedules, setSchedules] = useState<ScheduleWithSection[]>([]);
  const [events, setEvents] = useState<Record<string, CheckinEventItem[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const loadedSchedules = await listSchedules({ date: selectedDate });
      const pairs = await Promise.all(
        loadedSchedules.map(async (item) => {
          const scheduleEvents = await getCheckinsForSchedule(item.id);
          const sortedEvents = [...scheduleEvents].sort((left, right) => {
            const leftTime = left.checked_in_at ? Date.parse(left.checked_in_at) : 0;
            const rightTime = right.checked_in_at ? Date.parse(right.checked_in_at) : 0;
            return rightTime - leftTime;
          });

          return [String(item.id), sortedEvents] as const;
        }),
      );

      setSchedules(loadedSchedules);
      setEvents(Object.fromEntries(pairs) as Record<string, CheckinEventItem[]>);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load room operations.");
    } finally {
      setLoading(false);
    }
  }, [selectedDate]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { schedules, events, loading, error, refresh };
}
