import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";

interface RoomVenueOverviewProps {
  title: string;
  subtitle: string;
  metrics: Array<{ label: string; value: string; tone: "blue" | "green" | "gold" | "orange" | "crimson" | "navy" }>;
}

export function RoomVenueOverview({ metrics, subtitle, title }: RoomVenueOverviewProps) {
  return (
    <Card title={title} subtitle={subtitle}>
      <div className="page-stack">
        {metrics.map((metric) => (
          <div key={metric.label} className="signer-list__item">
            <strong>{metric.label}</strong>
            <Badge variant={metric.tone}>{metric.value}</Badge>
          </div>
        ))}
      </div>
    </Card>
  );
}
