/**
 * Hook for checking admin permissions.
 *
 * For now, all active users are considered admins.
 * In the future, this can be extended to check user roles.
 */

import { useAuth } from "../contexts/AuthContext";

export function useAdmin() {
  const { user } = useAuth();

  // For now, all active users are admins
  // TODO: Implement proper role checking when RBAC is expanded
  const isAdmin = user?.is_active ?? false;

  return {
    isAdmin,
  };
}
