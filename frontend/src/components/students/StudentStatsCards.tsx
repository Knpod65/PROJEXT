import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";

interface StudentStatsCardsProps {
  stats: {
    total: number;
    firstEnrollment: number;
    pendingImport: number;
    remainingCapacity: number;
    flagged: number;
    enrolled: number;
  };
}

export function StudentStatsCards({ stats }: StudentStatsCardsProps) {
  return (
    <div className="summary-grid">
      <Card title="Total Students" actions={<Badge variant="blue">{stats.total}</Badge>}>
        <p>Students in the current mock enrollment dataset.</p>
      </Card>
      <Card title="First Enrollment" actions={<Badge variant="gold">{stats.firstEnrollment}</Badge>}>
        <p>Students entering the system for the first time.</p>
      </Card>
      <Card title="Pending Import" actions={<Badge variant="orange">{stats.pendingImport}</Badge>}>
        <p>Mock queue waiting for Excel ingestion review.</p>
      </Card>
      <Card title="Remaining Capacity" actions={<Badge variant="green">{stats.remainingCapacity}</Badge>}>
        <p>Seats available before section capacity is reached.</p>
      </Card>
      <Card title="Flagged Records" actions={<Badge variant="crimson">{stats.flagged}</Badge>}>
        <p>Records requiring manual verification before enrollment.</p>
      </Card>
      <Card title="Enrolled" actions={<Badge variant="navy">{stats.enrolled}</Badge>}>
        <p>Records that already passed the mock enrollment flow.</p>
      </Card>
    </div>
  );
}
