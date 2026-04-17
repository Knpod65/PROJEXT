import { useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import type { WorkflowReviewNote } from "@/hooks/useWorkflowData";

interface WorkflowReviewPanelProps {
  notes: WorkflowReviewNote[];
  onReturnForCorrection: () => void;
  onFinalSignoff: () => void;
}

function severityVariant(severity: WorkflowReviewNote["severity"]) {
  return severity === "warning" ? "orange" as const : "blue" as const;
}

export function WorkflowReviewPanel({ notes, onFinalSignoff, onReturnForCorrection }: WorkflowReviewPanelProps) {
  const [signoffPending, setSignoffPending] = useState(false);

  return (
    <div className="grid-split">
      <Card title="ESQ Review and Feedback" subtitle="Read-only preview of feedback and decision controls">
        <div className="page-stack">
          {notes.map((note) => (
            <div key={note.id} className="signer-list__item">
              <div>
                <strong>{note.author}</strong>
                <p>{note.createdAt}</p>
              </div>
              <Badge variant={severityVariant(note.severity)}>{note.severity}</Badge>
              <p>{note.message}</p>
            </div>
          ))}
          <div className="inline-actions">
            <Button type="button" variant="outline" onClick={onReturnForCorrection}>
              Return To Admin
            </Button>
          </div>
        </div>
      </Card>

      <Card title="Final Authorization" subtitle="Sign-off controls are disabled in Milestone 3 read-only mode">
        <div className="page-stack">
          <p>
            Publishing will lock logistics allocations. This stage is intentionally read-only until mutation wiring is
            introduced in a later milestone.
          </p>
          <div className="inline-actions">
            <Button type="button" variant="gold" onClick={() => setSignoffPending(true)}>
              Digitally Sign and Publish
            </Button>
          </div>
        </div>
      </Card>

      <ConfirmDialog
        open={signoffPending}
        title="Digitally sign and publish"
        description="Publishing will lock all logistics allocations and notify all departments. This action cannot be reversed from the UI. Confirm only if all outstanding reviews have been resolved."
        confirmLabel="Sign and publish"
        variant="gold"
        onConfirm={() => { setSignoffPending(false); onFinalSignoff(); }}
        onCancel={() => setSignoffPending(false)}
      />
    </div>
  );
}
