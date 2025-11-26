/**
 * Craft mutation hooks for creating, updating, and deleting crafts.
 */

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../services";
import type { CraftCreate, CraftUpdate } from "../../types/craft";

export function useCreateCraft() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CraftCreate) => apiClient.crafts.createCraft(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["crafts"] });
    },
  });
}

export function useUpdateCraft() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: CraftUpdate }) =>
      apiClient.crafts.updateCraft(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["crafts"] });
      queryClient.invalidateQueries({ queryKey: ["crafts", variables.id] });
    },
  });
}

export function useDeleteCraft() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.crafts.deleteCraft(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["crafts"] });
    },
  });
}
