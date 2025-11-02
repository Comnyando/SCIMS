/**
 * Blueprint-related query hooks.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../services";
import type {
  Blueprint,
  BlueprintCreate,
  BlueprintUpdate,
  PaginatedResponse,
} from "../../types";

export interface UseBlueprintsOptions {
  skip?: number;
  limit?: number;
  search?: string;
  category?: string;
  output_item_id?: string;
  is_public?: boolean;
  created_by?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  enabled?: boolean;
}

export function useBlueprints(options: UseBlueprintsOptions = {}) {
  const {
    skip = 0,
    limit = 50,
    search,
    category,
    output_item_id,
    is_public,
    created_by,
    sort_by,
    sort_order,
    enabled = true,
  } = options;

  return useQuery<PaginatedResponse<Blueprint>>({
    queryKey: [
      "blueprints",
      skip,
      limit,
      search,
      category,
      output_item_id,
      is_public,
      created_by,
      sort_by,
      sort_order,
    ],
    queryFn: () =>
      apiClient.blueprints.getBlueprints(
        skip,
        limit,
        search,
        category,
        output_item_id,
        is_public,
        created_by,
        sort_by,
        sort_order
      ),
    enabled,
  });
}

export interface UseBlueprintOptions {
  id: string;
  enabled?: boolean;
}

export function useBlueprint(options: UseBlueprintOptions) {
  const { id, enabled = true } = options;

  return useQuery<Blueprint>({
    queryKey: ["blueprints", id],
    queryFn: () => apiClient.blueprints.getBlueprint(id),
    enabled: enabled && !!id,
  });
}

export interface UsePopularBlueprintsOptions {
  limit?: number;
  category?: string;
  enabled?: boolean;
}

export function usePopularBlueprints(
  options: UsePopularBlueprintsOptions = {}
) {
  const { limit = 10, category, enabled = true } = options;

  return useQuery<{ blueprints: Blueprint[]; total: number }>({
    queryKey: ["blueprints", "popular", limit, category],
    queryFn: () => apiClient.blueprints.getPopularBlueprints(limit, category),
    enabled,
  });
}

export interface UseBlueprintsByItemOptions {
  item_id: string;
  skip?: number;
  limit?: number;
  is_public?: boolean;
  enabled?: boolean;
}

export function useBlueprintsByItem(options: UseBlueprintsByItemOptions) {
  const { item_id, skip = 0, limit = 50, is_public, enabled = true } = options;

  return useQuery<PaginatedResponse<Blueprint>>({
    queryKey: ["blueprints", "by-item", item_id, skip, limit, is_public],
    queryFn: () =>
      apiClient.blueprints.getBlueprintsByItem(item_id, skip, limit, is_public),
    enabled: enabled && !!item_id,
  });
}

// Mutations
export function useCreateBlueprint() {
  const queryClient = useQueryClient();

  return useMutation<Blueprint, Error, BlueprintCreate>({
    mutationFn: (data) => apiClient.blueprints.createBlueprint(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["blueprints"] });
    },
  });
}

export function useUpdateBlueprint() {
  const queryClient = useQueryClient();

  return useMutation<Blueprint, Error, { id: string; data: BlueprintUpdate }>({
    mutationFn: ({ id, data }) =>
      apiClient.blueprints.updateBlueprint(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["blueprints"] });
      queryClient.invalidateQueries({ queryKey: ["blueprints", data.id] });
    },
  });
}

export function useDeleteBlueprint() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (id) => apiClient.blueprints.deleteBlueprint(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["blueprints"] });
    },
  });
}
