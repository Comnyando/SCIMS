/**
 * Authentication mutation hooks using TanStack Query.
 */

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { apiClient } from "../../services";
import type { LoginRequest, RegisterRequest } from "../../types";

export function useLogin() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (credentials: LoginRequest) => {
      // apiClient.login already handles localStorage and token storage
      return apiClient.login(credentials);
    },
    onSuccess: (data) => {
      // Update user cache for React Query
      queryClient.setQueryData(["user", "current"], data.user);
      // Invalidate any other user-related queries
      queryClient.invalidateQueries({ queryKey: ["user"] });
      // Navigate to dashboard
      navigate("/dashboard");
    },
  });
}

export function useRegister() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (data: RegisterRequest) => {
      // apiClient.register already handles localStorage and token storage
      return apiClient.register(data);
    },
    onSuccess: (response) => {
      // Update user cache for React Query
      queryClient.setQueryData(["user", "current"], response.user);
      // Invalidate any other user-related queries
      queryClient.invalidateQueries({ queryKey: ["user"] });
      // Navigate to dashboard
      navigate("/dashboard");
    },
  });
}

