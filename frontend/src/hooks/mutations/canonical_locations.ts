/**
 * Canonical Location mutation hooks for creating, updating, and deleting canonical locations.
 */

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../services";
import type {
  CanonicalLocationCreate,
  CanonicalLocationUpdate,
} from "../../types/canonical_location";

export function useCreateCanonicalLocation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CanonicalLocationCreate) =>
      apiClient.canonicalLocations.createCanonicalLocation(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["canonical-locations"] });
      queryClient.invalidateQueries({ queryKey: ["locations"] });
      queryClient.invalidateQueries({
        queryKey: ["commons", "public", "locations"],
      });
    },
  });
}

export function useUpdateCanonicalLocation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: CanonicalLocationUpdate }) =>
      apiClient.canonicalLocations.updateCanonicalLocation(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["canonical-locations"] });
      queryClient.invalidateQueries({
        queryKey: ["canonical-locations", variables.id],
      });
      queryClient.invalidateQueries({ queryKey: ["locations"] });
      queryClient.invalidateQueries({
        queryKey: ["commons", "public", "locations"],
      });
    },
  });
}

export function useDeleteCanonicalLocation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) =>
      apiClient.canonicalLocations.deleteCanonicalLocation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["canonical-locations"] });
      queryClient.invalidateQueries({ queryKey: ["locations"] });
      queryClient.invalidateQueries({
        queryKey: ["commons", "public", "locations"],
      });
    },
  });
}
