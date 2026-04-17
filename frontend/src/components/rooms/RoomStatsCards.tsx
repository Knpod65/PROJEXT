import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";

interface RoomStatsCardsProps {
  stats: {
    total: number;
    available: number;
    occupied: number;
    maintenance: number;
    reserved: number;
    totalCapacity: number;
  };
  titlePrefix: string;
}

export function RoomStatsCards({ stats, titlePrefix }: RoomStatsCardsProps) {
  return (
    <div className="summary-grid">
      <Card title={`${titlePrefix} Total`} actions={<Badge variant="blue">{stats.total}</Badge>}>
        <p>All mock records in the current room dataset.</p>
      </Card>
      <Card title="Available" actions={<Badge variant="green">{stats.available}</Badge>}>
        <p>Rooms ready for allocation right now.</p>
      </Card>
      <Card title="Occupied" actions={<Badge variant="gold">{stats.occupied}</Badge>}>
        <p>Rooms currently tied to a planned session.</p>
      </Card>
      <Card title="Maintenance" actions={<Badge variant="crimson">{stats.maintenance}</Badge>}>
        <p>Rooms temporarily unavailable for allocation.</p>
      </Card>
      <Card title="Reserved" actions={<Badge variant="orange">{stats.reserved}</Badge>}>
        <p>Rooms held for special handling or approvals.</p>
      </Card>
      <Card title="Capacity" actions={<Badge variant="navy">{stats.totalCapacity}</Badge>}>
        <p>Total seating capacity across the visible mock rooms.</p>
      </Card>
    </div>
  );
}
