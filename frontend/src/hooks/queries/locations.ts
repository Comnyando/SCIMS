/**
 * Location-related query hooks.
 */

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../services";
import type { Location, LocationsPaginatedResponse } from "../../types/location";

export interface UseLocationsOptions {
  skip?: number;
  limit?: number;
  type?: string;
  owner_type?: string;
  search?: string;
  enabled?: boolean;
}

export function useLocations(options: UseLocationsOptions = {}) {
  const { skip = 0, limit = 50, type, owner_type, search, enabled = true } = options;

  return useQuery<LocationsPaginatedResponse>({
    queryKey: ["locations", skip, limit, type, owner_type, search],
    queryFn: () => apiClient.locations.getLocations(skip, limit, type, owner_type, search),
    enabled,
  });
}

export interface UseLocationOptions {
  id: string;
  enabled?: boolean;
}

export function useLocation(options: UseLocationOptions) {
  const { id, enabled = true } = options;

  return useQuery<Location>({
    queryKey: ["locations", id],
    queryFn: () => apiClient.locations.getLocation(id),
    enabled: enabled && !!id,
  });
}

