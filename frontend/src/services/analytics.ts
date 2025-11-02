/**
 * Analytics service methods.
 */

import { ApiClient } from "./client";
import type {
  ConsentResponse,
  ConsentUpdate,
  UsageStatsResponse,
  RecipeStatsResponse,
} from "../types/analytics";

export class AnalyticsService extends ApiClient {
  async getConsent(): Promise<ConsentResponse> {
    const response = await this.client.get<ConsentResponse>(
      "/analytics/consent"
    );
    return response.data;
  }

  async updateConsent(data: ConsentUpdate): Promise<ConsentResponse> {
    const response = await this.client.put<ConsentResponse>(
      "/analytics/consent",
      data
    );
    return response.data;
  }

  async getUsageStats(periodDays = 30): Promise<UsageStatsResponse> {
    const params = new URLSearchParams({
      period_days: periodDays.toString(),
    });
    const response = await this.client.get<UsageStatsResponse>(
      `/analytics/usage-stats?${params}`
    );
    return response.data;
  }

  async getRecipeStats(
    blueprintId: string,
    periodType: "daily" | "weekly" | "monthly" = "monthly",
    periodDays?: number
  ): Promise<RecipeStatsResponse> {
    const params = new URLSearchParams({
      period_type: periodType,
    });
    if (periodDays) {
      params.append("period_days", periodDays.toString());
    }
    const response = await this.client.get<RecipeStatsResponse>(
      `/analytics/recipe-stats/${blueprintId}?${params}`
    );
    return response.data;
  }
}
