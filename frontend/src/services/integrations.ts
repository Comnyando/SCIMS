/**
 * Integrations service methods.
 */

import { ApiClient } from "./client";
import type {
  Integration,
  IntegrationCreate,
  IntegrationUpdate,
  IntegrationTestResponse,
  IntegrationLogsResponse,
} from "../types/integration";
import type { PaginatedResponse } from "../types/common";

export class IntegrationsService extends ApiClient {
  async getIntegrations(
    skip = 0,
    limit = 50,
    status_filter?: string,
    type_filter?: string,
    organization_id?: string
  ): Promise<PaginatedResponse<Integration>> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (status_filter) params.append("status_filter", status_filter);
    if (type_filter) params.append("type_filter", type_filter);
    if (organization_id) params.append("organization_id", organization_id);

    const response = await this.client.get<{
      integrations: Integration[];
      total: number;
      skip: number;
      limit: number;
      pages: number;
    }>(`/integrations?${params}`);

    return {
      items: response.data.integrations,
      total: response.data.total,
      skip: response.data.skip,
      limit: response.data.limit,
    };
  }

  async getIntegration(id: string): Promise<Integration> {
    const response = await this.client.get<Integration>(`/integrations/${id}`);
    return response.data;
  }

  async createIntegration(data: IntegrationCreate): Promise<Integration> {
    const response = await this.client.post<Integration>("/integrations", data);
    return response.data;
  }

  async updateIntegration(
    id: string,
    data: IntegrationUpdate
  ): Promise<Integration> {
    const response = await this.client.patch<Integration>(
      `/integrations/${id}`,
      data
    );
    return response.data;
  }

  async deleteIntegration(id: string): Promise<void> {
    await this.client.delete(`/integrations/${id}`);
  }

  async testIntegration(id: string): Promise<IntegrationTestResponse> {
    const response = await this.client.post<IntegrationTestResponse>(
      `/integrations/${id}/test`
    );
    return response.data;
  }

  async getIntegrationLogs(
    id: string,
    skip = 0,
    limit = 50,
    event_type?: string,
    status_filter?: string
  ): Promise<IntegrationLogsResponse> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (event_type) params.append("event_type", event_type);
    if (status_filter) params.append("status_filter", status_filter);

    const response = await this.client.get<IntegrationLogsResponse>(
      `/integrations/${id}/logs?${params}`
    );
    return response.data;
  }
}
