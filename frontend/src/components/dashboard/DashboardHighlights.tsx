import { Icon } from "@/components/ui/Icon";

export interface DashboardHighlightItem {
  icon: string;
  label: string;
  value: string;
  note: string;
}

interface DashboardHighlightsProps {
  items: DashboardHighlightItem[];
}

export function DashboardHighlights({ items }: DashboardHighlightsProps) {
  return (
    <div className="dashboard-highlights">
      {items.map((item) => (
        <div key={item.label} className="dashboard-highlights__item">
          <div className="dashboard-highlights__icon">
            <Icon name={item.icon} />
          </div>
          <div>
            <span className="dashboard-highlights__label">{item.label}</span>
            <strong className="dashboard-highlights__value">{item.value}</strong>
            <p className="dashboard-highlights__note">{item.note}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
