/**
 * Optimization-related query hooks.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../services";
import type {
  FindSourcesRequest,
  FindSourcesResponse,
  SuggestCraftsRequest,
  SuggestCraftsResponse,
  ResourceGapResponse,
} from "../../types/optimization";

export interface UseFindSourcesOptions {
  request: FindSourcesRequest;
  enabled?: boolean;
}

export function useFindSources(options: UseFindSourcesOptions) {
  const { request, enabled = true } = options;

  return useQuery<FindSourcesResponse>({
    queryKey: ["optimization", "find-sources", request],
    queryFn: () => apiClient.optimization.findSources(request),
    enabled: enabled && !!request.item_id && request.required_quantity > 0,
  });
}

export interface UseSuggestCraftsOptions {
  request: SuggestCraftsRequest;
  enabled?: boolean;
}

export function useSuggestCrafts(options: UseSuggestCraftsOptions) {
  const { request, enabled = true } = options;

  return useQuery<SuggestCraftsResponse>({
    queryKey: ["optimization", "suggest-crafts", request],
    queryFn: () => apiClient.optimization.suggestCrafts(request),
    enabled: enabled && !!request.target_item_id && request.target_quantity > 0,
  });
}

export interface UseResourceGapOptions {
  craftId: string;
  enabled?: boolean;
}

export function useResourceGap(options: UseResourceGapOptions) {
  const { craftId, enabled = true } = options;

  return useQuery<ResourceGapResponse>({
    queryKey: ["optimization", "resource-gap", craftId],
    queryFn: () => apiClient.optimization.getResourceGap(craftId),
    enabled: enabled && !!craftId,
    refetchInterval: 10000, // Refetch every 10 seconds to keep gaps up to date
  });
}

// Mutations
export function useFindSourcesMutation() {
  const queryClient = useQueryClient();

  return useMutation<FindSourcesResponse, Error, FindSourcesRequest>({
    mutationFn: (request) => apiClient.optimization.findSources(request),
    onSuccess: (data, variables) => {
      queryClient.setQueryData(
        ["optimization", "find-sources", variables],
        data
      );
    },
  });
}

export function useSuggestCraftsMutation() {
  const queryClient = useQueryClient();

  return useMutation<SuggestCraftsResponse, Error, SuggestCraftsRequest>({
    mutationFn: (request) => apiClient.optimization.suggestCrafts(request),
    onSuccess: (data, variables) => {
      queryClient.setQueryData(
        ["optimization", "suggest-crafts", variables],
        data
      );
    },
  });
}
