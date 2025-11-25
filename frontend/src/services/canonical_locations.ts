/**
 * Canonical Locations service methods.
 */

import { ApiClient } from "./client";
import type {
  CanonicalLocation,
  CanonicalLocationCreate,
  CanonicalLocationUpdate,
  CanonicalLocationsPaginatedResponse,
} from "../types/canonical_location";

export class CanonicalLocationsService extends ApiClient {
  async getCanonicalLocations(
    skip = 0,
    limit = 50,
    type?: string,
    parent_location_id?: string,
    search?: string
  ): Promise<CanonicalLocationsPaginatedResponse> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (type) params.append("type", type);
    if (parent_location_id)
      params.append("parent_location_id", parent_location_id);
    if (search) params.append("search", search);

    const response = await this.client.get<CanonicalLocationsPaginatedResponse>(
      `/canonical-locations?${params}`
    );
    return response.data;
  }

  async getCanonicalLocation(id: string): Promise<CanonicalLocation> {
    const response = await this.client.get<CanonicalLocation>(
      `/canonical-locations/${id}`
    );
    return response.data;
  }

  async createCanonicalLocation(
    data: CanonicalLocationCreate
  ): Promise<CanonicalLocation> {
    const response = await this.client.post<CanonicalLocation>(
      "/canonical-locations",
      data
    );
    return response.data;
  }

  async updateCanonicalLocation(
    id: string,
    data: CanonicalLocationUpdate
  ): Promise<CanonicalLocation> {
    const response = await this.client.patch<CanonicalLocation>(
      `/canonical-locations/${id}`,
      data
    );
    return response.data;
  }

  async deleteCanonicalLocation(id: string): Promise<void> {
    await this.client.delete(`/canonical-locations/${id}`);
  }
}
