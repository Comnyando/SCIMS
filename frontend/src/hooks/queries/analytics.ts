/**
 * React Query hooks for analytics.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../services";
import type { ConsentUpdate } from "../../types/analytics";

export function useConsent() {
  return useQuery({
    queryKey: ["analytics", "consent"],
    queryFn: () => apiClient.analytics.getConsent(),
  });
}

export function useUpdateConsent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ConsentUpdate) =>
      apiClient.analytics.updateConsent(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["analytics", "consent"] });
      // Also invalidate user queries to update analytics_consent in user context
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
    },
  });
}

export function useUsageStats(periodDays = 30, enabled = true) {
  return useQuery({
    queryKey: ["analytics", "usage-stats", periodDays],
    queryFn: () => apiClient.analytics.getUsageStats(periodDays),
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useRecipeStats(
  blueprintId: string | undefined,
  periodType: "daily" | "weekly" | "monthly" = "monthly",
  periodDays?: number,
  enabled = true
) {
  return useQuery({
    queryKey: [
      "analytics",
      "recipe-stats",
      blueprintId,
      periodType,
      periodDays,
    ],
    queryFn: () =>
      apiClient.analytics.getRecipeStats(blueprintId!, periodType, periodDays),
    enabled: enabled && !!blueprintId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
