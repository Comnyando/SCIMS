/**
 * Craft-related query hooks.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../services";
import type {
  Craft,
  CraftCreate,
  CraftUpdate,
  CraftProgress,
  PaginatedResponse,
} from "../../types";

export interface UseCraftsOptions {
  skip?: number;
  limit?: number;
  status_filter?: string;
  organization_id?: string;
  blueprint_id?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  enabled?: boolean;
}

export function useCrafts(options: UseCraftsOptions = {}) {
  const {
    skip = 0,
    limit = 50,
    status_filter,
    organization_id,
    blueprint_id,
    sort_by,
    sort_order,
    enabled = true,
  } = options;

  return useQuery<PaginatedResponse<Craft>>({
    queryKey: [
      "crafts",
      skip,
      limit,
      status_filter,
      organization_id,
      blueprint_id,
      sort_by,
      sort_order,
    ],
    queryFn: () =>
      apiClient.crafts.getCrafts(
        skip,
        limit,
        status_filter,
        organization_id,
        blueprint_id,
        sort_by,
        sort_order
      ),
    enabled,
    refetchInterval: 10000, // Refetch every 10 seconds for real-time updates
  });
}

export interface UseCraftOptions {
  id: string;
  include_ingredients?: boolean;
  enabled?: boolean;
}

export function useCraft(options: UseCraftOptions) {
  const { id, include_ingredients = false, enabled = true } = options;

  return useQuery<Craft>({
    queryKey: ["crafts", id, include_ingredients],
    queryFn: () => apiClient.crafts.getCraft(id, include_ingredients),
    enabled: enabled && !!id,
    refetchInterval: (query) => {
      // Only poll if craft is in progress
      const craft = query.state.data;
      if (craft?.status === "in_progress") {
        return 5000; // Poll every 5 seconds for in-progress crafts
      }
      return false;
    },
  });
}

export interface UseCraftProgressOptions {
  id: string;
  enabled?: boolean;
}

export function useCraftProgress(options: UseCraftProgressOptions) {
  const { id, enabled = true } = options;

  return useQuery<CraftProgress>({
    queryKey: ["crafts", id, "progress"],
    queryFn: () => apiClient.crafts.getCraftProgress(id),
    enabled: enabled && !!id,
    refetchInterval: (query) => {
      // Only poll if craft is in progress
      const progress = query.state.data;
      if (progress?.status === "in_progress") {
        return 5000; // Poll every 5 seconds for in-progress crafts
      }
      return false;
    },
  });
}

// Mutations
export function useCreateCraft() {
  const queryClient = useQueryClient();

  return useMutation<
    Craft,
    Error,
    { data: CraftCreate; reserve_ingredients?: boolean }
  >({
    mutationFn: ({ data, reserve_ingredients }) =>
      apiClient.crafts.createCraft(data, reserve_ingredients),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["crafts"] });
    },
  });
}

export function useUpdateCraft() {
  const queryClient = useQueryClient();

  return useMutation<Craft, Error, { id: string; data: CraftUpdate }>({
    mutationFn: ({ id, data }) => apiClient.crafts.updateCraft(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["crafts"] });
      queryClient.invalidateQueries({ queryKey: ["crafts", data.id] });
      queryClient.invalidateQueries({
        queryKey: ["crafts", data.id, "progress"],
      });
    },
  });
}

export function useDeleteCraft() {
  const queryClient = useQueryClient();

  return useMutation<
    void,
    Error,
    { id: string; unreserve_ingredients?: boolean }
  >({
    mutationFn: ({ id, unreserve_ingredients }) =>
      apiClient.crafts.deleteCraft(id, unreserve_ingredients),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["crafts"] });
    },
  });
}

export function useStartCraft() {
  const queryClient = useQueryClient();

  return useMutation<
    Craft,
    Error,
    { id: string; reserve_missing_ingredients?: boolean }
  >({
    mutationFn: ({ id, reserve_missing_ingredients }) =>
      apiClient.crafts.startCraft(id, reserve_missing_ingredients),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["crafts"] });
      queryClient.invalidateQueries({ queryKey: ["crafts", data.id] });
      queryClient.invalidateQueries({
        queryKey: ["crafts", data.id, "progress"],
      });
    },
  });
}

export function useCompleteCraft() {
  const queryClient = useQueryClient();

  return useMutation<Craft, Error, string>({
    mutationFn: (id) => apiClient.crafts.completeCraft(id),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["crafts"] });
      queryClient.invalidateQueries({ queryKey: ["crafts", data.id] });
      queryClient.invalidateQueries({
        queryKey: ["crafts", data.id, "progress"],
      });
      // Also invalidate inventory queries since craft completion affects stock
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
    },
  });
}
