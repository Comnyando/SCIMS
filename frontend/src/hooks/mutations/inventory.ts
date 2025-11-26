/**
 * Inventory mutation hooks for adjusting and transferring inventory.
 */

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../services";
import type { InventoryAdjust, InventoryTransfer } from "../../types/inventory";

export function useAdjustInventory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: InventoryAdjust) =>
      apiClient.inventory.adjustInventory(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
    },
  });
}

export function useTransferInventory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: InventoryTransfer) =>
      apiClient.inventory.transferInventory(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
    },
  });
}
