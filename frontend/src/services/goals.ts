/**
 * Goals service methods.
 */

import { ApiClient } from "./client";
import type {
  Goal,
  GoalCreate,
  GoalUpdate,
  GoalProgressResponse,
} from "../types/goal";
import type { PaginatedResponse } from "../types/common";

export class GoalsService extends ApiClient {
  async getGoals(
    skip = 0,
    limit = 50,
    status_filter?: string,
    organization_id?: string,
    sort_by?: string,
    sort_order?: "asc" | "desc"
  ): Promise<PaginatedResponse<Goal>> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (status_filter) params.append("status_filter", status_filter);
    if (organization_id) params.append("organization_id", organization_id);
    if (sort_by) params.append("sort_by", sort_by);
    if (sort_order) params.append("sort_order", sort_order);

    const response = await this.client.get<{
      goals: Goal[];
      total: number;
      skip: number;
      limit: number;
      pages: number;
    }>(`/goals?${params}`);
    // Transform response to match PaginatedResponse format
    return {
      items: response.data.goals,
      total: response.data.total,
      skip: response.data.skip,
      limit: response.data.limit,
    };
  }

  async getGoal(id: string): Promise<Goal> {
    const response = await this.client.get<Goal>(`/goals/${id}`);
    return response.data;
  }

  async createGoal(data: GoalCreate): Promise<Goal> {
    const response = await this.client.post<Goal>(`/goals`, data);
    return response.data;
  }

  async updateGoal(id: string, data: GoalUpdate): Promise<Goal> {
    const response = await this.client.patch<Goal>(`/goals/${id}`, data);
    return response.data;
  }

  async deleteGoal(id: string): Promise<void> {
    await this.client.delete(`/goals/${id}`);
  }

  async getGoalProgress(
    id: string,
    recalculate = false
  ): Promise<GoalProgressResponse> {
    const params = new URLSearchParams();
    if (recalculate) params.append("recalculate", "true");

    const url = `/goals/${id}/progress${params.toString() ? `?${params}` : ""}`;
    const response = await this.client.get<GoalProgressResponse>(url);
    return response.data;
  }
}
