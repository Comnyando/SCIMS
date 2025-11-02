/**
 * Goal-related query hooks.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../services";
import type {
  Goal,
  GoalCreate,
  GoalUpdate,
  GoalProgressResponse,
} from "../../types/goal";
import type { PaginatedResponse } from "../../types/common";

export interface UseGoalsOptions {
  skip?: number;
  limit?: number;
  status_filter?: string;
  organization_id?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  enabled?: boolean;
}

export function useGoals(options: UseGoalsOptions = {}) {
  const {
    skip = 0,
    limit = 50,
    status_filter,
    organization_id,
    sort_by,
    sort_order,
    enabled = true,
  } = options;

  return useQuery<PaginatedResponse<Goal>>({
    queryKey: [
      "goals",
      skip,
      limit,
      status_filter,
      organization_id,
      sort_by,
      sort_order,
    ],
    queryFn: () =>
      apiClient.goals.getGoals(
        skip,
        limit,
        status_filter,
        organization_id,
        sort_by,
        sort_order
      ),
    enabled,
    refetchInterval: 30000, // Refetch every 30 seconds for progress updates
  });
}

export interface UseGoalOptions {
  id: string;
  enabled?: boolean;
}

export function useGoal(options: UseGoalOptions) {
  const { id, enabled = true } = options;

  return useQuery<Goal>({
    queryKey: ["goals", id],
    queryFn: () => apiClient.goals.getGoal(id),
    enabled: enabled && !!id,
    refetchInterval: 30000, // Refetch every 30 seconds for active goals
  });
}

export interface UseGoalProgressOptions {
  id: string;
  recalculate?: boolean;
  enabled?: boolean;
}

export function useGoalProgress(options: UseGoalProgressOptions) {
  const { id, recalculate = false, enabled = true } = options;

  return useQuery<GoalProgressResponse>({
    queryKey: ["goals", id, "progress", recalculate],
    queryFn: () => apiClient.goals.getGoalProgress(id, recalculate),
    enabled: enabled && !!id,
    refetchInterval: (query) => {
      // Only poll if goal is active
      const progress = query.state.data;
      if (progress?.status === "active") {
        return 30000; // Poll every 30 seconds for active goals
      }
      return false;
    },
  });
}

// Mutations
export function useCreateGoal() {
  const queryClient = useQueryClient();

  return useMutation<Goal, Error, GoalCreate>({
    mutationFn: (data) => apiClient.goals.createGoal(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
    },
  });
}

export function useUpdateGoal() {
  const queryClient = useQueryClient();

  return useMutation<Goal, Error, { id: string; data: GoalUpdate }>({
    mutationFn: ({ id, data }) => apiClient.goals.updateGoal(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
      queryClient.invalidateQueries({ queryKey: ["goals", data.id] });
      queryClient.invalidateQueries({
        queryKey: ["goals", data.id, "progress"],
      });
    },
  });
}

export function useDeleteGoal() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (id) => apiClient.goals.deleteGoal(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
    },
  });
}
