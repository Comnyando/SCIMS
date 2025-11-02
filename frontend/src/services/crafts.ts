/**
 * Crafts service methods.
 */

import { ApiClient } from "./client";
import type {
  Craft,
  CraftCreate,
  CraftUpdate,
  CraftProgress,
} from "../types/craft";
import type { PaginatedResponse } from "../types/common";

export class CraftsService extends ApiClient {
  async getCrafts(
    skip = 0,
    limit = 50,
    status_filter?: string,
    organization_id?: string,
    blueprint_id?: string,
    sort_by?: string,
    sort_order?: "asc" | "desc"
  ): Promise<PaginatedResponse<Craft>> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (status_filter) params.append("status_filter", status_filter);
    if (organization_id) params.append("organization_id", organization_id);
    if (blueprint_id) params.append("blueprint_id", blueprint_id);
    if (sort_by) params.append("sort_by", sort_by);
    if (sort_order) params.append("sort_order", sort_order);

    const response = await this.client.get<{
      crafts: Craft[];
      total: number;
      skip: number;
      limit: number;
      pages: number;
    }>(`/crafts?${params}`);
    // Transform response to match PaginatedResponse format
    return {
      items: response.data.crafts,
      total: response.data.total,
      skip: response.data.skip,
      limit: response.data.limit,
    };
  }

  async getCraft(id: string, include_ingredients = false): Promise<Craft> {
    const params = new URLSearchParams();
    if (include_ingredients) params.append("include_ingredients", "true");

    const url = `/crafts/${id}${params.toString() ? `?${params}` : ""}`;
    const response = await this.client.get<Craft>(url);
    return response.data;
  }

  async createCraft(
    data: CraftCreate,
    reserve_ingredients = false
  ): Promise<Craft> {
    const params = new URLSearchParams();
    if (reserve_ingredients) params.append("reserve_ingredients", "true");

    const url = `/crafts${params.toString() ? `?${params}` : ""}`;
    const response = await this.client.post<Craft>(url, data);
    return response.data;
  }

  async updateCraft(id: string, data: CraftUpdate): Promise<Craft> {
    const response = await this.client.patch<Craft>(`/crafts/${id}`, data);
    return response.data;
  }

  async deleteCraft(id: string, unreserve_ingredients = false): Promise<void> {
    const params = new URLSearchParams();
    if (unreserve_ingredients) params.append("unreserve_ingredients", "true");

    const url = `/crafts/${id}${params.toString() ? `?${params}` : ""}`;
    await this.client.delete(url);
  }

  async startCraft(
    id: string,
    reserve_missing_ingredients = false
  ): Promise<Craft> {
    const params = new URLSearchParams();
    if (reserve_missing_ingredients)
      params.append("reserve_missing_ingredients", "true");

    const url = `/crafts/${id}/start${params.toString() ? `?${params}` : ""}`;
    const response = await this.client.post<Craft>(url);
    return response.data;
  }

  async completeCraft(id: string): Promise<Craft> {
    const response = await this.client.post<Craft>(`/crafts/${id}/complete`);
    return response.data;
  }

  async getCraftProgress(id: string): Promise<CraftProgress> {
    const response = await this.client.get<CraftProgress>(
      `/crafts/${id}/progress`
    );
    return response.data;
  }
}
