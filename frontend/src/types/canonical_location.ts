/**
 * Canonical Location-related types.
 */

import { LocationType } from "./enums";

export interface CanonicalLocation {
  id: string;
  name: string;
  type: LocationType;
  parent_location_id: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface CanonicalLocationCreate {
  name: string;
  type: LocationType;
  parent_location_id?: string;
  metadata?: Record<string, unknown>;
}

export interface CanonicalLocationUpdate {
  name?: string;
  type?: LocationType;
  parent_location_id?: string;
  metadata?: Record<string, unknown>;
}

export interface CanonicalLocationsPaginatedResponse {
  locations: CanonicalLocation[];
  total: number;
  skip: number;
  limit: number;
  pages?: number;
}
