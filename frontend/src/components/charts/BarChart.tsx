import { formatNumber } from "@/utils/format";

interface BarChartProps {
  labels: string[];
  values: number[];
  color?: string;
}

export function BarChart({ color = "var(--crimson)", labels, values }: BarChartProps) {
  const max = Math.max(...values, 1);

  if (labels.length === 0) {
    return <div className="chart-empty">ยังไม่มีข้อมูล</div>;
  }

  return (
    <div className="bar-chart">
      {labels.map((label, index) => (
        <div key={label} className="bar-chart__row">
          <div className="bar-chart__label">{label}</div>
          <div className="bar-chart__track">
            <div
              className="bar-chart__fill"
              style={{ width: `${((values[index] ?? 0) / max) * 100}%`, background: color }}
            />
          </div>
          <div className="bar-chart__value">{formatNumber(values[index] ?? 0)}</div>
        </div>
      ))}
    </div>
  );
}
