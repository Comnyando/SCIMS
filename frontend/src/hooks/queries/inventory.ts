/**
 * Inventory-related query hooks.
 */

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../services";
import type { InventoryStock, InventoryHistory, PaginatedResponse } from "../../types";

export interface UseInventoryOptions {
  skip?: number;
  limit?: number;
  item_id?: string;
  location_id?: string;
  search?: string;
  enabled?: boolean;
}

export function useInventory(options: UseInventoryOptions = {}) {
  const { skip = 0, limit = 50, item_id, location_id, search, enabled = true } = options;

  return useQuery<PaginatedResponse<InventoryStock>>({
    queryKey: ["inventory", skip, limit, item_id, location_id, search],
    queryFn: () => apiClient.inventory.getInventory(skip, limit, item_id, location_id, search),
    enabled,
  });
}

export interface UseInventoryHistoryOptions {
  skip?: number;
  limit?: number;
  item_id?: string;
  location_id?: string;
  transaction_type?: string;
  enabled?: boolean;
}

export function useInventoryHistory(options: UseInventoryHistoryOptions = {}) {
  const {
    skip = 0,
    limit = 50,
    item_id,
    location_id,
    transaction_type,
    enabled = true,
  } = options;

  return useQuery<PaginatedResponse<InventoryHistory>>({
    queryKey: ["inventory", "history", skip, limit, item_id, location_id, transaction_type],
    queryFn: () =>
      apiClient.inventory.getInventoryHistory(skip, limit, item_id, location_id, transaction_type),
    enabled,
  });
}

