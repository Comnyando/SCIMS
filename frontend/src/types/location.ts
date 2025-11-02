/**
 * Location-related types.
 */

export interface Location {
  id: string;
  name: string;
  type: "station" | "ship" | "player_inventory" | "warehouse";
  owner_type: "user" | "organization" | "ship";
  owner_id: string;
  parent_location_id: string | null;
  canonical_location_id: string | null;
  is_canonical: boolean;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface LocationCreate {
  name: string;
  type: "station" | "ship" | "player_inventory" | "warehouse";
  owner_type: "user" | "organization" | "ship";
  owner_id: string;
  parent_location_id?: string;
  canonical_location_id?: string;
  metadata?: Record<string, unknown>;
}

export interface LocationUpdate {
  name?: string;
  type?: "station" | "ship" | "player_inventory" | "warehouse";
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
