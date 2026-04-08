import type { ReactNode } from "react";

import { EmptyState } from "./EmptyState";
import { Skeleton } from "./Skeleton";

interface Column<T> {
  key: string;
  label: string;
  render?: (row: T) => ReactNode;
}

interface DataTableProps<T> {
  columns: Array<Column<T>>;
  rows: T[];
  rowKey: (row: T) => string | number;
  loading?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
}

function getValueByPath(row: Record<string, unknown>, key: string) {
  return key.split(".").reduce<unknown>((value, segment) => {
    if (!value || typeof value !== "object") return undefined;
    return (value as Record<string, unknown>)[segment];
  }, row);
}

export function DataTable<T extends object>({
  columns,
  emptyDescription,
  emptyTitle = "ยังไม่มีข้อมูล",
  loading,
  rowKey,
  rows,
}: DataTableProps<T>) {
  if (loading) {
    return (
      <div className="table-skeleton">
        {Array.from({ length: 5 }).map((_, index) => (
          <Skeleton key={index} className="table-skeleton__row" />
        ))}
      </div>
    );
  }

  if (rows.length === 0) {
    return <EmptyState icon="📄" title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key} scope="col">
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={rowKey(row)}>
              {columns.map((column) => (
                <td key={column.key}>
                  {column.render
                    ? column.render(row)
                    : String(getValueByPath(row as Record<string, unknown>, column.key) ?? "-")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
