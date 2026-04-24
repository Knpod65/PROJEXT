import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Skeleton } from "@/components/ui/Skeleton";
import {
  addUnavailability,
  deleteUnavailability,
  getStaffAvailabilityStaff,
  getUnavailability,
  type StaffAvailabilityMember,
  type UnavailabilityRecord,
} from "@/services/optimizer.service";
import { useUi } from "@/store/ui.store";

type SlotDefinition = {
  start: string;
  end: string;
  label: string;
};

function toMinutes(value: string) {
  const [hours, minutes] = value.split(":").map(Number);
  return (hours * 60) + minutes;
}

function formatTime(minutes: number) {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${String(hours).padStart(2, "0")}:${String(mins).padStart(2, "0")}`;
}

function buildSlots(): SlotDefinition[] {
  const slots: SlotDefinition[] = [];
  for (let minutes = 8 * 60; minutes < 19 * 60; minutes += 30) {
    const start = formatTime(minutes);
    const end = formatTime(minutes + 30);
    slots.push({ start, end, label: `${start}-${end}` });
  }
  return slots;
}

const STAFF_SLOTS = buildSlots();

function getRangeBounds(row: UnavailabilityRecord) {
  if (row.all_day) {
    return null;
  }
  const start = row.start_time ?? row.block_time?.split("-")[0] ?? null;
  const end = row.end_time ?? row.block_time?.split("-")[1] ?? null;
  if (!start || !end) {
    return null;
  }
  return { start, end };
}

function slotCoveredByRow(slot: SlotDefinition, row: UnavailabilityRecord) {
  if (row.all_day) {
    return true;
  }
  const bounds = getRangeBounds(row);
  if (!bounds) {
    return false;
  }
  return toMinutes(slot.start) < toMinutes(bounds.end) && toMinutes(slot.end) > toMinutes(bounds.start);
}

function compressSlotStarts(slotStarts: string[]) {
  const sorted = [...slotStarts].sort();
  const intervals: Array<{ start_time: string; end_time: string; block_time: string }> = [];
  let rangeStart: string | null = null;
  let previousStart: string | null = null;

  for (const start of sorted) {
    if (!rangeStart) {
      rangeStart = start;
      previousStart = start;
      continue;
    }

    if (toMinutes(start) === toMinutes(previousStart ?? start) + 30) {
      previousStart = start;
      continue;
    }

    const previousSlot = STAFF_SLOTS.find((slot) => slot.start === previousStart);
    if (previousSlot) {
      intervals.push({
        start_time: rangeStart,
        end_time: previousSlot.end,
        block_time: `${rangeStart}-${previousSlot.end}`,
      });
    }
    rangeStart = start;
    previousStart = start;
  }

  if (rangeStart && previousStart) {
    const previousSlot = STAFF_SLOTS.find((slot) => slot.start === previousStart);
    if (previousSlot) {
      intervals.push({
        start_time: rangeStart,
        end_time: previousSlot.end,
        block_time: `${rangeStart}-${previousSlot.end}`,
      });
    }
  }

  return intervals;
}

function AvailabilityStatusBadge({ blocked }: { blocked: boolean }) {
  return (
    <span className={`room-badge ${blocked ? "room-badge--inactive" : "room-badge--active"}`}>
      {blocked ? "Has blocks" : "Available"}
    </span>
  );
}

export function StaffAvailabilityPage() {
  const { toast } = useUi();
  const [staff, setStaff] = useState<StaffAvailabilityMember[]>([]);
  const [blocks, setBlocks] = useState<UnavailabilityRecord[]>([]);
  const [staffLoading, setStaffLoading] = useState(true);
  const [blocksLoading, setBlocksLoading] = useState(true);
  const [selectedStaffId, setSelectedStaffId] = useState<number | null>(null);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().slice(0, 10));
  const [selectedSlots, setSelectedSlots] = useState<string[]>([]);
  const [draftAllDay, setDraftAllDay] = useState(false);
  const [saving, setSaving] = useState(false);
  const [query, setQuery] = useState("");
  const [unitFilter, setUnitFilter] = useState("");
  const [availabilityFilter, setAvailabilityFilter] = useState<"all" | "available" | "blocked">("all");

  const loadStaff = useCallback(async () => {
    setStaffLoading(true);
    try {
      const data = await getStaffAvailabilityStaff();
      setStaff(data.rows);
    } catch {
      setStaff([]);
    } finally {
      setStaffLoading(false);
    }
  }, []);

  const loadBlocks = useCallback(async () => {
    setBlocksLoading(true);
    try {
      const data = await getUnavailability();
      setBlocks(data);
    } catch {
      setBlocks([]);
    } finally {
      setBlocksLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadStaff();
    void loadBlocks();
  }, [loadBlocks, loadStaff]);

  const selectedStaff = useMemo(
    () => staff.find((member) => member.id === selectedStaffId) ?? null,
    [staff, selectedStaffId],
  );

  const unitOptions = useMemo(
    () =>
      [...new Set(staff.map((member) => member.unit || member.division || "").filter(Boolean))]
        .sort((a, b) => a.localeCompare(b)),
    [staff],
  );

  const filteredStaff = useMemo(() => {
    return staff.filter((member) => {
      const haystack = [
        member.full_name,
        member.username,
        member.division,
        member.unit,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      const matchesQuery = query.trim().length === 0 || haystack.includes(query.trim().toLowerCase());
      const matchesUnit = unitFilter === "" || (member.unit || member.division || "") === unitFilter;
      const hasBlocks = member.availability_block_count > 0;
      const matchesAvailability =
        availabilityFilter === "all"
          || (availabilityFilter === "available" && !hasBlocks)
          || (availabilityFilter === "blocked" && hasBlocks);
      return matchesQuery && matchesUnit && matchesAvailability;
    });
  }, [availabilityFilter, query, staff, unitFilter]);

  useEffect(() => {
    if (!selectedStaffId && filteredStaff.length > 0) {
      setSelectedStaffId(filteredStaff[0].id);
    }
    if (selectedStaffId && filteredStaff.every((member) => member.id !== selectedStaffId)) {
      setSelectedStaffId(filteredStaff[0]?.id ?? null);
    }
  }, [filteredStaff, selectedStaffId]);

  const blocksForSelectedStaff = useMemo(() => {
    if (!selectedStaffId) {
      return [];
    }
    return blocks.filter((row) => row.user_id === selectedStaffId);
  }, [blocks, selectedStaffId]);

  const blocksForSelectedDate = useMemo(() => {
    return blocksForSelectedStaff.filter((row) => row.block_date === selectedDate);
  }, [blocksForSelectedStaff, selectedDate]);

  const toggleSlot = (slotStart: string) => {
    setSelectedSlots((current) =>
      current.includes(slotStart)
        ? current.filter((value) => value !== slotStart)
        : [...current, slotStart],
    );
  };

  const handleSaveBlocks = async () => {
    if (!selectedStaffId) {
      return;
    }
    setSaving(true);
    try {
      if (draftAllDay) {
        await addUnavailability({
          user_id: selectedStaffId,
          block_date: selectedDate,
        });
      } else {
        const intervals = compressSlotStarts(selectedSlots);
        for (const interval of intervals) {
          await addUnavailability({
            user_id: selectedStaffId,
            block_date: selectedDate,
            block_time: interval.block_time,
            start_time: interval.start_time,
            end_time: interval.end_time,
          });
        }
      }
      setSelectedSlots([]);
      setDraftAllDay(false);
      toast("Staff availability updated.", "success");
      await Promise.all([loadBlocks(), loadStaff()]);
    } catch (error) {
      toast(error instanceof Error ? error.message : "Could not save availability.", "error");
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteBlock = async (id: number) => {
    try {
      await deleteUnavailability(id);
      toast("Block removed.", "warning");
      await Promise.all([loadBlocks(), loadStaff()]);
    } catch (error) {
      toast(error instanceof Error ? error.message : "Could not remove block.", "error");
    }
  };

  return (
    <div className="page-stack">
      <Card
        title="Staff availability"
        subtitle="Mark operational availability for invigilation, paper distribution, and external exams."
      >
        <div className="filter-row">
          <label className="filter-field">
            <span>Search staff</span>
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search name or username" />
          </label>
          <label className="filter-field">
            <span>Unit</span>
            <select value={unitFilter} onChange={(event) => setUnitFilter(event.target.value)}>
              <option value="">All units</option>
              {unitOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <label className="filter-field">
            <span>Availability</span>
            <select value={availabilityFilter} onChange={(event) => setAvailabilityFilter(event.target.value as "all" | "available" | "blocked")}>
              <option value="all">All</option>
              <option value="available">Available</option>
              <option value="blocked">Has blocks</option>
            </select>
          </label>
        </div>

        {staffLoading ? (
          <div className="page-stack">
            {[0, 1, 2].map((i) => <Skeleton key={i} className="dashboard-skeleton" />)}
          </div>
        ) : filteredStaff.length === 0 ? (
          <EmptyState
            icon={<Icon name="groups" />}
            title="No staff found"
            description="Adjust the search or filters to find the staff member you want to manage."
          />
        ) : (
          <div className="table-wrap table-wrap--scrollable" style={{ maxHeight: "380px" }}>
            <table className="data-table data-table--compact data-table--fixed">
              <colgroup>
                <col style={{ width: "28%" }} />
                <col style={{ width: "18%" }} />
                <col style={{ width: "14%" }} />
                <col style={{ width: "14%" }} />
                <col style={{ width: "12%" }} />
                <col style={{ width: "14%" }} />
              </colgroup>
              <thead>
                <tr>
                  <th>Staff</th>
                  <th>Unit</th>
                  <th>Status</th>
                  <th>Duty load</th>
                  <th>Paper distribution</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredStaff.map((member) => {
                  const selected = member.id === selectedStaffId;
                  return (
                    <tr key={member.id} className={selected ? "row-selected" : ""}>
                      <td>
                        <div className="data-table__content data-table__content--clamp">
                          <strong>{member.full_name ?? member.username}</strong>
                          <p>{member.username}</p>
                          {member.excluded_reason ? <p>{member.excluded_reason}</p> : null}
                        </div>
                      </td>
                      <td className="text-muted">{member.unit ?? member.division ?? "-"}</td>
                      <td><AvailabilityStatusBadge blocked={member.availability_block_count > 0} /></td>
                      <td>
                        <div className="data-table__content data-table__content--clamp">
                          <strong>{member.total_workload}</strong>
                          <p>Invigilation {member.invigilation_count}</p>
                          <p>External {member.external_exam_count}</p>
                        </div>
                      </td>
                      <td>
                        <div className="data-table__content data-table__content--clamp">
                          <strong>{member.paper_distribution_count}</strong>
                          <p>{member.is_paper_distribution_candidate ? "Eligible pool" : "Not eligible"}</p>
                        </div>
                      </td>
                      <td>
                        <Button type="button" size="sm" variant={selected ? "primary" : "outline"} onClick={() => setSelectedStaffId(member.id)}>
                          {selected ? "Selected" : "Select"}
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <Card
        title={selectedStaff ? `Availability calendar — ${selectedStaff.full_name ?? selectedStaff.username}` : "Availability calendar"}
        subtitle="08:00–19:00 in 30-minute intervals. Saved blocks affect invigilation, paper distribution, and external-exam assignment."
      >
        {!selectedStaff ? (
          <EmptyState
            icon={<Icon name="calendar_month" />}
            title="Select a staff member"
            description="Choose a staff member from the table above to edit operational availability."
          />
        ) : (
          <div className="room-availability-layout">
            <div className="room-availability-editor">
              <div className="filter-row">
                <label className="filter-field">
                  <span>Date</span>
                  <input type="date" value={selectedDate} onChange={(event) => setSelectedDate(event.target.value)} />
                </label>
                <div className="inline-actions">
                  <Button
                    type="button"
                    variant={draftAllDay ? "primary" : "outline"}
                    onClick={() => setDraftAllDay((value) => !value)}
                  >
                    {draftAllDay ? "All-day block selected" : "Mark all day unavailable"}
                  </Button>
                  <Button
                    type="button"
                    disabled={saving || (!draftAllDay && selectedSlots.length === 0)}
                    loading={saving}
                    onClick={() => void handleSaveBlocks()}
                  >
                    Save block
                  </Button>
                </div>
              </div>

              {draftAllDay ? (
                <div className="room-availability-sidebar__summary">
                  <strong>All-day block ready</strong>
                  <span>This will block the selected staff member for the whole date.</span>
                </div>
              ) : (
                <div className="room-slot-grid">
                  {STAFF_SLOTS.map((slot) => {
                    const covered = blocksForSelectedDate.some((row) => slotCoveredByRow(slot, row));
                    const selected = selectedSlots.includes(slot.start);
                    return (
                      <button
                        key={slot.label}
                        type="button"
                        className={`room-slot${covered ? " room-slot--blocked" : ""}${selected ? " room-slot--selected" : ""}`}
                        disabled={covered || saving}
                        onClick={() => toggleSlot(slot.start)}
                      >
                        <strong>{slot.label}</strong>
                        <span>{covered ? "Blocked" : selected ? "Selected" : "Available"}</span>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            <aside className="room-availability-sidebar">
              <div className="room-availability-sidebar__summary">
                <strong>{selectedStaff.full_name ?? selectedStaff.username}</strong>
                <span>{selectedStaff.unit ?? selectedStaff.division ?? "No unit specified"}</span>
                <span>Total workload: {selectedStaff.total_workload}</span>
                <span>Paper distribution: {selectedStaff.paper_distribution_count}</span>
              </div>

              <div className="room-block-list">
                <div className="optimizer-section__header">
                  <div>
                    <h3>Saved blocks</h3>
                    <p className="text-muted">Current period blocks for this staff member.</p>
                  </div>
                </div>

                {blocksLoading ? (
                  <Skeleton className="dashboard-skeleton" />
                ) : blocksForSelectedStaff.length === 0 ? (
                  <p className="text-muted">No availability blocks saved yet.</p>
                ) : (
                  <div className="page-stack">
                    {blocksForSelectedStaff.map((block) => (
                      <div key={block.id} className="room-block-list__item">
                        <div>
                          <strong>{block.block_date}</strong>
                          <p>{block.all_day ? "All day" : block.block_time}</p>
                          {block.reason ? <p>{block.reason}</p> : null}
                        </div>
                        <Button type="button" size="sm" variant="ghost" onClick={() => void handleDeleteBlock(block.id)}>
                          Remove
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </aside>
          </div>
        )}
      </Card>
    </div>
  );
}
