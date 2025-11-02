/**
 * Locations service methods.
 */

import { ApiClient } from "./client";
import type { Location, LocationCreate, LocationUpdate, LocationsPaginatedResponse } from "../types/location";

export class LocationsService extends ApiClient {
  async getLocations(
    skip = 0,
    limit = 50,
    type?: string,
    owner_type?: string,
    search?: string
  ): Promise<LocationsPaginatedResponse> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (type) params.append("type", type);
    if (owner_type) params.append("owner_type", owner_type);
    if (search) params.append("search", search);

    const response = await this.client.get<LocationsPaginatedResponse>(`/locations?${params}`);
    return response.data;
  }

  async getLocation(id: string): Promise<Location> {
    const response = await this.client.get<Location>(`/locations/${id}`);
    return response.data;
  }

  async createLocation(data: LocationCreate): Promise<Location> {
    const response = await this.client.post<Location>("/locations", data);
    return response.data;
  }

  async updateLocation(id: string, data: LocationUpdate): Promise<Location> {
    const response = await this.client.put<Location>(`/locations/${id}`, data);
    return response.data;
  }

  async deleteLocation(id: string): Promise<void> {
    await this.client.delete(`/locations/${id}`);
  }
}

