/**
 * Import/Export related types.
 */

export interface ImportResponse {
  success: boolean;
  imported_count: number;
  failed_count: number;
  errors: Array<{
    row_number: number;
    field: string | null;
    message: string;
  }>;
}

export type ExportType = "items" | "inventory" | "blueprints";
export type ExportFormat = "csv" | "json";
