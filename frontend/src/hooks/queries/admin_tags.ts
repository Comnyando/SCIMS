/**
 * React Query hooks for admin tag management.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../services";
import type { TagCreate } from "../../types/commons";

export function useTagsAdmin(options?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: ["commons", "tags", "admin", options],
    queryFn: () => apiClient.commons.listTagsAdmin(options),
    staleTime: 30 * 1000,
  });
}

export function useCreateTag() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TagCreate) => apiClient.commons.createTag(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["commons", "tags"] });
    },
  });
}

export function useUpdateTag() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ tagId, data }: { tagId: string; data: TagCreate }) =>
      apiClient.commons.updateTag(tagId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["commons", "tags"] });
    },
  });
}

export function useDeleteTag() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (tagId: string) => apiClient.commons.deleteTag(tagId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["commons", "tags"] });
    },
  });
}
