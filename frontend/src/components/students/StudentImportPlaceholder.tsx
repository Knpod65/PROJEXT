import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

interface StudentImportPlaceholderProps {
  onImportClick: () => void;
}

export function StudentImportPlaceholder({ onImportClick }: StudentImportPlaceholderProps) {
  return (
    <Card title="Import Students from Excel" subtitle="UI placeholder only for Milestone 5">
      <div className="page-stack">
        <p>
          Drag-and-drop area and parsing pipeline are intentionally mocked in this milestone.
          Real file parsing and backend import integration are not implemented yet.
        </p>
        <div className="inline-actions">
          <Button type="button" onClick={onImportClick}>Choose Excel File</Button>
          <Button type="button" variant="outline" onClick={onImportClick}>Download Template</Button>
        </div>
      </div>
    </Card>
  );
}
