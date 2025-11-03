/**
 * Import/Export service methods.
 */

import { ApiClient } from "./client";
import type {
  ImportResponse,
  ExportType,
  ExportFormat,
} from "../types/import_export";

export class ImportExportService extends ApiClient {
  /**
   * Export data to CSV or JSON format.
   */
  async exportData(
    type: ExportType,
    format: ExportFormat,
    filters?: {
      category?: string;
      location_id?: string;
      item_id?: string;
      is_public?: boolean;
    }
  ): Promise<Blob> {
    const params = new URLSearchParams();
    if (filters?.category) params.append("category", filters.category);
    if (filters?.location_id) params.append("location_id", filters.location_id);
    if (filters?.item_id) params.append("item_id", filters.item_id);
    if (filters?.is_public !== undefined)
      params.append("is_public", filters.is_public.toString());

    const queryString = params.toString();
    const url = `/import-export/${type}.${format}${
      queryString ? `?${queryString}` : ""
    }`;

    const response = await this.client.get(url, {
      responseType: "blob",
    });

    return response.data;
  }

  /**
   * Import data from CSV or JSON file.
   */
  async importData(type: ExportType, file: File): Promise<ImportResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await this.client.post<ImportResponse>(
      `/import-export/${type}/import`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.data;
  }
}
