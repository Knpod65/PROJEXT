import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";

interface PagePlaceholderProps {
  title: string;
  description: string;
}

export function PagePlaceholder({ description, title }: PagePlaceholderProps) {
  return (
    <Card title={title}>
      <EmptyState
        icon="🛠️"
        title="หน้ากำลังประกอบต่อ"
        description={description}
      />
    </Card>
  );
}
