import { cx } from "@/utils/cx";

export interface TabItem {
  key: string;
  label: string;
  badge?: string | number;
}

interface TabsProps {
  activeKey: string;
  items: TabItem[];
  onChange: (key: string) => void;
}

export function Tabs({ activeKey, items, onChange }: TabsProps) {
  return (
    <div className="tabs" role="tablist">
      {items.map((item) => (
        <button
          key={item.key}
          className={cx("tabs__item", item.key === activeKey && "tabs__item--active")}
          onClick={() => onChange(item.key)}
          role="tab"
          type="button"
        >
          <span>{item.label}</span>
          {item.badge !== undefined ? <span className="tabs__badge">{item.badge}</span> : null}
        </button>
      ))}
    </div>
  );
}
