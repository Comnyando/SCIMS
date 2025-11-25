/**
 * Location-related types.
 */

import { LocationType, OwnerType } from "./enums";

export interface ChildLocationInfo {
  id: string;
  name: string;
}

export interface Location {
  id: string;
  name: string;
  type: LocationType;
  owner_type: OwnerType;
  owner_id: string;
  parent_location_id: string | null;
  parent_location_name: string | null;
  canonical_location_id: string | null;
  is_canonical: boolean;
  child_locations: ChildLocationInfo[];
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface LocationCreate {
  name: string;
  type: LocationType;
  owner_type: OwnerType;
  owner_id: string;
  parent_location_id?: string;
  canonical_location_id?: string;
  metadata?: Record<string, unknown>;
}

export interface LocationUpdate {
  name?: string;
  type?: LocationType;
  parent_location_id?: string;
  canonical_location_id?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Paginated response specifically for locations endpoint.
 * The backend returns "locations" not "items" for this endpoint.
 */
export interface LocationsPaginatedResponse {
  locations: Location[];
  total: number;
  skip: number;
  limit: number;
  pages?: number;
}
