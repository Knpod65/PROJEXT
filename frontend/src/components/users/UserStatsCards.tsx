import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import type { UserStats } from "@/hooks/useUsersData";

interface UserStatsCardsProps {
  stats: UserStats;
}

export function UserStatsCards({ stats }: UserStatsCardsProps) {
  return (
    <div className="summary-grid">
      <Card title="Total Users" actions={<Badge variant="blue">{stats.total}</Badge>}>
        <p>Registered accounts across all roles.</p>
      </Card>
      <Card title="Active Users" actions={<Badge variant="green">{stats.active}</Badge>}>
        <p>Accounts currently enabled for sign-in.</p>
      </Card>
      <Card title="Inactive Users" actions={<Badge variant="gray">{stats.inactive}</Badge>}>
        <p>Accounts that were deactivated from operations.</p>
      </Card>
      <Card title="Active Faculty" actions={<Badge variant="gold">{stats.teachers}</Badge>}>
        <p>Teacher-role accounts available this cycle.</p>
      </Card>
      <Card title="Admin Seats" actions={<Badge variant="navy">{stats.admins}</Badge>}>
        <p>Administrative operators with elevated access.</p>
      </Card>
      <Card title="Review Queue" actions={<Badge variant="orange">{stats.pendingApprovals}</Badge>}>
        <p>Preview placeholder for registration approval workflow.</p>
      </Card>
    </div>
  );
}
