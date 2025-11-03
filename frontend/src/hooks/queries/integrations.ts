/**
 * React Query hooks for integrations.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../services";
import type {
  IntegrationCreate,
  IntegrationUpdate,
} from "../../types/integration";

export function useIntegrations(options?: {
  skip?: number;
  limit?: number;
  status_filter?: string;
  type_filter?: string;
  organization_id?: string;
}) {
  return useQuery({
    queryKey: [
      "integrations",
      options?.skip,
      options?.limit,
      options?.status_filter,
      options?.type_filter,
      options?.organization_id,
    ],
    queryFn: () =>
      apiClient.integrations.getIntegrations(
        options?.skip,
        options?.limit,
        options?.status_filter,
        options?.type_filter,
        options?.organization_id
      ),
    staleTime: 30 * 1000, // 30 seconds
  });
}

export function useIntegration(id: string | undefined) {
  return useQuery({
    queryKey: ["integrations", id],
    queryFn: () => apiClient.integrations.getIntegration(id!),
    enabled: !!id,
  });
}

export function useCreateIntegration() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: IntegrationCreate) =>
      apiClient.integrations.createIntegration(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["integrations"] });
    },
  });
}

export function useUpdateIntegration() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: IntegrationUpdate }) =>
      apiClient.integrations.updateIntegration(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["integrations"] });
      queryClient.invalidateQueries({
        queryKey: ["integrations", variables.id],
      });
    },
  });
}

export function useDeleteIntegration() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.integrations.deleteIntegration(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["integrations"] });
    },
  });
}

export function useTestIntegration() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.integrations.testIntegration(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["integrations"] });
      queryClient.invalidateQueries({ queryKey: ["integrations", id] });
    },
  });
}

export function useIntegrationLogs(
  id: string | undefined,
  options?: {
    skip?: number;
    limit?: number;
    event_type?: string;
    status_filter?: string;
  }
) {
  return useQuery({
    queryKey: [
      "integrations",
      id,
      "logs",
      options?.skip,
      options?.limit,
      options?.event_type,
      options?.status_filter,
    ],
    queryFn: () =>
      apiClient.integrations.getIntegrationLogs(
        id!,
        options?.skip,
        options?.limit,
        options?.event_type,
        options?.status_filter
      ),
    enabled: !!id,
    staleTime: 10 * 1000, // 10 seconds
  });
}
