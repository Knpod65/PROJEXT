import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";

interface WorkflowStatusCardsProps {
  stats: {
    total: number;
    pending: number;
    returned: number;
    ready: number;
    highRisk: number;
  };
}

export function WorkflowStatusCards({ stats }: WorkflowStatusCardsProps) {
  return (
    <div className="summary-grid">
      <Card title="Approval Batches" actions={<Badge variant="blue">{stats.total}</Badge>}>
        <p>Total schedule batches in this review cycle.</p>
      </Card>
      <Card title="Pending" actions={<Badge variant="gold">{stats.pending}</Badge>}>
        <p>Awaiting executive decision in this read-only preview.</p>
      </Card>
      <Card title="Returned" actions={<Badge variant="crimson">{stats.returned}</Badge>}>
        <p>Requires correction before final sign-off.</p>
      </Card>
      <Card title="Ready" actions={<Badge variant="green">{stats.ready}</Badge>}>
        <p>Fully validated and ready to publish.</p>
      </Card>
      <Card title="High Risk" actions={<Badge variant="orange">{stats.highRisk}</Badge>}>
        <p>Needs focused oversight due to conflict or capacity risk.</p>
      </Card>
    </div>
  );
}
