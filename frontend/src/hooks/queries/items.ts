/**
 * Item-related query hooks.
 */

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../services";
import type { Item, PaginatedResponse } from "../../types";

export interface UseItemsOptions {
  skip?: number;
  limit?: number;
  search?: string;
  category?: string;
  enabled?: boolean;
}

export function useItems(options: UseItemsOptions = {}) {
  const { skip = 0, limit = 50, search, category, enabled = true } = options;

  return useQuery<PaginatedResponse<Item>>({
    queryKey: ["items", skip, limit, search, category],
    queryFn: () => apiClient.items.getItems(skip, limit, search, category),
    enabled,
  });
}

export interface UseItemOptions {
  id: string;
  enabled?: boolean;
}

export function useItem(options: UseItemOptions) {
  const { id, enabled = true } = options;

  return useQuery<Item>({
    queryKey: ["items", id],
    queryFn: () => apiClient.items.getItem(id),
    enabled: enabled && !!id,
  });
}

