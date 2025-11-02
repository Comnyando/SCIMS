/**
 * Optimization-related types.
 */

export interface SourceOption {
  source_type: string;
  location_id?: string;
  location_name?: string;
  source_id?: string;
  source_identifier?: string;
  available_quantity: number;
  cost_per_unit: number;
  total_cost: number;
  reliability_score?: number;
  metadata?: Record<string, unknown>;
}

export interface FindSourcesRequest {
  item_id: string;
  required_quantity: number;
  max_sources?: number;
  include_player_stocks?: boolean;
  min_reliability?: number;
  organization_id?: string;
}

export interface FindSourcesResponse {
  item_id: string;
  item_name?: string;
  required_quantity: number;
  sources: SourceOption[];
  total_available: number;
  has_sufficient: boolean;
}

export interface CraftSuggestion {
  blueprint_id: string;
  blueprint_name: string;
  output_item_id: string;
  output_item_name?: string;
  output_quantity: number;
  crafting_time_minutes: number;
  suggested_count: number;
  total_output: number;
  ingredients: Array<{
    item_id: string;
    quantity: number;
    available: number;
  }>;
  all_ingredients_available: boolean;
}

export interface SuggestCraftsRequest {
  target_item_id: string;
  target_quantity: number;
  organization_id?: string;
  max_suggestions?: number;
}

export interface SuggestCraftsResponse {
  target_item_id: string;
  target_item_name?: string;
  target_quantity: number;
  suggestions: CraftSuggestion[];
}

export interface ResourceGapItem {
  item_id: string;
  item_name?: string;
  required_quantity: number;
  available_quantity: number;
  gap_quantity: number;
  sources: SourceOption[];
}

export interface ResourceGapResponse {
  craft_id: string;
  craft_status: string;
  blueprint_name?: string;
  gaps: ResourceGapItem[];
  total_gaps: number;
  can_proceed: boolean;
}
