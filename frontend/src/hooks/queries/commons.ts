/**
 * React Query hooks for commons.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../services";
import type {
  CommonsSubmissionCreate,
  CommonsSubmissionUpdate,
  CommonsModerationActionCreate,
} from "../../types/commons";

// Submission hooks (user-facing)

export function useMySubmissions(options?: {
  skip?: number;
  limit?: number;
  status?: string;
  entity_type?: string;
}) {
  return useQuery({
    queryKey: [
      "commons",
      "my-submissions",
      options?.skip,
      options?.limit,
      options?.status,
      options?.entity_type,
    ],
    queryFn: () => apiClient.commons.getMySubmissions(options),
    staleTime: 30 * 1000, // 30 seconds
  });
}

export function useCreateSubmission() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CommonsSubmissionCreate) =>
      apiClient.commons.submitSubmission(data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["commons", "my-submissions"],
      });
    },
  });
}

export function useUpdateSubmission() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      submissionId,
      data,
    }: {
      submissionId: string;
      data: CommonsSubmissionUpdate;
    }) => apiClient.commons.updateSubmission(submissionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["commons", "my-submissions"],
      });
    },
  });
}

// Moderation hooks (admin only)

export function useSubmissions(options?: {
  skip?: number;
  limit?: number;
  status?: string;
  entity_type?: string;
}) {
  return useQuery({
    queryKey: [
      "commons",
      "submissions",
      options?.skip,
      options?.limit,
      options?.status,
      options?.entity_type,
    ],
    queryFn: () => apiClient.commons.listSubmissions(options),
    staleTime: 10 * 1000, // 10 seconds for moderation queue
  });
}

export function useSubmission(submissionId: string | undefined) {
  return useQuery({
    queryKey: ["commons", "submissions", submissionId],
    queryFn: () => apiClient.commons.getSubmission(submissionId!),
    enabled: !!submissionId,
  });
}

export function useApproveSubmission() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      submissionId,
      data,
    }: {
      submissionId: string;
      data: CommonsModerationActionCreate;
    }) => apiClient.commons.approveSubmission(submissionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["commons", "submissions"] });
      queryClient.invalidateQueries({ queryKey: ["commons", "public"] });
    },
  });
}

export function useRejectSubmission() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      submissionId,
      data,
    }: {
      submissionId: string;
      data: CommonsModerationActionCreate;
    }) => apiClient.commons.rejectSubmission(submissionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["commons", "submissions"] });
    },
  });
}

export function useRequestChangesSubmission() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      submissionId,
      data,
    }: {
      submissionId: string;
      data: CommonsModerationActionCreate;
    }) => apiClient.commons.requestChangesSubmission(submissionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["commons", "submissions"] });
    },
  });
}

export function useMergeSubmission() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      submissionId,
      data,
    }: {
      submissionId: string;
      data: CommonsModerationActionCreate;
    }) => apiClient.commons.mergeSubmission(submissionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["commons", "submissions"] });
      queryClient.invalidateQueries({ queryKey: ["commons", "public"] });
    },
  });
}

// Public entity hooks

export function usePublicItems(options?: {
  skip?: number;
  limit?: number;
  search?: string;
  tag?: string;
}) {
  return useQuery({
    queryKey: ["commons", "public", "items", options],
    queryFn: () => apiClient.commons.listPublicItems(options),
    staleTime: 5 * 60 * 1000, // 5 minutes (public data cached on server)
  });
}

export function usePublicRecipes(options?: {
  skip?: number;
  limit?: number;
  search?: string;
  tag?: string;
}) {
  return useQuery({
    queryKey: ["commons", "public", "recipes", options],
    queryFn: () => apiClient.commons.listPublicRecipes(options),
    staleTime: 5 * 60 * 1000,
  });
}

export function usePublicLocations(options?: {
  skip?: number;
  limit?: number;
  search?: string;
  tag?: string;
}) {
  return useQuery({
    queryKey: ["commons", "public", "locations", options],
    queryFn: () => apiClient.commons.listPublicLocations(options),
    staleTime: 5 * 60 * 1000,
  });
}

export function usePublicEntity(
  entityType: "item" | "recipe" | "location",
  entityId: string | undefined
) {
  return useQuery({
    queryKey: ["commons", "public", entityType, entityId],
    queryFn: () => apiClient.commons.getPublicEntity(entityType, entityId!),
    enabled: !!entityId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useSearchPublicEntities(options?: {
  q: string;
  entity_type?: string;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ["commons", "public", "search", options],
    queryFn: () => apiClient.commons.searchPublicEntities(options),
    enabled: !!options?.q,
    staleTime: 5 * 60 * 1000,
  });
}

export function useTags() {
  return useQuery({
    queryKey: ["commons", "tags"],
    queryFn: () => apiClient.commons.listTags(),
    staleTime: 5 * 60 * 1000,
  });
}
