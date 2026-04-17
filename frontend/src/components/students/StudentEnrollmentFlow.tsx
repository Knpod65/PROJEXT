import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";

interface StudentEnrollmentFlowProps {
  flow: {
    received: number;
    verified: number;
    enrolled: number;
    flagged: number;
  };
}

export function StudentEnrollmentFlow({ flow }: StudentEnrollmentFlowProps) {
  return (
    <Card title="Enrollment Flow" subtitle="Mock pipeline status for first-enrollment operations">
      <div className="page-stack">
        <div className="signer-list__item">
          <strong>1. Intake Received</strong>
          <Badge variant="blue">{flow.received}</Badge>
        </div>
        <div className="signer-list__item">
          <strong>2. Identity Verified</strong>
          <Badge variant="gold">{flow.verified}</Badge>
        </div>
        <div className="signer-list__item">
          <strong>3. Enrolled to Section</strong>
          <Badge variant="green">{flow.enrolled}</Badge>
        </div>
        <div className="signer-list__item">
          <strong>4. Flagged for Review</strong>
          <Badge variant="crimson">{flow.flagged}</Badge>
        </div>
      </div>
    </Card>
  );
}
