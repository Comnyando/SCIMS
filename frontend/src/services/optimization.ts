/**
 * Optimization service for API calls.
 */

import { ApiClient } from "./client";
import type {
  FindSourcesRequest,
  FindSourcesResponse,
  SuggestCraftsRequest,
  SuggestCraftsResponse,
  ResourceGapResponse,
} from "../types/optimization";

export class OptimizationService extends ApiClient {
  async findSources(request: FindSourcesRequest): Promise<FindSourcesResponse> {
    const response = await this.client.post<FindSourcesResponse>(
      "/optimization/find-sources",
      request
    );
    return response.data;
  }

  async suggestCrafts(
    request: SuggestCraftsRequest
  ): Promise<SuggestCraftsResponse> {
    const response = await this.client.post<SuggestCraftsResponse>(
      "/optimization/suggest-crafts",
      request
    );
    return response.data;
  }

  async getResourceGap(craftId: string): Promise<ResourceGapResponse> {
    const response = await this.client.get<ResourceGapResponse>(
      `/optimization/resource-gap/${craftId}`
    );
    return response.data;
  }
}
