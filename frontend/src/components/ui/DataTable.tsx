import type { ReactNode } from "react";

import { useI18n } from "@/i18n";
import { cx } from "@/utils/cx";

import { EmptyState } from "./EmptyState";
import { Icon } from "./Icon";
import { Skeleton } from "./Skeleton";

export interface DataTableColumn<T> {
  key: string;
  label: string;
  render?: (row: T) => ReactNode;
  align?: "left" | "center" | "right";
  width?: string;
  minWidth?: string;
  headerClassName?: string;
  cellClassName?: string;
}

interface DataTableProps<T> {
  columns: Array<DataTableColumn<T>>;
  rows: T[];
  rowKey: (row: T) => string | number;
  loading?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
  className?: string;
  tableClassName?: string;
  compact?: boolean;
  stickyHeader?: boolean;
  maxHeight?: number | string;
  scrollThreshold?: number;
  tableLayout?: "auto" | "fixed";
  rowClassName?: (row: T) => string | undefined;
}

function getValueByPath(row: Record<string, unknown>, key: string) {
  return key.split(".").reduce<unknown>((value, segment) => {
    if (!value || typeof value !== "object") return undefined;
    return (value as Record<string, unknown>)[segment];
  }, row);
}

function getColumnStyle<T>(column: DataTableColumn<T>) {
  return {
    width: column.width,
    minWidth: column.minWidth,
  };
}

export function DataTable<T extends object>({
  className,
  columns,
  compact = false,
  emptyDescription,
  emptyTitle,
  loading,
  maxHeight,
  rowClassName,
  rowKey,
  rows,
  scrollThreshold,
  stickyHeader = true,
  tableClassName,
  tableLayout = "auto",
}: DataTableProps<T>) {
  const { t } = useI18n();

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
    return (
      <EmptyState
        icon={<Icon name="table_rows" />}
        title={emptyTitle ?? t("common.noData")}
        description={emptyDescription}
      />
    );
  }

  const shouldEnableScroll =
    typeof scrollThreshold === "number" ? rows.length > scrollThreshold : typeof maxHeight !== "undefined";

  const wrapperStyle = shouldEnableScroll && maxHeight
    ? {
        maxHeight: typeof maxHeight === "number" ? `${maxHeight}px` : maxHeight,
      }
    : undefined;

  return (
    <div
      className={cx(
        "table-wrap",
        shouldEnableScroll && "table-wrap--scrollable",
        stickyHeader && shouldEnableScroll && "table-wrap--sticky",
        className,
      )}
      style={wrapperStyle}
    >
      <table
        className={cx(
          "data-table",
          compact && "data-table--compact",
          tableLayout === "fixed" && "data-table--fixed",
          tableClassName,
        )}
      >
        <colgroup>
          {columns.map((column) => (
            <col key={column.key} style={getColumnStyle(column)} />
          ))}
        </colgroup>
        <thead>
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                scope="col"
                className={cx(
                  `data-table__cell--${column.align ?? "left"}`,
                  column.headerClassName,
                )}
                style={getColumnStyle(column)}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={rowKey(row)} className={rowClassName?.(row)}>
              {columns.map((column) => (
                <td
                  key={column.key}
                  className={cx(
                    `data-table__cell--${column.align ?? "left"}`,
                    column.cellClassName,
                  )}
                  style={getColumnStyle(column)}
                >
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
