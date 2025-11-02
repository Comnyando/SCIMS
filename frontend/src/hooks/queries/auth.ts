/**
 * Authentication and user-related query hooks.
 */

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../services";
import type { User } from "../../types";

export function useCurrentUser() {
  return useQuery<User>({
    queryKey: ["user", "current"],
    queryFn: () => apiClient.getCurrentUser(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

