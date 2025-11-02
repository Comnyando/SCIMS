/**
 * Craft-related types.
 */

export type CraftStatus = "planned" | "in_progress" | "completed" | "cancelled";
export type IngredientSourceType = "stock" | "player" | "universe";
export type IngredientStatus = "pending" | "reserved" | "fulfilled";

export interface CraftIngredient {
  id: string;
  craft_id: string;
  item_id: string;
  required_quantity: number;
  source_location_id: string | null;
  source_type: IngredientSourceType;
  status: IngredientStatus;
  item?: {
    id: string;
    name: string;
    category: string | null;
  } | null;
  source_location?: {
    id: string;
    name: string;
    type: string;
  } | null;
}

export interface Craft {
  id: string;
  blueprint_id: string;
  organization_id: string | null;
  requested_by: string;
  status: CraftStatus;
  priority: number;
  scheduled_start: string | null;
  started_at: string | null;
  completed_at: string | null;
  output_location_id: string;
  metadata: Record<string, unknown> | null;
  created_at: string;
  blueprint?: {
    id: string;
    name: string;
    category: string | null;
    crafting_time_minutes: number;
    output_item_id: string;
    output_quantity: number;
  } | null;
  organization?: {
    id: string;
    name: string;
    slug: string;
  } | null;
  requester?: {
    id: string;
    username: string;
    email: string;
  } | null;
  output_location?: {
    id: string;
    name: string;
    type: string;
  } | null;
  ingredients?: CraftIngredient[] | null;
}

export interface CraftCreate {
  blueprint_id: string;
  organization_id?: string | null;
  output_location_id: string;
  priority?: number;
  scheduled_start?: string | null;
  metadata?: Record<string, unknown> | null;
  ingredients?: Omit<CraftIngredient, "id" | "craft_id">[] | null;
}

export interface CraftUpdate {
  organization_id?: string | null;
  output_location_id?: string;
  priority?: number;
  scheduled_start?: string | null;
  metadata?: Record<string, unknown> | null;
  status?: CraftStatus;
}

export interface CraftProgress {
  craft_id: string;
  status: CraftStatus;
  blueprint_name: string;
  output_item_name: string;
  crafting_time_minutes: number;
  elapsed_minutes: number | null;
  estimated_completion_minutes: number | null;
  ingredients_status: {
    total: number;
    pending: number;
    reserved: number;
    fulfilled: number;
    details: Array<{
      item_id: string;
      item_name: string;
      status: IngredientStatus;
      required_quantity: number;
    }>;
  };
}
