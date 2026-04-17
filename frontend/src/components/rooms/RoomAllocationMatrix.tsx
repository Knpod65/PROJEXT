interface AllocationCell {
  slot: string;
  roomName: string;
  label: string;
  tone: string;
}

interface AllocationRow {
  day: string;
  cells: AllocationCell[];
}

interface RoomAllocationMatrixProps {
  rows: AllocationRow[];
  title: string;
  subtitle: string;
}

function toneClass(tone: string) {
  if (tone === "available") {
    return "ui-badge ui-badge--green ui-badge--sm";
  }

  if (tone === "maintenance") {
    return "ui-badge ui-badge--crimson ui-badge--sm";
  }

  if (tone === "reserved") {
    return "ui-badge ui-badge--orange ui-badge--sm";
  }

  return "ui-badge ui-badge--gold ui-badge--sm";
}

export function RoomAllocationMatrix({ rows, subtitle, title }: RoomAllocationMatrixProps) {
  const slots = rows[0]?.cells.map((cell) => cell.slot) ?? [];

  return (
    <section className="schedule-board">
      <header className="schedule-board__header">
        <div>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
        <span>Mock matrix</span>
      </header>

      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th scope="col">Day</th>
              {slots.map((slot) => (
                <th key={slot} scope="col">{slot}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.day}>
                <td>
                  <strong>{row.day}</strong>
                </td>
                {row.cells.map((cell) => (
                  <td key={`${row.day}-${cell.slot}`}>
                    <div>
                      <div className={toneClass(cell.tone)}>{cell.roomName}</div>
                      <p>
                        <strong>{cell.label}</strong>
                      </p>
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
