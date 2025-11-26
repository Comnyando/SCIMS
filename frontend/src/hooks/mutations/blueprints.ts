/**
 * Blueprint mutation hooks for creating, updating, and deleting blueprints.
 */

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../services";
import type { BlueprintCreate, BlueprintUpdate } from "../../types/blueprint";

export function useCreateBlueprint() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: BlueprintCreate) =>
      apiClient.blueprints.createBlueprint(data),
    onSuccess: () => {
      // Invalidate all blueprint queries to ensure the list refreshes
      queryClient.invalidateQueries({ queryKey: ["blueprints"] });
      // Also refetch to ensure immediate update
      queryClient.refetchQueries({ queryKey: ["blueprints"] });
    },
  });
}

export function useUpdateBlueprint() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: BlueprintUpdate }) =>
      apiClient.blueprints.updateBlueprint(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["blueprints"] });
      queryClient.invalidateQueries({ queryKey: ["blueprints", variables.id] });
    },
  });
}

export function useDeleteBlueprint() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.blueprints.deleteBlueprint(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["blueprints"] });
    },
  });
}
