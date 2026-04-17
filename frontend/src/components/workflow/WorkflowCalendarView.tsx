import type { WorkflowCalendarDay } from "@/hooks/useWorkflowData";
import type { WorkflowScheduleSlot } from "@/hooks/useWorkflowData";

interface WorkflowCalendarViewProps {
  days: WorkflowCalendarDay[];
  timeSlots: string[];
  getSlot: (timeSlot: string, dayKey: string) => WorkflowScheduleSlot | undefined;
}

function streamClass(stream: WorkflowScheduleSlot["stream"]) {
  if (stream === "primary") {
    return "ui-badge ui-badge--blue ui-badge--sm";
  }

  if (stream === "secondary") {
    return "ui-badge ui-badge--green ui-badge--sm";
  }

  return "ui-badge ui-badge--navy ui-badge--sm";
}

export function WorkflowCalendarView({ days, getSlot, timeSlots }: WorkflowCalendarViewProps) {
  return (
    <div className="table-wrap" role="region" aria-label="Workflow calendar view">
      <table className="data-table">
        <thead>
          <tr>
            <th scope="col">Time</th>
            {days.map((day) => (
              <th key={day.key} scope="col">
                <div>
                  <strong>{day.label}</strong>
                  <p>{day.dateLabel}</p>
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {timeSlots.map((timeSlot) => (
            <tr key={timeSlot}>
              <td>
                <strong>{timeSlot}</strong>
              </td>
              {days.map((day) => {
                const slot = getSlot(timeSlot, day.key);

                if (!slot) {
                  return <td key={`${timeSlot}-${day.key}`}>-</td>;
                }

                return (
                  <td key={`${timeSlot}-${day.key}`}>
                    <div>
                      <div className={streamClass(slot.stream)}>{slot.courseCode}</div>
                      <p>
                        <strong>{slot.courseTitle}</strong>
                      </p>
                      <p>{slot.location}</p>
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
