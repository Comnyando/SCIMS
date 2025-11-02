/**
 * Blueprints service methods.
 */

import { ApiClient } from "./client";
import type {
  Blueprint,
  BlueprintCreate,
  BlueprintUpdate,
} from "../types/blueprint";
import type { PaginatedResponse } from "../types/common";

export class BlueprintsService extends ApiClient {
  async getBlueprints(
    skip = 0,
    limit = 50,
    search?: string,
    category?: string,
    output_item_id?: string,
    is_public?: boolean,
    created_by?: string,
    sort_by?: string,
    sort_order?: "asc" | "desc"
  ): Promise<PaginatedResponse<Blueprint>> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (search) params.append("search", search);
    if (category) params.append("category", category);
    if (output_item_id) params.append("output_item_id", output_item_id);
    if (is_public !== undefined)
      params.append("is_public", is_public.toString());
    if (created_by) params.append("created_by", created_by);
    if (sort_by) params.append("sort_by", sort_by);
    if (sort_order) params.append("sort_order", sort_order);

    const response = await this.client.get<PaginatedResponse<Blueprint>>(
      `/blueprints?${params}`
    );
    return response.data;
  }

  async getBlueprint(id: string): Promise<Blueprint> {
    const response = await this.client.get<Blueprint>(`/blueprints/${id}`);
    return response.data;
  }

  async createBlueprint(data: BlueprintCreate): Promise<Blueprint> {
    const response = await this.client.post<Blueprint>("/blueprints", data);
    return response.data;
  }

  async updateBlueprint(id: string, data: BlueprintUpdate): Promise<Blueprint> {
    const response = await this.client.patch<Blueprint>(
      `/blueprints/${id}`,
      data
    );
    return response.data;
  }

  async deleteBlueprint(id: string): Promise<void> {
    await this.client.delete(`/blueprints/${id}`);
  }

  async getPopularBlueprints(
    limit = 10,
    category?: string
  ): Promise<{ blueprints: Blueprint[]; total: number }> {
    const params = new URLSearchParams({
      limit: limit.toString(),
    });
    if (category) params.append("category", category);

    const response = await this.client.get<{
      blueprints: Blueprint[];
      total: number;
    }>(`/blueprints/popular?${params}`);
    return response.data;
  }

  async getBlueprintsByItem(
    item_id: string,
    skip = 0,
    limit = 50,
    is_public?: boolean
  ): Promise<PaginatedResponse<Blueprint>> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (is_public !== undefined)
      params.append("is_public", is_public.toString());

    const response = await this.client.get<PaginatedResponse<Blueprint>>(
      `/blueprints/by-item/${item_id}?${params}`
    );
    return response.data;
  }
}
