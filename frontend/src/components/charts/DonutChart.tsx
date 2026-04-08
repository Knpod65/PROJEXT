import { formatNumber } from "@/utils/format";

interface DonutChartProps {
  labels: string[];
  values: number[];
  colors: string[];
  centerLabel?: string;
}

export function DonutChart({ centerLabel, colors, labels, values }: DonutChartProps) {
  const total = values.reduce((sum, value) => sum + value, 0);

  if (total === 0) {
    return <div className="chart-empty">ยังไม่มีข้อมูล</div>;
  }

  let cursor = 0;
  const segments = values
    .map((value, index) => {
      const start = cursor;
      const end = cursor + (value / total) * 100;
      cursor = end;
      return `${colors[index] ?? "#d1d5db"} ${start}% ${end}%`;
    })
    .join(", ");

  return (
    <div className="donut-chart">
      <div className="donut-chart__visual" style={{ background: `conic-gradient(${segments})` }}>
        <div className="donut-chart__center">
          <strong>{formatNumber(total)}</strong>
          {centerLabel ? <span>{centerLabel}</span> : null}
        </div>
      </div>
      <div className="donut-chart__legend">
        {labels.map((label, index) => (
          <div key={label} className="donut-chart__legend-item">
            <span className="donut-chart__dot" style={{ background: colors[index] ?? "#d1d5db" }} />
            <span>{label}</span>
            <strong>{formatNumber(values[index] ?? 0)}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}
