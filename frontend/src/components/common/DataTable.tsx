/**
 * Reusable data table component using Blueprint.js.
 */

import { HTMLTable } from "@blueprintjs/core";
import { tableContainer } from "../../styles/common";
import { spacing, colors } from "../../styles/theme";

interface Column<T> {
  key: string;
  label: string;
  render?: (item: T) => React.ReactNode;
  align?: "left" | "right" | "center";
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  emptyMessage?: string;
  keyExtractor: (item: T) => string;
}

export default function DataTable<T>({
  columns,
  data,
  emptyMessage = "No data available",
  keyExtractor,
}: DataTableProps<T>) {
  return (
    <div style={tableContainer}>
      <HTMLTable
        striped
        interactive
        style={{
          width: "100%",
          backgroundColor: "var(--scims-background-primary)",
        }}
      >
        <thead>
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                style={{
                  padding: spacing.md,
                  textAlign: column.align || "left",
                  borderBottom: `2px solid var(--scims-table-border)`,
                  backgroundColor: "var(--scims-table-header-bg)",
                }}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                style={{
                  padding: spacing.xl,
                  textAlign: "center",
                  color: colors.text.secondary,
                }}
              >
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((item) => (
              <tr key={keyExtractor(item)}>
                {columns.map((column) => (
                  <td
                    key={column.key}
                    style={{
                      padding: spacing.md,
                      textAlign: column.align || "left",
                      borderBottom: `1px solid var(--scims-table-border)`,
                    }}
                  >
                    {column.render
                      ? column.render(item)
                      : String(
                          (item as Record<string, unknown>)[column.key] ?? "-"
                        )}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </HTMLTable>
    </div>
  );
}
